import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

PRODUCTION_ENV = os.getenv('PRODUCTION')

VERSION = '1.5.4'

TOKEN_BOT = os.getenv('API_BOT_TOKEN', '123456:123456test')

WEBHOOK_PATH = f'/webhook/{os.getenv("WEBHOOK")}'
WEBHOOK_URL = f'{os.getenv("HOST")}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 5000))

DATABASE_URL = os.getenv('DATABASE_URL')

HOST = os.getenv('HOST')

INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')
INTERNAL_API_URL = os.getenv('INTERNAL_API_URL')

ROLLBAR_TOKEN = os.getenv('ROLLBAR_TOKEN')

# Mailer
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
