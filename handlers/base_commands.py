from aiogram import types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_service = container.resolve(UserService)
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    lang = language_code(message)
    
    kbd = await kb.main(message)
    
    if user:
        # Персонализированное приветствие для зарегистрированных пользователей
        name = message.from_user.first_name or 'друг'
        welcome_text = t(lang, 'welcome_back').format(name=name)
    else:
        welcome_text = t(lang, 'start_message')
    
    await message.answer(
        welcome_text,
        reply_markup=kbd,
        disable_notification=True,
        parse_mode='Markdown'
    )


@dp.message(F.text.regexp(REGEXP_HELP))
@dp.message(Command('help'))
async def commands(message: types.Message):
    await helpers.delete_message(message)
    lang = language_code(message)
    
    # Создаём интерактивную справку с inline-кнопками
    help_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📱 QR-код', callback_data='help_qr'),
         InlineKeyboardButton(text='📊 Статистика', callback_data='help_stats')],
        [InlineKeyboardButton(text='⚙️ Настройки', callback_data='help_settings'),
         InlineKeyboardButton(text='❓ Общая справка', callback_data='help_general')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='help_back')]
    ])
    
    await message.answer(
        t(lang, 'help_interactive'),
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=help_kbd
    )


@dp.message(F.text.regexp(REGEXP_REGISTRATION))
@dp.message(Command('register'))
async def process_command_settings(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)
    athlete_service = container.resolve(AthleteService)

    # Find user by Telegram ID
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    lang = language_code(message)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(lang, 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    # Find athlete by user ID
    athlete = await athlete_service.find_athlete_by_user_id(user['id'])
    if not athlete:
        return await message.answer(t(lang, 'user_without_athlete'))

    await message.answer(t(language_code(message), 'athlete_already_registered').format(athlete['id']))


@dp.message(F.text.regexp(REGEXP_QR))
@dp.message(Command('qrcode'))
async def process_command_qrcode(message: types.Message):
    await helpers.delete_message(message)
    await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatAction.UPLOAD_PHOTO)

    # Get services from container
    user_service = container.resolve(UserService)
    athlete_service = container.resolve(AthleteService)

    telegram_id = message.from_user.id
    user = await user_service.find_user_by_telegram_id(telegram_id)
    lang = language_code(message)
    agreement_kbd = await kb.inline_agreement(message)

    if not user:
        return await message.answer(
            t(lang, 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    athlete = await athlete_service.find_athlete_by_user_id(user['id'])
    if not athlete:
        return await message.answer(t(lang, 'user_without_athlete'))

    code = athlete_service.get_athlete_code(athlete)
    qr_info = t(lang, 'qr_code_info').format(name=athlete["name"], code=code)
    
    with qrcode.generate(code) as pic:
        await bot.send_photo(
            message.chat.id,
            pic,
            caption=qr_info,
            reply_markup=await kb.main(message),
            disable_notification=True,
            parse_mode='Markdown'
        )


@dp.message(F.text.regexp(r'📊 (Статистика|Statistics)'))
@dp.message(Command('statistics'))
async def process_command_statistics(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)

    # Check if user exists
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    lang = language_code(message)
    
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(lang, 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )

    stats_text = t(lang, 'statistics_dashboard')
    await message.answer(stats_text, reply_markup=kb.inline_personal(lang), parse_mode='Markdown')


@dp.message(Command('club'))
async def process_command_club(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    athlete_service = container.resolve(AthleteService)

    # Find athlete with club information
    club = await athlete_service.find_athlete_with_club(message.from_user.id)
    lang = language_code(message)
    agreement_kbd = await kb.inline_agreement(message)

    if not club:
        return await message.answer(
            t(lang, 'confirm_registration'),
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


@dp.message(Command('home'))
async def process_command_home(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    athlete_service = container.resolve(AthleteService)

    # Find athlete with home event information
    event = await athlete_service.find_athlete_with_home_event(message.from_user.id)
    lang = language_code(message)
    agreement_kbd = await kb.inline_agreement(message)

    if not event:
        return await message.answer(
            t(lang, 'confirm_registration'),
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


@dp.message(Command('phone'))
async def process_command_phone(message: types.Message):
    await helpers.delete_message(message)

    # Get services from container
    user_service = container.resolve(UserService)
    lang = language_code(message)

    # Find user by Telegram ID
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(lang, 'confirm_registration'),
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


@dp.message(F.contact)
async def process_contact(message: types.Message):
    if message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number
        if await helpers.update_user_phone(message.from_user.id, phone):
            await message.answer(
                t(language_code(message), 'phone_received').format(phone),
                reply_markup=await kb.main(message)
            )
        else:
            await message.answer(t(language_code(message), 'phone_save_error'), reply_markup=await kb.main(message))
    else:
        await message.answer(t(language_code(message), 'wrong_contact'), reply_markup=await kb.main(message))


@dp.message(lambda message: message.text == t(message.from_user.language_code, 'btn_cancel'))
async def process_cancel_phone(message: types.Message):
    await message.answer(
        t(language_code(message), 'request_cancelled'),
        reply_markup=await kb.main(message)
    )


@dp.message(F.text.regexp(r'🔗 (Войти на сайт|Login)'))
@dp.message(Command('login'))
async def process_command_login(message: types.Message, state: FSMContext):
    await helpers.delete_message(message)
    user_service = container.resolve(UserService)
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    lang = language_code(message)
    
    if not user:
        return await message.answer(
            t(lang, 'confirm_registration'),
            reply_markup=await kb.inline_agreement(message),
            parse_mode='Markdown'
        )

    await state.set_state(helpers.LoginStates.SELECT_DOMAIN)
    await state.update_data(user_id=user['id'])

    await message.answer(
        t(lang, 'select_domain'),
        reply_markup=kb.inline_select_domain(lang)
    )
