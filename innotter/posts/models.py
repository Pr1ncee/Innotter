from user.models import User
from django.db import models


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
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='pages', blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField(User, related_name='follows', blank=True)
    follow_requests = models.ManyToManyField(User, related_name='requests', blank=True)

    is_private = models.BooleanField(default=False)

    image = models.URLField(null=True, blank=True)

    unblock_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Post(BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=False, blank=False, related_name='posts')
    title = models.CharField(max_length=50, default='Default Title')
    content = models.CharField(max_length=200, blank=True)
    reply_to = models.ForeignKey('posts.Post', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='replies')

    def __str__(self):
        return self.title

