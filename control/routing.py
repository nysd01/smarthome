from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from control import consumers  # Make sure you have this file and MyConsumer defined

websocket_urlpatterns = [
    re_path(r'ws/somepath/$', consumers.MyConsumer.as_asgi()),
]
