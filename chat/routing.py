from django.urls import re_path

from .consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/(?P<chat_type>private|public)/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi())
]
