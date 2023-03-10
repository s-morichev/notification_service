import logging
import time
import uuid

import orjson
import pika
from jinja2 import Template
from opentelemetry import trace

from core.models import Message, Notice, UserInfo
from core.constants import Mark, QUEUE_NOTICE, Transport
from db.rmq import RabbitMQ
from db.pg import get_template_from_db
from db.storage import get_mark, set_mark
from core.utils import get_ttl_from_datetime

# глушим вывод модуля rabbitmq, иначе он спамит в режиме debug
logging.getLogger("pika").setLevel(logging.WARNING)

tracer = trace.get_tracer(__name__)


def get_template(template_id: str) -> Template:
    template_str = get_template_from_db(template_id)
    return Template(template_str)


def get_user_info(user_id: uuid.UUID) -> UserInfo:
    return UserInfo(user_id=user_id, email="user@movies.com", username="Jon Doe", phone="5555-4444")


def mark_processed(notice_id, user_id, result=Mark.QUEUED, ttl=24 * 60 * 60):
    logging.debug("marked notice:{0} user:{1} mark:{2}".format(notice_id, user_id, result.name))

    # добавляем к ttl 1мин чтобы гонок не было и если есть сообщение - в редис точно была отметка
    set_mark(notice_id, user_id, result, ttl+60)


def is_processed(notice_id, user_id) -> bool:
    result = get_mark(notice_id, user_id)
    return result is not None


class Extractor:
    def __init__(self, rmq: RabbitMQ):
        self.channel = rmq.connection.channel()
        # self.channel.basic_qos(prefetch_size=1, prefetch_count=1)
        self.current_delivery_tag = None

    def get_data(self):
        method_frame, header_frame, body = self.channel.basic_get(QUEUE_NOTICE)
        if method_frame:
            nl = "\n"
            logging.debug(f"extract: {nl} method:{method_frame},{nl} header:{header_frame},{nl} body:{body}")
            self.current_delivery_tag = method_frame.delivery_tag
            notice_dict = orjson.loads(body)
            return Notice(**notice_dict)

    def mark_done(self):
        self.channel.basic_ack(self.current_delivery_tag)


class Transformer:
    @staticmethod
    def get_msg_meta(data: Notice, user_info: UserInfo) -> dict | None:
        transport = data.transport
        match transport:
            case Transport.EMAIL:
                if user_info.email:
                    # TODO надо бы придумать где тему письма получать
                    return {'email': user_info.email, 'subject': 'Movies Notice'}

            case Transport.SMS:
                if user_info.phone:
                    return {'phone': user_info.phone}

            case Transport.WEBSOCKET:
                # без понятия что нужно для сокетов. наверное только user_id, но он есть в сообщении
                return {}

        # если ничего не выдали до этого, значит вернем None и сообщение не отправится
        return None

    def transform(self, data: Notice):
        with tracer.start_as_current_span('etl_transform') as span:
            span.set_attribute('http.request_id', data.x_request_id)
            span.set_attribute('transport', data.transport)

            template = get_template(data.template_id)
            notice_id = data.notice_id
            ttl = get_ttl_from_datetime(data.expire_at)
            # узнаю повторная ли это обработка
            is_repeat = is_processed(notice_id, 0)
            if not is_repeat:
                mark_processed(notice_id, 0, ttl=ttl)

            for user in data.users:
                # если это повтор - проверяем на обработку конкретного пользователя
                if is_repeat and is_processed(notice_id, user):
                    logging.debug('msg rejected: notice_id:{0} user_id:{1}'.format(notice_id, user))
                    continue

                user_info = get_user_info(user)
                # пропускаем, если пользователь отказался от некоторых рассылок
                if data.msg_type in user_info.reject_notice:
                    # помечаем сообщение как отвергнутое
                    mark_processed(data.notice_id, user, Mark.REJECTED_USER, ttl)
                    continue

                msg_body = template.render(user_info.dict() | data.extra)
                msg_meta = self.get_msg_meta(data, user_info)
                # для случаев, когда не можем отправить сообщение,
                # потому что не хватает данных для отправки, например телефона
                if not msg_meta:
                    mark_processed(data.notice_id, user, Mark.REJECTED_NODATA, ttl)
                    continue

                message = Message(
                    x_request_id=data.x_request_id,
                    notice_id=data.notice_id,
                    msg_id=uuid.uuid4(),
                    user_id=user,
                    user_tz=0,
                    msg_meta=msg_meta,
                    msg_body=msg_body,
                    expire_at=data.expire_at,
                )
                yield data.transport, message


class Loader:
    def __init__(self, rmq: RabbitMQ):
        self.channel = rmq.connection.channel()

    def send_message(self, queue: str, msg: Message, ttl:int):
        properties = pika.BasicProperties(expiration=str(ttl * 1000))
        self.channel.basic_publish(exchange="", routing_key=queue, properties=properties, body=msg.json())

    def load(self, data):
        for transport, msg in data:
            with tracer.start_as_current_span('etl_load') as span:
                # делаем трассировку
                span.set_attribute('http.request_id', msg.x_request_id)
                span.set_attribute('transport', transport)

                # ставим в очередь на отправку
                sender_queue = transport
                ttl = get_ttl_from_datetime(msg.expire_at)
                self.send_message(sender_queue, msg, ttl)

                # помечаем как обработанное
                mark_processed(msg.notice_id, msg.user_id, Mark.QUEUED, ttl)

                logging.debug("message loaded: {0}".format(msg.dict()))


class ETL:
    is_run = False

    def __init__(self, rmq: RabbitMQ):
        self.extractor = Extractor(rmq)
        self.transformer = Transformer()
        self.loader = Loader(rmq)

    def stop(self):
        self.is_run = False
        logging.info("stop etl")

    def run(self):
        self.is_run = True
        while self.is_run:
            data = self.extractor.get_data()
            if not data:
                time.sleep(0.1)
                continue

            transformed_data = self.transformer.transform(data)
            # если есть что отправить
            if transformed_data:
                self.loader.load(transformed_data)

            # если в процессе ничего не упало - считаем что задание выполнено
            self.extractor.mark_done()
