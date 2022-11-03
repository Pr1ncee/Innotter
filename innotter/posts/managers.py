from datetime import date

from django.db import models

from user.models import User


class PageManager(models.Manager):
    """
    Represents custom Page model Manager.
    """
    def get_user_pages(self, user_id: int):
        """
        Return given user's pages.
        """
        return super().get_queryset().filter(owner=user_id)

    def get_valid_pages(self):
        """
        Return pages that owner isn't blocked, themselves aren't blocked and aren't private.
        """
        return super().get_queryset().exclude(owner__is_blocked=True)\
                                     .exclude(unblock_date__gt=date.today()).exclude(is_private=True)

    def get_all_valid_pages(self):
        """
        Return pages that owner isn't blocked and pages themselves aren't blocked as well.
        :return:
        """
        return super().get_queryset().exclude(owner__is_blocked=True).exclude(unblock_date__gt=date.today())


class PostManager(models.Manager):
    """
    Represents custom Post model Manager.
    """
    def get_user_posts(self, user_id: int):
        """
        Return only owned posts by a given user.
        """
        return super().get_queryset().filter(page__owner_id=user_id)

    def get_liked_posts(self, user: User):
        """
        Return QuerySet with posts liked by a given user.
        """
        return super().get_queryset().filter(liked_by=user)

    def get_valid_posts(self):
        """
        Return posts that owner isn't blocked, pages aren't blocked and aren't private.
        """
        return super().get_queryset().exclude(page__owner__is_blocked=True)\
                                     .exclude(page__unblock_date__gt=date.today()).exclude(page__is_private=True)

    def get_feed_posts(self, user: User):
        """
        Filter posts based on both user's owned posts and followed pages.
        Each post belongs to a certain page. Follow page means follow post as well.

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
