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


async def db_conn():
    return await asyncpg.connect(config.DATABASE_URL)

def language_code(message: types.Message) -> str:
    return message.from_user.language_code or 'ru'
