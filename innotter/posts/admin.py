from django.contrib import admin

from posts.models import Tag, Post, Page


admin.site.register([Tag, Post, Page])
