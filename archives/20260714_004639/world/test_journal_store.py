"""
test_journal_store.py — unit tests for journal_store.py
"""

import json
import os
import journal_store


def _cleanup():
    """Remove journal.json and any temp files between tests."""
    for path in ["journal.json", "journal.json.tmp"]:
        if os.path.exists(path):
            os.remove(path)


def test_load_entries_returns_empty_when_no_file():
    _cleanup()
    entries = journal_store.load_entries()
    assert entries == [], f"Expected empty list, got {entries}"


def test_load_entries_returns_list_from_valid_file():
    _cleanup()
    sample = [{"date": "2025-07-14", "body": "Great day.", "tags": ["happy"]}]
    with open("journal.json", "w") as f:
        json.dump(sample, f)
    entries = journal_store.load_entries()
    assert entries == sample, f"Expected {sample}, got {entries}"


def test_save_then_load_roundtrip():
    _cleanup()
    sample = [
        {"date": "2025-07-14", "body": "First entry.", "tags": ["test"]},
        {"date": "2025-07-15", "body": "Second entry.", "tags": []},
    ]
    journal_store.save_entries(sample)
    loaded = journal_store.load_entries()
    assert loaded == sample, f"Roundtrip failed: {loaded} != {sample}"


def test_load_entries_handles_bad_json():
    _cleanup()
    with open("journal.json", "w") as f:
        f.write("this is not json {{{")
    entries = journal_store.load_entries()
    assert entries == [], f"Expected empty list on bad JSON, got {entries}"


def test_load_entries_handles_non_list_data():
    _cleanup()
    with open("journal.json", "w") as f:
        json.dump({"not": "a list"}, f)
    entries = journal_store.load_entries()
    assert entries == [], f"Expected empty list for non-list data, got {entries}"


def test_atomic_write_does_not_leave_temp_file():
    _cleanup()
    sample = [{"date": "2025-07-14", "body": "Atomic test.", "tags": []}]
    journal_store.save_entries(sample)
    assert not os.path.exists("journal.json.tmp"), "Temp file should not remain"
    assert os.path.exists("journal.json"), "Real file should exist"


def test_save_overwrites_previous_data():
    _cleanup()
    first = [{"date": "2025-07-14", "body": "First.", "tags": []}]
    second = [{"date": "2025-07-15", "body": "Second.", "tags": []}]
    journal_store.save_entries(first)
    journal_store.save_entries(second)
    loaded = journal_store.load_entries()
    assert loaded == second, f"Expected second save to overwrite, got {loaded}"


def test_entry_with_multiple_tags():
    _cleanup()
    sample = [{"date": "2025-07-14", "body": "Tagged.", "tags": ["a", "b", "c"]}]
    journal_store.save_entries(sample)
    loaded = journal_store.load_entries()
    assert loaded == sample


def test_entry_without_tags_field():
    _cleanup()
    sample = [{"date": "2025-07-14", "body": "No tags key."}]
    journal_store.save_entries(sample)
    loaded = journal_store.load_entries()
    assert loaded == sample


def test_multiple_entries_save_and_load():
    _cleanup()
    sample = [
        {"date": "2025-07-10", "body": "Entry 1.", "tags": ["work"]},
        {"date": "2025-07-11", "body": "Entry 2.", "tags": ["personal"]},
        {"date": "2025-07-12", "body": "Entry 3.", "tags": ["work", "ideas"]},
    ]
    journal_store.save_entries(sample)
    loaded = journal_store.load_entries()
    assert len(loaded) == 3
    assert loaded == sample


def test_empty_list_save_and_load():
    _cleanup()
    journal_store.save_entries([])
    loaded = journal_store.load_entries()
    assert loaded == []


def test_load_preserves_order():
    _cleanup()
    sample = [
        {"date": "2025-07-14", "body": "A.", "tags": []},
        {"date": "2025-07-13", "body": "B.", "tags": []},
    ]
    journal_store.save_entries(sample)
    loaded = journal_store.load_entries()
    assert loaded[0]["body"] == "A."
    assert loaded[1]["body"] == "B."


if __name__ == "__main__":
    tests = [
        test_load_entries_returns_empty_when_no_file,
        test_load_entries_returns_list_from_valid_file,
        test_save_then_load_roundtrip,
        test_load_entries_handles_bad_json,
        test_load_entries_handles_non_list_data,
        test_atomic_write_does_not_leave_temp_file,
        test_save_overwrites_previous_data,
        test_entry_with_multiple_tags,
        test_entry_without_tags_field,
        test_multiple_entries_save_and_load,
        test_empty_list_save_and_load,
        test_load_preserves_order,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    # Clean up after all tests
    _cleanup()
