import json

from django.conf import settings
import pika

from innotter.posts.enum_objects import PostMethods, PageMethods
from .base_client import ClientMeta


exchange = settings.RABBITMQ_EXCHANGE_NAME


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
