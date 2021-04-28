import csv
import os
import re
import time

import aiohttp
import matplotlib.pyplot as plt
import pandas as pd
from lxml.html import fromstring
from matplotlib.colors import Normalize, PowerNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, MultipleLocator

from bot_exceptions import ParsingException, NoCollationRuns
from handlers.helper import ParkrunSite, min_to_mmss

__PARKRUNS_FILE = os.path.join(os.path.dirname(__file__), 'all_parkruns.txt')
__CLUBS_FILE = os.path.join(os.path.dirname(__file__), 'all_clubs.csv')

PARKRUNS = []
with open(__PARKRUNS_FILE, 'r', newline='\n') as file:
    for line in file:
        PARKRUNS.append(line.strip())

CLUBS = []
with open(__CLUBS_FILE, 'r', encoding='utf-8') as file:
    fieldnames = ['id', 'name', 'participants', 'runs', 'link']
    reader = csv.DictReader(file, fieldnames=fieldnames)
    for rec in reader:
        CLUBS.append(rec)

CLUBS.append({'id': '24630', 'name': 'ENGIRUNNERS', 'participants': '29', 'runs': '2152',
              'link': 'https://instagram.com/engirunners'})  # NOTE: personal order for D.Petrov


# TODO: добавить вывод предстоящих юбилейных паркранов
def anniversary_parkruns():
    pass


async def get_participants(club_id: str):
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get(f'https://www.parkrun.com/results/consolidatedclub/?clubNum={club_id}') as resp:
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


async def get_club_table(parkrun: str, club_id: str):
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get(f'https://www.parkrun.ru/{parkrun}/results/clubhistory/?clubNum={club_id}') as resp:
            html_club_results = await resp.text()
    try:
        data = pd.read_html(html_club_results)[0]
    except Exception:
        raise ParsingException(f'Parsing club history page id={club_id} for {parkrun} is failed.')
    data.drop(data.columns[[1, 5, 9, 12]], axis=1, inplace=True)
    return data


async def get_club_fans(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[7]], ascending=False).head(10)
    sportsmens = table[table.columns[0]]
    pr_num = table[table.columns[7]]
    message = f'Наибольшее количество забегов _в {parkrun}_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_club_purkruners(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[8]], ascending=False).head(10)
    sportsmens = table[table.columns[0]]
    pr_num = table[table.columns[8]]
    message = 'Рейтинг одноклубников _по количеству паркранов_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, pr_num), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def get_parkrun_club_top_results(parkrun: str, club_id: str):
    data = await get_club_table(parkrun, club_id)
    table = data.sort_values(by=[data.columns[1]]).head(10)
    sportsmens = table[table.columns[0]]
    result = table[table.columns[1]]
    message = f'Самые быстрые одноклубники _на паркране {parkrun}_:\n'
    for i, (name, num) in enumerate(zip(sportsmens, result), 1):
        message += f'{i:>2}.\xa0{name:<20}\xa0*{num:<3}*\n'
    return message.rstrip()


async def all_parkruns_records():
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get('https://www.parkrun.ru/results/courserecords/') as resp:
            html_all_parkruns = await resp.text()
    return pd.read_html(html_all_parkruns)[0]


