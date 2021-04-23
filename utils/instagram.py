import re
import time
from datetime import timedelta

from instapi import bind, User


def get_last_post(login, password, profile_name):
    bind(login, password)
    ig_profile = User.from_username(profile_name)
    for f in ig_profile.iter_feeds():
        media_type = f._media_info()['media_type']
        if media_type == 1:
            foto = f._media_info()['image_versions2']
        elif media_type == 8:
            foto = f._media_info()['carousel_media'][0]['image_versions2']
        else:
            continue
        foto_url = sorted(foto['candidates'], key=lambda pic: pic['width'])[0]['url']
        post_url = f"https://www.instagram.com/p/{f._media_info()['code']}"
        message = f._media_info()['caption']['text']
        paragraphs = re.split(r'\n.?\n', message, maxsplit=2)
        message = '\n\n'.join(paragraphs[:min(len(paragraphs), 2)])
        days_ago = timedelta(seconds=time.time() - f._media_info()['taken_at']).days
        how_long_ago = 'СЕГОДНЯ' if days_ago == 0 else 'ДЕНЬ НАЗАД' if days_ago == 1 \
            else f'{days_ago} ДНЯ НАЗАД' if 1 < days_ago < 4 else f'{days_ago} ДНЕЙ НАЗАД' if days_ago < 21 \
            else f'{days_ago} Д. НАЗАД'
        return foto_url, f"📌 @{profile_name} ⏳{how_long_ago}\n{message}\n➡Весь пост: {post_url}"


if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    USERNAME = os.environ.get('IG_USERNAME')
    PASSWD = os.environ.get('IG_PASSWORD')

    print(get_last_post(USERNAME, PASSWD, 'begovoy.monastyr'))
