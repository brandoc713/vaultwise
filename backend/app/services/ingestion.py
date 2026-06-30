from __future__ import annotations

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import FileType, ParseStatus, Statement, TextExtractionStatus, Transaction
from app.services.categorization_rules import categorize
from app.services.normalization import (
    infer_direction,
    make_dedupe_key,
    normalize_merchant,
    parse_date,
    status_from_confidence,
)
from app.services.parsers.generic_table_parser import GenericTableParser
from app.services.parsers.local_private_parser import LocalPrivateParser
from app.services.pdf_detection import detect_pdf_text
from app.services.pdf_text import extract_pdf_text
from app.services.redaction import redact_description


ALLOWED_SUFFIXES = {".pdf": FileType.pdf, ".csv": FileType.csv}


def ensure_local_dirs() -> None:
    settings = get_settings()
    for directory in [
        settings.statements_dir,
        settings.extracted_text_dir,
        settings.exports_dir,
        settings.models_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def store_upload(db: Session, account_id: UUID, upload: UploadFile) -> tuple[Statement, str | None]:
    ensure_local_dirs()
    settings = get_settings()
    original_name = Path(upload.filename or "statement").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only PDF and CSV statement uploads are supported.")

    temp_path = settings.statements_dir / f"pending-{original_name}"
    with temp_path.open("wb") as output:
        shutil.copyfileobj(upload.file, output)

    digest = sha256_file(temp_path)
    duplicate = db.query(Statement).filter(Statement.sha256 == digest).first()
    if duplicate:
        temp_path.unlink(missing_ok=True)
        return duplicate, "Duplicate statement detected by SHA-256. Existing upload returned."

    stored_path = settings.statements_dir / f"{digest}{suffix}"
    temp_path.replace(stored_path)

    statement = Statement(
        account_id=account_id,
        original_filename=original_name,
        stored_path=str(stored_path),
        file_type=ALLOWED_SUFFIXES[suffix],
        sha256=digest,
        parse_status=ParseStatus.uploaded,
    )
    if statement.file_type == FileType.pdf:
        detection = detect_pdf_text(stored_path, settings.pdf_text_threshold)
        statement.text_extraction_status = detection.status
        if detection.text_preview:
            (settings.extracted_text_dir / f"{digest}.preview.txt").write_text(
                detection.text_preview, encoding="utf-8"
            )
        message = detection.message
    else:
        statement.text_extraction_status = TextExtractionStatus.text_found
        message = "CSV upload stored. CSV parsing will use text rows in this MVP slice."

    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement, message


def parse_statement(db: Session, statement: Statement, prefer_private_parser: bool = True) -> Statement:
    path = Path(statement.stored_path)
    if statement.file_type == FileType.pdf:
        text = extract_pdf_text(path)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")

    parser = LocalPrivateParser() if prefer_private_parser else GenericTableParser()
    candidates = parser.parse(text)
    if not candidates and prefer_private_parser:
        parser = GenericTableParser()
        candidates = parser.parse(text)

    inserted = 0
    needs_review = 0
    duplicate_candidates = 0

    for candidate in candidates:
        transaction_date = parse_date(candidate.date_text, default_year=datetime.now().year)
        direction = infer_direction(candidate.amount, candidate.description)
        merchant = normalize_merchant(candidate.description)
        decision = categorize(candidate.description, merchant, db)
        status = status_from_confidence(decision.confidence, suspicious=candidate.suspicious)
        dedupe_key = make_dedupe_key(str(statement.id), transaction_date, candidate.amount, candidate.description)

        transaction = Transaction(
            statement_id=statement.id,
            account_id=statement.account_id,
            date=transaction_date,
            posted_date=transaction_date,
            description_raw=candidate.description,
            description_redacted=redact_description(candidate.description),
            merchant=merchant,
            amount=candidate.amount,
            direction=direction,
            category_id=decision.category_id,
            confidence=decision.confidence,
            status=status,
            manual_override=False,
            source_line=candidate.source_line,
            dedupe_key=dedupe_key,
        )
        db.add(transaction)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            duplicate_candidates += 1
            continue
        inserted += 1
        if status.value != "reviewed":
            needs_review += 1

    statement.parser_name = parser.name
    statement.parsed_count = inserted
    statement.needs_review_count = needs_review
    statement.duplicate_candidate_count = duplicate_candidates
    statement.parse_status = ParseStatus.needs_review if needs_review else ParseStatus.parsed
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement
