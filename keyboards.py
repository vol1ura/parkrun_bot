from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from app import container
from services.user_service import UserService
from utils.content import t


async def main(message) -> ReplyKeyboardMarkup:
    """MAIN bot keyboard layout"""
    user_service = container.resolve(UserService)
    user = await user_service.find_user_by_telegram_id(message.from_user.id)
    lang = message.from_user.language_code
    btn_title = t(lang, 'btn_qr_code') if user else t(lang, 'btn_registration')

    kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=btn_title), KeyboardButton(text=t(lang, 'btn_help'))]
        ],
        resize_keyboard=True
    )
    return kbd


# STATISTICS inline keyboard layout
# inline_stat = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Личные результаты', callback_data='personal_results')],
#     [InlineKeyboardButton(text='Сравнение результатов', callback_data='compare_results')],
#     [InlineKeyboardButton(text='Последний паркран', switch_inline_query_current_chat='latestresults')],
#     [InlineKeyboardButton(text='Одноклубники', switch_inline_query_current_chat='teammates')],
#     [InlineKeyboardButton(text='Рекорды', switch_inline_query_current_chat='records'),
#      InlineKeyboardButton(text='Рекордсмены', callback_data='most_records_parkruns')]
# ])


# CLUB ask to change
change_club = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сменить', callback_data='ask_club'),
     InlineKeyboardButton(text='Удалить', callback_data='remove_club')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_action')]
])

# CLUB ask to set
set_club = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Установить', callback_data='ask_club')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_action')]
])

confirm_set_club = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='set_club'),
     InlineKeyboardButton(text='Нет', callback_data='cancel_action')]
])

# HOME EVENT ask to change
change_home_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сменить', callback_data='ask_home_event'),
     InlineKeyboardButton(text='Удалить', callback_data='remove_home_event')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_action')]
])

# HOME EVENT ask to set
set_home_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Установить', callback_data='ask_home_event')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel_action')]
])

# PERSONAL RESULTS inline keyboard layout
inline_personal = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Последний забег', callback_data='last_activity_diagram'),
     InlineKeyboardButton(text='История', callback_data='personal_history')],
    [InlineKeyboardButton(text='Личники', callback_data='personal_bests'),
     InlineKeyboardButton(text='График 10 рез.', callback_data='personal_last')]
    # [InlineKeyboardButton(text='S95-туризм', callback_data='personal_tourism')]
])


# COMPARATION of personal results
# inline_compare = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Баттл-таблица', callback_data='battle_table')],
#     [InlineKeyboardButton(text='Баттл-диаграмма', callback_data='battle_diagram'),
#      InlineKeyboardButton(text='Файл Excel', callback_data='excel_table')],
#     [InlineKeyboardButton(text='Scatter', callback_data='battle_scatter')]
# ])

# ATHLETE REGISTRATION
async def accept_athlete(message) -> ReplyKeyboardMarkup:
    lang = message.from_user.language_code
    accept_athlete_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, 'btn_link')), KeyboardButton(text=t(lang, 'btn_no_link'))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return accept_athlete_kbd


# Confirm REGISTRATION
async def confirm_registration(message) -> ReplyKeyboardMarkup:
    lang = message.from_user.language_code
    confirm_registration_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, 'btn_create')), KeyboardButton(text=t(lang, 'btn_cancel'))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return confirm_registration_kbd


async def ask_for_new_athlete(message) -> ReplyKeyboardMarkup:
    lang = message.from_user.language_code
    ask_for_new_athlete_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, 'btn_create')), KeyboardButton(text=t(lang, 'btn_cancel'))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return ask_for_new_athlete_kbd


async def select_gender(message) -> ReplyKeyboardMarkup:
    lang = message.from_user.language_code
    select_gender_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, 'btn_male')), KeyboardButton(text=t(lang, 'btn_female'))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return select_gender_kbd


async def inline_agreement(message) -> InlineKeyboardMarkup:
    lang = message.from_user.language_code
    inline_agreement_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'btn_agree'), callback_data='start_registration'),
         InlineKeyboardButton(text=t(lang, 'btn_disagree'), callback_data='cancel_registration')]
    ])
    return inline_agreement_kbd


async def inline_find_athlete_by_id(message) -> InlineKeyboardMarkup:
    lang = message.from_user.language_code
    inline_find_athlete_by_id_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'btn_new_runner'), callback_data='create_new_athlete'),
         InlineKeyboardButton(text=t(lang, 'btn_cancel'), callback_data='cancel_registration')],
        [InlineKeyboardButton(text=t(lang, 'btn_input_ID'), callback_data='athlete_code_search'),
         InlineKeyboardButton(text=t(lang, 'btn_dont_remember_ID'), callback_data='help_to_find_id')]
    ])
    return inline_find_athlete_by_id_kbd


async def inline_open_s95(message) -> InlineKeyboardMarkup:
    lang = message.from_user.language_code
    inline_open_s95_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'btn_open_website'), url=t(lang, 'link_to_s95_website'))],
        [InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data='start_registration')]
    ])
    return inline_open_s95_kbd


async def phone_keyboard(message) -> ReplyKeyboardMarkup:
    phone_kbd = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(message.from_user.language_code, 'btn_share_phone'), request_contact=True)],
            [KeyboardButton(text=t(message.from_user.language_code, 'btn_cancel'))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return phone_kbd
