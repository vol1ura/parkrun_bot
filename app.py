import logging
import random
import re
import time

from aiogram import Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError, BotBlocked
from geopy.geocoders import Nominatim
from vedis import Vedis

import keyboards as kb
from bot_exceptions import ParsingException
from config import *
from utils import content, fucomp, weather, vk, search, parkrun, news, instagram


bot = Bot(TOKEN_BOT)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(format=u'%(levelname)s [ LINE:%(lineno)+3s ]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_throttled_query(*args, **kwargs):
    # args will be the same as in the original handler
    # kwargs will be updated with parameters given to .throttled (rate, key, user_id, chat_id)
    logger.warning(f'Message was throttled with args={args} and kwargs={kwargs}')
    message = args[0]  # as message was the first argument in the original handler
    await message.answer("Подождите, я не успеваю 🤖")


@dp.message_handler(commands='start')
@dp.throttled(rate=5)
async def send_welcome(message: types.Message):
    await message.answer(content.start_message, reply_markup=kb.main, disable_notification=True)


@dp.message_handler(regexp='❓ справка')
@dp.message_handler(commands=['help', 'помощь'])
@dp.throttled(rate=3)
async def commands(message: types.Message):
    await message.answer(content.help_message,
                         disable_notification=True, parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(commands=['admin', 'админ'])
@dp.message_handler(lambda message: fucomp.bot_compare(message.text, fucomp.phrases_admin))
@dp.throttled(rate=3)
async def admin(message: types.Message):
    if message.chat.type == 'private':  # private chat message
        await message.reply('Здесь нет админов, это персональный чат.')
    else:
        admin = random.choice(await bot.get_chat_administrators(message.chat.id)).user
        about_admin = f'\nАдмин @{admin.username} - {admin.first_name}  {admin.last_name}'
        await message.answer(random.choice(content.phrases_about_admin) + about_admin)


@dp.message_handler(regexp='🔧 настройки')
@dp.message_handler(commands=['settings'])
@dp.throttled(rate=2)
async def process_command_settings(message: types.Message):
    await message.answer('Установка параметров', reply_markup=kb.inline_parkrun)


@dp.message_handler(regexp='🌳 паркран')
@dp.message_handler(commands=['statistics'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await message.answer('Выберите интересующий вас показатель', reply_markup=kb.inline_stat)


@dp.message_handler(regexp='📋 разное')
@dp.message_handler(commands=['info'])
@dp.throttled(rate=2)
async def process_command_statistics(message: types.Message):
    await message.answer('Кое-что ещё помимо паркранов:', reply_markup=kb.inline_info)


@dp.callback_query_handler(lambda c: c.data == 'check_settings')
@dp.throttled(rate=5)
async def check_settings(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Получение данных..')
    user_id = callback_query.from_user.id
    try:
        with Vedis(DB_FILE) as db:
            h = db.Hash(user_id)
            mes1 = h['pr'].decode() if h['pr'] else 'не выбран.'
            mes2 = h['cl'].decode() if h['cl'] else 'не выбран.'
    except Exception as e:
        logger.error(f'Getting settings from DB failed for user {user_id}. Error: {e}')
        return await bot.answer_callback_query(callback_query.id,
                                               text='⛔ Не удалось получить настройки.',
                                               show_alert=True)
    await bot.send_message(callback_query.from_user.id, f'*Паркран*: {mes1}\n*Клуб*: {mes2}', parse_mode='Markdown')


@dp.message_handler(commands=['setparkrun'])
@dp.throttled(rate=4)
async def process_command_setparkrun(message: types.Message):
    parkrun_name = message.get_args()
    if not parkrun_name:
        return await message.answer(content.no_parkrun_message, reply_markup=kb.main)
    if parkrun_name not in parkrun.PARKRUNS:
        return await message.answer('В моей базе нет такого паркрана. Проверьте ввод.')
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(user_id)
            h['pr'] = parkrun_name
            return await message.answer(content.success_parkrun_set.format(parkrun_name))
        except Exception as e:
            logger.error(f'Writing parkrun to DB failed. User ID={user_id}, argument {parkrun_name}. Error: {e}')
            return await message.answer(content.settings_save_failed)


@dp.message_handler(commands=['setclub'])
@dp.throttled(rate=4)
async def process_command_setclub(message: types.Message):
    club = message.get_args()
    if not club:
        return await message.answer(content.no_club_message, reply_markup=kb.main)
    if club.isdigit():
        club_id = club
        club = await parkrun.check_club_as_id(club)
    else:
        club_id = next((c['id'] for c in parkrun.CLUBS if c['name'] == club), None)
    if not (club_id and club):
        return await message.answer('В базе нет такого клуба. Проверьте ввод.')
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        try:
            h = db.Hash(user_id)
            h['cl'] = club
            h['cl_id'] = club_id
            return await message.answer(content.success_club_set.format(club, club_id),
                                        disable_web_page_preview=True, parse_mode='Markdown')
        except Exception as e:
            logger.error(f'Writing club to DB failed. User ID={user_id}, argument {club}. Error: {e}')
            return await message.answer(content.settings_save_failed)


@dp.message_handler(regexp=r'(?i)бот,? (?:покажи )?(погод\w|воздух)( \w+,?){1,3}$')
@dp.throttled(handle_throttled_query, rate=10)
async def ask_weather(message: types.Message):
    match = re.search(r'бот,? (?:покажи )?(погод\w|воздух) ([\w, ]+)', message.text, re.I)
    if match:
        place = re.sub(r' в ', '', match.group(2)).strip()
        app = Nominatim(user_agent="parkrun-bot")
        try:
            location = app.geocode(place).raw
        except AttributeError:
            logger.warning(f'Requesting location failed. No such place {place}.')
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
@dp.throttled(handle_throttled_query, rate=10)
async def parkrun_personal_result(message: types.Message):
    await types.ChatActions.upload_photo()
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        h = db.Hash(user_id)
        parkrun_name = h['pr']
    if not parkrun_name:
        return await message.reply(content.no_parkrun_message)
    parkrun_name = parkrun_name.decode()
    try:
        turn = re.search(r'\d+$', message.text)
        turn = int(turn[0]) % 360 if turn else 0
        person = re.sub(r'.*(паркран\w?|parkrun) ', '', message.text)
        person = re.sub(r'\d', '', person).strip()
        pic = await parkrun.make_latest_results_diagram(parkrun_name, 'results.png', person, turn)
        await bot.send_photo(message.chat.id, pic)
        pic.close()
    except:
        logger.error(f'Attempt to generate personal diagram failed. Query: {message.text}')
        await message.reply('Что-то пошло не так. Возможно, вы неправильно ввели имя '
                            'или  такого участника не было на установленном вами паркране.')


@dp.message_handler(regexp=r'(?i)бот,? (паркран|parkrun)')
@dp.throttled(handle_throttled_query, rate=3)
async def get_parkrun_picture(message: types.Message):
    token = os.getenv('VK_SERVICE_TOKEN')
    photo_url = await vk.get_random_photo(token)
    await bot.send_photo(message.chat.id, photo_url, disable_notification=True)


@dp.message_handler(regexp=r'(?i)^бот\b', content_types=['text'])
@dp.throttled(handle_throttled_query, rate=2)
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
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        parkruns_menu = [types.InlineQueryResultArticle(
            id=f'{offset + k}', title=p, input_message_content=types.InputTextMessageContent(f'/setparkrun {p}')
        )
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(query.id, parkruns_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=60000)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'clubs' in query.query or 'клуб' in query.query)
async def query_all_clubs(query):
    offset = int(query.offset) if query.offset else 0
    try:
        clubs_list = parkrun.CLUBS
        quotes = clubs_list[offset:]
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        clubs_menu = [types.InlineQueryResultArticle(
            id=f'{k + offset}', title=p['name'], input_message_content=types.InputTextMessageContent(f"/setclub {p['name']}")
        )
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(query.id, clubs_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=60000)
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
        await bot.answer_inline_query(inline_query.id, places_weather, cache_time=3200)
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
        await bot.answer_inline_query(inline_query.id, places_air, cache_time=3200)
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
@dp.throttled(handle_throttled_query, rate=15)
async def process_most_records(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = await parkrun.top_records_count('records.png')
    await bot.send_photo(callback_query.from_user.id, pic)
    pic.close()


@dp.callback_query_handler(lambda c: c.data == 'top_active_clubs')
@dp.throttled(handle_throttled_query, rate=15)
async def process_active_clubs(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Подождите, идёт построение диаграммы...')
    pic = parkrun.top_active_clubs_diagram('top_clubs.png')
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
        await bot.answer_inline_query(inline_query.id, [m1, m2, m3, m4], cache_time=100000)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'teammates' in query.query)
async def query_teammates(inline_query):
    try:
        pattern = '⏳ Получение данных '
        m1 = types.InlineQueryResultArticle(
            id='1', title='Где бегали мои одноклубники?', description='перечень последних паркранов',
            input_message_content=types.InputTextMessageContent(pattern + 'об участии...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/1.jpg',
            thumb_width=48, thumb_height=48)
        m2 = types.InlineQueryResultArticle(
            id='2', title='Информация и установка клуба в системе parkrun',
            description='отобразится выбранный клуб',
            input_message_content=types.InputTextMessageContent(pattern + 'о выбранном клубе'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/2.jpg',
            thumb_width=48, thumb_height=48)
        m3 = types.InlineQueryResultArticle(
            id='3', title='Топ 10 одноклубников по числу забегов', description='на выбранном паркране',
            input_message_content=types.InputTextMessageContent(pattern + 'о количестве локальных стартов...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/4.jpg',
            thumb_width=48, thumb_height=48)
        m4 = types.InlineQueryResultArticle(
            id='4', title='Топ 10 одноклубников по количеству паркранов', description='по всем паркранам',
            input_message_content=types.InputTextMessageContent(pattern + 'о количестве всех стартов...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/5.jpg',
            thumb_width=48, thumb_height=48)
        m5 = types.InlineQueryResultArticle(
            id='5', title='Топ 10 результатов моих одноклубников', description='на выбранном паркране',
            input_message_content=types.InputTextMessageContent(pattern + 'о рекордах...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/6.jpg',
            thumb_width=48, thumb_height=48)
        await bot.answer_inline_query(inline_query.id, [m1, m3, m4, m5, m2], cache_time=36000)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'latestresults' in query.query)
async def query_latestparkrun(inline_query):
    try:
        pattern = '📊 Получение данных '
        # m3 = types.InlineQueryResultArticle(
        #     f'{3}', 'Топ 10 волонтёров', description='на паркране Кузьминки',
        #     input_message_content=types.InputTextMessageContent(pattern + 'о волонтёрах.', parse_mode='Markdown'),
        #     thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/3.jpg',
        #     thumb_width=48, thumb_height=48)
        m1 = types.InlineQueryResultArticle(
            id='1', title='Гистограмма с последними результатами', description='на выбранном паркране',
            input_message_content=types.InputTextMessageContent(pattern + 'и расчёт диаграммы...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/8.jpg',
            thumb_width=48, thumb_height=48)
        m2 = types.InlineQueryResultArticle(
            id='2', title='Диаграмма распределения участников по клубам', description='на выбранном паркране',
            input_message_content=types.InputTextMessageContent(pattern + 'о клубах...'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/9.jpg',
            thumb_width=48, thumb_height=48)
        await bot.answer_inline_query(inline_query.id, [m1, m2], cache_time=36000)
    except Exception as e:
        logger.error(e)


@dp.message_handler(regexp='⏳ Получение данных об участии...', content_types=['text'])
@dp.throttled(handle_throttled_query, rate=12)
async def latestparkruns_club_participation(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        club_id = db.Hash(user_id)['cl_id']
    if not club_id:
        await message.answer(content.no_club_message)
    else:
        club_id = club_id.decode()
        data = await parkrun.get_participants(club_id)
        await message.answer(data, parse_mode='Markdown', disable_web_page_preview=True)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(regexp='📊 Получение данных', content_types=['text'])
@dp.throttled(handle_throttled_query, rate=12)
async def post_latestparkrun_diagrams(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        h = db.Hash(user_id)
        parkrun_name = h['pr']
    if not parkrun_name:
        return await message.answer(content.no_parkrun_message)
    parkrun_name = parkrun_name.decode()

    if 'диаграммы' in message.text:
        pic = await parkrun.make_latest_results_diagram(parkrun_name, 'results.png')
        if os.path.exists("results.png"):
            await bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File results.png not found! Or the picture wasn\'t generated.')

    elif 'о клубах...' in message.text:
        pic = await parkrun.make_clubs_bar(parkrun_name, 'clubs.png')
        if os.path.exists("clubs.png"):
            await bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File clubs.png not found! Or the picture wasn\'t generated.')

    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(regexp='⏳ Получение данных о ', content_types=['text'])
@dp.throttled(handle_throttled_query, rate=12)
async def post_teammate_table(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    user_id = message.from_user.id
    with Vedis(DB_FILE) as db:
        h = db.Hash(user_id)
        parkrun_name = h['pr']
        club_id = h['cl_id']
    if not club_id:
        await message.answer(content.no_club_message)
    if not parkrun_name:
        await message.answer(content.no_parkrun_message)
    if not (club_id and parkrun_name):
        return
    parkrun_name = parkrun_name.decode()
    club_id = club_id.decode()

    if 'количестве локальных стартов' in message.text:
        data = await parkrun.get_club_fans(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'количестве всех стартов' in message.text:
        data = await parkrun.get_club_purkruners(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'рекордах' in message.text:
        data = await parkrun.get_parkrun_club_top_results(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'выбранном клубе' in message.text:
        club_rec = [club for club in parkrun.CLUBS if club['id'] == club_id]
        if club_rec:
           info = f"""*Выбранный клуб*: {club_rec[0]['name']}.
           *Зарегистрированных участников*: {club_rec[0]['participants']}.
           *Ссылка на клуб в интернете*: {club_rec[0]['link']}.
           *Ссылка на клуб на сайте parkrun.ru*: https://www.parkrun.com/profile/groups#id={club_rec[0]['id']}
           Перейдите по последней ссылке и нажмите кнопку _Присоединиться_, 
           чтобы установить клуб (вы должны быть залогинены)."""
           await message.answer(info, parse_mode='Markdown')
        else:
            await message.answer('Информация о вашем клубе не найдена. Проверьте настройки.')
    await bot.delete_message(message.chat.id, message.message_id)


@dp.inline_handler(lambda query: 'instagram' in query.query)
async def display_instagram_menu(query):
    offset = int(query.offset) if query.offset else 0
    try:
        quotes = content.instagram_profiles[offset:]
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        inst_menu = [types.InlineQueryResultArticle(
            id=f'{k + offset}', title=f'@{p}',
            input_message_content=types.InputTextMessageContent(f"Достаю последний пост из @{p}. Подождите...")
        )
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(query.id, inst_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=300000)
    except Exception as e:
        logger.error(e)


@dp.message_handler(regexp=r'Достаю последний пост из @[\w.]+ Подождите\.{3}')
@dp.throttled(handle_throttled_query, rate=20)
async def get_instagram_post(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    login = os.environ.get('IG_USERNAME')
    password = os.environ.get('IG_PASSWORD')
    user = re.search(r'из @([\w.]+)\. Подождите\.', message.text)[1]
    ig_post = instagram.get_last_post(login, password, user)
    await bot.send_photo(message.chat.id, *ig_post, disable_notification=True)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.errors_handler(exception=TelegramAPIError)
async def api_errors_handler(update, error):
    # Here we collect all available exceptions from Telegram and write them to log
    # First, we don't want to log BotBlocked exception, so we skip it
    if isinstance(error, BotBlocked):
        return True
    # We collect some info about an exception and write to file
    error_msg = f"Exception of type {type(error)}. Chat ID: {update.message.chat.id}. " \
                f"User ID: {update.message.from_user.id}. Error: {error}"
    logger.error(error_msg)
    return True


@dp.errors_handler(exception=ParsingException)
async def parsing_errors_handler(update, error):
    """
    We collect some info about an exception and write to log
    """
    error_msg = f"Exception of type {type(error)}. Chat ID: {update.message.chat.id}. " \
                f"User ID: {update.message.from_user.id}. Error: {error}"
    await bot.send_message(update.message.chat.id, 'Не могу получить эти данные.\n'
                                                   'Скорее всего, их пока просто нет 😿\n'
                                                   'Попробуйте выбрать другой паркран или клуб.')
    logger.error(error_msg)
    return True


async def setup_bot_commands(dispatcher: Dispatcher):
    """
    Here we setup bot commands to make them visible in Telegram UI
    """
    bot_commands = [
        types.BotCommand(command="/help", description="Справочное сообщение"),
        types.BotCommand(command="/settings", description="Сделать настройки"),
    ]
    await bot.set_my_commands(bot_commands)


# Run after startup
async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await parkrun.update_parkruns_list()
    await parkrun.update_parkruns_clubs()
    await setup_bot_commands(dp)


# Run before shutdown
async def on_shutdown(dp):
    logging.warning("Shutting down..")
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
