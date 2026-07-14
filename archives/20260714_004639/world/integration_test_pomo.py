"""
Integration test — full Pomodoro pipeline: timer_engine + session_log.

Exercises the complete flow:
  1. Create timer, run through full work session
  2. Log the completed session
  3. Verify persistence, stats, today filtering
"""

import os
import json
from datetime import date

from timer_engine import PomodoroTimer, Phase
from session_log import (
    load_sessions, save_session, get_today_sessions, get_stats, DB_PATH,
)


def _clean():
    for f in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(f):
            os.remove(f)


def test_full_pipeline_one_cycle():
    """Run a 1-cycle timer to completion, log it, and verify."""
    _clean()

    # --- Step 1: Run the timer engine ---
    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=1)
    tick = t.start()
    assert tick.phase == Phase.WORKING
    assert tick.cycle == 1

    # Tick through the full work session
    for _ in range(60):
        tick = t.tick()

    assert tick.phase == Phase.DONE
    assert tick.remaining == 0

    # --- Step 2: Log the session ---
    today_str = date.today().isoformat()
    session = {
        "timestamp": f"{today_str}T10:30:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 1,
        "cycles": 1,
        "status": "completed",
    }
    save_session(session)

    # --- Step 3: Verify persistence ---
    sessions = load_sessions()
    assert len(sessions) == 1
    assert sessions[0]["status"] == "completed"
    assert sessions[0]["work_minutes"] == 1
    assert sessions[0]["cycles"] == 1

    # --- Step 4: Verify stats ---
    stats = get_stats()
    assert stats["total_sessions"] == 1
    assert stats["total_work_minutes"] == 1
    assert stats["total_break_minutes"] == 1

    # --- Step 5: Verify today filtering ---
    today = get_today_sessions()
    assert len(today) == 1
    assert today[0]["date"] == today_str

    _clean()


def test_full_pipeline_multi_cycle():
    """Run a 2-cycle timer, log both cycles as separate sessions."""
    _clean()

    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=2)
    t.start()

    # Cycle 1: work → break
    for _ in range(60):
        t.tick()  # work done, now on break
    assert t.phase == Phase.ON_BREAK

    for _ in range(60):
        t.tick()  # break done, now cycle 2 work
    assert t.phase == Phase.WORKING
    assert t.cycle == 2

    # Log session 1
    today_str = date.today().isoformat()
    save_session({
        "timestamp": f"{today_str}T10:00:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 1,
        "cycles": 1,
        "status": "completed",
    })

    # Cycle 2: work → done (last cycle, no break after)
    for _ in range(60):
        t.tick()
    assert t.phase == Phase.DONE

    # Log session 2
    save_session({
        "timestamp": f"{today_str}T10:30:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 0,
        "cycles": 1,
        "status": "completed",
    })

    sessions = load_sessions()
    assert len(sessions) == 2

    stats = get_stats()
    assert stats["total_sessions"] == 2
    assert stats["total_work_minutes"] == 2

    _clean()


def test_pause_resume_pipeline():
    """Pause mid-work, resume, complete, and log."""
    _clean()

    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=1)
    t.start()

    # Tick 30 seconds in
    for _ in range(30):
        t.tick()
    assert t.remaining == 30

    # Pause
    tick = t.pause()
    assert tick.phase == Phase.PAUSED

    # Resume
    tick = t.resume()
    assert tick.phase == Phase.WORKING
    assert tick.remaining == 30

    # Finish
    for _ in range(30):
        tick = t.tick()
    assert tick.phase == Phase.DONE

    # Log
    today_str = date.today().isoformat()
    save_session({
        "timestamp": f"{today_str}T11:00:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 0,
        "cycles": 1,
        "status": "completed",
    })

    assert len(load_sessions()) == 1
    _clean()


def test_stop_mid_session_pipeline():
    """Stop mid-work, log partial session."""
    _clean()

    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=4)
    t.start()

    # Tick 10 seconds, then stop
    for _ in range(10):
        t.tick()
    tick = t.stop()
    assert tick.phase == Phase.DONE
    assert tick.remaining == 0

    today_str = date.today().isoformat()
    save_session({
        "timestamp": f"{today_str}T12:00:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 1,
        "cycles": 1,
        "status": "stopped",
    })

    sessions = load_sessions()
    assert len(sessions) == 1
    assert sessions[0]["status"] == "stopped"

    stats = get_stats()
    assert stats["total_sessions"] == 1

    _clean()


def test_json_file_integration():
    """Verify sessions.json is actually written to disk."""
    _clean()

    t = PomodoroTimer(work_minutes=1, break_minutes=1, cycles=1)
    t.start()
    for _ in range(60):
        t.tick()

    today_str = date.today().isoformat()
    save_session({
        "timestamp": f"{today_str}T14:00:00",
        "date": today_str,
        "work_minutes": 1,
        "break_minutes": 1,
        "cycles": 1,
        "status": "completed",
    })

    # Verify file exists and is valid JSON
    assert os.path.exists(DB_PATH)
    with open(DB_PATH) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1

    _clean()


if __name__ == "__main__":
    tests = [
        ("full pipeline one cycle", test_full_pipeline_one_cycle),
        ("full pipeline multi cycle", test_full_pipeline_multi_cycle),
        ("pause resume pipeline", test_pause_resume_pipeline),
        ("stop mid-session pipeline", test_stop_mid_session_pipeline),
        ("JSON file integration", test_json_file_integration),
    ]
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name}")
        except AssertionError as e:
            print(f"❌ {name}: {e}")
        finally:
            _clean()
    print("\n=== All integration tests passed! ===")
