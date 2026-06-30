from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.models import TransactionDirection, TransactionStatus


@dataclass(frozen=True)
class NormalizedTransaction:
    date: date
    posted_date: date | None
    description_raw: str
    merchant: str
    amount: Decimal
    direction: TransactionDirection
    status: TransactionStatus
    source_line: str
    dedupe_key: str


def parse_date(value: str, default_year: int | None = None) -> date:
    cleaned = value.strip()
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"]
    if default_year and re.fullmatch(r"\d{1,2}/\d{1,2}", cleaned):
        cleaned = f"{cleaned}/{default_year}"
        formats.insert(0, "%m/%d/%Y")
    for date_format in formats:
        try:
            return datetime.strptime(cleaned, date_format).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def parse_amount(value: str) -> Decimal:
    cleaned = value.strip().replace("$", "").replace(",", "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Unsupported amount format: {value}") from exc
    return -amount if negative else amount


def infer_direction(amount: Decimal, description: str) -> TransactionDirection:
    lowered = description.lower()
    if "transfer" in lowered or "card payment" in lowered or "credit card payment" in lowered:
        return TransactionDirection.transfer
    if amount >= 0:
        return TransactionDirection.income
    return TransactionDirection.expense


def normalize_merchant(description: str) -> str:
    cleaned = re.sub(r"\s+", " ", description).strip()
    cleaned = re.sub(r"\b\d{3,}\b", "", cleaned).strip()
    return cleaned.title()[:255] or "Unknown Merchant"


def make_dedupe_key(statement_id: str, transaction_date: date, amount: Decimal, description: str) -> str:
    raw = f"{statement_id}|{transaction_date.isoformat()}|{amount:.2f}|{description.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def status_from_confidence(confidence: float, suspicious: bool = False) -> TransactionStatus:
    if suspicious or confidence < 0.5:
        return TransactionStatus.flagged
    if confidence < 0.85:
        return TransactionStatus.needs_review
    return TransactionStatus.reviewed
