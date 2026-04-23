from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('topics', views.TopicViewSet, basename='topic')
router.register('videos', views.VideoViewSet, basename='video')

urlpatterns = [
    path('users/<str:username>/followers/', views.UserFollowerCollectionView.as_view(), name='user-follower-list'),
    path('users/<str:username>/following/', views.UserFollowingCollectionView.as_view(), name='user-following-list'),
    path('users/<str:username>/videos/', views.UserVideoCollectionView.as_view(), name='user-video-list'),
    path('videos/<int:id>/reactions/', views.VideoReactionView.as_view(), name='video-reaction-list'),
    path('videos/<int:video_id>/messages/', views.VideoMessageCollectionView.as_view(), name='video-message-list'),
    path('tokens/', views.CustomTokenObtainPairView.as_view(), name='token-list'),
    path('tokens/refreshes/', TokenRefreshView.as_view(), name='token-refresh-list'),
] + router.urls