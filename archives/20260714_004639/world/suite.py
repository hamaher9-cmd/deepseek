"""
suite.py — Unified Productivity Dashboard CLI.

Single command: python suite.py
Surfaces stats from all six tools at a glance.
"""

from datetime import date
from dashboard_engine import get_dashboard


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def _bar(done: int, total: int, width: int = 10) -> str:
    """Render a █░ progress bar."""
    if total == 0:
        return "░" * width
    filled = round(done / total * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def _pct(done: int, total: int) -> str:
    """Return percentage string or '—' if no total."""
    if total == 0:
        return "—"
    return f"{round(done / total * 100)}%"


def _relative_day(date_str: str) -> str:
    """Return a human-readable label like 'today' or '3d ago'."""
    if not date_str:
        return ""
    try:
        d = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return ""
    delta = (date.today() - d).days
    if delta == 0:
        return "today"
    elif delta == 1:
        return "yesterday"
    elif delta < 7:
        return f"{delta}d ago"
    elif delta < 30:
        weeks = delta // 7
        return f"{weeks}w ago"
    else:
        return date_str


def _snippet(text: str, max_len: int = 50) -> str:
    """Truncate and clean text for display."""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rstrip() + "…"


def _fmt_money(amount: float) -> str:
    """Format a dollar amount with sign and 2 decimals."""
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_tasks(stats: dict) -> list[str]:
    total = stats["total"]
    done = stats["done"]
    pending = stats["pending"]
    bar = _bar(done, total, 12)
    if total == 0:
        return ["  📋  Tasks          no tasks yet"]
    return [
        f"  📋  Tasks          {pending} pending · {done} done",
        f"       [{bar}] {_pct(done, total)} done",
    ]


def _render_pomodoro(stats: dict) -> list[str]:
    today = stats["today_sessions"]
    total = stats["total_sessions"]
    work_today = stats["today_work_minutes"]
    work_all = stats["total_work_minutes"]

    if total == 0:
        return ["  🍅  Pomodoro       no sessions yet"]

    lines = [f"  🍅  Pomodoro       {today} today · {total} total"]
    if today > 0:
        bar = _bar(work_today, max(120, work_today), 10)
        lines.append(f"       [{bar}] {work_today} min today")
    else:
        lines.append(f"       {work_all} min total · none today")
    return lines


def _render_habits(stats: dict) -> list[str]:
    active = stats["active"]
    checked = stats["checked_in_today"]
    top_name = stats["top_streak_name"]
    top_streak = stats["top_streak_count"]
    top_freq = stats["top_streak_frequency"]

    if active == 0:
        return ["  📊  Habits         no habits yet"]

    freq_icon = "📅" if top_freq == "weekly" else "📆"
    lines = [f"  📊  Habits         {active} active · {checked} checked in today"]

    if top_name and top_streak > 0:
        lines.append(f"       🔥 {top_name}: {top_streak}-day streak {freq_icon}")
    return lines


def _render_journal(stats: dict) -> list[str]:
    total = stats["total"]
    latest_date = stats["latest_date"]
    latest_snippet = stats["latest_snippet"]
    today_entry = stats["today_entry"]
    tag_count = stats["tag_count"]
    top_tags = stats["top_tags"]

    if total == 0:
        return ["  📓  Journal        no entries yet"]

    lines = [f"  📓  Journal        {total} entries · {tag_count} tags"]

    if today_entry:
        lines.append(f"       ✏️  Today: \"{_snippet(today_entry, 40)}\"")
    elif latest_date and latest_snippet:
        rel = _relative_day(latest_date)
        lines.append(f"       Last {rel}: \"{_snippet(latest_snippet, 40)}\"")

    if top_tags:
        tag_str = " · ".join(f"#{t}" for t, _ in top_tags[:3])
        lines.append(f"       🏷  {tag_str}")
    return lines


def _render_projects(stats: dict) -> list[str]:
    active = stats["active"]
    done = stats["done"]
    archived = stats["archived"]
    total = stats["total"]
    top_name = stats["top_project_name"]
    top_pct = stats["top_project_pct"]
    top_done = stats["top_project_done"]
    top_total = stats["top_project_total"]

    if total == 0:
        return ["  🗂️  Projects       no projects yet"]

    lines = [f"  🗂️  Projects       {active} active · {done} done · {archived} archived"]

    if top_name and top_total > 0:
        bar = _bar(top_done, top_total, 10)
        lines.append(f"       [{bar}] {top_pct}% — {_snippet(top_name, 30)}")
    return lines


def _render_budget(stats: dict) -> list[str]:
    total = stats["total"]
    balance = stats["balance"]
    month_income = stats["month_income"]
    month_expense = stats["month_expense"]
    top_categories = stats["top_categories"]

    if total == 0:
        return ["  💰  Budget         no transactions yet"]

    # Main line: balance with sign
    balance_str = _fmt_money(balance)
    if balance >= 0:
        bal_display = f"balance {balance_str} 👍"
    else:
        bal_display = f"balance {balance_str} ⚠️"

    lines = [f"  💰  Budget         {total} txn · {bal_display}"]

    # Monthly summary
    month = stats["this_month"]
    month_label = f"{date.today():%b %Y}"
    lines.append(
        f"       {month_label}: +{_fmt_money(month_income)} / -{_fmt_money(month_expense)}"
    )

    # Top category if any
    if top_categories:
        cat_name, cat_amt = top_categories[0]
        lines.append(f"       🏷  top: {cat_name} ({_fmt_money(cat_amt)})")

    return lines


# ---------------------------------------------------------------------------
# Main display
# ---------------------------------------------------------------------------

def main():
    d = get_dashboard()

    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║     📊  PRODUCTIVITY SUITE       ║")
    print("  ╠══════════════════════════════════╣")

    sections = [
        ("tasks", _render_tasks),
        ("pomodoro", _render_pomodoro),
        ("habits", _render_habits),
        ("journal", _render_journal),
        ("projects", _render_projects),
        ("budget", _render_budget),
    ]

    for i, (key, render_fn) in enumerate(sections):
        for line in render_fn(d[key]):
            print(f"  ║{line}")

    print("  ╚══════════════════════════════════╝")
    print()


if __name__ == "__main__":
    main()
