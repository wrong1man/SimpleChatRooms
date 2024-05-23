from channels.generic.websocket import AsyncWebsocketConsumer
import json
from celery import current_app
from django.utils import timezone
import redis
import traceback


class UserChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_instance = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user=self.scope['user']
        timestamp=timezone.now()
        try:
            if not self.user.is_authenticated:
                return await self.close()
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            current_app.send_task('messaging.tasks.log_activity',
                                  (self.user.id, f"[WS] User connected to chat {self.room_name}", timestamp))
            last_messages = self.redis_instance.lrange(self.room_name, 0, 99)
            for message in reversed(last_messages):  # Reverse to maintain chronological order
                await self.send(text_data=message.decode())
        except Exception as e:
            # Log connection error
            current_app.send_task('messaging.tasks.log_error',
                                  (self.user.id, traceback.format_exc(), f"[WS] connect", timestamp))
            raise e

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            # Log successful disconnection
            current_app.send_task('messaging.tasks.log_activity',
                                  (self.user.id, f"User disconnected from chat {self.room_name}", timezone.now()))

        except Exception as e:
            # Log disconnection error
            current_app.send_task('messaging.tasks.log_error',
                                  (self.user.id, traceback.format_exc(), f"disconnect", timezone.now()))
            raise e  # Re-raise the exception

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.user.id
        timestamp = timezone.now()
        try:
            # int("test")#forcing an error
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender':sender_id,
                    'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            current_app.send_task('messaging.tasks.add_message_to_conversation',(self.room_name,message,self.user.id,timestamp))#activity log performed within this task

            self.redis_instance.lpush(self.room_name, json.dumps({'message': message, 'sender': sender_id,'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')}))
            # Trim list to last 100 messages
            self.redis_instance.ltrim(self.room_name, 0, 99)
            # no need to block execution to await these methods.
        except Exception as e:
            # Log error in message receipt
            current_app.send_task('messaging.tasks.log_error', (self.user.id, traceback.format_exc(), f"receive", timezone.now()))
            raise e  # Re-raise the exception


    async def chat_message(self, event):
        message = event['message']
        sender_id=event['sender']
        timestamp=event['timestamp']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender':sender_id,
            'timestamp':timestamp,
        }))