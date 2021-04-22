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
stat_btn4 = InlineKeyboardButton('Результаты последнего паркрана', switch_inline_query_current_chat='latestresults')
stat_btn5 = InlineKeyboardButton('Одноклубники', switch_inline_query_current_chat='teammates')
stat_btn3 = InlineKeyboardButton('Top10 клубов', callback_data='top_active_clubs')
stat_btn1 = InlineKeyboardButton('Рекорды', switch_inline_query_current_chat='records')
stat_btn2 = InlineKeyboardButton('Рекордсмены', callback_data='most_records_parkruns')
inline_stat.add(stat_btn4).add(stat_btn5, stat_btn3, stat_btn1, stat_btn2)

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
inline_parkrun.insert(InlineKeyboardButton('Выбрать parkrun', switch_inline_query_current_chat='parkrun'))
inline_parkrun.insert(InlineKeyboardButton("Выбрать клуб", switch_inline_query_current_chat='clubs'))
inline_parkrun.insert(InlineKeyboardButton('Мои установки', callback_data='check_settings'))
inline_parkrun.insert(InlineKeyboardButton('Перейти на сайт parkrun.ru', url='https://parkrun.ru/'))
