import pytest

from parkrun import helpers


min_to_try = ['17:00', '19:15', '23:30', '23:31', '24:58', '24:59', '25:01', '25:02', '18:45', '18:46', '59:59']


def min_converter(m):
    return sum(k * int(p) for k, p in zip([1 / 60, 1, 60], m.split(':')[::-1]))


@pytest.mark.parametrize('mmss', min_to_try)
def test_min_to_mmss(mmss):
    mins = min_converter(mmss)
    actual_mmss = helpers.min_to_mmss(mins)
    assert isinstance(actual_mmss, str)
    assert actual_mmss == mmss


def test_clubs_dict():
    assert isinstance(helpers.CLUBS, list)
    assert len(helpers.CLUBS) > 0
    assert 'ENGIRUNNERS' in list(map(lambda v: v['name'], helpers.CLUBS))
    for club in helpers.CLUBS:
        isinstance(club, dict)
        assert all(map(lambda key: key in club, ['id', 'name', 'participants', 'runs', 'link']))


def test_parkruns_list():
    assert isinstance(helpers.PARKRUNS, list)
    assert len(helpers.PARKRUNS) > 0


def test_parkrun_site():
    parkrun_site = helpers.ParkrunSite('test_key')
    header = parkrun_site.headers
    assert isinstance(header, dict)
    assert 'User-Agent' in header
