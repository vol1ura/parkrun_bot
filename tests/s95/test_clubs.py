import asyncio
import datetime
# import os
import time

import pytest

# from bot_exceptions import ParsingException
from s95 import clubs

WR_in_Kuzminki = ('kuzminki', '23212')


@pytest.fixture(scope='module')
def club_table():
    time.sleep(3)
    return asyncio.run(clubs.get_club_table(*WR_in_Kuzminki))


@pytest.fixture
async def async_club_table(monkeypatch, club_table):
    future = asyncio.Future()
    future.set_result(club_table)
    monkeypatch.setattr('parkrun.clubs.get_club_table', lambda *args: future)


# def test_top_active_clubs_diagram(tmpdir):
#     pic_path = tmpdir.join('club_diagram.png')
#     clubs.top_active_clubs_diagram(pic_path).close()
#     assert os.path.exists(pic_path)


# clubs_to_try = [('23212', 'Wake&Run'), ('999999', None), ('21796', '21runners')]


# @pytest.mark.parametrize('club_id, expected_club_name', clubs_to_try)
# async def test_find_club_by_id(club_id, expected_club_name):
#     time.sleep(2)
#     club_name = await clubs.find_club_by_id(club_id)
#     assert expected_club_name == club_name


# @pytest.mark.asyncio
# async def test_find_club_by_id_fail(empty_page, aresponses):
#     club_id = 'failed_id'
#     aresponses.add('www.parkrun.ru', f'/groups/{club_id}/', 'GET', aresponses.Response(text=empty_page))
#     result = await clubs.find_club_by_id(club_id)
#     assert result is None
#     aresponses.assert_plan_strictly_followed()


# async def test_get_club_fans(async_club_table):
#     message = await clubs.get_club_fans(*WR_in_Kuzminki)
#     print(message)
#     assert isinstance(message, str)
#     assert 'Наибольшее количество забегов _в' in message


# async def test_get_club_parkruners(async_club_table):
#     message = await clubs.get_club_parkruners(*WR_in_Kuzminki)
#     print(message)
#     assert isinstance(message, str)
#     assert 'Рейтинг одноклубников _по количеству паркранов_:' in message


# async def test_get_parkrun_club_top_results(async_club_table):
#     message = await clubs.get_parkrun_club_top_results(*WR_in_Kuzminki)
#     print(message)
#     assert isinstance(message, str)
#     assert f'Самые быстрые одноклубники _на паркране {WR_in_Kuzminki[0]}_:' in message


# async def test_get_participants():
#     await asyncio.sleep(2)
#     message = await clubs.get_participants(WR_in_Kuzminki[1])
#     print(message)
#     assert 'Паркраны, где побывали одноклубники' in message


dates_to_try = [
    (datetime.date.today() - datetime.timedelta(7), True), (datetime.date.today() - datetime.timedelta(1), False),
    (datetime.date.today(), False), (datetime.date.today() - datetime.timedelta(3), False)
]


@pytest.mark.parametrize('content_date, presence', dates_to_try)
def test_add_relevance_notification(content_date, presence):
    notification = clubs.add_relevance_notification(content_date)
    condition = 'результаты за прошлую неделю' in notification
    assert condition if presence else not condition


# async def test_get_club_table_fail():
#     await asyncio.sleep(2)
#     club_id, parkrun = '9999999', 'no_such_parkrun'
#     with pytest.raises(ParsingException) as e:
#         await clubs.get_club_table(parkrun, club_id)
#     assert e.value.message == f'Something strange happend on club id={club_id} history page for {parkrun}.'
