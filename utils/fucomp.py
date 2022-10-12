import os
import re
from fuzzywuzzy import process, fuzz
import pickle


def bot_compare(user_phrase, dictionary: list) -> bool:
    accost_bot = re.compile(r'(?i)\bбот\b')
    user_str = str(user_phrase)
    if accost_bot.search(user_str):
        return process.extractOne(accost_bot.sub('', user_str), dictionary, scorer=fuzz.token_sort_ratio)[1] >= 70
    else:
        return False


def best_answer(user_phrase, dictionary: list) -> str:
    return process.extractOne(re.sub(r'(?i)\bбот\b,?', '', user_phrase).strip(), dictionary,
                              scorer=fuzz.token_set_ratio)[0]


# ======================= DICTIONARIES TO COMPARE =======================================================
phrases_weather = [
    'погода на улице', 'информация о погоде', 'прогноз погоды', "какая погода"
]

with open(os.path.join(os.path.dirname(__file__), 'message_base_meschch.pkl'), 'rb') as f:
    message_base_m = pickle.load(f)
