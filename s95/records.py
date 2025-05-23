import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from s95.helpers import ParkrunSite


async def all_parkruns_records():
    html = await ParkrunSite('courserecords').get_html()
    return pd.read_html(html)[0]


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
    plt.title('Участники с наибольшим количеством рекордов\nна различных паркранах', size=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(pic)
    # TODO: Add plt.close() after each plt.savefig() call
    return open(pic, 'rb')
