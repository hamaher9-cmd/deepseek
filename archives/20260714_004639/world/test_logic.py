"""Quick smoke test for logic.py — verify CRUD works."""
from logic import add_task, list_tasks, mark_done, delete_task

# Clean up any leftover tasks.json
import os
if os.path.exists("tasks.json"):
    os.remove("tasks.json")

# Test add
t1 = add_task("Buy milk")
assert t1["id"] == 1
assert t1["text"] == "Buy milk"
assert t1["done"] is False

t2 = add_task("Write code")
assert t2["id"] == 2

# Test list
all_tasks = list_tasks()
assert len(all_tasks) == 2

pending = list_tasks(show_done=False)
assert len(pending) == 2

# Test mark_done
done = mark_done(1)
assert done is not None
assert done["done"] is True

pending = list_tasks(show_done=False)
assert len(pending) == 1
assert pending[0]["id"] == 2

# Test mark_done on missing
assert mark_done(99) is None

# Test delete
assert delete_task(1) is True
assert len(list_tasks()) == 1
assert delete_task(99) is False

# Test add after delete (ID should be 3, not reusing)
t3 = add_task("Third")
assert t3["id"] == 3

# Cleanup
os.remove("tasks.json")

print("All logic tests passed!")
