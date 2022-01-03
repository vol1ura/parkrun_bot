import csv
import os
import re
import time
from datetime import date, timedelta

import aiohttp
import matplotlib.pyplot as plt
import pandas as pd
from lxml.html import fromstring

from bot_exceptions import ParsingException
from parkrun.helpers import ParkrunSite, CLUBS_FILE, CLUBS


async def update_parkruns_clubs():
    if os.path.exists(CLUBS_FILE) and os.path.getmtime(CLUBS_FILE) + 605000 > time.time():
        return
    html = await ParkrunSite('largestclubs').get_html()
    tree = fromstring(html)
    rows = tree.xpath('//*[@id="results"]/tbody/tr')
    all_clubs = []
    for row in rows:
        cells = row.xpath('.//td')
        id_url = cells[0].xpath('.//a/@href')[0]
        site_cell = cells[4].xpath('.//a/@href')
        link = site_cell[0] if site_cell else f'https://www.parkrun.ru/groups/{id_url}/'
        all_clubs.append({
            'id': id_url.replace('#featureClub=', ''),
            'name': cells[0].text_content(),
            'participants': cells[2].text_content(),
            'runs': cells[3].text_content(),
            'link': link
        })
    with open(CLUBS_FILE, 'w', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'participants', 'runs', 'link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(all_clubs)


async def check_club_as_id(club_id: str):
    club_name = next((c['name'] for c in CLUBS if c['id'] == club_id), None)
    if club_name:
        return club_name
    async with aiohttp.ClientSession(headers=ParkrunSite().headers) as session:
        async with session.get(f'https://www.parkrun.ru/groups/{club_id}/') as resp:
            html = await resp.text()
    tree = fromstring(html)
    notice = tree.xpath('//*[@id="content"]/div/p[@class="notice"]')
    if notice:
        return None
    try:
        club_name = tree.xpath('//*[@id="content"]/div/h1')[0].text_content()
        CLUBS.append({
            'id': club_id,
            'name': club_name,
            'participants': tree.xpath('//*[@id="content"]/div/p[2]')[0].text_content().split()[0],
            'runs': tree.xpath('//*[@id="content"]/div/p[3]')[0].text_content().split()[-1],
            'link': tree.xpath('//*[@id="content"]/div/ul/li[2]/a')[0].attrib['href']
        })
    except(KeyError, IndexError):
        return None
    return club_name


async def get_participants(club_id: str):
    async with aiohttp.ClientSession(headers=ParkrunSite().headers) as session:
        async with session.get(f'https://www.parkrun.com/results/consolidatedclub/?clubNum={club_id}') as resp:
            html = await resp.text()
    tree = fromstring(html)
    head = tree.xpath('//div[@class="floatleft"]/p')[0].text_content()
    data = re.search(r'(\d{4}-\d{2}-\d{2}). Of a total (\d+) members', head)
    info_date = date.fromisoformat(data.group(1))
    message = add_relevance_notification(info_date)
    places = tree.xpath('//div[@class="floatleft"]/h2')
    results_tables = tree.xpath('//table[contains(@id, "results")]')
    counts = [len(table.xpath('.//tr/td[4]//a')) for table in results_tables]
    links_to_results = tree.xpath('//div[@class="floatleft"]/p/a/@href')[1:-1]
    message += f'Паркраны, где побывали одноклубники {data.group(1)}:\n'

    for i, (p, l, count) in enumerate(zip(places, links_to_results, counts), 1):
        p_num = re.search(r'runSeqNumber=(\d+)', l).group(1)
        message += f"{i}. [{re.sub('parkrun', '', p.text_content()).strip()}\xa0№{p_num}]({l}) ({count}\xa0чел.)\n"
    message += f'\nУчаствовало {sum(counts)} из {data.group(2)} чел.'
    return message


def add_relevance_notification(content_date: date) -> str:
    notification = 'Извините, но результаты в системе parkrun ещё не обновились 😿 ' \
                   'Всё, что могу предложить на данный момент - результаты за прошлую неделю.\n'
    return notification if date.today() > content_date + timedelta(6) else ''


async def get_club_table(parkrun: str, club_id: str):
    async with aiohttp.ClientSession(headers=ParkrunSite().headers) as session:
        async with session.get(f'https://www.parkrun.ru/{parkrun}/results/clubhistory/?clubNum={club_id}') as resp:
            html_club_results = await resp.text()
            if 'Случилось странное' in html_club_results:
                raise ParsingException(f'Something strange happend on club id={club_id} history page for {parkrun}.')
    try:
        data = pd.read_html(html_club_results)[0]
    except Exception:
        raise ParsingException(f'Parsing club history page id={club_id} for {parkrun} is failed.')
    data.drop(data.columns[[1, 5, 9, 12]], axis=1, inplace=True)
    return data


async def get_club_fans(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[7]], ascending=False).head(10)
    sportsman = table[table.columns[0]]
    pr_num = table[table.columns[7]]
    message = f'Наибольшее количество забегов _в {parkrun}_:\n'
    for i, (name, num) in enumerate(zip(sportsman, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_club_parkruners(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[8]], ascending=False).head(10)
    sportsman = table[table.columns[0]]
    pr_num = table[table.columns[8]]
    message = 'Рейтинг одноклубников _по количеству паркранов_:\n'
    for i, (name, num) in enumerate(zip(sportsman, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_parkrun_club_top_results(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[1]]).head(10)
    sportsman = table[table.columns[0]]
    result = table[table.columns[1]]
    message = f'Самые быстрые одноклубники _на паркране {parkrun}_:\n'
    for i, (name, num) in enumerate(zip(sportsman, result), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


def top_active_clubs_diagram(pic: str):
    df = pd.DataFrame(CLUBS)
    df['runs'] = df['runs'].apply(int)
    df = df.sort_values(by=['runs'], ascending=False).head(10)
    clubs = df['name']
    vals = df['runs'].values
    fig = plt.figure(figsize=(6, 6), dpi=200)
    ax = fig.add_subplot()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#8c564b',
              '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#17ceaf']
    plt.xticks(rotation=70)
    plt.bar(clubs, height=vals, color=colors)
    for p, label, mark in zip(ax.patches, vals, clubs.values):
        if mark == 'Wake&Run':
            p.set_facecolor('#9467bd')
        ax.annotate(label, (p.get_x() + 0.05, p.get_height() + 10), color='gray')
    plt.title('10 активных клубов (по числу пробежек)', fontweight='bold')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')
