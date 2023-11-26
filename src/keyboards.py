from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def generateStylesKeyboard(styles):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(styles) // 2):
        keyboard.row(KeyboardButton(styles[i * 2]), KeyboardButton(styles[i * 2 + 1]))
    if len(styles) % 2 == 1:
        keyboard.row(KeyboardButton(styles[-1]))
    return keyboard
    

start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_kb.row(KeyboardButton("Выбор стиля изображения"), KeyboardButton("Ввод запроса"))
start_kb.row(KeyboardButton("Помощь"))
empty_kb = ReplyKeyboardRemove()
