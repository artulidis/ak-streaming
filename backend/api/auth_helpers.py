from rest_framework.exceptions import NotAuthenticated

from .serializers import ChatMessageWriteSerializer


def ensure_authenticated_user(user):
    if not getattr(user, 'is_authenticated', False):
        raise NotAuthenticated('Authentication credentials were not provided.')
    return user


def bind_authenticated_user(serializer, *, user, **extra_fields):
    actor = ensure_authenticated_user(user)
    return serializer.save(user=actor, **extra_fields)


def create_chat_message(*, user, video, message):
    serializer = ChatMessageWriteSerializer(data={'message': message})
    serializer.is_valid(raise_exception=True)
    return bind_authenticated_user(serializer, user=user, video=video)