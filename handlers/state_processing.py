import aiohttp
import re
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from config import INTERNAL_API_URL
from random import randint

import keyboards as kb

from app import dp, language_code, container
from handlers import helpers
from s95.athlete_code import AthleteCode
from services.user_service import UserService
from services.athlete_service import AthleteService
from services.club_service import ClubService
from services.event_service import EventService
from utils import mailer
from utils.content import t, home_event_notice


PROCEED_CREATION_REGEXP = '(Всё верно, создать|Okay, proceed|Ok, nastavi)'
LINK_ATHLETE_REGEXP = '(Это я, привязать|Yes, it is me|Da, to sam ja)'
GENDERS_LIST = ['мужской', 'женский', 'male', 'female', 'muški', 'ženski']
MALE_LIST = ['мужской', 'male', 'muški']


@dp.message_handler(state=helpers.UserStates.SEARCH_ATHLETE_CODE)
async def process_user_enter_parkrun_code(message: types.Message, state: FSMContext):
    athlete_code = AthleteCode(message.text)
    if not athlete_code.is_valid:
        return await message.reply(t(language_code(message), 'input_athletes_id'))

    # Get services from container
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


# Просим Почту сразу
@dp.message_handler(state=helpers.UserStates.SAVE_WITH_PARKRUN_CODE, regexp=LINK_ATHLETE_REGEXP)
async def process_save_with_parkrun_code(message: types.Message):
    await helpers.UserStates.EMAIL.set()
    await message.reply(t(language_code(message), 'ask_email'), reply_markup=types.ReplyKeyboardRemove())


# Запрашиваем Фамилию
@dp.message_handler(state=helpers.UserStates.SAVE_WITH_PARKRUN_CODE, regexp=PROCEED_CREATION_REGEXP)
async def process_ask_athlete_last_name(message: types.Message):
    await helpers.UserStates.next()
    await message.answer(t(language_code(message), 'input_lastname'), reply_markup=types.ReplyKeyboardRemove())


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
    await message.answer(t(language_code(message), 'input_lastname_again'), reply_markup=types.ReplyKeyboardRemove())


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
# Просим Почту
@dp.message_handler(state=helpers.UserStates.GENDER)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(male=(message.text.strip().lower() in MALE_LIST))
    await helpers.UserStates.next()
    await message.answer(t(language_code(message), 'ask_email'), reply_markup=types.ReplyKeyboardRemove())


# Почту для подтверждения
@dp.message_handler(
    state=helpers.UserStates.EMAIL,
    regexp=r'\A[a-zA-Z0-9.!#$%&*+/=?^_{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\Z'
)
async def process_get_email(message: types.Message, state: FSMContext):
    email = message.text.lower()

    # Get services from container
    user_service = container.resolve(UserService)
    athlete_service = container.resolve(AthleteService)

    # Check if user with this email exists
    user = await user_service.find_user_by_email(email)
    if user:
        # Check if user already has an athlete linked
        athlete = await athlete_service.find_athlete_by_user_id(user['id'])
        if athlete:
            await state.finish()
            # TODO: Log this situation
            return await message.reply(t(language_code(message), 'athlete_already_linked'))

        # If no athlete is linked, proceed with linking
        await state.update_data(user_id=user['id'])
        await message.answer(t(language_code(message), 'user_exists_needs_linking'))

    # Proceed to next state
    await helpers.UserStates.next()

    # Set up email verification
    async with state.proxy() as data:
        data['email'] = email
        data['attempt'] = 0
        data['sent_at'] = int(time.time())
        data['pin'] = randint(100, 999)
        lang = message.from_user.language_code
        confirmation_mailer = mailer.EmailConfirmation(data['pin'], lang)
        confirmation_mailer.send(email, f'{data["first_name"]} {data["last_name"]}')

    await message.reply(t(language_code(message), 'input_pin_code'))


@dp.message_handler(state=helpers.UserStates.EMAIL)
async def process_repeat_email(message: types.Message):
    await message.reply(t(language_code(message), 'incorrect_pin_code'))


