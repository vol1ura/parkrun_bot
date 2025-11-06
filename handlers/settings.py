from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import keyboards as kb

from app import dp, bot, language_code, container
from handlers import helpers
from services.user_service import UserService
from services.athlete_service import AthleteService
from utils.content import t


@dp.message(F.text.regexp(r'⚙️ (Настройки|Settings)'))
async def process_settings_menu(message: types.Message):
    await helpers.delete_message(message)
    lang = language_code(message)
    user_service = container.resolve(UserService)
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    
    if not user:
        agreement_kbd = await kb.inline_agreement(message)
        return await message.answer(
            t(lang, 'confirm_registration'),
            reply_markup=agreement_kbd,
            parse_mode='Markdown'
        )
    
    athlete_service = container.resolve(AthleteService)
    athlete = await athlete_service.find_athlete_by_user_id(user['id'])
    
    settings_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏠 Домашний забег', callback_data='settings_home'),
         InlineKeyboardButton(text='👥 Клуб', callback_data='settings_club')],
        [InlineKeyboardButton(text='📱 Телефон', callback_data='settings_phone')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='settings_back')]
    ])
    
    await message.answer(
        t(lang, 'settings_menu'),
        reply_markup=settings_kbd,
        parse_mode='Markdown'
    )


@dp.message(Command('reset'), StateFilter('*'))
async def process_command_reset(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.reply(t(language_code(message), 'request_cancelled'), reply_markup=await kb.main(message))


@dp.message(Command('continue'))
async def process_command_continue(message: types.Message, state: FSMContext):
    """Продолжение прерванного процесса"""
    current_state = await state.get_state()
    lang = language_code(message)
    
    if not current_state:
        await message.answer(
            'ℹ️ У вас нет активных процессов для продолжения.',
            reply_markup=await kb.main(message)
        )
        return
    
    # Определяем, какой процесс был прерван
    state_str = str(current_state)
    
    if 'UserStates' in state_str:
        # Процесс регистрации
        data = await state.get_data()
        if 'last_name' in data:
            if 'first_name' not in data:
                await message.answer(t(lang, 'input_firstname'), parse_mode='Markdown')
            elif 'male' not in data:
                gender_kbd = await kb.select_gender(message)
                await message.answer(t(lang, 'input_gender'), reply_markup=gender_kbd, parse_mode='Markdown')
            else:
                confirm_kbd = await kb.confirm_registration(message)
                await message.answer(
                    t(lang, 'confirm_personal_data').format(
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        gender=t(lang, 'btn_male' if data.get('male') else 'btn_female')
                    ),
                    parse_mode='Markdown',
                    reply_markup=confirm_kbd
                )
        else:
            await message.answer(t(lang, 'input_lastname'), parse_mode='Markdown')
    elif 'ClubStates' in state_str:
        await message.answer(
            'Введите название клуба или /reset для отмены',
            parse_mode='Markdown'
        )
    elif 'HomeEventStates' in state_str:
        data = await state.get_data()
        if 'country_id' not in data:
            await message.answer('Введите номер страны из списка выше или /reset для отмены')
        else:
            await message.answer('Введите номер мероприятия из списка выше или /reset для отмены')
    else:
        await message.answer(
            t(lang, 'continue_registration'),
            reply_markup=await kb.main(message),
            parse_mode='Markdown'
        )
