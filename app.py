import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import asyncpg
import redis.asyncio as redis

from config import TOKEN_BOT, REDIS_HOST, REDIS_PORT

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(levelname)s [ LINE:%(lineno)+3s ]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

async def db_conn():
    return await asyncpg.connect(user='postgres', password='123456', database='s95_dev', host='127.0.0.1')
