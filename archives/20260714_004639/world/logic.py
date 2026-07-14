"""
logic.py — Task CRUD operations for the Task Manager.

Sits between storage.py and cli.py. Every function loads, mutates, saves.
"""

from storage import load_tasks, save_tasks, next_id


def add_task(text: str) -> dict:
    """Add a new task. Returns the created task dict."""
    tasks = load_tasks()
    task = {"id": next_id(tasks), "text": text.strip(), "done": False}
    tasks.append(task)
    save_tasks(tasks)
    return task


def list_tasks(show_done: bool = True) -> list[dict]:
    """Return all tasks, or only pending ones if show_done=False."""
    tasks = load_tasks()
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    return tasks


def mark_done(task_id: int) -> dict | None:
    """Mark a task as done by ID. Returns the task or None if not found."""
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            return t
    return None


def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Returns True if deleted, False if not found."""
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            del tasks[i]
            save_tasks(tasks)
            return True
    return False
