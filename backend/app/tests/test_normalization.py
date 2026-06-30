from decimal import Decimal

from app.models import TransactionDirection, TransactionStatus
from app.services.normalization import (
    infer_direction,
    make_dedupe_key,
    parse_amount,
    parse_date,
    status_from_confidence,
)


def test_parse_date_and_amount():
    assert parse_date("2026-06-30").isoformat() == "2026-06-30"
    assert parse_date("6/30", default_year=2026).isoformat() == "2026-06-30"
    assert parse_amount("$1,234.56") == Decimal("1234.56")
    assert parse_amount("($45.10)") == Decimal("-45.10")


def test_direction_and_status():
    assert infer_direction(Decimal("1200"), "PAYROLL ACH CREDIT") == TransactionDirection.income
    assert infer_direction(Decimal("-80.25"), "KROGER #4481") == TransactionDirection.expense
    assert infer_direction(Decimal("-400"), "ACH TRANSFER TO SAVINGS") == TransactionDirection.transfer
    assert status_from_confidence(0.91) == TransactionStatus.reviewed
    assert status_from_confidence(0.7) == TransactionStatus.needs_review
    assert status_from_confidence(0.2) == TransactionStatus.flagged


def test_dedupe_key_is_stable():
    first = make_dedupe_key("stmt", parse_date("2026-06-30"), Decimal("-42.00"), "Coffee Shop")
    second = make_dedupe_key("stmt", parse_date("2026-06-30"), Decimal("-42.00"), "coffee shop")
    assert first == second
