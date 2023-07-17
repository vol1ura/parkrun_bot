import random

from aiogram.dispatcher.filters.state import StatesGroup, State
import pandas as pd

from app import logger, db_conn
from s95.athlete_code import AthleteCode
from s95.helpers import time_conv
from utils import content

FRIENDS_EVENT_ID = 4


class UserStates(StatesGroup):
    SEARCH_ATHLETE_CODE = State()
    SAVE_WITH_PARKRUN_CODE = State()
    ATHLETE_LAST_NAME = State()
    ATHLETE_FIRST_NAME = State()
    GENDER = State()
    EMAIL = State()
    VALIDATE_EMAIL = State()
    PASSWORD = State()


class ClubStates(StatesGroup):
    INPUT_NAME = State()
    CONFIRM_NAME = State()


class HomeEventStates(StatesGroup):
    INPUT_EVENT_ID = State()


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


async def find_club(telegram_id: int):
    conn = await db_conn()
    club = await conn.fetchrow(
        """SELECT athletes.*, clubs.name as club_name
        FROM athletes
        LEFT JOIN clubs ON athletes.club_id = clubs.id
        INNER JOIN users ON users.id = athletes.user_id
        WHERE users.telegram_id = $1""",
        telegram_id
    )
    await conn.close()
    return club


async def find_club_by_name(name: str):
    conn = await db_conn()
    club = await conn.fetchrow('SELECT * FROM clubs WHERE name ILIKE $1', f'{name}%')
    return club


async def find_home_event(telegram_id):
    conn = await db_conn()
    event = await conn.fetchrow(
        """SELECT athletes.*, events.name as event_name
        FROM athletes
        INNER JOIN users ON users.id = athletes.user_id
        LEFT JOIN events ON athletes.event_id = events.id
        WHERE users.telegram_id = $1""",
        telegram_id
    )
    await conn.close()
    return event


async def update_home_event(telegram_id: int, event_id: int) -> bool:
    conn = await db_conn()
    event = await find_event_by_id(event_id)
    if not event:
        return False
    athlete = await find_home_event(telegram_id)
    result = await conn.execute('UPDATE athletes SET event_id = $2 WHERE id = $1', athlete['id'], event_id)
    return True if result.endswith('1') else False


async def update_club(telegram_id: int, club_id: int) -> bool:
    conn = await db_conn()
    athlete = await find_club(telegram_id)
    result = await conn.execute('UPDATE athletes SET club_id = $2 WHERE id = $1', athlete['id'], club_id)
    return True if result.endswith('1') else False


async def find_user_by_email(email: str):
    conn = await db_conn()
    user = await conn.fetchrow('SELECT * FROM users WHERE LOWER(email) = $1', email.lower())
    await conn.close()
    return user


async def events():
    conn = await db_conn()
    events_list = await conn.fetch('SELECT * FROM events WHERE id != $1 ORDER BY id', FRIENDS_EVENT_ID)
    await conn.close()
    return events_list


async def find_event_by_id(event_id: int):
    if event_id == FRIENDS_EVENT_ID:
        return
    conn = await db_conn()
    event = await conn.fetchrow('SELECT * FROM events WHERE id = $1', event_id)
    await conn.close()
    return event


async def tg_channel_of_event(event_id: int):
    conn = await db_conn()
    link = await conn.fetchrow('SELECT link FROM contacts WHERE event_id = $1 AND contact_type = 2', event_id)
    await conn.close()
    return link['link']


async def user_results(telegram_id):
    conn = await db_conn()
    query = """SELECT results.position, results.total_time, activities.date, events.name FROM results
        INNER JOIN activities ON activities.id = results.activity_id
        INNER JOIN events ON events.id = activities.event_id
        INNER JOIN athletes ON athletes.id = results.athlete_id
        INNER JOIN users ON users.id = athletes.user_id
        WHERE users.telegram_id = $1
        ORDER BY activities.date DESC
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
