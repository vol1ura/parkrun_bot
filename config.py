import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

PRODUCTION_ENV = os.getenv('PRODUCTION', '').lower() in ('true', '1', 'yes')

VERSION = '1.9.9'

TOKEN_BOT = os.getenv('API_BOT_TOKEN', '123456:123456test')

HOST = os.getenv('HOST')

WEBHOOK_PATH = f'/bot/{os.getenv("WEBHOOK", "webhook")}'
WEBHOOK_URL = f'{HOST}{WEBHOOK_PATH}' if HOST else ''

WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = int(os.getenv('PORT', 5000))

DATABASE_URL = os.getenv('DATABASE_URL')


INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')
INTERNAL_API_URL = os.getenv('INTERNAL_API_URL')

ROLLBAR_TOKEN = os.getenv('ROLLBAR_TOKEN')
