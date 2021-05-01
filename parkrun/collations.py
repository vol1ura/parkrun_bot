import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator

from parkrun import helpers, parkrun
from bot_exceptions import NoCollationRuns


class CollationMaker:
    def __init__(self, athlete_name_1, athlete_page_1, athlete_name_2, athlete_page_2):
        self.__name_1 = athlete_name_1
        self.__name_2 = athlete_name_2
        df1 = parkrun.parse_personal_results(athlete_page_1)
        df2 = parkrun.parse_personal_results(athlete_page_2)

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
                          f"{helpers.min_to_mmss(abs(time_diff))} (мин:сек)."
        return result_message

    def to_excel(self, file_name: str):
        vizavi = f'{self.__name_2}'.split()[0]
        df = self.__df.iloc[:, [0, 1, 3, 4, 6, 9, 10, 12]].copy()
        df.rename(columns={'Место_x': 'Ваше место', 'Время_x': 'Ваше время', 'ЛР?_x': 'Личник?', 'ЛР?_y': 'Личник',
                           'Место_y': f'Место ({vizavi})', 'Время_y': f'Время ({vizavi})'}, inplace=True)
        df.to_excel(file_name, index=False, sheet_name='Сравнение результатов')
        return open(file_name)
