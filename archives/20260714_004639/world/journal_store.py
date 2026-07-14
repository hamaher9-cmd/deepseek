"""
journal_store.py — JSON file persistence for the Daily Journal.

Handles loading/saving journal entries from journal.json.
Auto-creates the file with graceful JSON error handling.
Uses atomic writes to prevent data corruption.
"""

import json
import os

DB_PATH = "journal.json"


def load_entries() -> list[dict]:
    """Return the list of entry dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_entries(entries: list[dict]) -> None:
    """Atomically write the full entry list to disk."""
    _atomic_write(entries)


def _atomic_write(entries: list[dict]) -> None:
    """Write entry list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(entries, f, indent=2)
    os.replace(tmp, DB_PATH)
