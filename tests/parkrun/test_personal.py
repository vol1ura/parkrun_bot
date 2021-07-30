import os

import pytest

from parkrun.personal import PersonalResults


@pytest.fixture(scope='module')
def personal_results(athlete_data_1):
    return PersonalResults(athlete_data_1.name, athlete_data_1.html)


def test_history(personal_results, tmpdir):
    pic_path = tmpdir.join('personal_history.png')
    personal_results.history(pic_path).close()
    assert os.path.exists(pic_path)


def test_personal_bests(personal_results, tmpdir):
    pic_path = tmpdir.join('personal_bests.png')
    personal_results.personal_bests(pic_path)
    assert os.path.exists(pic_path)


def test_tourism(personal_results, tmpdir):
    pic_path = tmpdir.join('personal_tourism.png')
    personal_results.tourism(pic_path)
    assert os.path.exists(pic_path)


def test_last_runs(personal_results, tmpdir):
    pic_path = tmpdir.join('last_runs.png')
    personal_results.last_runs(pic_path)
    assert os.path.exists(pic_path)


def test_wins_table(personal_results):
    table = personal_results.wins_table()
    assert isinstance(table, str)
    assert 'Паркран/Место' in table
