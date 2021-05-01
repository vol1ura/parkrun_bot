import os
import re

from vedis import Vedis

from app import dp, bot, logger
from config import DB_FILE
from handlers.helpers import handle_throttled_query
from utils import content, instagram
from parkrun import clubs, latest, helpers


@dp.message_handler(regexp='⏳ Получение данных об участии...')
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
        data = await clubs.get_participants(club_id)
        await message.answer(data, parse_mode='Markdown', disable_web_page_preview=True)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(regexp='📊 Получение данных')
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
        pic = await latest.make_latest_results_diagram(parkrun_name, 'results.png')
        if os.path.exists("results.png"):
            await bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File results.png not found! Or the picture wasn\'t generated.')

    elif 'о клубах...' in message.text:
        pic = await latest.make_clubs_bar(parkrun_name, 'clubs.png')
        if os.path.exists("clubs.png"):
            await bot.send_photo(message.chat.id, pic)
            pic.close()
        else:
            logger.error('File clubs.png not found! Or the picture wasn\'t generated.')

    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(regexp='⏳ Получение данных о ')
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
        data = await clubs.get_club_fans(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'количестве всех стартов' in message.text:
        data = await clubs.get_club_purkruners(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'рекордах' in message.text:
        data = await clubs.get_parkrun_club_top_results(parkrun_name, club_id)
        await message.answer(data, parse_mode='Markdown')

    elif 'выбранном клубе' in message.text:
        club_rec = [club for club in helpers.CLUBS if club['id'] == club_id]
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
