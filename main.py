from aiogram import Dispatcher, types
from aiogram.utils import executor
import logging
import config
import handlers
from app import bot, dp, init_db

logger = logging.getLogger(__name__)


async def setup_bot_commands(_: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command='/qrcode', description='Ваш QR-код в S95'),
        types.BotCommand(command='/register', description='Зарегистрироваться в S95'),
        types.BotCommand(command='/statistics', description='Персональная статистика'),
        types.BotCommand(command='/help', description='Краткая справка'),
        types.BotCommand(command='/phone', description='Поделиться номером'),
        types.BotCommand(command='/club', description='Установить клуб'),
        types.BotCommand(command='/home', description='Установить домашний забег'),
        types.BotCommand(command='/start', description='Перезапуск'),
        types.BotCommand(command='/reset', description='Отмена действия')
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    logger.info("Starting up...")
    
    # Initialize database connection pool
    await init_db()
    
    if config.PRODUCTION_ENV:
        await bot.delete_webhook()
        await bot.set_webhook(config.WEBHOOK_URL)
    
    await setup_bot_commands(dispatcher)
    logger.info("Bot started successfully")


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    logger.info("Shutting down...")
    
    # Close database connections
    pool = await dispatcher.bot.get('db_pool')
    if pool:
        await pool.close()
    
    # Close storage
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    
    # Close bot session
    session = await dispatcher.bot.get_session()
    await session.close()
    
    logger.info("Bot shut down successfully")


if __name__ == '__main__':
    if config.PRODUCTION_ENV:
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
            skip_updates=True
        )
