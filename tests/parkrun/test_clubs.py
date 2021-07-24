import asyncio
import os
import time
import pytest

from parkrun import clubs

WR_in_Kuzminki = ('kuzminki', '23212')


@pytest.fixture(scope='module')
def club_table():
    time.sleep(3)
    yield asyncio.run(clubs.get_club_table(*WR_in_Kuzminki))


def test_top_active_clubs_diagram(tmpdir):
    pic_path = tmpdir.join('club_diagram.png')
    clubs.top_active_clubs_diagram(pic_path).close()
    assert os.path.exists(pic_path)


async def test_update_parkruns_clubs():
    await clubs.update_parkruns_clubs()


clubs_to_try = [('23212', 'Wake&Run'), ('99999', None), ('21796', '21runners')]


@pytest.mark.parametrize('club_id, expected_club_name', clubs_to_try)
async def test_check_club_as_id(club_id, expected_club_name):
    time.sleep(2)
    club_name = await clubs.check_club_as_id(club_id)
    assert expected_club_name == club_name


async def test_get_club_fans(monkeypatch, club_table):
    future = asyncio.Future()
    future.set_result(club_table)
    monkeypatch.setattr('parkrun.clubs.get_club_table', lambda *args: future)
    message = await clubs.get_club_fans(*WR_in_Kuzminki)
    print(message)
    assert isinstance(message, str)
    assert 'Наибольшее количество забегов _в' in message


async def test_get_club_parkruners(monkeypatch, club_table):
    future = asyncio.Future()
    future.set_result(club_table)
    monkeypatch.setattr('parkrun.clubs.get_club_table', lambda *args: future)
    message = await clubs.get_club_parkruners(*WR_in_Kuzminki)
    print(message)
    assert isinstance(message, str)
    assert 'Рейтинг одноклубников _по количеству паркранов_:' in message


async def test_get_parkrun_club_top_results(monkeypatch, club_table):
    future = asyncio.Future()
    future.set_result(club_table)
    monkeypatch.setattr('parkrun.clubs.get_club_table', lambda *args: future)
    message = await clubs.get_parkrun_club_top_results(*WR_in_Kuzminki)
    print(message)
    assert isinstance(message, str)
    assert f'Самые быстрые одноклубники _на паркране {WR_in_Kuzminki[0]}_:' in message
