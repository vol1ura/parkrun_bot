from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# MAIN bot keyboard layout
main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton('🔧 настройки')
btn2 = KeyboardButton('❓ справка')
btn3 = KeyboardButton('🌳 паркран')
btn4 = KeyboardButton('📋 разное')
main.row(btn3, btn4).add(btn1, btn2)


# STATISTICS inline keyboard layout
inline_stat = InlineKeyboardMarkup(row_width=2)
inline_stat.insert(InlineKeyboardButton('Личные результаты', callback_data='personal_results'))
inline_stat.insert(InlineKeyboardButton('Сравнение результатов', callback_data='compare_results'))
inline_stat.row(InlineKeyboardButton('Последний паркран', switch_inline_query_current_chat='latestresults'))

inline_stat.row(InlineKeyboardButton('Одноклубники', switch_inline_query_current_chat='teammates'))
inline_stat.insert(InlineKeyboardButton('Top10 клубов', callback_data='top_active_clubs'))

inline_stat.insert(InlineKeyboardButton('Рекорды', switch_inline_query_current_chat='records'))
inline_stat.insert(InlineKeyboardButton('Рекордсмены', callback_data='most_records_parkruns'))


# INFORMATION keyboard layout with additional information
inline_info = InlineKeyboardMarkup(row_width=2)
inline_info.insert(InlineKeyboardButton("Ближайшие старты", switch_inline_query_current_chat='events'))

info_btn1 = InlineKeyboardButton("Посмотреть погоду", switch_inline_query_current_chat='weather')
info_btn2 = InlineKeyboardButton("Загрязнение воздуха", switch_inline_query_current_chat='air')

info_btn3 = InlineKeyboardButton('Новость из Instagram', switch_inline_query_current_chat='instagram')
info_btn4 = InlineKeyboardButton('Telegram каналы про бег', callback_data='telegram')
inline_info.row(info_btn1, info_btn2)
inline_info.add(info_btn4, info_btn3)


# SETTINGS inline keyboard layout
inline_parkrun = InlineKeyboardMarkup(row_width=2)
inline_parkrun.insert(InlineKeyboardButton('Мои установки', callback_data='check_settings'))
inline_parkrun.insert(InlineKeyboardButton('Ввести ParkrunID', callback_data='set_athlete'))

inline_parkrun.insert(InlineKeyboardButton('Выбрать parkrun', switch_inline_query_current_chat='parkrun'))
inline_parkrun.insert(InlineKeyboardButton("Выбрать клуб", switch_inline_query_current_chat='clubs'))

inline_parkrun.insert(InlineKeyboardButton('Перейти на сайт parkrun.ru', url='https://parkrun.ru/'))


# PERSONAL RESULTS inline keyboard layout
inline_personal = InlineKeyboardMarkup(row_width=2)
inline_personal.insert(InlineKeyboardButton('Моя история', callback_data='personal_history'))
inline_personal.insert(InlineKeyboardButton('Мои личники', callback_data='personal_bests'))
inline_personal.insert(InlineKeyboardButton('Паркран-туризм', callback_data='personal_tourism'))
inline_personal.insert(InlineKeyboardButton('Победы/участия', callback_data='personal_wins'))

# COMPARATION of personal results
inline_compare = InlineKeyboardMarkup(row_width=2)
inline_compare.row(InlineKeyboardButton('Ввести ID участника', callback_data='enter_compare_id'))
inline_compare.add(InlineKeyboardButton('Баттл-таблица', callback_data='battle_table'))
inline_compare.insert(InlineKeyboardButton('Баттл-диаграмма', callback_data='battle_diagram'))
inline_compare.insert(InlineKeyboardButton('Файл Excel', callback_data='excel_table'))
inline_compare.insert(InlineKeyboardButton('Scatter', callback_data='battle_scatter'))
