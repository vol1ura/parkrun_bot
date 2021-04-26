import random
import re
from os import getenv

from aiogram import types
from geopy import Nominatim
from vedis import Vedis

from app import bot, logger, handle_throttled_query, dp
from config import DB_FILE
from utils import content, fucomp, search, vk, parkrun, weather


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
    token = getenv('VK_SERVICE_TOKEN')
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

