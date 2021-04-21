from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

inline_kb_parkrun = InlineKeyboardMarkup(row_width=2)

inline_kb_parkrun.insert(InlineKeyboardButton("Выбрать parkrun", switch_inline_query_current_chat='parkrun'))
inline_kb_parkrun.add(InlineKeyboardButton('Перейти на сайт', url='https://parkrun.ru/'))
