import asyncio
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

import keyboards as kb

from app import dp, bot, logger, language_code, container
from bot_exceptions import CallbackException
from handlers import helpers
from s95 import latest, records
from s95.collations import CollationMaker
from s95.personal import PersonalResults
from services.country_service import CountryService
from utils import content
from utils.content import t, country_name


@dp.callback_query(F.data == 'most_records_parkruns')
async def process_most_records_parkruns(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await records.top_records_count('gen_png/records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query(F.data == 'personal_results')
async def process_personal_results(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    lang = language_code(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(lang, 'statistics_dashboard'),
        reply_markup=kb.inline_personal(lang),
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


@dp.callback_query(F.data == 'battle_diagram')
async def process_battle_diagram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, content.wait_diagram)
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = await asyncio.to_thread(lambda: CollationMaker(*pages).bars('gen_png/battle.png'))
    await bot.send_photo(user_id, pic, caption='Трактовка: чем меньше по высоте столбцы, тем ближе ваши результаты.')
    pic.close()


@dp.callback_query(F.data == 'battle_scatter')
async def process_battle_scatter(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Строю график. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    pic = await asyncio.to_thread(lambda: CollationMaker(*pages).scatter('gen_png/scatter.png'))
    await bot.send_photo(user_id, pic, caption=content.battle_scatter_caption)
    pic.close()


@dp.callback_query(F.data == 'battle_table')
async def process_battle_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Рассчитываю таблицу. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    table_text = await asyncio.to_thread(lambda: CollationMaker(*pages).table())
    await bot.send_message(callback_query.from_user.id, table_text, parse_mode='Markdown')


@dp.callback_query(F.data == 'excel_table')
async def process_excel_table(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Создаю файл. Подождите...')
    user_id = callback_query.from_user.id
    pages = await get_compared_pages(user_id)
    file_obj = await asyncio.to_thread(lambda: CollationMaker(*pages).to_excel('compare_parkrun.xlsx'))
    file_obj.close()
    await bot.send_document(
        user_id, FSInputFile('compare_parkrun.xlsx'),
        caption='Сравнительная таблица для анализа в Excel'
    )


@dp.callback_query(F.data == 'last_activity_diagram')
async def process_last_activity_diagram(callback_query: types.CallbackQuery):
    lang = language_code(callback_query)
    await bot.answer_callback_query(callback_query.id, t(lang, 'generating_diagram'))
    await bot.send_chat_action(chat_id=callback_query.from_user.id, action=types.ChatAction.UPLOAD_PHOTO)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with latest.make_latest_results_diagram(telegram_id, f'gen_png/results_{telegram_id}.png') as pic:
            await bot.send_photo(telegram_id, pic, caption=content.last_activity_caption)
    except Exception as e:
        logger.info(f'Failed to generate last activity diagram for {callback_query.from_user.id}: {e}')
        error_msg = t(lang, 'error_occurred').format(error_message='Не удалось построить диаграмму. Возможно, нет результатов.')
        await bot.send_message(
            callback_query.from_user.id,
            error_msg,
            parse_mode='Markdown'
        )


@dp.callback_query(F.data == 'personal_history')
async def process_personal_history_diagram(callback_query: types.CallbackQuery):
    lang = language_code(callback_query)
    await bot.answer_callback_query(callback_query.id, t(lang, 'generating_diagram'))
    await bot.send_chat_action(chat_id=callback_query.from_user.id, action=types.ChatAction.UPLOAD_PHOTO)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).history() as pic:
            await bot.send_photo(telegram_id, pic, caption=content.personal_history_caption)
    except Exception as e:
        logger.info(f'Failed to generate personal history diagram for {callback_query.from_user.id}: {e}')
        error_msg = t(lang, 'error_occurred').format(error_message='Не удалось построить диаграмму. Возможно, нет результатов.')
        await bot.send_message(
            callback_query.from_user.id,
            error_msg,
            parse_mode='Markdown'
        )


@dp.callback_query(F.data == 'personal_bests')
async def process_personal_bests_diagram(callback_query: types.CallbackQuery):
    lang = language_code(callback_query)
    await bot.answer_callback_query(callback_query.id, t(lang, 'generating_diagram'))
    await bot.send_chat_action(chat_id=callback_query.from_user.id, action=types.ChatAction.UPLOAD_PHOTO)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).personal_bests() as pic:
            await bot.send_photo(telegram_id, pic, caption=content.personal_bests_caption)
    except Exception as e:
        logger.info(f'Failed to generate personal bests diagram for {callback_query.from_user.id}: {e}')
        error_msg = t(lang, 'error_occurred').format(error_message='Не удалось построить диаграмму. Возможно, нет результатов.')
        await bot.send_message(
            callback_query.from_user.id,
            error_msg,
            parse_mode='Markdown'
        )


@dp.callback_query(F.data == 'personal_tourism')
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


@dp.callback_query(F.data == 'personal_last')
async def process_personal_last_parkruns_diagram(callback_query: types.CallbackQuery):
    lang = language_code(callback_query)
    await bot.answer_callback_query(callback_query.id, t(lang, 'generating_diagram'))
    await bot.send_chat_action(chat_id=callback_query.from_user.id, action=types.ChatAction.UPLOAD_PHOTO)
    await delete_message(callback_query)
    try:
        telegram_id = callback_query.from_user.id
        async with PersonalResults(telegram_id).last_runs() as pic:
            await bot.send_photo(telegram_id, pic, caption='Трактовка: оцените прогресс (если он есть).')
    except Exception as e:
        logger.info(f'Failed to generate personal last parkruns diagram for {callback_query.from_user.id}: {e}')
        error_msg = t(lang, 'error_occurred').format(error_message='Не удалось построить диаграмму. Возможно, нет результатов.')
        await bot.send_message(
            callback_query.from_user.id,
            error_msg,
            parse_mode='Markdown'
        )


@dp.callback_query(F.data == 'athlete_code_search')
async def process_athlete_code_search(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(helpers.UserStates.SEARCH_ATHLETE_CODE)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'athlete_code_search'),
        parse_mode='Markdown',
        reply_markup=types.ReplyKeyboardRemove(selective=False)
    )


@dp.callback_query(F.data == 'help_to_find_id')
async def process_help_to_find_id(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if await state.get_state():
        await state.clear()
    await delete_message(callback_query)
    s95_kbd = await kb.inline_open_s95(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'help_to_find_id'),
        parse_mode='Markdown',
        reply_markup=s95_kbd
    )


@dp.callback_query(F.data == 'cancel_registration')
async def process_cancel_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id, 'Регистрация прервана')
    if await state.get_state():
        await state.clear()
    await delete_message(callback_query)
    kbd = await kb.main(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'available_commands'),
        reply_markup=kbd
    )


