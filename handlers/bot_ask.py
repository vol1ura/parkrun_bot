import random
import re
from os import getenv

from aiogram import types

from app import bot, language_code, logger, dp
from s95 import latest
from utils import content, vk


@dp.message_handler(regexp=r'(?i)бот[, \w]+?диаграмма( \d+)?$')
async def s95_personal_result(message: types.Message):
    await types.ChatActions.upload_photo()
    telegram_id = message.from_user.id
    try:
        turn = re.search(r'\d+$', message.text)
        turn = int(turn[0]) % 360 if turn else 0
        pic = await latest.make_latest_results_diagram(telegram_id, 'gen_png/results.png', turn)
        await bot.send_photo(message.chat.id, pic)
        if turn == 0:
            await message.answer(content.t(language_code(message), 'how_to_rotate_labels'), disable_notification=True)
        pic.close()
    except Exception as e:
        logger.warning(f'Attempt to generate personal diagram failed. Query: {message.text}. Error: {e}')
        await message.reply('Что-то пошло не так.')


@dp.message_handler(regexp=r'(?i)бот,? (кузьминки|s95)')
async def get_parkrun_picture(message: types.Message):
    token = getenv('VK_SERVICE_TOKEN')
    photo_url = await vk.get_random_photo(token)
    await bot.send_photo(message.chat.id, photo_url, disable_notification=True)


@dp.message_handler(lambda mes: mes.reply_to_message and mes.reply_to_message.from_user.is_bot)
@dp.message_handler(regexp=r'(?i)^бот\b', content_types=['text'])
async def simple_answers(message: types.Message):
    locale = language_code(message)
    if 'как' in message.text and re.search(r'\bдела\b|жизнь|\bсам\b|поживаешь', message.text, re.I):
        ans = content.t(locale, 'phrases_about_myself')
    elif re.search(r'привет|\bhi\b|hello|здравствуй', message.text, re.I):
        user = message.from_user.first_name
        ans = [s.format(user) for s in content.t(locale, 'greetings')]
    elif 'погода' in message.text:
        bot_info = await bot.get_me()
        ans = ['Информацию о погоде можно получить через inline запрос: '
               f'в строке сообщений наберите "@{bot_info.username} погода".'
               'Либо, набрав сообщение, "Бот, погода Населённый пункт", '
               'например, "Бот, погода Кузьминки Москва".']
    else:
        ans = content.phrases_about_running

    if ans:
        await message.reply(random.choice(ans), disable_web_page_preview=True)
