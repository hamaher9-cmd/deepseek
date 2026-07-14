"""Project engine: project CRUD, task CRUD, progress calc, filtering.

All functions are pure: they take a list of project dicts plus arguments
and return (projects, result). Never touches the filesystem directly.

Project dict format:
    {
        "name": "Build a website",
        "status": "active",        # active, done, archived
        "created_at": "2025-07-21",
        "deadline": "2025-08-01",  # optional, None if unset
        "tasks": [
            {"id": 1, "title": "Design mockups", "done": False},
            {"id": 2, "title": "Code frontend", "done": True},
        ]
    }
"""

from datetime import date


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_index(projects, name):
    """Return index of project with given name, or None if missing."""
    for i, p in enumerate(projects):
        if p["name"] == name:
            return i
    return None


def _find_task(task_list, task_id):
    """Return (index, task) for *task_id*, or (None, None) if missing."""
    for i, t in enumerate(task_list):
        if t["id"] == task_id:
            return i, t
    return None, None


def _next_task_id(task_list):
    """Return the next available task id (max + 1, or 1 if empty)."""
    if not task_list:
        return 1
    return max(t["id"] for t in task_list) + 1


def _today_str():
    """Return today's date as ISO string."""
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

def add_project(projects, name, deadline=None):
    """Create a new project with *name* and optional *deadline*.

    Returns (projects, project_dict).

    Raises ValueError if a project with *name* already exists.
    """
    if _find_index(projects, name) is not None:
        raise ValueError(f"Project '{name}' already exists.")

    project = {
        "name": name,
        "status": "active",
        "created_at": _today_str(),
        "deadline": deadline,
        "tasks": [],
    }
    projects.append(project)
    return projects, project


def delete_project(projects, name):
    """Remove a project by name.

    Returns (projects, deleted_project).

    Raises ValueError if no project with *name* exists.
    """
    idx = _find_index(projects, name)
    if idx is None:
        raise ValueError(f"Project '{name}' not found.")
    removed = projects.pop(idx)
    return projects, removed


def list_projects(projects, status=None):
    """Return all projects, optionally filtered by *status*.

    *status* can be 'active', 'done', 'archived', or None (all).

    Projects are returned in creation order (as stored).
    """
    if status is None:
        return list(projects)
    return [p for p in projects if p["status"] == status]


def set_project_status(projects, name, new_status):
    """Set a project's status.

    Returns (projects, project_dict).

    *new_status* must be one of 'active', 'done', 'archived'.

    Raises ValueError if project not found or status is invalid.
    """
    if new_status not in ("active", "done", "archived"):
        raise ValueError(f"Invalid status '{new_status}'. Must be active, done, or archived.")

    idx = _find_index(projects, name)
    if idx is None:
        raise ValueError(f"Project '{name}' not found.")
    projects[idx]["status"] = new_status
    return projects, projects[idx]


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

def add_task(projects, project_name, title):
    """Add a task to a project. Auto-assigns the next sequential ID.

    Returns (projects, task_dict).

    Raises ValueError if the project is not found.
    """
    idx = _find_index(projects, project_name)
    if idx is None:
        raise ValueError(f"Project '{project_name}' not found.")

    project = projects[idx]
    task = {"id": _next_task_id(project["tasks"]), "title": title, "done": False}
    project["tasks"].append(task)
    return projects, task


def mark_task_done(projects, project_name, task_id):
    """Mark a task as done (idempotent).

    Returns (projects, task_dict).

    Raises ValueError if project or task not found.
    """
    idx = _find_index(projects, project_name)
    if idx is None:
        raise ValueError(f"Project '{project_name}' not found.")

    ti, task = _find_task(projects[idx]["tasks"], task_id)
    if ti is None:
        raise ValueError(f"Task {task_id} not found in project '{project_name}'.")

    projects[idx]["tasks"][ti]["done"] = True
    return projects, projects[idx]["tasks"][ti]


def undo_task(projects, project_name, task_id):
    """Mark a task as not done (idempotent).

    Returns (projects, task_dict).

    Raises ValueError if project or task not found.
    """
    idx = _find_index(projects, project_name)
    if idx is None:
        raise ValueError(f"Project '{project_name}' not found.")

    ti, task = _find_task(projects[idx]["tasks"], task_id)
    if ti is None:
        raise ValueError(f"Task {task_id} not found in project '{project_name}'.")

    projects[idx]["tasks"][ti]["done"] = False
    return projects, projects[idx]["tasks"][ti]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats(projects, project_name):
    """Return progress stats for a project.

    Returns a dict: {name, status, total, done, remaining, percent, deadline}

    Raises ValueError if project not found.
    """
    idx = _find_index(projects, project_name)
    if idx is None:
        raise ValueError(f"Project '{project_name}' not found.")

    p = projects[idx]
    tasks = p["tasks"]
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    remaining = total - done
    percent = (done / total * 100) if total > 0 else 0

    return {
        "name": p["name"],
        "status": p["status"],
        "total": total,
        "done": done,
        "remaining": remaining,
        "percent": round(percent, 1),
        "deadline": p["deadline"],
    }
