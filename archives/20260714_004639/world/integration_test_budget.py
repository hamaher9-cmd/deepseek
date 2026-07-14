"""
Integration test — full Budget Tracker pipeline: budget_store + budget_engine.

Exercises the complete flow:
  1. Add income + expense transactions
  2. Verify balance and persistence
  3. Monthly summaries with by-category breakdown
  4. Category totals
  5. List with filters
  6. Delete and verify removal
  7. Round-trip: load from disk, modify, save, reload
"""

import os

from budget_store import load_transactions, save_transactions, DB_PATH
from budget_engine import (
    add_transaction,
    delete_transaction,
    list_transactions,
    get_balance,
    get_monthly_summary,
    get_category_totals,
    list_months,
)


def _clean():
    for f in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(f):
            os.remove(f)


def test_full_pipeline_add_balance():
    """Add income + expenses, verify balance and persistence."""
    _clean()

    # Step 1: Start empty
    txns = load_transactions()
    assert txns == []

    # Step 2: Add transactions
    txns, t1 = add_transaction(txns, "2025-08-01", 3000.00, "income", "salary", "August paycheck")
    assert t1["id"] == 1
    assert t1["type"] == "income"

    txns, t2 = add_transaction(txns, "2025-08-02", 1200.00, "expense", "rent", "August rent")
    assert t2["id"] == 2

    txns, t3 = add_transaction(txns, "2025-08-03", 85.50, "expense", "food", "Groceries")
    assert t3["id"] == 3
    save_transactions(txns)

    # Step 3: Reload and verify
    txns = load_transactions()
    assert len(txns) == 3
    assert get_balance(txns) == 3000.00 - 1200.00 - 85.50

    _clean()


def test_full_pipeline_monthly_summary():
    """Verify monthly summary with by-category breakdown."""
    _clean()

    txns = []
    add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    add_transaction(txns, "2025-08-05", 500.00, "income", "freelance")
    add_transaction(txns, "2025-08-02", 1200.00, "expense", "rent")
    add_transaction(txns, "2025-08-10", 200.00, "expense", "food")
    add_transaction(txns, "2025-09-01", 100.00, "expense", "food")

    summary = get_monthly_summary(txns, "2025-08")
    assert summary["income_total"] == 3500.00
    assert summary["expense_total"] == 1400.00
    assert summary["net"] == 2100.00
    assert "rent" in summary["by_category"]
    assert "food" in summary["by_category"]
    assert "salary" in summary["by_category"]
    # September not included
    assert summary["income_total"] - summary["expense_total"] == summary["net"]

    _clean()


def test_full_pipeline_category_totals():
    """Verify category totals aggregate across all transactions."""
    _clean()

    txns = []
    add_transaction(txns, "2025-08-01", 100.00, "expense", "food")
    add_transaction(txns, "2025-08-02", 50.00, "expense", "food")
    add_transaction(txns, "2025-08-03", 200.00, "expense", "rent")

    totals = get_category_totals(txns)
    assert totals["rent"] == 200.00
    assert totals["food"] == 150.00
    # rent > food, so rent comes first
    keys = list(totals.keys())
    assert keys[0] == "rent"
    assert keys[1] == "food"

    _clean()


def test_full_pipeline_list_filters():
    """Test listing with month, category, and type filters."""
    _clean()

    txns = []
    add_transaction(txns, "2025-08-01", 100.00, "expense", "food")
    add_transaction(txns, "2025-08-02", 200.00, "expense", "rent")
    add_transaction(txns, "2025-09-01", 50.00, "expense", "food")
    add_transaction(txns, "2025-08-15", 500.00, "income", "salary")

    # Filter by month
    aug = list_transactions(txns, month="2025-08")
    assert len(aug) == 3
    # Filter by category
    food = list_transactions(txns, category="food")
    assert len(food) == 2
    # Filter by type
    income = list_transactions(txns, type="income")
    assert len(income) == 1
    assert income[0]["category"] == "salary"
    # Combined filter
    aug_food = list_transactions(txns, month="2025-08", category="food")
    assert len(aug_food) == 1
    # No matches
    empty = list_transactions(txns, month="2024-01")
    assert empty == []

    _clean()


def test_full_pipeline_delete():
    """Add multiple transactions, delete one, verify the rest remain."""
    _clean()

    txns = []
    add_transaction(txns, "2025-08-01", 100.00, "expense", "food")
    add_transaction(txns, "2025-08-02", 200.00, "expense", "rent")
    save_transactions(txns)

    txns = load_transactions()
    txns, removed = delete_transaction(txns, 1)
    assert removed["category"] == "food"
    save_transactions(txns)

    txns = load_transactions()
    assert len(txns) == 1
    assert txns[0]["id"] == 2

    _clean()


def test_full_pipeline_round_trip():
    """Full round-trip: save, reload, modify, save, reload again."""
    _clean()

    # Session 1
    txns = []
    add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    add_transaction(txns, "2025-08-02", 1200.00, "expense", "rent")
    save_transactions(txns)

    # Session 2: reload from disk
    txns = load_transactions()
    assert len(txns) == 2
    assert get_balance(txns) == 1800.00

    # Modify
    add_transaction(txns, "2025-08-03", 85.50, "expense", "food", "Groceries")
    save_transactions(txns)

    # Session 3: reload and verify
    txns = load_transactions()
    assert len(txns) == 3
    assert get_balance(txns) == 1800.00 - 85.50
    months = list_months(txns)
    assert "2025-08" in months

    _clean()


def test_full_pipeline_list_months():
    """Verify list_months returns sorted unique months."""
    _clean()

    txns = []
    add_transaction(txns, "2025-01-15", 100.00, "expense", "food")
    add_transaction(txns, "2025-03-10", 200.00, "expense", "rent")
    add_transaction(txns, "2025-01-20", 50.00, "expense", "food")
    add_transaction(txns, "2024-12-01", 500.00, "income", "salary")

    months = list_months(txns)
    assert months == ["2024-12", "2025-01", "2025-03"]

    _clean()


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"✅ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed + failed} total, {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
