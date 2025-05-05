import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Основные настройки
PRODUCTION_ENV = os.getenv('PRODUCTION', 'false').lower() == 'true'
VERSION = '1.8.0'

# Настройки бота
TOKEN_BOT = os.getenv('API_BOT_TOKEN', '--SENSITIVE--')
WEBHOOK_PATH = f'/webhook/{os.getenv("WEBHOOK", "--SENSITIVE--")}'
WEBHOOK_URL = f'{os.getenv("HOST", "--SENSITIVE--")}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 5000))

# Настройки базы данных
DATABASE_URL = os.getenv('DATABASE_URL', '--SENSITIVE--')
DB_MIN_SIZE = int(os.getenv('DB_MIN_SIZE', 5))
DB_MAX_SIZE = int(os.getenv('DB_MAX_SIZE', 20))
DB_COMMAND_TIMEOUT = int(os.getenv('DB_COMMAND_TIMEOUT', 60))
DB_MAX_QUERIES = int(os.getenv('DB_MAX_QUERIES', 50000))
DB_MAX_INACTIVE_TIME = int(os.getenv('DB_MAX_INACTIVE_TIME', 300))

# Настройки Redis
REDIS_URL = os.getenv('REDIS_URL', '--SENSITIVE--')
REDIS_ENCODING = 'utf-8'
REDIS_DECODE_RESPONSES = True
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Настройки rate limiting
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))
RATE_WINDOW = int(os.getenv('RATE_WINDOW', 60))

# Настройки кэширования
CACHE_TTL = int(os.getenv('CACHE_TTL', 300))
CACHE_PREFIX = os.getenv('CACHE_PREFIX', 'cache:')

# Настройки API
INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY', '--SENSITIVE--')
INTERNAL_API_URL = os.getenv('INTERNAL_API_URL', '--SENSITIVE--')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))

# Настройки мониторинга
ROLLBAR_TOKEN = os.getenv('ROLLBAR_TOKEN', '--SENSITIVE--')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Настройки email
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '--SENSITIVE--')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '--SENSITIVE--')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '--SENSITIVE--')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_SERVER = os.getenv('SMTP_SERVER', '--SENSITIVE--')

HOST = os.getenv('HOST')
