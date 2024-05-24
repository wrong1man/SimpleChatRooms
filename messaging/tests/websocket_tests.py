from channels.testing import WebsocketCommunicator
from channels.testing import HttpCommunicator
from SimpleChatRooms.asgi import application
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
import pytest
import json
from django.test import Client
import re

'''
This file tests:
1. Conversation creation via /start_chat/ http endpoint
2. Connection to Websocket
3. Sending a message to the Websocket
4. Receiving messages from the Websocket

not tested:
- Receiving (redis stored) chat history
- API throttling
'''

@pytest.mark.asyncio
@database_sync_to_async
def create_user(username, password):
    user = get_user_model().objects.create_user(username=username, password=password)
    return user


@pytest.mark.asyncio
@database_sync_to_async
def start_conversation(user1, user2):
    client = Client()
    client.force_login(user1)
    response = client.get(f'/start_chat/?target_user={user2.id}')
    # replace '/start_chat/' with your actual start chat URL
    # assumes the response contains the conversation ID
    if response.status_code == 200:
        match = re.search(r'window.conversationId = (\d+);', response.content.decode())
        if match:
            conversation_id = match.group(1)
            return conversation_id
        else:
            raise ValueError("Could not find conversation ID in JavaScript code")
    if response.status_code == 200:
        return json.loads(response.content)['conversation_id']
    else:
        raise ValueError("Could not start conversation")


@pytest.mark.asyncio
async def auth_connect(user, conversation_id):
    communicator = WebsocketCommunicator(application, f'/ws/userchat/{conversation_id}/')
    communicator.scope['user'] = user
    connected, _ = await communicator.connect()
    assert connected is True
    return communicator


@pytest.mark.asyncio
async def test_can_send_and_receive_messages():
    user1 = await create_user('testuser1111', 'testpass')
    user2 = await create_user('testuser2222', 'testpass')
    conversation_id = await start_conversation(user1, user2)
    print(f"Started conversation: {conversation_id} - PASS")
    communicator = await auth_connect(user1, conversation_id)
    print(f"Connected to Websocket - PASS")
    await communicator.send_json_to({'message': 'Hello'})
    print(f"Sent message to Websocket - PASS")
    response = await communicator.receive_json_from()
    assert response['message'] == 'Hello'
    print(f"Received message from Websocket - PASS")

    await communicator.disconnect()
    await cleanup(user1, user2)


@pytest.mark.asyncio
@database_sync_to_async
def cleanup(user1,user2):
    user1.delete()
    user2.delete()