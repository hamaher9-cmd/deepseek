"""
Integration test — full Project Tracker pipeline: project_store + project_engine.

Exercises the complete flow:
  1. Add project, verify in store
  2. Add tasks, mark done/undo
  3. Stats and progress calculation
  4. Status filtering (active/done/archived)
  5. Delete and verify removal
  6. Round-trip: load from disk, modify, save, reload
"""

import os

from project_store import load_projects, save_projects, DB_PATH
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


def _clean():
    for f in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(f):
            os.remove(f)


def test_full_pipeline_add_tasks_done():
    """Create project, add tasks, mark done, verify stats."""
    _clean()

    # Step 1: Start empty
    projects = load_projects()
    assert projects == []

    # Step 2: Add a project
    projects, p = add_project(projects, "Build a website", deadline="2025-12-31")
    assert p["name"] == "Build a website"
    assert p["status"] == "active"
    assert p["deadline"] == "2025-12-31"
    save_projects(projects)

    # Step 3: Reload and verify persistence
    projects = load_projects()
    assert len(projects) == 1
    assert projects[0]["name"] == "Build a website"

    # Step 4: Add tasks
    projects, t1 = add_task(projects, "Build a website", "Design mockups")
    assert t1["id"] == 1
    assert t1["done"] is False
    projects, t2 = add_task(projects, "Build a website", "Code frontend")
    assert t2["id"] == 2
    projects, t3 = add_task(projects, "Build a website", "Write tests")
    assert t3["id"] == 3
    save_projects(projects)

    # Step 5: Mark task 1 done
    projects = load_projects()
    projects, task = mark_task_done(projects, "Build a website", 1)
    assert task["done"] is True
    save_projects(projects)

    # Step 6: Verify stats (get_stats returns: total, done, remaining, percent)
    projects = load_projects()
    s = get_stats(projects, "Build a website")
    assert s["total"] == 3
    assert s["done"] == 1
    assert s["remaining"] == 2
    assert s["percent"] == round(100/3, 1)

    _clean()


def test_full_pipeline_undo():
    """Mark a task done, then undo it."""
    _clean()

    projects = []
    projects, _ = add_project(projects, "Test project")
    add_task(projects, "Test project", "Task A")
    mark_task_done(projects, "Test project", 1)
    assert projects[0]["tasks"][0]["done"] is True

    projects, task = undo_task(projects, "Test project", 1)
    assert task["done"] is False
    assert projects[0]["tasks"][0]["done"] is False

    _clean()


def test_full_pipeline_status_filtering():
    """Move project through statuses and verify filtering."""
    _clean()

    projects = []
    add_project(projects, "Active project")
    add_project(projects, "Done project")
    add_project(projects, "Archived project")
    save_projects(projects)

    # Set statuses
    projects = load_projects()
    set_project_status(projects, "Done project", "done")
    set_project_status(projects, "Archived project", "archived")
    save_projects(projects)

    # Verify filters
    projects = load_projects()
    assert len(list_projects(projects, status="active")) == 1
    assert list_projects(projects, status="active")[0]["name"] == "Active project"

    assert len(list_projects(projects, status="done")) == 1
    assert list_projects(projects, status="done")[0]["name"] == "Done project"

    assert len(list_projects(projects, status="archived")) == 1
    assert list_projects(projects, status="archived")[0]["name"] == "Archived project"

    assert len(list_projects(projects)) == 3

    _clean()


def test_full_pipeline_delete():
    """Add multiple projects, delete one, verify the other remains."""
    _clean()

    projects = []
    add_project(projects, "Keep me")
    add_project(projects, "Delete me")
    save_projects(projects)

    projects = load_projects()
    projects, removed = delete_project(projects, "Delete me")
    assert removed["name"] == "Delete me"
    save_projects(projects)

    projects = load_projects()
    assert len(projects) == 1
    assert projects[0]["name"] == "Keep me"

    _clean()


def test_full_pipeline_round_trip():
    """Full round-trip: save, reload, modify, save, reload again."""
    _clean()

    # Session 1
    projects = []
    add_project(projects, "Round-trip project")
    add_task(projects, "Round-trip project", "Task 1")
    add_task(projects, "Round-trip project", "Task 2")
    mark_task_done(projects, "Round-trip project", 1)
    save_projects(projects)

    # Session 2: reload from disk
    projects = load_projects()
    assert len(projects) == 1
    assert len(projects[0]["tasks"]) == 2
    assert projects[0]["tasks"][0]["done"] is True
    assert projects[0]["tasks"][1]["done"] is False

    # Modify
    add_task(projects, "Round-trip project", "Task 3")
    mark_task_done(projects, "Round-trip project", 2)
    save_projects(projects)

    # Session 3: reload again
    projects = load_projects()
    assert len(projects[0]["tasks"]) == 3
    assert projects[0]["tasks"][0]["done"] is True   # still done
    assert projects[0]["tasks"][1]["done"] is True   # newly done
    assert projects[0]["tasks"][2]["done"] is False  # new, not done

    # Stats
    s = get_stats(projects, "Round-trip project")
    assert s["total"] == 3
    assert s["done"] == 2
    assert s["remaining"] == 1

    _clean()


if __name__ == "__main__":
    test_full_pipeline_add_tasks_done()
    print("✅ full pipeline: add → tasks → done → stats")

    test_full_pipeline_undo()
    print("✅ full pipeline: mark done → undo")

    test_full_pipeline_status_filtering()
    print("✅ full pipeline: status filtering (active/done/archived)")

    test_full_pipeline_delete()
    print("✅ full pipeline: delete")

    test_full_pipeline_round_trip()
    print("✅ full pipeline: round-trip persistence")
