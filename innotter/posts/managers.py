from datetime import date

from django.db import models

from user.models import User


class PageManager(models.Manager):
    """
    Custom Page model Manager.
    """
    def get_user_pages(self, user_id: int):
        """
        Return user's pages.
        """
        return super().get_queryset().filter(owner=user_id)

    def get_valid_pages(self):
        """
        Return pages with non-blocked owners, that aren't blocked and private.
        """
        return super().get_queryset().exclude(owner__is_blocked=True)\
                                     .exclude(unblock_date__gt=date.today())\
                                     .exclude(is_private=True)

    def get_all_valid_pages(self):
        """
        Return pages with non-blocked owners and that aren't blocked.
        """
        return super().get_queryset().exclude(owner__is_blocked=True).exclude(unblock_date__gt=date.today())


class PostManager(models.Manager):
    """
    Custom Post model Manager.
    """
    def get_user_posts(self, user_id: int):
        """
        Return user's posts.
        """
        return super().get_queryset().filter(page__owner_id=user_id)

    def get_liked_posts(self, user: User):
        """
        Return QuerySet with user's liked posts.
        """
        return super().get_queryset().filter(liked_by=user)

    def get_valid_posts(self):
        """
        Return posts with non-blocked owners, that aren't blocked and private.
        """
        return super().get_queryset().exclude(page__owner__is_blocked=True)\
                                     .exclude(page__unblock_date__gt=date.today())\
                                     .exclude(page__is_private=True)

    def get_feed_posts(self, user: User):
        """
        Filter posts based on both user's posts and followed pages.
        Each post belongs to a certain page. Following page means following post as well.

        'user': user who made a request.
        'my_posts': Queryset object which is made of user's posts.
        'followed_posts': Queryset object which is made of valid followed posts.
        'queryset': Queryset object which is a distinct union of 'my_posts' & 'followed_posts'
                    firstly ordered by created date and secondly by id (both descending).
        """
        my_posts = super().get_queryset().filter(page__owner=user)
        followed_posts = super().get_queryset().filter(page__followers=user)\
                                               .exclude(page__unblock_date__gt=date.today())

        queryset = (my_posts | followed_posts).distinct().order_by('-created_at', '-id')
        return queryset
