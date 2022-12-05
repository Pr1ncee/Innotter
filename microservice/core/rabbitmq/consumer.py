import sys

sys.path.append('/app/microservice/core/')

import json
from warnings import warn

from botocore.exceptions import ClientError
import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.channel import Channel
from pika.exceptions import AMQPConnectionError, StreamLostError, ChannelWrongStateError
from pika.spec import BasicProperties, Basic

from aws.dynamodb_client import DynamoDBClient
from domain.enum_objects import PageMethods, PostMethods, UserMethods
from settings import settings


db = DynamoDBClient


class ClientMeta(type):
    """
    Metaclass for pika clients
    """
    @property
    def channel(cls) -> BlockingConnection | None:
        """
        Return either connection object or NoneType. Depend on whether the exception raised or not.
        """
        if not getattr(cls, '_channel', None):
            try:
                creds = pika.PlainCredentials(username=settings.USERNAME, password=settings.PASSWORD)
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=settings.HOST,
                    port=settings.PORT,
                    credentials=creds,
                    heartbeat=settings.HEARTBEAT,
                    blocked_connection_timeout=settings.TIMEOUT)
                )
                new_channel = connection.channel()
                setattr(cls, '_channel', new_channel)
            except AMQPConnectionError:
                warn("The message broker hasn't started yet")
        return getattr(cls, '_channel')


class PikaClient(metaclass=ClientMeta):
    _channel = None
    _queue = None

    @classmethod
    def callback(
            cls,
            channel: Channel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
    ):
        payload = json.loads(body)
        cls.save_data(payload, properties.content_type)

    @classmethod
    def start_consumer(cls, queue: str) -> None:
        """
        Take queue name and start consuming message from it, at the same time
        catching such exceptions as emtpy deque, invalid queue name and internal connection errors
        :param queue: queue name to connect
        :return: None
        """
        cls._queue = queue
        try:
            cls.channel.basic_consume(cls._queue, on_message_callback=cls.callback, auto_ack=True)
            cls.channel.start_consuming()
        except (StreamLostError, ChannelWrongStateError, AttributeError):
            warn('No items in the deque or queue name may be invalid')

    @classmethod
    def stop_consumer(cls):
        """
        Stop consuming and close the current channel.
        """
        try:
            cls.channel.stop_consuming()
            cls.channel.close()
        except TypeError:
            warn("You must firstly start the workers")

    @staticmethod
    def preprocessing_data(data: dict, update=False) -> dict:
        """
        Represent the given data in appropriate formatting rules
        :param data: data to be saved
        :param update: represents the given data according to the 'update' method formatting rules in boto3
        :return: processed data.
        """
        processed_data = {field: {(pk_type_and_str := db.target_pk_type(value))[0]: pk_type_and_str[1]}
                          for (field, value) in data.items()}
        if update:
            return {field: {'Value': value} for (field, value) in processed_data.items()}
        return processed_data

    @staticmethod
    def save_data(data: dict, method: str):
        """
        Call the appropriate method based on given method type.
        Get primary key 'id', 'cause the tables have the same pk 'id'
        :param data: data to be saved
        :param method: method type (e.g. 'update_posts')
        :return:
        """
        process_function = PikaClient.preprocessing_data
        pk = settings.PK
        target_pk = int(data.get('id'))  # Convert to state the primary key's type
        routing_key = method.split('_')[-1]  # ['update', 'posts'] -> 'posts'
        try:
            match method:
                case PostMethods.CREATE.value | PageMethods.CREATE.value | UserMethods.CREATE.value:
                    processed_data = process_function(data)
                    db.put_item(table_name=routing_key, item=processed_data)
                case \
                    PostMethods.UPDATE.value | \
                    PostMethods.LIKE.value | \
                    PageMethods.UPDATE.value | \
                    UserMethods.UPDATE.value:
                    processed_data = process_function(data, update=True)
                    db.update_item(
                        table_name=routing_key,
                        pk=pk,
                        target_pk=target_pk,
                        fields_to_update=processed_data
                    )
                case PostMethods.DELETE.value | PageMethods.DELETE.value:
                    db.delete_item(
                        table_name=routing_key,
                        pk=pk,
                        target_pk=target_pk
                    )
        except ClientError:
            warn("Operation has failed, the given data wasn't valid")
