from enum import Enum


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

