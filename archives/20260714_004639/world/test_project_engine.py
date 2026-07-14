"""Unit tests for project_engine.py — plain asserts, run directly."""
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


# -----------------------------------------------------------------------
# add_project
# -----------------------------------------------------------------------

def test_add_project_creates_active_with_empty_tasks():
    projects = []
    projects, p = add_project(projects, "Build a website")
    assert p["name"] == "Build a website"
    assert p["status"] == "active"
    assert p["tasks"] == []
    assert p["deadline"] is None
    assert "created_at" in p
    assert len(projects) == 1


def test_add_project_with_deadline():
    projects = []
    projects, p = add_project(projects, "Ship API", deadline="2025-12-31")
    assert p["deadline"] == "2025-12-31"


def test_add_project_raises_on_duplicate_name():
    projects = []
    add_project(projects, "Only one")
    try:
        add_project(projects, "Only one")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already exists" in str(e)


def test_add_project_multiple_projects():
    projects = []
    add_project(projects, "Alpha")
    add_project(projects, "Beta")
    assert len(projects) == 2
    assert projects[0]["name"] == "Alpha"
    assert projects[1]["name"] == "Beta"


# -----------------------------------------------------------------------
# delete_project
# -----------------------------------------------------------------------

def test_delete_project_removes_and_returns():
    projects = []
    add_project(projects, "Delete me")
    projects, removed = delete_project(projects, "Delete me")
    assert removed["name"] == "Delete me"
    assert len(projects) == 0


def test_delete_project_raises_on_missing():
    projects = []
    try:
        delete_project(projects, "Ghost")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


def test_delete_project_keeps_other_projects():
    projects = []
    add_project(projects, "Keep")
    add_project(projects, "Remove")
    projects, _ = delete_project(projects, "Remove")
    assert len(projects) == 1
    assert projects[0]["name"] == "Keep"


# -----------------------------------------------------------------------
# list_projects
# -----------------------------------------------------------------------

def test_list_projects_returns_all_when_no_filter():
    projects = []
    add_project(projects, "A")
    add_project(projects, "B")
    result = list_projects(projects)
    assert len(result) == 2


def test_list_projects_filters_by_active():
    projects = []
    add_project(projects, "Active one")
    add_project(projects, "Done one")
    set_project_status(projects, "Done one", "done")
    result = list_projects(projects, status="active")
    assert len(result) == 1
    assert result[0]["name"] == "Active one"


def test_list_projects_filters_by_done():
    projects = []
    add_project(projects, "A")
    add_project(projects, "B")
    set_project_status(projects, "B", "done")
    result = list_projects(projects, status="done")
    assert len(result) == 1
    assert result[0]["name"] == "B"


def test_list_projects_filters_by_archived():
    projects = []
    add_project(projects, "A")
    add_project(projects, "Old")
    set_project_status(projects, "Old", "archived")
    result = list_projects(projects, status="archived")
    assert len(result) == 1
    assert result[0]["name"] == "Old"


def test_list_projects_returns_empty_when_no_matches():
    projects = []
    add_project(projects, "Active")
    result = list_projects(projects, status="done")
    assert result == []


# -----------------------------------------------------------------------
# set_project_status
# -----------------------------------------------------------------------

def test_set_project_status_to_done():
    projects = []
    add_project(projects, "P")
    projects, p = set_project_status(projects, "P", "done")
    assert p["status"] == "done"


def test_set_project_status_to_archived():
    projects = []
    add_project(projects, "P")
    projects, p = set_project_status(projects, "P", "archived")
    assert p["status"] == "archived"


def test_set_project_status_back_to_active():
    projects = []
    add_project(projects, "P")
    set_project_status(projects, "P", "done")
    projects, p = set_project_status(projects, "P", "active")
    assert p["status"] == "active"


def test_set_project_status_raises_on_invalid_status():
    projects = []
    add_project(projects, "P")
    try:
        set_project_status(projects, "P", "pending")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "pending" in str(e) or "Invalid" in str(e)


def test_set_project_status_raises_on_missing_project():
    projects = []
    try:
        set_project_status(projects, "Ghost", "done")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


# -----------------------------------------------------------------------
# add_task
# -----------------------------------------------------------------------

def test_add_task_creates_task_with_id_1():
    projects = []
    add_project(projects, "P")
    projects, task = add_task(projects, "P", "Design mockups")
    assert task["id"] == 1
    assert task["title"] == "Design mockups"
    assert task["done"] is False
    assert len(projects[0]["tasks"]) == 1


def test_add_task_auto_increments_ids():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "Task A")
    projects, task = add_task(projects, "P", "Task B")
    assert task["id"] == 2


def test_add_task_gaps_filled_by_max_plus_one():
    projects = []
    add_project(projects, "P")
    # Manually set up tasks with non-sequential ids by manipulating list
    projects[0]["tasks"] = [
        {"id": 5, "title": "High ID", "done": False},
    ]
    projects, task = add_task(projects, "P", "Next task")
    assert task["id"] == 6


