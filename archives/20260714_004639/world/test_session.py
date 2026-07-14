"""Unit tests for session_log layer."""

import json
import os
from datetime import date

from session_log import load_sessions, save_session, get_today_sessions, get_stats, DB_PATH


def _clean():
    """Remove test database if it exists."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    tmp = DB_PATH + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)


def test_load_empty():
    _clean()
    assert load_sessions() == []


def test_save_and_load():
    _clean()
    session = {
        "timestamp": "2025-01-15T10:30:00",
        "date": "2025-01-15",
        "work_minutes": 25,
        "break_minutes": 5,
        "cycles": 4,
        "status": "completed",
    }
    save_session(session)
    sessions = load_sessions()
    assert len(sessions) == 1
    assert sessions[0]["work_minutes"] == 25
    assert sessions[0]["status"] == "completed"


def test_multiple_sessions():
    _clean()
    for i in range(3):
        save_session({
            "timestamp": f"2025-01-{15+i}T10:00:00",
            "date": f"2025-01-{15+i}",
            "work_minutes": 25,
            "break_minutes": 5,
            "cycles": i + 1,
            "status": "completed",
        })
    assert len(load_sessions()) == 3


def test_get_today_sessions():
    _clean()
    today = date.today().isoformat()
    yesterday = "2000-01-01"  # definitely not today

    save_session({
        "timestamp": f"{today}T10:00:00",
        "date": today,
        "work_minutes": 25,
        "break_minutes": 5,
        "cycles": 2,
        "status": "completed",
    })
    save_session({
        "timestamp": f"{yesterday}T10:00:00",
        "date": yesterday,
        "work_minutes": 10,
        "break_minutes": 3,
        "cycles": 1,
        "status": "stopped",
    })

    today_sessions = get_today_sessions()
    assert len(today_sessions) == 1
    assert today_sessions[0]["date"] == today
    assert today_sessions[0]["cycles"] == 2


def test_get_stats():
    _clean()
    save_session({
        "timestamp": "2025-01-15T10:00:00",
        "date": "2025-01-15",
        "work_minutes": 25,
        "break_minutes": 5,
        "cycles": 4,
        "status": "completed",
    })
    save_session({
        "timestamp": "2025-01-15T11:00:00",
        "date": "2025-01-15",
        "work_minutes": 10,
        "break_minutes": 3,
        "cycles": 1,
        "status": "stopped",
    })

    stats = get_stats()
    assert stats["total_sessions"] == 2
    assert stats["total_work_minutes"] == 35
    assert stats["total_break_minutes"] == 8


def test_stats_empty():
    _clean()
    stats = get_stats()
    assert stats["total_sessions"] == 0
    assert stats["total_work_minutes"] == 0
    assert stats["total_break_minutes"] == 0


def test_corrupt_json():
    _clean()
    with open(DB_PATH, "w") as f:
        f.write("this is not json {{{")
    # Should gracefully return empty list
    assert load_sessions() == []


def test_atomic_write_preserves_existing():
    """Verify save_session doesn't corrupt existing data."""
    _clean()
    save_session({
        "timestamp": "2025-01-15T10:00:00",
        "date": "2025-01-15",
        "work_minutes": 25,
        "break_minutes": 5,
        "cycles": 4,
        "status": "completed",
    })
    save_session({
        "timestamp": "2025-01-15T11:00:00",
        "date": "2025-01-15",
        "work_minutes": 15,
        "break_minutes": 3,
        "cycles": 2,
        "status": "completed",
    })
    sessions = load_sessions()
    assert len(sessions) == 2
    assert sessions[0]["work_minutes"] == 25
    assert sessions[1]["work_minutes"] == 15


def test_get_today_sessions_empty():
    _clean()
    assert get_today_sessions() == []


if __name__ == "__main__":
    tests = [
        ("load empty", test_load_empty),
        ("save and load", test_save_and_load),
        ("multiple sessions", test_multiple_sessions),
        ("get today sessions", test_get_today_sessions),
        ("get stats", test_get_stats),
        ("stats empty", test_stats_empty),
        ("corrupt JSON", test_corrupt_json),
        ("atomic write preserves", test_atomic_write_preserves_existing),
        ("today sessions empty", test_get_today_sessions_empty),
    ]
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name}")
        except AssertionError as e:
            print(f"❌ {name}: {e}")
        finally:
            _clean()
    print("\nAll session_log tests passed!")
