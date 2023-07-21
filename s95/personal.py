import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MultipleLocator, NullLocator

from handlers.helpers import find_user_by, user_results


class PersonalResults:
    def __init__(self, telegram_id):
        self.__telegram_id = telegram_id

    async def _fetch_results(self):
        user = await find_user_by('telegram_id', self.__telegram_id)
        self.__athlete_name = f'{user["first_name"]} {user["last_name"]}'
        self.__df = await user_results(self.__telegram_id)
        df_dates = pd.to_datetime(self.__df['Run Date'])
        self.__df['Год'] = df_dates.dt.year
        self.__df['Месяц'] = df_dates.dt.month_name(locale='ru_RU.UTF-8').str.slice(stop=3)
        self.__months = ['Янв', 'Фев', 'Мар', 'Апр', 'Мая', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

    async def history(self, pic: str):
        await self._fetch_results()
        _, ax = plt.subplots(figsize=(9, 6), dpi=150)
        rundata = \
            self.__df.pivot_table(index='Месяц', columns='Год', values='Time', aggfunc=len, fill_value=0).astype(int)

        for month in self.__months:
            if month not in rundata.index.values:
                rundata.loc[month] = 0
        # sort chronological
        rundata = rundata.reindex(self.__months)
        maxruns = rundata.max().max()
        ticks = np.arange(0, maxruns + 1)
        boundaries = np.arange(-0.5, maxruns + 1.5)

        sns.heatmap(rundata, linewidths=0.4, cmap='Greens',
                    cbar_kws={"ticks": ticks, "boundaries": boundaries, 'label': 'Забегов в месяц'})
        ax.set_title(f'{self.__athlete_name}: история участия в S95', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    async def personal_bests(self, pic: str):
        await self._fetch_results()
        _, ax = plt.subplots(figsize=(9, 6), dpi=150)

        # pivot df into long form and aggregate by fastest time
        rundata = self.__df.pivot_table(index='Месяц', columns='Год', values='m',
                                        aggfunc=np.min, fill_value=np.nan)
        # add rows of zeros for any months missed
        for month in self.__months:
            if month not in rundata.index.values:
                rundata.loc[month] = np.nan
        # sort chronological
        rundata = rundata.reindex(self.__months)

        sns.heatmap(rundata, linewidths=0.4, cmap='hot', cbar_kws={'label': 'Время (минуты)'}, ax=ax)
        ax.set_title(f'{self.__athlete_name}: изменение лучшего результата с годами', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    async def tourism(self, pic: str):
        await self._fetch_results()
        _, ax = plt.subplots(figsize=(9, 6), dpi=150)
        # pivot df into long form and aggregate by fastest time
        rundata = self.__df.pivot_table(index='Месяц', columns='Год', values='Event', fill_value=0,
                                        aggfunc=lambda runs: len(np.unique(runs, return_counts=True)[1]))
        maxuniq = rundata.max().max()

        # add rows of zeros for any months missed
        for month in self.__months:
            if month not in rundata.index.values:
                rundata.loc[month] = np.nan
        # sort chronological
        rundata = rundata.reindex(self.__months)
        cmap = sns.cubehelix_palette(rot=-.5, n_colors=maxuniq + 1)
        ticks = np.arange(0, maxuniq + 1)
        boundaries = np.arange(-0.5, maxuniq + 1.5)
        sns.heatmap(rundata, linewidths=0.4, cmap=cmap,
                    cbar_kws={"ticks": ticks, 'label': 'Количество разных паркранов', "boundaries": boundaries}, ax=ax)
        ax.set_title(f'{self.__athlete_name}: интенсивность паркран-туризма', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    async def last_runs(self, pic: str):
        await self._fetch_results()
        plt.figure(figsize=(7, 9), dpi=150)
        df_last = self.__df.head(10)[::-1].reset_index(drop=True)
        df_last['Run Date'] = pd.to_datetime(df_last['Run Date'])
        ax = df_last.plot(x='Run Date', y='m', lw=2, label='Результат')
        xlabels = df_last['Run Date']
        ax.set_xticks(xlabels)
        ax.set_xticklabels(xlabels.dt.strftime('%d.%m.%Y'), rotation=70)
        ax.minorticks_on()
        ax.grid(which='major', axis='x', lw=0.5)
        ax.grid(which='major', axis='y', lw=1)
        ax.grid(which='minor', axis='y', lw=0.5, ls=':')
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(1 / 6))
        ax.yaxis.tick_right()
        ax.xaxis.set_minor_locator(NullLocator())
        plt.xlabel('Дата забега')
        plt.ylabel('Минуты')
        plt.title(f'{len(df_last)} забегов S95', fontweight='bold')
        plt.tight_layout()
        plt.savefig(pic)
        return open(pic, 'rb')

    async def wins_table(self):
        await self._fetch_results()
        pos_df = pd.crosstab(self.__df['Event'], self.__df['Pos'], margins=True)
        columns = [1, 2, 3, 'All']
        for i in columns:
            if i not in pos_df.columns:
                pos_df[i] = 0
        pos_df = pos_df[columns].sort_values(by=columns, ascending=False)
        total = pos_df.loc['All']
        pos_df.drop('All', axis=0, inplace=True)
        pos_df = pos_df.append(total)
        separator = '-------------+-----+-----+-----+----'
        rows = ['```', 'Забег/Место|  1  |  2  |  3  | ∑ ', separator]
        for row in pos_df.itertuples():
            rows.append(f'{row[0][:12]:<12} | {row[1]:3d} | {row[2]:3d} | {row[3]:3d} | {row[4]:3d}')
        rows += [separator, rows.pop().replace('All  ', 'Итого'), '```']
        return '\n'.join(rows)
