from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.exceptions import NotAuthenticated, Throttled, ValidationError

from api.auth_helpers import ensure_authenticated_user
from api.serializers import ChatMessageReadSerializer, ChatMessageWriteSerializer
from api.services import create_video_message
from api.streaming import get_active_stream_session
from api.throttles import WebsocketMessageRateThrottle, WebsocketThrottleRequest

class LiveChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.video_id = self.scope['url_route']['kwargs']['id']
        self.stream_chat = f"stream_{self.video_id}"

        if not getattr(self.scope.get('user'), 'is_authenticated', False):
            await self.close(code=4401)
            return

        if not await self.has_active_stream_session():
            await self.close(code=4404)
            return

        await self.channel_layer.group_add(self.stream_chat, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'stream_chat'):
            await self.channel_layer.group_discard(self.stream_chat, self.channel_name)

    async def receive_json(self, content, **kwargs):
        try:
            message_payload = await self.create_message_payload(content)
        except NotAuthenticated:
            await self.close(code=4401)
            return
        except ValidationError as exc:
            await self.send_json({'errors': exc.detail})
            return
        except Throttled as exc:
            response = {'errors': {'message': ['Too many chat messages.']}}
            wait = exc.wait()
            if wait is not None:
                response['retry_after'] = wait
            await self.send_json(response)
            return

        await self.channel_layer.group_send(
            self.stream_chat,
            {
                'type': 'chat.message',
                'message': message_payload,
            },
        )

    async def chat_message(self, event):
        await self.send_json(event['message'])

    @database_sync_to_async
    def has_active_stream_session(self):
        return get_active_stream_session(video_id=self.video_id) is not None

    @database_sync_to_async
    def create_message_payload(self, content):
        user = ensure_authenticated_user(self.scope.get('user'))

        throttle = WebsocketMessageRateThrottle()
        throttle_request = WebsocketThrottleRequest(user=user, video_id=self.video_id)

        if not throttle.allow_request(throttle_request, None):
            raise Throttled(wait=throttle.wait())

        serializer = ChatMessageWriteSerializer(
            data={'message': content.get('body', '') if isinstance(content, dict) else ''}
        )
        serializer.is_valid(raise_exception=True)

        message = create_video_message(
            user=user,
            video_id=self.video_id,
            message=serializer.validated_data['message'],
        )
        return ChatMessageReadSerializer(message).data