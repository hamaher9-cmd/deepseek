"""
cli.py — Command-line interface for the Task Manager.

Wires argparse to logic.py. Usage:
  python cli.py add "Buy milk"
  python cli.py list [--all]
  python cli.py done 3
  python cli.py delete 2
"""

import argparse
import sys
from logic import add_task, list_tasks, mark_done, delete_task


def cmd_add(args):
    task = add_task(args.text)
    print(f"Added #{task['id']}: {task['text']}")


def cmd_list(args):
    tasks = list_tasks(show_done=args.all)
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        marker = "[x]" if t["done"] else "[ ]"
        print(f"  {t['id']}. {marker} {t['text']}")


def cmd_done(args):
    task = mark_done(args.id)
    if task is None:
        print(f"No task with id {args.id}.")
        sys.exit(1)
    print(f"Marked #{task['id']} done: {task['text']}")


def cmd_delete(args):
    ok = delete_task(args.id)
    if not ok:
        print(f"No task with id {args.id}.")
        sys.exit(1)
    print(f"Deleted #{args.id}.")


def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="Simple Task Manager CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("text", help="Task description")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--all", action="store_true", help="Show done tasks too")
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    # delete
    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
