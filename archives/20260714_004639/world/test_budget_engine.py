"""Unit tests for budget_engine.py — plain asserts, run directly."""
from budget_engine import (
    add_transaction,
    delete_transaction,
    list_transactions,
    get_balance,
    get_monthly_summary,
    get_category_totals,
    list_months,
)


# -----------------------------------------------------------------------
# add_transaction
# -----------------------------------------------------------------------

def test_add_transaction_creates_income():
    txns = []
    txns, t = add_transaction(txns, "2025-08-01", 1000.00, "income", "salary")
    assert t["id"] == 1
    assert t["date"] == "2025-08-01"
    assert t["amount"] == 1000.00
    assert t["type"] == "income"
    assert t["category"] == "salary"
    assert t["note"] is None
    assert len(txns) == 1


def test_add_transaction_creates_expense():
    txns = []
    txns, t = add_transaction(txns, "2025-08-02", 45.50, "expense", "food", note="lunch")
    assert t["type"] == "expense"
    assert t["note"] == "lunch"
    assert t["amount"] == 45.50


def test_add_transaction_auto_increments_id():
    txns = []
    txns, t1 = add_transaction(txns, "2025-08-01", 10.00, "income", "salary")
    txns, t2 = add_transaction(txns, "2025-08-02", 20.00, "expense", "food")
    assert t1["id"] == 1
    assert t2["id"] == 2


def test_add_transaction_id_uses_max_plus_one():
    txns = [{"id": 5, "date": "2025-08-01", "amount": 50.00,
             "type": "expense", "category": "food", "note": None}]
    txns, t = add_transaction(txns, "2025-08-02", 100.00, "income", "salary")
    assert t["id"] == 6


def test_add_transaction_raises_on_invalid_type():
    txns = []
    try:
        add_transaction(txns, "2025-08-01", 10.00, "refund", "shopping")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "refund" in str(e) or "Invalid" in str(e)


def test_add_transaction_raises_on_empty_category():
    txns = []
    try:
        add_transaction(txns, "2025-08-01", 10.00, "expense", "")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_transaction_raises_on_none_category():
    txns = []
    try:
        add_transaction(txns, "2025-08-01", 10.00, "expense", None)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_transaction_converts_int_amount_to_float():
    txns = []
    txns, t = add_transaction(txns, "2025-08-01", 42, "income", "freelance")
    assert isinstance(t["amount"], float)
    assert t["amount"] == 42.0


def test_add_transaction_note_defaults_to_none():
    txns = []
    txns, t = add_transaction(txns, "2025-08-01", 10.00, "expense", "food")
    assert t["note"] is None


# -----------------------------------------------------------------------
# delete_transaction
# -----------------------------------------------------------------------

def test_delete_transaction_removes_and_returns():
    txns = []
    txns, t = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txid = t["id"]
    txns, removed = delete_transaction(txns, txid)
    assert removed["id"] == txid
    assert len(txns) == 0


def test_delete_transaction_raises_on_missing():
    txns = []
    try:
        delete_transaction(txns, 999)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "999" in str(e)


def test_delete_transaction_keeps_other_transactions():
    txns = []
    txns, t1 = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, t2 = add_transaction(txns, "2025-08-02", 50.00, "expense", "food")
    txns, _ = delete_transaction(txns, t1["id"])
    assert len(txns) == 1
    assert txns[0]["id"] == t2["id"]


# -----------------------------------------------------------------------
# list_transactions
# -----------------------------------------------------------------------

def test_list_transactions_returns_all_newest_first():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-03", 50.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-02", 75.00, "expense", "utilities")
    result = list_transactions(txns)
    assert len(result) == 3
    # Newest first: 2025-08-03, then 2025-08-02, then 2025-08-01
    assert result[0]["date"] == "2025-08-03"
    assert result[1]["date"] == "2025-08-02"
    assert result[2]["date"] == "2025-08-01"


def test_list_transactions_filters_by_month():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-09-15", 50.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-20", 75.00, "expense", "utilities")
    result = list_transactions(txns, month="2025-08")
    assert len(result) == 2
    assert all(t["date"].startswith("2025-08") for t in result)


def test_list_transactions_filters_by_category():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 50.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-03", 30.00, "expense", "food")
    result = list_transactions(txns, category="food")
    assert len(result) == 2
    assert all(t["category"] == "food" for t in result)


def test_list_transactions_filters_by_type():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 50.00, "expense", "food")
    result = list_transactions(txns, type="income")
    assert len(result) == 1
    assert result[0]["type"] == "income"


def test_list_transactions_combined_filters():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-09-01", 50.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-15", 75.00, "expense", "utilities")
    result = list_transactions(txns, month="2025-08", category="food")
    assert len(result) == 1
    assert result[0]["amount"] == 100.00


def test_list_transactions_returns_empty_when_no_matches():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    result = list_transactions(txns, type="expense")
    assert result == []


def test_list_transactions_empty_input():
    assert list_transactions([]) == []


def test_list_transactions_same_date_uses_id_tiebreak():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")   # id 1
    txns, _ = add_transaction(txns, "2025-08-01", 50.00, "expense", "food")     # id 2
    result = list_transactions(txns)
    # Same date, higher id first
    assert result[0]["id"] == 2
    assert result[1]["id"] == 1


# -----------------------------------------------------------------------
# get_balance
# -----------------------------------------------------------------------

def test_get_balance_empty():
    assert get_balance([]) == 0.0


