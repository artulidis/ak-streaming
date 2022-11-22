from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import json

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import MyUserSerializer, MyUserProfileImageSerializer, MyUserFollowSerializer
from .models import MyUser

from .serializers import UserFollowingCountSerializer
from .models import UserFollowingCount

from .serializers import WatchListSerializer
from .models import WatchList

from .serializers import TopicSerializer
from .models import Topic

from .serializers import VideoTopicSerializer
from .serializers import VideoThumbnailSerializer
from .serializers import VideoLikesDislikesSerializer

from .serializers import VideoSerializer
from .models import Video

from .serializers import CommentSerializer
from .models import Comment

class MyUserListCreateApiView(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = MyUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'username'


    def get_queryset(self):
        self.username = get_object_or_404(MyUser, username=self.kwargs['username'])
        return MyUser.objects.filter(username=self.username)

    def perform_update(self, serializer):
        return super().perform_update(serializer)


class UserFollowingCountRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserFollowingCountSerializer
    lookup_field = 'owner'

    def get_queryset(self):
        self.list = UserFollowingCount.objects.get_or_create(owner=MyUser.objects.get(id=self.kwargs['owner']))
        return UserFollowingCount.objects.filter(owner=self.list[0].owner.id)

class MyUserFollowRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MyUserFollowSerializer
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        print(request.data)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return MyUser.objects.filter(username=self.kwargs['username'])


class MyUserProfileImageRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = MyUserProfileImageSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return MyUser.objects.filter(id=self.kwargs['id'])

class MyUserUsernameProfileImageRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = MyUserProfileImageSerializer
    lookup_field = 'username'

    def get_queryset(self):
        return MyUser.objects.filter(username=self.kwargs['username'])


class WatchListListCreateApiView(generics.ListCreateAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)

class TopicListCreateApiView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class VideoListCreateApiView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class VideoTopicCreateApiView(generics.CreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoTopicSerializer

    def post(self, request, format=None):
        serializer = VideoTopicSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class VideoThumbnailRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = VideoThumbnailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs['id'])


class VideoLikesDislikesRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = VideoLikesDislikesSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs['id'])




class VideoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    lookup_field = 'user'

    def get_queryset(self):
        return Video.objects.filter(user=self.kwargs['user'])


class VideoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VideoSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Video.objects.filter(id=self.kwargs['id'])

    def update(self, request, *args, **kwargs):
        print(request.data)
        return super().update(request, *args, **kwargs)


class CommentListCreateApiView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class VideoCommentsListCreateApiView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    lookup_field = 'video_id'

    def get_queryset(self):
        return Comment.objects.filter(video=self.kwargs['video_id'])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer