import logging
import random
import re
import time

from aiogram import Bot, Dispatcher, types, executor
from geopy.geocoders import Nominatim

import keyboards as kb
from config import *
from utils import content, fucomp, weather, vk, search, parkrun, news, instagram

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.answer(content.start_message, reply_markup=kb.main, disable_notification=True)


@dp.message_handler(regexp='❓ справка')
@dp.message_handler(commands=['help', 'помощь'])
async def commands(message: types.Message):
    await message.answer(content.help_message, disable_notification=True, parse_mode='html')


@dp.message_handler(commands=['admin', 'админ'])
@dp.message_handler(lambda message: fucomp.bot_compare(message.text, fucomp.phrases_admin))
async def admin(message: types.Message):
    if message.chat.type == 'private':  # private chat message
        await message.reply('Здесь нет админов, это персональный чат.')
    else:
        admin = random.choice(await bot.get_chat_administrators(message.chat.id)).user
        about_admin = f'\nАдмин @{admin.username} - {admin.first_name}  {admin.last_name}'
        await message.answer(random.choice(content.phrases_about_admin) + about_admin)


@dp.message_handler(regexp='🔧 настройки')
@dp.message_handler(commands=['settings'])
async def process_command_settings(message: types.Message):
    await message.answer('Установка параметров', reply_markup=kb.inline_parkrun)


@dp.message_handler(regexp='📑 общая статистика')
@dp.message_handler(commands=['statistics'])
async def process_command_statistics(message: types.Message):
    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_stat)


@dp.message_handler(regexp='📋 полезная информация')
@dp.message_handler(commands=['info'])
async def process_command_statistics(message: types.Message):
    await message.answer('Кое-что ещё помимо паркранов:', reply_markup=kb.inline_info)


@dp.message_handler(regexp=r'(?i)бот,? (?:покажи )?(погод\w|воздух)( \w+,?){1,3}$')
async def ask_weather(message: types.Message):
    match = re.search(r'бот,? (?:покажи )?(погод\w|воздух) ([\w, ]+)', message.text, re.I)
    if match:
        place = re.sub(r' в ', '', match.group(2)).strip()
        app = Nominatim(user_agent="parkrun-bot")
        try:
            location = app.geocode(place).raw
        except AttributeError:
            return await message.reply(f'Есть такой населённый пункт - {place}? ...не знаю. Введите запрос в в формате '
                                       '"Бот, погода Город" или "Бот, воздух Название Область".')
        if match.group(1).startswith('погод'):
            await bot.send_chat_action(message.chat.id, 'typing')
            weather_info = await weather.get_weather(place, location['lat'], location['lon'])
            await message.answer(weather_info)
        else:
            await bot.send_chat_action(message.chat.id, 'typing')
            air_info = await weather.get_air_quality(place, location['lat'], location['lon'])
            await message.answer(air_info[1])


@dp.message_handler(regexp=r'(?i)бот[, \w]+?(паркран\w?|parkrun)( \w+)( \d+)?$')
async def parkrun_personal_result(message: types.Message):
    await types.ChatActions.upload_photo()
    try:
        turn = re.search(r'\d+$', message.text)
        turn = int(turn[0]) % 360 if turn else 0
        person = re.sub(r'.*(паркран\w?|parkrun) ', '', message.text)
        person = re.sub(r'\d', '', person).strip()
        pic = await parkrun.make_latest_results_diagram('kuzminki', 'results.png', person, turn)
        await bot.send_photo(message.chat.id, pic)
        pic.close()
    except:
        logger.error(f'Attempt to generate personal diagram failed. Query: {message.text}')
        await message.reply('Что-то пошло не так. Возможно, вы неправильно ввели имя.')


@dp.message_handler(regexp=r'(?i)бот,? (паркран|parkrun)')
async def get_parkrun_picture(message: types.Message):
    token = os.getenv('VK_SERVICE_TOKEN')
    photo_url = await vk.get_random_photo(token)
    await bot.send_photo(message.chat.id, photo_url, disable_notification=True)


