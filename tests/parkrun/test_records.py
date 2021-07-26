import asyncio
import os
import time

import pandas
import pytest

from parkrun import records, helpers


@pytest.fixture(scope='module')
def course_records():
    time.sleep(2)
    return asyncio.run(records.all_parkruns_records())


@pytest.fixture
async def async_patch_df(loop, course_records, monkeypatch):
    future = asyncio.Future()
    future.set_result(course_records)
    monkeypatch.setattr('parkrun.records.all_parkruns_records', lambda: future)


def test_all_parkruns_records(course_records):
    df = course_records
    assert isinstance(df, pandas.DataFrame)
    assert len(df) >= len(helpers.PARKRUNS)


async def test_top_parkruns(async_patch_df):
    tables = await records.top_parkruns()
    assert isinstance(tables, list)
    assert len(tables) == 4
    for message in tables:
        assert isinstance(message, str)
        assert '*10 самых' in message


async def test_top_records_count(tmpdir, async_patch_df):
    pic_path = tmpdir.join('top_records.png')
    pic = await records.top_records_count(pic_path)
    pic.close()
    assert os.path.exists(pic_path)
    print(pic_path)


async def test_update_parkruns_list(async_patch_df):
    await records.update_parkruns_list()
