import asyncio
import random
import re
from datetime import datetime
import os

import pandas
import pytest

from parkrun import latest

PARKRUN = 'Yoshkar-Ola Alleya Zdorovya'


@pytest.fixture
def yoshka_latest_results():
    return asyncio.run(latest.parse_latest_results(PARKRUN))


def test_parse_latest_results(yoshka_latest_results):
    df, parkrun_date = yoshka_latest_results
    assert isinstance(df, pandas.DataFrame)
    assert isinstance(parkrun_date, str)
    assert isinstance(datetime.strptime(parkrun_date, '%d/%m/%Y'), datetime)


async def test_make_latest_results_diagram(yoshka_latest_results, monkeypatch, tmpdir):
    future = asyncio.Future()
    future.set_result(yoshka_latest_results)
    monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
    pic_path = tmpdir.join('latest_diag.png')
    pic_file = await latest.make_latest_results_diagram(PARKRUN, pic_path)
    pic_file.close()
    assert os.path.exists(pic_path)
    print(pic_path)


async def test_make_latest_results_diagram_personal(yoshka_latest_results, monkeypatch, tmpdir):
    future = asyncio.Future()
    future.set_result(yoshka_latest_results)
    monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
    pic_path = tmpdir.join('latest_diag_personal.png')
    df, _ = yoshka_latest_results
    df.dropna(thresh=3, inplace=True)
    df.reset_index(inplace=True)
    random_name = random.choice(df['Участник'].apply(lambda s: re.search(r'^([^\d]+)\d.*', s)[1]))
    print(random_name)
    pic_file = await latest.make_latest_results_diagram(
        PARKRUN, pic_path, random_name.split()[-1], random.randrange(800)
    )
    pic_file.close()
    assert os.path.exists(pic_path)
    print(pic_path)


async def test_make_latest_results_diagram_noperson(yoshka_latest_results, monkeypatch, tmpdir):
    future = asyncio.Future()
    future.set_result(yoshka_latest_results)
    monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
    pic_path = tmpdir.join('latest_diag_noperson.png')
    with pytest.raises(AttributeError):
        await latest.make_latest_results_diagram(PARKRUN, pic_path, 'no_such_name_athelete', random.randrange(800))


async def test_make_clubs_bar(yoshka_latest_results, monkeypatch, tmpdir):
    future = asyncio.Future()
    future.set_result(yoshka_latest_results)
    monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
    pic_path = tmpdir.join('latest_clubs.png')
    pic_file = await latest.make_clubs_bar(PARKRUN, pic_path)
    pic_file.close()
    assert os.path.exists(pic_path)
    print(pic_path)


async def test_review_table(yoshka_latest_results, monkeypatch):
    future = asyncio.Future()
    future.set_result(yoshka_latest_results)
    monkeypatch.setattr('parkrun.latest.parse_latest_results', lambda *args: future)
    table = await latest.review_table(PARKRUN)
    print(table)
    assert isinstance(table, str)
    assert f'*Паркран {PARKRUN}* состоялся' in table
