"""
project_store.py — JSON file persistence for the Project Tracker.

Handles loading/saving the project list from projects.json.
Auto-creates the file with graceful JSON error handling.
Uses atomic writes to prevent data corruption.
"""

import json
import os

DB_PATH = "projects.json"


def load_projects() -> list[dict]:
    """Return the list of project dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_projects(projects: list[dict]) -> None:
    """Atomically write the full project list to disk."""
    _atomic_write(projects)


def _atomic_write(projects: list[dict]) -> None:
    """Write project list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(projects, f, indent=2)
    os.replace(tmp, DB_PATH)
