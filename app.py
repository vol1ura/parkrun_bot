import logging
import random
import re

from aiogram import Bot, Dispatcher, types, executor
from geopy.geocoders import Nominatim

import keyboards as kb
from config import *
from utils import content, fucomp, weather, vk, search, parkrun

bot = Bot(TOKEN_BOT)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.answer(content.start_message, disable_notification=True)


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


@dp.message_handler(commands=['parkrun'])
async def process_command_parkrun(message: types.Message):
    await message.reply('Установка параметров', reply_markup=kb.inline_kb_parkrun)


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


# Run after startup
async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await parkrun.update_parkruns_list()


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
