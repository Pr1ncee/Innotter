from typing import BinaryIO

import boto3
from django.core.files.uploadedfile import InMemoryUploadedFile


file_obj_type = InMemoryUploadedFile | BinaryIO


class ClientMeta(type):
    """
    Metaclass for AWS services.
    """
    @property
    def client(cls):
        """
        Return a low-level service client by name of inheriting service.
        """
        if not getattr(cls, '_client', None):
            service_name = getattr(cls, '_service_name')
            client = boto3.client(service_name)
            setattr(cls, '_client', client)
        return getattr(cls, '_client')


class S3Client(metaclass=ClientMeta):
    """
    Wrapper of AWS S3 service using boto3.
    'upload_path' returns endpoint of storing file object (i.e. "some_directory/some_image.png")
    'get_file_url' returns full path to stored file object.
    """
    _service_name = 's3'
    _url = "https://{}.s3.{}.amazonaws.com/{}"
    _client = None

    @classmethod
    def upload_fileobj(cls, file_obj: file_obj_type, bucket_name: str, upload_path: str) -> None:
        """
        Put the given object to the specified bucket at S3.
        :param file_obj: file object to be saved.
        :param bucket_name: name of the storage.
        :param upload_path: path that consist of directories the file will be saved in and file name.
        :return: None.
        """
        return cls.client.upload_fileobj(file_obj, bucket_name, upload_path)

    @classmethod
    def upload_path(cls, file_name: str, upload_dirs: list[str]) -> str:
        """
        Path that consists of directories the file will be saved in and file name.
        :param file_name: file name.
        :param upload_dirs: foregoing directories.
        :return: upload path.
        """
        full_upload_path = upload_dirs.copy()
        full_upload_path.append(file_name)
        return '/'.join(full_upload_path)

    @classmethod
    def get_file_url(cls, bucket_name: str, region_name: str, upload_path: str) -> str:
        """
        Create a full url to the given image.
        :param bucket_name: name of the storage.
        :param region_name: region name.
        :param upload_path: upload path. See above.
        :return: full url.
        """
        return cls._url.format(bucket_name, region_name, upload_path)
