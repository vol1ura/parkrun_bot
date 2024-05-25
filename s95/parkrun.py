import pandas as pd


def parse_personal_results(html_page: str):
    df = pd.read_sql(html_page)
    df['m'] = df['Time'].transform(lambda t: sum(k * int(p) for k, p in zip([1 / 60, 1, 60], t.split(':')[::-1])))
    return df


async def get_athlete_data(athlete_id):
    return 'athlete_name', 'html'
