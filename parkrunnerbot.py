import logging
import os
import random
import re
import time

import telebot
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
# https://api.telegram.org/{TOKEN}/getMe
from telebot import types

from utils import content, vk, instagram, weather, parkrun, news, fucomp, search

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN_BOT = os.environ.get('API_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN_BOT)
logger = telebot.logger
telebot.logger.setLevel(logging.WARNING)  # Outputs WARNING messages to log and console.


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, content.start_message, disable_notification=True)


@bot.message_handler(commands=['about', 'оботе'])
@bot.message_handler(regexp=r'(?i)^бот\b(?=.*о себе)', content_types=['text'])
def about(message):
    bot.send_message(message.chat.id, content.about_message,
                     disable_notification=True, parse_mode='html', disable_web_page_preview=True)


@bot.message_handler(commands=['admin', 'админ'])
@bot.message_handler(func=lambda message: fucomp.bot_compare(message.text, fucomp.phrases_admin))
def admin(message):
    if message.chat.type == "private":  # private chat message
        bot.send_message(message.chat.id, 'Здесь нет админов, это персональный чат.')
    else:
        admin = random.choice(bot.get_chat_administrators(message.chat.id)).user.to_dict()
        about_admin = f"\nАдмин @{admin['username']} - {admin['first_name']}  {admin['last_name']}"
        bot.send_message(message.chat.id, random.choice(content.phrases_about_admin) + about_admin)


@bot.message_handler(commands=['help', 'помощь', 'команды', 'справка'])
def commands(message):
    bot_nick = bot.get_me().to_dict()["username"]
    bot.send_message(message.chat.id, f"""Я понимаю следующие команды:
    🤖 /about, /оботе - информация о боте
    ❓ /help, /помощь, /справка, /команды - _данное сообщение_
    Есть *inline* режим запросов - наберите в поле ввода сообщения @{bot_nick} <запрос> (примеры):
    @{bot_nick} погода
    @{bot_nick} паркран
    @{bot_nick} воздух
    @{bot_nick} старты
    Через пару секунд появится меню, из которого можно выбрать нужный вариант информации.
    Про погоду и воздух можно также спросить напрямую, например, _Бот, погода Москва Кузьминки_, либо 
    _Бот, воздух Кисловодск_.
    При запросе _Бот, паркран Фамилия_, бот попытается найти результат участника с указанной фамилией на последнем
    загруженном в систему паркране Кузьминки. Если маркеры наползают друг на друга, можно повернуть надпись, 
    указав целое количество градусов поворота, например, _Бот, паркран Фамилия 45_ - надписи повернутся на 45°.
    Если отправлять сообщения _Бот паркран_,  _Бот, инстаграм_, бот будет находить картинки или новости.
    Бот _не чувствителен_ к знакам пунктуации, регистру букв, и, в большинстве случаев, к порядку фраз. 
    Кроме того, с ботом можно просто поболтать - отправьте сообщение, начинающееся словом *бот*.""",
                     disable_notification=True, parse_mode='Markdown')


@bot.message_handler(regexp=r'(?i)бот,? (?:покажи )?(погод\w|воздух)( \w+,?){1,3}$')
def ask_weather(message):
    match = re.search(r'бот,? (?:покажи )?(погод\w|воздух) ([\w, ]+)', message.text, re.I)
    if match:
        place = re.sub(r' в\b', '', match.group(2).strip())
        app = Nominatim(user_agent="wr-tg-bot")
        try:
            location = app.geocode(place).raw
        except AttributeError:
            return bot.reply_to(message, 'Есть такой населённый пункт? ...не знаю. Введите запрос в в формате '
                                         '"Бот, погода Город" или "Бот, воздух Название Область".')
        if match.group(1).startswith('погод'):
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, weather.get_weather(place, location['lat'], location['lon']))
        else:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, weather.get_air_quality(place, location['lat'], location['lon'])[1])


@bot.inline_handler(lambda query: 'погода' in query.query)
def query_weather(inline_query):
    try:
        places_weather = [types.InlineQueryResultArticle(
            f'{k}', k, description='погода сейчас',
            input_message_content=types.InputTextMessageContent(weather.get_weather(k, v.lat, v.lon)))
            for k, v in content.places.items()]
        bot.answer_inline_query(inline_query.id, places_weather, cache_time=3000)
    except Exception as e:
        logger.error(e)


@bot.inline_handler(lambda query: 'воздух' in query.query)
def query_air(inline_query):
    try:
        places_air = [types.InlineQueryResultArticle(
            f'{k}', k, description='качество воздуха',
            input_message_content=types.InputTextMessageContent(weather.get_air_quality(k, v.lat, v.lon)[1]))
            for k, v in content.places.items()]
        bot.answer_inline_query(inline_query.id, places_air, cache_time=3000)
    except Exception as e:
        logger.error(e)


