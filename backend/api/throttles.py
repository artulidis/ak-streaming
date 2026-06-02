from rest_framework.throttling import SimpleRateThrottle, UserRateThrottle


class IdentRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class RegistrationRateThrottle(IdentRateThrottle):
    scope = 'registration'


class LoginRateThrottle(IdentRateThrottle):
    scope = 'login'


class TokenRefreshRateThrottle(IdentRateThrottle):
    scope = 'token_refresh'


class TokenRevokeRateThrottle(IdentRateThrottle):
    scope = 'token_revoke'


class ReactionWriteRateThrottle(UserRateThrottle):
    scope = 'reaction_write'


class MessageWriteRateThrottle(UserRateThrottle):
    scope = 'message_write'


class WebsocketThrottleRequest:
    def __init__(self, *, user, video_id):
        self.user = user
        self.video_id = video_id


class WebsocketMessageRateThrottle(SimpleRateThrottle):
    scope = 'websocket_message_write'

    def get_cache_key(self, request, view):
        user = getattr(request, 'user', None)
        video_id = getattr(request, 'video_id', None)

        if user is None or not getattr(user, 'is_authenticated', False) or video_id is None:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': f'{user.pk}:{video_id}',
        }