import typing
import logging
import aioredis
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup

import config
from utils.cache import Cache
from utils.database import Database
from utils.rate_limiter import RateLimiter
from utils.infernasel_anticrash import InfernaselAnticrash
from utils.infernasel_antiflood import InfernaselAntiflood, AntifloodMiddleware
from utils.infernasel_fastsec import InfernaselFastsec, SecurityMiddleware

# Настройка логирования
logging.basicConfig(
    format=u'%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация Redis
redis = aioredis.from_url(
    config.REDIS_URL,
    encoding=config.REDIS_ENCODING,
    decode_responses=config.REDIS_DECODE_RESPONSES
)

# Инициализация кэша
cache = Cache(redis, prefix=config.CACHE_PREFIX)

# Инициализация rate limiter
rate_limiter = RateLimiter(redis, limit=config.RATE_LIMIT, window=config.RATE_WINDOW)

# Инициализация систем безопасности
anticrash = InfernaselAnticrash(
    max_memory_percent=80,
    max_cpu_percent=90
)

antiflood = InfernaselAntiflood(
    message_limit=5,
    time_window=60,
    max_file_size=20 * 1024 * 1024
)

fastsec = InfernaselFastsec()

# Инициализация хранилища состояний
storage = RedisStorage2(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    password=config.REDIS_PASSWORD
)

# Инициализация бота и диспетчера
bot = Bot(config.TOKEN_BOT)
dp = Dispatcher(bot, storage=storage)

# Добавление middleware
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(AntifloodMiddleware(antiflood))
dp.middleware.setup(SecurityMiddleware(fastsec))

# Инициализация базы данных
db = Database(
    config.DATABASE_URL,
    min_size=config.DB_MIN_SIZE,
    max_size=config.DB_MAX_SIZE,
    cache=cache
)

async def init_db():
    """Инициализация базы данных и создание необходимых таблиц"""
    await db.connect()
    await db.create_tables()
    return db

# Настройка антикрэш системы
anticrash.setup()

# Регистрация задач очистки
async def cleanup_tasks():
    await db.close()
    await redis.close()
    await bot.close()

anticrash.register_cleanup_task(cleanup_tasks)

def language_code(message: typing.Union[types.Message, types.CallbackQuery]) -> str:
    return message.from_user.language_code or 'ru'
