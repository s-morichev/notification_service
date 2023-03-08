import json
from abc import abstractmethod, ABC

import backoff as backoff
from aio_pika import connect, Message
from aiormq import AMQPConnectionError


class BaseProducer(ABC):
    @abstractmethod
    async def connect_broker(self, *args):
        pass

    @abstractmethod
    async def publish(self, *args):
        pass


class RabbitMQ(BaseProducer):
    def __init__(self, dsn):
        self.dsn = dsn
        self.connection = None

    @backoff.on_exception(backoff.expo, AMQPConnectionError, max_time=60, raise_on_giveup=True)
    async def connect_broker(self):
        self.connection = await connect(self.dsn)
        return True

    async def close(self):
        try:
            await self.connection.close()
        except Exception as e:
            raise e

    async def publish(self, queue_name: str, message: dict) -> str:
        async with self.connection:
            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            await channel.default_exchange.publish(
                Message(body=json.dumps(message).encode('utf-8')),
                routing_key=queue.name)
            return "Message sent"
