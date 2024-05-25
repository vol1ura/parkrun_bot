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
