from aiogram import types
from config import VERSION

import keyboards as kb

from app import dp, bot, language_code
from handlers import helpers
from utils import content
from utils import qrcode


@dp.message_handler(commands=['start'])
@dp.throttled(rate=5)
async def send_welcome(message: types.Message):
    kbd = await kb.main(message)
    await message.answer(content.t(language_code(message), 'start_message'),
        reply_markup=kbd,
        disable_notification=True
    )


@dp.message_handler(regexp = '❓ справка')
@dp.message_handler(regexp = '❓ help')
@dp.message_handler(commands=['help'])
@dp.throttled(rate=3)
async def commands(message: types.Message):
    await helpers.delete_message(message)
    await message.answer(
        content.t(language_code(message), 'help_message').format(VERSION),
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=await kb.main(message)
    )


@dp.message_handler(regexp = '⚙️ регистрация')
@dp.message_handler(regexp = '⚙️ registration')
@dp.message_handler(commands=['register'])
@dp.throttled(rate=2)
async def process_command_settings(message: types.Message):
    await helpers.delete_message(message)
    telegram_id = message.from_user.id
    user = await helpers.find_user_by('telegram_id', telegram_id)
    agreement_kbd = await kb.inline_agreement(message)
    if not user:
        return await message.answer(
            content.t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )
    athlete = await helpers.find_athlete_by('user_id', user['id'])
    if not athlete:
        return await message.answer(
            content.t(language_code(message), 'user_without_athlete')
        )
    await message.answer(
        content.t(language_code(message), 'athlete_already_registered')
    )


@dp.message_handler(regexp='ℹ️ QR-код')
@dp.message_handler(regexp='ℹ️ QR-code')
@dp.message_handler(commands=['qrcode'])
@dp.throttled(rate=3)
async def process_command_qrcode(message: types.Message):
    await helpers.delete_message(message)
    telegram_id = message.from_user.id
    user = await helpers.find_user_by('telegram_id', telegram_id)
    agreement_kbd = await kb.inline_agreement(message)
    if not user:
        return await message.answer(
            content.t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )
    athlete = await helpers.find_athlete_by('user_id', user['id'])
    if not athlete:
        return await message.answer(
            content.t(language_code(message), 'user_without_athlete')
        )
    code = helpers.athlete_code(athlete)
    with qrcode.generate(code) as pic:
        await bot.send_photo(message.chat.id, pic, caption=f'{athlete["name"]} (A{code})')


@dp.message_handler(commands=['statistics'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await helpers.delete_message(message)
    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_personal)


# @dp.message_handler(regexp='📋 разное')
# @dp.message_handler(commands=['info'])
# @dp.throttled(rate=2)
# async def process_command_info(message: types.Message):
#     await helpers.delete_message(message)
#     await message.answer('Кое-что ещё:', reply_markup=kb.inline_info)


@dp.message_handler(commands=['club'])
@dp.throttled(rate=2)
async def process_command_club(message: types.Message):
    await helpers.delete_message(message)
    club = await helpers.find_club(message.from_user.id)
    agreement_kbd = await kb.inline_agreement(message)
    if not club:
        return await message.answer(
            content.t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )
    if not club['club_id']:
        return await message.answer(
            content.t(language_code(message), 'setup_running_club'),
            reply_markup=kb.set_club
        )
    await message.answer(
        content.about_club.format(club['club_name']),
        reply_markup=kb.change_club,
        parse_mode='Markdown'
    )


@dp.message_handler(commands=['home'])
@dp.throttled(rate=2)
async def process_command_home(message: types.Message):
    await helpers.delete_message(message)
    event = await helpers.find_home_event(message.from_user.id)
    agreement_kbd = await kb.inline_agreement(message)
    if not event:
        return await message.answer(
            content.t(language_code(message), 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )
    if not event['event_id']:
        return await message.answer(
            content.t(language_code(message), 'setup_home_run'),
            reply_markup=kb.set_home_event
        )
    await message.answer(
        content.about_home_event.format(event['event_name']),
        reply_markup=kb.change_home_event,
        parse_mode='Markdown'
    )
