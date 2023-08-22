import time

from chat.models import *
from django.db import connection


# from terminal_assistant import *


def time_of_function(function):
    def wrapped(*args):
        start_time = time.perf_counter_ns()
        res = function(*args)
        final_time = time.perf_counter_ns() - start_time
        print("{:,}".format(final_time))
        return res

    return wrapped


def get_default_users():
    """Возвращает пользователей с username 'admin' & 'user_1'"""
    users = (get_admin(), get_user('user_1'))
    return users


def create_default_users():
    """создаёт superuser'а с username 'admin' и user'а с username 'user_1'"""
    users = (create_admin(), create_user('user_1'))
    return users


def get_admin():
    """Возвращает пользователя с username 'admin', по умолчанию это superuser."""
    user = User.objects.get(username='admin')
    print('Success')
    return user


def create_admin():
    """создаёт superuser'а с username 'admin' и паролем 'admin', по умолчанию уже создан."""
    user = User.objects.create_superuser(username='admin', password='admin')
    print('Success')
    return user


def get_user(username):
    """Возвращает пользователя с username 'username'"""
    user = User.objects.get(username=username)
    print('Success')
    return user


def create_user(username):
    """создаёт user'а c username 'username' и паролем 'admin'"""
    user = User.objects.create_user(username=username, password='admin')
    print('Success')
    return user


def num_queries():
    """
    Возвращает кол-во запросов в бд, удобно ставить перед и после функцией или чем то другим,
    что бы посмотреть сколько запросов оно совершает.
    Можно из этого сделать декоратор, если вас такой вариант не устроит.
    """
    return len(connection.queries)


def test_get_chat(url_uniquename, user):
    url_user = User.objects.filter(username=url_uniquename)
    if url_user:
        chat = PrivateChat.objects.filter(users__in=[url_user[0], user])
        if chat:
            return chat[0]
        else:
            return PrivateChat.objects.create().users.set((url_user[0], user))
    else:
        return PublicChat.objects.get(name=url_uniquename)
