# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/soccer/chat/(?P<room_name>[a-zA-Z]+[\-a-zA-Z]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/nba/chat/(?P<room_name>[a-zA-Z]+[\-a-zA-Z]+)/$', consumers.ChatConsumer.as_asgi()),
]