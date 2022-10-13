import random

from aiogram.dispatcher.filters.state import StatesGroup, State

from app import logger, db_conn
from utils import content


class UserStates(StatesGroup):
    SEARCH_ATHLETE_CODE = State()
    SAVE_WITH_PARKRUN_CODE = State()
    ATHLETE_LAST_NAME = State()
    ATHLETE_FIRST_NAME = State()
    GENDER = State()
    EMAIL = State()
    VALIDATE_EMAIL = State()
    PASSWORD = State()
    COMPARE_ID = State()  # TODO: remove me


async def find_athlete_by(field: str, value):
    conn = await db_conn()
    athlete = await conn.fetchrow(f'SELECT * FROM athletes WHERE {field} = $1', value)
    await conn.close()
    return athlete


async def find_user_by(field: str, value):
    conn = await db_conn()
    user = await conn.fetchrow(f'SELECT * FROM users WHERE {field} = $1', value)
    await conn.close()
    return user


async def find_user_by_email(email: str):
    conn = await db_conn()
    user = await conn.fetchrow('SELECT * FROM users WHERE email ILIKE $1', email)
    await conn.close()
    return user


async def handle_throttled_query(*args, **kwargs):
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with {kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer(random.choice(content.throttled_messages))
