import os
import re

import aiohttp
import matplotlib.pyplot as plt
import pandas as pd
from lxml.html import fromstring
from matplotlib.colors import Normalize, PowerNorm
from matplotlib.ticker import MaxNLocator

PARKRUN_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"}

club_link = '[Установи в профиле клуб Wake&Run, перейдя по ссылке](https://www.parkrun.com/profile/groups#id=23212&q=Wake%26Run)'


with open(os.path.join(os.path.dirname(__file__), 'all_parkruns.txt'), 'r') as f:
    PARKRUNS = f.readlines()


# TODO: добавить вывод предстоящих юбилейных паркранов
def anniversary_parkruns():
    pass


async def add_volunteers(start, stop, session):
    url = 'https://www.parkrun.ru/kuzminki/results/weeklyresults/?runSeqNumber='
    parkrun_number = start
    while parkrun_number <= stop:
        async with session.get(url + str(parkrun_number)) as resp:
            html = await resp.text()
        tree = fromstring(html)
        volunteers = tree.xpath('//*[@class="paddedt left"]/p[1]/a')
        with open('static/kuzminki_full_stat.txt', 'a') as f:
            for volunteer in volunteers:
                volunteer_name = volunteer.text_content()
                volunteer_id = re.search(r'\d+', volunteer.attrib['href'])[0]
                f.write(f'kuzminki\t{parkrun_number}\tA{volunteer_id} {volunteer_name}\n')
        parkrun_number += 1


async def get_volunteers():
    url = f'https://www.parkrun.ru/kuzminki/results/latestresults/'
    session = aiohttp.ClientSession(headers=PARKRUN_HEADERS)
    async with session.get(url) as resp:
        html = await resp.text()
    tree = fromstring(html)
    parkrun_number = int(tree.xpath('//div[@class="Results"]/div/h3/span[3]/text()')[0][1:])
    with open('static/kuzminki_full_stat.txt', 'r') as f:
        all_stat = f.readlines()
    last_parkrun_db = int(all_stat[-2].split()[1])
    if last_parkrun_db < parkrun_number:
        await add_volunteers(last_parkrun_db + 1, parkrun_number, session)
        with open('static/kuzminki_full_stat.txt', 'r') as f:
            all_stat = f.readlines()
    await session.close()
    volunteers = {}
    for line in all_stat:
        name = line.split(maxsplit=3)[-1].strip()
        volunteers[name] = volunteers.setdefault(name, 0) + 1

    top_volunteers = sorted(volunteers.items(), key=lambda v: v[1], reverse=True)[:10]
    result = '*Toп 10 волонтёров parkrun Kuzminki*\n'
    for i, volunteer in enumerate(top_volunteers, 1):
        result += f'{i}. {volunteer[0]} | {volunteer[1]}\n'
    return result.strip()


async def get_participants():
    async with aiohttp.ClientSession(headers=PARKRUN_HEADERS) as session:
        async with session.get('https://www.parkrun.com/results/consolidatedclub/?clubNum=23212') as resp:
            html = await resp.text()
    tree = fromstring(html)
    head = tree.xpath('//div[@class="floatleft"]/p')[0].text_content()
    data = re.search(r'(\d{4}-\d{2}-\d{2}). Of a total (\d+) members, (\d+) took part', head)
    places = tree.xpath('//div[@class="floatleft"]/h2')
    links_to_results = tree.xpath('//div[@class="floatleft"]/p/a/@href')[1:-1]
    message = f'Паркраны, где побывали наши одноклубники {data.group(1)}:\n'
    for i, (p, l) in enumerate(zip(places, links_to_results), 1):
        p_num = re.search(r'runSeqNumber=(\d+)', l).group(1)
        message += f"{i}. [{re.sub('parkrun', '', p.text_content()).strip()}\xa0№{p_num}]({l})\n"
    message += f'\nУчаствовало {data.group(3)} из {data.group(2)} чел.'
    return message


