import csv
import os
import random

PARKRUNS_FILE = os.path.join(os.path.dirname(__file__), 'all_parkruns.txt')
CLUBS_FILE = os.path.join(os.path.dirname(__file__), 'all_clubs.csv')

PARKRUNS = []
with open(PARKRUNS_FILE, 'r', newline='\n') as file:
    for line in file:
        PARKRUNS.append(line.strip())

CLUBS = []
with open(CLUBS_FILE, 'r', encoding='utf-8') as file:
    fieldnames = ['id', 'name', 'participants', 'runs', 'link']
    reader = csv.DictReader(file, fieldnames=fieldnames)
    for rec in reader:
        CLUBS.append(rec)

CLUBS.append({'id': '24630', 'name': 'ENGIRUNNERS', 'participants': '29', 'runs': '2157',
              'link': 'https://instagram.com/engirunners'})  # NOTE: personal order for D.Petrov


class ParkrunSite:
    PARKRUN_HEADERS = [
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/83.0.4103.61 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/89.0.4389.86 YaBrowser/21.3.0.740 Yowser/2.5 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/90.0.4430.85 Safari/537.36"}
    ]

    @classmethod
    def headers(cls):
        return random.choice(ParkrunSite.PARKRUN_HEADERS)


def min_to_mmss(m) -> str:
    mins = int(m)
    return f'{mins}:{int((m - mins) * 60)}'
