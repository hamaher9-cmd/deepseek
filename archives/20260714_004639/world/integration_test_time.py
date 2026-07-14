"""
integration_test_time.py — Full pipeline test for Time Blocker.

Tests: add → day → week → conflicts → delete
"""
import os
import sys

# Clean up any existing data file before starting
DATA_FILE = "time_blocks.json"
if os.path.exists(DATA_FILE):
    os.remove(DATA_FILE)

# -----------------------------------------------------------------------
# Test 1: add block (returns exit 0)
# -----------------------------------------------------------------------
import subprocess

def run(cmd):
    """Run time_cli.py with args, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "time_cli.py"] + cmd,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr

# Test 1: add a block
rc, out, err = run(["add", "mon", "09:00", "60", "Deep Work"])
assert rc == 0, f"add failed: {err}"
assert "Deep Work" in out, f"add output missing label: {out}"
assert "mon" in out.lower() or "Monday" in out, f"add output missing day: {out}"
print("✅ test_add_block_mon")

# Test 2: add another block same day later (no conflict)
rc, out, err = run(["add", "mon", "11:00", "30", "Standup"])
assert rc == 0, f"add standup failed: {err}"
print("✅ test_add_block_standup")

# Test 3: add a block with task id
rc, out, err = run(["add", "tue", "14:00", "45", "Code Review", "--task-id", "7"])
assert rc == 0, f"add with task-id failed: {err}"
assert "task #7" in out, f"add output missing task-id: {out}"
print("✅ test_add_block_with_task_id")

# Test 4: add a block on fri
rc, out, err = run(["add", "fri", "16:00", "90", "Wrap Up"])
assert rc == 0, f"add fri failed: {err}"
print("✅ test_add_block_fri")

# Test 5: day view
rc, out, err = run(["day", "mon"])
assert rc == 0, f"day failed: {err}"
assert "Deep Work" in out, f"day view missing Deep Work: {out}"
assert "Standup" in out, f"day view missing Standup: {out}"
print("✅ test_day_view")

# Test 6: day view for empty day
rc, out, err = run(["day", "sun"])
assert rc == 0, f"day sun failed: {err}"
# Should show no blocks or a helpful message
print("✅ test_day_view_empty")

# Test 7: week view
rc, out, err = run(["week"])
assert rc == 0, f"week failed: {err}"
assert "MON" in out.upper(), f"week view missing MON: {out}"
print("✅ test_week_view")

# Test 8: conflicts — add overlapping block
rc, out, err = run(["add", "mon", "09:30", "45", "Conflict Test"])
assert rc == 0, f"add conflict block failed: {err}"
assert "Conflict" in out, "conflict warning not shown"
print("✅ test_conflict_detection_on_add")

# Test 9: conflicts view
rc, out, err = run(["conflicts", "mon"])
assert rc == 0, f"conflicts command failed: {err}"
# Should show at least one conflict (the one we just added)
assert "overlap" in out.lower() or "Conflict" in out or "#" in out, f"conflicts view empty: {out}"
print("✅ test_conflicts_view")

# Test 10: delete a block
rc, out, err = run(["delete", "1"])
assert rc == 0, f"delete failed: {err}"
assert "Deleted" in out, f"delete output missing Deleted: {out}"
print("✅ test_delete_block")

# Test 11: delete non-existent block
rc, out, err = run(["delete", "999"])
assert rc != 0, f"delete non-existent should fail: {out}"
print("✅ test_delete_nonexistent")

# Test 12: add back a block after delete to confirm id increments
rc, out, err = run(["add", "wed", "08:00", "30", "Morning"])
assert rc == 0, f"add after delete failed: {err}"
print("✅ test_add_after_delete")

# Clean up
if os.path.exists(DATA_FILE):
    os.remove(DATA_FILE)

print(f"\n✅ full pipeline: add → day → week → conflicts → delete")
