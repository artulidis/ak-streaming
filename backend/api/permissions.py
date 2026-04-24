from django.contrib.auth import get_user_model
from rest_framework.permissions import SAFE_METHODS, BasePermission

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