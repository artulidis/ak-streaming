from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user_from_token(raw_token):
    authenticator = JWTAuthentication()
    validated_token = authenticator.get_validated_token(raw_token)
    return authenticator.get_user(validated_token)


class QueryStringJWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope.get('query_string', b'').decode())
        raw_token = query_string.get('token', [None])[0]

        if raw_token:
            try:
                scope['user'] = await get_user_from_token(raw_token)
            except (AuthenticationFailed, InvalidToken, TokenError):
                scope['user'] = AnonymousUser()
        else:
            scope.setdefault('user', AnonymousUser())

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return AuthMiddlewareStack(QueryStringJWTAuthMiddleware(inner))