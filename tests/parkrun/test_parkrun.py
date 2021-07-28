import pandas as pd
from aioresponses import aioresponses

from parkrun import parkrun


async def test_get_athlete_data(athlete_data_1):
    with aioresponses() as mock_resp:
        mock_resp.get(athlete_data_1.url, body=athlete_data_1.html)
        athlete_name, html = await parkrun.get_athlete_data(athlete_data_1.id)
    assert isinstance(athlete_name, str)
    assert athlete_name == athlete_data_1.name
    assert isinstance(html, str)
    assert html


def test_parse_personal_results(athlete_data_1):
    df = parkrun.parse_personal_results(athlete_data_1.html)
    assert isinstance(df, pd.DataFrame)
    assert 'm' in df


def test_anniversary_parkruns():
    assert True
