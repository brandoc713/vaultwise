from sqlalchemy.orm import Session

from app.models import Account, AccountType, Category, CategoryKind


CATEGORY_SEEDS = [
    ("Income", CategoryKind.income, "#2f855a"),
    ("Groceries", CategoryKind.expense, "#536f56"),
    ("Housing", CategoryKind.expense, "#9a6048"),
    ("Utilities", CategoryKind.expense, "#526b7a"),
    ("Dining", CategoryKind.expense, "#b06b36"),
    ("Transportation", CategoryKind.expense, "#5c6f91"),
    ("Health", CategoryKind.expense, "#7c5f82"),
    ("Shopping", CategoryKind.expense, "#8a6f3d"),
    ("Fees", CategoryKind.expense, "#8b4d4d"),
    ("Transfers", CategoryKind.transfer, "#4f6f7a"),
    ("Loans", CategoryKind.loan, "#735f4b"),
    ("Investments", CategoryKind.investment, "#476a62"),
    ("Uncategorized", CategoryKind.expense, "#6b7280"),
]


def seed_reference_data(db: Session) -> None:
    for name, kind, color in CATEGORY_SEEDS:
        exists = db.query(Category).filter(Category.name == name).first()
        if not exists:
            db.add(Category(name=name, kind=kind, color=color))

    demo_account = db.query(Account).filter(Account.name == "Local Statement Import").first()
    if not demo_account:
        db.add(
            Account(
                name="Local Statement Import",
                institution="Private Local Bank",
                account_type=AccountType.checking,
                last_four="0000",
            )
        )
    db.commit()
