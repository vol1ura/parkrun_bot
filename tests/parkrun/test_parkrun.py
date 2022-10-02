import pandas as pd
import pytest

from s95 import parkrun


@pytest.mark.asyncio
async def test_get_athlete_data(athlete_data_1, aresponses):
    aresponses.add(response=aresponses.Response(text=athlete_data_1.html))
    athlete_name, html = await parkrun.get_athlete_data(athlete_data_1.id)
    assert isinstance(athlete_name, str)
    assert athlete_name == athlete_data_1.name
    assert isinstance(html, str)
    assert html
    aresponses.assert_plan_strictly_followed()


def test_parse_personal_results(athlete_data_1):
    df = parkrun.parse_personal_results(athlete_data_1.html)
    assert isinstance(df, pd.DataFrame)
    assert 'm' in df


def test_anniversary_parkruns():
    # TODO: make feature and tests
    parkrun.anniversary_parkruns()
    assert True
