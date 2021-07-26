import asyncio
from collections import namedtuple

import pytest

from parkrun import helpers

AthletePersonalData = namedtuple('AthletePersonalData', 'id name url html')


@pytest.fixture(scope='module')
def athlete_data_1():
    athlete_id = '925293'
    athlete_name = 'Михаил КУДИНОВ'
    athlete_url = f'https://www.parkrun.ru/results/athleteeventresultshistory?athleteNumber={athlete_id}&eventNumber=0'
    html = asyncio.run(helpers.ParkrunSite('kudinov_mike').get_html(athlete_url))
    return AthletePersonalData(athlete_id, athlete_name, athlete_url, html)


@pytest.fixture(scope='module')
def athlete_data_2():
    athlete_id = '1827227'
    athlete_name = 'Людмила ХОДАКОВА'
    athlete_url = f'https://www.parkrun.ru/results/athleteeventresultshistory?athleteNumber={athlete_id}&eventNumber=0'
    html = asyncio.run(helpers.ParkrunSite('hodakova_luda').get_html(athlete_url))
    return AthletePersonalData(athlete_id, athlete_name, athlete_url, html)
