"""Unit tests for project_store.py — plain asserts, run directly."""
import os
import json
from project_store import load_projects, save_projects, DB_PATH


def _cleanup():
    """Remove test db so each test starts fresh."""
    for path in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(path):
            os.remove(path)


# -----------------------------------------------------------------------
# load_projects
# -----------------------------------------------------------------------

def test_load_projects_returns_empty_list_when_no_file():
    _cleanup()
    assert load_projects() == []


def test_load_projects_returns_empty_list_when_file_is_empty():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("")
    assert load_projects() == []


def test_load_projects_returns_empty_list_on_bad_json():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("not valid json {{{")
    assert load_projects() == []


def test_load_projects_returns_empty_list_when_json_is_not_a_list():
    _cleanup()
    with open(DB_PATH, "w") as f:
        json.dump({"not": "a list"}, f)
    assert load_projects() == []


def test_load_projects_loads_existing_data():
    _cleanup()
    projects = [
        {"name": "Build a website", "status": "active", "created_at": "2025-07-21",
         "deadline": "2025-08-01", "tasks": []}
    ]
    with open(DB_PATH, "w") as f:
        json.dump(projects, f)
    loaded = load_projects()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Build a website"


def test_load_projects_loads_multiple_projects():
    _cleanup()
    projects = [
        {"name": "P1", "status": "active", "created_at": "2025-07-01", "deadline": None, "tasks": []},
        {"name": "P2", "status": "done", "created_at": "2025-07-02", "deadline": "2025-08-01", "tasks": []},
    ]
    with open(DB_PATH, "w") as f:
        json.dump(projects, f)
    loaded = load_projects()
    assert len(loaded) == 2
    assert loaded[1]["name"] == "P2"


# -----------------------------------------------------------------------
# save_projects
# -----------------------------------------------------------------------

def test_save_projects_creates_file():
    _cleanup()
    projects = [{"name": "A", "status": "active", "created_at": "2025-07-21", "deadline": None, "tasks": []}]
    save_projects(projects)
    assert os.path.exists(DB_PATH)
    loaded = load_projects()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "A"


def test_save_projects_overwrites_existing():
    _cleanup()
    projects1 = [{"name": "First", "status": "active", "created_at": "2025-01-01", "deadline": None, "tasks": []}]
    save_projects(projects1)
    projects2 = [{"name": "Second", "status": "done", "created_at": "2025-01-02", "deadline": None, "tasks": []}]
    save_projects(projects2)
    loaded = load_projects()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Second"


def test_save_projects_handles_empty_list():
    _cleanup()
    save_projects([])
    assert load_projects() == []


def test_save_projects_does_not_leave_temp_file():
    _cleanup()
    projects = [{"name": "X", "status": "active", "created_at": "2025-07-21", "deadline": None, "tasks": []}]
    save_projects(projects)
    assert not os.path.exists(DB_PATH + ".tmp")


# -----------------------------------------------------------------------
# round-trip
# -----------------------------------------------------------------------

def test_round_trip_preserves_data():
    _cleanup()
    projects = [
        {
            "name": "Build a website",
            "status": "active",
            "created_at": "2025-07-21",
            "deadline": "2025-08-01",
            "tasks": [
                {"id": 1, "title": "Design mockups", "done": False},
                {"id": 2, "title": "Code frontend", "done": False},
            ],
        }
    ]
    save_projects(projects)
    assert load_projects() == projects


def test_round_trip_preserves_deadline_none():
    _cleanup()
    projects = [{"name": "No deadline", "status": "active", "created_at": "2025-07-21",
                  "deadline": None, "tasks": []}]
    save_projects(projects)
    loaded = load_projects()
    assert loaded[0]["deadline"] is None


def test_round_trip_preserves_mixed_tasks():
    _cleanup()
    projects = [
        {
            "name": "Complex",
            "status": "active",
            "created_at": "2025-07-21",
            "deadline": None,
            "tasks": [
                {"id": 1, "title": "A", "done": True},
                {"id": 2, "title": "B", "done": False},
                {"id": 3, "title": "C", "done": True},
            ],
        }
    ]
    save_projects(projects)
    loaded = load_projects()
    assert len(loaded[0]["tasks"]) == 3
    assert loaded[0]["tasks"][1]["done"] is False


def test_round_trip_multiple_projects():
    _cleanup()
    projects = [
        {"name": "P1", "status": "active", "created_at": "2025-07-01", "deadline": None, "tasks": []},
        {"name": "P2", "status": "done", "created_at": "2025-07-02", "deadline": "2025-08-01",
         "tasks": [{"id": 1, "title": "t1", "done": True}]},
        {"name": "P3", "status": "archived", "created_at": "2025-07-03", "deadline": None, "tasks": []},
    ]
    save_projects(projects)
    loaded = load_projects()
    assert loaded == projects


# -----------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("load_projects returns empty list when no file", test_load_projects_returns_empty_list_when_no_file),
        ("load_projects returns empty list when file is empty", test_load_projects_returns_empty_list_when_file_is_empty),
        ("load_projects returns empty list on bad JSON", test_load_projects_returns_empty_list_on_bad_json),
        ("load_projects returns empty list when JSON is not a list", test_load_projects_returns_empty_list_when_json_is_not_a_list),
        ("load_projects loads existing data", test_load_projects_loads_existing_data),
        ("load_projects loads multiple projects", test_load_projects_loads_multiple_projects),
        ("save_projects creates file", test_save_projects_creates_file),
        ("save_projects overwrites existing", test_save_projects_overwrites_existing),
        ("save_projects handles empty list", test_save_projects_handles_empty_list),
        ("save_projects does not leave temp file", test_save_projects_does_not_leave_temp_file),
        ("round trip preserves data", test_round_trip_preserves_data),
        ("round trip preserves deadline=None", test_round_trip_preserves_deadline_none),
        ("round trip preserves mixed tasks", test_round_trip_preserves_mixed_tasks),
        ("round trip multiple projects", test_round_trip_multiple_projects),
    ]

    passed = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            print(f"❌ {name}")
            raise
        else:
            print(f"✅ {name}")
            passed += 1

    print(f"\n--- {passed}/{len(tests)} tests passed ---")
