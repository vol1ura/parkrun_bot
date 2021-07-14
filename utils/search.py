# https://cse.google.com/cse/all
import os
import random
import re
import urllib.parse

import aiohttp
from lxml.html import fromstring


async def google(phrase):
    search_phrase = re.sub(r'(?i)бот|\.|,|!', '', phrase).strip()
    params = {
        "q": f"{search_phrase}",
        "key": f"{os.environ.get('GOOGLE_API_KEY')}",
        "cx": f"{os.environ.get('GOOGLE_CX')}"
    }
    values_url = urllib.parse.urlencode(params)
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.googleapis.com/customsearch/v1?' + values_url) as resp:
            result = await resp.json()
    try:
        res1 = random.choice(result['items'])['htmlSnippet']
    except KeyError:  # pragma: no cover
        return ''
    res2 = re.sub(r'(?im)<b>|</b>|\.\.\.|<br>|&nbsp;|&quot;|\n', '', res1)
    res3 = re.sub(r'Марафорум - форум о любительском беге, тренировках,( соревнованиях.)?', '', res2, re.MULTILINE)
    res4 = re.sub(r' Сейчас этот раздел просматривают:.*', '.', res3, re.MULTILINE)
    res5 = re.sub(r'\d\d \w+ \d{2,4}', '', res4)
    res6 = re.sub(r'Сообщение Добавлено: \w{,2} \d{,2} \w+ \d{2,4}, \d\d:\d\d', '', res5)
    res7 = re.sub(r'Марафорум|» Соревнования|» Кроссы, трейлы\.|Часовой пояс:|UTC\.|Кто сейчас на форуме\.*', '', res6)
    res8 = re.sub(r'Последний раз редактировалось .*, \d\d:\d\d, всего', '', res7)
    return [re.sub(r'[.!?] [\w ]+$', '.', res8.strip(), re.MULTILINE)]


async def bashim(phrase):
    search_phrase = re.sub(r'(?i)\bбот\b|\.|,|!|\?', '', phrase).strip()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://bash.im/search?text={search_phrase}') as resp:
            html = await resp.text()
    tree = fromstring(html)
    cites = tree.xpath('//article/div/div')
    if cites:
        for cite in cites:
            cite = re.split(r'[\w. ]+?:', re.sub(r'\n', '', cite.text_content()))
            [cite.remove(s) for s in list(cite) if s == '']
            print(f'"{cite[0].strip()}",')
    return ''
