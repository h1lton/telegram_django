from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .scripts import get_chat


@login_required
def chat_view(request, chat_name):
    chat, chat_type = get_chat(chat_name, request.user)
    print(chat.id)
    return render(
        request,
        'index.html',
        {'chat': chat, 'chat_type': chat_type})
