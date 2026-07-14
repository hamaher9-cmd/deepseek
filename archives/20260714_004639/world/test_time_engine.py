"""Unit tests for time_engine.py — plain asserts, run directly."""
from time_engine import (
    add_block,
    delete_block,
    list_day,
    list_week,
    find_conflicts,
)


# -----------------------------------------------------------------------
# add_block
# -----------------------------------------------------------------------

def test_add_block_creates_block():
    blocks = []
    blocks, b = add_block(blocks, "mon", "09:00", 60, "Deep Work")
    assert b["id"] == 1
    assert b["day"] == "mon"
    assert b["start"] == "09:00"
    assert b["duration"] == 60
    assert b["label"] == "Deep Work"
    assert b["task_id"] is None
    assert len(blocks) == 1


def test_add_block_with_task_id():
    blocks = []
    blocks, b = add_block(blocks, "tue", "14:00", 30, "Meeting", task_id=5)
    assert b["task_id"] == 5


def test_add_block_auto_increments_id():
    blocks = []
    blocks, b1 = add_block(blocks, "mon", "09:00", 60, "First")
    blocks, b2 = add_block(blocks, "mon", "10:00", 30, "Second")
    assert b1["id"] == 1
    assert b2["id"] == 2


def test_add_block_id_uses_max_plus_one():
    blocks = [{"id": 7, "day": "fri", "start": "16:00", "duration": 45, "label": "Old", "task_id": None}]
    blocks, b = add_block(blocks, "mon", "09:00", 60, "New")
    assert b["id"] == 8


def test_add_block_raises_on_invalid_day():
    blocks = []
    try:
        add_block(blocks, "funday", "09:00", 60, "Fun")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "funday" in str(e)


def test_add_block_raises_on_bad_start_format():
    blocks = []
    for bad in ["9:00", "09:00am", "foo", "25:00", "09:60", "09:", ":00"]:
        try:
            add_block(blocks, "mon", bad, 60, "Test")
            assert False, f"Should have raised ValueError for {bad!r}"
        except ValueError:
            pass


def test_add_block_raises_on_out_of_range_hour():
    blocks = []
    try:
        add_block(blocks, "mon", "25:00", 60, "Late")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_block_raises_on_out_of_range_minute():
    blocks = []
    try:
        add_block(blocks, "mon", "09:60", 60, "Bad minutes")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_block_raises_on_zero_duration():
    blocks = []
    try:
        add_block(blocks, "mon", "09:00", 0, "Instant")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_block_raises_on_negative_duration():
    blocks = []
    try:
        add_block(blocks, "mon", "09:00", -30, "Backwards")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_block_raises_on_non_int_duration():
    blocks = []
    try:
        add_block(blocks, "mon", "09:00", "sixty", "Bad type")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_block_accepts_all_seven_days():
    blocks = []
    for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        blocks, b = add_block(blocks, day, "08:00", 30, day)
        assert b["day"] == day
    assert len(blocks) == 7


def test_add_block_accepts_midnight_and_2359():
    blocks = []
    blocks, b1 = add_block(blocks, "mon", "00:00", 30, "Midnight")
    blocks, b2 = add_block(blocks, "mon", "23:59", 1, "Last minute")
    assert b1["start"] == "00:00"
    assert b2["start"] == "23:59"


def test_add_block_raises_on_none_day():
    blocks = []
    try:
        add_block(blocks, None, "09:00", 60, "None day")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# -----------------------------------------------------------------------
# delete_block
# -----------------------------------------------------------------------

def test_delete_block_removes_and_returns():
    blocks = []
    blocks, b = add_block(blocks, "mon", "09:00", 60, "Deep Work")
    block_id = b["id"]
    blocks, removed = delete_block(blocks, block_id)
    assert removed["id"] == block_id
    assert removed["label"] == "Deep Work"
    assert len(blocks) == 0


