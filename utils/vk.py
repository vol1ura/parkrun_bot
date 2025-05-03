import aiohttp
import random
import logging
import config

logger = logging.getLogger(__name__)

VK_ALBUM_OWNER_ID = '-212432495'
ALBUMS_ID = ['wall', 285307254]  # id of the best albums for this owner_id


def make_vk_api_url(token: str, method: str, owner_id=VK_ALBUM_OWNER_ID, album_id=None):
    album_param = f'&album_id={album_id}' if album_id else ''
    return f'https://api.vk.com/method/{method}?owner_id={owner_id}{album_param}&access_token={token}&v=5.130'


async def get_random_photo(token):
    async with aiohttp.ClientSession() as session:
        # Получаем список альбомов
        base_url = make_vk_api_url(token, 'photos.getAlbums')
        print(f"Albums URL: {base_url}")
        async with session.get(base_url) as resp:
            all_albums = await resp.json()
            print(f"Albums response: {all_albums}")
        
        # Получаем ID последних альбомов
        last_albums = [album['id'] for album in all_albums['response']['items'][:2]]
        print(f"Last albums: {last_albums}")
        all_albums_list = ALBUMS_ID + last_albums
        print(f"All albums list: {all_albums_list}")
        album_id = random.choice(all_albums_list)
        print(f"Selected album_id: {album_id}")
        
        # Получаем фотографии из выбранного альбома
        base_url = make_vk_api_url(token, 'photos.get', album_id=album_id)
        print(f"Photos URL: {base_url}")
        async with session.get(base_url) as resp:
            photos_response = await resp.json()
            print(f"Photos response: {photos_response}")
        
        # Выбираем случайное фото и возвращаем URL третьей по размеру версии
        if not photos_response.get('response', {}).get('items'):
            logger.error(f"No photos found in album {album_id}")
            return None
            
        random_photo = random.choice(photos_response['response']['items'])
        print(f"Random photo: {random_photo}")
        sorted_sizes = sorted(random_photo['sizes'], key=lambda x: -x['height'])
        print(f"Sorted sizes: {sorted_sizes}")
        
        if len(sorted_sizes) < 3:
            logger.error(f"Photo {random_photo['id']} has less than 3 sizes")
            return sorted_sizes[0]['url'] if sorted_sizes else None
            
        return sorted_sizes[2]['url']


async def post_to_vk(message: str, photo_url: str = None) -> bool:
    """
    Post a message to VK wall with optional photo
    """
    try:
        params = {
            'owner_id': VK_ALBUM_OWNER_ID,
            'message': message,
            'from_group': 1,
            'access_token': config.VK_SERVICE_TOKEN,
            'v': '5.130'
        }
        
        if photo_url:
            params['attachments'] = photo_url
        
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.vk.com/method/wall.post', data=params) as resp:
                result = await resp.json()
                if 'error' in result:
                    logger.error(f'Error posting to VK: {result["error"]}')
                    return False
                return True
    except Exception as e:
        logger.error(f'Error posting to VK: {e}')
        return False


# if __name__ == '__main__':
#     from dotenv import load_dotenv
#     import asyncio
#     import os
#
#     dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
#     if os.path.exists(dotenv_path):
#         load_dotenv(dotenv_path)
#
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     link = loop.run_until_complete(get_random_photo(os.getenv('VK_SERVICE_TOKEN')))
#     print(link)
#     loop.close()
