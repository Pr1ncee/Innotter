from django.conf import settings
import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.exceptions import AMQPConnectionError


username = settings.RABBITMQ_DEFAULT_USER
password = settings.RABBITMQ_DEFAULT_PASS
host = settings.RABBITMQ_HOST
port = settings.RABBITMQ_PORT
heartbeat, timeout = 600, 300


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
