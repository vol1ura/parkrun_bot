import typing
import asyncpg
import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

import config
from di.container import Container

container = Container()

bot = Bot(config.TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(levelname)s [ %(filename)s:%(lineno)s ]: %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)


async def setup_container():
    """Set up dependency injection container with all services and repositories"""
    try:
        pool = await asyncpg.create_pool(config.DATABASE_URL, max_size=25)
        if pool is None:
            raise Exception('Database connection pool is not created')
    except asyncio.TimeoutError:
        logger.error('Database connection timeout during startup')
        raise
    except Exception as e:
        logger.error(f"Failed to setup container: {e}")
        raise

    # Import repositories
    from repositories.user_repository import UserRepository
    from repositories.athlete_repository import AthleteRepository
    from repositories.club_repository import ClubRepository
    from repositories.event_repository import EventRepository
    from repositories.activity_repository import ActivityRepository
    from repositories.result_repository import ResultRepository

    # Import services
    from services.user_service import UserService
    from services.activity_service import ActivityService
    from services.athlete_service import AthleteService
    from services.club_service import ClubService
    from services.event_service import EventService
    from services.result_service import ResultService
    from services.statistics_service import StatisticsService

    # Register repositories
    user_repo = UserRepository(pool)
    athlete_repo = AthleteRepository(pool)
    club_repo = ClubRepository(pool)
    event_repo = EventRepository(pool)
    activity_repo = ActivityRepository(pool)
    result_repo = ResultRepository(pool)

    container.register(UserRepository, user_repo)
    container.register(AthleteRepository, athlete_repo)
    container.register(ClubRepository, club_repo)
    container.register(EventRepository, event_repo)
    container.register(ActivityRepository, activity_repo)
    container.register(ResultRepository, result_repo)

    # Register services
    user_service = UserService(user_repo)
    activity_service = ActivityService(activity_repo, result_repo)
    athlete_service = AthleteService(athlete_repo)
    club_service = ClubService(club_repo)
    event_service = EventService(event_repo)
    result_service = ResultService(result_repo)
    statistics_service = StatisticsService(user_repo, result_repo)

    container.register(UserService, user_service)
    container.register(ActivityService, activity_service)
    container.register(AthleteService, athlete_service)
    container.register(ClubService, club_service)
    container.register(EventService, event_service)
    container.register(ResultService, result_service)
    container.register(StatisticsService, statistics_service)


def language_code(message: typing.Union[types.Message, types.CallbackQuery]) -> str:
    return message.from_user.language_code or 'ru'
