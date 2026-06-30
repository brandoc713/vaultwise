from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, TypeDecorator

from app.database import Base


class GUID(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class PortableJSON(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(JSON)


class AccountType(str, enum.Enum):
    checking = "checking"
    savings = "savings"
    credit = "credit"
    loan = "loan"
    investment = "investment"


class CategoryKind(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"
    loan = "loan"
    investment = "investment"


class FileType(str, enum.Enum):
    pdf = "pdf"
    csv = "csv"


class TextExtractionStatus(str, enum.Enum):
    text_found = "text_found"
    scanned_or_empty = "scanned_or_empty"
    failed = "failed"


class ParseStatus(str, enum.Enum):
    uploaded = "uploaded"
    parsed = "parsed"
    needs_review = "needs_review"
    failed = "failed"


class TransactionDirection(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class TransactionStatus(str, enum.Enum):
    reviewed = "reviewed"
    needs_review = "needs_review"
    flagged = "flagged"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    statements: Mapped[list[Statement]] = relationship(back_populates="account")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="account")


class Statement(Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("accounts.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    parser_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    text_extraction_status: Mapped[TextExtractionStatus] = mapped_column(
        Enum(TextExtractionStatus), default=TextExtractionStatus.scanned_or_empty
    )
    parse_status: Mapped[ParseStatus] = mapped_column(Enum(ParseStatus), default=ParseStatus.uploaded)
    parsed_count: Mapped[int] = mapped_column(default=0)
    needs_review_count: Mapped[int] = mapped_column(default=0)
    duplicate_candidate_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped[Account] = relationship(back_populates="statements")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="statement")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    kind: Mapped[CategoryKind] = mapped_column(Enum(CategoryKind), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)

    transactions: Mapped[list[Transaction]] = relationship(back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (Index("ix_transactions_dedupe_key", "dedupe_key", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    statement_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("statements.id"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("accounts.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description_raw: Mapped[str] = mapped_column(Text, nullable=False)
    description_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    direction: Mapped[TransactionDirection] = mapped_column(Enum(TransactionDirection), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("categories.id"), nullable=True)
    confidence: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.flagged)
    manual_override: Mapped[bool] = mapped_column(default=False)
    source_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    dedupe_key: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    account: Mapped[Account] = relationship(back_populates="transactions")
    statement: Mapped[Statement] = relationship(back_populates="transactions")
    category: Mapped[Category | None] = relationship(back_populates="transactions")


class Correction(Base):
    __tablename__ = "corrections"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("transactions.id"), nullable=False)
    previous_category_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    new_category_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    previous_merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("transactions.id"), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    predicted_category_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    confidence: Mapped[float] = mapped_column(default=0.0)
    features_json: Mapped[dict] = mapped_column(PortableJSON(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
