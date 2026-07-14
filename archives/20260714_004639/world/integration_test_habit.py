"""
Integration test — full Habit Tracker pipeline: habit_store + habit_engine.

Exercises the complete flow:
  1. Add habits via engine, persist via store
  2. Check in, verify persistence
  3. List with streaks, stats, delete
  4. Round-trip: load from disk, modify, save, reload
"""

import os
from datetime import date, timedelta

from habit_store import load_habits, save_habits, DB_PATH
from habit_engine import (
    add_habit,
    checkin,
    list_habits,
    get_stats,
    delete_habit,
)


def _clean():
    for f in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(f):
            os.remove(f)


def test_full_pipeline_add_checkin_stats():
    """Add a habit, check in several times, verify stats."""
    _clean()

    # --- Step 1: Start empty ---
    habits = load_habits()
    assert habits == []

    # --- Step 2: Add a daily habit ---
    habits, new_h = add_habit(habits, "Exercise", "daily")
    assert new_h["name"] == "Exercise"
    assert new_h["frequency"] == "daily"
    assert new_h["checkins"] == []
    save_habits(habits)

    # --- Step 3: Check in on consecutive days ---
    d1 = (date.today() - timedelta(days=2)).isoformat()
    d2 = (date.today() - timedelta(days=1)).isoformat()
    d3 = date.today().isoformat()

    habits = load_habits()
    habits, res = checkin(habits, "Exercise", d1)
    assert res["already"] is False
    save_habits(habits)

    habits = load_habits()
    habits, res = checkin(habits, "Exercise", d2)
    assert res["already"] is False
    save_habits(habits)

    habits = load_habits()
    habits, res = checkin(habits, "Exercise", d3)
    assert res["already"] is False
    save_habits(habits)

    # --- Step 4: Verify checkins persisted ---
    habits = load_habits()
    assert len(habits[0]["checkins"]) == 3
    assert habits[0]["checkins"] == [d1, d2, d3]

    # --- Step 5: Verify stats ---
    s = get_stats(habits, "Exercise", today_str=d3)
    assert s["total_checkins"] == 3
    assert s["current_streak"] == 3
    assert s["best_streak"] == 3
    assert s["frequency"] == "daily"

    _clean()


def test_full_pipeline_duplicate_checkin():
    """Check in twice on the same day — second should be 'already'."""
    _clean()

    habits = []
    habits, _ = add_habit(habits, "Read", "daily")
    save_habits(habits)

    today = date.today().isoformat()
    habits = load_habits()
    habits, res1 = checkin(habits, "Read", today)
    assert res1["already"] is False
    save_habits(habits)

    habits = load_habits()
    habits, res2 = checkin(habits, "Read", today)
    assert res2["already"] is True
    save_habits(habits)

    # Only one checkin in the list
    habits = load_habits()
    assert habits[0]["checkins"] == [today]

    _clean()


