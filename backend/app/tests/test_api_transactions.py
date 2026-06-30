from io import BytesIO

from app.database import SessionLocal
from app.models import Correction, Transaction


def test_health_and_account_create(client):
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post(
        "/api/accounts",
        json={
            "name": "Test Checking",
            "institution": "Private Local Bank",
            "account_type": "checking",
            "last_four": "1234",
        },
    )
    assert response.status_code == 201
    assert response.json()["last_four"] == "1234"


def test_statement_upload_rejects_unsupported_files(client):
    account_id = client.get("/api/accounts").json()[0]["id"]
    response = client.post(
        "/api/statements/upload",
        data={"account_id": account_id},
        files={"file": ("statement.txt", BytesIO(b"not allowed"), "text/plain")},
    )
    assert response.status_code == 400


def test_csv_upload_parse_patch_and_export(client):
    account_id = client.get("/api/accounts").json()[0]["id"]
    csv_body = b"""2026-06-01 ACME PAYROLL ACH CREDIT 5200.00
2026-06-02 RENT PAYMENT AUTOPAY -1875.00
2026-06-03 UNKNOWN POS 88210 -43.19
"""
    upload = client.post(
        "/api/statements/upload",
        data={"account_id": account_id},
        files={"file": ("statement.csv", BytesIO(csv_body), "text/csv")},
    )
    assert upload.status_code == 201
    statement_id = upload.json()["id"]

    parsed = client.post(f"/api/statements/{statement_id}/parse")
    assert parsed.status_code == 200
    assert parsed.json()["parsed_count"] == 3

    transactions = client.get("/api/transactions").json()
    assert len(transactions) == 3
    categories = client.get("/api/categories").json()
    groceries = next(category for category in categories if category["name"] == "Groceries")

    patch = client.patch(
        f"/api/transactions/{transactions[0]['id']}",
        json={"category_id": groceries["id"], "merchant": "Corrected Merchant", "status": "reviewed"},
    )
    assert patch.status_code == 200
    assert patch.json()["manual_override"] is True

    db = SessionLocal()
    try:
        assert db.query(Correction).count() == 1
        assert db.query(Transaction).count() == 3
    finally:
        db.close()

    export = client.get("/api/transactions/export.csv")
    assert export.status_code == 200
    assert "transaction_id,account_id,statement_id" in export.text
