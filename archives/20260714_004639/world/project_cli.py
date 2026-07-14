"""
project_cli.py — Command-line interface for the Project Tracker.

Wires argparse to project_engine + project_store. Usage:
  python project_cli.py add "Build a website" [--deadline 2025-08-01]
  python project_cli.py task "Build a website" "Design mockups"
  python project_cli.py done "Build a website" 1
  python project_cli.py undo "Build a website" 1
  python project_cli.py list [--active|--done|--archived|--all]
  python project_cli.py stats "Build a website"
  python project_cli.py delete "Build a website"
"""

import argparse
import sys
from datetime import date

from project_store import load_projects, save_projects
from project_engine import (
    add_project,
    delete_project,
    list_projects,
    set_project_status,
    add_task,
    mark_task_done,
    undo_task,
    get_stats,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

_FOLDER = "🗂️"
_CHECK = "✅"
_EMPTY = "⬜"
_TRASH = "🗑"
_DATE = "📅"
_ROCKET = "🚀"
_WARN = "⚠️"
_BAR_WIDTH = 20


def _status_icon(status: str) -> str:
    icons = {"active": "🟢", "done": "✅", "archived": "📦"}
    return icons.get(status, "❓")


def _progress_bar(done: int, total: int) -> str:
    """Render a progress bar like ████████░░░░░░░░░░ 40.0%"""
    if total == 0:
        return "░" * _BAR_WIDTH + "   0.0%"
    filled = round(done / total * _BAR_WIDTH)
    bar = "█" * filled + "░" * (_BAR_WIDTH - filled)
    pct = done / total * 100
    return f"{bar} {pct:.1f}%"


def _relative_day(date_str: str) -> str:
    """Return a human-readable label like '(today)' or '(3 days ago)'."""
    if not date_str:
        return ""
    d = date.fromisoformat(date_str)
    delta = (date.today() - d).days
    if delta == 0:
        return "(today)"
    elif delta == 1:
        return "(yesterday)"
    elif delta == -1:
        return "(tomorrow)"
    elif delta < -1:
        return f"(in {-delta} days)"
    elif delta < 7:
        return f"({delta} days ago)"
    elif delta < 30:
        weeks = delta // 7
        return f"({weeks} week{'s' if weeks > 1 else ''} ago)"
    else:
        return ""


def _find_project(projects, name):
    """Return project dict by name, or None."""
    for p in projects:
        if p["name"] == name:
            return p
    return None


def _print_project(p, show_tasks=True):
    """Pretty-print a single project."""
    icon = _status_icon(p["status"])
    tasks = p["tasks"]
    done_count = sum(1 for t in tasks if t["done"])
    total = len(tasks)

    print(f"\n  {icon} {p['name']} [{p['status']}]")
    print(f"  {'─' * 50}")

    if p.get("deadline"):
        rel = _relative_day(p["deadline"])
        print(f"  {_DATE} Deadline: {p['deadline']} {rel}")

    if total > 0:
        bar = _progress_bar(done_count, total)
        print(f"  Tasks: {done_count}/{total} done  {bar}")
    else:
        print(f"  Tasks: none yet")

    if show_tasks and tasks:
        for t in tasks:
            marker = _CHECK if t["done"] else _EMPTY
            print(f"    {marker} [{t['id']}] {t['title']}")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_add(args):
    """Add a new project."""
    projects = load_projects()
    try:
        projects, p = add_project(projects, args.name, deadline=args.deadline)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_projects(projects)
    deadline_str = f" (deadline: {args.deadline})" if args.deadline else ""
    print(f"{_FOLDER} Created project: \"{args.name}\"{deadline_str}")


def cmd_task(args):
    """Add a task to a project."""
    projects = load_projects()
    try:
        projects, task = add_task(projects, args.project, args.title)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_projects(projects)
    print(f"{_EMPTY} Added task [{task['id']}] \"{task['title']}\" to \"{args.project}\"")


def cmd_done(args):
    """Mark a task as done."""
    projects = load_projects()
    try:
        projects, task = mark_task_done(projects, args.project, args.task_id)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_projects(projects)
    print(f"{_CHECK} Marked [{args.task_id}] \"{task['title']}\" as done in \"{args.project}\"")


def cmd_undo(args):
    """Mark a task as not done."""
    projects = load_projects()
    try:
        projects, task = undo_task(projects, args.project, args.task_id)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_projects(projects)
    print(f"{_EMPTY} Undid [{args.task_id}] \"{task['title']}\" in \"{args.project}\"")


def cmd_list(args):
    """List projects with optional status filter."""
    projects = load_projects()
    if not projects:
        print("No projects yet. Add one with: python project_cli.py add \"Project Name\"")
        return

    # Determine filter
    status = None
    if args.active:
        status = "active"
    elif args.done:
        status = "done"
    elif args.archived:
        status = "archived"
    # --all or default: status stays None

    filtered = list_projects(projects, status=status)

    if not filtered:
        labels = {None: "No projects", "active": "No active projects",
                  "done": "No done projects", "archived": "No archived projects"}
        print(labels.get(status, "No projects") + ".")
        return

    for p in filtered:
        _print_project(p, show_tasks=True)


def cmd_stats(args):
    """Show detailed stats for a project."""
    projects = load_projects()

    # get_stats gives aggregate numbers
    try:
        s = get_stats(projects, args.name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Grab the full project for created_at + task list
    p = _find_project(projects, args.name)

    icon = _status_icon(s["status"])
    done = s["done"]
    total = s["total"]
    bar = _progress_bar(done, total)

    print(f"\n  {icon} {s['name']} [{s['status']}]")
    print(f"  {'─' * 50}")
    if p and p.get("created_at"):
        print(f"  Created:   {p['created_at']} {_relative_day(p['created_at'])}")
    if s.get("deadline"):
        print(f"  {_DATE} Deadline: {s['deadline']} {_relative_day(s['deadline'])}")
    print(f"  Tasks:     {done}/{total} done")
    print(f"  Progress:  {bar}")

    if p and p["tasks"]:
        print(f"\n  Tasks:")
        for t in p["tasks"]:
            marker = _CHECK if t["done"] else _EMPTY
            print(f"    {marker} [{t['id']}] {t['title']}")
    else:
        print(f"\n  {_WARN} No tasks yet. Add one with:")
        print(f"    python project_cli.py task \"{s['name']}\" \"Task title\"")


def cmd_delete(args):
    """Delete a project."""
    projects = load_projects()
    try:
        projects, removed = delete_project(projects, args.name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_projects(projects)
    print(f"{_TRASH} Deleted project: \"{removed['name']}\"")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="project", description="Project Tracker")
    sub = parser.add_subparsers(dest="command")

    # add
    sp = sub.add_parser("add", help="Create a new project")
    sp.add_argument("name", help="Project name")
    sp.add_argument("--deadline", default=None, help="Deadline (YYYY-MM-DD)")
    sp.set_defaults(func=cmd_add)

    # task
    sp = sub.add_parser("task", help="Add a task to a project")
    sp.add_argument("project", help="Project name")
    sp.add_argument("title", help="Task title")
    sp.set_defaults(func=cmd_task)

    # done
    sp = sub.add_parser("done", help="Mark a task as done")
    sp.add_argument("project", help="Project name")
    sp.add_argument("task_id", type=int, help="Task ID")
    sp.set_defaults(func=cmd_done)

    # undo
    sp = sub.add_parser("undo", help="Mark a task as not done")
    sp.add_argument("project", help="Project name")
    sp.add_argument("task_id", type=int, help="Task ID")
    sp.set_defaults(func=cmd_undo)

    # list
    sp = sub.add_parser("list", help="List projects")
    group = sp.add_mutually_exclusive_group()
    group.add_argument("--active", action="store_true", help="Show active only")
    group.add_argument("--done", action="store_true", help="Show done only")
    group.add_argument("--archived", action="store_true", help="Show archived only")
    group.add_argument("--all", action="store_true", help="Show all projects")
    sp.set_defaults(func=cmd_list)

    # stats
    sp = sub.add_parser("stats", help="Show project statistics")
    sp.add_argument("name", help="Project name")
    sp.set_defaults(func=cmd_stats)

    # delete
    sp = sub.add_parser("delete", help="Delete a project")
    sp.add_argument("name", help="Project name")
    sp.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
