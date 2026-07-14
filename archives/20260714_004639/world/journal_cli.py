"""
journal_cli.py — Command-line interface for the Daily Journal.

Wires argparse to journal_engine + journal_store. Usage:
  python journal_cli.py write "Today was great." [--tags happy,productive]
  python journal_cli.py today
  python journal_cli.py read 2025-07-14
  python journal_cli.py search "great" [--tag happy]
  python journal_cli.py list [--tag productive]
  python journal_cli.py tags
  python journal_cli.py delete 2025-07-14
"""

import argparse
import sys
from datetime import date

from journal_store import load_entries, save_entries
from journal_engine import (
    add_entry,
    get_entry,
    delete_entry,
    search_entries,
    list_entries,
    list_tags,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

_BOOK = "📓"
_CALENDAR = "📅"
_TAG = "🏷"
_SEARCH = "🔍"
_TRASH = "🗑"
_PEN = "✍️"


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
    elif delta < 365:
        months = delta // 30
        return f"({months} month{'s' if months > 1 else ''} ago)"
    else:
        return ""


def _print_entry(entry, show_tags=True):
    """Pretty-print a single journal entry."""
    relative = _relative_day(entry["date"])
    print(f"\n  {_CALENDAR} {entry['date']} {relative}")
    print(f"  {'─' * 40}")
    # Wrap body nicely
    body = entry["body"]
    for line in body.split("\n"):
        print(f"  {line}")
    if show_tags and entry.get("tags"):
        tag_str = ", ".join(f"{_TAG} {t}" for t in entry["tags"])
        print(f"\n  {tag_str}")


def _tag_bar(tag_info):
    """Return a small visual bar for tag frequency."""
    if not tag_info:
        return
    max_count = tag_info[0]["count"]
    for t in tag_info:
        bar = "█" * t["count"] + "░" * (max_count - t["count"])
        print(f"  {_TAG} {t['tag']:15s} {bar} {t['count']}")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_write(args):
    """Write a new journal entry for today (or overwrite existing)."""
    entries = load_entries()
    today_str = date.today().isoformat()

    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    entries, entry = add_entry(entries, today_str, args.body, tags)
    save_entries(entries)

    if get_entry(entries, today_str) and len(entries) > 0:
        # Check if this was an overwrite by checking if we had it before
        print(f"{_PEN} Entry saved for {today_str} {_relative_day(today_str)}")
    else:
        print(f"{_PEN} Entry saved for {today_str} {_relative_day(today_str)}")


def cmd_today(args):
    """Show today's journal entry."""
    entries = load_entries()
    today_str = date.today().isoformat()
    entry = get_entry(entries, today_str)

    if entry is None:
        print(f"{_BOOK} No entry for today ({today_str}).")
        print(f"   Write one with: python journal_cli.py write \"Your thoughts...\"")
        return

    print(f"{_BOOK} Today's Entry:")
    _print_entry(entry)


def cmd_read(args):
    """Read a journal entry for a specific date."""
    entries = load_entries()
    entry = get_entry(entries, args.date)

    if entry is None:
        print(f"{_BOOK} No entry for {args.date}.")
        return

    print(f"{_BOOK} Entry for {args.date}:")
    _print_entry(entry)


def cmd_search(args):
    """Search journal entries by body text, with optional tag filter."""
    entries = load_entries()
    results = search_entries(entries, args.query, tag=args.tag)

    tag_hint = f" (tag: {_TAG} {args.tag})" if args.tag else ""
    print(f"\n{_SEARCH} Search results for \"{args.query}\"{tag_hint}:")
    print("═" * 50)

    if not results:
        print(f"  No entries found.")
        return

    print(f"  Found {len(results)} match{'es' if len(results) != 1 else ''}:")
    for entry in results:
        _print_entry(entry)


def cmd_list(args):
    """List all journal entries, optionally filtered by tag."""
    entries = load_entries()
    results = list_entries(entries, tag=args.tag)

    tag_hint = f" (tag: {_TAG} {args.tag})" if args.tag else ""
    print(f"\n{_BOOK} Journal Entries{tag_hint}:")
    print("═" * 50)

    if not results:
        print(f"  No entries yet. Write one with: python journal_cli.py write \"Your thoughts...\"")
        return

    print(f"  {len(results)} entr{'y' if len(results) == 1 else 'ies'}:")
    for entry in results:
        # Compact display for list
        relative = _relative_day(entry["date"])
        body_preview = entry["body"][:60] + ("..." if len(entry["body"]) > 60 else "")
        tag_str = ""
        if entry.get("tags"):
            tag_str = f"  [{', '.join(entry['tags'])}]"
        print(f"  {_CALENDAR} {entry['date']} {relative}  — {body_preview}{tag_str}")


def cmd_tags(args):
    """List all tags with usage counts."""
    entries = load_entries()
    tag_info = list_tags(entries)

    print(f"\n{_TAG} Journal Tags:")
    print("═" * 50)

    if not tag_info:
        print(f"  No tags yet. Add tags with: python journal_cli.py write \"...\" --tags tag1,tag2")
        return

    _tag_bar(tag_info)


def cmd_delete(args):
    """Delete a journal entry by date."""
    entries = load_entries()
    try:
        entries, removed = delete_entry(entries, args.date)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_entries(entries)
    print(f"{_TRASH} Deleted entry for {removed['date']} {_relative_day(removed['date'])}")
    print(f"   Body preview: {removed['body'][:60]}{'...' if len(removed['body']) > 60 else ''}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="journal",
        description="Daily Journal CLI 📓",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # write
    p_write = sub.add_parser("write", help="Write a journal entry for today")
    p_write.add_argument("body", help="The journal entry text")
    p_write.add_argument("--tags", help="Comma-separated tags, e.g. 'happy,productive'")

    # today
    sub.add_parser("today", help="Show today's journal entry")

    # read
    p_read = sub.add_parser("read", help="Read a journal entry for a specific date")
    p_read.add_argument("date", help="Date in YYYY-MM-DD format")

    # search
    p_search = sub.add_parser("search", help="Search journal entries by body text")
    p_search.add_argument("query", help="Search query (case-insensitive)")
    p_search.add_argument("--tag", help="Filter results by tag")

    # list
    p_list = sub.add_parser("list", help="List all journal entries")
    p_list.add_argument("--tag", help="Filter by tag")

    # tags
    sub.add_parser("tags", help="List all tags with usage counts")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a journal entry by date")
    p_delete.add_argument("date", help="Date in YYYY-MM-DD format")

    args = parser.parse_args()

    # Dispatch
    handlers = {
        "write": cmd_write,
        "today": cmd_today,
        "read": cmd_read,
        "search": cmd_search,
        "list": cmd_list,
        "tags": cmd_tags,
        "delete": cmd_delete,
    }

    handlers[args.command](args)


if __name__ == "__main__":
    main()
