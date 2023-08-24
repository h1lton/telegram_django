import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import *


# docker run --rm -p 6379:6379 redis:7


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            self.close()

        self.methods = {
            'add_message': self.add_message,
            'delete_message': self.delete_message,
            'edit_message': self.edit_message,
        }

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
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        method = text_data_json['method']
        print('Receive method: ')

        func = self.methods[method]
        func(text_data_json)

    @staticmethod
    def message_serializer(message: Message):
        return {
            'id': message.id,
            'sender': str(message.sender.username),
            'text': message.text,
            'time_create': str(message.time_create),
        }

    def add_message(self, event):
        text = event['text']
        message = Message.objects.create(sender=self.user, chat=self.chat, text=text)
        serialized_message = self.message_serializer(message)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'add.group.message',
                'message': serialized_message,
            }
        )

    def add_group_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(
            {
                'message': message,
                'method': 'add_message'
            }
        ))

    def edit_message(self, event):
        text = event['text']
        message_id = int(event['message_id'])
        message = Message.objects.get(id=message_id)
        if message.chat == self.chat:
            message.text = text
            message.is_edited = True
            # todo: добавить отслеживание отредактировано ли поле в template
            message.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'edit.group.message',
                    'message_id': message_id,
                    'text': text,
                }
            )

    def edit_group_message(self, event):
        message_id = event['message_id']
        text = event['text']
        self.send(text_data=json.dumps(
            {
                'method': 'edit_message',
                'message_id': message_id,
                'text': text,
            }
        ))

    def delete_message(self, event):
        message_id = event['message_id']
        message = Message.objects.get(id=message_id)
        if message.chat == self.chat:
            message.delete()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'delete.group.message',
                    'message_id': message_id
                }
            )

    def delete_group_message(self, event):
        message_id = event['message_id']
        self.send(text_data=json.dumps(
            {
                'message_id': message_id,
                'method': 'delete_message',
            }
        ))
