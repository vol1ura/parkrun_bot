import pytest

from bot_exceptions import ParsingException, CallbackException, NoCollationRuns


def test_parsing_exception():
    with pytest.raises(ParsingException) as exc:
        raise ParsingException
    assert exc.value.message == 'Page parsing failed'

    with pytest.raises(ParsingException) as exc:
        raise ParsingException('custom message')
    assert exc.value.message == 'custom message'


def test_callback_exception():
    with pytest.raises(CallbackException) as exc:
        raise CallbackException
    assert exc.value.message == 'Введённые данные не верны.'

    with pytest.raises(ParsingException) as exc:
        raise ParsingException('custom message')
    assert exc.value.message == 'custom message'


def test_no_collation_runs():
    with pytest.raises(NoCollationRuns) as exc:
        raise NoCollationRuns
    assert exc.value.message == 'У вас пока ещё не было совместных пробежек.'

    with pytest.raises(ParsingException) as exc:
        raise ParsingException('custom message')
    assert exc.value.message == 'custom message'
