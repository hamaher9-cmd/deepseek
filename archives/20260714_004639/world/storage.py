"""
storage.py — JSON file persistence for the Task Manager.

Handles loading/saving the task list from tasks.json.
Auto-creates the file and assigns auto-incrementing IDs.
"""

import json
import os

DB_PATH = "tasks.json"


def load_tasks() -> list[dict]:
    """Return the list of task dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_tasks(tasks: list[dict]) -> None:
    """Atomically write the full task list to disk."""
    with open(DB_PATH, "w") as f:
        json.dump(tasks, f, indent=2)


def next_id(tasks: list[dict]) -> int:
    """Return the next available ID (1-based)."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1
