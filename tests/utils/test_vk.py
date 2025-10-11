import os
import re

from utils import vk


async def test_get_random_photo():
    photo_url = await vk.get_random_photo(os.getenv('VK_SERVICE_TOKEN'))
    print(photo_url)
    assert isinstance(photo_url, str)
    assert photo_url.startswith('https://')


def test_make_vk_api_url():
    url = vk.make_vk_api_url('test_token', 'test_method', '-1234567890', '111')
    assert re.fullmatch(r'https://api\.vk\.ru/method/test_method\?owner_id=-1234567890'
                        r'&album_id=111&access_token=test_token&v=5.199', url)
