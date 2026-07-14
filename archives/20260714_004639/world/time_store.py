"""
time_store.py — JSON file persistence for the Time Blocker.

Handles loading/saving the block list from time_blocks.json.
Auto-creates the file with graceful JSON error handling.
Uses atomic writes to prevent data corruption.
"""

import json
import os

DB_PATH = "time_blocks.json"


def load_blocks() -> list[dict]:
    """Return the list of time block dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_blocks(blocks: list[dict]) -> None:
    """Atomically write the full block list to disk."""
    _atomic_write(blocks)


def _atomic_write(blocks: list[dict]) -> None:
    """Write block list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(blocks, f, indent=2)
    os.replace(tmp, DB_PATH)