async def get_club_table():
    async with aiohttp.ClientSession(headers=PARKRUN_HEADERS) as session:
        async with session.get('https://www.parkrun.ru/kuzminki/results/clubhistory/?clubNum=23212') as resp:
            html_club_results = await resp.text()
    data = pd.read_html(html_club_results)[0]
    data.drop(data.columns[[1, 5, 9, 12]], axis=1, inplace=True)
    return data


async def get_kuzminki_fans():
    data = await get_club_table()
    table = data.sort_values(by=[data.columns[7]], ascending=False).reset_index(drop=True).head(10)
    sportsmens = table[table.columns[0]]
    pr_num = table[table.columns[7]]
    message = 'Наибольшее количество забегов _в Кузьминках_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_wr_purkruners():
    data = await get_club_table()
    table = data.sort_values(by=[data.columns[8]], ascending=False).reset_index(drop=True).head(10)
    sportsmens = table[table.columns[0]]
    pr_num = table[table.columns[8]]
    message = 'Рейтинг одноклубников _по количеству паркранов_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_kuzminki_top_results():
    data = await get_club_table()
    table = data.sort_values(by=[data.columns[1]]).reset_index(drop=True).head(10)
    sportsmens = table[table.columns[0]]
    result = table[table.columns[1]]
    message = 'Самые быстрые одноклубники _на паркране Кузьминки_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, result), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def all_parkruns_records():
    async with aiohttp.ClientSession(headers=PARKRUN_HEADERS) as session:
        async with session.get('https://www.parkrun.ru/results/courserecords/') as resp:
            html_all_parkruns = await resp.text()
    return pd.read_html(html_all_parkruns)[0]


async def top_parkruns(asc=True, men=True):
    data = await all_parkruns_records()
    sex_col = 7 if men else 3
    table = data.sort_values(by=[data.columns[sex_col]], ascending=asc).reset_index(drop=True).head(10)
    parkrun = table[table.columns[0]]
    result = table[table.columns[sex_col]]
    message = f"*10 самых {'быстрых' if asc else 'медленных'} паркранов:*\n"
    for i, (name, num) in enumerate(zip(parkrun, result), 1):
        message += f'{i:>2}.\xa0{name:<25}\xa0*{num:<3}*\n'
    return message.rstrip()


async def top_records_count(men=True):
    data = await all_parkruns_records()
    sex_col = 6 if men else 2
    most_recods = data[data.columns[sex_col]].value_counts()
    most_recods = most_recods[most_recods > 1]
    names = most_recods.index
    vals = most_recods.values
    message = f"*{'Мужчины' if men else 'Женщины'} с наибольшим количеством рекордов на разных паркранах:*\n"
    for i, (name, val) in enumerate(zip(names, vals), 1):
        message += f'{i:>2}.\xa0{name:<25}\xa0*{val:<2}*\n'
    return message.rstrip()


async def update_parkruns_list():
    data = await all_parkruns_records()
    with open(os.path.join(os.path.dirname(__file__), 'all_parkruns.txt'), 'w') as f:
        f.write('\n'.join(data[data.columns[0]].values))


async def parse_latest_results(parkrun: str):
    pr = re.sub('[- ]', '', parkrun)
    async with aiohttp.ClientSession(headers=PARKRUN_HEADERS) as session:
        async with session.get(f"https://www.parkrun.ru/{pr}/results/latestresults/") as resp:
            html = await resp.text()
    tree = fromstring(html)
    parkrun_date = tree.xpath('//span[@class="format-date"]/text()')[0]
    df = pd.read_html(html)[0]
    return df, parkrun_date


