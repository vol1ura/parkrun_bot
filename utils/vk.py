import random
import vk_requests


owner_id = -121950041  # group or user id on VK.com
albums_id = ['wall', 256663165]  # id of best albums of this owner_id


def get_random_photo(token):
    api = vk_requests.create_api(service_token=token)
    last_albums = [album['id'] for album in api.photos.getAlbums(owner_id=owner_id)['items'][:2]]
    album_id = random.choice(albums_id + last_albums)
    photos_wall_parkrun_kuzminki = api.photos.get(owner_id=owner_id, album_id=album_id)
    random_photo = random.choice(photos_wall_parkrun_kuzminki['items'])
    return sorted(random_photo['sizes'], key=lambda x: -x['height'])[2]['url']
