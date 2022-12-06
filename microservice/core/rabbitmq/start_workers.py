import sys

sys.path.append('/app/microservice/core/')

from core.rabbitmq.consumer import PikaClient
from core.settings import settings


pika_worker = PikaClient


def start_workers():
    while True:
        pika_worker.start_consumer(settings.ROUTING_KEY)


start_workers()
