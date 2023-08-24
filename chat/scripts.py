from django.shortcuts import get_object_or_404

from .models import *


def get_chat(chat_name, user):
    """
    Если 'chat_name' будет моделью 'User' то мы возвращаем или создаём модель 'PrivateChat' в ином случае
    возвращаем модель 'PublicChat' если её нет, вызываем Http404.
    """
    url_user = User.objects.filter(username=chat_name)
    if url_user:
        chat = PrivateChat.objects.filter(users=url_user[0]).filter(users=user)
        if chat:
            return chat[0]
        else:
            chat = PrivateChat.objects.create()
            chat.users.add(url_user[0], user)
            return chat
    else:
        return PublicChat.objects.get(name=chat_name)