@dp.message_handler(regexp=r'(?i)^бот\b', content_types=['text'])
async def simple_answers(message: types.Message):
    if 'как' in message.text and re.search(r'\bдела\b|жизнь|\bсам\b|поживаешь', message.text, re.I):
        ans = content.phrases_about_myself
    elif re.search(r'привет|\bhi\b|hello|здравствуй', message.text, re.I):
        user = message.from_user.first_name
        ans = [s.format(user) for s in content.greeting]
    elif fucomp.bot_compare(message.text, fucomp.phrases_parkrun):
        ans = content.phrases_about_parkrun
    elif 'погода' in message.text:
        bot_info = await bot.get_me()
        ans = ['Информацию о погоде можно получить через inline запрос: '
               f'в строке сообщений наберите "@{bot_info.username} погода".'
               'Либо, набрав сообщение, "Бот, погода Населённый пункт", '
               'например, "Бот, погода Кузьминки Москва".']
    elif re.search(r'GRUT|ГРУТ', message.text, re.I):
        ans = content.phrases_grut
    elif re.search(r'\bгречк|\bгречневая', message.text, re.I):
        ans = content.phrases_grechka
    else:
        ans = []

    if ans:
        await message.reply(random.choice(ans), disable_web_page_preview=True)
        return
    else:
        await bot.send_chat_action(message.chat.id, 'typing')
        if random.randrange(11) % 2:
            ans = await search.google(message.text)
            if not ans:
                ans = [random.choice(content.phrases_about_running)]
        else:
            ans = [fucomp.best_answer(message.text, fucomp.message_base_m)]
    await message.answer(random.choice(ans), disable_web_page_preview=True, disable_notification=True)


@dp.inline_handler(lambda query: 'parkrun' in query.query or 'паркран' in query.query)
async def query_all_parkruns(query):
    offset = int(query.offset) if query.offset else 0
    try:
        parkruns_list = parkrun.PARKRUNS
        quotes = parkruns_list[offset:]
        m_next_offset = str(offset + 5) if len(quotes) >= 5 else None
        parkruns_menu = [types.InlineQueryResultArticle(
            id=f'{k}', title=p, input_message_content=types.InputTextMessageContent(f'/setparkrun {p}')
        )
            for k, p in enumerate(quotes[:5])]
        await bot.answer_inline_query(query.id, parkruns_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=3)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'clubs' in query.query or 'клуб' in query.query)
async def query_all_clubs(query):
    offset = int(query.offset) if query.offset else 0
    try:
        clubs_list = parkrun.CLUBS
        quotes = clubs_list[offset:]
        m_next_offset = str(offset + 5) if len(quotes) >= 5 else None
        clubs_menu = [types.InlineQueryResultArticle(
            id=f'{k}', title=p['name'], input_message_content=types.InputTextMessageContent(f"/setclub {p['name']}")
        )
            for k, p in enumerate(quotes[:5])]
        await bot.answer_inline_query(query.id, clubs_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=30)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'погода' in query.query or 'weather' in query.query)
async def query_weather(inline_query):
    try:
        data = []
        for k, v in content.places.items():
            w = await weather.get_weather(k, v.lat, v.lon)
            data.append(w)
        places_weather = [types.InlineQueryResultArticle(
            id=f'{k}', title=k, description='погода сейчас',
            input_message_content=types.InputTextMessageContent(w))
            for (k, v), w in zip(content.places.items(), data)]
        await bot.answer_inline_query(inline_query.id, places_weather, cache_time=35)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'воздух' in query.query or 'air' in query.query)
