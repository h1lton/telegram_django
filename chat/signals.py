from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import PublicChat, Message

User = get_user_model()


@receiver(pre_save, sender=PublicChat)
def validate_name(instance, **kwargs):
    if User.objects.filter(username=instance.name).exists():
        raise ValidationError('This name is already exists.')
