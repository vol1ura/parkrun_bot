import typing
import asyncpg
import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

import config

bot = Bot(config.TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(levelname)s [ %(filename)s:%(lineno)s ]: %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

# Глобальная переменная пула
db_pool: typing.Optional[asyncpg.Pool] = None

async def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(dsn=config.DATABASE_URL)

def get_pool() -> asyncpg.Pool:
    if db_pool is None:
        raise RuntimeError("Database pool is not initialized")
    return db_pool

def language_code(message: typing.Union[types.Message, types.CallbackQuery]) -> str:
    return message.from_user.language_code or 'ru'
