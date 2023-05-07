import random

from aiogram.dispatcher.filters.state import StatesGroup, State
import pandas as pd

from app import logger, db_conn
from s95.athlete_code import AthleteCode
from s95.helpers import time_conv
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
    user = await conn.fetchrow('SELECT * FROM users WHERE LOWER(email) = $1', email.lower())
    await conn.close()
    return user


async def user_results(telegram_id):
    conn = await db_conn()
    query = f"""SELECT results.position, results.total_time, activities.date, events.name FROM results
        INNER JOIN activities ON activities.id = results.activity_id
        INNER JOIN events ON events.id = activities.event_id
        INNER JOIN athletes ON athletes.id = results.athlete_id
        INNER JOIN users ON users.id = athletes.user_id
        WHERE users.telegram_id = $1
    """
    data = await conn.fetch(query, telegram_id)
    df = pd.DataFrame(data, columns=['Pos', 'Time', 'Run Date', 'Event'])
    df['m'] = df['Time'].apply(lambda t: time_conv(t))
    await conn.close()
    return df


def athlete_code(athlete):
    return athlete["parkrun_code"] or athlete["fiveverst_code"] or athlete["parkzhrun_code"] \
        or athlete["id"] + AthleteCode.SAT_5AM_9KM_BORDER


async def handle_throttled_query(*args, **kwargs):
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with {kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer(random.choice(content.throttled_messages))
