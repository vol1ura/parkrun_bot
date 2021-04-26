from os import environ

from aiogram import Dispatcher
from aiogram.utils import executor

from config import *
from app import bot, setup_bot_commands, dp
from utils import parkrun
import handlers  # important import!!!


# Run after startup
async def on_startup(dispatcher: Dispatcher):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await parkrun.update_parkruns_list()
    await parkrun.update_parkruns_clubs()
    await setup_bot_commands(dispatcher)


# Run before shutdown
async def on_shutdown(dispatcher: Dispatcher):
    print("Shutting down..")
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    print("Bot down")


if __name__ == "__main__":
    if "HEROKU" in list(environ.keys()):
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
