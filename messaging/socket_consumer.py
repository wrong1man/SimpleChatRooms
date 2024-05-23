# from django.shortcuts import render
from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.auth import _get_user_session_key
import json
from celery import current_app
from django.utils import timezone
import redis
# from channels.db import database_sync_to_async


class UserChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_instance = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user=self.scope['user']
        # print(user, user.id, user.is_authenticated)
        # print(self.scope)
        if not self.user.is_authenticated:
            return await self.close()
            # return {"error":"Not authenticated"}
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        last_messages = self.redis_instance.lrange(self.room_name, 0, 99)
        for message in reversed(last_messages):  # Reverse to maintain chronological order
            await self.send(text_data=message.decode())

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.user.id
        timestamp = timezone.now()
        # print(f"{sender_id}: {message}")

        # Send message to connected users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender':sender_id,
                'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        current_app.send_task('messaging.tasks.add_message_to_conversation',(self.room_name,message,self.user.id,timestamp))

        self.redis_instance.lpush(self.room_name, json.dumps({'message': message, 'sender': sender_id,'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')}))
        # Trim list to last 100 messages
        self.redis_instance.ltrim(self.room_name, 0, 99)
        # Receive message from room group

    async def chat_message(self, event):
        message = event['message']
        sender_id=event['sender']
        timestamp=event['timestamp']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender':sender_id,
            'timestamp':timestamp,
        }))