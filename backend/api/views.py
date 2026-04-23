from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS, AllowAny, BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import ChatMessage, Follow, Topic, Video, VideoReaction
from .serializers import (
    ChatMessageSerializer,
    FollowSerializer,
    TopicSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSummarySerializer,
    VideoReactionSerializer,
    VideoSerializer,
)

User = get_user_model()


class IsOwnerOrReadOnly(BasePermission):
    message = 'Only the owners of a resource have permission to modify them.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, User):
            return obj == request.user

        owner_field = getattr(view, 'owner_field', 'user')
        return getattr(obj, owner_field, None) == request.user


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all().order_by('username')
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action == 'list':
            return UserSummarySerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permission() for permission in (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)]


class UserFollowerCollectionView(generics.ListCreateAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.select_related('follower', 'following').filter(
            following__username=self.kwargs['username']
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['following'] = self.kwargs['username']
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        target_user = get_object_or_404(User, username=self.kwargs['username'])

        if target_user == self.request.user:
            raise ValidationError({'following': 'Users may not follow themselves.'})

        if Follow.objects.filter(follower=self.request.user, following=target_user).exists():
            raise ValidationError({'following': 'User already followed.'})

        serializer.save(follower=self.request.user, following=target_user)


class UserFollowingCollectionView(generics.ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.select_related('follower', 'following').filter(
            follower__username=self.kwargs['username']
        ).order_by('-created_at')


class TopicViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
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
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Video.objects.select_related('user').prefetch_related('topics')
    lookup_field = 'id'
    owner_field = 'user'

    def get_queryset(self):
        return Video.objects.select_related('user').prefetch_related('topics').order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserVideoCollectionView(generics.ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        return Video.objects.select_related('user').prefetch_related('topics').filter(
            user__username=self.kwargs['username']
        ).order_by('-created')


class VideoReactionView(generics.GenericAPIView):
    serializer_class = VideoReactionSerializer

    def get_video(self):
        return get_object_or_404(Video, id=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        video = self.get_video()
        user_reaction = None

        if request.user.is_authenticated:
            user_reaction = VideoReaction.objects.filter(
                user=request.user,
                video=video,
            ).values_list('reaction', flat=True).first()

        return Response(
            {
                'id': video.id,
                'like_count': video.like_count,
                'dislike_count': video.dislike_count,
                'user_reaction': user_reaction,
            }
        )

    def put(self, request, *args, **kwargs):
        return self._save_reaction(request)

    def patch(self, request, *args, **kwargs):
        return self._save_reaction(request)

    def delete(self, request, *args, **kwargs):
        video = self.get_video()

        with transaction.atomic():
            reaction = VideoReaction.objects.select_for_update().filter(
                user=request.user,
                video=video,
            ).first()

            if reaction is None:
                return Response(status=status.HTTP_204_NO_CONTENT)

            reaction.delete()
            self._sync_reaction_counts(video.id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _save_reaction(self, request):
        video = self.get_video()
        serializer = self.get_serializer(
            data={
                'video': video.id,
                'reaction': request.data.get('reaction'),
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        new_reaction = serializer.validated_data['reaction']

        with transaction.atomic():
            VideoReaction.objects.update_or_create(
                user=request.user,
                video=video,
                defaults={'reaction': new_reaction},
            )
            self._sync_reaction_counts(video.id)

        video.refresh_from_db(fields=['like_count', 'dislike_count'])

        return Response(
            {
                'id': video.id,
                'like_count': video.like_count,
                'dislike_count': video.dislike_count,
                'user_reaction': new_reaction,
            },
            status=status.HTTP_200_OK,
        )

    def _sync_reaction_counts(self, video_id):
        counts = {
            row['reaction']: row['total']
            for row in VideoReaction.objects.filter(video_id=video_id).values('reaction').annotate(total=Count('id'))
        }

        Video.objects.filter(id=video_id).update(
            like_count=counts.get(VideoReaction.LIKE, 0),
            dislike_count=counts.get(VideoReaction.DISLIKE, 0),
        )


class VideoMessageCollectionView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.select_related('user', 'video').filter(
            video_id=self.kwargs['video_id']
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['video'] = self.kwargs['video_id']
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        video = get_object_or_404(Video, id=self.kwargs['video_id'])
        serializer.save(user=self.request.user, video=video)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer