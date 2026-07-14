"""
Integration test — full Journal pipeline: journal_store + journal_engine.

Exercises the complete flow:
  1. Write entries via engine, persist via store
  2. Read / today, verify persistence
  3. Search with and without tag filters
  4. List with tag filters, tags summary
  5. Delete and verify removal
  6. Round-trip: load from disk, modify, save, reload
"""

import os
from datetime import date, timedelta

from journal_store import load_entries, save_entries, DB_PATH
from journal_engine import (
    add_entry,
    get_entry,
    delete_entry,
    search_entries,
    list_entries,
    list_tags,
)


def _clean():
    for f in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(f):
            os.remove(f)


def test_full_pipeline_write_read_delete():
    """Write an entry, read it back, delete it, verify gone."""
    _clean()

    # --- Step 1: Start empty ---
    entries = load_entries()
    assert entries == []

    # --- Step 2: Write an entry ---
    today = date.today().isoformat()
    entries, e = add_entry(entries, today, "Today was a great day.", ["happy"])
    assert e["date"] == today
    assert e["body"] == "Today was a great day."
    assert e["tags"] == ["happy"]
    save_entries(entries)

    # --- Step 3: Read it back ---
    entries = load_entries()
    e = get_entry(entries, today)
    assert e is not None
    assert e["body"] == "Today was a great day."
    assert e["tags"] == ["happy"]

    # --- Step 4: Delete it ---
    entries, removed = delete_entry(entries, today)
    assert removed["date"] == today
    save_entries(entries)

    entries = load_entries()
    assert entries == []

    _clean()


def test_full_pipeline_write_overwrite():
    """Write an entry, then overwrite it on the same date."""
    _clean()

    today = date.today().isoformat()

    entries = []
    entries, e1 = add_entry(entries, today, "First draft.", ["notes"])
    save_entries(entries)

    entries = load_entries()
    entries, e2 = add_entry(entries, today, "Final version.", ["published"])
    save_entries(entries)

    entries = load_entries()
    assert len(entries) == 1
    assert entries[0]["body"] == "Final version."
    assert entries[0]["tags"] == ["published"]

    _clean()


def test_full_pipeline_search():
    """Write multiple entries and search across them."""
    _clean()

    entries = []
    entries, _ = add_entry(entries, "2025-07-01", "Started learning Rust.", ["coding"])
    entries, _ = add_entry(entries, "2025-07-02", "Read a book about Python.", ["coding", "reading"])
    entries, _ = add_entry(entries, "2025-07-03", "Went for a long walk outside.", ["health"])
    save_entries(entries)

    # Search by body text
    entries = load_entries()
    results = search_entries(entries, "python")
    assert len(results) == 1
    assert results[0]["date"] == "2025-07-02"

    # Search case-insensitive
    results = search_entries(entries, "RUST")
    assert len(results) == 1
    assert results[0]["date"] == "2025-07-01"

    # Search with tag filter
    results = search_entries(entries, "book", tag="reading")
    assert len(results) == 1
    assert results[0]["date"] == "2025-07-02"

    # Search with non-matching tag
    results = search_entries(entries, "walk", tag="coding")
    assert len(results) == 0

    # Search results should be newest first
    results = search_entries(entries, "a")  # all entries contain "a"
    assert len(results) == 3
    assert results[0]["date"] == "2025-07-03"
    assert results[2]["date"] == "2025-07-01"

    _clean()


def test_full_pipeline_list_and_tags():
    """List entries with tag filter and verify tag summaries."""
    _clean()

    entries = []
    entries, _ = add_entry(entries, "2025-07-01", "Morning run.", ["health", "morning"])
    entries, _ = add_entry(entries, "2025-07-02", "Code review.", ["coding"])
    entries, _ = add_entry(entries, "2025-07-03", "Evening yoga.", ["health", "evening"])
    save_entries(entries)

    # List all (date ascending)
    entries = load_entries()
    all_entries = list_entries(entries)
    assert len(all_entries) == 3
    assert all_entries[0]["date"] == "2025-07-01"
    assert all_entries[2]["date"] == "2025-07-03"

    # List with tag filter
    health_entries = list_entries(entries, tag="health")
    assert len(health_entries) == 2
    dates = [e["date"] for e in health_entries]
    assert "2025-07-01" in dates
    assert "2025-07-03" in dates

    # List with non-existent tag
    empty = list_entries(entries, tag="nonexistent")
    assert empty == []

    # Tags summary
    tags = list_tags(entries)
    assert len(tags) >= 3
    # "health" should have count 2 and be first
    assert tags[0]["tag"] == "health"
    assert tags[0]["count"] == 2

    _clean()


def test_full_pipeline_round_trip():
    """Save entries, reload from disk, modify, save, reload again."""
    _clean()

    # First session
    entries = []
    entries, _ = add_entry(entries, "2025-07-10", "Session one entry.", ["test"])
    save_entries(entries)

    # Reload
    entries = load_entries()
    assert len(entries) == 1

    # Add another entry
    entries, _ = add_entry(entries, "2025-07-11", "Session two entry.", ["test"])
    save_entries(entries)

    # Reload again
    entries = load_entries()
    assert len(entries) == 2
    assert entries[0]["date"] == "2025-07-10"
    assert entries[1]["date"] == "2025-07-11"

    _clean()


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("full pipeline: write → read → delete", test_full_pipeline_write_read_delete),
        ("full pipeline: write overwrite", test_full_pipeline_write_overwrite),
        ("full pipeline: search with tag filters", test_full_pipeline_search),
        ("full pipeline: list and tags summary", test_full_pipeline_list_and_tags),
        ("full pipeline: round-trip persistence", test_full_pipeline_round_trip),
    ]

    passed = 0
    for name, test in tests:
        try:
            test()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name} — FAILED: {e}")
        except Exception as e:
            print(f"❌ {name} — ERROR: {type(e).__name__}: {e}")

    print(f"\n{passed}/{len(tests)} integration tests passed.")
