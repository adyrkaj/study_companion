import pytest
from unittest.mock import AsyncMock

# Adapt imports to match your handler functions
from mybot.handlers import (
    add_note_handler,
    schedule_handler,
    flashcard_handler,
    exam_handler,
    timer_handler,
)


@pytest.mark.asyncio
async def test_add_note_feature(mock_telegram_objects):
    update, context = mock_telegram_objects
    update.message.text = "/addnote Remember to test code"

    await add_note_handler(update, context)

    # Assert reply was sent to user
    update.message.reply_text.assert_called_once()
    assert "saved" in update.message.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_schedule_feature(mock_telegram_objects):
    update, context = mock_telegram_objects
    update.message.text = "/schedule Math Exam at 10AM"

    await schedule_handler(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_flashcard_feature(mock_telegram_objects):
    update, context = mock_telegram_objects
    update.message.text = "/flashcard Q: Python? A: Language"

    await flashcard_handler(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_exam_feature(mock_telegram_objects):
    update, context = mock_telegram_objects
    update.message.text = "/addexam Physics Friday"

    await exam_handler(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_timer_feature(mock_telegram_objects):
    update, context = mock_telegram_objects
    update.message.text = "/timer 25 Pomodoro"

    await timer_handler(update, context)
    update.message.reply_text.assert_called_once()