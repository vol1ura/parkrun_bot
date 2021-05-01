from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp, bot
from handlers.helpers import UserStates, add_db_athlete
from utils import redis


@dp.message_handler(state=UserStates.ATHLETE_ID)
async def process_user_enter_athlete_id(message: types.Message, state: FSMContext):
    athlete_id = message.text.strip()
    athlete_name = await add_db_athlete(athlete_id)
    if athlete_name:
        await redis.set_value(str(message.from_user.id), id=athlete_id, name=athlete_name)
        await bot.send_message(message.chat.id, f'Отлично, {athlete_name}, запомнил!')
        await state.finish()
    else:
        await bot.send_message(message.chat.id, 'Не удалось найти участника с таким ID проверьте корректность ввода. '
                                                'Введите свой ID снова, либо /reset для отмены запроса.')


@dp.message_handler(state=UserStates.COMPARE_ID)
async def process_user_enter_compare_id(message: types.Message, state: FSMContext):
    athlete_id = message.text.strip()
    athlete_name = await add_db_athlete(athlete_id)
    if athlete_name:
        await redis.set_value(str(message.from_user.id), compare_id=athlete_id)
        await bot.send_message(message.chat.id, f'*Участник*: {athlete_name}.\n'
                                                f'Данные сохранены.', parse_mode='Markdown')
        await state.finish()
    else:
        await bot.send_message(message.chat.id, 'Не удалось найти участника с таким ID проверьте корректность ввода.'
                                                'Введите свой ID снова, либо /reset для отмены запроса.')
