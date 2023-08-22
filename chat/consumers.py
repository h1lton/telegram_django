import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import *


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            self.close()

        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        if self.scope['url_route']['kwargs']['chat_type'] == 'private':
            self.room_group_name = f'private_{self.chat_id}'
            self.chat = PrivateChat.objects.filter(id=self.chat_id, users__in=[self.user])
        else:
            self.room_group_name = f'public_{self.chat_id}'
            self.chat = PublicChat.objects.filter(id=self.chat_id, users__in=[self.user])

        if self.chat:
            self.chat = self.chat[0]
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # todo: сделать словарь с методами на method
        message = text_data_json['message']
        Message.objects.create(sender=self.user, chat=self.chat, text=message)
        sender, message = self.user.username, message
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message,
                'sender': sender
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        sender = event['sender']
        message = event['message']
        print(event, 2)
        # Send message to WebSocket
        self.send(text_data=json.dumps({'sender': sender, 'message': message}))
