from typing import BinaryIO

from botocore.exceptions import ClientError
from django.core.files.uploadedfile import InMemoryUploadedFile

from .base_client import ClientMeta


file_obj_type = InMemoryUploadedFile | BinaryIO


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
        Put the given object to the specified bucket at S3
        :param file_obj: file object to be saved
        :param bucket_name: name of the storage
        :param upload_path: path that consist of directories the file will be saved in and file name.
        :return: None.
        """
        return cls.client.upload_fileobj(file_obj, bucket_name, upload_path)

    @classmethod
    def upload_path(cls, file_name: str, upload_dirs: list[str]) -> str:
        """
        Path that consists of directories the file will be saved in and file name
        :param file_name: file name
        :param upload_dirs: foregoing directories.
        :return: upload path.
        """
        full_upload_path = upload_dirs.copy()
        full_upload_path.append(file_name)
        return '/'.join(full_upload_path)

    @classmethod
    def get_file_url(cls, bucket_name: str, region_name: str, upload_path: str) -> str:
        """
        Create an object url to the given image
        :param bucket_name: name of the storage
        :param region_name: region name.
        :param upload_path: upload path. See above.
        :return: object url.
        """
        return cls._url.format(bucket_name, region_name, upload_path)

    @classmethod
    def create_presigned_url(cls, bucket_name: str, upload_path: str, expiration: int = 3600) -> str | None:
        """
        Create a presigned url with expiration time to access the object at the remote storage
        :param bucket_name: name of the storage
        :param upload_path: upload path. See above.
        :param expiration: the time in which the url will be invalid.
        :return: generated presigned url .
        """
        presigned_url = None
        try:
            presigned_url = cls.client.generate_presigned_url('get_object',
                                                              Params={'Bucket': bucket_name,
                                                                      'Key': upload_path},
                                                              ExpiresIn=expiration)
        except ClientError:
            pass
        return presigned_url
