"""
budget_cli.py — Command-line interface for the Budget Tracker.

Wires argparse to budget_engine + budget_store. Usage:
  python budget_cli.py add 12.50 food --type expense --date 2025-08-01 [--note "lunch"]
  python budget_cli.py list [--month YYYY-MM] [--category food] [--type expense]
  python budget_cli.py delete 3
  python budget_cli.py balance
  python budget_cli.py summary [--month YYYY-MM]
  python budget_cli.py categories
"""

import argparse
import sys
from datetime import date

from budget_store import load_transactions, save_transactions
from budget_engine import (
    add_transaction,
    delete_transaction,
    list_transactions,
    get_balance,
    get_monthly_summary,
    get_category_totals,
    list_months,
)


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

_INCOME_ICON = "📈"
_EXPENSE_ICON = "📉"
_BALANCE_ICON = "💰"
_CATEGORY_ICON = "🏷️"
_SUMMARY_ICON = "📊"

# Category color/emoji map (common categories get nice icons)
_CATEGORY_EMOJI = {
    "salary": "💼",
    "freelance": "💻",
    "food": "🍔",
    "rent": "🏠",
    "utilities": "⚡",
    "shopping": "🛍️",
    "transport": "🚗",
    "health": "💊",
    "entertainment": "🎬",
    "travel": "✈️",
    "education": "📚",
}


def _cat_icon(category: str) -> str:
    return _CATEGORY_EMOJI.get(category.lower(), "📌")


def _type_icon(tx_type: str) -> str:
    return _INCOME_ICON if tx_type == "income" else _EXPENSE_ICON


def _fmt_amount(amount: float, tx_type: str = None) -> str:
    """Format amount with sign for display."""
    prefix = "+" if tx_type == "income" else ("-" if tx_type == "expense" else "")
    return f"{prefix}${amount:,.2f}"


