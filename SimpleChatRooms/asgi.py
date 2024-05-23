"""
ASGI config for SimpleChatRooms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SimpleChatRooms.settings')
#
# application = get_asgi_application()

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from .routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SimpleChatRooms.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(AuthMiddlewareStack(URLRouter(
        websocket_urlpatterns
    ),))
})
