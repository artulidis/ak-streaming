from django.urls import path
from . import views

urlpatterns = [
    path('publish-auth/', views.InternalPublishAuthView.as_view(), name='publish-auth'),
    path('publish-end/', views.InternalPublishEndView.as_view(), name='publish-end'),
]