import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator

from app import container
from repositories.activity_repository import ActivityRepository
from repositories.result_repository import ResultRepository
from s95.helpers import time_conv


async def parse_latest_results(telegram_id: int):
    activity_repo = container.resolve(ActivityRepository)
    result_repo = container.resolve(ResultRepository)

    last_activity = await activity_repo.find_latest_by_telegram_id(telegram_id)
    if last_activity is None:
        return

    data = await result_repo.find_by_activity_id(last_activity['id'])
    df = pd.DataFrame(data, columns=['Pos', 'Время', 'athlete_id', 'Участник', 'Клуб'])
    df['Время'] = df['Время'].apply(lambda t: time_conv(t))

    return df, last_activity['date'], last_activity['name'], last_activity['athlete_id']


async def make_latest_results_diagram(telegram_id: int, pic: str, turn=0):
    result = await parse_latest_results(telegram_id)
    if result is None:
        return None

    df, activity_date, event_name, athlete_id = result
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


if __name__ == '__main__':
    from dotenv import load_dotenv
    import asyncio
    import os

    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    df = loop.run_until_complete(make_latest_results_diagram(444495414, 'test.png', 30))
    print(df)

    loop.close()
