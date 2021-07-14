import re
from utils import search


async def test_google():
    message = await search.google('бот, гречка')
    print(message)
    assert isinstance(message, list)
    assert len(message) == 1
    assert not re.match(r'^бот', message[0], re.I)


async def test_bashim():
    message = await search.bashim('короновирус')
    print(message)
    assert isinstance(message, str)
