import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MultipleLocator, NullLocator

from parkrun import parkrun


class PersonalResults:
    def __init__(self, athlete_name, athlete_page):
        self.athlete_name = athlete_name
        self.df = parkrun.parse_personal_results(athlete_page)
        self.df['Год'] = pd.to_datetime(self.df['Дата parkrun'], dayfirst=True).dt.year
        self.df['Месяц'] = pd.to_datetime(self.df['Дата parkrun'], dayfirst=True) \
            .dt.month_name(locale='ru_RU.UTF-8').str.slice(stop=3)
        self.months = ['Янв', 'Фев', 'Мар', 'Апр', 'Мая', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

    def history(self, pic: str):
        fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
        rundata = self.df.pivot_table(index='Месяц', columns='Год', values='Время', aggfunc=len, fill_value=0) \
            .astype(int)

        for month in self.months:
            if month not in rundata.index.values:
                rundata.loc[month] = 0
        # sort chronological
        rundata = rundata.reindex(self.months)
        maxruns = rundata.max().max()
        ticks = np.arange(0, maxruns + 1)
        boundaries = np.arange(-0.5, maxruns + 1.5)

        sns.heatmap(rundata, linewidths=0.4, cmap='Greens',
                    cbar_kws={"ticks": ticks, "boundaries": boundaries, 'label': 'Паркранов в месяц'})
        ax.set_title(f'{self.athlete_name}: история участия в паркранах', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def personal_bests(self, pic: str):
        fig, ax = plt.subplots(figsize=(9, 6), dpi=150)

        # pivot df into long form and aggregate by fastest time
        rundata = self.df.pivot_table(index='Месяц', columns='Год', values='m',
                                      aggfunc=np.min, fill_value=np.nan)
        # add rows of zeros for any months missed
        for month in self.months:
            if month not in rundata.index.values:
                rundata.loc[month] = np.nan
        # sort chronological
        rundata = rundata.reindex(self.months)

        sns.heatmap(rundata, linewidths=0.4, cmap='hot', cbar_kws={'label': 'Время (минуты)'}, ax=ax)
        ax.set_title(f'{self.athlete_name}: изменение лучшего результата с годами', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def tourism(self, pic: str):
        fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
        # pivot df into long form and aggregate by fastest time
        rundata = self.df.pivot_table(index='Месяц', columns='Год', values='Паркран', fill_value=0,
                                      aggfunc=lambda parkruns: len(np.unique(parkruns, return_counts=True)[1]))
        maxuniq = rundata.max().max()

        # add rows of zeros for any months missed
        for month in self.months:
            if month not in rundata.index.values:
                rundata.loc[month] = np.nan
        # sort chronological
        rundata = rundata.reindex(self.months)
        cmap = sns.cubehelix_palette(rot=-.5, n_colors=maxuniq + 1)
        ticks = np.arange(0, maxuniq + 1)
        boundaries = np.arange(-0.5, maxuniq + 1.5)
        sns.heatmap(rundata, linewidths=0.4, cmap=cmap,
                    cbar_kws={"ticks": ticks, 'label': 'Количество разных паркранов', "boundaries": boundaries}, ax=ax)
        ax.set_title(f'{self.athlete_name}: интенсивность паркран-туризма', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def last_runs(self, pic: str):
        plt.figure(figsize=(7, 9), dpi=150)
        df_last = self.df.head(10)[::-1].reset_index(drop=True)
        ax = df_last.plot(x='Дата parkrun', y='m', lw=2, label='Результат')
        xlabels = df_last['Дата parkrun']
        ax.set_xticks(xlabels.index)
        ax.set_xticklabels(xlabels, rotation=70)
        ax.minorticks_on()
        ax.grid(which='major', axis='x', lw=0.5)
        ax.grid(which='major', axis='y', lw=1)
        ax.grid(which='minor', axis='y', lw=0.5, ls=':')
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(1 / 6))
        ax.yaxis.tick_right()
        ax.xaxis.set_minor_locator(NullLocator())
        plt.xlabel('Дата паркрана')
        plt.ylabel('Минуты')
        plt.title('10 забегов parkrun', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    def wins_table(self):
        pos_df = pd.crosstab(self.df['Паркран'], self.df['Место'], margins=True)
        columns = [1, 2, 3, 'All']
        for i in columns:
            if i not in pos_df.columns:
                pos_df[i] = 0
        pos_df = pos_df[columns].sort_values(by=columns, ascending=False)
        total = pos_df.loc['All']
        pos_df.drop('All', axis=0, inplace=True)
        pos_df = pos_df.append(total)
        separator = '-------------+-----+-----+-----+----'
        rows = ['```', 'Паркран/Место|  1  |  2  |  3  | ∑ ', separator]
        for row in pos_df.itertuples():
            rows.append(f'{row[0][:12]:<12} | {row[1]:3d} | {row[2]:3d} | {row[3]:3d} | {row[4]:3d}')
        rows += [separator, rows.pop().replace('All  ', 'Итого'), '```']
        return '\n'.join(rows)
