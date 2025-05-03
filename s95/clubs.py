import matplotlib.pyplot as plt
import pandas as pd
import logging
from typing import Optional, Dict, Any

from app import db

logger = logging.getLogger(__name__)


async def get_club(club_id: int) -> Optional[Dict[str, Any]]:
    try:
        club = await db.execute('SELECT * FROM clubs WHERE id = $1', club_id)
        return club
    except Exception as e:
        logger.error(f'Error getting club {club_id}: {e}')
        return None


async def find_club_by_id(club_id: int):
    club = await get_club(club_id)
    return club.name if club else None


async def get_club_table(parkrun: str, club_id: str):
    return {}


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
    df = pd.DataFrame()
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
