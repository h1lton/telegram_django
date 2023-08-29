import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import *


# docker run --rm -p 6379:6379 redis:7

class ChatConsumerMixin:
    def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            self.close()
            return
        
        self.methods = {
            'add_message': self.add_message,
            'delete_message': self.delete_message,
            'edit_message': self.edit_message,
        }
        
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        chat_type = self.scope['path'].split('/')[2] # self.scope['path'] выглядит так: '/ws/private/2/
        self.room_group_name = f'{chat_type}_{self.chat_id}' # например private_1 
        if chat_type == 'private':
            chat = PrivateChat.objects.filter(id=self.chat_id, users__in=[self.user])
        else:
            chat = PublicChat.objects.filter(id=self.chat_id) # сделать проверку на то что юзер входит в группу/канал

        if chat:
            self.chat = chat[0]
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    @staticmethod
    def message_serializer(message: Message):
        return {
            'id': message.id,
            'sender': str(message.sender.username),
            'text': message.text,
            'time_create': str(message.time_create),
        }


class ChatConsumer(ChatConsumerMixin, WebsocketConsumer):
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        method = text_data_json['method']
        print(f'Receive method: {method}')

        func = self.methods[method]
        func(text_data_json)

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


class PublicChatConsumer(ChatConsumerMixin, WebsocketConsumer):
    def connect(self):
        super().connect()
        self.is_admin = self.chat.is_admin(self.user)
        self.send(text_data=json.dumps({ 
            'method': 'initialize',
            'chat_type': self.chat.type, 
            'is_admin': self.is_admin,
        })) 

    def receive(self, text_data):
        if self.chat.type == 1 and not self.is_admin:
            return # запрет в каналах на удаление, добавление и редактирование сообщений пользователям без админки

        text_data_json = json.loads(text_data)
        method = text_data_json['method']

        func = self.methods[method]
        func(text_data_json)

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
        self.send(text_data=json.dumps({
            'method': 'add_message',
            'message': message,
        }))


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
