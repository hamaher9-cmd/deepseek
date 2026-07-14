"""Journal engine: entry CRUD, date queries, full-text search, tags.

All functions are pure: they take a list of entry dicts plus arguments
and return (entries, result). Never touches the filesystem directly.

Entry dict format:
    {"date": "2025-07-14", "body": "Today was great.", "tags": ["happy"]}
"""

from datetime import date


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_index(entries, date_str):
    """Return index of entry with given date string, or None if missing."""
    for i, e in enumerate(entries):
        if e["date"] == date_str:
            return i
    return None


def _sorted(entries):
    """Return entries sorted by date ascending."""
    return sorted(entries, key=lambda e: e["date"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_entry(entries, date_str, body, tags=None):
    """Add or overwrite an entry for *date_str*.

    Returns (entries, entry_dict).  If an entry for that date already
    exists it is replaced in-place.

    *tags* defaults to an empty list when None.
    """
    if tags is None:
        tags = []

    new_entry = {
        "date": date_str,
        "body": body,
        "tags": tags,
    }

    idx = _find_index(entries, date_str)
    if idx is not None:
        entries[idx] = new_entry
    else:
        entries.append(new_entry)

    return entries, new_entry


def get_entry(entries, date_str):
    """Return the entry dict for *date_str*, or None if not found."""
    idx = _find_index(entries, date_str)
    return entries[idx] if idx is not None else None


def delete_entry(entries, date_str):
    """Remove an entry by date.

    Returns (entries, deleted_entry).

    Raises ValueError if no entry exists for that date.
    """
    idx = _find_index(entries, date_str)
    if idx is None:
        raise ValueError(f"No entry for date '{date_str}'.")
    removed = entries.pop(idx)
    return entries, removed


def search_entries(entries, query, tag=None):
    """Search entry bodies for *query* (case-insensitive substring).

    If *tag* is given, only entries containing that tag are considered.

    Returns a list of matching entries, most recent first.
    """
    q = query.lower()
    results = []
    for e in entries:
        if tag is not None and tag not in e.get("tags", []):
            continue
        if q in e["body"].lower():
            results.append(e)
    # Sort by date descending (most recent first) for search results
    results.sort(key=lambda e: e["date"], reverse=True)
    return results


def list_entries(entries, tag=None):
    """Return all entries, sorted by date ascending.

    If *tag* is given, only entries containing that tag are returned.
    """
    results = []
    for e in entries:
        if tag is not None and tag not in e.get("tags", []):
            continue
        results.append(e)
    return _sorted(results)


def list_tags(entries):
    """Return a list of {tag, count} dicts for all tags across entries.

    Sorted by count descending, then alphabetically for ties.
    """
    counts = {}
    for e in entries:
        for t in e.get("tags", []):
            counts[t] = counts.get(t, 0) + 1

    result = [{"tag": t, "count": c} for t, c in counts.items()]
    # Sort by count descending, then tag alphabetically
    result.sort(key=lambda x: (-x["count"], x["tag"]))
    return result
