import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Создаем тестовый бот с фиктивным токеном
test_bot = Bot(token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')
storage = MemoryStorage()
test_dp = Dispatcher(test_bot, storage=storage)

# Мокаем все необходимые модули перед импортом app
with patch('aiogram.Bot', return_value=test_bot) as bot_mock, \
     patch('aioredis.from_url') as redis_mock, \
     patch('asyncpg.create_pool') as db_mock, \
     patch('utils.infernasel_anticrash.InfernaselAnticrash.setup') as anticrash_mock:
    
    # Настраиваем моки
    bot_mock.return_value.send_message = AsyncMock()
    bot_mock.return_value.answer_callback_query = AsyncMock()
    
    redis_mock.return_value = AsyncMock()
    
    db_pool = AsyncMock()
    db_pool.acquire = AsyncMock()
    db_pool.release = AsyncMock()
    db_pool.execute = AsyncMock()
    db_mock.return_value = db_pool
    
    anticrash_mock.return_value = None
    
    # Импортируем app только после настройки моков
    from app import bot, dp, db

@pytest.mark.asyncio
async def test_bot_initialization():
    assert bot is not None
    assert dp is not None

@pytest.mark.asyncio
async def test_db_initialization():
    assert db is not None 