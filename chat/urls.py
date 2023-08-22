from django.urls import path

from . import views

urlpatterns = [
    path('<str:chat_name>', views.chat_view, name='chat_view'),
]
