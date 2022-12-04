import json

from django.conf import settings
import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.exceptions import AMQPConnectionError

from .enum_objects import PostMethods, PageMethods

username = settings.RABBITMQ_DEFAULT_USER
password = settings.RABBITMQ_DEFAULT_PASS
host = settings.RABBITMQ_HOST
port = settings.RABBITMQ_PORT
heartbeat, timeout = 600, 300
exchange = settings.RABBITMQ_EXCHANGE_NAME


class ClientMeta(type):
    """
    Metaclass for pika client
    """
    @property
    def channel(cls) -> BlockingConnection | None:
        """
        Return either connection object or NoneType. Depend on whether the channel is opened or not.
        """
        if not getattr(cls, '_channel', None):
            try:
                creds = pika.PlainCredentials(username=username, password=password)
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=host,
                    port=port,
                    credentials=creds,
                    heartbeat=heartbeat,
                    blocked_connection_timeout=timeout)
                )
                new_channel = connection.channel()
                setattr(cls, '_channel', new_channel)
            except AMQPConnectionError:
                pass
        return getattr(cls, '_channel')


class PikaClient(metaclass=ClientMeta):
    """
    pika package wrapper
    '_channel' is a variable that stores connection object if the latter exists
    """
    _channel = None
    _routing_key = None

    @classmethod
    def routing_key(cls, value):
        cls._routing_key = value

    @classmethod
    def publish(cls, method: PostMethods | PageMethods, body: dict) -> None:
        """
        Publish given data to the RabbitMQ exchange. Add properties based on method type
        :param method: method type
        :param body: payload of the message
        :return: None
        """
        properties = pika.BasicProperties(method.value)
        cls.channel.basic_publish(
            exchange=exchange,
            routing_key=cls._routing_key,
            body=json.dumps(body),
            properties=properties
        )
