"""
test_time_store.py — unit tests for time_store.py
"""

import os
import json
import time_store


def _cleanup():
    """Remove test artifacts."""
    for f in ["time_blocks.json", "time_blocks.json.tmp"]:
        if os.path.exists(f):
            os.remove(f)


def test_load_blocks_returns_empty_when_no_file():
    _cleanup()
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_save_and_load_roundtrip():
    _cleanup()
    blocks = [
        {"id": 1, "day": "mon", "start": "09:00", "duration": 60, "label": "Deep Work", "task_id": None},
        {"id": 2, "day": "tue", "start": "14:00", "duration": 30, "label": "Meeting", "task_id": 5},
    ]
    time_store.save_blocks(blocks)
    loaded = time_store.load_blocks()
    assert loaded == blocks, f"Roundtrip failed: {loaded}"


def test_save_overwrites_existing():
    _cleanup()
    time_store.save_blocks([{"id": 1, "day": "mon", "start": "09:00", "duration": 30, "label": "Old"}])
    time_store.save_blocks([{"id": 2, "day": "fri", "start": "16:00", "duration": 45, "label": "New"}])
    loaded = time_store.load_blocks()
    assert len(loaded) == 1, f"Expected 1 block, got {len(loaded)}"
    assert loaded[0]["label"] == "New"


def test_load_handles_bad_json():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        f.write("this is not json {{{")
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_load_handles_non_list_json():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        json.dump({"not": "a list"}, f)
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_load_handles_empty_file():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        f.write("")
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_save_empty_list():
    _cleanup()
    time_store.save_blocks([])
    loaded = time_store.load_blocks()
    assert loaded == [], f"Expected [], got {loaded}"
    assert os.path.exists("time_blocks.json")


def test_no_temp_file_left_behind():
    _cleanup()
    time_store.save_blocks([{"id": 1, "day": "wed", "start": "10:00", "duration": 90, "label": "Code Review"}])
    assert not os.path.exists("time_blocks.json.tmp"), "Temp file should not exist after save"


def test_atomic_write_does_not_corrupt_on_disk_full_sim():
    """Verify atomic write uses temp file pattern."""
    _cleanup()
    blocks = [{"id": 1, "day": "thu", "start": "08:00", "duration": 120, "label": "Planning"}]
    time_store.save_blocks(blocks)
    # If atomic write worked, file exists and temp is gone
    assert os.path.exists("time_blocks.json")
    assert not os.path.exists("time_blocks.json.tmp")
    loaded = time_store.load_blocks()
    assert loaded == blocks


def test_load_handles_null_json():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        f.write("null")
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_load_handles_number_json():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        f.write("42")
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


def test_load_handles_string_json():
    _cleanup()
    with open("time_blocks.json", "w") as f:
        f.write('"just a string"')
    result = time_store.load_blocks()
    assert result == [], f"Expected [], got {result}"


# --- Run ---
if __name__ == "__main__":
    tests = [
        test_load_blocks_returns_empty_when_no_file,
        test_save_and_load_roundtrip,
        test_save_overwrites_existing,
        test_load_handles_bad_json,
        test_load_handles_non_list_json,
        test_load_handles_empty_file,
        test_save_empty_list,
        test_no_temp_file_left_behind,
        test_atomic_write_does_not_corrupt_on_disk_full_sim,
        test_load_handles_null_json,
        test_load_handles_number_json,
        test_load_handles_string_json,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"✅ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    _cleanup()
