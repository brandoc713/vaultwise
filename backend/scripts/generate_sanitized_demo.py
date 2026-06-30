from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Account, Category, Statement, Transaction


BLOCKED_PATTERNS = [
    re.compile(r"\b\d{12,19}\b"),
    re.compile(r"\b[0-9a-f]{64}\b", re.IGNORECASE),
]

MERCHANT_POOLS = {
    "Groceries": ["Green Market", "Neighborhood Grocery", "Fresh Basket"],
    "Housing": ["Housing Provider"],
    "Utilities": ["Utility Provider", "Internet Provider", "City Services"],
    "Dining": ["Local Cafe", "Family Restaurant", "Pizza Kitchen"],
    "Transportation": ["Fuel Station", "Ride Service", "Parking Service"],
    "Shopping": ["Online Retailer", "Home Store", "General Retailer"],
    "Health": ["Pharmacy", "Medical Office"],
    "Income": ["Employer Payroll", "Mobile Deposit"],
    "Transfers": ["Internal Transfer", "Card Payment"],
    "Fees": ["Bank Fee"],
    "Loans": ["Loan Servicer"],
    "Investments": ["Investment Platform"],
    "Uncategorized": ["Unknown Merchant"],
}


def stable_index(value: str, length: int) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % length


def safe_amount(transaction: Transaction, categories: dict[str, Category], account: Account | None) -> float:
    name = category_name(transaction.category_id, categories)
    base = abs(transaction.amount)
    scale_seed = stable_index(f"{transaction.id}-{transaction.merchant}", 7)
    scale = Decimal("0.88") + (Decimal(scale_seed) * Decimal("0.04"))
    rounded = ((base * scale) / Decimal("5")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal("5")
    if demo_direction(transaction, categories, account) == "expense":
        return float(-rounded)
    return float(rounded)


def demo_direction(transaction: Transaction, categories: dict[str, Category], account: Account | None) -> str:
    category = categories.get(str(transaction.category_id))
    if category:
        if category.kind.value in {"expense", "loan"}:
            return "expense"
        if category.kind.value == "income":
            return "income"
        if category.kind.value in {"transfer", "investment"}:
            return "transfer"
    if account and account.account_type.value == "credit":
        return "expense"
    return transaction.direction.value


def category_name(category_id, categories: dict[str, Category]) -> str:
    category = categories.get(str(category_id))
    return category.name if category else "Uncategorized"


def safe_merchant(transaction: Transaction, categories: dict[str, Category]) -> str:
    name = category_name(transaction.category_id, categories)
    pool = MERCHANT_POOLS.get(name, MERCHANT_POOLS["Uncategorized"])
    return pool[stable_index(f"{transaction.merchant}-{transaction.description_redacted}", len(pool))]


def ts_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_fixture(db: Session, output: Path) -> None:
    statements = db.query(Statement).order_by(Statement.created_at).all()
    transactions = db.query(Transaction).order_by(Transaction.date, Transaction.created_at).all()
    active_account_ids = {str(statement.account_id) for statement in statements} | {
        str(transaction.account_id) for transaction in transactions
    }
    accounts = [
        account
        for account in db.query(Account).order_by(Account.created_at).all()
        if str(account.id) in active_account_ids
    ]
    categories = db.query(Category).order_by(Category.name).all()
    category_lookup = {str(category.id): category for category in categories}
    statement_lookup = {str(statement.id): statement for statement in statements}
    account_lookup = {str(account.id): account for account in accounts}

    account_ids = {str(account.id): f"demo-account-{index + 1}" for index, account in enumerate(accounts)}
    statement_ids = {
        str(statement.id): f"demo-statement-{index + 1}" for index, statement in enumerate(statements)
    }

    statement_month_counts: dict[str, int] = defaultdict(int)
    lines = ['import type { Account, Category, StatementImport, Transaction } from "../types";', ""]

    lines.append("export const accounts: Account[] = [")
    for account in accounts:
        demo_type = account.account_type.value
        demo_name = "Demo Checking" if demo_type == "checking" else "Demo Credit Card" if demo_type == "credit" else f"Demo {demo_type.title()}"
        lines.append(
            "  { "
            f"id: {ts_string(account_ids[str(account.id)])}, "
            f"name: {ts_string(demo_name)}, "
            'institution: "Demo Financial", '
            f"type: {ts_string(demo_type)}, "
            'lastFour: "0000" '
            "},"
        )
    lines.append("];")
    lines.append("")

    lines.append("export const categories: Category[] = [")
    for category in categories:
        safe_id = f"demo-category-{category.name.lower().replace(' ', '-')}"
        lines.append(
            "  { "
            f"id: {ts_string(safe_id)}, "
            f"name: {ts_string(category.name)}, "
            f"type: {ts_string(category.kind.value)}, "
            f"color: {ts_string(category.color)} "
            "},"
        )
    lines.append("];")
    lines.append("")

    category_ids = {
        str(category.id): f"demo-category-{category.name.lower().replace(' ', '-')}" for category in categories
    }

    lines.append("export const statementImports: StatementImport[] = [")
    for statement in statements:
        statement_month_counts[str(statement.account_id)] += 1
        account_type = statement.account.account_type.value if statement.account else "account"
        sequence = statement_month_counts[str(statement.account_id)]
        lines.append(
            "  { "
            f"id: {ts_string(statement_ids[str(statement.id)])}, "
            f"accountId: {ts_string(account_ids[str(statement.account_id)])}, "
            f"fileName: {ts_string(f'demo-{account_type}-statement-{sequence:02d}.pdf')}, "
            f"fileType: {ts_string(statement.file_type.value)}, "
            f"importedAt: {ts_string(statement.created_at.isoformat())}, "
            f"parsedCount: {statement.parsed_count}, "
            f"needsReviewCount: {statement.needs_review_count}, "
            f"duplicateCandidateCount: {statement.duplicate_candidate_count}, "
            f"status: {ts_string('parsed' if statement.parse_status.value == 'parsed' else 'needs_review')} "
            "},"
        )
    lines.append("];")
    lines.append("")

    lines.append("export const transactions: Transaction[] = [")
    for index, transaction in enumerate(transactions):
        statement = statement_lookup.get(str(transaction.statement_id))
        account = account_lookup.get(str(transaction.account_id))
        shifted_date = transaction.date + timedelta(days=17)
        shifted_posted = (transaction.posted_date or transaction.date) + timedelta(days=17)
        merchant = safe_merchant(transaction, category_lookup)
        category = category_name(transaction.category_id, category_lookup)
        description = f"{merchant} {category} transaction"
        lines.append(
            "  { "
            f"id: {ts_string(f'demo-transaction-{index + 1:04d}')}, "
            f"accountId: {ts_string(account_ids[str(transaction.account_id)])}, "
            f"statementId: {ts_string(statement_ids.get(str(transaction.statement_id), 'demo-statement-unknown'))}, "
            f"date: {ts_string(shifted_date.isoformat())}, "
            f"postedDate: {ts_string(shifted_posted.isoformat())}, "
            f"description: {ts_string(description)}, "
            f"merchant: {ts_string(merchant)}, "
            f"amount: {safe_amount(transaction, category_lookup, account)}, "
            f"direction: {ts_string(demo_direction(transaction, category_lookup, account))}, "
            f"categoryId: {ts_string(category_ids.get(str(transaction.category_id), 'demo-category-uncategorized'))}, "
            f"confidence: {round(float(transaction.confidence), 2)}, "
            f"status: {ts_string(transaction.status.value)}, "
            f"manualOverride: {str(bool(transaction.manual_override)).lower()} "
            "},"
        )
    lines.append("];")
    lines.append("")

    content = "\n".join(lines)
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(content):
            raise ValueError("Generated fixture failed privacy validation.")
    output.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate public-safe sanitized frontend fixtures from local DB data.")
    parser.add_argument("--output", default="src/data/sanitizedFixtures.ts")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        write_fixture(db, Path(args.output))
    finally:
        db.close()
    print(f"Sanitized fixture written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
