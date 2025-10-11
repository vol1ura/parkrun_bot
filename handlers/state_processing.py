import aiohttp
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from config import INTERNAL_API_URL

import keyboards as kb

from app import dp, language_code, container
from handlers import helpers
from s95.athlete_code import AthleteCode
from services.athlete_service import AthleteService
from services.club_service import ClubService
from services.country_service import CountryService
from services.event_service import EventService
from utils.content import t, home_event_notice, country_name


PROCEED_CREATION_REGEXP = '(Всё верно, создать|Okay, proceed|Ok, nastavi)'
CANCEL_REGEXP = '(Отмена|Otkaži|Cancel)'
LINK_ATHLETE_REGEXP = '(Это я, привязать|Yes, it is me|Da, to sam ja)'
GENDERS_LIST = ['мужской', 'женский', 'male', 'female', 'muški', 'ženski']
MALE_LIST = ['мужской', 'male', 'muški']


@dp.message_handler(state=helpers.UserStates.SEARCH_ATHLETE_CODE)
async def process_user_enter_parkrun_code(message: types.Message, state: FSMContext):
    athlete_code = AthleteCode(message.text)
    if not athlete_code.is_valid:
        return await message.reply(t(language_code(message), 'input_athletes_id'))

    athlete_service = container.resolve(AthleteService)

    # Update state with code information
    await helpers.UserStates.next()
    if athlete_code.key == 's95':
        await state.update_data(parkrun_code=None)
    else:
        await state.update_data(**{athlete_code.key: athlete_code.value})

    # Find athlete by code
    athlete = await athlete_service.find_athlete_by_code(athlete_code.key, athlete_code.value)

    if athlete:
        if athlete["user_id"]:
            await state.finish()
            return await message.answer(t(language_code(message), 'user_exists_linked'))

        # Process found athlete
        async with state.proxy() as data:
            data['athlete_id'] = athlete['id']
            names_list = re.split(r'\s', athlete['name'] or '', maxsplit=1)
            if len(names_list) < 2:
                names_list.insert(0, 'Noname')
            data['first_name'], data['last_name'] = names_list
            data['male'] = athlete['male']

        accept_athlete_kbd = await kb.accept_athlete(message)
        await message.answer(
            t(language_code(message), 'found_athlete_info').format(athlete_id=athlete['id'], name=athlete['name']),
            reply_markup=accept_athlete_kbd,
            parse_mode='html'
        )
    else:
        # Athlete not found, offer to create new
        new_athlete_kbd = await kb.ask_for_new_athlete(message)
        await message.reply(
            t(language_code(message), 'athlete_code_check')
            .format(athlete_id=athlete_code.value, url=athlete_code.url),
            reply_markup=new_athlete_kbd,
            parse_mode='html',
            disable_web_page_preview=True
        )


# Сразу переходим к подтверждению
@dp.message_handler(state=helpers.UserStates.SAVE_WITH_PARKRUN_CODE, regexp=LINK_ATHLETE_REGEXP)
async def process_save_with_parkrun_code(message: types.Message, state: FSMContext):
    confirm_kbd = await kb.confirm_registration(message)
    async with state.proxy() as data:
        await message.answer(
            t(language_code(message), 'confirm_personal_data').format(
                first_name=data['first_name'],
                last_name=data['last_name'],
                gender=t(language_code(message), 'btn_male' if data['male'] else 'btn_female')
            ),
            parse_mode='Markdown',
            reply_markup=confirm_kbd
        )
    await helpers.UserStates.CONFIRM.set()


# Запрашиваем Фамилию
@dp.message_handler(state=helpers.UserStates.SAVE_WITH_PARKRUN_CODE, regexp=PROCEED_CREATION_REGEXP)
async def process_ask_athlete_last_name(message: types.Message):
    await helpers.UserStates.next()
    await message.answer(
        t(language_code(message), 'input_lastname'),
        reply_markup=types.ReplyKeyboardRemove(selective=False)
    )


