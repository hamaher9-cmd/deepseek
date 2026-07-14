"""Unit tests for habit_store.py — plain asserts, run directly."""
import os
import json
from datetime import date
from habit_store import load_habits, save_habits, DB_PATH


def _cleanup():
    """Remove test db so each test starts fresh."""
    for path in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(path):
            os.remove(path)


# -----------------------------------------------------------------------
# load_habits
# -----------------------------------------------------------------------

def test_load_habits_returns_empty_list_when_no_file():
    _cleanup()
    assert load_habits() == []


def test_load_habits_returns_empty_list_when_file_is_empty():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("")
    assert load_habits() == []


def test_load_habits_returns_empty_list_on_bad_json():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("not valid json {{{")
    assert load_habits() == []


def test_load_habits_returns_empty_list_when_json_is_not_a_list():
    _cleanup()
    with open(DB_PATH, "w") as f:
        json.dump({"not": "a list"}, f)
    assert load_habits() == []


def test_load_habits_loads_existing_data():
    _cleanup()
    habits = [
        {"name": "Exercise", "frequency": "daily", "created_at": "2025-07-14", "checkins": []}
    ]
    with open(DB_PATH, "w") as f:
        json.dump(habits, f)
    loaded = load_habits()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Exercise"


def test_load_habits_loads_multiple_habits():
    _cleanup()
    habits = [
        {"name": "Read", "frequency": "daily", "created_at": "2025-07-14", "checkins": []},
        {"name": "Gym", "frequency": "weekly", "created_at": "2025-07-13", "checkins": ["2025-07-14"]},
    ]
    with open(DB_PATH, "w") as f:
        json.dump(habits, f)
    loaded = load_habits()
    assert len(loaded) == 2
    assert loaded[1]["name"] == "Gym"
    assert loaded[1]["checkins"] == ["2025-07-14"]


# -----------------------------------------------------------------------
# save_habits
# -----------------------------------------------------------------------

def test_save_habits_creates_file():
    _cleanup()
    habits = [{"name": "Meditate", "frequency": "daily", "created_at": "2025-07-14", "checkins": []}]
    save_habits(habits)
    assert os.path.exists(DB_PATH)
    loaded = load_habits()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Meditate"


def test_save_habits_overwrites_existing():
    _cleanup()
    # first save
    habits = [{"name": "Run", "frequency": "daily", "created_at": "2025-07-14", "checkins": []}]
    save_habits(habits)

    # overwrite with new data
    habits2 = [{"name": "Swim", "frequency": "weekly", "created_at": "2025-07-15", "checkins": ["2025-07-15"]}]
    save_habits(habits2)

    loaded = load_habits()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "Swim"


def test_save_habits_handles_empty_list():
    _cleanup()
    save_habits([])
    assert load_habits() == []


def test_save_habits_does_not_leave_temp_file():
    _cleanup()
    habits = [{"name": "Read", "frequency": "daily", "created_at": "2025-07-14", "checkins": []}]
    save_habits(habits)
    assert not os.path.exists(DB_PATH + ".tmp")


# -----------------------------------------------------------------------
# round-trip
# -----------------------------------------------------------------------

def test_round_trip_preserves_data():
    _cleanup()
    today = str(date.today())
    habits = [
        {
            "name": "Exercise",
            "frequency": "daily",
            "created_at": today,
            "checkins": [today],
        }
    ]
    save_habits(habits)
    loaded = load_habits()
    assert loaded == habits


def test_round_trip_multiple_habits_with_checkins():
    _cleanup()
    habits = [
        {"name": "Read", "frequency": "daily", "created_at": "2025-07-01", "checkins": ["2025-07-01", "2025-07-02", "2025-07-03"]},
        {"name": "Gym", "frequency": "weekly", "created_at": "2025-07-01", "checkins": ["2025-07-01", "2025-07-08"]},
    ]
    save_habits(habits)
    loaded = load_habits()
    assert loaded == habits


# -----------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("load_habits returns empty list when no file", test_load_habits_returns_empty_list_when_no_file),
        ("load_habits returns empty list when file is empty", test_load_habits_returns_empty_list_when_file_is_empty),
        ("load_habits returns empty list on bad JSON", test_load_habits_returns_empty_list_on_bad_json),
        ("load_habits returns empty list when JSON is not a list", test_load_habits_returns_empty_list_when_json_is_not_a_list),
        ("load_habits loads existing data", test_load_habits_loads_existing_data),
        ("load_habits loads multiple habits", test_load_habits_loads_multiple_habits),
        ("save_habits creates file", test_save_habits_creates_file),
        ("save_habits overwrites existing", test_save_habits_overwrites_existing),
        ("save_habits handles empty list", test_save_habits_handles_empty_list),
        ("save_habits does not leave temp file", test_save_habits_does_not_leave_temp_file),
        ("round-trip preserves data", test_round_trip_preserves_data),
        ("round-trip multiple habits with checkins", test_round_trip_multiple_habits_with_checkins),
    ]

    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
        except Exception as e:
            print(f"💥 {name}: {type(e).__name__}: {e}")
        finally:
            _cleanup()

    print(f"\n{passed}/{len(tests)} passed")