async def query_air(inline_query):
    try:
        data = []
        for k, v in content.places.items():
            aq = await weather.get_air_quality(k, v.lat, v.lon)
            data.append(aq)
        places_air = [types.InlineQueryResultArticle(
            id=f'{k}', title=k, description='качество воздуха',
            input_message_content=types.InputTextMessageContent(aq[1]))
            for (k, v), aq in zip(content.places.items(), data)]
        await bot.answer_inline_query(inline_query.id, places_air, cache_time=36)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: re.search(r'соревнован|старт|забег|events', query.query))
async def query_competitions(inline_query):
    try:
        date = time.gmtime(time.time())
        month, year = date.tm_mon, date.tm_year
        competitions = await news.get_competitions(month, year)
        logger.info(str(len(competitions)))
        if len(competitions) < 10:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            competitions += await news.get_competitions(month, year)
        queries = []
        for i, comp in enumerate(competitions, 1):
            queries.append(types.InlineQueryResultArticle(
                id=str(i), title=comp[0], description=comp[1],
                input_message_content=types.InputTextMessageContent(comp[2], parse_mode='html')))
        await bot.answer_inline_query(inline_query.id, queries, cache_time=300000)
    except Exception as e:
        logger.error(e)


@dp.callback_query_handler(lambda c: c.data == 'telegram')
async def process_callback_telegram(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, content.telegram_channels,
                           parse_mode='Markdown', disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data == 'most_records_parkruns')
async def process_most_records(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await parkrun.top_records_count('records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.inline_handler(lambda query: 'records' in query.query)
async def display_records_menu(inline_query):
    try:
        records_tables = await parkrun.top_parkruns()
        m1 = types.InlineQueryResultArticle(id='1', title='Top10 быстрых паркранов', description='по мужским рекордам',
                                            input_message_content=types.InputTextMessageContent(records_tables[0],
                                                                                                parse_mode='Markdown'))
        m2 = types.InlineQueryResultArticle(id='2', title='Top10 быстрых паркранов', description='по женским рекордам',
                                            input_message_content=types.InputTextMessageContent(records_tables[2],
                                                                                                parse_mode='Markdown'))
        m3 = types.InlineQueryResultArticle(id='3', title='Top10 медленных паркранов',
                                            description='по мужским результатам',
                                            input_message_content=types.InputTextMessageContent(records_tables[1],
                                                                                                parse_mode='Markdown'))
        m4 = types.InlineQueryResultArticle(id='4', title='Top10 медленных паркранов',
                                            description='по женским результатам',
                                            input_message_content=types.InputTextMessageContent(records_tables[3],
                                                                                                parse_mode='Markdown'))
        await bot.answer_inline_query(inline_query.id, [m1, m2, m3, m4], cache_time=600)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'instagram' in query.query)
async def display_instagram_menu(query):
    offset = int(query.offset) if query.offset else 0
    try:
        quotes = content.instagram_profiles[offset:]
        m_next_offset = str(offset + 5) if len(quotes) >= 5 else None
        inst_menu = [types.InlineQueryResultArticle(
            id=f'{k}', title=f'@{p}',
            input_message_content=types.InputTextMessageContent(f"Достаю последний пост из @{p}. Подождите...")
        )
            for k, p in enumerate(quotes[:5])]
        await bot.answer_inline_query(query.id, inst_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=30)
    except Exception as e:
        logger.error(e)


@dp.message_handler(regexp=r'Достаю последний пост из @[\w.]+ Подождите\.{3}')
async def get_instagram_post(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    login = os.environ.get('IG_USERNAME')
    password = os.environ.get('IG_PASSWORD')
    user = re.search(r'из @([\w.]+)\. Подождите\.', message.text)[1]
    print(user)
    ig_post = instagram.get_last_post(login, password, user)
    await bot.send_photo(message.chat.id, *ig_post, disable_notification=True)


# Run after startup
async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await parkrun.update_parkruns_list()
    await parkrun.update_parkruns_clubs()


# Run before shutdown
async def on_shutdown(dp):
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == "__main__":
    if "HEROKU" in list(os.environ.keys()):
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )
    else:
        executor.start_polling(dp)