def test_get_balance_only_income():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 5000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-15", 500.00, "income", "freelance")
    assert get_balance(txns) == 5500.00


def test_get_balance_only_expense():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-02", 200.00, "expense", "food")
    assert get_balance(txns) == -1700.00


def test_get_balance_mixed():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-03", 200.00, "expense", "food")
    assert get_balance(txns) == 1300.00


def test_get_balance_handles_cents():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.33, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 55.11, "expense", "food")
    assert get_balance(txns) == 45.22


# -----------------------------------------------------------------------
# get_monthly_summary
# -----------------------------------------------------------------------

def test_get_monthly_summary_empty_month():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    result = get_monthly_summary(txns, "2025-09")
    assert result["income_total"] == 0.0
    assert result["expense_total"] == 0.0
    assert result["net"] == 0.0
    assert result["by_category"] == {}


def test_get_monthly_summary_income_only():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 5000.00, "income", "salary")
    result = get_monthly_summary(txns, "2025-08")
    assert result["income_total"] == 5000.00
    assert result["expense_total"] == 0.0
    assert result["net"] == 5000.00
    assert result["by_category"] == {"salary": 5000.00}


def test_get_monthly_summary_expense_only():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-02", 200.00, "expense", "food")
    result = get_monthly_summary(txns, "2025-08")
    assert result["income_total"] == 0.0
    assert result["expense_total"] == 1700.00
    assert result["net"] == -1700.00


def test_get_monthly_summary_mixed():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-05", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-10", 200.00, "expense", "food")
    result = get_monthly_summary(txns, "2025-08")
    assert result["income_total"] == 3000.00
    assert result["expense_total"] == 1700.00
    assert result["net"] == 1300.00


def test_get_monthly_summary_by_category_mixed():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-05", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-10", 200.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-15", 50.00, "expense", "food")
    result = get_monthly_summary(txns, "2025-08")
    by_cat = result["by_category"]
    assert by_cat["salary"] == 3000.00
    assert by_cat["rent"] == -1500.00
    assert by_cat["food"] == -250.00


def test_get_monthly_summary_other_months_not_included():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 1000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-09-01", 2000.00, "income", "salary")
    result = get_monthly_summary(txns, "2025-08")
    assert result["income_total"] == 1000.00


def test_get_monthly_summary_handles_year_boundaries():
    txns = []
    txns, _ = add_transaction(txns, "2024-12-31", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-01-01", 200.00, "expense", "food")
    result = get_monthly_summary(txns, "2024-12")
    assert result["income_total"] == 100.00
    assert result["expense_total"] == 0.0


# -----------------------------------------------------------------------
# get_category_totals
# -----------------------------------------------------------------------

def test_get_category_totals_empty():
    assert get_category_totals([]) == {}


def test_get_category_totals_single():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 5000.00, "income", "salary")
    result = get_category_totals(txns)
    assert result == {"salary": 5000.00}


def test_get_category_totals_multiple():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 5000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 1500.00, "expense", "rent")
    txns, _ = add_transaction(txns, "2025-08-03", 300.00, "expense", "food")
    result = get_category_totals(txns)
    # Sorted by amount desc
    assert list(result.keys()) == ["salary", "rent", "food"]
    assert result["salary"] == 5000.00
    assert result["rent"] == 1500.00
    assert result["food"] == 300.00


def test_get_category_totals_aggregates_same_category():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 500.00, "income", "freelance")
    txns, _ = add_transaction(txns, "2025-08-15", 300.00, "income", "freelance")
    txns, _ = add_transaction(txns, "2025-08-02", 200.00, "expense", "food")
    result = get_category_totals(txns)
    assert result["freelance"] == 800.00
    assert result["food"] == 200.00


def test_get_category_totals_sorts_by_amount_then_alpha():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "expense", "zebra")
    txns, _ = add_transaction(txns, "2025-08-02", 100.00, "expense", "alpha")
    result = get_category_totals(txns)
    # Same amount, alphabetical
    assert list(result.keys()) == ["alpha", "zebra"]


def test_get_category_totals_includes_income_and_expense():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 3000.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-02", 500.00, "expense", "salary")  # misc deduction same category
    result = get_category_totals(txns)
    assert result["salary"] == 3500.00


# -----------------------------------------------------------------------
# list_months
# -----------------------------------------------------------------------

def test_list_months_empty():
    assert list_months([]) == []


def test_list_months_single():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-15", 100.00, "income", "salary")
    assert list_months(txns) == ["2025-08"]


def test_list_months_multiple_sorted():
    txns = []
    txns, _ = add_transaction(txns, "2025-12-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-01-15", 50.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-08-20", 75.00, "expense", "utilities")
    assert list_months(txns) == ["2025-01", "2025-08", "2025-12"]


def test_list_months_deduplicates():
    txns = []
    txns, _ = add_transaction(txns, "2025-08-01", 100.00, "income", "salary")
    txns, _ = add_transaction(txns, "2025-08-15", 50.00, "expense", "food")
    assert list_months(txns) == ["2025-08"]


def test_list_months_handles_year_boundaries():
    txns = []
    txns, _ = add_transaction(txns, "2024-12-31", 100.00, "expense", "food")
    txns, _ = add_transaction(txns, "2025-01-01", 200.00, "income", "salary")
    assert list_months(txns) == ["2024-12", "2025-01"]


# -----------------------------------------------------------------------
# Test runner
# -----------------------------------------------------------------------
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
