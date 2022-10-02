import asyncio
import os
import time

import pandas
import pytest

from s95 import records, helpers


@pytest.fixture(scope='module')
def course_records():
    time.sleep(2.5)
    return asyncio.run(records.all_parkruns_records())


@pytest.fixture
async def mock_parkrun_records(course_records, monkeypatch):
    future = asyncio.Future()
    future.set_result(course_records)
    monkeypatch.setattr('parkrun.records.all_parkruns_records', lambda: future)


def test_all_parkruns_records(course_records):
    df = course_records
    assert isinstance(df, pandas.DataFrame)
    assert len(df) >= len(helpers.PARKRUNS)


async def test_top_parkruns(mock_parkrun_records):
    tables = await records.top_parkruns()
    assert isinstance(tables, list)
    assert len(tables) == 4
    for message in tables:
        assert isinstance(message, str)
        assert '*10 самых' in message


async def test_top_records_count(tmpdir, mock_parkrun_records):
    pic_path = tmpdir.join('top_records.png')
    pic = await records.top_records_count(pic_path)
    pic.close()
    assert os.path.exists(pic_path)
    print(pic_path)
