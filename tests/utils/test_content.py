import pytest

from utils import content

sets_of_phrases_to_try = [
    content.greeting, content.phrases_grut, content.phrases_grechka,
    content.phrases_about_myself, content.phrases_about_running
]


@pytest.mark.parametrize('phrases', sets_of_phrases_to_try)
def test_content_with_lists(phrases):
    assert bool(phrases) and isinstance(phrases, list)
    assert all(isinstance(elem, str) for elem in phrases)


phrases_to_try = [
    content.help_message, content.start_message, content.no_parkrun_message,
    content.no_club_message, content.no_athlete_message, content.success_athlete_set, content.success_parkrun_set,
    content.success_club_set, content.settings_save_failed
]


@pytest.mark.parametrize('phrases', phrases_to_try, ids=range(len(phrases_to_try)))
def test_content_with_strings(phrases):
    assert isinstance(phrases, str)
