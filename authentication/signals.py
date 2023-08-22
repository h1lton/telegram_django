from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from chat.models import PublicChat

User = get_user_model()


@receiver(pre_save, sender=User)
def validate_username(instance, **kwargs):
    if PublicChat.objects.filter(name=instance.username).exists():
        raise ValidationError('This username is already exists.')
