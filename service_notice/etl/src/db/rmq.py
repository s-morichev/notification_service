import logging

import pika


class RabbitMQ:
    def __init__(self, uri: str):
        logging.debug("start rabbitmq")

        parameters = pika.URLParameters(uri)
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue="notice")

    def close(self):
        if self.connection:
            self.connection.close()
            logging.debug("close rabbitmq")


db: RabbitMQ | None = None
