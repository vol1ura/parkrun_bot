import logging
import random

from aiogram import Bot, Dispatcher, types, executor

from config import *
from utils import content, fucomp

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.DEBUG)


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, text=content.start_message, disable_notification=True)


@dp.message_handler(commands=['help', 'помощь'])
async def commands(message):
    await bot.send_message(message.chat.id, text=content.help_message, disable_notification=True, parse_mode='html')


@dp.message_handler(commands=['admin', 'админ'])
@dp.message_handler(lambda message: fucomp.bot_compare(message.text, fucomp.phrases_admin))
async def admin(message):
    if message.chat.type == 'private':  # private chat message
        await message.reply('Здесь нет админов, это персональный чат.')
    else:
        admin = random.choice(await bot.get_chat_administrators(message.chat.id)).user
        about_admin = f"\nАдмин @{admin.username} - {admin.first_name}  {admin.last_name}"
        await bot.send_message(message.chat.id, random.choice(content.phrases_about_admin) + about_admin)


# Run after startup
async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


# Run before shutdown
async def on_shutdown(dp):
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == "__main__":
    if "HEROKU" in list(os.environ.keys()):
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
