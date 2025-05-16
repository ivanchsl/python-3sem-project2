import pytest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from keyboards import generateStylesKeyboard, start_kb, empty_kb


STYLES_TEST_CASES = [
    (["Style1", "Style2", "Style3"], 2, [["Style1", "Style2"], ["Style3"]]),
    (["A", "B"], 1, [["A", "B"]]),
    (["Single"], 1, [["Single"]]),
    ([], 0, []),
]


@pytest.mark.parametrize("styles,expected_rows,expected_layout", STYLES_TEST_CASES)
def test_generate_styles_keyboard(styles, expected_rows, expected_layout):
    keyboard = generateStylesKeyboard(styles)

    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert keyboard.resize_keyboard is True
    assert len(keyboard.keyboard) == expected_rows

    for row_idx, row in enumerate(expected_layout):
        assert len(keyboard.keyboard[row_idx]) == len(row)
        for btn_idx, text in enumerate(row):
            assert keyboard.keyboard[row_idx][btn_idx].text == text


def test_start_keyboard():
    assert isinstance(start_kb, ReplyKeyboardMarkup)
    assert start_kb.resize_keyboard is True
    assert start_kb.one_time_keyboard is True

    expected_layout = [
        ["Выбор стиля изображения", "Ввод запроса"],
        ["Помощь"]
    ]

    assert len(start_kb.keyboard) == 2
    for row_idx, row in enumerate(expected_layout):
        assert len(start_kb.keyboard[row_idx]) == len(row)
        for btn_idx, text in enumerate(row):
            assert start_kb.keyboard[row_idx][btn_idx].text == text


def test_empty_keyboard():
    assert isinstance(empty_kb, ReplyKeyboardRemove)
