import json
import pytest
from unittest.mock import MagicMock, AsyncMock


# Import your storage and bot modules here
# Example: from mybot import storage, bot_module


@pytest.fixture(autouse=True)
def isolate_persistence(tmp_path, monkeypatch):
    """Isolate user_data.json to a temporary directory and reset in-memory state."""
    # 1. Point file path to temp directory
    temp_data_file = tmp_path / "user_data.json"

    # Adapt 'mybot.storage.DATA_FILE' to match your actual file path variable
    monkeypatch.setattr("mybot.storage.DATA_FILE", str(temp_data_file))

    # 2. Clear in-memory storage before test execution
    # Adapt 'mybot.storage.user_store' to match your global dict/store variable
    if hasattr(storage, "user_store"):
        storage.user_store.clear()

    yield temp_data_file

    # 3. Clean up in-memory storage after test execution
    if hasattr(storage, "user_store"):
        storage.user_store.clear()


@pytest.fixture
def mock_telegram_objects():
    """Provides reusable mock Telegram Update and Context objects."""
    update = MagicMock()
    context = MagicMock()

    # Mock Message and User details
    update.effective_user.id = 12345678
    update.effective_user.username = "testuser"
    update.effective_chat.id = 12345678

    # Mock async send_message method
    update.message.reply_text = AsyncMock()
    context.bot.send_message = AsyncMock()

    return update, context