# from django.shortcuts import render
from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.auth import _get_user_session_key
import json

# from channels.db import database_sync_to_async


class UserChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = 'chat_%s' % self.room_name
        user=self.scope['user']
        # print(user, user.id, user.is_authenticated)
        # print(self.scope)
        if not user.is_authenticated:
            return await self.close()
            # return {"error":"Not authenticated"}
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender']
        # print(f"{sender_id}: {message}")

        # Send message to connected users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender':sender_id,
            }
        )

        # Receive message from room group

    async def chat_message(self, event):
        message = event['message']
        sender_id=event['sender']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender':sender_id,
        }))