from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    username = models.CharField(max_length=30, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True)
    image_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices, default=Roles.USER)
    is_blocked = models.BooleanField(default=False)
    liked = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name="lovers")
    refresh_token = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return self.username
