from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex='^[a-z0-9_]+$',
            message=_('Only lowercase letters, numbers and underscores are allowed.')
        )]
    )