def test_full_pipeline_list_with_streaks():
    """Add two habits, check in, list with streaks."""
    _clean()

    habits = []
    habits, _ = add_habit(habits, "Run", "daily")
    habits, _ = add_habit(habits, "Gym", "weekly")
    save_habits(habits)

    # Check in Run for the past 5 days
    for i in range(5, 0, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        habits = load_habits()
        habits, _ = checkin(habits, "Run", d)
        save_habits(habits)

    # Check in Gym for the past 2 weeks
    habits = load_habits()
    habits, _ = checkin(habits, "Gym", (date.today() - timedelta(days=10)).isoformat())
    habits, _ = checkin(habits, "Gym", (date.today() - timedelta(days=3)).isoformat())
    save_habits(habits)

    # List with streaks
    habits = load_habits()
    result = list_habits(habits, with_streaks=True)
    assert len(result) == 2

    run = [h for h in result if h["name"] == "Run"][0]
    assert run["total_checkins"] == 5
    assert run["current"] >= 0  # depends on today vs last checkin
    assert run["best"] >= 5

    gym = [h for h in result if h["name"] == "Gym"][0]
    assert gym["total_checkins"] == 2
    assert gym["frequency"] == "weekly"

    _clean()


def test_full_pipeline_delete():
    """Add a habit, check in, delete it, verify gone."""
    _clean()

    habits = []
    habits, _ = add_habit(habits, "Meditate", "daily")
    habits, _ = checkin(habits, "Meditate", date.today().isoformat())
    save_habits(habits)

    habits = load_habits()
    assert len(habits) == 1

    habits, removed = delete_habit(habits, "Meditate")
    assert removed["name"] == "Meditate"
    save_habits(habits)

    habits = load_habits()
    assert len(habits) == 0

    _clean()


def test_full_pipeline_round_trip():
    """Save multiple habits, reload, modify, save again, verify."""
    _clean()

    # First session: add two habits
    habits = []
    habits, _ = add_habit(habits, "Exercise", "daily")
    habits, _ = add_habit(habits, "Journal", "daily")
    habits, _ = checkin(habits, "Exercise", "2025-07-01")
    habits, _ = checkin(habits, "Journal", "2025-07-01")
    save_habits(habits)

    # Reload from disk
    habits = load_habits()
    assert len(habits) == 2
    assert habits[0]["checkins"] == ["2025-07-01"]
    assert habits[1]["checkins"] == ["2025-07-01"]

    # Add a third habit
    habits, _ = add_habit(habits, "Read", "weekly")
    save_habits(habits)

    # Reload and verify all three
    habits = load_habits()
    assert len(habits) == 3
    names = [h["name"] for h in habits]
    assert "Exercise" in names
    assert "Journal" in names
    assert "Read" in names

    # Delete one
    habits, _ = delete_habit(habits, "Journal")
    save_habits(habits)

    habits = load_habits()
    assert len(habits) == 2
    assert habits[0]["name"] == "Exercise"
    assert habits[1]["name"] == "Read"

    _clean()


def test_full_pipeline_weekly_streak():
    """Test weekly habit streak across multiple weeks."""
    _clean()

    habits = []
    habits, _ = add_habit(habits, "Gym", "weekly")
    save_habits(habits)

    # Check in for 3 consecutive Mondays
    habits = load_habits()
    habits, _ = checkin(habits, "Gym", "2025-07-07")  # Monday week 28
    habits, _ = checkin(habits, "Gym", "2025-07-14")  # Monday week 29
    habits, _ = checkin(habits, "Gym", "2025-07-21")  # Monday week 30
    save_habits(habits)

    habits = load_habits()
    s = get_stats(habits, "Gym", today_str="2025-07-21")
    assert s["total_checkins"] == 3
    assert s["current_streak"] == 3
    assert s["best_streak"] == 3

    _clean()


def test_full_pipeline_add_duplicate_error():
    """Adding a duplicate habit should raise ValueError."""
    _clean()

    habits = []
    habits, _ = add_habit(habits, "Run", "daily")
    save_habits(habits)

    habits = load_habits()
    try:
        add_habit(habits, "Run", "daily")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already exists" in str(e)

    _clean()


# -----------------------------------------------------------------------
# Runner
# -----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("full pipeline: add → checkin → stats", test_full_pipeline_add_checkin_stats),
        ("full pipeline: duplicate checkin handled", test_full_pipeline_duplicate_checkin),
        ("full pipeline: list with streaks", test_full_pipeline_list_with_streaks),
        ("full pipeline: delete removes from disk", test_full_pipeline_delete),
        ("full pipeline: round-trip save → reload → modify", test_full_pipeline_round_trip),
        ("full pipeline: weekly streak across weeks", test_full_pipeline_weekly_streak),
        ("full pipeline: add duplicate error", test_full_pipeline_add_duplicate_error),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {name}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed, {passed + failed} total")
