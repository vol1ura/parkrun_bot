from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb

from app import dp, bot
from bot_exceptions import CallbackException
from handlers.helpers import ClubStates, HomeEventStates, UserStates, events, handle_throttled_query, find_user_by, update_club
from s95 import latest, records, clubs
from s95.collations import CollationMaker
from s95.personal import PersonalResults
from utils import content


@dp.callback_query_handler(lambda c: c.data == 'most_records_parkruns')
@dp.throttled(handle_throttled_query, rate=6)
async def process_most_records_parkruns(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await records.top_records_count('gen_png/records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'top_active_clubs')
@dp.throttled(handle_throttled_query, rate=6)
async def process_top_active_clubs(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = clubs.top_active_clubs_diagram('gen_png/top_clubs.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'compare_results')
@dp.throttled(rate=2)
async def process_compare_results(callback_query: types.CallbackQuery):
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
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        '*Представление ваших результатов.*\n'
        'Здесь можно сделать визуализацию ваших результатов за всю историю участия в забегах S95.',
        reply_markup=kb.inline_personal, 
        parse_mode='Markdown'
    )


async def get_compared_pages(user_id):
    settings = None # await redis.get_value(user_id)
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
    athlete_name_1 = await find_user_by('id', athlete_id_1)
    athlete_name_2 = await find_user_by('id', athlete_id_2)
    # with Vedis(DB_FILE) as db:
    #     try:
    #         h = db.Hash(f'A{athlete_id_1}')
    #         athlete_page_1 = h['athlete_page'].decode()
    #         h = db.Hash(f'A{athlete_id_2}')
    #         athlete_page_2 = h['athlete_page'].decode()
    #     except Exception as e:
    #         logger.error(e)
    #         raise CallbackException('Что-то пошло не так. Проверьте настройки или попробуйте ввести ID-шники снова.')
    return athlete_name_1, athlete_name_2


@dp.callback_query_handler(lambda c: c.data == 'battle_diagram')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = CollationMaker(*pages).bars('gen_png/battle.png')
    await bot.send_photo(user_id, pic, caption='Трактовка: чем меньше по высоте столбцы, тем ближе ваши результаты.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_scatter')
@dp.throttled(handle_throttled_query, rate=10)
async def process_battle_scatter(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю график. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = CollationMaker(*pages).scatter('gen_png/scatter.png')
    await bot.send_photo(user_id, pic, caption=content.battle_scatter_caption)
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


@dp.callback_query_handler(lambda c: c.data == 'last_activity_diagram')
@dp.throttled(handle_throttled_query, rate=10)
async def process_last_activity_diagram(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id, content.wait_diagram)
        telegram_id = callback_query.from_user.id
        pic = await latest.make_latest_results_diagram(telegram_id, 'gen_png/results.png')
        await bot.send_photo(telegram_id, pic, caption=content.last_activity_caption)
        pic.close()
    except Exception:
        await bot.send_message(callback_query.from_user.id, 'Не удалось построить диаграмму. Возможно, нет результатов.')


@dp.callback_query_handler(lambda c: c.data == 'personal_history')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_history_diagram(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id, content.wait_diagram)
        telegram_id = callback_query.from_user.id
        pic = await PersonalResults(telegram_id).history('gen_png/participate.png')
        await bot.send_photo(telegram_id, pic, caption=content.personal_history_caption)
        pic.close()
    except Exception:
        await bot.send_message(callback_query.from_user.id, 'Не удалось построить диаграмму. Возможно, нет результатов.')


@dp.callback_query_handler(lambda c: c.data == 'personal_bests')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_bests_diagram(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id, content.wait_diagram)
        telegram_id = callback_query.from_user.id
        pic = await PersonalResults(telegram_id).personal_bests('gen_png/pb.png')
        await bot.send_photo(telegram_id, pic, caption=content.personal_bests_caption)
        pic.close()
    except Exception:
        await bot.send_message(callback_query.from_user.id, 'Не удалось построить диаграмму. Возможно, нет результатов.')


@dp.callback_query_handler(lambda c: c.data == 'personal_tourism')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_tourism_diagram(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id, content.wait_diagram)
        telegram_id = callback_query.from_user.id
        pic = await PersonalResults(telegram_id).tourism('gen_png/tourism.png')
        await bot.send_photo(telegram_id, pic, caption=content.personal_tourism_caption)
        pic.close()
    except Exception:
        await bot.send_message(callback_query.from_user.id, 'Не удалось построить диаграмму. Возможно, нет результатов.')


@dp.callback_query_handler(lambda c: c.data == 'personal_last')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_last_parkruns_diagram(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id, content.wait_diagram)
        telegram_id = callback_query.from_user.id
        pic = await PersonalResults(telegram_id).last_runs('gen_png/last_runs.png')
        await bot.send_photo(telegram_id, pic, caption='Трактовка: оцените прогресс (если он есть).')
        pic.close()
    except Exception:
        await bot.send_message(callback_query.from_user.id, 'Не удалось построить диаграмму. Возможно, нет результатов.')


@dp.callback_query_handler(lambda c: c.data == 'personal_wins')
@dp.throttled(handle_throttled_query, rate=10)
async def process_personal_wins_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Рассчитываю таблицу. Подождите...')
    telegram_id = callback_query.from_user.id
    table = await PersonalResults(telegram_id).wins_table()
    await bot.send_message(callback_query.from_user.id, table, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'athlete_code_search')
@dp.throttled(rate=5)
async def process_athlete_code_search(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await UserStates.SEARCH_ATHLETE_CODE.set()
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, content.athlete_code_search, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'help_to_find_id')
async def process_help_to_find_id(callback_query: types.CallbackQuery, state: FSMContext):
    if await state.get_state():
        await state.reset_state()
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, content.help_to_find_id,
                           parse_mode='Markdown', reply_markup=kb.inline_open_s95)


@dp.callback_query_handler(lambda c: c.data == 'cancel_registration')
async def process_cancel_registration(callback_query: types.CallbackQuery, state: FSMContext):
    if await state.get_state():
        await state.reset_state()
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    kbd = await kb.main(callback_query.from_user.id)
    await bot.send_message(
        callback_query.from_user.id,
        'Все команды доступны через левое нижнее меню',
        reply_markup=kbd
    )


@dp.callback_query_handler(lambda c: c.data == 'start_registration')
async def process_start_registration(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(
        callback_query.from_user.id,
        content.you_already_have_id,
        reply_markup=kb.inline_find_athlete_by_id
    )


@dp.callback_query_handler(lambda c: c.data == 'create_new_athlete')
async def process_new_athlete_registration(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await UserStates.ATHLETE_LAST_NAME.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите пожалуйста свою *Фамилию*',
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )

    
@dp.callback_query_handler(lambda c: c.data == 'cancel_action')
async def process_cancel_action(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, 'Действие отменено')


@dp.callback_query_handler(lambda c: c.data == 'cancel_action', state=ClubStates)
async def process_cancel_action_with_state(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, 'Действие отменено')


@dp.callback_query_handler(lambda c: c.data == 'ask_club')
async def process_ask_club(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await bot.send_message(
        callback_query.from_user.id, 
        content.ask_club, 
        parse_mode='Markdown', 
        disable_web_page_preview=True
    )
    await ClubStates.INPUT_NAME.set()


@dp.callback_query_handler(lambda c: c.data == 'set_club', state=ClubStates.CONFIRM_NAME)
async def process_set_club(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    async with state.proxy() as data:
        result = await update_club(callback_query.from_user.id, data['club_id'])
        if result:
            await bot.send_message(
                callback_query.from_user.id, 
                f'Клуб [{data["club_name"]}](https://s95.ru/clubs/{data["club_id"]}) установлен', 
                parse_mode='Markdown', 
                disable_web_page_preview=False
            )
        else:
            await bot.send_message(callback_query.from_user.id, 'Не удалось установить клуб. Попробуйте снова')
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'ask_home_event')
async def process_ask_home_event(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    events_list = await events()
    message = content.ask_home_event
    for event in events_list:
        message += f'\n*{event["id"]}* - {event["name"]}'
    await bot.send_message(callback_query.from_user.id, message, parse_mode='Markdown')
    await HomeEventStates.INPUT_EVENT_ID.set()
