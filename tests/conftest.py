import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

# Создаем тестовый бот с фиктивным токеном
test_bot = Bot(token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')
storage = MemoryStorage()
test_dp = Dispatcher(test_bot, storage=storage)

# Устанавливаем тестовые значения переменных окружения
os.environ['PRODUCTION'] = 'false'
os.environ['API_BOT_TOKEN'] = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
os.environ['WEBHOOK'] = 'test_webhook'
os.environ['HOST'] = 'http://localhost:5000'
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'

@pytest.fixture(scope='session', autouse=True)
def setup_dot_env() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)

@pytest.fixture
async def bot():
    return test_bot

@pytest.fixture
async def dp():
    return test_dp

@pytest.fixture
async def redis():
    redis_mock = AsyncMock()
    redis_mock.from_url = AsyncMock()
    redis_mock.close = AsyncMock()
    return redis_mock

@pytest.fixture
async def cache(redis):
    cache_mock = AsyncMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    cache_mock.delete = AsyncMock()
    return cache_mock

@pytest.fixture
async def db():
    db_mock = AsyncMock()
    db_mock.connect = AsyncMock()
    db_mock.close = AsyncMock()
    db_mock.create_tables = AsyncMock()
    db_mock.execute = AsyncMock()
    db_mock.fetchone = AsyncMock()
    db_mock.fetchall = AsyncMock()
    return db_mock

@pytest.fixture
async def vk_api():
    vk_mock = AsyncMock()
    vk_mock.wall.post = AsyncMock(return_value={'post_id': 1})
    return vk_mock

@pytest.fixture
async def app(bot, dp, db, redis, cache, vk_api):
    """Фикстура для основного приложения"""
    with patch('app.Bot', return_value=bot), \
         patch('app.Dispatcher', return_value=dp), \
         patch('app.Database', return_value=db), \
         patch('aioredis.from_url', return_value=redis), \
         patch('app.Cache', return_value=cache), \
         patch('app.VkApi', return_value=vk_api):
        
        from app import init_db
        await init_db()
        
        yield {
            'bot': bot,
            'dp': dp,
            'db': db,
            'redis': redis,
            'cache': cache,
            'vk_api': vk_api
        }

pytest_plugins = ['aiohttp.pytest_plugin']
