from datetime import date

import pytest

from s95 import helpers


min_to_try = ['17:00', '19:15', '23:30', '23:31', '24:58', '24:59', '25:01', '25:02', '18:45', '18:46', '59:59']


def min_converter(m):
    return sum(k * int(p) for k, p in zip([1 / 60, 1, 60], m.split(':')[::-1]))


@pytest.mark.parametrize('mmss', min_to_try)
def test_min_to_mmss(mmss):
    mins = min_converter(mmss)
    actual_mmss = helpers.min_to_mmss(mins)
    assert isinstance(actual_mmss, str)
    assert actual_mmss == mmss
    assert helpers.min_to_mmss(mins - 10**(-8)) == mmss
    assert helpers.min_to_mmss(mins + 10**(-8)) == mmss


# def test_clubs_dict():
#     assert isinstance(helpers.CLUBS, list)
#     assert len(helpers.CLUBS) > 0
#     assert 'ENGIRUNNERS' in list(map(lambda v: v['name'], helpers.CLUBS))
#     for club in helpers.CLUBS:
#         isinstance(club, dict)
#         assert all(map(lambda key: key in club, ['id', 'name', 'participants', 'runs', 'link']))


# def test_parkruns_list():
#     assert isinstance(helpers.PARKRUNS, list)
#     assert len(helpers.PARKRUNS) > 0


def test_parkrun_site():
    parkrun_site = helpers.ParkrunSite('test_key')
    header = parkrun_site.headers
    assert isinstance(header, dict)
    assert 'User-Agent' in header


dates_to_try = [
    ('2021-07-24', '2021-07-24', True), ('2021-07-24', '2021-07-25', False),
    ('2021-07-23', '2021-07-23', True), ('2021-07-25', '2021-07-25', True),
    ('2021-07-20', '2021-07-23', True), ('2021-07-19', '2021-07-24', True),
    ('2021-07-16', '2021-07-24', False), ('2021-07-12', '2021-07-25', False),
    ('2021-07-17', '2021-07-24', False), ('2021-07-17', '2021-07-25', False),
    ('2021-07-09', '2021-07-23', False), ('2021-05-29', '2021-07-24', False),
    ('2020-10-24', '2021-07-20', False), ('2020-10-24', '2021-01-01', False),
    ('2021-07-17', '2021-07-20', False), ('2021-06-26', '2021-07-24', False),
    ('', '2021-07-24', False), (None, '2021-07-20', False)
]


@pytest.mark.parametrize('content_date, request_date, result', dates_to_try)
def test_date_comparison(content_date, request_date, result):
    h = helpers.ParkrunSite._compare_dates(content_date, date.fromisoformat(request_date))
    assert result == h


def test_read_parkruns(tmpdir):
    file = tmpdir.join('all_parkruns.txt')
    expected_values = ['test1', 'test2', 'test3']
    file.write('\n'.join(expected_values))
    actual_values = helpers.read_parkruns(file)
    assert isinstance(actual_values, list)
    assert expected_values == actual_values


def test_read_parkruns_no_file():
    actual_values = helpers.read_parkruns('no_such_file.txt')
    assert isinstance(actual_values, list)
    assert [] == actual_values


def test_read_clubs(tmpdir):
    file = tmpdir.join('top_clubs.csv')
    file.write('1,2,3,4,5\na,b,c,d,e')
    actual_values = helpers.read_clubs(file)
    assert isinstance(actual_values, list)
    assert len(actual_values) == 2
    for item in actual_values:
        assert isinstance(item, dict)
        assert list(item.keys()) == ['id', 'name', 'participants', 'runs', 'link']


def test_read_clubs_no_file():
    actual_values = helpers.read_clubs('no_such_file.txt')
    assert isinstance(actual_values, list)
    assert [] == actual_values
