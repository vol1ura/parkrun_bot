import random

from aiogram.dispatcher.filters.state import StatesGroup, State
from vedis import Vedis

from app import logger
from config import DB_FILE
from parkrun import parkrun
from utils import content


class UserStates(StatesGroup):
    ATHLETE_ID = State()
    COMPARE_ID = State()


async def add_db_athlete(athlete_id):
    if not athlete_id or not athlete_id.isdigit():
        return None
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(f'A{athlete_id}')
            athlete_name = h['athlete'].decode() if h['athlete'] else None
        except Exception as e:
            athlete_name = None
            logger.error(f'Access to DB failed. Athlete ID={athlete_id}. Error: {e}')
    if not athlete_name:
        athlete_name, athlete_page = await parkrun.get_athlete_data(athlete_id)
        if not athlete_name:
            return None
        with Vedis(DB_FILE) as db:
            try:
                h = db.Hash(f'A{athlete_id}')
                h['athlete'] = athlete_name
                h['athlete_page'] = athlete_page
            except Exception as e:
                logger.error('Writing athlete to DB failed. '
                             f'Athlete ID={athlete_id}, {athlete_name}. Error: {e}')
    return athlete_name


async def handle_throttled_query(*args, **kwargs):
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with {kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer(random.choice(content.throttled_messages))
