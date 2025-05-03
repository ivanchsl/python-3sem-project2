import asyncio
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import BufferedInputFile
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram_sqlite_storage.sqlitestore import SQLStorage
import logging
import base64


import kandinsky
import config
import keyboards
import texts


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_API)
storage = SQLStorage("fsm_storage.db")
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


class States(StatesGroup):
    """
    States for conversation flow.
    """
    INPUT_PROMPT = State()
    INPUT_STYLE = State()


@router.message(Command("cancel"))
async def cancelState(
    message: types.Message,
    state: FSMContext
) -> None:
    """Cancel all operations and clear state.
    
    Args:
        message: Incoming message object
        state: Current finite state machine context
    """
    await state.clear()
    await message.answer("Остановлено.", reply_markup=keyboards.empty_kb)


@router.message(StateFilter(States.INPUT_PROMPT))
async def executePrompt(
    message: types.Message,
    state: FSMContext
) -> None:
    """
    Handle prompt input and start image generation process.
    
    Args:
        message: Incoming message with prompt text
        state: Current finite state machine context
        
    Raises:
        Various API exceptions
    """
    await state.set_state(None)
    data = await state.get_data()
    if not isinstance(data, dict):
        data = {}
    style_title = data.get("style_title", "DEFAULT")
    style = data.get("style", "DEFAULT")
    await message.answer(f"Изображение генерируется стилем {style_title}.", reply_markup=keyboards.empty_kb)
    async with kandinsky.API(config.KANDINSKY_API_KEY, config.KANDINSKY_SECRET_KEY) as api:
        await api.startGeneration(message.text.strip(), style)
        for i in range(15):
            await api.checkGeneration()
            result = api.getPhotos()
            if result:
                for item in result:
                    photo = base64.b64decode(item)
                    await message.answer_photo(photo=BufferedInputFile(
                        file=photo,
                        filename="generated_image.png"
                    ), reply_markup=keyboards.start_kb)
                return
            await asyncio.sleep(4)
            await message.answer(texts.getWaitText(i), reply_markup=keyboards.empty_kb)
    await message.answer("Превышено максимальное время ожидания генерации.", reply_markup=keyboards.start_kb)


@router.message(StateFilter(States.INPUT_STYLE))
async def applyStyle(
    message: types.Message,
    state: FSMContext
) -> None:
    """
    Handle style selection.
    
    Args:
        message: Incoming message with style name
        state: Current finite state machine context
    """
    await state.set_state(None)
    async with kandinsky.API() as api:
        style = await api.getStyleByTitle(message.text)
    if style is None:
        await message.answer("Неверный стиль.", reply_markup=keyboards.start_kb)
        return
    await state.update_data(style_title=message.text, style=style)
    await message.answer("Стиль установлен.", reply_markup=keyboards.start_kb)


@router.message(or_f(
    Command("input"),
    F.text.startswith("Ввод запроса")
))
async def inputPrompt(
    message: types.Message,
    state: FSMContext
) -> None:
    """
    Initiate prompt input flow.
    
    Args:
        message: Incoming message triggering the command
        state: Current finite state machine context
    """
    await state.set_state(States.INPUT_PROMPT)
    await message.answer("Напишите запрос.", reply_markup=keyboards.empty_kb)


@router.message(or_f(
    Command("style"),
    F.text.startswith("Выбор стиля")
))
async def inputStyle(
    message: types.Message,
    state: FSMContext
) -> None:
    """
    Initiate style selection flow.
    
    Args:
        message: Incoming message triggering the command
        state: Current finite state machine context
    """
    await state.set_state(States.INPUT_STYLE)
    async with kandinsky.API() as api:
        styles = await api.getStyleList()
    keyboard = keyboards.generateStylesKeyboard(styles)
    await message.answer("Выберите стиль изображения.", reply_markup=keyboard)


@router.message(or_f(
    Command("help"),
    F.text.startswith("Помощь")
))
async def helpCommand(message: types.Message):
    """
    Show help information.
    
    Args:
        message: Incoming message triggering the command
    """
    await message.answer(texts.help_text, reply_markup=keyboards.start_kb)


@router.message()
async def start(message: types.Message):
    """
    Handle start command or any unhandled messages.
    
    Args:
        message: Incoming message triggering the command
    """
    await message.answer("Привет!", reply_markup=keyboards.start_kb)


dp.run_polling(bot)
