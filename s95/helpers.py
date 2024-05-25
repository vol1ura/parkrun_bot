import random
from datetime import date, timedelta

from app import logger


class ParkrunSite:
    __PARKRUN_HEADERS = [
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/85.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/83.0.4103.61 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/89.0.4389.86 YaBrowser/21.3.0.740 Yowser/2.5 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/90.0.4430.85 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"},
        {"User-Agent": "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16.2"},
        {"User-Agent": "Opera/9.80 (Macintosh; Intel Mac OS X 10.14.1) Presto/2.12.388 Version/12.16"}
    ]

    # __PARKRUN_URL = {
    #     'largestclubs': 'https://www.parkrun.com.au/results/largestclubs/',
    #     'courserecords': 'https://www.parkrun.com.au/results/courserecords/'
    # }

    def __init__(self, key=''):
        self.__key = key
        self.__redis_key = f'parkrun_{key}'
        self.headers = random.choice(ParkrunSite.__PARKRUN_HEADERS)

    @staticmethod
    def _compare_dates(date1: str, date2) -> bool:
        if not date1:
            return False
        date1 = date.fromisoformat(date1)
        date_sun = date2 if date2.isoweekday() == 7 else date2 - timedelta(date2.isoweekday())
        return date1 >= date_sun

    async def get_html(self, url=None):
        return url

    async def update_info(self, actual_date: str):
        """
        Method to set actual date of content. It is used to rewrite date of access to requested
        page that will be assign by default in get_html().
        """
        # await redis.set_value(self.__redis_key, date=actual_date)
        logger.info(f'Information for [{self.__key}] was updated by date={actual_date}')


def min_to_mmss(m) -> str:
    mins = round(m) if abs(m - round(m)) < 0.0166665 else int(m)
    return f'{mins}:{round((m - mins) * 60):02d}'


def time_conv(t):
    arr = list(map(lambda x: int(x), str(t).split(':')))
    return (arr[0] - 21) * 60 + arr[1] + arr[2] / 60
