from django.db import models

from posts.managers import PageManager, PostManager
from user.models import User


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=32, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='pages', blank=True, null=True)
    image = models.CharField(max_length=1024, null=True, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField(User, related_name='follows', blank=True)
    follow_requests = models.ManyToManyField(User, related_name='requests', blank=True)

    is_private = models.BooleanField(default=False)

    unblock_date = models.DateField(null=True, blank=True)

    objects = models.Manager()
    pages_objects = PageManager()

    def __str__(self):
        return self.name


class Post(BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=False, blank=False, related_name='posts')
    title = models.CharField(max_length=50, default='Default Title')
    content = models.CharField(max_length=200, blank=True)
    reply_to = models.ForeignKey('posts.Post', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='replies')

    objects = models.Manager()
    posts_objects = PostManager()

    def __str__(self):
        return self.title

