import aiohttp
import pandas as pd
from lxml.html import fromstring

from parkrun import helpers


# TODO: добавить вывод предстоящих юбилейных паркранов
def anniversary_parkruns():
    pass


def parse_personal_results(html_page: str):
    df = pd.read_html(html_page)[2]
    df['m'] = df['Время'].transform(lambda t: sum(k * int(p) for k, p in zip([1 / 60, 1, 60], t.split(':')[::-1])))
    return df


async def get_athlete_data(athlete_id):
    athlete_url = f'https://www.parkrun.ru/results/athleteeventresultshistory?athleteNumber={athlete_id}&eventNumber=0'
    async with aiohttp.ClientSession(headers=helpers.ParkrunSite().headers) as session:
        async with session.get(athlete_url) as resp:
            html = await resp.text()
    tree = fromstring(html)
    title = tree.xpath('//div[@id="content"]/h2/text()')
    athlete_name = (title[0] if title else '').split('- ')[0].strip()
    return athlete_name, html if athlete_name else ''


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
