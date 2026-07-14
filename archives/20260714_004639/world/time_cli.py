"""
time_cli.py — Command-line interface for the Time Blocker.

Wires argparse to time_engine + time_store. Usage:
  python time_cli.py add <day> <HH:MM> <mins> <label> [--task-id N]
  python time_cli.py day <day>
  python time_cli.py week
  python time_cli.py delete <id>
  python time_cli.py conflicts <day>
"""

import argparse
import sys

from time_store import load_blocks, save_blocks
from time_engine import (
    add_block,
    delete_block,
    list_day,
    list_week,
    find_conflicts,
    VALID_DAYS,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

DAY_NAMES = {
    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
    "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday",
}

DAY_ICONS = {
    "mon": "📅", "tue": "📅", "wed": "📅", "thu": "📅",
    "fri": "🎉", "sat": "🌞", "sun": "🌻",
}

BLOCK_ICON = "🕐"
CONFLICT_ICON = "⚠️"


def _day_label(day: str) -> str:
    icon = DAY_ICONS.get(day, "📅")
    name = DAY_NAMES.get(day, day.capitalize())
    return f"{icon} {name}"


def _fmt_minutes(total_minutes: int) -> str:
    """Format minutes as 'Xh Ym' or 'Xm'."""
    if total_minutes <= 0:
        return "0m"
    h = total_minutes // 60
    m = total_minutes % 60
    if h and m:
        return f"{h}h {m}m"
    elif h:
        return f"{h}h"
    else:
        return f"{m}m"


def _fmt_block_line(block, show_day=False) -> str:
    """Format a single block for display."""
    start = block["start"]
    dur = block["duration"]
    label = block["label"]
    task_id = block["task_id"]
    task_str = f" [task #{task_id}]" if task_id else ""
    day_str = f" {block['day']} " if show_day else ""
    return (f"  {BLOCK_ICON} #{block['id']}{day_str}"
            f"{start} · {_fmt_minutes(dur)} · {label}{task_str}")


def _bar(percent: float, width: int = 16) -> str:
    """Visual progress/occupancy bar."""
    filled = min(round(percent / 100 * width), width) if percent > 0 else 0
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Day view — vertical time grid
# ---------------------------------------------------------------------------

def _render_day_grid(blocks, day):
    """Render a 24-hour vertical time grid with blocks overlaid."""
    print(f"\n{_day_label(day)}")
    print("─" * 54)

    # Build a map: hour -> list of block labels for that hour
    # Each block occupies its duration in minutes from start
    hour_slots = {h: [] for h in range(24)}

    for b in blocks:
        start_h, start_m = map(int, b["start"].split(":"))
        end_minutes = start_h * 60 + start_m + b["duration"]
        end_h = end_minutes // 60
        # Fractional coverage for the start hour
        frac_start = (60 - start_m) / 60 if start_m > 0 else 1.0

        for h in range(start_h, min(end_h + 1, 24)):
            if h == start_h and start_m > 0:
                hour_slots[h].append((frac_start, b))
            elif h == end_h and end_minutes % 60 != 0:
                frac = (end_minutes % 60) / 60
                hour_slots[h].append((frac, b))
            elif h < end_h or h == start_h:
                hour_slots[h].append((1.0, b))

    for hour in range(24):
        hour_label = f"{hour:02d}:00"
        slot = hour_slots[hour]

        if not slot:
            print(f"  {hour_label} │")
            continue

        # Take the most dominant block for this hour
        best_frac, best_block = max(slot, key=lambda x: x[0])
        label = best_block["label"]
        bar_width = max(1, round(best_frac * 28))
        bar_seg = "█" * bar_width
        # Truncate label if needed
        display = label[:28] if len(label) > 28 else label
        print(f"  {hour_label} │ {bar_seg} {display}")

    print("─" * 54)

    # Block detail list
    total_minutes = sum(b["duration"] for b in blocks)
    print(f"  {len(blocks)} block(s) · {_fmt_minutes(total_minutes)} total")
    for b in blocks:
        print(_fmt_block_line(b))


# ---------------------------------------------------------------------------
# Week view — compact 7-column overview
# ---------------------------------------------------------------------------

def _render_week_overview(week_data):
    """Render a compact 7-day overview."""
    print("\n🕐 Week Overview")
    print("─" * 80)
    header = ""
    for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        header += f"  {day.upper():<9}"
    print(header)
    print("  " + "─" * 70)

    # Find max blocks across days
    max_blocks = max((len(week_data[d]) for d in week_data), default=1)
    if max_blocks == 0:
        max_blocks = 1

    for row in range(max_blocks):
        line = ""
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            if row < len(week_data[day]):
                b = week_data[day][row]
                entry = f"{b['start']} {b['label'][:6]:<6}"
                line += f"  {entry:<9}"
            else:
                line += "  " + " " * 9
        if line.strip():
            print(line)

    print("  " + "─" * 70)

    # Totals row
    totals = ""
    for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        blocks = week_data[day]
        total_m = sum(b["duration"] for b in blocks)
        totals += f"  {len(blocks)}blk {_fmt_minutes(total_m):>5}"
    print(totals)
    print()


# ---------------------------------------------------------------------------
# Conflicts view
# ---------------------------------------------------------------------------

def _render_conflicts(blocks, day):
    """Find and display all overlapping blocks on a day."""
    print(f"\n{CONFLICT_ICON} Conflicts for {_day_label(day)}")
    print("─" * 54)

    # Check all pairs
    conflicts_found = []
    seen_pairs = set()
    day_blocks = [b for b in blocks if b["day"] == day]
    day_blocks.sort(key=lambda b: b["start"])

    for i, a in enumerate(day_blocks):
        for j, b in enumerate(day_blocks):
            if i >= j:
                continue
            pair_key = (a["id"], b["id"])
            if pair_key in seen_pairs:
                continue
            # Check if they overlap
            from time_engine import _overlap
            if _overlap(a["start"], a["duration"], b["start"], b["duration"]):
                seen_pairs.add(pair_key)
                conflicts_found.append((a, b))

    if not conflicts_found:
        print(f"  ✅ No conflicts on {DAY_NAMES.get(day, day)}.")
        return

    print(f"  Found {len(conflicts_found)} overlap(s):\n")
    for a, b in conflicts_found:
        a_end_h = (int(a["start"].split(":")[0]) * 60 + int(a["start"].split(":")[1]) + a["duration"]) // 60
        a_end_m = (int(a["start"].split(":")[0]) * 60 + int(a["start"].split(":")[1]) + a["duration"]) % 60
        a_end = f"{a_end_h:02d}:{a_end_m:02d}"
        print(f"  {CONFLICT_ICON} #{a['id']} {a['start']}-{a_end} {a['label']}")
        print(f"    ╰─ #{b['id']} {b['start']} {_fmt_minutes(b['duration'])} {b['label']}")
        print()


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_add(args):
    """Add a new time block."""
    blocks = load_blocks()
    try:
        blocks, block = add_block(
            blocks, args.day, args.start, args.duration, args.label, args.task_id
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Check for conflicts
    conflicts = find_conflicts(blocks, args.day, args.start, args.duration)
    # Exclude the block we just added
    conflicts = [c for c in conflicts if c["id"] != block["id"]]

    save_blocks(blocks)
    print(f"{BLOCK_ICON} Added #{block['id']}: {_day_label(block['day'])} "
          f"{block['start']} · {_fmt_minutes(block['duration'])} · {block['label']}"
          + (f" [task #{block['task_id']}]" if block.get('task_id') else ""))

    if conflicts:
        print(f"\n  {CONFLICT_ICON} Conflicts detected with:")
        for c in conflicts:
            print(f"    #{c['id']} {c['start']} · {_fmt_minutes(c['duration'])} · {c['label']}")


def cmd_day(args):
    """Show time grid for a specific day."""
    blocks = load_blocks()
    try:
        day_blocks = list_day(blocks, args.day)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not day_blocks:
        print(f"\n{_day_label(args.day)}")
        print("─" * 30)
        print(f"  No blocks scheduled. Add one with:")
        print(f"  python time_cli.py add {args.day} 09:00 60 \"Deep Work\"")
        return

    _render_day_grid(day_blocks, args.day)


def cmd_week(args):
    """Show a 7-day overview."""
    blocks = load_blocks()
    week_data = list_week(blocks)

    total_blocks = sum(len(v) for v in week_data.values())
    if total_blocks == 0:
        print("\n🕐 Week Overview")
        print("─" * 30)
        print("  No blocks scheduled. Add one with:")
        print("  python time_cli.py add mon 09:00 60 \"Deep Work\"")
        return

    _render_week_overview(week_data)


def cmd_delete(args):
    """Delete a block by id."""
    blocks = load_blocks()
    blocks, removed = delete_block(blocks, args.id)

    if removed is None:
        print(f"No block found with id #{args.id}.")
        sys.exit(1)

    save_blocks(blocks)
    print(f"🗑️ Deleted #{removed['id']}: {_day_label(removed['day'])} "
          f"{removed['start']} · {removed['label']}")


def cmd_conflicts(args):
    """Show all overlapping blocks on a day."""
    blocks = load_blocks()
    try:
        # Validate day
        if args.day not in VALID_DAYS:
            print(f"Error: Invalid day '{args.day}'. Must be one of: {', '.join(sorted(VALID_DAYS))}.")
            sys.exit(1)
    except (ValueError, AttributeError):
        pass
    _render_conflicts(blocks, args.day)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="time",
        description="🕐 Time Blocker — schedule your week in blocks",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a time block")
    p_add.add_argument("day", choices=sorted(VALID_DAYS), help="Day of week")
    p_add.add_argument("start", help="Start time (HH:MM)")
    p_add.add_argument("duration", type=int, help="Duration in minutes")
    p_add.add_argument("label", help="Block label")
    p_add.add_argument("--task-id", type=int, default=None, help="Linked task ID")

    # day
    p_day = sub.add_parser("day", help="Show time grid for a day")
    p_day.add_argument("day", choices=sorted(VALID_DAYS), help="Day of week")

    # week
    sub.add_parser("week", help="Show 7-day overview")

    # delete
    p_del = sub.add_parser("delete", help="Delete a block by ID")
    p_del.add_argument("id", type=int, help="Block ID to delete")

    # conflicts
    p_conf = sub.add_parser("conflicts", help="Show overlapping blocks on a day")
    p_conf.add_argument("day", choices=sorted(VALID_DAYS), help="Day of week")

    args = parser.parse_args()

    handlers = {
        "add": cmd_add,
        "day": cmd_day,
        "week": cmd_week,
        "delete": cmd_delete,
        "conflicts": cmd_conflicts,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
