from asyncio import sleep
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
import base64


import kandinsky
import config
import keyboards
import texts


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class States(StatesGroup):
    INPUT_PROMPT = State()
    INPUT_STYLE = State()


@dp.message_handler(state='*', commands=["cancel"])
async def cancelState(message: types.Message):
    await dp.current_state().finish()
    await message.answer("Остановлено.", reply_markup=keyboards.empty_kb)


@dp.message_handler(state=States.INPUT_PROMPT)
async def executePrompt(message: types.Message):
    await dp.current_state().set_state()
    data = await dp.current_state().get_data()
    style_title = data.get("style_title", "DEFAULT")
    style = data.get("style", "DEFAULT")
    await message.answer(f"Изображение генерируется стилем {style_title}.", reply_markup=keyboards.empty_kb)
    api = kandinsky.API(config.KANDINSKY_API_KEY, config.KANDINSKY_SECRET_KEY)
    api.startGeneration(message.text.strip(), style)
    for i in range(15):
        if api.checkGeneration():
            photo = base64.b64decode(api.getPhoto())
            await bot.send_photo(message.chat.id, photo=photo, reply_markup=keyboards.start_kb)
            return
        await sleep(4)
        await message.answer(texts.getWaitText(i), reply_markup=keyboards.empty_kb)
    await message.answer("Сгенерировать не удалось.", reply_markup=keyboards.start_kb)


@dp.message_handler(state=States.INPUT_STYLE)
async def applyStyle(message: types.Message):
    await dp.current_state().set_state()
    style = kandinsky.getStyleByTitle(message.text)
    if style is None:
        await message.answer("Неверный стиль.", reply_markup=keyboards.start_kb)
        return
    await dp.current_state().update_data(style_title=message.text, style=style)
    await message.answer("Стиль установлен.", reply_markup=keyboards.start_kb)


@dp.message_handler(commands=["input"])
@dp.message_handler(lambda message: message.text and message.text.startswith("Ввод запроса"))
async def inputPrompt(message: types.Message):
    await States.INPUT_PROMPT.set()
    await message.answer("Напишите запрос.", reply_markup=keyboards.empty_kb)


@dp.message_handler(commands=["style"])
@dp.message_handler(lambda message: message.text and message.text.startswith("Выбор стиля"))
async def inputStyle(message: types.Message):
    await States.INPUT_STYLE.set()
    keyboard = keyboards.generateStylesKeyboard(kandinsky.getStyles())
    await message.answer("Выберите стиль изображения.", reply_markup=keyboard)


@dp.message_handler(commands=["help"])
@dp.message_handler(lambda message: message.text and message.text.startswith("Помощь"))
async def helpCommand(message: types.Message):
    await message.answer(texts.help_text, reply_markup=keyboards.start_kb)


@dp.message_handler()
async def start(message: types.Message):
    await message.answer("Привет!", reply_markup=keyboards.start_kb)


executor.start_polling(dp, skip_updates=True)
