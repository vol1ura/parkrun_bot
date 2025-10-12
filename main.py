import asyncio
from aiogram import types
from aiohttp import web

import config
import handlers

from app import bot, dp, setup_container, storage


async def setup_bot_commands():
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command='qrcode', description='Ваш QR-код в S95'),
        types.BotCommand(command='register', description='Зарегистрироваться в S95'),
        types.BotCommand(command='login', description='Войти на сайт S95'),
        types.BotCommand(command='statistics', description='Персональная статистика'),
        types.BotCommand(command='help', description='Краткая справка'),
        types.BotCommand(command='phone', description='Привязать свой телефон к профилю'),
        types.BotCommand(command='home', description='Установить домашний забег'),
        types.BotCommand(command='club', description='Установить клуб'),
        types.BotCommand(command='start', description='Перезапуск'),
        types.BotCommand(command='reset', description='Отмена действия')
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup():
    await setup_container()
    await bot.delete_webhook(drop_pending_updates=True)
    # if config.PRODUCTION_ENV:
    #     await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)
    await setup_bot_commands()


# Run before shutdown
async def on_shutdown():
    print('Shutting down..')
    await storage.close()
    print('Bot down')


async def main():
    """Main function to run the bot"""
    handlers.print_info()

    # Register startup hook
    dp.startup.register(on_startup)
    # Register shutdown hook
    dp.shutdown.register(on_shutdown)

    if False:  # config.PRODUCTION_ENV
        # Webhook mode (not fully implemented here, needs aiohttp app setup)
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        web.run_app(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)
    else:
        # Polling mode
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
