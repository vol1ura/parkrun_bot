from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

import keyboards


async def test_main_kb(database) -> None:
    main_kb = await keyboards.main(1)
    assert isinstance(main_kb, ReplyKeyboardMarkup)
    print([main_kb.values['keyboard']])


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


def test_inline_open_s95_kb():
    inline_open_s95_kb = keyboards.inline_open_s95
    assert isinstance(inline_open_s95_kb, InlineKeyboardMarkup)
