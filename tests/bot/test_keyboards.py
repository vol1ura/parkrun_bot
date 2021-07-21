from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
import keyboards


def test_main_kb():
    main_kb = keyboards.main
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
