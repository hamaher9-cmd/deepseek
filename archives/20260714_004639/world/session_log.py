"""
session_log.py — JSON session persistence for the Pomodoro Timer.

Handles loading/saving completed Pomodoro sessions from sessions.json.
Auto-creates the file with graceful JSON error handling.
"""

import json
import os
from datetime import date

DB_PATH = "sessions.json"


def load_sessions() -> list[dict]:
    """Return all logged sessions. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_session(session: dict) -> None:
    """Append a single session dict to the log file."""
    sessions = load_sessions()
    sessions.append(session)
    _atomic_write(sessions)


def get_today_sessions() -> list[dict]:
    """Return only sessions logged today."""
    today_str = date.today().isoformat()
    return [s for s in load_sessions() if s.get("date") == today_str]


def get_stats() -> dict:
    """Return aggregate stats across all sessions."""
    sessions = load_sessions()
    total = len(sessions)
    work_min = sum(s.get("work_minutes", 0) for s in sessions)
    break_min = sum(s.get("break_minutes", 0) for s in sessions)
    return {
        "total_sessions": total,
        "total_work_minutes": work_min,
        "total_break_minutes": break_min,
    }


def _atomic_write(sessions: list[dict]) -> None:
    """Write session list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(sessions, f, indent=2)
    os.replace(tmp, DB_PATH)
