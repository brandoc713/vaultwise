from sqlalchemy.orm import Session

from app.config import get_settings
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
    settings = get_settings()
    for name, kind, color in CATEGORY_SEEDS:
        exists = db.query(Category).filter(Category.name == name).first()
        if not exists:
            db.add(Category(name=name, kind=kind, color=color))

    account_seeds = [
        (
            settings.checking_account_name,
            "Private Local Bank",
            AccountType.checking,
            settings.checking_account_last_four[-4:],
        ),
        (
            settings.credit_account_name,
            "Private Local Bank",
            AccountType.credit,
            settings.credit_account_last_four[-4:],
        ),
    ]
    for name, institution, account_type, last_four in account_seeds:
        exists = db.query(Account).filter(Account.name == name).first()
        if not exists:
            db.add(
                Account(
                    name=name,
                    institution=institution,
                    account_type=account_type,
                    last_four=last_four,
                )
            )
    db.commit()