@dp.callback_query(F.data == 'start_registration')
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


@dp.callback_query(F.data == 'create_new_athlete')
async def process_new_athlete_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await state.set_state(helpers.UserStates.ATHLETE_LAST_NAME)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'input_lastname'),
        reply_markup=types.ReplyKeyboardRemove(selective=False),
        parse_mode='Markdown'
    )


@dp.callback_query(F.data == 'cancel_action')
async def process_cancel_action(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'request_cancelled')
    )


@dp.callback_query(helpers.LoginStates.SELECT_DOMAIN, F.data.startswith('domain_'))
async def process_domain_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    domain = callback_query.data.split('_')[1]  # domain_ru -> ru
    data = await state.get_data()
    user_id = data.get('user_id')

    if not user_id:
        await state.clear()
        return await bot.send_message(
            callback_query.from_user.id,
            t(language_code(callback_query), 'something_wrong')
        )

    auth_link = await helpers.get_auth_link(user_id, domain)
    await state.clear()
    await delete_message(callback_query)

    if not auth_link:
        return await bot.send_message(
            callback_query.from_user.id,
            t(language_code(callback_query), 'login_link_error'),
            reply_markup=await kb.main(callback_query)
        )

    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'your_login_link').format(link=auth_link),
        reply_markup=await kb.main(callback_query),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


