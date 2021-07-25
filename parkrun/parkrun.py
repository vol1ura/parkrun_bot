import aiohttp
import pandas as pd
from lxml.html import fromstring

from parkrun.helpers import ParkrunSite


# TODO: добавить вывод предстоящих юбилейных паркранов
def anniversary_parkruns():
    pass


def parse_personal_results(html_page: str):
    df = pd.read_html(html_page)[2]
    df['m'] = df['Время'].transform(lambda t: sum(k * int(p) for k, p in zip([1 / 60, 1, 60], t.split(':')[::-1])))
    return df


async def get_athlete_data(athlete_id):
    athlete_url = f'https://www.parkrun.ru/results/athleteeventresultshistory?athleteNumber={athlete_id}&eventNumber=0'
    async with aiohttp.ClientSession(headers=ParkrunSite().headers) as session:
        async with session.get(athlete_url) as resp:
            html = await resp.text()
    tree = fromstring(html)
    title = tree.xpath('//div[@id="content"]/h2/text()')
    athlete_name = (title[0] if title else '').split('- ')[0].strip()
    return athlete_name, html if athlete_name else ''
