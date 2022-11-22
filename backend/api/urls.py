from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('users/', views.MyUserListCreateApiView.as_view(), name='users'),
    path('user/<str:username>/', views.MyUserRetrieveUpdateDestroyAPIView.as_view(), name='user'),
    path('user/profile_image/<str:username>/', views.MyUserUsernameProfileImageRetrieveAPIView.as_view(), name='user_avatar'),

    path('followers/<str:username>/', views.MyUserFollowRetrieveUpdateAPIView.as_view(), name='user_followers'),
    path('following/<int:owner>/', views.UserFollowingCountRetrieveUpdateAPIView.as_view(), name='user_following'),

    path('subscription/<str:id>/', views.MyUserProfileImageRetrieveAPIView.as_view(), name='user_subscription_info'),
    
    path('watchlists/', views.WatchListListCreateApiView.as_view(), name='watchlists'),

    path('topics/', views.TopicListCreateApiView.as_view(), name='topics'),
    path('topics/<int:id>', views.TopicListCreateApiView.as_view(), name='topics'),

    path('videos/', views.VideoListCreateApiView.as_view(), name='videos'),
    path('videos/<int:user>/', views.VideoListCreateAPIView.as_view(), name='user_videos'),
    path('videos/post/topic/', views.VideoTopicCreateApiView.as_view(), name='videos_topic'),
    path('video/<int:id>/', views.VideoRetrieveUpdateDestroyAPIView.as_view(), name='video'),
    path('video/likes/<int:id>/', views.VideoLikesDislikesRetrieveUpdateAPIView.as_view(), name='video_likes'),
    path('video/thumbnail/<int:id>/', views.VideoThumbnailRetrieveUpdateAPIView.as_view(), name='video_thumbnail'),

    path('comments/', views.CommentListCreateApiView.as_view(), name='comments'),
    path('comments/<int:video_id>/', views.VideoCommentsListCreateApiView.as_view(), name='video_comments'),

    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]