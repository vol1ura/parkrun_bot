import asyncio
import os
from collections import namedtuple

import pytest

from s95 import helpers

AthletePersonalData = namedtuple('AthletePersonalData', 'id name url html')


def get_athlete_data(athlete_id, athlete_name, athlete_key):
    athlete_url = helpers.athlete_all_history_url(athlete_id)
    html = asyncio.run(helpers.ParkrunSite(athlete_key).get_html(athlete_url))
    return AthletePersonalData(athlete_id, athlete_name, athlete_url, html)


@pytest.fixture(scope='module')
def athlete_data_1():
    return get_athlete_data('925293', 'Михаил КУДИНОВ', 'kudinov_mike')


@pytest.fixture(scope='module')
def athlete_data_2():
    return get_athlete_data('1827227', 'Людмила ХОДАКОВА', 'hodakova_luda')


@pytest.fixture
def empty_page():
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'empty_page.html')
    with open(html_file, encoding='utf-8') as f:
        html = f.read()
    return html
