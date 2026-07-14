"""
habit_store.py — JSON file persistence for the Habit Tracker.

Handles loading/saving the habit list from habits.json.
Auto-creates the file with graceful JSON error handling.
Uses atomic writes to prevent data corruption.
"""

import json
import os

DB_PATH = "habits.json"


def load_habits() -> list[dict]:
    """Return the list of habit dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_habits(habits: list[dict]) -> None:
    """Atomically write the full habit list to disk."""
    _atomic_write(habits)


def _atomic_write(habits: list[dict]) -> None:
    """Write habit list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(habits, f, indent=2)
    os.replace(tmp, DB_PATH)
