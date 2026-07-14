"""Budget engine: transaction CRUD, summaries, balance, category totals.

All functions are pure: they take a list of transaction dicts plus arguments
and return (transactions, result). Never touches the filesystem directly.

Transaction dict format:
    {
        "id": 1,
        "date": "2025-08-01",
        "amount": 12.50,
        "type": "income",          # "income" or "expense"
        "category": "food",
        "note": "optional string"  # None if not provided
    }
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_index(transactions, tx_id):
    """Return index of transaction with given id, or None if missing."""
    for i, t in enumerate(transactions):
        if t["id"] == tx_id:
            return i
    return None


def _next_id(transactions):
    """Return the next available transaction id (max + 1, or 1 if empty)."""
    if not transactions:
        return 1
    return max(t["id"] for t in transactions) + 1


# ---------------------------------------------------------------------------
# Transaction CRUD
# ---------------------------------------------------------------------------

def add_transaction(transactions, date, amount, type, category, note=None):
    """Add a new transaction. Auto-assigns the next sequential ID.

    Returns (transactions, transaction_dict).

    Raises ValueError if *type* is not 'income' or 'expense',
    or if *category* is empty/None.
    """
    if type not in ("income", "expense"):
        raise ValueError(f"Invalid type '{type}'. Must be 'income' or 'expense'.")

    if not category:
        raise ValueError("Category must not be empty.")

    txn = {
        "id": _next_id(transactions),
        "date": date,
        "amount": float(amount),
        "type": type,
        "category": category,
        "note": note,
    }
    transactions.append(txn)
    return transactions, txn


def delete_transaction(transactions, id):
    """Remove a transaction by id.

    Returns (transactions, deleted_transaction).

    Raises ValueError if no transaction with *id* exists.
    """
    idx = _find_index(transactions, id)
    if idx is None:
        raise ValueError(f"Transaction {id} not found.")
    removed = transactions.pop(idx)
    return transactions, removed


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def list_transactions(transactions, month=None, category=None, type=None):
    """Return transactions with optional filters, newest-first.

    *month*: YYYY-MM string, matches on date prefix (e.g. "2025-08").
    *category*: exact match on category.
    *type*: 'income' or 'expense'.
    """
    result = list(transactions)

    if month is not None:
        result = [t for t in result if t["date"].startswith(month)]
    if category is not None:
        result = [t for t in result if t["category"] == category]
    if type is not None:
        result = [t for t in result if t["type"] == type]

    # Newest first: sort by date descending, then id descending for tie-break
    result.sort(key=lambda t: (t["date"], t["id"]), reverse=True)
    return result


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------

def get_balance(transactions):
    """Return net balance: total income minus total expense."""
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    return round(income - expense, 2)


def get_monthly_summary(transactions, month):
    """Return a summary dict for *month* (YYYY-MM).

    Returns:
        {
            "income_total": float,
            "expense_total": float,
            "net": float,
            "by_category": {category: net_total, ...}  # income +, expense -
        }
    """
    month_txns = [t for t in transactions if t["date"].startswith(month)]

    income_total = sum(t["amount"] for t in month_txns if t["type"] == "income")
    expense_total = sum(t["amount"] for t in month_txns if t["type"] == "expense")
    net = round(income_total - expense_total, 2)

    by_category = {}
    for t in month_txns:
        cat = t["category"]
        if cat not in by_category:
            by_category[cat] = 0.0
        if t["type"] == "income":
            by_category[cat] += t["amount"]
        else:
            by_category[cat] -= t["amount"]
        by_category[cat] = round(by_category[cat], 2)

    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "net": net,
        "by_category": by_category,
    }


def get_category_totals(transactions):
    """Return {category: total_amount} sorted by amount descending.

    Totals are the sum of all amounts (positive) per category.
    """
    totals = {}
    for t in transactions:
        cat = t["category"]
        totals[cat] = totals.get(cat, 0.0) + t["amount"]
        totals[cat] = round(totals[cat], 2)

    # Sort by amount desc, then alphabetically for ties
    sorted_items = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    return dict(sorted_items)


def list_months(transactions):
    """Return sorted unique YYYY-MM strings for all months with transactions."""
    months = sorted(set(t["date"][:7] for t in transactions))
    return months
