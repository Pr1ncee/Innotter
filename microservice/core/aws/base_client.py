import sys

sys.path.append('/app/microservice/')

import boto3
from boto3.resources.base import ServiceResource

from core.settings import settings


class ClientMeta(type):
    """
    Metaclass for AWS services.
    """
    @property
    def client(cls) -> ServiceResource:
        """
        Return a low-level service client by name of inheriting service.
        """
        if not getattr(cls, '_client', None):
            service_name = getattr(cls, '_service_name')
            client = boto3.client(
                service_name,
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            setattr(cls, '_client', client)
        return getattr(cls, '_client')
