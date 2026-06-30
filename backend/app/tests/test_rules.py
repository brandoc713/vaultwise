from app.database import SessionLocal
from app.services.categorization_rules import categorize
from app.services.seeds import seed_reference_data


def test_rules_map_expected_categories():
    db = SessionLocal()
    try:
        seed_reference_data(db)
        assert categorize("ACME PAYROLL ACH CREDIT", "Acme Payroll", db).confidence >= 0.9
        assert categorize("RENT PAYMENT AUTOPAY", "Oak Street Homes", db).source == "rule"
        assert categorize("KROGER #4481", "Kroger", db).source == "rule"
        assert categorize("ACH TRANSFER TO SAVINGS", "Bank Transfer", db).source == "rule"
        unknown = categorize("UNUSUAL POS 88210", "Unknown POS", db)
        assert unknown.category_id is None
        assert unknown.confidence == 0
    finally:
        db.close()
