import logging
from abc import abstractmethod
from email.message import EmailMessage
from http import HTTPStatus

import sendgrid
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import From, HtmlContent, Mail, Subject, To

from config import settings
from models import EmailNotification

logger = logging.getLogger(__name__)


class BaseSender:
    @abstractmethod
    def send(self, notice: EmailNotification):
        ...

    def handle_unsent(self, notice: EmailNotification):
        # TODO реализовать повторную отправку
        pass


class SendgridSender(BaseSender):
    def __init__(self):
        self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    def send(self, notice: EmailNotification):
        message = Mail(
            from_email=From(settings.SEND_FROM_EMAIL),
            to_emails=To(notice.msg_meta.email),
            subject=Subject(notice.msg_meta.subject),
            html_content=HtmlContent(notice.msg_body),
        )
        try:
            response = self.sendgrid_client.send(message=message)
        except HTTPError:
            logger.exception("Error on sending email notification %s", notice.json())
            self.handle_unsent(notice)
            return

        if response.status_code != HTTPStatus.ACCEPTED:
            logger.exception("Error on sending email notification %s", notice.json())
            self.handle_unsent(notice)
            return

        logger.info("Send notification %s", notice.json())


class DebugSender(BaseSender):
    def send(self, notice: EmailNotification):
        message = EmailMessage()
        message["From"] = settings.SEND_FROM_EMAIL
        message["To"] = notice.msg_meta.email
        message["Subject"] = notice.msg_meta.subject
        message.set_content(notice.msg_body)
        print(f"#---MESSAGE START---#\n{message}\n#---MESSAGE END---#")