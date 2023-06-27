import re

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import pandas as pd

from matplotlib.colors import Normalize, PowerNorm
from matplotlib.ticker import MaxNLocator

from app import db_conn
from s95.helpers import min_to_mmss, time_conv


async def parse_latest_results(telegram_id: int):
    conn = await db_conn()
    query = """SELECT activities.id, activities.date, events.name, athletes.id AS athlete_id FROM activities
        INNER JOIN events ON events.id = activities.event_id
        INNER JOIN results ON results.activity_id = activities.id
        INNER JOIN athletes ON athletes.id = results.athlete_id
        INNER JOIN users ON users.id = athletes.user_id
        WHERE users.telegram_id = $1 AND activities.published = TRUE
        ORDER BY activities.date DESC
        LIMIT 1
    """
    last_activity = await conn.fetchrow(query, telegram_id)
    if last_activity is None:
        return
    query = """SELECT position, total_time, athlete_id, athletes.name, clubs.name FROM results
        LEFT OUTER JOIN athletes ON athletes.id = results.athlete_id
        LEFT OUTER JOIN clubs ON clubs.id = athletes.club_id
        WHERE results.activity_id = $1
        ORDER BY results.position ASC
    """
    data = await conn.fetch(query, last_activity['id'])
    await conn.close()
    df = pd.DataFrame(data, columns=['Pos', 'Время', 'athlete_id', 'Участник', 'Клуб'])
    df['Время'] = df['Время'].apply(lambda t: time_conv(t))
    return df, last_activity['date'], last_activity['name'], last_activity['athlete_id']


