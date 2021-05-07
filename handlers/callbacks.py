from aiogram import types
from vedis import Vedis

import keyboards as kb
from app import dp, bot, logger
from bot_exceptions import CallbackException
from config import DB_FILE
from handlers.helpers import UserStates, handle_throttled_query, add_db_athlete
from parkrun import records, clubs
from parkrun.collations import CollationMaker
from parkrun.personal import PersonalResults
from utils import content, redis


@dp.callback_query_handler(lambda c: c.data == 'telegram')
async def process_callback_telegram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, content.telegram_channels,
                           parse_mode='Markdown', disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data == 'most_records_parkruns')
@dp.throttled(handle_throttled_query, rate=6)
async def process_most_records_parkruns(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await records.top_records_count('records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'top_active_clubs')
@dp.throttled(handle_throttled_query, rate=6)
async def process_top_active_clubs(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = clubs.top_active_clubs_diagram('top_clubs.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'compare_results')
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
        reply_markup=kb.inline_compare, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'personal_results')
@dp.throttled(rate=2)
async def process_personal_results(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        '*Представление ваших результатов.*\n'
        'Здесь можно сделать визуализацию ваших результатов за всю историю участия в Parkrun.\n'
        'Предварительно необходимо установить свой паркран ID (через меню *настройки*).',
        reply_markup=kb.inline_personal, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'enter_compare_id')
@dp.throttled(handle_throttled_query, rate=8)
async def process_enter_compare_id(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        'Введите parkrunID участника - это те *цифры*, что написаны на штрих-кодах (*без буквы*). '
        'Это число можно также посмотреть на сайте parkrun.ru на страничке участника '
        'в адресной строке браузера (_athleteNumber_).', parse_mode='Markdown')
    await UserStates.COMPARE_ID.set()


async def get_compared_pages(user_id):
    settings = await redis.get_value(user_id)
    athlete_id_1 = settings.get('id', None)
    athlete_id_2 = settings.get('compare_id', None)
    if not athlete_id_1:
        raise CallbackException('Вы не ввели свой parkrun ID.\n'
                                'Перейдите в настройки и нажмите кнопку Выбрать участника')
    if not athlete_id_2:
        raise CallbackException('Вы не ввели parkrun ID участника для сравнения.\n'
                                'Нажмите кнопку Ввести ID участника.')
    if athlete_id_1 == athlete_id_2:
        raise CallbackException('Ваш parkrun ID не должен совпадать с parkrun ID, выбранного участника.')
    athlete_name_1 = await add_db_athlete(athlete_id_1)
    athlete_name_2 = await add_db_athlete(athlete_id_2)
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(f'A{athlete_id_1}')
            athlete_page_1 = h['athlete_page'].decode()
            h = db.Hash(f'A{athlete_id_2}')
            athlete_page_2 = h['athlete_page'].decode()
        except Exception as e:
            logger.error(e)
            raise CallbackException('Что-то пошло не так. Проверьте настройки или попробуйте ввести ID-шники снова.')
    return athlete_name_1, athlete_page_1, athlete_name_2, athlete_page_2


async def get_personal_page(user_id):
    settings = await redis.get_value(user_id)
    athlete_id = settings.get('id', None)
    if not athlete_id:
        raise CallbackException('Вы не ввели свой parkrun ID.\n'
                                'Перейдите в настройки и нажмите кнопку Выбрать участника')
    athlete_name = await add_db_athlete(athlete_id)
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(f'A{athlete_id}')
            athlete_page = h['athlete_page'].decode()
        except Exception as e:
            logger.error(e)
            raise CallbackException('Что-то пошло не так. Проверьте настройки или попробуйте ввести ID-шники снова.')
    return athlete_name, athlete_page


@dp.callback_query_handler(lambda c: c.data == 'battle_diagram')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю диаграмму. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = CollationMaker(*pages).bars('battle.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: чем меньше по высоте столбцы, тем ближе ваши результаты.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_scatter')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_scatter(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю график. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = CollationMaker(*pages).scatter('scatter.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: каждая точка - совместный забег, чем ближе точки к '
                                               'левому нижнему углу и красной линией, тем  больше соперничество.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_table')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Рассчитываю таблицу. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    await bot.send_message(callback_query.from_user.id, CollationMaker(*pages).table(), parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'excel_table')
@dp.throttled(handle_throttled_query, rate=10)
async def process_excel_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Создаю файл. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    CollationMaker(*pages).to_excel('compare_parkrun.xlsx').close()
    await bot.send_document(user_id, types.InputFile('compare_parkrun.xlsx'),
                            caption='Сравнительная таблица для анализа в Excel')


@dp.callback_query_handler(lambda c: c.data == 'personal_history')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_history_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю диаграмму. Подождите...')
    user_id = callback_query.from_user.id
    page = await get_personal_page(user_id)
    pic = PersonalResults(*page).history('participate.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: равномерность и интенсивность цвета показывает '
                                               'регулярность участия в паркранах.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'personal_bests')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_bests_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю диаграмму. Подождите...')
    user_id = callback_query.from_user.id
    page = await get_personal_page(user_id)
    pic = PersonalResults(*page).personal_bests('pb.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: по цвету можно понять, когда у вас были лучшие результаты.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'personal_tourism')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_tourism_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю диаграмму. Подождите...')
    user_id = callback_query.from_user.id
    page = await get_personal_page(user_id)
    pic = PersonalResults(*page).tourism('tourism.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: по цвету можно понять, когда и как часто вы '
                                               'посещали разные паркраны.')
    pic.close()
