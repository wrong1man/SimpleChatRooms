from channels.generic.websocket import AsyncWebsocketConsumer
import json
from SimpleChatRooms.celery import app as celery_app
from django.utils import timezone, dateparse
import redis
import traceback
from django.conf import settings
# Time in seconds between messages for throttling
THROTTLE_SECONDS=2

# Number of messages to keep in REDIS cache
REDIS_MESSAGES_TO_KEEP = 100

REDIS_HOST=settings.REDIS_HOST
class UserChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize Redis instance
        self.redis_instance = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        timestamp = timezone.now()

        try:
            # Close the connection if user is not authenticated
            if not self.user.is_authenticated:
                return await self.close()

            # Add user to the group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Log user connection activity
            celery_app.send_task('messaging.tasks.log_activity',
                                  args=(self.user.id, f"[WS] User connected to chat {self.room_name}", timestamp))

            # Send the last 100 messages to the user
            last_messages = self.redis_instance.lrange(self.room_name, 0, 99)
            for message in reversed(last_messages):  # Reverse to maintain chronological order
                await self.send(text_data=message.decode())

        except Exception as e:
            # Log connection error
            celery_app.send_task('messaging.tasks.log_error',args=(self.user.id, traceback.format_exc(), f"connect", timestamp))
            raise e

    async def disconnect(self, close_code):
        try:
            # Remove user from the group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            # Log successful disconnection
            celery_app.send_task('messaging.tasks.log_activity',
                                  (self.user.id, f"[WS] User disconnected from chat {self.room_name}", timezone.now()))

        except Exception as e:
            # Log disconnection error
            celery_app.send_task('messaging.tasks.log_error',
                                  (self.user.id, traceback.format_exc(), f"disconnect", timezone.now()))
            raise e  # Re-raise the exception

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.user.id
        timestamp = timezone.now()

        # Message throttling
        # Get the timestamp of the last message sent by the user
        last_message_timestamp = self.redis_instance.get(f'messages:{sender_id}:last_timestamp')

        # If the user has sent a message in the last {THROTTLE_SECONDS} seconds, deny the call
        if last_message_timestamp and timestamp - dateparse.parse_datetime(last_message_timestamp.decode('utf-8')) < timezone.timedelta(seconds=THROTTLE_SECONDS):
            #print("THROTTLED!")
            await self.send(text_data=json.dumps({
                'error': 'You are sending messages too quickly. Please wait a moment before sending another message.',
            }))
            return
        #End of throttling section

        try:
            # Store last message timestamp for throttling
            self.redis_instance.set(f'messages:{sender_id}:last_timestamp', str(timestamp))

            # Send the message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender':sender_id,
                    'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            # Add the message to the conversation and log activit
            celery_app.send_task('messaging.tasks.add_message_to_conversation',(self.room_name,message,self.user.id,timestamp))#activity log performed within this task

            # Push the message to Redis
            self.redis_instance.lpush(self.room_name, json.dumps({'message': message, 'sender': sender_id,'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')}))
            # Trim list to last {REDIS_MESSAGES_TO_KEEP} messages
            self.redis_instance.ltrim(self.room_name, 0, REDIS_MESSAGES_TO_KEEP-1)
            # no need to block execution to await these methods.

        except Exception as e:
            # Log error in message receipt
            celery_app.send_task('messaging.tasks.log_error', (self.user.id, traceback.format_exc(), f"receive", timezone.now()))
            raise e  # Re-raise the exception


    async def chat_message(self, event):
        message = event['message']
        sender_id=event['sender']
        timestamp=event['timestamp']

        # Send the message to the user
        await self.send(text_data=json.dumps({
            'message': message,
            'sender':sender_id,
            'timestamp':timestamp,
        }))