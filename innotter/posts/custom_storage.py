from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MediaStorage(S3Boto3Storage):
    """Custom storage for users' files using AWS S3"""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME