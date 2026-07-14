"""Add Time Blocker integration to dashboard_engine.py, suite.py, and tests."""

import dashboard_engine as de
import suite

# ==============================================================================
# 1. dashboard_engine.py — add PATHS entry
# ==============================================================================

de_src = open("dashboard_engine.py").read()

# Add "time" to PATHS dict (after "budget")
old_paths = '"budget": "budget.json",\n}'
new_paths = '"budget": "budget.json",\n    "time": "time.json",\n}'
assert old_paths in de_src, "PATHS line not found"
de_src = de_src.replace(old_paths, new_paths, 1)

# Add _time_stats function before get_dashboard
time_stats_fn = '''
def _time_stats() -> dict:
    """Aggregate time block stats for the dashboard."""
    from time_engine import list_day
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

# Replace the "def get_dashboard():" with the new function + updated get_dashboard
old_get = '\n\ndef get_dashboard():'
assert old_get in de_src, "get_dashboard not found"
de_src = de_src.replace(old_get, time_stats_fn, 1)

# Add "time" key to get_dashboard return dict
old_return = '"budget": _budget_stats(),\n    }'
new_return = '"budget": _budget_stats(),\n        "time": _time_stats(),\n    }'
assert old_return in de_src, "return dict not found"
de_src = de_src.replace(old_return, new_return, 1)

# Update docstring
old_docstring = 'Returns a dict with keys: tasks, pomodoro, habits, journal, projects, budget.'
new_docstring = 'Returns a dict with keys: tasks, pomodoro, habits, journal, projects, budget, time.'
de_src = de_src.replace(old_docstring, new_docstring, 1)

open("dashboard_engine.py", "w").write(de_src)
print("✅ dashboard_engine.py updated")

# ==============================================================================
# 2. suite.py — add _render_time and update main()
# ==============================================================================

suite_src = open("suite.py").read()

# Add _render_time before main()
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

# Add time section to main's sections list
old_sections_end = '("budget", _render_budget),\n    ]'
new_sections_end = '("budget", _render_budget),\n        ("time", _render_time),\n    ]'
assert old_sections_end in suite_src, "sections list not found"
suite_src = suite_src.replace(old_sections_end, new_sections_end, 1)

open("suite.py", "w").write(suite_src)
print("✅ suite.py updated")

# ==============================================================================
# 3. test_dashboard_engine.py — add time key expectations
# ==============================================================================

test_src = open("test_dashboard_engine.py").read()

# Update key assertion in test_get_dashboard_all_empty
old_keys = '{"tasks", "pomodoro", "habits", "journal", "projects", "budget"}'
new_keys = '{"tasks", "pomodoro", "habits", "journal", "projects", "budget", "time"}'
assert old_keys in test_src, "keys assertion not found in empty test"
test_src = test_src.replace(old_keys, new_keys, 1)

# Add time assertions in all_empty test
old_empty_end = 'assert dash["budget"]["balance"] == 0.0'
new_empty_end = 'assert dash["budget"]["balance"] == 0.0\n        assert dash["time"]["total"] == 0\n        assert dash["time"]["today_blocks"] == 0'
assert old_empty_end in test_src, "budget balance assertion not found"
test_src = test_src.replace(old_empty_end, new_empty_end, 1)

# Add time.json in fake_load for mixed test
old_budget_return = 'elif path.endswith("budget.json"):\n            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]'
new_budget_return = 'elif path.endswith("time.json"):\n            return [{"id": 1, "day": "mon", "start": "09:00", "duration": 60, "label": "Standup"}]\n        elif path.endswith("budget.json"):\n            return [{"id": 1, "type": "income", "amount": 100.0, "category": "salary", "date": today}]'
assert old_budget_return in test_src, "budget fake_load not found"
test_src = test_src.replace(old_budget_return, new_budget_return, 1)

# Add time assertions in mixed test
old_mixed_end = 'assert dash["budget"]["balance"] == 100.0'
new_mixed_end = 'assert dash["budget"]["balance"] == 100.0\n        assert dash["time"]["total"] == 1\n        assert dash["time"]["busiest_day"] == "mon"'
assert old_mixed_end in test_src, "mixed budget assertion not found"
test_src = test_src.replace(old_mixed_end, new_mixed_end, 1)

open("test_dashboard_engine.py", "w").write(test_src)
print("✅ test_dashboard_engine.py updated")
print("\nAll done! Time Blocker now integrated into dashboard.")
