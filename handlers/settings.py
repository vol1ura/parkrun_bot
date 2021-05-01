from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb
from app import bot, dp
from handlers.helpers import UserStates
from parkrun import helpers, clubs
from utils import content, redis


@dp.message_handler(commands='reset', state='*')
@dp.throttled(rate=1)
async def process_command_reset(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.reset_state()
    await message.reply('Запрос отменён')


@dp.callback_query_handler(lambda c: c.data == 'check_settings')
@dp.throttled(rate=5)
async def check_settings(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Получение данных..')
    user_id = callback_query.from_user.id
    settings = await redis.get_value(user_id)
    mes1 = settings.get('pr', 'не выбран')
    mes2 = settings.get('cl', 'не выбран')
    mes3 = settings.get('name', 'не выбран')
    # except Exception as e:
    #     logger.error(f'Getting settings from DB failed for user {user_id}. Error: {e}')
    #     return await bot.answer_callback_query(callback_query.id,
    #                                            text='⛔ Не удалось получить настройки.',
    #                                            show_alert=True)
    await bot.send_message(callback_query.from_user.id, f'*Паркран*: {mes1}\n'
                                                        f'*Клуб*: {mes2}\n'
                                                        f'*Участник*: {mes3}', parse_mode='Markdown')


@dp.message_handler(commands=['setparkrun'])
@dp.throttled(rate=4)
async def process_command_setparkrun(message: types.Message):
    parkrun_name = message.get_args()
    if not parkrun_name:
        return await message.answer(content.no_parkrun_message, reply_markup=kb.main)
    if not next((True for p in helpers.PARKRUNS if parkrun_name.lower() == p.lower()), False):
        return await message.answer('В моей базе нет такого паркрана. Проверьте ввод.')
    user_id = message.from_user.id
    await redis.set_value(user_id, pr=parkrun_name)
    return await message.answer(content.success_parkrun_set.format(parkrun_name), parse_mode='Markdown')


@dp.message_handler(commands=['setclub'])
@dp.throttled(rate=4)
async def process_command_setclub(message: types.Message):
    club = message.get_args()
    if not club:
        return await message.answer(content.no_club_message, reply_markup=kb.main)
    if club.isdigit():
        club_id = club
        club = await clubs.check_club_as_id(club)
    else:
        club_id = next((c['id'] for c in helpers.CLUBS if c['name'] == club), None)
    if not (club_id and club):
        return await message.answer('В базе нет такого клуба. Проверьте ввод.')
    user_id = message.from_user.id
    await redis.set_value(user_id, cl=club, cl_id=club_id)
    return await message.answer(content.success_club_set.format(club, club_id),
                                disable_web_page_preview=True, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'set_athlete')
@dp.throttled(rate=5)
async def process_callback_set_athlete(callback_query: types.CallbackQuery):
    # запрашиваем у пользователя его айдишник в системе паркран
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    await UserStates.ATHLETE_ID.set()
    await bot.send_message(user_id,
                           'Введите свой номер в системе parkrun (*цифры* с вашего штрих-кода, *без буквы*).',
                           parse_mode='Markdown')
