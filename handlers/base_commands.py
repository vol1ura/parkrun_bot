from aiogram import types
from config import VERSION

import keyboards as kb

from app import dp, bot, language_code, container
from handlers import helpers
from services.user_service import UserService
from services.athlete_service import AthleteService
from utils.content import t, about_club, about_home_event
from utils import qrcode

REGEXP_QR = 'ℹ️ (QR-код|QR-code|QR-kod)'
REGEXP_REGISTRATION = '⚙️ (регистрация|registration|registracija)'
REGEXP_HELP = '❓ (справка|help|pomoć)'


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kbd = await kb.main(message)
    await message.answer(
        t(language_code(message), 'start_message'),
        reply_markup=kbd,
        disable_notification=True
    )


@dp.message_handler(regexp=REGEXP_HELP)
@dp.message_handler(commands=['help'])
async def commands(message: types.Message):
    await helpers.delete_message(message)
    await message.answer(
        t(language_code(message), 'help_message').format(VERSION),
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=await kb.main(message)
    )


@dp.message_handler(regexp=REGEXP_REGISTRATION)
@dp.message_handler(commands=['register'])
async def process_command_settings(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)
    athlete_service = container.resolve(AthleteService)

    # Find user by Telegram ID
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    # Find athlete by user ID
    athlete = await athlete_service.find_athlete_by_user_id(user['id'])
    if not athlete:
        return await message.answer(t(language_code(message), 'user_without_athlete'))

    await message.answer(t(language_code(message), 'athlete_already_registered').format(athlete['id']))


@dp.message_handler(regexp=REGEXP_QR)
@dp.message_handler(commands=['qrcode'])
async def process_command_qrcode(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)
    athlete_service = container.resolve(AthleteService)

    telegram_id = message.from_user.id
    user = await user_service.find_user_by_telegram_id(telegram_id)
    agreement_kbd = await kb.inline_agreement(message)

    if not user:
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    athlete = await athlete_service.find_athlete_by_user_id(user['id'])
    if not athlete:
        return await message.answer(t(language_code(message), 'user_without_athlete'))

    code = athlete_service.get_athlete_code(athlete)
    with qrcode.generate(code) as pic:
        await bot.send_photo(message.chat.id, pic, caption=f'{athlete["name"]} (A{code})', reply_markup=await kb.main(message))


@dp.message_handler(commands=['statistics'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)

    # Check if user exists
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_personal)


@dp.message_handler(commands=['club'])
@dp.throttled(rate=1)
async def process_command_club(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    athlete_service = container.resolve(AthleteService)

    # Find athlete with club information
    club = await athlete_service.find_athlete_with_club(message.from_user.id)
    agreement_kbd = await kb.inline_agreement(message)

    if not club:
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    if not club['club_id']:
        return await message.answer(
            t(language_code(message), 'setup_running_club'),
            reply_markup=kb.set_club
        )

    await message.answer(
        about_club.format(club['club_name']),
        reply_markup=kb.change_club,
        parse_mode='Markdown'
    )


@dp.message_handler(commands=['home'])
@dp.throttled(rate=1)
async def process_command_home(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    athlete_service = container.resolve(AthleteService)

    # Find athlete with home event information
    event = await athlete_service.find_athlete_with_home_event(message.from_user.id)
    agreement_kbd = await kb.inline_agreement(message)

    if not event:
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    if not event['event_id']:
        return await message.answer(
            t(language_code(message), 'setup_home_run'),
            reply_markup=kb.set_home_event
        )

    await message.answer(
        about_home_event.format(event['event_name']),
        reply_markup=kb.change_home_event,
        parse_mode='Markdown'
    )


@dp.message_handler(commands=['phone'])
async def process_command_phone(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)

    # Find user by Telegram ID
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    if user.get('phone'):
        return await message.answer(
            t(language_code(message), 'phone_already_set').format(user['phone']),
            reply_markup=await kb.main(message)
        )

    phone_kbd = await kb.phone_keyboard(message)
    await message.answer(
        t(language_code(message), 'request_phone'),
        disable_web_page_preview=True,
        reply_markup=phone_kbd,
        parse_mode='Markdown'
    )


@dp.message_handler(content_types=['contact'])
async def process_contact(message: types.Message):
    if message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number
        if await helpers.update_user_phone(message.from_user.id, phone):
            await message.answer(
                t(language_code(message), 'phone_received').format(phone),
                reply_markup=await kb.main(message)
            )
        else:
            await message.answer(
                t(language_code(message), 'phone_save_error'),
                reply_markup=await kb.main(message)
            )
    else:
        await message.answer(
            t(language_code(message), 'wrong_contact'),
            reply_markup=await kb.main(message)
        )


@dp.message_handler(lambda message: message.text == t(message.from_user.language_code, 'btn_cancel'))
async def process_cancel_phone(message: types.Message):
    await message.answer(
        t(language_code(message), 'request_cancelled'),
        reply_markup=await kb.main(message)
    )


@dp.message_handler(commands=['login'])
async def process_command_login(message: types.Message):
    # Get services from container
    user_service = container.resolve(UserService)

    # Find user by Telegram ID
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(t(language_code(message), 'login_not_registered'), reply_markup=agreement_kbd)

    auth_link = await helpers.get_auth_link(user['id'])
    if not auth_link:
        return await message.answer(t(language_code(message), 'login_link_error'), reply_markup=await kb.main(message))

    await message.answer(
        t(language_code(message), 'your_login_link').format(link=auth_link),
        reply_markup=await kb.main(message),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
