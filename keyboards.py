from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from handlers.helpers import find_user_by
from utils.content import t


async def main(message) -> ReplyKeyboardMarkup:
    """MAIN bot keyboard layout"""
    kbd = ReplyKeyboardMarkup(resize_keyboard=True)
    user = await find_user_by('telegram_id', message.from_user.id)
    lang = message.from_user.language_code
    btn_title = t(lang, 'btn_qr_code') if user else t(lang, 'btn_registration')
    btn2 = KeyboardButton(t(lang, 'btn_help'))
    btn1 = KeyboardButton(btn_title)
    kbd.add(btn1, btn2)
    return kbd


# STATISTICS inline keyboard layout
# inline_stat = InlineKeyboardMarkup(row_width=2)
# inline_stat.insert(InlineKeyboardButton('Личные результаты', callback_data='personal_results'))
# inline_stat.insert(InlineKeyboardButton('Сравнение результатов', callback_data='compare_results'))
# inline_stat.row(InlineKeyboardButton('Последний паркран', switch_inline_query_current_chat='latestresults'))

# inline_stat.row(InlineKeyboardButton('Одноклубники', switch_inline_query_current_chat='teammates'))
# inline_stat.insert(InlineKeyboardButton('Top10 клубов', callback_data='top_active_clubs'))

# inline_stat.insert(InlineKeyboardButton('Рекорды', switch_inline_query_current_chat='records'))
# inline_stat.insert(InlineKeyboardButton('Рекордсмены', callback_data='most_records_parkruns'))


# INFORMATION keyboard layout with additional information
# inline_info = InlineKeyboardMarkup(row_width=2)
# inline_info.insert(InlineKeyboardButton("Ближайшие старты", switch_inline_query_current_chat='events'))

# info_btn1 = InlineKeyboardButton("Посмотреть погоду", switch_inline_query_current_chat='weather')
# info_btn2 = InlineKeyboardButton("Загрязнение воздуха", switch_inline_query_current_chat='air')

# inline_info.row(info_btn1, info_btn2)

# CLUB ask to change
change_club = InlineKeyboardMarkup(row_width=2)
change_club.insert(InlineKeyboardButton('Сменить', callback_data='ask_club'))
change_club.insert(InlineKeyboardButton('Удалить', callback_data='remove_club'))
change_club.insert(InlineKeyboardButton('Отмена', callback_data='cancel_action'))

# CLUB ask to set
set_club = InlineKeyboardMarkup(row_width=2)
set_club.insert(InlineKeyboardButton('Установить', callback_data='ask_club'))
set_club.insert(InlineKeyboardButton('Отмена', callback_data='cancel_action'))

confirm_set_club = InlineKeyboardMarkup(row_width=2)
confirm_set_club.insert(InlineKeyboardButton('Да', callback_data='set_club'))
confirm_set_club.insert(InlineKeyboardButton('Нет', callback_data='cancel_action'))

# HOME EVENT ask to change
change_home_event = InlineKeyboardMarkup(row_width=2)
change_home_event.insert(InlineKeyboardButton('Сменить', callback_data='ask_home_event'))
change_home_event.insert(InlineKeyboardButton('Удалить', callback_data='remove_home_event'))
change_home_event.insert(InlineKeyboardButton('Отмена', callback_data='cancel_action'))

# HOME EVENT ask to set
set_home_event = InlineKeyboardMarkup(row_width=2)
set_home_event.insert(InlineKeyboardButton('Установить', callback_data='ask_home_event'))
set_home_event.insert(InlineKeyboardButton('Отмена', callback_data='cancel_action'))

# PERSONAL RESULTS inline keyboard layout
inline_personal = InlineKeyboardMarkup(row_width=2)
inline_personal.insert(InlineKeyboardButton('Последний забег', callback_data='last_activity_diagram'))
inline_personal.insert(InlineKeyboardButton('История', callback_data='personal_history'))
inline_personal.insert(InlineKeyboardButton('Личники', callback_data='personal_bests'))
# inline_personal.insert(InlineKeyboardButton('S95-туризм', callback_data='personal_tourism'))
inline_personal.insert(InlineKeyboardButton('График 10 рез.', callback_data='personal_last'))


# COMPARATION of personal results
# inline_compare = InlineKeyboardMarkup(row_width=2)
# inline_compare.add(InlineKeyboardButton('Баттл-таблица', callback_data='battle_table'))
# inline_compare.insert(InlineKeyboardButton('Баттл-диаграмма', callback_data='battle_diagram'))
# inline_compare.insert(InlineKeyboardButton('Файл Excel', callback_data='excel_table'))
# inline_compare.insert(InlineKeyboardButton('Scatter', callback_data='battle_scatter'))

# ATHLETE REGISTRATION
async def accept_athlete(message) -> ReplyKeyboardMarkup:
    accept_athlete_kbd = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    lang = message.from_user.language_code
    accept_athlete_kbd.add(t(lang, "btn_link"), t(lang, "btn_no_link"))
    return accept_athlete_kbd


async def ask_for_new_athlete(message) -> ReplyKeyboardMarkup:
    ask_for_new_athlete_kbd = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    lang = message.from_user.language_code
    ask_for_new_athlete_kbd.add(t(lang, "btn_create"), t(lang, "btn_cancel"))
    return ask_for_new_athlete_kbd


async def select_gender(message) -> ReplyKeyboardMarkup:
    select_gender_kbd = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, selective=True)
    lang = message.from_user.language_code
    select_gender_kbd.add(t(lang, "btn_male"), t(lang, "btn_female"))
    return select_gender_kbd


async def inline_agreement(message) -> ReplyKeyboardMarkup:
    inline_agreement_kbd = InlineKeyboardMarkup(row_width=2)
    lang = message.from_user.language_code
    inline_agreement_kbd.insert(InlineKeyboardButton(t(lang, 'btn_agree'), callback_data='start_registration'))
    inline_agreement_kbd.insert(InlineKeyboardButton(t(lang, 'btn_disagree'), callback_data='cancel_registration'))
    return inline_agreement_kbd


async def inline_find_athlete_by_id(message) -> ReplyKeyboardMarkup:
    inline_find_athlete_by_id_kbd = InlineKeyboardMarkup(row_width=2)
    lang = message.from_user.language_code
    inline_find_athlete_by_id_kbd.insert(InlineKeyboardButton(t(lang, 'btn_input_ID'),
                                                              callback_data='athlete_code_search'))
    inline_find_athlete_by_id_kbd.insert(InlineKeyboardButton(t(lang, 'btn_dont_remember_ID'),
                                                              callback_data='help_to_find_id'))
    inline_find_athlete_by_id_kbd.insert(InlineKeyboardButton(t(lang, 'btn_new_runner'),
                                                              callback_data='create_new_athlete'))
    inline_find_athlete_by_id_kbd.insert(InlineKeyboardButton(t(lang, 'btn_cancel'),
                                                              callback_data='cancel_registration'))
    return inline_find_athlete_by_id_kbd


async def inline_open_s95(message) -> ReplyKeyboardMarkup:
    inline_open_s95_kbd = InlineKeyboardMarkup()
    lang = message.from_user.language_code
    inline_open_s95_kbd.row(InlineKeyboardButton(t(lang, 'btn_open_website'),
                                                 url=t(lang, 'link_to_s95_website')))
    return inline_open_s95_kbd
