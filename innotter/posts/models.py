from user.models import User
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='pages')

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField(User, related_name='follows')
    follow_requests = models.ManyToManyField(User, related_name='requests')

    is_private = models.BooleanField(default=False)

    image = models.URLField(null=True, blank=True)

    unblock_date = models.DateField(null=True, blank=True)


class Post(BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')

    content = models.CharField(max_length=200)
    reply_to = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, related_name='replies')

