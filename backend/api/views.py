from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from .auth_helpers import bind_authenticated_user
from .models import AccountStreamKey, ChatMessage, Follow, StreamSession, Topic, Video, VideoReaction
from .permissions import IsOwnerOrReadOnly
from .services import clear_video_reaction, create_follow, create_video_message, delete_follow, set_video_reaction
from .serializers import (
    AccountStreamKeyRotateResponseSerializer,
    AccountStreamKeySerializer,
    ChatMessageReadSerializer,
    ChatMessageWriteSerializer,
    StreamSessionReadSerializer,
    TopicSerializer,
    UserFollowStateSerializer,
    UserProfileSerializer,
    UserProfileWriteSerializer,
    UserRegistrationSerializer,
    UserSummarySerializer,
    VideoDetailSerializer,
    VideoListSerializer,
    VideoReactionStateSerializer,
    VideoReactionWriteSerializer,
    VideoWriteSerializer,
)
from .streaming import LiveSessionConflict, create_stream_session, end_stream_session, rotate_account_stream_key
from .throttles import (
    LoginRateThrottle,
    MessageWriteRateThrottle,
    ReactionWriteRateThrottle,
    RegistrationRateThrottle,
    TokenRefreshRateThrottle,
    TokenRevokeRateThrottle,
)

User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = User.objects.all().order_by('username')
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action == 'list':
            return UserSummarySerializer
        if self.action in ('update', 'partial_update'):
            return UserProfileWriteSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)]

    def get_throttles(self):
        if self.action == 'create':
            return [RegistrationRateThrottle()]
        return super().get_throttles()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = UserProfileSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = UserProfileSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(response_serializer.data)


class UserFollowerCollectionView(generics.ListAPIView):
    serializer_class = UserSummarySerializer

    def get_target_user(self):
        return get_object_or_404(User.objects.only('id'), username=self.kwargs['username'])

    def get_queryset(self):
        target_user = self.get_target_user()
        return User.objects.filter(
            following_edges__following_id=target_user.id
        ).order_by('-following_edges__created_at')


class UserFollowingCollectionView(generics.ListAPIView):
    serializer_class = UserSummarySerializer

    def get_target_user(self):
        return get_object_or_404(User.objects.only('id'), username=self.kwargs['username'])

    def get_queryset(self):
        target_user = self.get_target_user()
        return User.objects.filter(
            follower_edges__follower_id=target_user.id
        ).order_by('-follower_edges__created_at')


