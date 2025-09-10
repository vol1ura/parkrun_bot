import aiohttp
import random

VK_ALBUM_OWNER_ID = '-212432495'
ALBUMS_ID = ['wall', 303697978]  # id of the best albums for this owner_id


def make_vk_api_url(token: str, method: str, owner_id=VK_ALBUM_OWNER_ID, album_id=None):
    album_param = f'&album_id={album_id}' if album_id else ''
    return f'https://api.vk.ru/method/{method}?owner_id={owner_id}{album_param}&access_token={token}&v=5.130'


async def get_random_photo(token):
    async with aiohttp.ClientSession() as session:
        base_url = make_vk_api_url(token, 'photos.getAlbums')
        async with session.get(base_url) as resp:
            all_albums = await resp.json()
        last_albums = [album['id'] for album in all_albums['response']['items'][:2]]
        album_id = random.choice(ALBUMS_ID + last_albums)
        base_url = make_vk_api_url(token, 'photos.get', album_id=album_id)
        async with session.get(base_url) as resp:
            photos_wall_parkrun_kuzminki = await resp.json()
    random_photo = random.choice(photos_wall_parkrun_kuzminki['response']['items'])
    return sorted(random_photo['sizes'], key=lambda x: -x['height'])[2]['url']


if __name__ == '__main__':
    from dotenv import load_dotenv
    import asyncio
    import os

    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    link = loop.run_until_complete(get_random_photo(os.getenv('VK_SERVICE_TOKEN')))
    print(link)
    loop.close()