@dp.message_handler(state=helpers.UserStates.SAVE_WITH_PARKRUN_CODE)
async def process_cancel_parkrun_code(message: types.Message, state: FSMContext):
    await state.finish()
    kbd = await kb.main(message)
    await message.reply(t(language_code(message), 'request_cancelled'), reply_markup=kbd)


# Получаем Фамилию
# Запрашиваем Имя
@dp.message_handler(state=helpers.UserStates.ATHLETE_LAST_NAME, regexp=r'\A[^\W\d_]+([-\'][^\W\d_]{2,})?\Z')
async def process_get_athlete_last_name(message: types.Message, state: FSMContext):
    await helpers.UserStates.next()
    await state.update_data(last_name=message.text.upper())
    await message.answer(t(language_code(message), 'input_firstname'))


@dp.message_handler(state=helpers.UserStates.ATHLETE_LAST_NAME)
async def process_repeat_last_name(message: types.Message):
    await message.answer(
        t(language_code(message), 'input_lastname_again'),
        reply_markup=types.ReplyKeyboardRemove(selective=False)
    )


# Сохраняем Имя
# Запрашиваем Пол
@dp.message_handler(state=helpers.UserStates.ATHLETE_FIRST_NAME, regexp=r'\A[^\W\d_]+(?:-[^\W\d_]{2,})?\Z')
async def process_get_athlete_first_name(message: types.Message, state: FSMContext):
    await helpers.UserStates.next()
    await state.update_data(first_name=message.text)
    gender_kbd = await kb.select_gender(message)
    await message.answer(t(language_code(message), 'input_gender'), reply_markup=gender_kbd)


# Повторно запрашиваем имя, если не сработала регулярка
@dp.message_handler(state=helpers.UserStates.ATHLETE_FIRST_NAME)
async def process_repeat_first_name(message: types.Message):
    await message.answer(t(language_code(message), 'input_firstname_again'))


# Запрашиваем Пол ещё раз
@dp.message_handler(lambda m: m.text.strip().lower() not in GENDERS_LIST, state=helpers.UserStates.GENDER)
async def process_gender_invalid(message: types.Message):
    gender_kbd = await kb.select_gender(message)
    await message.reply(t(language_code(message), 'define_your_gender'), reply_markup=gender_kbd)


# Сохраняем Пол
# Просим подтвердить все данные
@dp.message_handler(state=helpers.UserStates.GENDER)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['male'] = message.text.strip().lower() in MALE_LIST
        confirm_kbd = await kb.confirm_registration(message)
        await message.answer(
            t(language_code(message), 'confirm_personal_data').format(
                first_name=data['first_name'],
                last_name=data['last_name'],
                gender=t(language_code(message), 'btn_male' if data['male'] else 'btn_female')
            ),
            parse_mode='Markdown',
            reply_markup=confirm_kbd
        )
    await helpers.UserStates.next()


