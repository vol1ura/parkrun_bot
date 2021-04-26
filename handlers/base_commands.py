import random

from aiogram import types

import keyboards as kb
from app import dp, bot
from utils import content, fucomp


@dp.message_handler(commands='start')
@dp.throttled(rate=5)
async def send_welcome(message: types.Message):
    await message.answer(content.start_message, reply_markup=kb.main, disable_notification=True)


@dp.message_handler(regexp='❓ справка')
@dp.message_handler(commands=['help', 'помощь'])
@dp.throttled(rate=3)
async def commands(message: types.Message):
    await message.answer(content.help_message,
                         disable_notification=True, parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(commands=['admin', 'админ'])
@dp.message_handler(lambda message: fucomp.bot_compare(message.text, fucomp.phrases_admin))
@dp.throttled(rate=3)
async def admin(message: types.Message):
    if message.chat.type == 'private':  # private chat message
        await message.reply('Здесь нет админов, это персональный чат.')
    else:
        admin = random.choice(await bot.get_chat_administrators(message.chat.id)).user
        about_admin = f'\nАдмин @{admin.username} - {admin.first_name}  {admin.last_name}'
        await message.answer(random.choice(content.phrases_about_admin) + about_admin)


@dp.message_handler(regexp='🔧 настройки')
@dp.message_handler(commands=['settings'])
@dp.throttled(rate=2)
async def process_command_settings(message: types.Message):
    await message.answer('Установка параметров', reply_markup=kb.inline_parkrun)


@dp.message_handler(regexp='🌳 паркран')
@dp.message_handler(commands=['statistics'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_stat)


@dp.message_handler(regexp='📋 разное')
@dp.message_handler(commands=['info'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await message.answer('Кое-что ещё помимо паркранов:', reply_markup=kb.inline_info)
