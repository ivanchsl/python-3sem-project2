from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from typing import List


def generateStylesKeyboard(styles: List[str]) -> ReplyKeyboardMarkup:
    """
    Generates a reply keyboard with styles arranged in 2 columns.
    
    Args:
        styles: List of style names to display as keyboard buttons
        
    Returns:
        ReplyKeyboardMarkup: Configured keyboard markup with buttons in 2-column layout
    """
    kb = []
    for i in range(len(styles) // 2):
        kb.append([
            KeyboardButton(text=styles[i * 2]),
            KeyboardButton(text=styles[i * 2 + 1])
        ])
    if len(styles) % 2 == 1:
        kb.append([KeyboardButton(text=styles[-1])])
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбор стиля изображения"),
         KeyboardButton(text="Ввод запроса")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
empty_kb = ReplyKeyboardRemove()
