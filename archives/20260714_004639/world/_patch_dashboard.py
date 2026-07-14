"""Patch dashboard_engine.py, suite.py, and tests to include Time Blocker."""
import os

# ============================================================
# 1. dashboard_engine.py
# ============================================================
de_path = "dashboard_engine.py"
de_src = open(de_path).read()

# a) Add "time" to PATHS
old_paths = '"budget": "budget.json",\n}'
new_paths = '"budget": "budget.json",\n    "time": "time.json",\n}'
assert old_paths in de_src, "PATHS dict not found"
de_src = de_src.replace(old_paths, new_paths, 1)

# b) Add _time_stats() before get_dashboard()
time_stats_fn = '''
def _time_stats() -> dict:
    """Aggregate time block stats for the dashboard."""
    blocks = _safe_load(PATHS["time"])
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    today_day = days[date.today().weekday()]

    today_blocks = [b for b in blocks if b.get("day") == today_day]
    today_blocks.sort(key=lambda b: b.get("start", ""))

    # Count blocks per day
    day_counts = {}
    for b in blocks:
        d = b.get("day", "")
        if d:
            day_counts[d] = day_counts.get(d, 0) + 1

    busiest_day = max(day_counts, key=day_counts.get) if day_counts else None
    busiest_count = day_counts.get(busiest_day, 0) if busiest_day else 0

    # Find next upcoming block today
    now_minutes = date.today().hour * 60 + date.today().minute
    upcoming = None
    for b in today_blocks:
        start_str = b.get("start", "")
        if start_str and len(start_str) == 5:
            try:
                s_min = int(start_str[:2]) * 60 + int(start_str[3:])
                if s_min > now_minutes:
                    upcoming = b
                    break
            except ValueError:
                pass

    today_duration = sum(b.get("duration", 0) for b in today_blocks)
    total_duration = sum(b.get("duration", 0) for b in blocks)

    return {
        "total": len(blocks),
        "today_blocks": len(today_blocks),
        "today_duration": today_duration,
        "total_duration": total_duration,
        "busiest_day": busiest_day,
        "busiest_count": busiest_count,
        "upcoming_label": upcoming["label"] if upcoming else None,
        "upcoming_start": upcoming["start"] if upcoming else None,
    }


def get_dashboard():
'''

old_get = '\n\ndef get_dashboard():'
assert old_get in de_src, "get_dashboard not found"
de_src = de_src.replace(old_get, time_stats_fn, 1)

# c) Add "time" key to get_dashboard return dict
old_return = '"budget": _budget_stats(),\n    }'
new_return = '"budget": _budget_stats(),\n        "time": _time_stats(),\n    }'
assert old_return in de_src, "return dict not found"
de_src = de_src.replace(old_return, new_return, 1)

# d) Update docstring
old_doc = 'Returns a dict with keys: tasks, pomodoro, habits, journal, projects, budget.'
new_doc = 'Returns a dict with keys: tasks, pomodoro, habits, journal, projects, budget, time.'
de_src = de_src.replace(old_doc, new_doc, 1)

open(de_path, "w").write(de_src)
print("✅ dashboard_engine.py patched")

# ============================================================
# 2. suite.py
# ============================================================
suite_path = "suite.py"
suite_src = open(suite_path).read()

# a) Add _render_time before main()
render_time_fn = '''
def _render_time(stats: dict) -> list[str]:
    """Render time blocker section."""
    total = stats["total"]
    today = stats["today_blocks"]
    today_dur = stats["today_duration"]
    upcoming_label = stats["upcoming_label"]
    upcoming_start = stats["upcoming_start"]
    busiest_day = stats["busiest_day"]
    busiest_count = stats["busiest_count"]

    if total == 0:
        return ["  🕐  Time Blocks    no blocks yet"]

    lines = [f"  🕐  Time Blocks    {total} total · {today} today"]

    if upcoming_label:
        lines.append(f"       ⏰  Next: {upcoming_start} — {_snippet(upcoming_label, 28)}")

    if busiest_day and busiest_count > 0:
        day_label = busiest_day.title()
        lines.append(f"       📅  Busiest: {day_label} ({busiest_count} blocks)")

    if today_dur > 0:
        h = today_dur // 60
        m = today_dur % 60
        if m == 0:
            lines.append(f"       🕐  {h}h scheduled today")
        else:
            lines.append(f"       🕐  {h}h {m}m scheduled today")

    return lines


def main():
'''

old_main = '\n\ndef main():'
assert old_main in suite_src, "main not found"
suite_src = suite_src.replace(old_main, render_time_fn, 1)

