import pytest as pytest

from utils import fucomp

test_phrases = ['бот, покажи статью о беге', 'Бот, позови администратора',
                'Бот, какая погода в Москве?', 'бот, когда откроют паркраны?']

phrases_to_try = [fucomp.phrases_parkrun, fucomp.phrases_admin,
                  fucomp.phrases_instagram, fucomp.phrases_weather]


@pytest.mark.parametrize('phrase_set', phrases_to_try)
def test_bot_compare(phrase_set):
    compare = list(map(lambda p: fucomp.bot_compare(p, phrase_set), test_phrases))
    assert sum(1 for b in compare if b) == 1


def test_compare_no_accost():
    compare = fucomp.bot_compare('без обращения к боту', fucomp.message_base_m)
    assert not compare


def test_best_answer():
    answer = fucomp.best_answer('Бот, какие кроссовки лучше для кроссов?', fucomp.message_base_m)
    print(answer)
    assert isinstance(answer, str)
    assert 'кроссовки' in answer
