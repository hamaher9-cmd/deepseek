"""End-to-end integration test: storage + logic + CLI wiring."""
import os, sys

# Clean slate
if os.path.exists("tasks.json"):
    os.remove("tasks.json")

from logic import add_task, list_tasks, mark_done, delete_task
from storage import load_tasks

print("=== Full Integration Test ===")

# Add
t1 = add_task("Buy milk")
t2 = add_task("Write code")
t3 = add_task("Ship it")
print(f"Added #1: {t1['text']}, #2: {t2['text']}, #3: {t3['text']}")

# List all
print("\nAll tasks:")
for t in list_tasks():
    print(f"  {t['id']}. [{ 'x' if t['done'] else ' ' }] {t['text']}")

# List pending only
print("\nPending:")
for t in list_tasks(show_done=False):
    print(f"  {t['id']}. [{ 'x' if t['done'] else ' ' }] {t['text']}")

# Mark done
mark_done(2)
print("\nAfter marking #2 done:")
for t in list_tasks():
    print(f"  {t['id']}. [{ 'x' if t['done'] else ' ' }] {t['text']}")

# Delete
delete_task(1)
print("\nAfter deleting #1:")
for t in list_tasks():
    print(f"  {t['id']}. [{ 'x' if t['done'] else ' ' }] {t['text']}")

# Verify JSON on disk
on_disk = load_tasks()
assert len(on_disk) == 2
assert on_disk[0]["id"] == 2 and on_disk[0]["done"] is True
assert on_disk[1]["id"] == 3 and on_disk[1]["done"] is False

# Edge cases
assert mark_done(99) is None
assert delete_task(99) is False
assert len(list_tasks()) == 2  # unchanged

# Verify next_id with existing data
from storage import next_id
assert next_id(on_disk) == 4

print("\n✅ All integration checks passed!")

# Cleanup
os.remove("tasks.json")