# b) Add time section to main's sections list
old_sections = '("budget", _render_budget),\n    ]'
new_sections = '("budget", _render_budget),\n        ("time", _render_time),\n    ]'
assert old_sections in suite_src, "sections list not found"
suite_src = suite_src.replace(old_sections, new_sections, 1)

open(suite_path, "w").write(suite_src)
print("✅ suite.py patched")

# ============================================================
# 3. test_dashboard_engine.py
# ============================================================
test_path = "test_dashboard_engine.py"
test_src = open(test_path).read()

# a) Add time stats tests before the full dashboard tests section
time_tests = '''# ---------------------------------------------------------------------------
# Time blocker stats
# ---------------------------------------------------------------------------

def test_time_stats_empty():
    with patch.object(de, '_safe_load', return_value=[]):
        stats = de._time_stats()
        assert stats["total"] == 0
        assert stats["today_blocks"] == 0
        assert stats["today_duration"] == 0
        assert stats["total_duration"] == 0
        assert stats["busiest_day"] is None
        assert stats["busiest_count"] == 0


def test_time_stats_with_blocks():
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    today_day = days[date.today().weekday()]
    other_day = "mon" if today_day != "mon" else "tue"

    blocks = [
        {"id": 1, "day": today_day, "start": "09:00", "duration": 60, "label": "Standup"},
        {"id": 2, "day": today_day, "start": "14:00", "duration": 120, "label": "Deep work"},
        {"id": 3, "day": other_day, "start": "10:00", "duration": 30, "label": "Review"},
    ]
    with patch.object(de, '_safe_load', return_value=blocks):
        stats = de._time_stats()
        assert stats["total"] == 3
        assert stats["today_blocks"] == 2
        assert stats["today_duration"] == 180  # 60 + 120
        assert stats["total_duration"] == 210  # 60 + 120 + 30
        # Today has 2 blocks, other_day has 1 => busiest is today with 2
        assert stats["busiest_day"] == today_day
        assert stats["busiest_count"] == 2


# ---------------------------------------------------------------------------
# Full dashboard integration
# ---------------------------------------------------------------------------

'''

# Find insertion point: right before "# Full dashboard integration"
old_marker = "# ---------------------------------------------------------------------------\n# Full dashboard integration\n# ---------------------------------------------------------------------------"
assert old_marker in test_src, "marker not found"
test_src = test_src.replace(old_marker, time_tests + old_marker, 1)

# b) Update test_get_dashboard_all_empty to include "time" key
old_keys = 'assert set(dash.keys()) == {"tasks", "pomodoro", "habits", "journal", "projects", "budget"}'
new_keys = 'assert set(dash.keys()) == {"tasks", "pomodoro", "habits", "journal", "projects", "budget", "time"}'
assert old_keys in test_src, "keys assert not found"
test_src = test_src.replace(old_keys, new_keys, 1)

# c) Add time empty assertion
old_budget_assert = 'assert dash["budget"]["balance"] == 0.0'
new_budget_assert = 'assert dash["budget"]["balance"] == 0.0\n        assert dash["time"]["total"] == 0\n        assert dash["time"]["today_blocks"] == 0'
assert old_budget_assert in test_src, "budget assert not found"
test_src = test_src.replace(old_budget_assert, new_budget_assert, 1)

# d) Update test_get_dashboard_mixed fake_load to handle time.json
old_budget_return = 'elif path.endswith("budget.json"):\n            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]'
new_budget_return = 'elif path.endswith("budget.json"):\n            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]\n        elif path.endswith("time.json"):\n            return [{"id": 1, "day": "mon", "start": "09:00", "duration": 60, "label": "Meeting"}]'
assert old_budget_return in test_src, "budget return not found"
test_src = test_src.replace(old_budget_return, new_budget_return, 1)

# e) Add time assertions in test_get_dashboard_mixed
old_budget_mixed = 'assert dash["budget"]["balance"] == 100.0'
new_budget_mixed = 'assert dash["budget"]["balance"] == 100.0\n        assert dash["time"]["total"] == 1\n        assert dash["time"]["today_duration"] >= 0'
assert old_budget_mixed in test_src, "budget mixed assert not found"
test_src = test_src.replace(old_budget_mixed, new_budget_mixed, 1)

# f) Add time tests to the runner list
old_runner = 'test_get_dashboard_all_empty,\n        test_get_dashboard_mixed,'
new_runner = 'test_get_dashboard_all_empty,\n        test_get_dashboard_mixed,\n        # Time\n        test_time_stats_empty,\n        test_time_stats_with_blocks,'
assert old_runner in test_src, "runner list not found"
test_src = test_src.replace(old_runner, new_runner, 1)

open(test_path, "w").write(test_src)
print("✅ test_dashboard_engine.py patched")

print("\n✅ All three files patched successfully!")