class UserFollowStateView(generics.GenericAPIView):
    serializer_class = UserFollowStateSerializer
    permission_classes = [IsAuthenticated]

    def get_target_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get(self, request, *args, **kwargs):
        target_user = self.get_target_user()
        serializer = self.get_serializer(
            {
                'is_following': Follow.objects.filter(
                    follower=request.user,
                    following=target_user,
                ).exists()
            }
        )
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        target_user = self.get_target_user()
        create_follow(follower=request.user, following=target_user)

        serializer = self.get_serializer({'is_following': True})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        target_user = self.get_target_user()
        delete_follow(follower=request.user, following=target_user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Topic.objects.all().order_by('name')
    serializer_class = TopicSerializer
    lookup_field = 'id'


class VideoViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Video.objects.select_related('user').prefetch_related('topics')
    lookup_field = 'id'
    owner_field = 'user'

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return VideoWriteSerializer
        return VideoDetailSerializer

    def get_queryset(self):
        queryset = Video.objects.select_related('user').prefetch_related('topics').order_by('-created')
        username = self.request.query_params.get('user')
        topic_name = self.request.query_params.get('topic_name')

        if username:
            queryset = queryset.filter(user__username=username)

        if topic_name:
            queryset = queryset.filter(topics__name=topic_name).distinct()

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = VideoDetailSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response_serializer = VideoDetailSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(response_serializer.data)

    def perform_create(self, serializer):
        bind_authenticated_user(serializer, user=self.request.user)


class VideoReactionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    api_to_model_reaction = {
        'like': VideoReaction.LIKE,
        'dislike': VideoReaction.DISLIKE,
    }
    model_to_api_reaction = {
        VideoReaction.LIKE: 'like',
        VideoReaction.DISLIKE: 'dislike',
    }

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return VideoReactionWriteSerializer
        return VideoReactionStateSerializer

    def get_throttles(self):
        if self.request.method in ('PUT', 'DELETE'):
            return [ReactionWriteRateThrottle()]
        return super().get_throttles()

    def get_video(self):
        return get_object_or_404(Video, id=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        video = self.get_video()
        reaction = VideoReaction.objects.filter(user=request.user, video=video).values_list('reaction', flat=True).first()
        serializer = self.get_serializer(
            {
                'reaction': self.model_to_api_reaction.get(reaction),
            }
        )
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self._save_reaction(request)

    def delete(self, request, *args, **kwargs):
        video = self.get_video()
        clear_video_reaction(user=request.user, video=video)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _save_reaction(self, request):
        video = self.get_video()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_reaction = serializer.validated_data['reaction']
        new_model_reaction = self.api_to_model_reaction[new_reaction]
        set_video_reaction(user=request.user, video=video, reaction=new_model_reaction)

        response_serializer = VideoReactionStateSerializer({'reaction': new_reaction})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class VideoMessageCollectionView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_video(self):
        return get_object_or_404(Video.objects.only('id'), id=self.kwargs['id'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatMessageWriteSerializer
        return ChatMessageReadSerializer

    def get_throttles(self):
        if self.request.method == 'POST':
            return [MessageWriteRateThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        video = self.get_video()
        return ChatMessage.objects.select_related('user').filter(
            video_id=video.id
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = self.perform_create(serializer)
        response_serializer = ChatMessageReadSerializer(message, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        video = self.get_video()
        return create_video_message(
            user=self.request.user,
            message=serializer.validated_data['message'],
            video_id=video.id,
        )


class VideoStreamSessionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = StreamSessionReadSerializer

    def get_video(self):
        return get_object_or_404(Video.objects.select_related('user'), id=self.kwargs['id'])

    def get_stream_session(self):
        stream_session = StreamSession.objects.select_related('user', 'video').filter(
            video_id=self.kwargs['id'],
            is_live=True,
        ).first()
        if stream_session is None:
            raise NotFound('No active stream session was found for this video.')
        return stream_session

    def _assert_video_owner(self, video):
        if not self.request.user.is_authenticated:
            self.permission_denied(self.request)
        if video.user_id != self.request.user.id:
            raise PermissionDenied('Only the owner of this video may manage its live session.')

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_stream_session())
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        video = self.get_video()
        self._assert_video_owner(video)

        try:
            stream_session = create_stream_session(user=request.user, video=video)
        except LiveSessionConflict as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(stream_session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        video = self.get_video()
        self._assert_video_owner(video)

        stream_session = StreamSession.objects.filter(video=video, is_live=True).first()
        if stream_session is not None:
            end_stream_session(stream_session=stream_session)

        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountStreamKeyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountStreamKeySerializer

    def get(self, request, *args, **kwargs):
        account_stream_key = AccountStreamKey.objects.filter(user=request.user).first()
        if account_stream_key is None:
            raise NotFound('No account stream key has been rotated for this user yet.')

        serializer = self.get_serializer(account_stream_key)
        return Response(serializer.data)


class AccountStreamKeyRotateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountStreamKeyRotateResponseSerializer

    def post(self, request, *args, **kwargs):
        account_stream_key, plaintext_key = rotate_account_stream_key(user=request.user)
        serializer = self.get_serializer(
            {
                'stream_key': plaintext_key,
                'stream_key_last4': account_stream_key.stream_key_last4,
                'rotated_at': account_stream_key.rotated_at,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSummarySerializer(self.user, context=self.context).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_classes = [TokenRefreshRateThrottle]


class TokenRevokeView(TokenBlacklistView):
    permission_classes = [AllowAny]
    throttle_classes = [TokenRevokeRateThrottle]