async def update_parkruns_clubs():
    if os.path.exists(__CLUBS_FILE) and os.path.getmtime(__CLUBS_FILE) + 605000 > time.time():
        print(os.path.getmtime(__CLUBS_FILE), time.time())
        return
    print('request for club list on parkrun.ru')
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get('https://www.parkrun.ru/results/largestclubs/') as resp:
            html = await resp.text()
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
    with open(__CLUBS_FILE, 'w', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'participants', 'runs', 'link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(all_clubs)


async def check_club_as_id(club_id: str):
    club_name = next((c['name'] for c in CLUBS if c['id'] == club_id), None)
    if club_name:
        return club_name
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
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
    except(KeyError, AttributeError):
        return None
    return club_name


def top_active_clubs():
    CLUBS.sort(key=lambda c: -int(c['runs']))
    message = f"*10 активных клубов (по числу пробежек):*\n"
    for i, club in enumerate(CLUBS[:10], 1):
        message += f"{i:>2}.\xa0[{club['name']:<29}]({club['link']})\xa0*{club['runs']:<3}*\n"
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


async def top_parkruns():
    data = await all_parkruns_records()
    tables = []
    for men in [True, False]:
        for asc in [True, False]:
            sex_col = 7 if men else 3
            table = data.sort_values(by=[data.columns[sex_col]], ascending=asc).head(10)
            parkrun = table[table.columns[0]]
            result = table[table.columns[sex_col]]
            message = f"*10 самых {'быстрых' if asc else 'медленных'} паркранов:*\n"
            for i, (name, num) in enumerate(zip(parkrun, result), 1):
                message += f'{i:>2}.\xa0{name:<25}\xa0*{num:<3}*\n'
            tables.append(message.rstrip())
    return tables


async def top_records_count(pic: str):
    """
    Create diagram with man and woman total records count.
    Here function take in account only more then two records.
    Argument is a picture name.
    Result is a file object
    """
    data = await all_parkruns_records()
    rec_men = data[data.columns[6]].value_counts()
    rec_women = data[data.columns[2]].value_counts()
    most_rec_men = rec_men[rec_men > 1]
    most_rec_women = rec_women[rec_women > 1]
    df = pd.concat([most_rec_men, most_rec_women], axis=0).sort_values(ascending=True)
    plt.figure(figsize=(7, 7), dpi=200)
    ax = df.plot(kind='barh', grid=True)
    for ptch, tick in zip(ax.patches, ax.yaxis.get_major_ticks()):
        c = '#2ca02c' if tick.label.get_text() in most_rec_men.index else '#9467bd'
        ptch.set_facecolor(c)

    ax.grid(b=False, which='major', axis='y')
    ax.xaxis.set_major_locator(MaxNLocator(steps=[1, 2], integer=True))
    ax.xaxis.tick_top()
    plt.title('Учасники с наибольшим количеством рекордов\nна различных паркранах', size=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')


async def update_parkruns_list():
    data = await all_parkruns_records()
    with open(__PARKRUNS_FILE, 'w') as f:
        f.write('\n'.join(data[data.columns[0]].values))


async def parse_latest_results(parkrun: str):
    pr = re.sub('[- ]', '', parkrun)
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get(f"https://www.parkrun.ru/{pr}/results/latestresults/") as resp:
            html = await resp.text()
    tree = fromstring(html)
    parkrun_date = tree.xpath('//span[@class="format-date"]/text()')[0]
    try:
        df = pd.read_html(html)[0]
    except Exception:
        raise ParsingException(f'Parsing latest results page for {parkrun} if failed.')
    return df, parkrun_date


async def make_latest_results_diagram(parkrun: str, pic: str, name=None, turn=0):
    parsed_results = await parse_latest_results(parkrun)
    df = parsed_results[0].copy()
    number_runners = len(df)
    df = df.dropna(thresh=3)
    df['Время'] = df['Время'].dropna() \
        .transform(lambda s: re.search(r'^(\d:)?\d\d:\d\d', s)[0]) \
        .transform(lambda mmss: sum(x * int(t) for x, t in zip([1 / 60, 1, 60], mmss.split(':')[::-1])))

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


async def get_athlete_data(athlete_id):
    athlete_url = f'https://www.parkrun.ru/results/athleteeventresultshistory?athleteNumber={athlete_id}&eventNumber=0'
    async with aiohttp.ClientSession(headers=ParkrunSite.headers()) as session:
        async with session.get(athlete_url) as resp:
            html = await resp.text()
    tree = fromstring(html)
    title = tree.xpath('//div[@id="content"]/h2/text()')
    athlete_name = (title[0] if title else '').split('- ')[0].strip()
    return athlete_name, html if athlete_name else ''


def parse_personal_results(html_page: str):
    df = pd.read_html(html_page)[2]
    df['m'] = df['Время'].transform(lambda t: sum(k * int(p) for k, p in zip([1 / 60, 1, 60], t.split(':')[::-1])))
    return df


class CollationMaker:
    def __init__(self, athlete_name_1, athlete_page_1, athlete_name_2, athlete_page_2):
        self.__name_1 = athlete_name_1
        self.__name_2 = athlete_name_2
        df1 = parse_personal_results(athlete_page_1)
        df2 = parse_personal_results(athlete_page_2)

        self.__df = pd.merge(df1, df2, on=['Дата parkrun', 'Паркран'])
        self.__joint_races = len(self.__df)
        if not self.__joint_races:
            raise NoCollationRuns(athlete_name_2)
        self.__wins = self.__df['m_x'] < self.__df['m_y']
        count_wins = pd.value_counts(self.__wins)
        self.__score = f'{count_wins.get(True, 0)}:{count_wins.get(False, 0)}'

    def __color(self):
        return self.__wins.where(self.__wins, '#ff7f0e').where(~self.__wins, '#2ca02c')

    @staticmethod
    def __ll(df):
        return int(min(df['m_x'].min(), df['m_y'].min()))

    @staticmethod
    def __ur(df):
        return int(max(df['m_x'].max(), df['m_y'].max()))

    def bars(self, pic: str):
        fig = plt.figure(figsize=(6, 4.5), dpi=200)
        ax = fig.add_subplot()
        battle_df = self.__df.head(10)

        def label_bars(marks, heights, rects, wins, color):
            for mark, height, rect, win in zip(marks, heights, rects, wins):
                ax.annotate(f'{mark}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, -10 if win else 2),  # 3 points vertical offset.
                            textcoords='offset points',
                            ha='center', va='bottom', size=8, color=color, fontweight='bold')

        xlabels = battle_df['Дата parkrun']
        x = xlabels.index
        ax.set_xticks(x)
        ax.set_xticklabels(xlabels, rotation=70)
        heights0 = battle_df['m_x'].combine(battle_df['m_y'], min)
        heights1 = battle_df['m_x'].combine(battle_df['m_y'], max)

        rects = ax.bar(x, heights1 - heights0, 0.6, bottom=heights0,
                       edgecolor='black', color=self.__color())
        label_bars(battle_df['Время_y'], battle_df['m_y'], rects, ~self.__wins, '#7f7f7f')
        label_bars(battle_df['Время_x'], battle_df['m_x'], rects, self.__wins, 'black')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel(f'Последние {len(battle_df)} паркранов', fontweight='bold')
        ax.set_ylabel('Результат')
        ax.set_ylim(self.__ll(battle_df) - 1, self.__ur(battle_df) + 2)
        ax.set_title(f'Соотношение результатов\nна совместных забегах {self.__score}',
                     size=15, fontweight='bold')
        legend_elements = [Patch(facecolor='#ff7f0e', edgecolor='black', label='Проигрыш'),
                           Patch(facecolor='#2ca02c', edgecolor='black', label='Выигрыш'),
                           Line2D([0], [0], color='black', lw=2, label=self.__name_1.split()[0]),
                           Line2D([0], [0], color='#7f7f7f', lw=2, label=self.__name_2.split()[0])]
        ax.legend(handles=legend_elements)
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def scatter(self, pic: str):
        fig = plt.figure(figsize=(5, 5), dpi=150)
        ax = fig.add_subplot()
        ax.scatter(self.__df['m_x'], self.__df['m_y'], c=self.__color())

        ll_ur = [self.__ll(self.__df), self.__ur(self.__df) + 1]
        plt.plot(ll_ur, ll_ur, color='r', alpha=0.6)

        ax.set_xlabel(self.__name_1, fontweight='bold')
        ax.set_ylabel(self.__name_2, fontweight='bold')
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.set_title(f'Соотношение результатов\nна совместных забегах {self.__score}', size=15, fontweight='bold')
        legend_elements = [Patch(facecolor='#ff7f0e', label='Проигрыш'),
                           Patch(facecolor='#2ca02c', label='Выигрыш')]
        ax.legend(handles=legend_elements)

        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def table(self):
        self.__df['time_diff'] = self.__df['m_x'] - self.__df['m_y']
        battle_df = self.__df.head(10)
        result_message = f'*Последние {len(battle_df)} совместных забегов:*\n' \
                         '#     Дата     | *Время* | Время | Паркран\n'
        for i, row in battle_df.iterrows():
            result_message += f"{i} {row['Дата parkrun']} | {row['Время_x']} | {row['Время_y']} | {row['Паркран']}\n"
        result_message += '---------------------------------------\n'
        result_message += f'*Всего совместных забегов*: {self.__joint_races}\n'
        result_message += f'*Счёт* {self.__name_1.split()[0]}:{self.__name_2.split()[0]} = {self.__score}\n'
        time_diff = self.__df['time_diff'].sum()
        result_message += f"По разнице результатов вы {'выигрываете' if time_diff < 0 else 'проигрываете'} " \
                          f"{min_to_mmss(abs(time_diff))} (мин:сек)."
        return result_message

    def make_csv(self, file_name: str):
        vizavi = f'{self.__name_2}'
        with open(file_name, 'w', encoding='utf-8') as fd:
            fieldnames = ['Дата', 'Паркран', 'Ваше время', vizavi, 'Ваше место', f'Место {vizavi}']
            writer = csv.DictWriter(fd, fieldnames=fieldnames)
            writer.writeheader()
            for _, row in self.__df.iterrows():
                writer.writerow({'Дата': row['Дата parkrun'], 'Паркран': row['Паркран'],
                                 'Ваше время': row['Время_x'], vizavi: row['Время_y'],
                                 'Ваше место': row['Место_x'], f'Место {vizavi}': row['Место_y']})
        return open(file_name)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    # t = loop.run_until_complete(check_club_as_id('24630'))
    # print(t)
    # print(CLUBS)
    # loop.run_until_complete(update_parkruns_clubs())
    # t = loop.run_until_complete(top_active_clubs())
    # mes = most_slow_parkruns()
    # print(t)
    # get_latest_results_diagram()
    # f = loop.run_until_complete(make_clubs_bar('Kolomenskoe', '../utils/results.png'))
    # f = loop.run_until_complete(top_records_count('../utils/results.png'))
    # ff = loop.run_until_complete(make_pic_battle('../utils/battle.png', 875743, 925293))
    # ff = top_active_clubs_diagram('../utils/clubs.png')
    # ff = top_active_clubs_diagram('../utils/clubs.png')
    # ff.close()
    # ff, _ = loop.run_until_complete(get_athlete_data(925293))
    # print(ff)
    # add_volunteers(204, 204)
    # make_clubs_bar('../utils/clubs.png').close()
    # club_id = next((c['id'] for c in CLUBS if c['name'] == 'IQ_Runners1'), None)
    # print(club_id)
