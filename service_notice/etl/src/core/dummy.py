import random
import uuid
from datetime import datetime, timedelta, timezone

import pika

from core.models import Notice


def fake_data(rmq):
    channel = rmq.connection.channel()
    channel.queue_declare(queue="notice")
    channel.queue_purge(queue="notice")
    channel.queue_declare(queue="email")
    channel.queue_purge(queue="email")
    presents = ["медаль", "премию", "скидку 10%"]
    for i in range(10):
        notice = Notice(
            x_request_id=f'request_{i}',
            users=[uuid.uuid4() for i in range(random.randint(1, 10))],
            notice_id=uuid.uuid4(),
            template_id=f"default",
            transport="email",
            msg_type="promo",
            extra={"present": random.choice(presents)},
            expire_at=datetime.now(tz=timezone.utc) + timedelta(hours=2),
        )
        ttl = int((notice.expire_at - datetime.now(tz=timezone.utc)).total_seconds())
        properties = pika.BasicProperties(expiration=str(ttl * 1000))
        channel.basic_publish(exchange="", routing_key="notice", properties=properties, body=notice.json())
