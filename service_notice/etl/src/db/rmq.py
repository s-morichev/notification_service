import logging

import pika


class RabbitMQ:
    def __init__(self, uri: str):
        logging.debug("start rabbitmq")

        parameters = pika.URLParameters(uri)
        self.connection = pika.BlockingConnection(parameters=parameters)

    def close(self):
        if self.connection:
            self.connection.close()
            logging.debug("close rabbitmq")


db: RabbitMQ | None = None
