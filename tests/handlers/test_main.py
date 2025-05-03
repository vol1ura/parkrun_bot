import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

from . import MockTelegram, TOKEN


@pytest.fixture(name='fake_bot')
async def bot_fixture(monkeypatch):
    """ Bot fixture """
    monkeypatch.setenv('API_BOT_TOKEN', TOKEN)
    import app

    _bot = app.bot
    yield _bot


@pytest.fixture(autouse=True)
def event_loop():
    """Создаем новый event loop для каждого теста"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def test_setup_bot_commands(fake_bot, loop):
    """ setup_bot_commands method test """
    from app import dp
    from main import setup_bot_commands
    async with MockTelegram(message_data=True):
        await setup_bot_commands(dp)


@pytest.mark.asyncio
async def test_on_shutdown():
    """Тест метода on_shutdown"""
    # Создаем мок бота
    bot = Bot(token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')
    
    # Создаем мок для db_pool
    mock_pool = AsyncMock()
    mock_pool.close = AsyncMock()
    
    # Создаем мок для session
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    
    # Создаем storage
    storage = MemoryStorage()
    
    # Создаем диспетчер
    dp = Dispatcher(bot, storage=storage)
    
    # Создаем асинхронный мок для метода get
    async def mock_get(key):
        if key == 'db_pool':
            return mock_pool
        return None
    
    # Создаем асинхронный мок для метода get_session
    async def mock_get_session():
        return mock_session
    
    # Патчим методы бота
    with patch.object(bot, 'get', mock_get), \
         patch.object(bot, 'get_session', mock_get_session):
        
        # Импортируем и вызываем on_shutdown
        from main import on_shutdown
        await on_shutdown(dp)
        
        # Проверяем, что методы были вызваны
        mock_pool.close.assert_called_once()
        mock_session.close.assert_called_once()
