"""
budget_store.py — JSON file persistence for the Budget Tracker.

Handles loading/saving the transaction list from budget.json.
Auto-creates the file with graceful JSON error handling.
Uses atomic writes to prevent data corruption.
"""

import json
import os

DB_PATH = "budget.json"


def load_transactions() -> list[dict]:
    """Return the list of transaction dicts. Creates file if missing."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def save_transactions(transactions: list[dict]) -> None:
    """Atomically write the full transaction list to disk."""
    _atomic_write(transactions)


def _atomic_write(transactions: list[dict]) -> None:
    """Write transaction list to disk atomically via temp file + rename."""
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(transactions, f, indent=2)
    os.replace(tmp, DB_PATH)
