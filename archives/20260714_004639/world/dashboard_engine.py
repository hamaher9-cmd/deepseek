"""
dashboard_engine.py — Unified stats aggregator for the Productivity Suite.

Reads from all seven JSON stores and returns a single aggregated
snapshot. All functions are pure: no side effects, no writes.
"""

import os
import json
from datetime import date


# --- File paths (mirrored from each store) ---
PATHS = {
    "tasks": "tasks.json",
    "sessions": "sessions.json",
    "habits": "habits.json",
    "journal": "journal.json",
    "projects": "projects.json",
    "budget": "budget.json",
    "time": "time_blocks.json",
}


def _safe_load(path: str) -> list[dict]:
    """Load a JSON file, returning [] on any failure."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _snippet(text: str, max_len: int = 80) -> str:
    """Truncate and clean text for display."""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rstrip() + "…"


# ---------------------------------------------------------------------------
# Per-tool aggregators
# ---------------------------------------------------------------------------

def _task_stats() -> dict:
    tasks = _safe_load(PATHS["tasks"])
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("done"))
    pending = total - done
    return {
        "total": total,
        "done": done,
        "pending": pending,
    }


def _pomodoro_stats() -> dict:
    sessions = _safe_load(PATHS["sessions"])
    today_str = date.today().isoformat()
    today_sessions = [s for s in sessions if s.get("date") == today_str]
    total_sessions = len(sessions)
    today_count = len(today_sessions)
    total_work = sum(s.get("work_minutes", 0) for s in sessions)
    today_work = sum(s.get("work_minutes", 0) for s in today_sessions)
    return {
        "total_sessions": total_sessions,
        "today_sessions": today_count,
        "total_work_minutes": total_work,
        "today_work_minutes": today_work,
    }


def _habit_stats() -> dict:
    habits = _safe_load(PATHS["habits"])
    today_str = date.today().isoformat()

    active = len(habits)
    best_streak = 0
    best_name = None
    best_frequency = "daily"

    for h in habits:
        checkins = sorted(h.get("checkins", []))
        if not checkins:
            continue
        freq = h.get("frequency", "daily")
        streak = 1
        for i in range(len(checkins) - 1, 0, -1):
            if checkins[i] == checkins[i - 1]:
                continue
            if _is_adjacent(checkins[i - 1], checkins[i], freq):
                streak += 1
            else:
                break
        if streak > best_streak:
            best_streak = streak
            best_name = h["name"]
            best_frequency = freq

    checked_in_today = sum(1 for h in habits if today_str in h.get("checkins", []))

    return {
        "active": active,
        "checked_in_today": checked_in_today,
        "top_streak_name": best_name,
        "top_streak_count": best_streak,
        "top_streak_frequency": best_frequency,
    }


def _is_adjacent(prev: str, curr: str, frequency: str) -> bool:
    """Check if two date strings are adjacent based on frequency."""
    from datetime import date as dt, timedelta
    try:
        p = dt.fromisoformat(prev)
        c = dt.fromisoformat(curr)
        delta = (c - p).days
        if frequency == "daily":
            return delta == 1
        else:
            return 1 <= delta <= 7
    except (ValueError, TypeError):
        return False


def _journal_stats() -> dict:
    entries = _safe_load(PATHS["journal"])
    total = len(entries)
    today_str = date.today().isoformat()
    today_entry = None
    latest = None
    for e in entries:
        d = e.get("date", "")
        content = e.get("content", "")
        if d == today_str:
            today_entry = content
        if latest is None or d > latest.get("date", ""):
            latest = {"date": d, "content": content}

    tag_counts = {}
    for e in entries:
        for tag in e.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "total": total,
        "today_entry": today_entry,
        "latest_date": latest["date"] if latest else None,
        "latest_snippet": (_snippet(latest["content"]) if latest else None),
        "tag_count": len(tag_counts),
        "top_tags": sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))[:5],
    }


def _project_stats() -> dict:
    projects = _safe_load(PATHS["projects"])
    active = sum(1 for p in projects if p.get("status") == "active")
    done = sum(1 for p in projects if p.get("status") == "done")
    archived = sum(1 for p in projects if p.get("status") == "archived")

    best_name = None
    best_pct = 0.0
    best_total = 0
    best_done = 0

    for p in projects:
        if p.get("status") != "active":
            continue
        tasks = p.get("tasks", [])
        t_total = len(tasks)
        t_done = sum(1 for t in tasks if t.get("done"))
        pct = (t_done / t_total * 100) if t_total > 0 else 0.0
        if t_total > 0 and pct > best_pct:
            best_pct = pct
            best_name = p["name"]
            best_total = t_total
            best_done = t_done
        elif best_name is None and t_total > 0:
            best_pct = pct
            best_name = p["name"]
            best_total = t_total
            best_done = t_done

    return {
        "total": len(projects),
        "active": active,
        "done": done,
        "archived": archived,
        "top_project_name": best_name,
        "top_project_pct": round(best_pct, 1),
        "top_project_done": best_done,
        "top_project_total": best_total,
    }


def _budget_stats() -> dict:
    transactions = _safe_load(PATHS["budget"])
    today_str = date.today().isoformat()
    this_month = today_str[:7]

    income_total = 0.0
    expense_total = 0.0
    month_income = 0.0
    month_expense = 0.0

    category_totals: dict[str, float] = {}

    for t in transactions:
        amt = t.get("amount", 0.0)
        cat = t.get("category", "uncategorized")
        t_type = t.get("type", "expense")
        t_date = t.get("date", "")

        category_totals[cat] = category_totals.get(cat, 0.0) + amt

        if t_type == "income":
            income_total += amt
            if t_date.startswith(this_month):
                month_income += amt
        else:
            expense_total += amt
            if t_date.startswith(this_month):
                month_expense += amt

    balance = round(income_total - expense_total, 2)
    income_total = round(income_total, 2)
    expense_total = round(expense_total, 2)
    month_income = round(month_income, 2)
    month_expense = round(month_expense, 2)

    top_cats = sorted(category_totals.items(), key=lambda x: -x[1])[:3]

    return {
        "total": len(transactions),
        "balance": balance,
        "income_total": income_total,
        "expense_total": expense_total,
        "month_income": month_income,
        "month_expense": month_expense,
        "this_month": this_month,
        "top_categories": top_cats,
    }


def _time_stats() -> dict:
    """Aggregate time block stats for the dashboard."""
    blocks = _safe_load(PATHS["time"])
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    today_day = days[date.today().weekday()]

    today_blocks = [b for b in blocks if b.get("day") == today_day]
    today_blocks.sort(key=lambda b: b.get("start", ""))

    # Count blocks per day
    day_counts: dict[str, int] = {}
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


def get_dashboard() -> dict:
    """Return aggregated stats from all seven productivity tools.

    Returns a dict with keys: tasks, pomodoro, habits, journal, projects, budget, time.
    Each value is a dict of stats for that tool.
    All tools are read fresh on every call.  No tool's absence is fatal.
    """
    return {
        "tasks": _task_stats(),
        "pomodoro": _pomodoro_stats(),
        "habits": _habit_stats(),
        "journal": _journal_stats(),
        "projects": _project_stats(),
        "budget": _budget_stats(),
        "time": _time_stats(),
    }
