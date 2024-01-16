import pytest

from utils import content

sets_of_phrases_to_try = [
    content.t('ru', 'greetings'), content.t('ru', 'phrases_about_myself'), content.phrases_about_running
]


@pytest.mark.parametrize('phrases', sets_of_phrases_to_try)
def test_content_with_lists(phrases):
    assert bool(phrases) and isinstance(phrases, list)
    assert all(isinstance(elem, str) for elem in phrases)


phrases_to_try = [
    content.t('ru', 'help_message').format('0.0.0'), content.t('ru', 'start_message'), content.settings_save_failed
]


@pytest.mark.parametrize('phrases', phrases_to_try, ids=range(len(phrases_to_try)))
def test_content_with_strings(phrases):
    assert isinstance(phrases, str)
