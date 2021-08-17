import pytest

from . import MockTelegram, TOKEN


@pytest.fixture(name='bot')
async def bot_fixture(monkeypatch):
    """ Bot fixture """
    monkeypatch.setenv('API_BOT_TOKEN', TOKEN)
    import app

    _bot = app.bot
    yield _bot
    await _bot.close()


async def test_setup_bot_commands(bot):
    """ setup_bot_commands method test """
    from app import dp
    from main import setup_bot_commands
    async with MockTelegram(message_data=True):
        await setup_bot_commands(dp)


async def test_on_shutdown(bot):
    """ on_shutdown method test """
    from app import dp
    from main import on_shutdown
    async with MockTelegram(message_data=True):
        await on_shutdown(dp)
