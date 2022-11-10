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