def test_delete_block_idempotent_on_missing():
    blocks = []
    blocks, b = add_block(blocks, "mon", "09:00", 60, "Only block")
    blocks, removed = delete_block(blocks, 999)
    assert removed is None
    assert len(blocks) == 1
    assert blocks[0]["id"] == b["id"]


def test_delete_block_keeps_other_blocks():
    blocks = []
    blocks, b1 = add_block(blocks, "mon", "09:00", 60, "First")
    blocks, b2 = add_block(blocks, "mon", "11:00", 30, "Second")
    blocks, _ = delete_block(blocks, b1["id"])
    assert len(blocks) == 1
    assert blocks[0]["id"] == b2["id"]


def test_delete_block_idempotent_on_empty_list():
    blocks = []
    blocks, removed = delete_block(blocks, 1)
    assert removed is None
    assert blocks == []


# -----------------------------------------------------------------------
# list_day
# -----------------------------------------------------------------------

def test_list_day_returns_blocks_sorted_by_start():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "14:00", 30, "Afternoon")
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Morning")
    blocks, _ = add_block(blocks, "mon", "11:30", 45, "Midday")
    result = list_day(blocks, "mon")
    assert len(result) == 3
    assert result[0]["start"] == "09:00"
    assert result[1]["start"] == "11:30"
    assert result[2]["start"] == "14:00"


def test_list_day_only_returns_requested_day():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Monday")
    blocks, _ = add_block(blocks, "tue", "10:00", 30, "Tuesday")
    blocks, _ = add_block(blocks, "wed", "11:00", 45, "Wednesday")
    result = list_day(blocks, "mon")
    assert len(result) == 1
    assert result[0]["label"] == "Monday"


def test_list_day_returns_empty_for_day_with_no_blocks():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Monday")
    result = list_day(blocks, "fri")
    assert result == []


def test_list_day_raises_on_invalid_day():
    blocks = []
    try:
        list_day(blocks, "funday")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# -----------------------------------------------------------------------
# list_week
# -----------------------------------------------------------------------

def test_list_week_returns_all_seven_days():
    blocks = []
    result = list_week(blocks)
    assert set(result.keys()) == {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
    for day in result:
        assert result[day] == []


def test_list_week_groups_blocks_by_day():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Mon AM")
    blocks, _ = add_block(blocks, "mon", "14:00", 30, "Mon PM")
    blocks, _ = add_block(blocks, "wed", "10:00", 45, "Wed")
    result = list_week(blocks)
    assert len(result["mon"]) == 2
    assert len(result["wed"]) == 1
    assert result["tue"] == []


def test_list_week_sorts_blocks_within_each_day():
    blocks = []
    blocks, _ = add_block(blocks, "fri", "16:00", 30, "Late")
    blocks, _ = add_block(blocks, "fri", "09:00", 60, "Early")
    blocks, _ = add_block(blocks, "fri", "12:00", 45, "Mid")
    result = list_week(blocks)
    fri = result["fri"]
    assert [b["start"] for b in fri] == ["09:00", "12:00", "16:00"]


def test_list_week_all_days_empty_for_no_blocks():
    result = list_week([])
    for day in result:
        assert result[day] == []


# -----------------------------------------------------------------------
# find_conflicts
# -----------------------------------------------------------------------

def test_find_conflicts_detects_overlapping_block():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Existing")
    # Proposed: 09:30-10:00 — overlaps with existing 09:00-10:00
    conflicts = find_conflicts(blocks, "mon", "09:30", 30)
    assert len(conflicts) == 1
    assert conflicts[0]["label"] == "Existing"


def test_find_conflicts_detects_block_that_starts_during_proposed():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:30", 30, "Existing")
    # Proposed: 09:00-10:00 — envelops existing
    conflicts = find_conflicts(blocks, "mon", "09:00", 60)
    assert len(conflicts) == 1


def test_find_conflicts_adjacent_blocks_do_not_conflict():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 30, "First")
    # Proposed starts exactly when existing ends: 09:30
    conflicts = find_conflicts(blocks, "mon", "09:30", 30)
    assert conflicts == []


