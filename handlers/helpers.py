import aiohttp
import pandas as pd
import random
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound, TelegramAPIError
from typing import Optional

from app import logger, db
from config import INTERNAL_API_URL
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


async def delete_message(message: types.Message) -> None:
    try:
        await message.delete()
    except MessageToDeleteNotFound:
        pass


async def find_athlete_by(field: str, value):
    try:
        athlete = await db.execute(f'SELECT * FROM athletes WHERE {field} = $1', value)
        return athlete
    except Exception as e:
        logger.error(f'Error finding athlete by {field}={value}: {e}')
        return None


async def find_user_by(field: str, value):
    try:
        user = await db.execute(f'SELECT * FROM users WHERE {field} = $1', value)
        return user
    except Exception as e:
        logger.error(f'Error finding user by {field}={value}: {e}')
        return None


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


async def find_home_event(telegram_id: int):
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


async def update_home_event(telegram_id: int, event_id: Optional[int] = None) -> bool:
    try:
        async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
            payload = {'telegram_id': telegram_id, 'athlete': {'event_id': event_id}}
            async with session.put(f'{INTERNAL_API_URL}/athlete', json=payload) as response:
                if not response.ok:
                    logger.error(f'Failed to update home event_id={event_id} for user with telegram_id={telegram_id}')
                    return False
    except Exception:
        logger.error(f'Error while update event_id={event_id} for user with telegram_id={telegram_id}')
        return False
    else:
        return True


async def update_club(telegram_id: int, club_id: Optional[int] = None) -> bool:
    try:
        async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
            payload = {'telegram_id': telegram_id, 'athlete': {'club_id': club_id}}
            async with session.put(f'{INTERNAL_API_URL}/athlete', json=payload) as response:
                if not response.ok:
                    logger.error(f'Failed to set club_id={club_id} for user with telegram_id={telegram_id}')
                    return False
    except Exception:
        logger.error(f'Error while update club_id={club_id} for user with telegram_id={telegram_id}')
        return False
    else:
        return True


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
    link = await conn.fetchrow('SELECT link FROM contacts WHERE event_id = $1 AND contact_type = 3', event_id)
    await conn.close()
    return link and link['link']


async def user_results(telegram_id: int) -> pd.DataFrame:
    conn = await db_conn()
    query = """SELECT results.position, results.total_time, activities.date, events.name FROM results
        INNER JOIN activities ON activities.id = results.activity_id
        INNER JOIN events ON events.id = activities.event_id
        INNER JOIN athletes ON athletes.id = results.athlete_id
        INNER JOIN users ON users.id = athletes.user_id
        WHERE users.telegram_id = $1 AND activities.published = TRUE
        ORDER BY activities.date DESC
    """
    data = await conn.fetch(query, telegram_id)
    df = pd.DataFrame(data, columns=['Pos', 'Time', 'Run Date', 'Event'])
    df['m'] = df['Time'].apply(lambda t: time_conv(t))
    await conn.close()
    return df


def athlete_code(athlete):
    return athlete["parkrun_code"] or athlete["fiveverst_code"] or athlete["runpark_code"] \
        or athlete["parkzhrun_code"] or athlete["id"] + AthleteCode.SAT_5AM_9KM_BORDER


async def handle_throttled_query(*args, **kwargs):
    message = args[0]  # as message was the first argument in the original handler
    try:
        telegram_id = message.from_user.id
        action = message.data
    except Exception:
        telegram_id = 'Unknown'
        action = 'unknown'
    logger.warning(f'Message was throttled on {action} action with rate={kwargs["rate"]} and id={telegram_id}')
    await message.answer(random.choice(content.throttled_messages))


async def update_user_phone(telegram_id: int, phone: str) -> bool:
    try:
        conn = await db_conn()
        await conn.execute('UPDATE users SET phone = $1 WHERE telegram_id = $2', phone, telegram_id)
        await conn.close()
        return True
    except Exception:
        logger.error(f'Error while updating phone for user with telegram_id={telegram_id}')
        return False


async def get_auth_link(user_id: int) -> Optional[str]:
    try:
        async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
            async with session.post(f'{INTERNAL_API_URL}/user/auth_link', json={'user_id': user_id}) as response:
                if not response.ok:
                    logger.error(f'Failed to get auth link for user with id={user_id}')
                    return None
                data = await response.json()
                return data['link']
    except Exception as e:
        logger.error(f'Error while getting auth link for user with id={user_id}: {e}')
        return None


async def find_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    try:
        user = await db.execute('SELECT * FROM users WHERE telegram_id = $1', telegram_id)
        return user
    except Exception as e:
        logger.error(f'Error finding user by telegram_id {telegram_id}: {e}')
        return None
