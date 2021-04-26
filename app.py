import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from config import TOKEN_BOT

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(levelname)s [ LINE:%(lineno)+3s ]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_throttled_query(*args, **kwargs):
    # args will be the same as in the original handler
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with args={args} and kwargs={kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer("Подождите, я не успеваю 🤖\n"
                         "Данный запрос нельзя выполнять слишком часто.")


async def setup_bot_commands(dispatcher: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command="/help", description="Справочное сообщение"),
        types.BotCommand(command="/settings", description="Сделать настройки"),
    ]
    await bot.set_my_commands(bot_commands)
