from os import environ

from aiogram import Dispatcher, types
from aiogram.utils import executor

from config import *
from app import bot, dp
import handlers  # important import!!!


async def setup_bot_commands(dispatcher: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command="/help", description="Справочное сообщение"),
        types.BotCommand(command="/register", description="Зарегистрироваться"),
        types.BotCommand(command="/settings", description="Сделать настройки"),
        types.BotCommand(command="/setclub", description="Установить клуб"),
        types.BotCommand(command='/start', description='Показать клавиатуру | Перезапуск')
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await setup_bot_commands(dispatcher)


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    print("Shutting down..")
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    print("Bot down")


if __name__ == "__main__":
    if "production" in list(environ.keys()):
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    else:
        executor.start_polling(dp)
