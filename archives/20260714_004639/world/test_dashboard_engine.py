"""
test_dashboard_engine.py — unit tests for dashboard_engine.py

Tests each aggregator in isolation by monkey-patching _safe_load,
then tests the full get_dashboard() composition.
"""

from unittest.mock import patch
import dashboard_engine as de
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Task stats
# ---------------------------------------------------------------------------

def test_task_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._task_stats()
        assert stats == {"total": 0, "done": 0, "pending": 0}


def test_task_stats_all_pending():
    data = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Walk dog", "done": False},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._task_stats()
        assert stats == {"total": 2, "done": 0, "pending": 2}


def test_task_stats_mixed():
    data = [
        {"id": 1, "title": "Buy milk", "done": True},
        {"id": 2, "title": "Walk dog", "done": False},
        {"id": 3, "title": "Read book", "done": True},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._task_stats()
        assert stats == {"total": 3, "done": 2, "pending": 1}


def test_task_stats_all_done():
    data = [
        {"id": 1, "title": "A", "done": True},
        {"id": 2, "title": "B", "done": True},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._task_stats()
        assert stats == {"total": 2, "done": 2, "pending": 0}


def test_task_stats_missing_done_field():
    data = [{"id": 1, "title": "No done field"}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._task_stats()
        assert stats["pending"] == 1
        assert stats["done"] == 0


# ---------------------------------------------------------------------------
# Pomodoro stats
# ---------------------------------------------------------------------------

def test_pomodoro_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._pomodoro_stats()
        assert stats["total_sessions"] == 0
        assert stats["today_sessions"] == 0
        assert stats["total_work_minutes"] == 0
        assert stats["today_work_minutes"] == 0


def test_pomodoro_stats_with_sessions():
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    data = [
        {"date": today, "work_minutes": 25, "break_minutes": 5},
        {"date": today, "work_minutes": 25, "break_minutes": 5},
        {"date": yesterday, "work_minutes": 15, "break_minutes": 3},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._pomodoro_stats()
        assert stats["total_sessions"] == 3
        assert stats["today_sessions"] == 2
        assert stats["total_work_minutes"] == 65
        assert stats["today_work_minutes"] == 50


def test_pomodoro_stats_missing_work_minutes():
    data = [{"date": date.today().isoformat()}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._pomodoro_stats()
        assert stats["today_sessions"] == 1
        assert stats["today_work_minutes"] == 0


def test_pomodoro_stats_missing_date_field():
    data = [{"work_minutes": 25}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._pomodoro_stats()
        # No date field means it won't match today
        assert stats["today_sessions"] == 0
        assert stats["total_sessions"] == 1


# ---------------------------------------------------------------------------
# Habit stats
# ---------------------------------------------------------------------------

def test_habit_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._habit_stats()
        assert stats == {
            "active": 0,
            "checked_in_today": 0,
            "top_streak_name": None,
            "top_streak_count": 0,
            "top_streak_frequency": "daily",
        }


def test_habit_stats_no_checkins():
    data = [
        {"name": "Exercise", "frequency": "daily", "checkins": []},
        {"name": "Read", "frequency": "daily", "checkins": []},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._habit_stats()
        assert stats["active"] == 2
        assert stats["top_streak_count"] == 0
        assert stats["checked_in_today"] == 0


def test_habit_stats_with_streaks():
    today = date.today().isoformat()
    d1 = (date.today() - timedelta(days=1)).isoformat()
    d2 = (date.today() - timedelta(days=2)).isoformat()
    d3 = (date.today() - timedelta(days=3)).isoformat()

    data = [
        {
            "name": "Exercise",
            "frequency": "daily",
            "checkins": [d3, d2, d1, today],  # 4-day streak
        },
        {
            "name": "Read",
            "frequency": "daily",
            "checkins": [d3, d1],  # broken streak
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._habit_stats()
        assert stats["active"] == 2
        assert stats["top_streak_name"] == "Exercise"
        assert stats["top_streak_count"] >= 3  # at least the streak we built
        assert stats["top_streak_frequency"] == "daily"
        assert stats["checked_in_today"] == 1  # only Exercise checked in today


def test_habit_stats_today_checkin():
    today = date.today().isoformat()
    data = [
        {"name": "Exercise", "frequency": "daily", "checkins": [today]},
        {"name": "Read", "frequency": "daily", "checkins": [today]},
        {"name": "Meditate", "frequency": "daily", "checkins": []},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._habit_stats()
        assert stats["checked_in_today"] == 2


def test_habit_stats_weekly_streak():
    today = date.today().isoformat()
    last_week = (date.today() - timedelta(days=7)).isoformat()
    data = [
        {
            "name": "Weekly Review",
            "frequency": "weekly",
            "checkins": [last_week, today],
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._habit_stats()
        assert stats["top_streak_name"] == "Weekly Review"
        assert stats["top_streak_count"] == 2
        assert stats["top_streak_frequency"] == "weekly"


def test_habit_stats_missing_checkins_field():
    data = [{"name": "Exercise", "frequency": "daily"}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._habit_stats()
        assert stats["active"] == 1
        assert stats["top_streak_count"] == 0


# ---------------------------------------------------------------------------
# Journal stats
# ---------------------------------------------------------------------------

def test_journal_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._journal_stats()
        assert stats["total"] == 0
        assert stats["today_entry"] is None
        assert stats["latest_date"] is None
        assert stats["latest_snippet"] is None
        assert stats["tag_count"] == 0
        assert stats["top_tags"] == []


def test_journal_stats_with_entries():
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    data = [
        {
            "date": yesterday,
            "content": "Yesterday was productive.",
            "tags": ["work", "productive"],
        },
        {
            "date": today,
            "content": "Today is great! Building a dashboard.",
            "tags": ["work", "coding"],
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._journal_stats()
        assert stats["total"] == 2
        assert stats["latest_date"] == today
        assert stats["today_entry"] == "Today is great! Building a dashboard."
        assert stats["latest_snippet"] == "Today is great! Building a dashboard."
        assert stats["tag_count"] == 3  # work, productive, coding
        # Top tag should be "work" (count 2)
        assert stats["top_tags"][0] == ("work", 2)


def test_journal_stats_long_snippet():
    data = [
        {
            "date": date.today().isoformat(),
            "content": "A" * 100,
            "tags": [],
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._journal_stats()
        assert len(stats["latest_snippet"]) <= 60
        assert stats["latest_snippet"].endswith("...")


def test_journal_stats_no_tags():
    data = [{"date": date.today().isoformat(), "content": "No tags."}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._journal_stats()
        assert stats["tag_count"] == 0
        assert stats["top_tags"] == []


def test_journal_stats_top_tags_ordering():
    data = [
        {"date": "2025-01-01", "content": "A", "tags": ["alpha", "beta"]},
        {"date": "2025-01-02", "content": "B", "tags": ["alpha"]},
        {"date": "2025-01-03", "content": "C", "tags": ["beta", "gamma"]},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._journal_stats()
        # alpha: 2, beta: 2, gamma: 1
        # Ties broken by alpha ordering
        assert stats["top_tags"][0] == ("alpha", 2)
        assert stats["top_tags"][1] == ("beta", 2)
        assert stats["top_tags"][2] == ("gamma", 1)
        assert len(stats["top_tags"]) == 3


# ---------------------------------------------------------------------------
# Project stats
# ---------------------------------------------------------------------------

def test_project_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._project_stats()
        assert stats == {
            "total": 0,
            "active": 0,
            "done": 0,
            "archived": 0,
            "top_project_name": None,
            "top_project_pct": 0.0,
            "top_project_done": 0,
            "top_project_total": 0,
        }


def test_project_stats_mixed_statuses():
    data = [
        {"name": "Active A", "status": "active", "tasks": []},
        {"name": "Active B", "status": "active", "tasks": []},
        {"name": "Done", "status": "done", "tasks": []},
        {"name": "Archived", "status": "archived", "tasks": []},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        assert stats["total"] == 4
        assert stats["active"] == 2
        assert stats["done"] == 1
        assert stats["archived"] == 1


def test_project_stats_progress():
    data = [
        {
            "name": "Build Website",
            "status": "active",
            "tasks": [
                {"id": 1, "title": "Design", "done": True},
                {"id": 2, "title": "Code", "done": True},
                {"id": 3, "title": "Test", "done": False},
                {"id": 4, "title": "Deploy", "done": False},
            ],
        },
        {
            "name": "Write Book",
            "status": "active",
            "tasks": [
                {"id": 1, "title": "Outline", "done": True},
                {"id": 2, "title": "Draft", "done": False},
            ],
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        # Build Website: 2/4 = 50%. Write Book: 1/2 = 50%.
        # Both 50% — first one wins since we only update on >
        assert stats["top_project_name"] == "Build Website"
        assert stats["top_project_pct"] == 50.0
        assert stats["top_project_done"] == 2
        assert stats["top_project_total"] == 4


def test_project_stats_best_progress_wins():
    data = [
        {
            "name": "Low Progress",
            "status": "active",
            "tasks": [
                {"id": 1, "title": "A", "done": True},
                {"id": 2, "title": "B", "done": False},
                {"id": 3, "title": "C", "done": False},
            ],  # 33%
        },
        {
            "name": "High Progress",
            "status": "active",
            "tasks": [
                {"id": 1, "title": "X", "done": True},
                {"id": 2, "title": "Y", "done": True},
                {"id": 3, "title": "Z", "done": True},
            ],  # 100%
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        assert stats["top_project_name"] == "High Progress"
        assert stats["top_project_pct"] == 100.0
        assert stats["top_project_done"] == 3
        assert stats["top_project_total"] == 3


def test_project_stats_only_active_considered():
    data = [
        {
            "name": "Done 100%",
            "status": "done",
            "tasks": [
                {"id": 1, "title": "A", "done": True},
            ],  # 100% but done
        },
        {
            "name": "Active 50%",
            "status": "active",
            "tasks": [
                {"id": 1, "title": "B", "done": True},
                {"id": 2, "title": "C", "done": False},
            ],
        },
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        assert stats["top_project_name"] == "Active 50%"


def test_project_stats_zero_tasks():
    data = [
        {"name": "Empty", "status": "active", "tasks": []},
    ]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        assert stats["active"] == 1
        # No tasks means it won't be selected as top (we skip t_total == 0
        # in the primary branch, but fallback sets it)
        assert stats["top_project_name"] is None or stats["top_project_total"] == 0


def test_project_stats_missing_tasks_field():
    data = [{"name": "No Tasks", "status": "active"}]
    with patch.object(de, '_safe_load', return_value=data):
        stats = de._project_stats()
        assert stats["active"] == 1
        assert stats["total"] == 1


# ---------------------------------------------------------------------------
# Full get_dashboard composition
# ---------------------------------------------------------------------------

def test_get_dashboard_all_empty():
    """When all stores are empty, get_dashboard returns zeroed stats."""
    with patch.object(de, '_safe_load', return_value=[]):
        dash = de.get_dashboard()
        assert set(dash.keys()) == {"tasks", "pomodoro", "habits", "journal", "projects", "budget"}
        assert dash["tasks"]["total"] == 0
        assert dash["pomodoro"]["total_sessions"] == 0
        assert dash["habits"]["active"] == 0
        assert dash["journal"]["total"] == 0
        assert dash["projects"]["total"] == 0
        assert dash["budget"]["total"] == 0
        assert dash["budget"]["balance"] == 0.0


def test_get_dashboard_mixed():
    """Patch each call sequence to return different data per path."""
    today = date.today().isoformat()

    def fake_load(path):
        if path.endswith("tasks.json"):
            return [{"id": 1, "title": "Task", "done": False}]
        elif path.endswith("sessions.json"):
            return [{"date": today, "work_minutes": 25, "break_minutes": 5}]
        elif path.endswith("habits.json"):
            return [{"name": "Exercise", "frequency": "daily", "checkins": [today]}]
        elif path.endswith("journal.json"):
            return [{"date": today, "content": "Hello", "tags": ["test"]}]
        elif path.endswith("projects.json"):
            return [{"name": "P1", "status": "active", "tasks": []}]
        elif path.endswith("budget.json"):
            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]
        return []

    with patch.object(de, '_safe_load', side_effect=fake_load):
        dash = de.get_dashboard()
        assert dash["tasks"]["total"] == 1
        assert dash["tasks"]["pending"] == 1
        assert dash["pomodoro"]["today_sessions"] == 1
        assert dash["habits"]["active"] == 1
        assert dash["habits"]["checked_in_today"] == 1
        assert dash["journal"]["total"] == 1
        assert dash["projects"]["active"] == 1
        assert dash["budget"]["total"] == 1
        assert dash["budget"]["balance"] == 100.0


def test_get_dashboard_handles_missing_files():
    """Even if some stores are empty, the dashboard still returns."""
    with patch.object(de, '_safe_load', return_value=[]):
        dash = de.get_dashboard()
        # Should not raise, all keys present with zero values
        assert dash["tasks"]["total"] == 0
        assert dash["projects"]["active"] == 0


# ---------------------------------------------------------------------------
# _snippet
# ---------------------------------------------------------------------------

def test_snippet_short_text():
    assert de._snippet("Hello") == "Hello"


def test_snippet_long_text():
    long_text = "x" * 100
    result = de._snippet(long_text)
    assert len(result) <= 60
    assert result.endswith("...")


def test_snippet_newlines():
    result = de._snippet("Line one.\nLine two.\nLine three.")
    assert "\n" not in result
    assert "Line one. Line two. Line three." in result


def test_snippet_empty():
    assert de._snippet("") == ""
    assert de._snippet(None) == ""


# ---------------------------------------------------------------------------
# _is_adjacent
# ---------------------------------------------------------------------------

def test_is_adjacent_daily_consecutive():
    assert de._is_adjacent("2025-07-14", "2025-07-15", "daily") is True


def test_is_adjacent_daily_skip():
    assert de._is_adjacent("2025-07-14", "2025-07-16", "daily") is False


def test_is_adjacent_weekly_within_7():
    assert de._is_adjacent("2025-07-01", "2025-07-08", "weekly") is True


def test_is_adjacent_weekly_exceeds_7():
    assert de._is_adjacent("2025-07-01", "2025-07-09", "weekly") is False


def test_is_adjacent_invalid_dates():
    assert de._is_adjacent("bad", "2025-07-15", "daily") is False
    assert de._is_adjacent("2025-07-14", "bad", "daily") is False


if __name__ == "__main__":
    tests = [
        # Task stats
        test_task_stats_empty,
        test_task_stats_all_pending,
        test_task_stats_mixed,
        test_task_stats_all_done,
        test_task_stats_missing_done_field,
        # Pomodoro stats
        test_pomodoro_stats_empty,
        test_pomodoro_stats_with_sessions,
        test_pomodoro_stats_missing_work_minutes,
        test_pomodoro_stats_missing_date_field,
        # Habit stats
        test_habit_stats_empty,
        test_habit_stats_no_checkins,
        test_habit_stats_with_streaks,
        test_habit_stats_today_checkin,
        test_habit_stats_weekly_streak,
        test_habit_stats_missing_checkins_field,
        # Journal stats
        test_journal_stats_empty,
        test_journal_stats_with_entries,
        test_journal_stats_long_snippet,
        test_journal_stats_no_tags,
        test_journal_stats_top_tags_ordering,
        # Project stats
        test_project_stats_empty,
        test_project_stats_mixed_statuses,
        test_project_stats_progress,
        test_project_stats_best_progress_wins,
        test_project_stats_only_active_considered,
        test_project_stats_zero_tasks,
        test_project_stats_missing_tasks_field,
        # Full dashboard
        test_get_dashboard_all_empty,
        test_get_dashboard_mixed,
        test_get_dashboard_handles_missing_files,
        # Helpers
        test_snippet_short_text,
        test_snippet_long_text,
        test_snippet_newlines,
        test_snippet_empty,
        test_is_adjacent_daily_consecutive,
        test_is_adjacent_daily_skip,
        test_is_adjacent_weekly_within_7,
        test_is_adjacent_weekly_exceeds_7,
        test_is_adjacent_invalid_dates,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
        except Exception as e:
            print(f"💥 {test.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
