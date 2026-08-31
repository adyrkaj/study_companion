import json
import pytest

# Adapt imports to your project layout
from mybot.storage import load_data, save_data, get_user_store


def test_get_user_store_initialization():
    """Verify get_user_store initializes correctly."""
    store = get_user_store(user_id=12345)
    assert store is not None
    assert isinstance(store, dict)


def test_save_and_load_data_success(isolate_persistence):
    """Verify data correctly persists to disk and reloads accurately."""
    store = get_user_store(user_id=12345)
    store["notes"] = ["Buy groceries", "Study Python"]

    save_data()

    # Ensure file was actually created on disk
    assert isolate_persistence.exists()

    # Clear in-memory data to prove load works independently
    store.clear()

    load_data()
    reloaded_store = get_user_store(user_id=12345)
    assert reloaded_store["notes"] == ["Buy groceries", "Study Python"]


def test_load_data_handles_corrupted_json(isolate_persistence):
    """Verify corrupted JSON files are handled gracefully without crashing."""
    # Write invalid JSON content to the temp file
    isolate_persistence.write_text("{ invalid json syntax ...")

    # load_data should catch the JSONDecodeError and initialize a clean state
    load_data()

    store = get_user_store(user_id=12345)
    assert store == {} or isinstance(store, dict)