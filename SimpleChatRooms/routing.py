from django.urls import re_path

from messaging.socket_consumer import *
websocket_urlpatterns = [
    re_path(r'ws/userchat/(?P<conversation_id>\w+)/$', UserChatConsumer.as_asgi()),
]