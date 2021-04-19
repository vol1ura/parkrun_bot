import os
import random
import re
import time

from aiogram import Bot, Dispatcher, executor, types

from dotenv import load_dotenv
# https://api.telegram.org/{TOKEN_BOT}/getMe

from utils import content, vk, instagram, weather, parkrun, news, fucomp, search

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN_BOT = os.environ.get('API_BOT_TOKEN')
bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(bot)




# @bot.inline_handler(lambda query: 'погода' in query.query)
# def query_weather(inline_query):
#     try:
#         places_weather = [types.InlineQueryResultArticle(
#             f'{k}', k, description='погода сейчас',
#             input_message_content=types.InputTextMessageContent(weather.get_weather(k, v.lat, v.lon)))
#             for k, v in content.places.items()]
#         bot.answer_inline_query(inline_query.id, places_weather, cache_time=3000)
#     except Exception as e:
#         logger.error(e)
#
#
# @bot.inline_handler(lambda query: 'воздух' in query.query)
# def query_air(inline_query):
#     try:
#         places_air = [types.InlineQueryResultArticle(
#             f'{k}', k, description='качество воздуха',
#             input_message_content=types.InputTextMessageContent(weather.get_air_quality(k, v.lat, v.lon)[1]))
#             for k, v in content.places.items()]
#         bot.answer_inline_query(inline_query.id, places_air, cache_time=3000)
#     except Exception as e:
#         logger.error(e)
#
#
# @bot.inline_handler(lambda query: 'паркран' in query.query or 'parkrun' in query.query)
# def query_parkrun(inline_query):
#     try:
#         pattern = '⏳ Получение данных '
#         m1 = types.InlineQueryResultArticle(
#             f'{1}', 'Где бегали наши одноклубники?', description='перечень паркранов',
#             input_message_content=types.InputTextMessageContent(pattern + 'об участии...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/1.jpg',
#             thumb_width=48, thumb_height=48)
#         m2 = types.InlineQueryResultArticle(
#             f'{2}', 'Как установить наш клуб в parkrun?', description='ссылка на клуб Wake&Run',
#             input_message_content=types.InputTextMessageContent(parkrun.club_link,
#                                                                 parse_mode='Markdown', disable_web_page_preview=True),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/2.jpg',
#             thumb_width=48, thumb_height=48)
#         m3 = types.InlineQueryResultArticle(
#             f'{3}', 'Топ 10 волонтёров', description='на паркране Кузьминки',
#             input_message_content=types.InputTextMessageContent(pattern + 'о волонтёрах.', parse_mode='Markdown'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/3.jpg',
#             thumb_width=48, thumb_height=48)
#         m4 = types.InlineQueryResultArticle(
#             f'{4}', 'Топ 10 одноклубников по числу забегов', description='на паркране Кузьминки',
#             input_message_content=types.InputTextMessageContent(pattern + 'о количестве стартов в Кузьминках...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/4.jpg',
#             thumb_width=48, thumb_height=48)
#         m5 = types.InlineQueryResultArticle(
#             f'{5}', 'Топ 10 одноклубников по количеству паркранов', description='по всем паркранам',
#             input_message_content=types.InputTextMessageContent(pattern + 'о количестве всех стартов...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/5.jpg',
#             thumb_width=48, thumb_height=48)
#         m6 = types.InlineQueryResultArticle(
#             f'{6}', 'Топ 10 результатов одноклубников', description='на паркране Кузьминки',
#             input_message_content=types.InputTextMessageContent(pattern + 'о рекордах...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/6.jpg',
#             thumb_width=48, thumb_height=48)
#         m7 = types.InlineQueryResultArticle(
#             f'{7}', 'Самые медленные паркраны России', description='по мужским результатам',
#             input_message_content=types.InputTextMessageContent(pattern + 'о российских паркранах'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/7.jpg',
#             thumb_width=48, thumb_height=48)
#         m8 = types.InlineQueryResultArticle(
#             f'{8}', 'Гистограмма с последними результатами', description='на паркране Кузьминки',
#             input_message_content=types.InputTextMessageContent(pattern + 'и расчёт диаграммы...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/8.jpg',
#             thumb_width=48, thumb_height=48)
#         m9 = types.InlineQueryResultArticle(
#             f'{9}', 'Диаграмма с распределением по клубам', description='на паркране Кузьминки',
#             input_message_content=types.InputTextMessageContent(pattern + 'о клубах...'),
#             thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/9.jpg',
#             thumb_width=48, thumb_height=48)
#         bot.answer_inline_query(inline_query.id, [m1, m3, m8, m9, m4, m5, m6, m7, m2], cache_time=36000)
#     except Exception as e:
#         logger.error(e)
#
#
# @bot.message_handler(regexp='⏳ Получение данных', content_types=['text'])
# def post_parkrun_info(message):
#     bot.send_chat_action(message.chat.id, 'typing')
#     if 'об участии' in message.text:
#         bot.send_message(message.chat.id,
#                          parkrun.get_participants(),
#                          parse_mode='Markdown',
#                          disable_web_page_preview=True)
#     elif 'диаграммы' in message.text:
#         pic = parkrun.make_latest_results_diagram('results.png')
#         if os.path.exists("results.png"):
#             bot.send_photo(message.chat.id, pic)
#             pic.close()
#         else:
#             logger.error('File results.png not found! Or the picture wasn\'t generated.')
#     elif 'о количестве стартов в Кузьминках' in message.text:
#         bot.send_message(message.chat.id, parkrun.get_kuzminki_fans(), parse_mode='Markdown')
#     elif 'о количестве всех стартов' in message.text:
#         bot.send_message(message.chat.id, parkrun.get_wr_purkruners(), parse_mode='Markdown')
#     elif 'о рекордах' in message.text:
#         bot.send_message(message.chat.id, parkrun.get_kuzminki_top_results(), parse_mode='Markdown')
#     elif 'о российских паркранах' in message.text:
#         bot.send_message(message.chat.id, parkrun.most_slow_parkruns(), parse_mode='Markdown')
#     elif 'о волонтёрах' in message.text:
#         bot.send_message(message.chat.id, parkrun.get_volunteers(), parse_mode='Markdown')
#     elif 'о клубах...' in message.text:
#         pic = parkrun.make_clubs_bar('clubs.png')
#         if os.path.exists("clubs.png"):
#             bot.send_photo(message.chat.id, pic)
#             pic.close()
#         else:
#             logger.error('File clubs.png not found! Or the picture wasn\'t generated.')
#
#     bot.delete_message(message.chat.id, message.id)
#
#
# @bot.inline_handler(lambda query: re.search(r'соревнован|старт|забег|competition|event', query.query))
# def query_competitions(inline_query):
#     try:
#         date = time.gmtime(time.time())
#         month, year = date.tm_mon, date.tm_year
#         competitions = news.get_competitions(month, year)
#         logger.info(str(len(competitions)))
#         if len(competitions) < 10:
#             if month == 12:
#                 month = 1
#                 year += 1
#             else:
#                 month += 1
#             competitions += news.get_competitions(month, year)
#         queries = []
#         for i, comp in enumerate(competitions, 1):
#             queries.append(types.InlineQueryResultArticle(
#                 str(i), comp[0], description=comp[1],
#                 input_message_content=types.InputTextMessageContent(comp[2], parse_mode='html')))
#         bot.answer_inline_query(inline_query.id, queries, cache_time=30000)
#     except Exception as e:
#         logger.error(e)
#
#
# @bot.message_handler(func=lambda message: fucomp.bot_compare(message.text, fucomp.phrases_instagram))
# def get_instagram_post(message):
#     login = os.environ.get('IG_USERNAME')
#     password = os.environ.get('IG_PASSWORD')
#     user = random.choice(content.instagram_profiles)
#     wait_message = bot.reply_to(message, 'Сейчас что-нибудь найду, подождите...', disable_notification=True)
#     ig_post = instagram.get_last_post(login, password, user)
#     bot.send_photo(message.chat.id, *ig_post, disable_notification=True)
#     bot.delete_message(wait_message.chat.id, wait_message.id)


if __name__ == '__main__':
    # print(os.environ.get('API_BOT_TOKEN'))
    bot.delete_webhook()
    executor.start_polling(dp, skip_updates=True)
