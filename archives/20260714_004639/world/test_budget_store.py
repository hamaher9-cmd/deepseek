"""Unit tests for budget_store.py — plain asserts, run directly."""
import os
import json
from budget_store import load_transactions, save_transactions, DB_PATH


def _cleanup():
    """Remove test db so each test starts fresh."""
    for path in (DB_PATH, DB_PATH + ".tmp"):
        if os.path.exists(path):
            os.remove(path)


# -----------------------------------------------------------------------
# load_transactions
# -----------------------------------------------------------------------

def test_load_transactions_returns_empty_when_no_file():
    _cleanup()
    assert load_transactions() == []


def test_load_transactions_returns_empty_when_file_is_empty():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("")
    assert load_transactions() == []


def test_load_transactions_returns_empty_on_bad_json():
    _cleanup()
    with open(DB_PATH, "w") as f:
        f.write("not valid json {{{")
    assert load_transactions() == []


def test_load_transactions_returns_empty_when_json_is_not_a_list():
    _cleanup()
    with open(DB_PATH, "w") as f:
        json.dump({"not": "a list"}, f)
    assert load_transactions() == []


def test_load_transactions_loads_existing_data():
    _cleanup()
    txns = [
        {"id": 1, "date": "2025-08-01", "amount": 12.50,
         "type": "expense", "category": "food", "note": "lunch"}
    ]
    with open(DB_PATH, "w") as f:
        json.dump(txns, f)
    loaded = load_transactions()
    assert len(loaded) == 1
    assert loaded[0]["amount"] == 12.50


def test_load_transactions_loads_multiple():
    _cleanup()
    txns = [
        {"id": 1, "date": "2025-08-01", "amount": 1000.00,
         "type": "income", "category": "salary", "note": None},
        {"id": 2, "date": "2025-08-02", "amount": 45.00,
         "type": "expense", "category": "food", "note": "groceries"},
    ]
    with open(DB_PATH, "w") as f:
        json.dump(txns, f)
    loaded = load_transactions()
    assert len(loaded) == 2
    assert loaded[1]["category"] == "food"


# -----------------------------------------------------------------------
# save_transactions
# -----------------------------------------------------------------------

def test_save_transactions_creates_file():
    _cleanup()
    txns = [{"id": 1, "date": "2025-08-01", "amount": 2500.00,
             "type": "income", "category": "salary", "note": None}]
    save_transactions(txns)
    assert os.path.exists(DB_PATH)
    loaded = load_transactions()
    assert len(loaded) == 1
    assert loaded[0]["amount"] == 2500.00


def test_save_transactions_overwrites_existing():
    _cleanup()
    a = [{"id": 1, "date": "2025-01-01", "amount": 10.00,
          "type": "expense", "category": "food", "note": None}]
    b = [{"id": 2, "date": "2025-01-02", "amount": 20.00,
          "type": "expense", "category": "rent", "note": None}]
    save_transactions(a)
    save_transactions(b)
    loaded = load_transactions()
    assert len(loaded) == 1
    assert loaded[0]["amount"] == 20.00


def test_save_transactions_handles_empty_list():
    _cleanup()
    save_transactions([])
    assert load_transactions() == []


def test_save_transactions_no_temp_file_left():
    _cleanup()
    save_transactions([{"id": 1, "date": "2025-08-01", "amount": 5.00,
                         "type": "expense", "category": "food", "note": None}])
    assert not os.path.exists(DB_PATH + ".tmp")


# -----------------------------------------------------------------------
# round-trip
# -----------------------------------------------------------------------

def test_round_trip_preserves_data():
    _cleanup()
    txns = [
        {"id": 1, "date": "2025-08-01", "amount": 250.75,
         "type": "expense", "category": "shopping", "note": "new shoes"},
        {"id": 2, "date": "2025-08-01", "amount": 3000.00,
         "type": "income", "category": "salary", "note": "august"},
    ]
    save_transactions(txns)
    assert load_transactions() == txns


def test_round_trip_preserves_none_note():
    _cleanup()
    txns = [{"id": 1, "date": "2025-08-01", "amount": 100.00,
             "type": "expense", "category": "utilities", "note": None}]
    save_transactions(txns)
    loaded = load_transactions()
    assert loaded[0]["note"] is None


def test_round_trip_preserves_float_amounts():
    _cleanup()
    txns = [{"id": 1, "date": "2025-08-01", "amount": 12.99,
             "type": "expense", "category": "food", "note": "coffee"}]
    save_transactions(txns)
    loaded = load_transactions()
    assert loaded[0]["amount"] == 12.99


def test_round_trip_mixed_types():
    _cleanup()
    txns = [
        {"id": 1, "date": "2025-08-01", "amount": 5000.00,
         "type": "income", "category": "salary", "note": None},
        {"id": 2, "date": "2025-08-02", "amount": 1500.00,
         "type": "expense", "category": "rent", "note": "august"},
        {"id": 3, "date": "2025-08-03", "amount": 65.30,
         "type": "expense", "category": "food", "note": "groceries"},
        {"id": 4, "date": "2025-08-04", "amount": 200.00,
         "type": "income", "category": "freelance", "note": "logo design"},
    ]
    save_transactions(txns)
    loaded = load_transactions()
    assert len(loaded) == 4
    income_ids = [t["id"] for t in loaded if t["type"] == "income"]
    assert income_ids == [1, 4]


# -----------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("load_transactions returns empty when no file", test_load_transactions_returns_empty_when_no_file),
        ("load_transactions returns empty when file is empty", test_load_transactions_returns_empty_when_file_is_empty),
        ("load_transactions returns empty on bad JSON", test_load_transactions_returns_empty_on_bad_json),
        ("load_transactions returns empty when JSON is not a list", test_load_transactions_returns_empty_when_json_is_not_a_list),
        ("load_transactions loads existing data", test_load_transactions_loads_existing_data),
        ("load_transactions loads multiple", test_load_transactions_loads_multiple),
        ("save_transactions creates file", test_save_transactions_creates_file),
        ("save_transactions overwrites existing", test_save_transactions_overwrites_existing),
        ("save_transactions handles empty list", test_save_transactions_handles_empty_list),
        ("save_transactions no temp file left", test_save_transactions_no_temp_file_left),
        ("round-trip preserves data", test_round_trip_preserves_data),
        ("round-trip preserves None note", test_round_trip_preserves_none_note),
        ("round-trip preserves float amounts", test_round_trip_preserves_float_amounts),
        ("round-trip mixed types", test_round_trip_mixed_types),
    ]

    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name} — {e}")
        except Exception as e:
            print(f"💥 {name} — {type(e).__name__}: {e}")

    print(f"\n{passed}/{len(tests)} passed")
