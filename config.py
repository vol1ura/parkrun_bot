import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

PROJECT_NAME = os.getenv('PROJECT', 'test')
TOKEN_BOT = os.getenv('API_BOT_TOKEN', '123456:123456test')

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{os.getenv("WEBHOOK")}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 5000))

DB_FILE = os.path.join(os.path.dirname(__file__), 'database.vdb')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
