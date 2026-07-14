"""
integration_test_dashboard.py — full pipeline: real JSON → get_dashboard → suite output
Creates real data files, runs the engine and CLI, verifies output, cleans up.
"""
import os
import json
import sys
import io
from datetime import date, timedelta

import dashboard_engine as de
import suite

today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()
d2 = (date.today() - timedelta(days=2)).isoformat()

# --- Store original files ---
FILES = ["tasks.json", "sessions.json", "habits.json", "journal.json", "projects.json"]
BACKUPS = {}
for f in FILES:
    if os.path.exists(f):
        with open(f, "r") as fh:
            BACKUPS[f] = fh.read()

def cleanup():
    for f in FILES:
        if f in BACKUPS:
            with open(f, "w") as fh:
                fh.write(BACKUPS[f])
        elif os.path.exists(f):
            os.remove(f)

try:
    # --- Setup test data ---
    # Tasks
    with open("tasks.json", "w") as f:
        json.dump([
            {"id": 1, "title": "Buy milk", "done": True},
            {"id": 2, "title": "Walk dog", "done": False},
            {"id": 3, "title": "Read book", "done": False},
        ], f)

    # Sessions (pomodoro)
    with open("sessions.json", "w") as f:
        json.dump([
            {"date": today, "work_minutes": 25, "break_minutes": 5},
            {"date": today, "work_minutes": 25, "break_minutes": 5},
            {"date": yesterday, "work_minutes": 15, "break_minutes": 3},
        ], f)

    # Habits
    with open("habits.json", "w") as f:
        json.dump([
            {"name": "Exercise", "frequency": "daily",
             "checkins": [d2, yesterday, today]},
            {"name": "Read", "frequency": "daily",
             "checkins": [yesterday]},
        ], f)

    # Journal
    with open("journal.json", "w") as f:
        json.dump([
            {"date": yesterday, "content": "Yesterday was productive.",
             "tags": ["productive", "work"]},
            {"date": today, "content": "Today I shipped the dashboard!",
             "tags": ["coding", "productive"]},
        ], f)

    # Projects
    with open("projects.json", "w") as f:
        json.dump([
            {"name": "Build dashboard", "status": "active", "created_at": yesterday,
             "tasks": [
                 {"id": 1, "title": "Engine layer", "done": True},
                 {"id": 2, "title": "CLI layer", "done": True},
                 {"id": 3, "title": "Integration test", "done": False},
             ]},
            {"name": "Old project", "status": "done", "created_at": d2,
             "tasks": [{"id": 1, "title": "Done task", "done": True}]},
            {"name": "Archived thing", "status": "archived", "created_at": d2,
             "tasks": []},
        ], f)

    # --- Test 1: get_dashboard() returns correct aggregated stats ---
    dash = de.get_dashboard()

    assert dash["tasks"]["total"] == 3, f"tasks total: {dash['tasks']['total']}"
    assert dash["tasks"]["done"] == 1
    assert dash["tasks"]["pending"] == 2
    print("✅ test_dashboard_tasks")

    assert dash["pomodoro"]["total_sessions"] == 3
    assert dash["pomodoro"]["today_sessions"] == 2
    assert dash["pomodoro"]["total_work_minutes"] == 65
    assert dash["pomodoro"]["today_work_minutes"] == 50
    print("✅ test_dashboard_pomodoro")

    assert dash["habits"]["active"] == 2
    assert dash["habits"]["checked_in_today"] == 1  # Only Exercise has today
    assert dash["habits"]["top_streak_name"] == "Exercise"
    assert dash["habits"]["top_streak_count"] >= 2  # yesterday + today
    print("✅ test_dashboard_habits")

    assert dash["journal"]["total"] == 2
    assert dash["journal"]["today_entry"] == "Today I shipped the dashboard!"
    assert dash["journal"]["tag_count"] == 3  # productive, work, coding
    assert ("productive", 2) in dash["journal"]["top_tags"]
    print("✅ test_dashboard_journal")

    assert dash["projects"]["total"] == 3
    assert dash["projects"]["active"] == 1
    assert dash["projects"]["done"] == 1
    assert dash["projects"]["archived"] == 1
    assert dash["projects"]["top_project_name"] == "Build dashboard"
    print("✅ test_dashboard_projects")

    # --- Test 2: suite.main() renders without crashing ---
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        suite.main()
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "📋" in output
    assert "🍅" in output
    assert "📊" in output
    assert "📓" in output
    assert "🗂️" in output
    assert "Build dashboard" in output  # top project
    print("✅ test_suite_renders_all_sections")

    # --- Test 3: suite.main() with no data files ---
    for f in FILES:
        if os.path.exists(f):
            os.remove(f)

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        suite.main()
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "no tasks yet" in output
    assert "no sessions yet" in output
    assert "no habits yet" in output
    assert "no entries yet" in output
    assert "no projects yet" in output
    print("✅ test_suite_handles_all_empty")

    print("\n=== Full dashboard integration: 8/8 tests passed ✅ ===")

finally:
    cleanup()
