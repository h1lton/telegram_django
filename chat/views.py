from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .scripts import *


class ChatDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'chat'
    template_name = 'chat/index.html'

    def get_object(self, queryset=None):
        chat_name = self.kwargs.get('chat_name')
        try:
            chat = get_chat(chat_name, self.request.user)
        except:
            raise Http404('Chat with this name not found')

        return chat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat = self.get_object()
        context['messages'] = chat.messages.order_by('time_create')[:30]
        context['chat_type'] = 'private' if chat.__class__.__name__ == 'PrivateChat' else 'public'
        context['user'] = self.request.user
        return context