def test_find_conflicts_non_overlapping_no_conflict():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 30, "Morning")
    conflicts = find_conflicts(blocks, "mon", "14:00", 60)
    assert conflicts == []


def test_find_conflicts_returns_empty_when_no_blocks():
    blocks = []
    conflicts = find_conflicts(blocks, "mon", "09:00", 60)
    assert conflicts == []


def test_find_conflicts_returns_multiple_sorted():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "A")
    blocks, _ = add_block(blocks, "mon", "09:30", 30, "B")
    blocks, _ = add_block(blocks, "mon", "13:00", 60, "C")
    # Proposed: 09:15-45 — overlaps with A and B, not C
    conflicts = find_conflicts(blocks, "mon", "09:15", 30)
    assert len(conflicts) == 2
    assert conflicts[0]["label"] == "A"
    assert conflicts[1]["label"] == "B"


def test_find_conflicts_ignores_other_days():
    blocks = []
    blocks, _ = add_block(blocks, "tue", "09:00", 60, "Tuesday block")
    conflicts = find_conflicts(blocks, "mon", "09:00", 60)
    assert conflicts == []


def test_find_conflicts_raises_on_invalid_day():
    blocks = []
    try:
        find_conflicts(blocks, "funday", "09:00", 60)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_find_conflicts_exact_same_time_is_conflict():
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:00", 60, "Existing")
    conflicts = find_conflicts(blocks, "mon", "09:00", 60)
    assert len(conflicts) == 1


def test_find_conflicts_partial_tail_overlap():
    """Proposed starts before existing but ends during it."""
    blocks = []
    blocks, _ = add_block(blocks, "mon", "09:30", 60, "Existing")
    # Proposed: 09:00-10:00 — starts before, ends during
    conflicts = find_conflicts(blocks, "mon", "09:00", 60)
    assert len(conflicts) == 1


# --- Run ---
if __name__ == "__main__":
    tests = [
        # add_block
        test_add_block_creates_block,
        test_add_block_with_task_id,
        test_add_block_auto_increments_id,
        test_add_block_id_uses_max_plus_one,
        test_add_block_raises_on_invalid_day,
        test_add_block_raises_on_bad_start_format,
        test_add_block_raises_on_out_of_range_hour,
        test_add_block_raises_on_out_of_range_minute,
        test_add_block_raises_on_zero_duration,
        test_add_block_raises_on_negative_duration,
        test_add_block_raises_on_non_int_duration,
        test_add_block_accepts_all_seven_days,
        test_add_block_accepts_midnight_and_2359,
        test_add_block_raises_on_none_day,
        # delete_block
        test_delete_block_removes_and_returns,
        test_delete_block_idempotent_on_missing,
        test_delete_block_keeps_other_blocks,
        test_delete_block_idempotent_on_empty_list,
        # list_day
        test_list_day_returns_blocks_sorted_by_start,
        test_list_day_only_returns_requested_day,
        test_list_day_returns_empty_for_day_with_no_blocks,
        test_list_day_raises_on_invalid_day,
        # list_week
        test_list_week_returns_all_seven_days,
        test_list_week_groups_blocks_by_day,
        test_list_week_sorts_blocks_within_each_day,
        test_list_week_all_days_empty_for_no_blocks,
        # find_conflicts
        test_find_conflicts_detects_overlapping_block,
        test_find_conflicts_detects_block_that_starts_during_proposed,
        test_find_conflicts_adjacent_blocks_do_not_conflict,
        test_find_conflicts_non_overlapping_no_conflict,
        test_find_conflicts_returns_empty_when_no_blocks,
        test_find_conflicts_returns_multiple_sorted,
        test_find_conflicts_ignores_other_days,
        test_find_conflicts_raises_on_invalid_day,
        test_find_conflicts_exact_same_time_is_conflict,
        test_find_conflicts_partial_tail_overlap,
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
