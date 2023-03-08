import logging
from functools import partial

import backoff
import pika
from pika.exceptions import AMQPConnectionError
from pydantic import ValidationError

import logging_config  # noqa
from config import settings
from models import EmailNotification
from senders import DebugSender, SendgridSender

logger = logging.getLogger(__name__)


@backoff.on_exception(
    backoff.expo,
    AMQPConnectionError,
    max_time=60,
    backoff_log_level=logging.ERROR,
    raise_on_giveup=True,
    logger=logger,
)
def init_rabbit():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(username=settings.RABBITMQ_USER, password=settings.RABBITMQ_PASSWORD),
        )
    )
    channel = connection.channel()
    return channel


def send_email(channel, method, properties, body, sender=None):
    try:
        notification = EmailNotification.parse_raw(body)
    except ValidationError:
        logger.exception("Error on parsing body %s", body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    sender.send(notification)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    if settings.DEBUG:
        sender = DebugSender()
    else:
        sender = SendgridSender()
    callback = partial(send_email, sender=sender)

    channel = init_rabbit()
    channel.queue_declare(queue=settings.EMAIL_QUEUE)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.EMAIL_QUEUE, on_message_callback=callback)

    logger.info("Start listening on channel %s", settings.EMAIL_QUEUE)
    channel.start_consuming()


if __name__ == "__main__":
    main()