@dp.message_handler(state=helpers.UserStates.VALIDATE_EMAIL)
async def process_email_validation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data.get('sent_at') or data['sent_at'] + 30 * 60 < time.time() or data.get('attempt', 3) >= 3:
            await helpers.UserStates.previous()
            return await message.reply(t(language_code(message), 'pin_code_expired'))
        data['attempt'] += 1
        if not message.text.isdecimal() or data['pin'] != int(message.text.strip()):
            return await message.reply(
                t(language_code(message), 'pincode_input_attempts').format(attempt=data["attempt"])
            )
        if 'user_id' not in data:
            await helpers.UserStates.next()
            return await message.answer(
                t(language_code(message), 'input_password') + t(language_code(message), 'password_requirements')
            )
        payload = {
            'user_id': data['user_id'],
            'user': {
                'telegram_id': message.from_user.id,
                'telegram_user': message.from_user.username
            }
        }
        # привязать участника к юзеру либо создать нового
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
                async with session.put(f'{INTERNAL_API_URL}/user', json=payload) as response:
                    resp = await response.json()
                    if resp.ok:
                        await state.finish()
                        kbd = await kb.main(message)
                        await message.answer(
                            t(language_code(message), 'user_linked_successfully'),
                            reply_markup=kbd
                        )
                        await message.answer(
                            t(language_code(message), 'subscription_suggestion'),
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
                    else:
                        if 'user' in resp['errors']:
                            await message.answer('Ошибки в данных пользователя: ' + ', '.join(resp['errors']['user']))
                        if 'athlete' in resp['errors']:
                            await message.answer('Ошибки в данных участника: ' + ', '.join(resp['errors']['athlete']))
                        await message.answer(t(language_code(message), 'try_pin_code'))
        except Exception:
            await message.answer(t(language_code(message), 'try_pin_code'))
        finally:
            await message.delete()


@dp.message_handler(state=helpers.UserStates.PASSWORD, regexp=r'\A(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}\Z')
async def process_password_validation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        payload = {
            'user': {
                'email': data['email'],
                'password': message.text,
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
                    kbd = await kb.main(message)
                    await message.answer(t(language_code(message), 'successful_registration'), reply_markup=kbd)
                    await message.answer(
                        t(language_code(message), 'subscription_suggestion'),
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                else:
                    if 'user' in resp['errors']:
                        await message.answer('Ошибки в данных пользователя: ' + ', '.join(resp['errors']['user']))
                    if 'athlete' in resp['errors']:
                        await message.answer('Ошибки в данных участника: ' + ', '.join(resp['errors']['athlete']))
                    await message.answer(t(language_code(message), 'try_password'))
    except Exception:
        await message.answer(t(language_code(message), 'try_password'))
    finally:
        await message.delete()
        await message.answer(t(language_code(message), 'password_erased'))


@dp.message_handler(state=helpers.UserStates.PASSWORD)
async def process_invalid_password(message: types.Message):
    await message.answer(
        t(language_code(message), 'invalid_password') + t(language_code(message), 'password_requirements')
    )
    await helpers.delete_message(message)
    await message.answer(t(language_code(message), 'password_erased_again'))


@dp.message_handler(state=helpers.HomeEventStates.INPUT_EVENT_ID, regexp=r'\A\d+\Z')
async def process_input_event_id(message: types.Message, state: FSMContext):
    event_id = int(message.text)

    # Get services from container
    event_service = container.resolve(EventService)

    # Check if event exists
    event = await event_service.find_event_by_id(event_id)
    if not event:
        return await message.answer('Введён некорректный номер. Попробуйте ещё раз. Либо /reset для отмены')

    # Update home event
    result = await helpers.update_home_event(message.from_user.id, event_id)
    if not result:
        return await message.answer('Произошла ошибка при установке домашнего забега. Попробуйте ещё раз.')

    # Get Telegram channel link
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
    if len(message.text) < 3:
        return await message.answer('Введите название клуба немного точнее')

    # Get services from container
    club_service = container.resolve(ClubService)

    # Find club by name
    club = await club_service.find_club_by_name(message.text)
    if not club:
        return await message.answer(t(language_code(message), 'club_not_found'))

    # Update state data
    await state.update_data(club_id=club['id'], club_name=club['name'])
    await helpers.ClubStates.next()

    # Show confirmation message
    await message.answer(
        f'Найден клуб [{club["name"]}](https://s95.ru/clubs/{club["id"]}). Установить?',
        reply_markup=kb.confirm_set_club,
        parse_mode='Markdown'
    )