def test_add_task_raises_on_missing_project():
    projects = []
    try:
        add_task(projects, "Ghost", "Task")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


# -----------------------------------------------------------------------
# mark_task_done
# -----------------------------------------------------------------------

def test_mark_task_done_sets_done_true():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    projects, task = mark_task_done(projects, "P", 1)
    assert task["done"] is True


def test_mark_task_done_is_idempotent():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    mark_task_done(projects, "P", 1)
    projects, task = mark_task_done(projects, "P", 1)
    assert task["done"] is True


def test_mark_task_done_raises_on_missing_project():
    projects = []
    try:
        mark_task_done(projects, "Ghost", 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


def test_mark_task_done_raises_on_missing_task():
    projects = []
    add_project(projects, "P")
    try:
        mark_task_done(projects, "P", 99)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "99" in str(e)


# -----------------------------------------------------------------------
# undo_task
# -----------------------------------------------------------------------

def test_undo_task_sets_done_false():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    mark_task_done(projects, "P", 1)
    projects, task = undo_task(projects, "P", 1)
    assert task["done"] is False


def test_undo_task_is_idempotent():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    projects, task = undo_task(projects, "P", 1)
    assert task["done"] is False


def test_undo_task_raises_on_missing_project():
    projects = []
    try:
        undo_task(projects, "Ghost", 1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


def test_undo_task_raises_on_missing_task():
    projects = []
    add_project(projects, "P")
    try:
        undo_task(projects, "P", 99)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "99" in str(e)


# -----------------------------------------------------------------------
# get_stats
# -----------------------------------------------------------------------

def test_get_stats_empty_project_zero_percent():
    projects = []
    add_project(projects, "P")
    stats = get_stats(projects, "P")
    assert stats["total"] == 0
    assert stats["done"] == 0
    assert stats["remaining"] == 0
    assert stats["percent"] == 0


def test_get_stats_all_done_is_100_percent():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    add_task(projects, "P", "T2")
    mark_task_done(projects, "P", 1)
    mark_task_done(projects, "P", 2)
    stats = get_stats(projects, "P")
    assert stats["done"] == 2
    assert stats["remaining"] == 0
    assert stats["percent"] == 100.0


def test_get_stats_mixed_progress():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    add_task(projects, "P", "T2")
    add_task(projects, "P", "T3")
    mark_task_done(projects, "P", 1)
    stats = get_stats(projects, "P")
    assert stats["total"] == 3
    assert stats["done"] == 1
    assert stats["remaining"] == 2
    # 1/3 = 33.333... → 33.3
    assert stats["percent"] == round(1/3 * 100, 1)


def test_get_stats_rounds_percent():
    projects = []
    add_project(projects, "P")
    add_task(projects, "P", "T1")
    add_task(projects, "P", "T2")
    add_task(projects, "P", "T3")
    mark_task_done(projects, "P", 1)
    mark_task_done(projects, "P", 2)
    stats = get_stats(projects, "P")
    assert stats["percent"] == round(2/3 * 100, 1)


def test_get_stats_includes_name_and_status():
    projects = []
    add_project(projects, "My Project")
    stats = get_stats(projects, "My Project")
    assert stats["name"] == "My Project"
    assert stats["status"] == "active"


def test_get_stats_includes_deadline():
    projects = []
    add_project(projects, "P", deadline="2025-08-01")
    stats = get_stats(projects, "P")
    assert stats["deadline"] == "2025-08-01"


def test_get_stats_deadline_none_when_unset():
    projects = []
    add_project(projects, "P")
    stats = get_stats(projects, "P")
    assert stats["deadline"] is None


def test_get_stats_raises_on_missing_project():
    projects = []
    try:
        get_stats(projects, "Ghost")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Ghost" in str(e)


# -----------------------------------------------------------------------
# cross-layer scenarios
# -----------------------------------------------------------------------

def test_full_workflow_create_add_tasks_complete_project():
    projects = []
    # Create project
    projects, p = add_project(projects, "Ship feature", deadline="2025-09-01")
    assert p["status"] == "active"

    # Add tasks
    add_task(projects, "Ship feature", "Write spec")
    add_task(projects, "Ship feature", "Implement")
    add_task(projects, "Ship feature", "Test")

    # Mark some done
    mark_task_done(projects, "Ship feature", 1)
    mark_task_done(projects, "Ship feature", 2)

    # Check stats
    stats = get_stats(projects, "Ship feature")
    assert stats["total"] == 3
    assert stats["done"] == 2
    assert stats["remaining"] == 1

    # Undo one
    undo_task(projects, "Ship feature", 2)
    stats = get_stats(projects, "Ship feature")
    assert stats["done"] == 1

    # Complete remaining
    mark_task_done(projects, "Ship feature", 2)
    mark_task_done(projects, "Ship feature", 3)
    stats = get_stats(projects, "Ship feature")
    assert stats["done"] == 3
    assert stats["percent"] == 100.0

    # Mark project done
    set_project_status(projects, "Ship feature", "done")
    assert list_projects(projects, status="done")[0]["name"] == "Ship feature"