async def make_latest_results_diagram(parkrun: str, pic: str, name=None, turn=0):
    parsed_results = await parse_latest_results(parkrun)
    df = parsed_results[0].copy()
    number_runners = len(df)
    df = df.dropna(thresh=3)
    df['Время'] = df['Время'].dropna() \
        .transform(lambda s: re.search(r'^(\d:)?\d\d:\d\d', s)[0]) \
        .transform(lambda time: sum(x * int(t) for x, t in zip([1 / 60, 1, 60], time.split(':')[::-1])))

    plt.figure(figsize=(5.5, 4), dpi=300)
    ax = df['Время'].hist(bins=32)
    ptchs = ax.patches
    med = df['Время'].median()
    m_height = 0
    personal_y_mark = 0

    norm = Normalize(0, med)

    if name:
        personal_res = df[df['Участник'].str.contains(name.upper())].reset_index(drop=True)
        if personal_res.empty:
            raise AttributeError
        personal_name = re.search(r'([^\d]+)\d.*', personal_res["Участник"][0])[1]
        personal_name = ' '.join(n.capitalize() for n in personal_name.split())
        personal_time = personal_res['Время'][0]
    else:
        personal_time = 0
        personal_name = ''

    for ptch in ptchs:
        ptch_x = ptch.get_x()
        color = plt.cm.viridis(norm(med - abs(med - ptch_x)))
        ptch.set_facecolor(color)
        if ptch_x <= med:
            m_height = ptch.get_height() + 0.3
        if ptch_x <= personal_time:
            personal_y_mark = ptch.get_height() + 0.3

    med_message = f'Медиана {int(med)}:{(med - int(med)) * 60:02.0f}'
    ax.annotate(med_message, (med - 0.5, m_height + 0.1), rotation=turn)
    plt.plot([med, med], [0, m_height], 'b')

    ldr_time = ptchs[0].get_x()
    ldr_y_mark = ptchs[0].get_height() + 0.3
    ldr_message = f'Лидер {int(ldr_time)}:{(ldr_time - int(ldr_time)) * 60:02.0f}'
    ax.annotate(ldr_message, (ldr_time - 0.5, ldr_y_mark + 0.2), rotation=90)
    plt.plot([ldr_time, ldr_time], [0, ldr_y_mark], 'r')

    lst_time = ptchs[-1].get_x() + ptchs[-1].get_width()
    lst_y_mark = ptchs[-1].get_height() + 0.3
    ax.annotate(f'Всего\nучастников {number_runners}', (lst_time - 0.6, lst_y_mark + 0.1), rotation=90)
    plt.plot([lst_time, lst_time], [0, lst_y_mark], 'r')

    if name and personal_time:
        ax.annotate(f'{personal_name}\n{int(personal_time)}:{(personal_time - int(personal_time)) * 60:02.0f}',
                    (personal_time - 0.5, personal_y_mark + 0.2),
                    rotation=turn, color='red', size=12, fontweight='bold')
        plt.plot([personal_time, personal_time], [0, personal_y_mark], 'r')

    ax.xaxis.set_major_locator(MaxNLocator(steps=[2, 4, 5], integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(steps=[1, 2], integer=True))
    ax.set_xlabel("Результаты участников (минуты)")
    ax.set_ylabel("Результатов в диапазоне")
    plt.title(f'Результаты паркрана {parkrun} {parsed_results[1]}', size=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')


async def make_clubs_bar(parkrun: str, pic: str):
    parsed_results = await parse_latest_results(parkrun)
    df = parsed_results[0].copy()
    df = df.dropna(thresh=3)

    clubs = df['Клуб'].value_counts()
    norm = PowerNorm(gamma=0.6)
    colors = plt.cm.cool(norm(clubs.values))
    fig = plt.figure(figsize=(6, 6), dpi=200)
    ax = fig.add_subplot()
    ax.grid(False, axis='x')
    ax.grid(True, axis='y')
    ax.yaxis.set_major_locator(MaxNLocator(steps=[1, 2, 4, 8], integer=True))
    plt.xticks(rotation=80, size=8)
    plt.bar(clubs.index, clubs.values, color=colors)
    plt.title(f'Клубы на паркране {parkrun} {parsed_results[1]}', size=10, fontweight='bold')
    plt.ylabel('Количество участников')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    t = loop.run_until_complete(get_parkruns_list())
    # mes = most_slow_parkruns()
    print(t, type(t), t[1])
    # get_latest_results_diagram()
    # f = loop.run_until_complete(make_clubs_bar('Kolomenskoe', '../utils/results.png'))
    # f.close()
    # add_volunteers(204, 204)
    # make_clubs_bar('../utils/clubs.png').close()
