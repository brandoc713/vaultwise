from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import SessionLocal, create_db_and_tables
from app.models import Account, FileType, ParseStatus, Statement, TextExtractionStatus, Transaction
from app.services.ingestion import parse_statement, sha256_file
from app.services.pdf_detection import detect_pdf_text
from app.services.seeds import seed_reference_data


def account_for_filename(filename: str, accounts: list[Account]) -> Account | None:
    settings = get_settings()
    lowered = filename.lower()
    checking_token = settings.checking_statement_filename_token.lower()
    credit_token = settings.credit_statement_filename_token.lower()

    if checking_token and checking_token in lowered:
        return next(
            (
                account
                for account in accounts
                if account.account_type.value == "checking" and account.name == settings.checking_account_name
            ),
            None,
        )
    if credit_token and credit_token in lowered:
        return next(
            (
                account
                for account in accounts
                if account.account_type.value == "credit" and account.name == settings.credit_account_name
            ),
            None,
        )
    return None


def repair_statement_account(db, statement: Statement, account: Account) -> None:
    if statement.account_id == account.id:
        return
    statement.account_id = account.id
    db.query(Transaction).filter(Transaction.statement_id == statement.id).update(
        {Transaction.account_id: account.id},
        synchronize_session=False,
    )
    db.add(statement)
    db.commit()


def sync_statement_counts(db, statement: Statement) -> None:
    rows = db.query(Transaction).filter(Transaction.statement_id == statement.id).all()
    statement.parsed_count = len(rows)
    statement.needs_review_count = sum(1 for row in rows if row.status.value != "reviewed")
    db.add(statement)
    db.commit()


def register_statement(path: Path, parse: bool) -> tuple[str, str]:
    settings = get_settings()
    db = SessionLocal()
    try:
        seed_reference_data(db)
        accounts = db.query(Account).order_by(Account.created_at).all()
        account = account_for_filename(path.name, accounts)
        if account is None:
            return (path.name, "skipped: filename did not match configured account tokens")

        digest = sha256_file(path)
        existing = db.query(Statement).filter(Statement.sha256 == digest).first()
        if existing:
            repair_statement_account(db, existing, account)
            if parse and existing.parse_status == ParseStatus.uploaded:
                parse_statement(db, existing)
                sync_statement_counts(db, existing)
                return (path.name, "parsed existing registration")
            sync_statement_counts(db, existing)
            return (path.name, "already registered")

        suffix = path.suffix.lower()
        if suffix not in {".pdf", ".csv"}:
            return (path.name, "skipped: unsupported file type")

        statement = Statement(
            account_id=account.id,
            original_filename=path.name,
            stored_path=str(path),
            file_type=FileType.pdf if suffix == ".pdf" else FileType.csv,
            sha256=digest,
            parse_status=ParseStatus.uploaded,
        )

        if statement.file_type == FileType.pdf:
            detection = detect_pdf_text(path, settings.pdf_text_threshold)
            statement.text_extraction_status = detection.status
            if detection.text_preview:
                settings.extracted_text_dir.mkdir(parents=True, exist_ok=True)
                (settings.extracted_text_dir / f"{digest}.preview.txt").write_text(
                    detection.text_preview,
                    encoding="utf-8",
                )
        else:
            statement.text_extraction_status = TextExtractionStatus.text_found

        db.add(statement)
        db.commit()
        db.refresh(statement)

        if parse:
            parse_statement(db, statement)
            sync_statement_counts(db, statement)
            return (path.name, f"registered and parsed for {account.name}")
        return (path.name, f"registered for {account.name}")
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Register ignored local statement PDFs/CSVs with account ownership.")
    parser.add_argument(
        "--dir",
        default=str(get_settings().statements_dir),
        help="Directory containing private statement files. Defaults to LOCAL_DATA_DIR/statements.",
    )
    parser.add_argument("--parse", action="store_true", help="Parse statements immediately after registration.")
    args = parser.parse_args()

    create_db_and_tables()
    root = Path(args.dir)
    if not root.exists():
        print(f"No statement directory found: {root}")
        return 1

    files = sorted(path for path in root.iterdir() if path.suffix.lower() in {".pdf", ".csv"})
    if not files:
        print(f"No PDF/CSV statements found in {root}")
        return 1

    for path in files:
        name, status = register_statement(path, args.parse)
        print(f"{name}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
