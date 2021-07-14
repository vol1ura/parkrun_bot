import os
import time

import aiohttp
from lxml.html import fromstring


def compass_direction(degree: int, lan='en') -> str:
    compass_arr = {'ru': ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ",
                          "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ", "С"],
                   'en': ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                          "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]}
    return compass_arr[lan][int((degree % 360) / 22.5 + 0.5)]


async def get_weather(place, lat, lon, lang='ru'):
    weather_api_key = os.environ.get('OWM_TOKEN')
    base_url = f"http://api.openweathermap.org/data/2.5/weather?" \
               f"lat={lat}&lon={lon}&appid={weather_api_key}&units=metric&lang={lang}"
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as resp:
            w = await resp.json()
    wind_dir = compass_direction(w['wind']['deg'], lang)
    sunset = time.strftime("%H:%M", time.localtime(w['sys']['sunset']))
    weather_description = f"🏙 {place}: сейчас {w['weather'][0]['description']}\n" \
                          f"🌡 {w['main']['temp']:.1f}°C, ощущ. как {w['main']['feels_like']:.0f}°C\n" \
                          f"💨 {w['wind']['speed']:.1f}м/с с\xa0{wind_dir}, 💦\xa0{w['main']['humidity']}%\n" \
                          f"🌇 {sunset} "
    return weather_description


async def get_air_quality(place, lat, lon, lang='ru'):
    weather_api_key = os.environ.get('OWM_TOKEN')
    base_url = f"http://api.openweathermap.org/data/2.5/air_pollution?" \
               f"lat={lat}&lon={lon}&appid={weather_api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as resp:
            aq = await resp.json()
    # Air Quality Index: 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor
    aqi = aq['list'][0]['main']['aqi']
    aqi_e = ['👍', '🙂', '😐', '🙁', '🤢'][aqi - 1]
    air = {'ru': 'воздух', 'en': 'air'}
    air_description = f"{place}: {air[lang]} {aqi_e} PM2.5~{aq['list'][0]['components']['pm2_5']:.0f}, " \
                      f"SO₂~{aq['list'][0]['components']['so2']:.0f}, NO₂~{aq['list'][0]['components']['no2']:.0f}, " \
                      f"NH₃~{aq['list'][0]['components']['nh3']:.1f} (в µg/m³)."
    return aqi, air_description


async def get_air_accu_quality(lat, lon):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US;q=0.8,en;q=0.3",
        "Connection": "keep-alive",
        "Host": "www.accuweather.com",
        "Referer": "https://www.accuweather.com/",
        "Sec-GPC": "1",
        "TE": "Trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    session = aiohttp.ClientSession(headers=headers)
    url = await get_url_accu(lat, lon, session)
    result = await parse_air_accu(url, session)
    await session.close()
    return result


async def get_url_accu(lat, lon, session):
    url_host = 'https://www.accuweather.com'
    url_path = f'/en/search-locations?query={lat}%2C{lon}'
    async with session.get(url_host + url_path) as resp:
        url = url_host + resp.url.path
        print('URL: ', url)
    return url


async def parse_air_accu(url: str, session):
    pollutant = {'SO 2': 'SO₂', 'PM 2.5': 'PM2.5', 'O 3': 'O₃', 'PM 10': 'PM10', 'NO 2': 'NO₂', 'CO': 'CO'}
    category = {'Fair': '🙂', 'Excellent': '👍', 'Poor': '😐', 'Unhealthy': '🙁', 'Very Unhealthy': '🤢',
                'Dangerous': '☠'}
    air_index = {'Fair': 2, 'Excellent': 1, 'Poor': 3, 'Unhealthy': 4, 'Very Unhealthy': 5, 'Dangerous': 6}
    url = url.replace('weather-forecast', 'air-quality-index')
    async with session.get(url) as resp:
        html = await resp.text()
    tree = fromstring(html)
    aqi_category = tree.xpath('//*/p[@class="category-text"]')[0].text_content().strip()
    air_description = f'воздух {category[aqi_category]}'
    rows = tree.xpath('//div[contains(@class, "air-quality-pollutant")]')
    for row in rows:
        p = row.xpath('.//div[@class="display-type"]')[0].text_content().strip()
        if p[-1] == '0':
            continue
        cat = row.xpath('.//div[@class="category"]')[0].text_content().strip()
        v_aqp = row.xpath('.//div[@class="pollutant-concentration"]')[0].text_content().split()[0]
        air_description += f', {v_aqp}({pollutant[p]})-{category[cat]}'
    air_description += ', в µg/m³.'
    return air_index[aqi_category], air_description
