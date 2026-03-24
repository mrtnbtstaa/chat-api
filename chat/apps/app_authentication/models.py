from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models.models import UUIDTimestampModel
from django.contrib.auth.models import User

class User(AbstractUser, UUIDTimestampModel):

    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    

class Profile(UUIDTimestampModel):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )

    picture = models.ImageField(
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"