def _bar(percent: float, width: int = 20) -> str:
    """Visual progress bar. percent should be 0-100."""
    filled = min(round(percent / 100 * width), width) if percent > 0 else 0
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_add(args):
    """Add a new transaction."""
    txns = load_transactions()
    try:
        txns, txn = add_transaction(
            txns, args.date, args.amount, args.type, args.category, args.note
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_transactions(txns)
    icon = _type_icon(txn["type"])
    cat_icon = _cat_icon(txn["category"])
    print(f"{icon} Added #{txn['id']}: {_fmt_amount(txn['amount'], txn['type'])} "
          f"{cat_icon} {txn['category']}" + (f" — \"{txn['note']}\"" if txn['note'] else ""))


def cmd_list(args):
    """List transactions with optional filters."""
    txns = load_transactions()
    result = list_transactions(
        txns, month=args.month, category=args.category, type=args.type
    )

    if not result:
        filters = []
        if args.month:
            filters.append(f"month={args.month}")
        if args.category:
            filters.append(f"category={args.category}")
        if args.type:
            filters.append(f"type={args.type}")
        ctx = " matching " + ", ".join(filters) if filters else ""
        print(f"No transactions{ctx}. Add one with: python budget_cli.py add <amount> <category>")
        return

    # Header
    header_parts = ["\n📋 Transactions"]
    if args.month:
        header_parts.append(f"for {args.month}")
    if args.category:
        header_parts.append(f"in {_cat_icon(args.category)} {args.category}")
    if args.type:
        header_parts.append(f"({args.type})")
    print(" ".join(header_parts))
    print("─" * 70)
    print(f"  {'ID':<5} {'Date':<12} {'Type':<8} {'Category':<14} {'Amount':>10}  Note")
    print("  " + "─" * 65)

    # Rows
    income_sum = 0.0
    expense_sum = 0.0

    for t in result:
        icon = _type_icon(t["type"])
        cat_icon = _cat_icon(t["category"])
        amount_str = _fmt_amount(t["amount"], t["type"])
        note = t["note"] or ""
        print(f"  {t['id']:<5} {t['date']:<12} {icon} {t['type']:<5} "
              f"{cat_icon} {t['category']:<12} {amount_str:>10}  {note}")

        if t["type"] == "income":
            income_sum += t["amount"]
        else:
            expense_sum += t["amount"]

    # Summary footer
    print("  " + "─" * 65)
    print(f"  {'':<5} {'':<12} {'':<8} {'':<14} {_fmt_amount(income_sum, 'income'):>10}  income")
    print(f"  {'':<5} {'':<12} {'':<8} {'':<14} {_fmt_amount(-expense_sum, 'expense'):>10}  expense")
    net = income_sum - expense_sum
    net_sign = "+" if net >= 0 else ""
    print(f"  {'':<5} {'':<12} {'':<8} {'Net':<14} {net_sign}${net:,.2f}".rjust(82))


def cmd_delete(args):
    """Delete a transaction by id."""
    txns = load_transactions()
    try:
        txns, removed = delete_transaction(txns, args.id)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    save_transactions(txns)
    icon = _type_icon(removed["type"])
    cat_icon = _cat_icon(removed["category"])
    print(f"🗑  Deleted #{removed['id']}: {icon} {_fmt_amount(removed['amount'], removed['type'])} "
          f"{cat_icon} {removed['category']}")


def cmd_balance(args):
    """Show overall balance."""
    txns = load_transactions()
    balance = get_balance(txns)

    income = sum(t["amount"] for t in txns if t["type"] == "income")
    expense = sum(t["amount"] for t in txns if t["type"] == "expense")

    print(f"\n{_BALANCE_ICON}  Balance")
    print("─" * 35)
    print(f"  {_INCOME_ICON} Income:   {_fmt_amount(income, 'income')}")
    print(f"  {_EXPENSE_ICON} Expense:  {_fmt_amount(-expense, 'expense')}")
    print("  " + "─" * 31)

    if income + expense == 0:
        print(f"  Net:       ${balance:,.2f}  (no transactions)")
        return

    # Savings rate
    if income > 0:
        savings_rate = (balance / income) * 100
        bar = _bar(max(0, savings_rate), 20)
        label = "savings rate" if balance >= 0 else "deficit"
        abs_rate = abs(savings_rate)
        sign = "+" if balance >= 0 else ""
        print(f"  Net:       {sign}${balance:,.2f}")
        print(f"\n  {label}:  {bar} {abs_rate:.1f}%")
    else:
        print(f"  Net:       ${balance:,.2f}")


def cmd_summary(args):
    """Show monthly summary."""
    txns = load_transactions()
    month = args.month

    if month is None:
        # Default to current month
        month = date.today().strftime("%Y-%m")

    s = get_monthly_summary(txns, month)

    if s["income_total"] == 0 and s["expense_total"] == 0:
        print(f"\nNo transactions for {month}.")
        return

    print(f"\n{_SUMMARY_ICON}  Monthly Summary — {month}")
    print("═" * 50)
    print(f"  {_INCOME_ICON} Income:   {_fmt_amount(s['income_total'], 'income')}")
    print(f"  {_EXPENSE_ICON} Expense:  {_fmt_amount(-s['expense_total'], 'expense')}")
    net_sign = "+" if s['net'] >= 0 else ""
    print(f"  {_BALANCE_ICON} Net:      {net_sign}${s['net']:,.2f}")

    if s["by_category"]:
        # Savings/spending rate bar
        if s["income_total"] > 0:
            spent_pct = (s["expense_total"] / s["income_total"]) * 100
            bar = _bar(min(spent_pct, 100), 20)
            print(f"\n  Spent:    {bar} {spent_pct:.1f}% of income")

        print(f"\n  {_CATEGORY_ICON} By Category:")
        print("  " + "─" * 40)
        # Sort by absolute value desc
        sorted_cats = sorted(s["by_category"].items(), key=lambda kv: abs(kv[1]), reverse=True)
        for cat, total in sorted_cats:
            cat_icon = _cat_icon(cat)
            sign = "+" if total >= 0 else ""
            print(f"    {cat_icon} {cat:<14} {sign}${total:,.2f}")


def cmd_categories(args):
    """Show category totals across all transactions."""
    txns = load_transactions()
    if not txns:
        print("No transactions yet. Add one with: python budget_cli.py add <amount> <category>")
        return

    totals = get_category_totals(txns)

    # Find max for bar scaling
    max_total = max(abs(v) for v in totals.values()) if totals else 1

    print(f"\n{_CATEGORY_ICON}  Category Totals")
    print("═" * 50)

    for cat, total in totals.items():
        cat_icon = _cat_icon(cat)
        # Bar proportional to max
        pct = (abs(total) / max_total) * 100 if max_total > 0 else 0
        bar = _bar(pct, 15)
        sign = "+" if total >= 0 else ""
        if total > 0:
            type_label = f"{_INCOME_ICON}"
        else:
            type_label = f"{_EXPENSE_ICON}"
        print(f"  {cat_icon} {cat:<14} {bar} {type_label} {sign}${total:,.2f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="budget",
        description="Budget Tracker CLI 💰",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a transaction")
    p_add.add_argument("amount", type=float, help="Transaction amount")
    p_add.add_argument("category", help="Category (e.g. food, rent, salary)")
    p_add.add_argument("--type", required=True, choices=["income", "expense"],
                       help="Transaction type")
    p_add.add_argument("--date", default=date.today().isoformat(),
                       help="Date in YYYY-MM-DD (default: today)")
    p_add.add_argument("--note", default=None, help="Optional note")

    # list
    p_list = sub.add_parser("list", help="List transactions")
    p_list.add_argument("--month", default=None, help="Filter by month (YYYY-MM)")
    p_list.add_argument("--category", default=None, help="Filter by category")
    p_list.add_argument("--type", default=None, choices=["income", "expense"],
                        help="Filter by type")

    # delete
    p_del = sub.add_parser("delete", help="Delete a transaction by ID")
    p_del.add_argument("id", type=int, help="Transaction ID to delete")

    # balance
    sub.add_parser("balance", help="Show overall balance")

    # summary
    p_sum = sub.add_parser("summary", help="Show monthly summary")
    p_sum.add_argument("--month", default=None,
                       help="Month in YYYY-MM (default: current month)")

    # categories
    sub.add_parser("categories", help="Show category totals")

    args = parser.parse_args()

    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "delete": cmd_delete,
        "balance": cmd_balance,
        "summary": cmd_summary,
        "categories": cmd_categories,
    }

    handlers[args.command](args)


if __name__ == "__main__":
    main()
