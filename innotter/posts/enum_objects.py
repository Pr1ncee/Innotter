from enum import Enum

from django.conf import settings


class Mode(Enum):
    """
    Represent the enumerated mods for accepting or denying follow requests.
    """
    DENY = 0
    ACCEPT = 1


class Directory(Enum):
    """
    Represent the enumerated directories at AWS S3 to save in.
    """
    PAGES = settings.AWS_PAGES_UPLOAD_DIR
    USERS = settings.AWS_USERS_UPLOAD_DIR


class PostMethods(Enum):
    """
    Define the methods which can change post's state
    """
    CREATE = 'create_posts'
    UPDATE = 'update_posts'
    LIKE = 'like_posts'
    DELETE = 'delete_posts'


class PageMethods(Enum):
    """
    Define the methods which can change page's state
    """
    CREATE = 'create_pages'
    UPDATE = 'update_pages'
    DELETE = 'delete_pages'


class UserMethods(Enum):
    """
    Define the methods which can change user's state
    """
    CREATE = 'create_users'
    UPDATE = 'update_users'
