from channels.consumer import AsyncConsumer
import json
from datetime import date, datetime, timedelta
from channels.db import database_sync_to_async
from api.models import Comment, MyUser, Video

class LiveChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):

        stream_chat = f"stream_{self.scope['url_route']['kwargs']['id']}"
        self.stream_chat = stream_chat
        await self.channel_layer.group_add(
            stream_chat,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept"
        })

        print("connect", event)

    async def websocket_receive(self, event):
        front_text = event.get('text', None)
        if front_text is not None:
            message_data = json.loads(front_text)
            message = message_data.get('body')

            new_message = await self.create_message(message)

            response = {
                'user': new_message.user.username,
                'body': new_message.body,
                'video': new_message.video.id,
                'created': str(new_message.created)
            }

            await self.channel_layer.group_send(
                self.stream_chat,
                {
                    'type': 'message_event',
                    'text': json.dumps(response)
                }
            )

        print("receive", message_data["user"])
    
    async def message_event(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def websocket_error(self, event):
        print("error", event)

    async def websocket_disconnect(self, event):
        print("disconnect", event)

    @database_sync_to_async
    def create_message(self, body):
        video = Video.objects.get(id=self.scope['url_route']['kwargs']['id'])
        user = MyUser.objects.get(username=self.scope['url_route']['kwargs']['username'])
        return Comment.objects.create(video=video, user=user, body=body)