import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN_BOT = os.getenv('API_BOT_TOKEN', '123456:123456test')

WEBHOOK_PATH = f'/webhook/{os.getenv("WEBHOOK")}'
WEBHOOK_URL = f'{os.environ.get("HOST")}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 5000))

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/1')
