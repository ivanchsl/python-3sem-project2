import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
import asyncio
import base64


from bot_router import router, States, texts, keyboards
from bot_router import (
    cancelState,
    executePrompt,
    applyStyle,
    inputPrompt,
    inputStyle,
    helpCommand,
    start
)


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.text = "test"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_state():
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    return state


@pytest.mark.asyncio
async def test_cancel_state(mock_message, mock_state):
    await cancelState(mock_message, mock_state)
    mock_state.clear.assert_awaited_once()
    mock_message.answer.assert_awaited_with("Остановлено.", reply_markup=keyboards.empty_kb)


@pytest.mark.asyncio
@patch("bot_router.asyncio.sleep", new_callable=AsyncMock)
@patch("bot_router.kandinsky.API")
async def test_execute_prompt_success(mock_api, mock_sleep, mock_message, mock_state):
    mock_message.answer_photo = AsyncMock()
    mock_api_inst = AsyncMock()
    mock_api_inst.startGeneration = AsyncMock()
    mock_api_inst.checkGeneration = AsyncMock()
    mock_api_inst.getPhotos = MagicMock(return_value=["base64_string"])
    mock_api.return_value.__aenter__.return_value = mock_api_inst
    mock_state.get_data.return_value = {"style_title": "Test Style", "style": "test_style"}

    await executePrompt(mock_message, mock_state)

    mock_message.answer.assert_any_call(f"Изображение генерируется стилем Test Style.", reply_markup=keyboards.empty_kb)
    mock_api_inst.startGeneration.assert_awaited_with("test", "test_style")
    assert mock_api_inst.checkGeneration.await_count == 1
    mock_message.answer_photo.assert_awaited_once()
    call_args = mock_message.answer_photo.call_args
    assert isinstance(call_args.kwargs["photo"], BufferedInputFile)
    assert call_args.kwargs["photo"].filename == "generated_image.png"


@pytest.mark.asyncio
@patch("bot_router.asyncio.sleep", new_callable=AsyncMock)
@patch("bot_router.kandinsky.API")
async def test_execute_prompt_timeout(mock_api, mock_sleep, mock_message, mock_state):
    mock_api_inst = AsyncMock()
    mock_api_inst.getPhotos = MagicMock(return_value=[])
    mock_api.return_value.__aenter__.return_value = mock_api_inst

    await executePrompt(mock_message, mock_state)

    mock_message.answer.assert_any_call("Превышено максимальное время ожидания генерации.", reply_markup=keyboards.start_kb)


@pytest.mark.asyncio
@patch("bot_router.kandinsky.API")
async def test_execute_prompt_missing_state_data(mock_api, mock_message, mock_state):
    mock_message.answer_photo = AsyncMock()
    mock_api_inst = AsyncMock()
    mock_api_inst.startGeneration = AsyncMock()
    mock_api_inst.checkGeneration = AsyncMock()
    mock_api_inst.getPhotos = MagicMock(return_value=["base64_string"])
    mock_api.return_value.__aenter__.return_value = mock_api_inst
    mock_state.get_data.return_value = "invalid_data"

    await executePrompt(mock_message, mock_state)

    mock_message.answer.assert_awaited_with("Изображение генерируется стилем DEFAULT.", reply_markup=keyboards.empty_kb)


@pytest.mark.asyncio
@patch("bot_router.kandinsky.API")
async def test_apply_style_success(mock_api, mock_message, mock_state):
    mock_api_inst = AsyncMock()
    mock_api_inst.getStyleByTitle = AsyncMock(return_value="display_style")
    mock_api.return_value.__aenter__.return_value = mock_api_inst

    await applyStyle(mock_message, mock_state)

    mock_state.update_data.assert_awaited_with(style_title="test", style="display_style")
    mock_message.answer.assert_awaited_with("Стиль установлен.", reply_markup=keyboards.start_kb)


@pytest.mark.asyncio
@patch("bot_router.kandinsky.API")
async def test_apply_style_invalid(mock_api, mock_message, mock_state):
    mock_api_inst = AsyncMock()
    mock_api_inst.getStyleByTitle = AsyncMock(return_value=None)
    mock_api.return_value.__aenter__.return_value = mock_api_inst

    await applyStyle(mock_message, mock_state)

    mock_message.answer.assert_awaited_with("Неверный стиль.", reply_markup=keyboards.start_kb)


@pytest.mark.asyncio
async def test_input_prompt(mock_message, mock_state):
    await inputPrompt(mock_message, mock_state)
    mock_state.set_state.assert_awaited_with(States.INPUT_PROMPT)
    mock_message.answer.assert_awaited_with("Напишите запрос.", reply_markup=keyboards.empty_kb)


@pytest.mark.asyncio
@patch("bot_router.kandinsky.API")
async def test_input_style(mock_api, mock_message, mock_state):
    mock_api_inst = AsyncMock()
    mock_api_inst.getStyleList = AsyncMock(return_value=["Style1", "Style2", "Style3"])
    mock_api.return_value.__aenter__.return_value = mock_api_inst

    await inputStyle(mock_message, mock_state)

    mock_state.set_state.assert_awaited_with(States.INPUT_STYLE)
    call_args = mock_message.answer.call_args

    reply_markup = call_args.kwargs["reply_markup"]
    assert isinstance(reply_markup, ReplyKeyboardMarkup)
    assert reply_markup.resize_keyboard is True
    assert len(reply_markup.keyboard) == 2
    assert len(reply_markup.keyboard[0]) == 2
    assert len(reply_markup.keyboard[1]) == 1
    assert reply_markup.keyboard[0][0].text == "Style1"
    assert reply_markup.keyboard[0][1].text == "Style2"
    assert reply_markup.keyboard[1][0].text == "Style3"


@pytest.mark.asyncio
async def test_help_command(mock_message):
    await helpCommand(mock_message)
    mock_message.answer.assert_awaited_with(texts.help_text, reply_markup=keyboards.start_kb)


@pytest.mark.asyncio
async def test_start(mock_message):
    await start(mock_message)
    mock_message.answer.assert_awaited_with("Привет!", reply_markup=keyboards.start_kb)
