import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext

import keyboards as kb

from app import dp, bot, logger, language_code
from bot_exceptions import CallbackException
from handlers import helpers
from s95 import latest, records
from s95.collations import CollationMaker
from s95.personal import PersonalResults
from utils import content
from utils.content import t


@dp.callback_query_handler(lambda c: c.data == 'most_records_parkruns')
@dp.throttled(helpers.handle_throttled_query, rate=3)
async def process_most_records_parkruns(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await records.top_records_count('gen_png/records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'personal_results')
@dp.throttled(rate=2)
async def process_personal_results(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        '*Представление ваших результатов.*\n'
        'Здесь можно сделать визуализацию ваших результатов за всю историю участия в забегах S95.',
        reply_markup=kb.inline_personal,
        parse_mode='Markdown'
    )


async def get_compared_pages(user_id):
    settings = {}  # await redis.get_value(user_id)
    athlete_id_1 = settings.get('id', None)
    athlete_id_2 = settings.get('compare_id', None)
    if not athlete_id_2:
        raise CallbackException('Вы не ввели parkrun ID участника для сравнения.\n'
                                'Нажмите кнопку Ввести ID участника.')
    if athlete_id_1 == athlete_id_2:
        raise CallbackException('Ваш parkrun ID не должен совпадать с parkrun ID, выбранного участника.')
    athlete_name_1 = await helpers.find_user_by('id', athlete_id_1)
    athlete_name_2 = await helpers.find_user_by('id', athlete_id_2)
    return athlete_name_1, athlete_name_2


@dp.callback_query_handler(lambda c: c.data == 'battle_diagram')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_battle_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = await asyncio.to_thread(lambda: CollationMaker(*pages).bars('gen_png/battle.png'))
    await bot.send_photo(user_id, pic, caption='Трактовка: чем меньше по высоте столбцы, тем ближе ваши результаты.')
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_scatter')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_battle_scatter(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю график. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = await asyncio.to_thread(lambda: CollationMaker(*pages).scatter('gen_png/scatter.png'))
    await bot.send_photo(user_id, pic, caption=content.battle_scatter_caption)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'battle_table')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_battle_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Рассчитываю таблицу. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    table_text = await asyncio.to_thread(lambda: CollationMaker(*pages).table())
    await bot.send_message(callback_query.from_user.id, table_text, parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'excel_table')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_excel_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Создаю файл. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    file_obj = await asyncio.to_thread(lambda: CollationMaker(*pages).to_excel('compare_parkrun.xlsx'))
    file_obj.close()
    await bot.send_document(
        user_id, types.InputFile('compare_parkrun.xlsx'),
        caption='Сравнительная таблица для анализа в Excel'
    )


@dp.callback_query_handler(lambda c: c.data == 'last_activity_diagram')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_last_activity_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with latest.make_latest_results_diagram(telegram_id, f'gen_png/results_{telegram_id}.png') as pic:
            await bot.send_photo(telegram_id, pic, caption=content.last_activity_caption)
    except Exception as e:
        logger.info(f'Failed to generate last activity diagram for {callback_query.from_user.id}: {e}')
        await bot.send_message(
            callback_query.from_user.id,
            'Не удалось построить диаграмму. Возможно, нет результатов.'
        )


@dp.callback_query_handler(lambda c: c.data == 'personal_history')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_personal_history_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).history() as pic:
            await bot.send_photo(telegram_id, pic, caption=content.personal_history_caption)
    except Exception as e:
        logger.info(f'Failed to generate personal history diagram for {callback_query.from_user.id}: {e}')
        await bot.send_message(
            callback_query.from_user.id,
            'Не удалось построить диаграмму. Возможно, нет результатов.'
        )


@dp.callback_query_handler(lambda c: c.data == 'personal_bests')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_personal_bests_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).personal_bests() as pic:
            await bot.send_photo(telegram_id, pic, caption=content.personal_bests_caption)
    except Exception as e:
        logger.info(f'Failed to generate personal bests diagram for {callback_query.from_user.id}: {e}')
        await bot.send_message(
            callback_query.from_user.id,
            'Не удалось построить диаграмму. Возможно, нет результатов.'
        )


