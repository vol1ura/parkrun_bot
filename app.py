import asyncpg
import logging
import rollbar

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

import config

bot = Bot(config.TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(levelname)s [ LINE:%(lineno)+3s ]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if config.PRODUCTION_ENV:
    rollbar.init(config.ROLLBAR_TOKEN, 'production')


async def db_conn():
    return await asyncpg.connect(config.DATABASE_URL)
