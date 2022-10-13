import aiohttp
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from config import INTERNAL_API_KEY, INTERNAL_API_URL
from random import randint

import keyboards as kb

from app import dp, bot
from handlers.helpers import UserStates, find_athlete_by, find_user_by, find_user_by_email
from s95.athlete_code import AthleteCode
from utils import redis, content, mailer


@dp.message_handler(lambda message: not AthleteCode(message.text).is_valid, state=UserStates.SEARCH_ATHLETE_CODE)
async def process_age_invalid(message: types.Message):
    return await message.reply("Введите свой parkrun ID (только цифры, без буквы А в начале). Либо /reset для отмены.")


@dp.message_handler(state=UserStates.SEARCH_ATHLETE_CODE)
async def process_user_enter_parkrun_code(message: types.Message, state: FSMContext):
    await UserStates.next()
    athlete_code = AthleteCode(message.text)
    if athlete_code.key == 's95':
        await state.update_data(parkrun_code=None)
    else:
        await state.update_data(**{athlete_code.key: athlete_code.value})
    athlete = await find_athlete_by(athlete_code.key, athlete_code.value)
    if athlete:
        if athlete["user_id"]:
            await state.finish()
            return await message.answer('Участник с этим parkrun ID уже зарегистрирован и привязан.')
        async with state.proxy() as data:
            data['athlete_id'] = athlete['id']
            data['first_name'], data["last_name"] = athlete['name'].split(' ', 1)
        await message.answer(
            content.found_athlete_info.format(athlete_id=athlete['id'], name=athlete['name']),
            reply_markup=kb.accept_athlete,
            parse_mode='html'
        )
    else:
        await message.reply(content.athlete_code_check(athlete_code),
                            reply_markup=kb.ask_for_new_athlete, parse_mode="html", disable_web_page_preview=True)


# Просим Почту сразу
@dp.message_handler(state=UserStates.SAVE_WITH_PARKRUN_CODE, regexp="Это я, привязать")
async def process_save_with_parkrun_code(message: types.Message):
    await UserStates.EMAIL.set()
    await message.reply(content.ask_email, reply_markup=types.ReplyKeyboardRemove())


# Запрашиваем Фамилию
@dp.message_handler(state=UserStates.SAVE_WITH_PARKRUN_CODE, regexp="Всё верно, создать")
async def process_ask_athlete_last_name(message: types.Message):
    await UserStates.next()
    await message.answer("Введите свою фамилию", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=UserStates.SAVE_WITH_PARKRUN_CODE)
