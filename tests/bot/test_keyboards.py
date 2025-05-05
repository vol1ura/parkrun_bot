from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, User
from aiogram.types.message import Message
import pytest
from keyboards import main

import keyboards


@pytest.mark.asyncio
async def test_main_kb(db, loop):
    message = Message()
    message.from_user = User(id=1, is_bot=False)
    main_kb = await main(message)
    assert isinstance(main_kb, ReplyKeyboardMarkup)


def test_set_home_event_kb():
    set_home_event_kb = keyboards.set_home_event
    assert isinstance(set_home_event_kb, InlineKeyboardMarkup)


def test_change_club_kb():
    change_club_kb = keyboards.change_club
    assert isinstance(change_club_kb, InlineKeyboardMarkup)


def test_set_club_kb():
    set_club_kb = keyboards.set_club
    assert isinstance(set_club_kb, InlineKeyboardMarkup)


def test_confirm_set_club_kb():
    confirm_set_club_kb = keyboards.confirm_set_club
    assert isinstance(confirm_set_club_kb, InlineKeyboardMarkup)


def test_inline_personal_kb():
    inline_personal_kb = keyboards.inline_personal
    assert isinstance(inline_personal_kb, InlineKeyboardMarkup)


async def test_inline_open_s95_kb():
    message = Message()
    message.from_user = User(id=1, language_code='ru')
    inline_open_s95_kb = await keyboards.inline_open_s95(message)
    assert isinstance(inline_open_s95_kb, InlineKeyboardMarkup)
