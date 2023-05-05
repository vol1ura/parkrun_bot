from os import environ

from aiogram import Dispatcher, types
from aiogram.utils import executor

import config
import handlers  # important import!!!

from app import bot, dp


async def setup_bot_commands(_: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command='/start', description='Показать клавиатуру | Перезапуск'),
        types.BotCommand(command='/barcode', description='Штрих-код'),
        types.BotCommand(command='/help', description='Справочное сообщение'),
        types.BotCommand(command='/register', description='Зарегистрироваться в S95')
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)
    await setup_bot_commands(dispatcher)


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    print('Shutting down..')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    print('Bot down')


if __name__ == '__main__':
    if 'production' in list(environ.keys()):
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=config.WEBAPP_HOST,
            port=config.WEBAPP_PORT
        )
    else:
        handlers.print_info()
        executor.start_polling(dp)
