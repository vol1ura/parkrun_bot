import aiohttp
import pandas as pd
import random

from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from typing import Optional

from app import logger, container
from config import INTERNAL_API_URL
from services.user_service import UserService
from services.athlete_service import AthleteService
from services.club_service import ClubService
from services.event_service import EventService
from services.result_service import ResultService
from utils import content


class UserStates(StatesGroup):
    SEARCH_ATHLETE_CODE = State()
    SAVE_WITH_PARKRUN_CODE = State()
    ATHLETE_LAST_NAME = State()
    ATHLETE_FIRST_NAME = State()
    GENDER = State()
    CONFIRM = State()


class ClubStates(StatesGroup):
    INPUT_NAME = State()
    CONFIRM_NAME = State()


class HomeEventStates(StatesGroup):
    SELECT_COUNTRY = State()
    INPUT_EVENT_ID = State()


class LoginStates(StatesGroup):
    SELECT_DOMAIN = State()


async def delete_message(message: types.Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def find_athlete_by(field: str, value):
    """Find an athlete by a specific field (legacy function)"""
    athlete_service = container.resolve(AthleteService)

    if field == 'user_id':
        return await athlete_service.find_athlete_by_user_id(value)
    elif field == 'id':
        return await athlete_service.find_athlete_by_id(value)
    elif field in ['parkrun_code', 'fiveverst_code', 'runpark_code', 'parkzhrun_code']:
        return await athlete_service.find_athlete_by_code(field, value)
    else:
        # Generic fallback using repository's find_by method
        return await athlete_service.athlete_repository.find_by(field, value)


async def find_user_by(field: str, value):
    """Find a user by a specific field (legacy function)"""
    user_service = container.resolve(UserService)

    if field == 'telegram_id':
        return await user_service.find_user_by_telegram_id(value)
    elif field == 'id':
        return await user_service.find_user_by_id(value)
    elif field == 'email':
        return await user_service.find_user_by_email(value)
    else:
        # Generic fallback using repository's find_by method
        return await user_service.user_repository.find_by(field, value)


async def find_club(telegram_id: int):
    """Find an athlete with club information by Telegram ID (legacy function)"""
    athlete_service = container.resolve(AthleteService)
    return await athlete_service.find_athlete_with_club(telegram_id)


async def find_club_by_name(name: str):
    """Find a club by name (legacy function)"""
    club_service = container.resolve(ClubService)
    return await club_service.find_club_by_name(name)


async def find_home_event(telegram_id: int):
    """Find an athlete with home event information by Telegram ID (legacy function)"""
    athlete_service = container.resolve(AthleteService)
    return await athlete_service.find_athlete_with_home_event(telegram_id)


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
    """Find a user by email (legacy function)"""
    user_service = container.resolve(UserService)
    return await user_service.find_user_by_email(email)


async def events():
    """Get all events except the 'friends' event (legacy function)"""
    event_service = container.resolve(EventService)
    return await event_service.find_all_events()


async def find_event_by_id(event_id: int):
    """Find an event by ID, excluding the 'friends' event (legacy function)"""
    event_service = container.resolve(EventService)
    return await event_service.find_event_by_id(event_id)


async def tg_channel_of_event(event_id: int):
    """Find the Telegram channel link for an event (legacy function)"""
    event_service = container.resolve(EventService)
    return await event_service.find_telegram_channel(event_id)


async def user_results(telegram_id: int) -> pd.DataFrame:
    """Get all results for a user by Telegram ID (legacy function)"""
    result_service = container.resolve(ResultService)
    return await result_service.get_user_results(telegram_id)


def athlete_code(athlete):
    """Get the athlete code based on available codes (legacy function)"""
    athlete_service = container.resolve(AthleteService)
    return athlete_service.get_athlete_code(athlete)


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
    """Update a user's phone number (legacy function)"""
    try:
        user_service = container.resolve(UserService)
        user = await user_service.find_user_by_telegram_id(telegram_id)
        if not user:
            logger.error(f'User with telegram_id={telegram_id} not found')
            return False

        await user_service.update_user(user['id'], {'phone': phone})
        return True
    except Exception as e:
        logger.error(f'Error while updating phone for user with telegram_id={telegram_id}: {e}')
        return False


async def get_auth_link(user_id: int, domain: str) -> Optional[str]:
    payload = {'user_id': user_id, 'domain': domain}
    try:
        async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
            async with session.post(f'{INTERNAL_API_URL}/user/auth_link', json=payload) as response:
                if not response.ok:
                    logger.error(f'Failed to get auth link for user with id={user_id}')
                    return None
                data = await response.json()
                return data['link']
    except Exception as e:
        logger.error(f'Error while getting auth link for user with id={user_id}: {e}')
        return None
