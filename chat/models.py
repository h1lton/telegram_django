from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Message(models.Model):
    chat_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    chat_id = models.PositiveBigIntegerField()
    chat = GenericForeignKey('chat_type', 'chat_id')
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sender'
    )
    text = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} - {self.text}'


class PrivateChat(models.Model):
    users = models.ManyToManyField(User, related_name='private_chat_users')
    messages = GenericRelation(Message, object_id_field='chat_id', content_type_field='chat_type')


class PublicChat(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+\Z',
                message=_('Only lowercase letters, numbers and underscores are allowed.')
            )
        ]
    )
    type = models.SmallIntegerField(choices=((1, 'Channel'), (2, 'Group')))
    users = models.ManyToManyField(User, related_name='public_chat_users')
    admins = models.ManyToManyField(User, related_name='admins')
    messages = GenericRelation(Message, object_id_field='chat_id', content_type_field='chat_type')

    def is_admin(self, user):
        return self.admins.filter(id=user.id).exists()
