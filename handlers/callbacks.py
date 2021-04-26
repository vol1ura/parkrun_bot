from aiogram import types
from vedis import Vedis

import keyboards as kb
from app import dp, bot, handle_throttled_query, logger
from bot_exceptions import CallbackException
from config import DB_FILE
from handlers.helper import UserStates
from utils import content, parkrun


@dp.callback_query_handler(lambda c: c.data == 'telegram')
async def process_callback_telegram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, content.telegram_channels,
                           parse_mode='Markdown', disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data == 'most_records_parkruns')
@dp.throttled(handle_throttled_query, rate=15)
async def process_most_records_parkruns(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await parkrun.top_records_count('records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'top_active_clubs')
@dp.throttled(handle_throttled_query, rate=15)
async def process_top_active_clubs(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = parkrun.top_active_clubs_diagram('top_clubs.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'personal_results')
@dp.throttled(rate=2)
async def process_personal_results(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        '*Сравнение персональных результатов.*\n'
        'Здесь можно сравнить свои результаты с результатами другого '
        'участника на тех паркранах, на которых вы когда-либо бежали вместе.\n'
        'Предварительно необходимо установить свой паркран ID (через меню настройки) '
        'и паркран ID участника для сравнения (кнопка Ввести ID участника)',
        reply_markup=kb.inline_personal, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'enter_compare_id')
@dp.throttled(handle_throttled_query, rate=15)
async def process_enter_compare_id(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        'Введите parkrunID участника - это те *цифры*, что написаны на штрих-кодах (*без буквы*). '
        'Это число можно также посмотреть на сайте parkrun.ru на страничке участника '
        'в адресной строке браузера (_athleteNumber_).', parse_mode='Markdown')
    await UserStates.COMPARE_ID.set()


async def get_compared_pages(user_id):
    with Vedis(DB_FILE) as db:
        h = db.Hash(user_id)
        athlete_id_1 = h['id'].decode() if h['id'] else None
        athlete_id_2 = h['compare_id'].decode() if h['compare_id'] else None
    if not athlete_id_1:
        raise CallbackException('Вы не ввели свой parkrun ID.\n'
                                'Перейдите в настройки и нажмите кнопку Выбрать участника')
    if not athlete_id_2:
        raise CallbackException('Вы не ввели parkrun ID участника для сравнения.\n'
                                'Нажмите кнопку Ввести ID участника.')
    if athlete_id_1 == athlete_id_2:
        raise CallbackException('Ваш parkrun ID не должен совпадать с parkrun ID, выбранного участника.')
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(f'A{athlete_id_1}')
            athlete_name_1 = h['athlete'].decode()
            athlete_page_1 = h['athlete_page'].decode()
            h = db.Hash(f'A{athlete_id_2}')
            athlete_name_2 = h['athlete'].decode()
            athlete_page_2 = h['athlete_page'].decode()
        except Exception as e:
            logger.error(e)
            raise CallbackException('Что-то пошло не так. Проверьте настройки или попробуйте ввести IDшники снова.')
    return athlete_name_1, athlete_page_1, athlete_name_2, athlete_page_2


@dp.callback_query_handler(lambda c: c.data == 'battle_diagram')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Построение диаграммы. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = parkrun.make_pic_battle('battle.png', *pages)
    await bot.send_photo(user_id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_table')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Расчёт таблицы. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    await bot.send_message(callback_query.from_user.id, parkrun.make_battle_table(*pages), parse_mode='Markdown')
