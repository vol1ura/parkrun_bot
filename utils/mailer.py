import os
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


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
    def __init__(self, pin_code):
        self.__pin_code = pin_code
        self.__subject = 'Подтверждение регистрации'
        super().__init__()

    def send(self, receiver_email, receiver_name):
        super().send(receiver_email, receiver_name, self.__subject, self.__body)

    @property
    def __body(self):
        return f"""Приветствуем!

        Секретный код: {self.__pin_code}
        Отправьте его боту. Код действителен 30 минут с момента запроса.

        Вы получили данное сообщение, так как ваш e-mail был указан в процессе регистрации на сайте https://{config.HOST}/
        Если это были не вы, просто проигнорируйте данное сообщение.

        --
        С уважением,
        команда {config.EMAIL_SENDER}
        """


if __name__ == '__main__':
    from dotenv import load_dotenv

    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    EmailConfirmation(1111).send('test@gmail.com', 'Ura')