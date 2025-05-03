import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.content import t

import config

logger = logging.getLogger(__name__)

async def send_email(receiver_email: str, receiver_name: str, subject: str, body: str) -> bool:
    """
    Send email using SMTP server
    """
    try:
        context = ssl.create_default_context()
        message = MIMEMultipart()
        message['From'] = f'{config.EMAIL_SENDER} <{config.EMAIL_ADDRESS}>'
        message['To'] = f'{receiver_name} <{receiver_email}>'
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_ADDRESS, receiver_email, message.as_string())
        return True
    except Exception as e:
        logger.error(f'Error sending email to {receiver_email}: {e}')
        return False


class Mailer:
    def send(self, receiver_email, receiver_name, subject, body):
        """
        Log in to server using secure context and send email
        """
        context = ssl.create_default_context()
        message = self.__message(receiver_email, receiver_name, subject, body)
        with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_ADDRESS, receiver_email, message.as_string())

    def __message(self, receiver_email, receiver_name, subject, body):
        """
        Create a multipart message and set headers
        """
        message = MIMEMultipart()
        message['From'] = f'{config.EMAIL_SENDER} <{config.EMAIL_ADDRESS}>'
        message['To'] = f'{receiver_name} <{receiver_email}>'
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        return message


class EmailConfirmation(Mailer):
    def __init__(self, pin_code: int, lang: str):
        self.__pin_code = pin_code
        self.__lang = lang
        super().__init__()

    def send(self, receiver_email: str, receiver_name: str):
        subject = t(self.__lang, 'email_subject')
        body = t(self.__lang, 'email_body') \
            .format(pin_code=self.__pin_code, webhost=config.HOST, email_sender=config.EMAIL_SENDER)
        super().send(receiver_email, receiver_name, subject, body)
