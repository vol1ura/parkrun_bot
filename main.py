from aiogram import Dispatcher, types
from aiogram.utils import executor

import config
import handlers

from app import bot, dp, setup_container


async def setup_bot_commands(_: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command='/qrcode', description='Ваш QR-код в S95'),
        types.BotCommand(command='/register', description='Зарегистрироваться в S95'),
        types.BotCommand(command='/login', description='Войти на сайт S95'),
        types.BotCommand(command='/statistics', description='Персональная статистика'),
        types.BotCommand(command='/help', description='Краткая справка'),
        types.BotCommand(command='/phone', description='Привязать свой телефон к профилю'),
        types.BotCommand(command='/club', description='Установить клуб'),
        types.BotCommand(command='/home', description='Установить домашний забег'),
        types.BotCommand(command='/start', description='Перезапуск'),
        types.BotCommand(command='/reset', description='Отмена действия')
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    await setup_container()
    await bot.delete_webhook()
    if config.PRODUCTION_ENV:
        await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)
    await setup_bot_commands(dispatcher)


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    print('Shutting down..')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    print('Bot down')


if __name__ == '__main__':
    if False:  # config.PRODUCTION_ENV
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
        executor.start_polling(
            dp,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True  # drop pending updates to avoid InvalidQueryID for stale callbacks
        )
