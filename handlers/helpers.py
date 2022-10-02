import random

from aiogram.dispatcher.filters.state import StatesGroup, State

from app import logger, db_conn
from utils import content


class UserStates(StatesGroup):
    SEARCH_PARKRUN_CODE = State()
    SAVE_WITH_PARKRUN_CODE = State()
    ATHLETE_LAST_NAME = State()
    ATHLETE_FIRST_NAME = State()
    GENDER = State()
    EMAIL = State()
    VALIDATE_EMAIL = State()
    PASSWORD = State()
    COMPARE_ID = State()


async def fetch_athlete(athlete_id):
    if not athlete_id or not athlete_id.isdigit():
        return None
    parkrun_id = int(athlete_id)
    conn = await db_conn()
    athlete = await conn.fetchrow('SELECT * FROM athletes WHERE parkrun_code = $1', parkrun_id)
    print(athlete)
    if athlete:
        return athlete


async def handle_throttled_query(*args, **kwargs):
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with {kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer(random.choice(content.throttled_messages))
