from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models import Transaction, TransactionDirection, TransactionStatus
from app.services.normalization import make_dedupe_key


def test_ml_rejects_insufficient_labels(client):
    response = client.post("/api/ml/train")
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_data"


def test_ml_train_and_predict(client):
    db = SessionLocal()
    try:
        account_id = client.get("/api/accounts").json()[0]["id"]
        categories = client.get("/api/categories").json()
        income = next(category for category in categories if category["name"] == "Income")
        groceries = next(category for category in categories if category["name"] == "Groceries")

        statement = client.post(
            "/api/statements/upload",
            data={"account_id": account_id},
            files={"file": ("training.csv", b"2026-06-01 PLACEHOLDER 1.00", "text/csv")},
        ).json()

        rows = [
            (date(2026, 6, 1), "ACME PAYROLL", Decimal("5200.00"), TransactionDirection.income, income["id"]),
            (date(2026, 6, 15), "ACME PAYROLL", Decimal("5200.00"), TransactionDirection.income, income["id"]),
            (date(2026, 6, 3), "KROGER MARKET", Decimal("-80.00"), TransactionDirection.expense, groceries["id"]),
            (date(2026, 6, 10), "KROGER MARKET", Decimal("-91.00"), TransactionDirection.expense, groceries["id"]),
        ]
        for tx_date, description, amount, direction, category_id in rows:
            db.add(
                Transaction(
                    statement_id=statement["id"],
                    account_id=account_id,
                    date=tx_date,
                    posted_date=tx_date,
                    description_raw=description,
                    description_redacted=description,
                    merchant=description,
                    amount=amount,
                    direction=direction,
                    category_id=category_id,
                    confidence=1.0,
                    status=TransactionStatus.reviewed,
                    manual_override=True,
                    source_line=description,
                    dedupe_key=make_dedupe_key(statement["id"], tx_date, amount, description),
                )
            )
        db.commit()
    finally:
        db.close()

    train = client.post("/api/ml/train")
    assert train.status_code == 200
    assert train.json()["status"] == "trained"

    predict = client.post(
        "/api/ml/predict",
        json={"description": "KROGER MARKET", "merchant": "Kroger", "amount": -45.0, "direction": "expense"},
    )
    assert predict.status_code == 200
    assert predict.json()["category_id"] is not None
