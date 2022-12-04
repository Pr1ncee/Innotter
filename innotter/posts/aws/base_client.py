import boto3
from boto3.resources.base import ServiceResource
from django.conf import settings


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
            client = boto3.client(service_name, region_name=settings.AWS_REGION_NAME)
            setattr(cls, '_client', client)
        return getattr(cls, '_client')
