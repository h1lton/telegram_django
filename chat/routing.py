from django.urls import re_path

from .consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/private/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'^ws/public/(?P<chat_id>\w+)/$', PublicChatConsumer.as_asgi())
]