@bot.inline_handler(lambda query: 'паркран' in query.query or 'parkrun' in query.query)
def query_parkrun(inline_query):
    try:
        pattern = '⏳ Получение данных '
        m1 = types.InlineQueryResultArticle(
            f'{1}', 'Где бегали наши одноклубники?', description='перечень паркранов',
            input_message_content=types.InputTextMessageContent(pattern + 'об участии...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/1.jpg',
            thumb_width=48, thumb_height=48)
        m2 = types.InlineQueryResultArticle(
            f'{2}', 'Как установить наш клуб в parkrun?', description='ссылка на клуб Wake&Run',
            input_message_content=types.InputTextMessageContent(parkrun.club_link,
                                                                parse_mode='Markdown', disable_web_page_preview=True),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/2.jpg',
            thumb_width=48, thumb_height=48)
        m3 = types.InlineQueryResultArticle(
            f'{3}', 'Топ 10 волонтёров', description='на паркране Кузьминки',
            input_message_content=types.InputTextMessageContent(pattern + 'о волонтёрах.', parse_mode='Markdown'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/3.jpg',
            thumb_width=48, thumb_height=48)
        m4 = types.InlineQueryResultArticle(
            f'{4}', 'Топ 10 одноклубников по числу забегов', description='на паркране Кузьминки',
            input_message_content=types.InputTextMessageContent(pattern + 'о количестве стартов в Кузьминках...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/4.jpg',
            thumb_width=48, thumb_height=48)
        m5 = types.InlineQueryResultArticle(
            f'{5}', 'Топ 10 одноклубников по количеству паркранов', description='по всем паркранам',
            input_message_content=types.InputTextMessageContent(pattern + 'о количестве всех стартов...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/5.jpg',
            thumb_width=48, thumb_height=48)
        m6 = types.InlineQueryResultArticle(
            f'{6}', 'Топ 10 результатов одноклубников', description='на паркране Кузьминки',
            input_message_content=types.InputTextMessageContent(pattern + 'о рекордах...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/6.jpg',
            thumb_width=48, thumb_height=48)
        m7 = types.InlineQueryResultArticle(
            f'{7}', 'Самые медленные паркраны России', description='по мужским результатам',
            input_message_content=types.InputTextMessageContent(pattern + 'о российских паркранах'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/7.jpg',
            thumb_width=48, thumb_height=48)
        m8 = types.InlineQueryResultArticle(
            f'{8}', 'Гистограмма с последними результатами', description='на паркране Кузьминки',
            input_message_content=types.InputTextMessageContent(pattern + 'и расчёт диаграммы...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/8.jpg',
            thumb_width=48, thumb_height=48)
        m9 = types.InlineQueryResultArticle(
            f'{9}', 'Диаграмма с распределением по клубам', description='на паркране Кузьминки',
            input_message_content=types.InputTextMessageContent(pattern + 'о клубах...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/9.jpg',
            thumb_width=48, thumb_height=48)
        bot.answer_inline_query(inline_query.id, [m1, m3, m8, m9, m4, m5, m6, m7, m2], cache_time=36000)
    except Exception as e:
        logger.error(e)


@bot.message_handler(regexp='⏳ Получение данных', content_types=['text'])
def post_parkrun_info(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if 'об участии' in message.text:
        bot.send_message(message.chat.id,
                         parkrun.get_participants(),
                         parse_mode='Markdown',
                         disable_web_page_preview=True)
    elif 'диаграммы' in message.text:
        pic = parkrun.make_latest_results_diagram('results.png')
        if os.path.exists("results.png"):
            bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File results.png not found! Or the picture wasn\'t generated.')
    elif 'о количестве стартов в Кузьминках' in message.text:
        bot.send_message(message.chat.id, parkrun.get_kuzminki_fans(), parse_mode='Markdown')
    elif 'о количестве всех стартов' in message.text:
        bot.send_message(message.chat.id, parkrun.get_wr_purkruners(), parse_mode='Markdown')
    elif 'о рекордах' in message.text:
        bot.send_message(message.chat.id, parkrun.get_kuzminki_top_results(), parse_mode='Markdown')
    elif 'о российских паркранах' in message.text:
        bot.send_message(message.chat.id, parkrun.most_slow_parkruns(), parse_mode='Markdown')
    elif 'о волонтёрах' in message.text:
        bot.send_message(message.chat.id, parkrun.get_volunteers(), parse_mode='Markdown')
    elif 'о клубах...' in message.text:
        pic = parkrun.make_clubs_bar('clubs.png')
        if os.path.exists("clubs.png"):
            bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File clubs.png not found! Or the picture wasn\'t generated.')

    bot.delete_message(message.chat.id, message.id)


@bot.inline_handler(lambda query: re.search(r'соревнован|старт|забег|competition|event', query.query))
def query_competitions(inline_query):
    try:
        date = time.gmtime(time.time())
        month, year = date.tm_mon, date.tm_year
        competitions = news.get_competitions(month, year)
        logger.info(str(len(competitions)))
        if len(competitions) < 10:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            competitions += news.get_competitions(month, year)
        queries = []
        for i, comp in enumerate(competitions, 1):
            queries.append(types.InlineQueryResultArticle(
                str(i), comp[0], description=comp[1],
                input_message_content=types.InputTextMessageContent(comp[2], parse_mode='html')))
        bot.answer_inline_query(inline_query.id, queries, cache_time=30000)
    except Exception as e:
        logger.error(e)


@bot.message_handler(regexp=r'(?i)бот[, \w]+?(паркран\w?|parkrun)( \w+){1,3}( \d+)?$')
def parkrun_personal_result(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        turn = re.search(r'\d+$', message.text)
        turn = int(turn[0]) % 360 if turn else 0
        person = re.sub(r'.*(паркран\w?|parkrun) ', '', message.text)
        person = re.sub(r'\d', '', person).strip()
        pic = parkrun.make_latest_results_diagram('results.png', person, turn)
        bot.send_photo(message.chat.id, pic)
        pic.close()
    except:
        logger.error(f'Attempt to generate personal diagram failed. Query: {message.text}')
        bot.reply_to(message, 'Что-то пошло не так. Возможно, вы неправильно ввели имя.')


@bot.message_handler(regexp=r'(?i)бот,? (паркран|parkrun)', content_types=['text'])
def get_parkrun_picture(message):
    token = os.environ.get('VK_SERVICE_TOKEN')
    bot.send_photo(message.chat.id, vk.get_random_photo(token), disable_notification=True)


@bot.message_handler(func=lambda message: fucomp.bot_compare(message.text, fucomp.phrases_instagram))
def get_instagram_post(message):
    login = os.environ.get('IG_USERNAME')
    password = os.environ.get('IG_PASSWORD')
    user = random.choice(content.instagram_profiles)
    wait_message = bot.reply_to(message, 'Сейчас что-нибудь найду, подождите...', disable_notification=True)
    ig_post = instagram.get_last_post(login, password, user)
    bot.send_photo(message.chat.id, *ig_post, disable_notification=True)
    bot.delete_message(wait_message.chat.id, wait_message.id)


@bot.message_handler(regexp=r'(?i)^бот\b', content_types=['text'])
def simple_answers(message):
    ans = []
    if 'как' in message.text and re.search(r'\bдела\b|жизнь|\bсам\b|поживаешь', message.text, re.I):
        ans = content.phrases_about_myself
    elif re.search(r'привет|\bhi\b|hello|здравствуй', message.text, re.I):
        user = message.from_user.first_name
        ans = [s.format(user) for s in content.greeting]
    elif fucomp.bot_compare(message.text, fucomp.phrases_parkrun):
        ans = content.phrases_about_parkrun

    if ans:
        bot.reply_to(message, random.choice(ans), disable_web_page_preview=True)
        return
    elif 'погода' in message.text:
        bot_nick = bot.get_me().to_dict()["username"]
        ans = ['Информацию о погоде можно получить через inline запрос: '
               f'в строке сообщений наберите "@{bot_nick} погода".'
               'Либо, набрав сообщение, "Бот, погода Населённый пункт", '
               'например, "Бот, погода Кузьминки Москва".']
    elif re.search(r'GRUT|ГРУТ', message.text, re.I):
        ans = content.phrases_grut
    elif re.search(r'\bгречк|\bгречневая', message.text, re.I):
        ans = content.phrases_grechka
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        if random.randrange(11) % 2:
            ans = [search.google(message.text)]
            if not ans[0]:
                ans = [random.choice(content.phrases_about_running)]
        else:
            ans = [fucomp.best_answer(message.text, fucomp.message_base_m)]
    bot.send_message(message.chat.id, random.choice(ans), disable_web_page_preview=True, disable_notification=True)


if __name__ == '__main__':
    # print(os.environ.get('API_BOT_TOKEN'))
    bot.remove_webhook()
    bot.polling(none_stop=True)