async def process_cancel_parkrun_code(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Запрос отменён. Попробуйте снова.", reply_markup=kb.main)


# Получаем Фамилию
# Запрашиваем Имя
@dp.message_handler(state=UserStates.ATHLETE_LAST_NAME, regexp=r'(?i)\A[a-zа-яё]{2,}(-[a-zа-яё]{2,})?\Z')
async def process_get_athlete_last_name(message: types.Message, state: FSMContext):
    await UserStates.next()
    await state.update_data(last_name=message.text)
    await message.answer("Введите своё имя")


@dp.message_handler(state=UserStates.ATHLETE_LAST_NAME)
async def process_repeat_last_name(message: types.Message):
    await message.answer('Введите свою фамилию. Допустимы только буквы и дефис.', reply_markup=types.ReplyKeyboardRemove())


# Сохраняем Имя
# Запрашиваем Пол
@dp.message_handler(state=UserStates.ATHLETE_FIRST_NAME, regexp=r'(?i)\A[a-zа-яё]{2,}\Z')
async def process_get_athlete_first_name(message: types.Message, state: FSMContext):
    await UserStates.next()
    await state.update_data(first_name=message.text)
    await message.answer('Укажите свой пол', reply_markup=kb.select_gender)


@dp.message_handler(state=UserStates.ATHLETE_FIRST_NAME)
async def process_repeat_first_name(message: types.Message):
    await message.answer('Введите своё имя. Допустимы только буквы.')


# Запрашиваем Пол ещё раз
@dp.message_handler(lambda message: message.text.strip().lower() not in ['мужской', 'женский'], state=UserStates.GENDER)
async def process_gender_invalid(message: types.Message):
    await message.reply(content.define_yourself_gender, reply_markup=kb.select_gender)


# Сохраняем Пол
# Просим Почту
@dp.message_handler(state=UserStates.GENDER)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(male=(message.text.strip().lower() == "мужской"))
    await UserStates.next()
    async with state.proxy() as data:
        print(data)
    await message.answer(content.ask_email, reply_markup=types.ReplyKeyboardRemove())


# Почту для подтверждения
@dp.message_handler(state=UserStates.EMAIL, regexp=r'\A[a-zA-Z0-9.!#$%&*+/=?^_{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\Z')
@dp.throttled(rate=15)
async def process_get_email(message: types.Message, state: FSMContext):
    email = message.text.lower()
    user = await find_user_by_email(email)
    if user:
        # проверить, что у юзера с этой почтой не привязан участник
        if await find_athlete_by('user_id', user['id']):
            await state.finish()
            # Залогировать эту ситуацию
            return await message.reply(content.athlete_already_linked)
        # Если участник не привязан, то делаем привязку
        await state.update_data(user_id=user['id'])
        await message.answer('Пользователь с таким адресом уже зарегистрирован. Теперь необходимо сделать привязку участника.')
    await UserStates.next()
    async with state.proxy() as data:
        data["email"] = email
        data["attempt"] = 0
        data["sent_at"] = int(time.time())
        data["pin"] = randint(100, 999)
        confirmation_mailer = mailer.EmailConfirmation(data['pin'])
        confirmation_mailer.send(email, f'{data["first_name"]} {data["last_name"]}')
    await message.reply(content.input_pin_code)


@dp.message_handler(state=UserStates.EMAIL)
async def process_repeat_email(message: types.Message):
    await message.reply("Введите Ваш e-mail. На него будет выслан проверочный код.")


@dp.message_handler(state=UserStates.VALIDATE_EMAIL)
@dp.throttled(rate=5)
async def process_email_validation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data["sent_at"] or data["sent_at"] + 30 * 60 < time.time() or data.get("attempt", 3) >= 3:
            await UserStates.previous()
            return await message.reply(content.pin_code_expired)
        data["attempt"] += 1
        if not message.text.isdigit() or data["pin"] != int(message.text.strip()):
            return await message.reply(f'Неверный код. Попробуйте ввести ещё раз. Это {data["attempt"]} попытка из 3.')
        if 'user_id' not in data:
            await UserStates.next()
            return await message.answer(content.input_password)

        # привязать участника к юзеру
        payload = {
            'user_id': data['user_id'],
            'user': {
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
                'fiveverst_code': data['fiveverst_code'] if 'fiveverst_code' in data else None
            }
        headers = {
            'Authorization': INTERNAL_API_KEY,
            'Accept': 'application/json'
        }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.put(f'{INTERNAL_API_URL}/user.json', json=payload) as resp:
                    data = await resp.json()
                    if resp.ok:
                        await state.finish()
                        await message.answer(data['message'], reply_markup=kb.main)
                    else:
                        if 'user' in data['errors']:
                            await message.answer('Ошибки в данных пользователя: ' + ', '.join(data['errors']['user']))
                        if 'athlete' in data['errors']:
                            await message.answer('Ошибки в данных участника: ' + ', '.join(data['errors']['athlete']))
                        await message.answer(content.try_pin_code)
        except Exception:
            await message.answer(content.try_pin_code)
        finally:
            await message.delete()


@dp.message_handler(state=UserStates.PASSWORD, regexp=r'\A(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\sa-zA-Z\d]).{6,}\Z')
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
                'fiveverst_code': data['fiveverst_code'] if 'fiveverst_code' in data else None
            }
    headers = {
        'Authorization': INTERNAL_API_KEY,
        'Accept': 'application/json'
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f'{INTERNAL_API_URL}/user.json', json=payload) as resp:
                data = await resp.json()
                if resp.ok:
                    await state.finish()
                    await message.answer(data['message'], reply_markup=kb.main)
                else:
                    if 'user' in data['errors']:
                        await message.answer('Ошибки в данных пользователя: ' + ', '.join(data['errors']['user']))
                    if 'athlete' in data['errors']:
                        await message.answer('Ошибки в данных участника: ' + ', '.join(data['errors']['athlete']))
                    await message.answer(content.try_password)
    except Exception:
        await message.answer(content.try_password)
    finally:
        await message.delete()
        await message.answer(content.password_erased)


@dp.message_handler(state=UserStates.PASSWORD)
async def process_invalid_password(message: types.Message):
    await message.answer(content.invalid_password)
    await message.answer(f'{content.password_erased} Придумайте пароль.')
    await message.delete()


@dp.message_handler(state=UserStates.COMPARE_ID)
async def process_user_enter_compare_id(message: types.Message, state: FSMContext):
    athlete_id = message.text.strip()
    athlete_name = await find_user_by('id', athlete_id)
    if athlete_name:
        await redis.set_value(str(message.from_user.id), compare_id=athlete_id)
        await bot.send_message(message.chat.id, f'*Участник*: {athlete_name}.\n'
                                                f'Данные сохранены.', parse_mode="Markdown")
        await state.finish()
    else:
        await bot.send_message(message.chat.id, "Не удалось найти участника с таким ID проверьте корректность ввода."
                                                "Введите свой ID снова, либо /reset для отмены запроса.")
