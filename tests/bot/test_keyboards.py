import asyncio
import pytest

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

import keyboards
from handlers import helpers


# @pytest.mark.asyncio
# async def test_my_test_class(thing):
#     # the patched function can be awaited..
#     main_kb = await keyboards.main(1)
#     assert isinstance(main_kb, ReplyKeyboardMarkup)


@pytest.mark.asyncio
async def test_main_kb(monkeypatch):
    future = asyncio.Future()
    future.set_result(None)
    monkeypatch.setattr(helpers, 'find_user_by', lambda *args: future)
    main_kb = await keyboards.main(1)
    assert isinstance(main_kb, ReplyKeyboardMarkup)
    print([main_kb.values['keyboard']])


def test_inline_stat_kb():
    inline_stat_kb = keyboards.inline_stat
    assert isinstance(inline_stat_kb, InlineKeyboardMarkup)


def test_inline_info_kb():
    inline_info_kb = keyboards.inline_stat
    assert isinstance(inline_info_kb, InlineKeyboardMarkup)


def test_inline_parkrun_kb():
    inline_parkrun_kb = keyboards.inline_stat
    assert isinstance(inline_parkrun_kb, InlineKeyboardMarkup)


def test_inline_personal_kb():
    inline_personal_kb = keyboards.inline_stat
    assert isinstance(inline_personal_kb, InlineKeyboardMarkup)
