from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

app_name = 'api'

router = SimpleRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('topics', views.TopicViewSet, basename='topic')
router.register('videos', views.VideoViewSet, basename='video')

urlpatterns = [
    path('users/<str:username>/followers/', views.UserFollowerCollectionView.as_view(), name='user-follower-list'),
    path('users/<str:username>/following/', views.UserFollowingCollectionView.as_view(), name='user-following-list'),
    path('users/<str:username>/follow/', views.UserFollowStateView.as_view(), name='user-follow-state'),
    path('videos/<int:id>/reaction/', views.VideoReactionView.as_view(), name='video-reaction-detail'),
    path('videos/<int:id>/messages/', views.VideoMessageCollectionView.as_view(), name='video-message-list'),
    path('tokens/', views.CustomTokenObtainPairView.as_view(), name='token-list'),
    path('tokens/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh-detail'),
    path('tokens/revoke/', views.TokenRevokeView.as_view(), name='token-revoke-detail'),
] + router.urls