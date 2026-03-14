import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_email_confirmed = models.BooleanField(default=False)
    email_token = models.UUIDField(default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="Страна")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
