from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models.models import UUIDTimestampModel
from django.contrib.auth.models import User
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, UUIDTimestampModel):
    username = None
    first_name = None
    last_name = None
    full_name = models.CharField(max_length=25, blank=True, null=True)
    display_name = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email' # Set email as the unique identifier
    is_online = models.BooleanField(default=False)
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

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
        upload_to='profile'
    )

    def __str__(self):
        return f"{self.user.full_name}'s Profile"