@dp.callback_query(helpers.ClubStates(), F.data == 'cancel_action')
async def process_cancel_action_with_state(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await state.clear()
    await bot.send_message(
        callback_query.from_user.id,
        t(language_code(callback_query), 'request_cancelled')
    )


@dp.callback_query(F.data == 'remove_club')
async def process_remove_club(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    result = await helpers.update_club(callback_query.from_user.id, None)
    if result:
        await bot.send_message(callback_query.from_user.id, 'Вы успешно вышли из клуба.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Не удалось удалить клуб. Попробуйте снова')


@dp.callback_query(F.data == 'ask_club')
async def process_ask_club(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        content.ask_club,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    await state.set_state(helpers.ClubStates.INPUT_NAME)


@dp.callback_query(helpers.ClubStates.CONFIRM_NAME, F.data == 'set_club')
async def process_set_club(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    data = await state.get_data()
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
    await state.clear()


@dp.callback_query(F.data == 'ask_home_event')
async def process_ask_home_event(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    country_service = container.resolve(CountryService)
    countries_list = await country_service.find_all_countries()

    lang = language_code(callback_query)
    message = 'Выберите страну вашего домашнего забега:\n\n'
    for country in countries_list:
        localized_name = country_name(lang, country["code"])
        message += f'*{country["id"]}* - {localized_name}\n'
    message += '\n*Введите число* из приведённого выше списка, либо /reset для отмены'

    await bot.send_message(callback_query.from_user.id, message, parse_mode='Markdown')
    await state.set_state(helpers.HomeEventStates.SELECT_COUNTRY)
    await delete_message(callback_query)


@dp.callback_query(F.data == 'remove_home_event')
async def process_remove_home_event(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    result = await helpers.update_home_event(callback_query.from_user.id, None)
    if result:
        await bot.send_message(callback_query.from_user.id, 'Вы успешно удалили домашний забег.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Не удалось удалить домашний забег. Попробуйте снова')


# Обработчики для интерактивной справки
@dp.callback_query(F.data == 'help_qr')
async def process_help_qr(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    lang = language_code(callback_query)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=t(lang, 'help_section_qr'),
        parse_mode='Markdown',
        reply_markup=callback_query.message.reply_markup
    )


@dp.callback_query(F.data == 'help_stats')
async def process_help_stats(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    lang = language_code(callback_query)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=t(lang, 'help_section_stats'),
        parse_mode='Markdown',
        reply_markup=callback_query.message.reply_markup
    )


@dp.callback_query(F.data == 'help_settings')
async def process_help_settings(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    lang = language_code(callback_query)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=t(lang, 'help_section_settings'),
        parse_mode='Markdown',
        reply_markup=callback_query.message.reply_markup
    )


@dp.callback_query(F.data == 'help_general')
async def process_help_general(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    lang = language_code(callback_query)
    from config import VERSION
    help_text = t(lang, 'help_message').format(VERSION)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=help_text,
        parse_mode='Markdown',
        reply_markup=callback_query.message.reply_markup
    )


@dp.callback_query(F.data == 'help_back')
async def process_help_back(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    lang = language_code(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(lang, 'available_commands'),
        reply_markup=await kb.main(callback_query)
    )


# Обработчики для настроек
@dp.callback_query(F.data == 'settings_home')
async def process_settings_home(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    from handlers.base_commands import process_command_home
    # Создаём временное сообщение для обработчика
    message = types.Message(
        message_id=callback_query.message.message_id,
        date=callback_query.message.date,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        content_type='text',
        text='/home'
    )
    await process_command_home(message)


@dp.callback_query(F.data == 'settings_club')
async def process_settings_club(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    from handlers.base_commands import process_command_club
    message = types.Message(
        message_id=callback_query.message.message_id,
        date=callback_query.message.date,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        content_type='text',
        text='/club'
    )
    await process_command_club(message)


@dp.callback_query(F.data == 'settings_phone')
async def process_settings_phone(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    from handlers.base_commands import process_command_phone
    message = types.Message(
        message_id=callback_query.message.message_id,
        date=callback_query.message.date,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        content_type='text',
        text='/phone'
    )
    await process_command_phone(message)


@dp.callback_query(F.data == 'settings_back')
async def process_settings_back(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_message(callback_query)
    lang = language_code(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        t(lang, 'available_commands'),
        reply_markup=await kb.main(callback_query)
    )


async def delete_message(callback_query: types.CallbackQuery):
    try:
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    except Exception:
        logger.info("Message can't be deleted")
