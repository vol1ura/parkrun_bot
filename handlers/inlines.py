import re
import time

from aiogram import types

from app import logger, bot, dp
from utils import content, weather, news
from parkrun import helpers, records


@dp.inline_handler(lambda query: 'parkrun' in query.query or 'паркран' in query.query)
async def query_all_parkruns(inline_query: types.InlineQuery):
    offset = int(inline_query.offset) if inline_query.offset else 0
    try:
        parkruns_list = helpers.PARKRUNS
        quotes = parkruns_list[offset:]
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        parkruns_menu = [types.InlineQueryResultArticle(
            id=f'{offset + k}', title=p, input_message_content=types.InputTextMessageContent(f'/setparkrun {p}')
        )
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(inline_query.id, parkruns_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=60000)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'clubs' in query.query or 'клуб' in query.query)
async def query_all_clubs(inline_query: types.InlineQuery):
    offset = int(inline_query.offset) if inline_query.offset else 0
    try:
        clubs_list = helpers.CLUBS
        quotes = clubs_list[offset:]
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        clubs_menu = [types.InlineQueryResultArticle(
            id=f'{k + offset}', title=p['name'],
            input_message_content=types.InputTextMessageContent(f"/setclub {p['name']}"))
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(inline_query.id, clubs_menu,
                                      next_offset=m_next_offset if m_next_offset else "", cache_time=0)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'погода' in query.query or 'weather' in query.query)
async def query_weather(inline_query: types.InlineQuery):
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
async def query_air(inline_query: types.InlineQuery):
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
async def query_competitions(inline_query: types.InlineQuery):
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
        await bot.answer_inline_query(inline_query.id, queries, cache_time=400000)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'records' in query.query)
async def display_records_menu(inline_query: types.InlineQuery):
    try:
        records_tables = await records.top_parkruns()
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
async def query_teammates(inline_query: types.InlineQuery):
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
async def query_latestparkrun(inline_query: types.InlineQuery):
    try:
        pattern = '📊 Получение данных '
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
        m3 = types.InlineQueryResultArticle(
            id='3', title='Сводка основных показателей', description='общая статистика и лидеры',
            input_message_content=types.InputTextMessageContent(pattern + 'с общей инфой.', parse_mode='Markdown'),
            thumb_url='https://raw.githubusercontent.com/vol1ura/wr-tg-bot/master/static/pics/3.jpg',
            thumb_width=48, thumb_height=48)
        await bot.answer_inline_query(inline_query.id, [m1, m2, m3], cache_time=0)
    except Exception as e:
        logger.error(e)


@dp.inline_handler(lambda query: 'instagram' in query.query)
async def display_instagram_menu(inline_query: types.InlineQuery):
    offset = int(inline_query.offset) if inline_query.offset else 0
    try:
        quotes = content.instagram_profiles[offset:]
        m_next_offset = str(offset + 15) if len(quotes) >= 15 else None
        inst_menu = [types.InlineQueryResultArticle(
            id=f'{k + offset}', title=f'@{p}',
            input_message_content=types.InputTextMessageContent(f"Достаю последний пост из @{p}. Подождите...")
        )
            for k, p in enumerate(quotes[:15])]
        await bot.answer_inline_query(inline_query.id, inst_menu,
                                      next_offset=m_next_offset if m_next_offset else '', cache_time=300000)
    except Exception as e:
        logger.error(e)
