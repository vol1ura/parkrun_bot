from aiogram import types

import keyboards as kb

from app import dp
from handlers.helpers import find_athlete_by, find_user_by
from utils import content


@dp.message_handler(commands='start')
@dp.throttled(rate=5)
async def send_welcome(message: types.Message):
    await message.answer(content.start_message, reply_markup=kb.main, disable_notification=True)


@dp.message_handler(regexp='❓ справка')
@dp.message_handler(commands=['help', 'помощь'])
@dp.throttled(rate=3)
async def commands(message: types.Message):
    await message.delete()
    await message.answer(content.help_message,
                         disable_notification=True, parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(regexp='🔧 настройки')
@dp.message_handler(commands=['settings'])
@dp.throttled(rate=2)
async def process_command_settings(message: types.Message):
    await message.delete()
    telegram_id = message.from_user.id
    user = await find_user_by('telegram_id', telegram_id)
    if not user:
        return await message.answer("Вы пока не зарегистрированы. Хотите зарегистрироваться? Нажимая кнопку 'Да, я согласен' вы принимаете правила участия и даёте согласие на обработку персональных данных.", reply_markup=kb.inline_agreement)

    athlete = await find_athlete_by('user_id', user['id'])
    if not athlete:
        return await message.answer('Вы зарегистрированы, но участник почему-то не привязан или не создан.')
    await message.answer(f'Вы зарегистрированы. Ссылка на ваш профиль: https://s95.ru/athletes/{athlete["id"]}')


@dp.message_handler(regexp='🌳 Sat 9am 5km')
@dp.message_handler(commands=['statistics'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_stat)


@dp.message_handler(regexp='📋 разное')
@dp.message_handler(commands=['info'])
@dp.throttled(rate=2)
async def process_command_info(message: types.Message):
    await message.answer('Кое-что ещё:', reply_markup=kb.inline_info)