@dp.callback_query_handler(lambda c: c.data == 'personal_tourism')
@dp.throttled(helpers.handle_throttled_query, rate=2)
async def process_personal_tourism_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).tourism() as pic:
            await bot.send_photo(telegram_id, pic, caption=content.personal_tourism_caption)
    except Exception as e:
        logger.info(f'Failed to generate personal tourism diagram for {callback_query.from_user.id}: {e}')
        await bot.send_message(
            callback_query.from_user.id,
            'Не удалось построить диаграмму. Возможно, нет результатов.'
        )


@dp.callback_query_handler(lambda c: c.data == 'personal_last')
@dp.throttled(helpers.handle_throttled_query, rate=1)
async def process_personal_last_parkruns_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).last_runs() as pic:
            await bot.send_photo(telegram_id, pic, caption='Трактовка: оцените прогресс (если он есть).')
    except Exception as e:
        logger.info(f'Failed to generate personal last parkruns diagram for {callback_query.from_user.id}: {e}')
        await bot.send_message(
            callback_query.from_user.id,
            'Не удалось построить диаграмму. Возможно, нет результатов.'
        )


@dp.callback_query_handler(lambda c: c.data == 'athlete_code_search')
async def process_athlete_code_search(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await helpers.UserStates.SEARCH_ATHLETE_CODE.set()
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'athlete_code_search'),
        parse_mode='Markdown',
        reply_markup=types.ReplyKeyboardRemove(selective=False)
    )


@dp.callback_query_handler(lambda c: c.data == 'help_to_find_id')
async def process_help_to_find_id(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if await state.get_state():
        await state.reset_state()
    await delete_message(callback_query)
    s95_kbd = await kb.inline_open_s95(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'help_to_find_id'),
        parse_mode='Markdown',
        reply_markup=s95_kbd
    )


@dp.callback_query_handler(lambda c: c.data == 'cancel_registration')
async def process_cancel_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id, 'Регистрация прервана')
    if await state.get_state():
        await state.reset_state()
    await delete_message(callback_query)
    kbd = await kb.main(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'available_commands'),
        reply_markup=kbd
    )


@dp.callback_query_handler(lambda c: c.data == 'start_registration')
async def process_start_registration(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Начинаем регистрацию')
    await delete_message(callback_query)
    find_athlete_kbd = await kb.inline_find_athlete_by_id(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'you_already_have_id'),
        reply_markup=find_athlete_kbd,
        parse_mode='Markdown'
    )


@dp.callback_query_handler(lambda c: c.data == 'create_new_athlete')
async def process_new_athlete_registration(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await helpers.UserStates.ATHLETE_LAST_NAME.set()
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'input_lastname'),
        reply_markup=types.ReplyKeyboardRemove(selective=False)
    )


@dp.callback_query_handler(lambda c: c.data == 'cancel_action')
async def process_cancel_action(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'request_cancelled')
    )


@dp.callback_query_handler(lambda c: c.data == 'cancel_action', state=helpers.ClubStates)
async def process_cancel_action_with_state(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'request_cancelled')
    )


@dp.callback_query_handler(lambda c: c.data == 'remove_club')
async def process_remove_club(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    result = await helpers.update_club(callback_query.from_user.id, None)
    if result:
        await bot.send_message(callback_query.from_user.id, 'Вы успешно вышли из клуба.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Не удалось удалить клуб. Попробуйте снова')


@dp.callback_query_handler(lambda c: c.data == 'ask_club')
async def process_ask_club(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        content.ask_club,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    await helpers.ClubStates.INPUT_NAME.set()


@dp.callback_query_handler(lambda c: c.data == 'set_club', state=helpers.ClubStates.CONFIRM_NAME)
async def process_set_club(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    async with state.proxy() as data:
        result = await helpers.update_club(callback_query.from_user.id, data['club_id'])
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
    await delete_message(callback_query)
    events_list = await helpers.events()
    message = content.ask_home_event
    for event in events_list:
        message += f'\n*{event["id"]}* - {event["name"]}'
    await bot.send_message(callback_query.from_user.id, message, parse_mode='Markdown')
    await helpers.HomeEventStates.INPUT_EVENT_ID.set()


@dp.callback_query_handler(lambda c: c.data == 'remove_home_event')
async def process_remove_home_event(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    result = await helpers.update_home_event(callback_query.from_user.id, None)
    if result:
        await bot.send_message(callback_query.from_user.id, 'Вы успешно удалили домашний забег.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Не удалось удалить домашний забег. Попробуйте снова')


async def delete_message(callback_query: types.CallbackQuery):
    try:
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    except Exception:
        logger.info("Message can't be deleted")