async def make_latest_results_diagram(telegram_id: int, pic: str, turn=0):
    df, activity_date, event_name, athlete_id = await parse_latest_results(telegram_id)
    number_runners = len(df)
    plt.figure(figsize=(5.5, 4), dpi=300)
    ax = df['Время'].hist(bins=32)
    ptchs = ax.patches
    med = df['Время'].median()
    m_height = 0
    personal_y_mark = 0

    norm = Normalize(0, med)

    personal_res = df.loc[df['athlete_id'] == athlete_id].reset_index(drop=True)
    personal_name = personal_res["Участник"][0]
    personal_time = personal_res['Время'][0]

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

    ldr_time = round(ptchs[0].get_x(), 4)
    ldr_y_mark = ptchs[0].get_height() + 0.3
    ldr_message = f'Лидер {int(ldr_time)}:{(ldr_time - int(ldr_time)) * 60:02.0f}'
    ax.annotate(ldr_message, (ldr_time - 0.5, ldr_y_mark + 0.2), rotation=90, va='bottom')
    plt.plot([ldr_time, ldr_time], [0, ldr_y_mark], 'r')

    lst_time = ptchs[-1].get_x() + ptchs[-1].get_width()
    lst_y_mark = ptchs[-1].get_height() + 0.3
    ax.annotate(f'Всего\nучастников {number_runners}', (lst_time - 0.6, lst_y_mark + 0.1), rotation=90, va='bottom')
    plt.plot([lst_time, lst_time], [0, lst_y_mark], 'r')

    ax.annotate(f'{personal_name}\n{int(personal_time)}:{(personal_time - int(personal_time)) * 60:02.0f}',
                (personal_time - 0.5, personal_y_mark + 0.2),
                rotation=turn, color='red', size=12, fontweight='bold')
    plt.plot([personal_time, personal_time], [0, personal_y_mark], 'r')

    ax.xaxis.set_major_locator(MaxNLocator(steps=[2, 4, 5], integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(steps=[1, 2], integer=True))
    ax.set_xlabel("Результаты участников (минуты)")
    ax.set_ylabel("Результатов в диапазоне")
    plt.title(f'Результаты забега {event_name} {activity_date}', size=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')


async def make_clubs_bar(telegram_id: int, pic: str):
    df, activity_date, event_name, _ = await parse_latest_results(telegram_id)
    fig = plt.figure(figsize=(6, 6), dpi=200)
    ax = fig.add_subplot()
    clubs = df['Клуб'].value_counts()
    if clubs.empty:
        text = fig.text(0.5, 0.5, 'Не было участников из\nзарегистрированных клубов',
                        color='white', ha='center', va='center', size=22)
        text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
    else:
        norm = PowerNorm(gamma=0.6)
        colors = plt.cm.cool(norm(clubs.values))
        ax.grid(False, axis='x')
        ax.grid(True, axis='y')
        ax.yaxis.set_major_locator(MaxNLocator(steps=[1, 2, 4, 8], integer=True))
        plt.xticks(rotation=80, size=8)
        plt.bar(clubs.index, clubs.values, color=colors)
        plt.title(f'Клубы на забеге {event_name} {activity_date}', size=10, fontweight='bold')
        plt.ylabel('Количество участников')
    plt.tight_layout()
    plt.savefig(pic)
    return open(pic, 'rb')


async def review_table(parkrun: str):
    df, parkrun_date = await parse_latest_results(parkrun)
    count_total = len(df)
    if count_total == 0:
        return f'Паркран {parkrun} {parkrun_date} не состоялся.'
    df.dropna(thresh=4, inplace=True)
    df['Позиция м/ж'] = df[df.columns[2]].dropna()\
        .transform(lambda s: int(re.search(r'(?:Мужской|Женский)[ ]+(\d+)', s)[1]))
    df['Участник'] = df['Участник'].transform(lambda s: re.search(r'([^\d]+)\d.*|Неизвестный', s)[1])
    df['Личник'] = df['Время'].dropna().transform(lambda s: re.search(r'(?<=\d\d:\d\d)(.*)', s)[1])
    df['Время'] = df['Время'].dropna().transform(lambda s: re.search(r'^(\d:)?\d\d:\d\d', s)[0])
    df['result_m'] = df['Время']\
        .transform(lambda time: sum(x * int(t) for x, t in zip([1/60, 1, 60], time.split(':')[::-1])))
    pb = df['Личник'][df['Личник'] == 'Новый ЛР!'].count() * 100.0 / count_total
    median = min_to_mmss(df['result_m'].median())
    q95 = min_to_mmss(df['result_m'].quantile(q=0.95))
    q10 = min_to_mmss(df['result_m'].quantile(q=0.1))
    count_w = df['Пол'][df['Пол'].str.contains('Женский')].count()
    count_m = df['Пол'][df['Пол'].str.contains('Мужской')].count()
    count_unknown = count_total - count_m - count_w
    mean_w = min_to_mmss(df[df['Пол'].str.contains('Женский')]['result_m'].mean())
    mean_m = min_to_mmss(df[df['Пол'].str.contains('Мужской')]['result_m'].mean())
    report = f'*Паркран {parkrun}* состоялся {parkrun_date}.\n' \
             f'Всего приняло участие {count_total} человек, среди них {count_m} мужчин, ' \
             f'{count_w} женщин и {count_unknown} неизвестных.\n' \
             f'_Установили личник_: {pb:.1f}% участников.\n' \
             f'_Средний результат_: у мужчин {mean_m}, у женщин {mean_w}.\n' \
             f'_Медианное время_: {median}.\n' \
             f'_Квантили_: 10% - {q10}, 95% - {q95}.\n' \
             '*Результаты лидеров*\n' \
             f'``` # |      Участник      | Время\n'
    for _, row in df[df['Позиция м/ж'] < 4].iterrows():
        report += f"{row['Позиция м/ж']:>2} | {row['Участник']:<18} | {row['Время']}\n"
    return report + '```'


if __name__ == '__main__':
    from dotenv import load_dotenv
    import asyncio
    import os

    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    loop = asyncio.get_event_loop()
    df = loop.run_until_complete(make_latest_results_diagram(444495414, 'test.png', 30))
    print(df)
