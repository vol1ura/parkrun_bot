import random

from aiogram.dispatcher.filters.state import StatesGroup, State
from vedis import Vedis

from app import logger
from config import DB_FILE
from utils import parkrun


class UserStates(StatesGroup):
    ATHLETE_ID = State()
    COMPARE_ID = State()


class ParkrunSite:
    PARKRUN_HEADERS = [
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 YaBrowser/21.3.0.740 Yowser/2.5 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"}
    ]

    @classmethod
    def headers(cls):
        return random.choice(ParkrunSite.PARKRUN_HEADERS)


def min_to_mmss(m) -> str:
    mins = int(m)
    return f'{mins}:{int((m - mins) * 60)}'


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
