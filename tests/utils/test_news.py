import re
from datetime import date, timedelta

import pytest

from utils import news


@pytest.mark.parametrize('test_date', [date.today() + timedelta(30 * d) for d in range(3)])
async def test_get_competitions(test_date):
    competitions = await news.get_competitions(test_date.month, test_date.year)
    print(competitions)
    assert isinstance(competitions, list)
    for competition in competitions:
        assert isinstance(competition, tuple)
        assert isinstance(competition[0], str)
        assert re.fullmatch(r'(\d\d - )?\d\d\.\d\d', competition[1])
        assert isinstance(competition[2], str)
        assert re.match(r'✏️<a href=\"http://probeg\.org/card\.php\?id=\d+\">.*</a>\n'
                        r'🕒.<b>Дата</b>: (\d\d - )?\d\d\.\d\d.| 📌.+ \(\w+\)', competition[2])
