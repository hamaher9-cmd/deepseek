"""
habit_cli.py — Command-line interface for the Habit Tracker.

Wires argparse to habit_engine + habit_store. Usage:
  python habit_cli.py add "Exercise" [--daily|--weekly]
  python habit_cli.py checkin "Exercise" [--date YYYY-MM-DD]
  python habit_cli.py list [--with-streaks]
  python habit_cli.py stats "Exercise"
  python habit_cli.py delete "Exercise"
"""

import argparse
import sys
from datetime import date

from habit_store import load_habits, save_habits
from habit_engine import (
    add_habit,
    checkin,
    list_habits,
    get_stats,
    delete_habit,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

_STREAK_BAR = "🔥"
_WEEKLY_MARKER = "📅"
_DAILY_MARKER = "📆"


def _freq_icon(freq: str) -> str:
    return _WEEKLY_MARKER if freq == "weekly" else _DAILY_MARKER


def _streak_str(current: int, best: int) -> str:
    return f"{_STREAK_BAR} current={current}  best={best}"


def _bar(n: int, max_n: int = 30) -> str:
    """Small visual bar for checkin counts."""
    if max_n == 0:
        return ""
    width = 20
    filled = min(round(n / max_n * width), width) if max_n else 0
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_add(args):
    habits = load_habits()
    freq = "weekly" if args.weekly else "daily"
    try:
        habits, new_h = add_habit(habits, args.name, freq)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_habits(habits)
    icon = _freq_icon(freq)
    print(f"{icon} Added habit: \"{args.name}\" ({freq})")


def cmd_checkin(args):
    habits = load_habits()
    try:
        habits, res = checkin(habits, args.name, args.date)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_habits(habits)
    if res["already"]:
        print(f"⏳ \"{args.name}\" already checked in on {res['date']}.")
    else:
        print(f"✅ Checked in \"{args.name}\" on {res['date']}.")


def cmd_list(args):
    habits = load_habits()
    if not habits:
        print("No habits tracked yet. Add one with: python habit_cli.py add \"Name\"")
        return

    result = list_habits(habits, with_streaks=args.with_streaks)
    print(f"\n📋 Your Habits ({len(result)}):")
    print("─" * 50)

    for h in result:
        icon = _freq_icon(h["frequency"])
        line = f"  {icon} {h['name']} ({h['frequency']}) — {h['total_checkins']} check-ins"
        if args.with_streaks:
            line += f"  {_streak_str(h['current'], h['best'])}"
        print(line)


def cmd_stats(args):
    habits = load_habits()
    try:
        s = get_stats(habits, args.name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    icon = _freq_icon(s["frequency"])
    print(f"\n📊 Stats for {icon} {s['name']}")
    print("─" * 40)
    print(f"  Frequency:       {s['frequency']}")
    print(f"  Created:         {s['created_at']}")
    print(f"  Total check-ins: {s['total_checkins']}")
    print(f"  Current streak:  {s['current_streak']} {_STREAK_BAR}")
    print(f"  Best streak:     {s['best_streak']} {_STREAK_BAR}")

    if s["checkins"]:
        print(f"\n  Check-in history ({len(s['checkins'])}):")
        for d in s["checkins"]:
            relative = _relative_day(d)
            print(f"    • {d} {relative}")
    else:
        print("\n  No check-ins yet.")


def _relative_day(date_str: str) -> str:
    """Return a human-readable label like '(today)' or '(3 days ago)'."""
    d = date.fromisoformat(date_str)
    delta = (date.today() - d).days
    if delta == 0:
        return "(today)"
    elif delta == 1:
        return "(yesterday)"
    elif delta < 7:
        return f"({delta} days ago)"
    elif delta < 30:
        weeks = delta // 7
        return f"({weeks} week{'s' if weeks > 1 else ''} ago)"
    else:
        return ""


def cmd_delete(args):
    habits = load_habits()
    try:
        habits, removed = delete_habit(habits, args.name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_habits(habits)
    icon = _freq_icon(removed["frequency"])
    print(f"🗑  Deleted habit: {icon} \"{removed['name']}\" "
          f"({removed['total_checkins']} check-ins)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="habit",
        description="Habit Tracker CLI 📊",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new habit")
    p_add.add_argument("name", help="Habit name")
    freq = p_add.add_mutually_exclusive_group()
    freq.add_argument("--daily", action="store_true", default=True,
                      help="Track daily (default)")
    freq.add_argument("--weekly", action="store_true",
                      help="Track weekly")
    p_add.set_defaults(func=cmd_add)

    # checkin
    p_ci = sub.add_parser("checkin", help="Check in to a habit")
    p_ci.add_argument("name", help="Habit name")
    p_ci.add_argument("--date", default=None,
                      help="Date as YYYY-MM-DD (default: today)")
    p_ci.set_defaults(func=cmd_checkin)

    # list
    p_list = sub.add_parser("list", help="List all habits")
    p_list.add_argument("--with-streaks", action="store_true",
                        help="Show current and best streaks")
    p_list.set_defaults(func=cmd_list)

    # stats
    p_stats = sub.add_parser("stats", help="Detailed stats for a habit")
    p_stats.add_argument("name", help="Habit name")
    p_stats.set_defaults(func=cmd_stats)

    # delete
    p_del = sub.add_parser("delete", help="Delete a habit")
    p_del.add_argument("name", help="Habit name")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