@dp.message_handler(state=helpers.UserStates.CONFIRM, regexp=PROCEED_CREATION_REGEXP)
async def confirm_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        payload = {
            'user': {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'telegram_id': message.from_user.id,
                'telegram_user': message.from_user.username
            }
        }
        if 'athlete_id' in data:
            payload['athlete_id'] = data['athlete_id']
        else:
            payload['athlete'] = {
                'name': f'{data["first_name"]} {data["last_name"]}',
                'male': data['male'],
                'parkrun_code': data['parkrun_code'] if 'parkrun_code' in data else None,
                'fiveverst_code': data['fiveverst_code'] if 'fiveverst_code' in data else None,
                'runpark_code': data['runpark_code'] if 'runpark_code' in data else None
            }
    try:
        async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
            async with session.post(f'{INTERNAL_API_URL}/user', json=payload) as response:
                resp = await response.json()
                if response.ok:
                    await state.finish()
                    await message.answer(t(language_code(message), 'successful_registration'))
                    await message.answer(
                        t(language_code(message), 'subscription_suggestion'),
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    kbd = await kb.main(message)
                    await message.answer(t(language_code(message), 'home_event_suggestion'), reply_markup=kbd)
                else:
                    if 'user' in resp['errors']:
                        await message.answer('Ошибки в данных пользователя: ' + ', '.join(resp['errors']['user']))
                    if 'athlete' in resp['errors']:
                        await message.answer('Ошибки в данных участника: ' + ', '.join(resp['errors']['athlete']))
                    await message.answer(t(language_code(message), 'something_wrong'))
    except Exception:
        await message.answer(t(language_code(message), 'something_wrong'))
    finally:
        await message.delete()


@dp.message_handler(state=helpers.UserStates.CONFIRM, regexp=CANCEL_REGEXP)
async def cancel_registration(message: types.Message, state: FSMContext):
    await state.finish()
    kbd = await kb.main(message)
    await message.reply(t(language_code(message), 'request_cancelled'), reply_markup=kbd)


@dp.message_handler(state=helpers.HomeEventStates.SELECT_COUNTRY, regexp=r'\A\d+\Z')
async def process_select_country(message: types.Message, state: FSMContext):
    country_id = int(message.text)
    country_service = container.resolve(CountryService)
    country = await country_service.find_country_by_id(country_id)

    if not country:
        return await message.answer('Введён некорректный номер страны. Попробуйте ещё раз. Либо /reset для отмены')

    await state.update_data(country_id=country_id)

    event_service = container.resolve(EventService)
    events_list = await event_service.find_events_by_country(country_id)

    lang = language_code(message)
    localized_country_name = country_name(lang, country['code'])

    if not events_list:
        await state.finish()
        return await message.answer(f'В стране "{localized_country_name}" нет доступных мероприятий.')

    message_text = f'Выберите мероприятие в стране *{localized_country_name}*:\n\n'
    for event in events_list:
        message_text += f'*{event["id"]}* - {event["name"]}\n'

    await message.answer(message_text, parse_mode='Markdown')
    await helpers.HomeEventStates.next()


@dp.message_handler(state=helpers.HomeEventStates.SELECT_COUNTRY)
async def process_incorrect_country_id(message: types.Message):
    await message.answer('Введите число из приведённого выше списка стран. Либо /reset для отмены')


@dp.message_handler(state=helpers.HomeEventStates.INPUT_EVENT_ID, regexp=r'\A\d+\Z')
async def process_input_event_id(message: types.Message, state: FSMContext):
    event_id = int(message.text)
    event_service = container.resolve(EventService)
    event = await event_service.find_event_by_id(event_id)
    if not event:
        return await message.answer('Введён некорректный номер. Попробуйте ещё раз. Либо /reset для отмены')

    result = await helpers.update_home_event(message.from_user.id, event_id)
    if not result:
        return await message.answer('Произошла ошибка при установке домашнего забега. Попробуйте ещё раз.')

    answer = 'Домашний забег установлен.'
    link = await event_service.find_telegram_channel(event_id)
    if link:
        answer += ' ' + home_event_notice.format(link)

    await message.answer(answer, parse_mode='Markdown', disable_web_page_preview=True)
    await state.finish()


# Повторный запрос кода локации
@dp.message_handler(state=helpers.HomeEventStates.INPUT_EVENT_ID)
async def process_incorrect_input_club_id(message: types.Message):
    await message.answer('Введите число из приведённого выше списка. Либо /reset для отмены')


@dp.message_handler(state=helpers.ClubStates.INPUT_NAME)
async def process_club_name(message: types.Message, state: FSMContext):
    if len(message.text) < 2:
        return await message.answer('Введите название клуба немного точнее')

    club_service = container.resolve(ClubService)
    club = await club_service.find_club_by_name(message.text)
    if not club:
        return await message.answer(t(language_code(message), 'club_not_found'))

    await state.update_data(club_id=club['id'], club_name=club['name'])
    await helpers.ClubStates.next()

    await message.answer(
        f'Найден клуб [{club["name"]}](https://s95.ru/clubs/{club["id"]}). Установить?',
        reply_markup=kb.confirm_set_club,
        parse_mode='Markdown'
    )
