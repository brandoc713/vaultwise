from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    AccountType,
    CategoryKind,
    FileType,
    ParseStatus,
    TextExtractionStatus,
    TransactionDirection,
    TransactionStatus,
)


class AccountCreate(BaseModel):
    name: str
    institution: str
    account_type: AccountType
    last_four: str | None = Field(default=None, max_length=4)


class AccountRead(AccountCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    kind: CategoryKind
    color: str


class StatementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    original_filename: str
    file_type: FileType
    sha256: str
    parser_name: str | None
    text_extraction_status: TextExtractionStatus
    parse_status: ParseStatus
    parsed_count: int
    needs_review_count: int
    duplicate_candidate_count: int
    created_at: datetime
    message: str | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    statement_id: uuid.UUID
    account_id: uuid.UUID
    date: date
    posted_date: date | None
    description: str
    merchant: str | None
    amount: Decimal
    direction: TransactionDirection
    category_id: uuid.UUID | None
    confidence: float
    status: TransactionStatus
    manual_override: bool


class TransactionUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    merchant: str | None = None
    status: TransactionStatus | None = None


class MLTrainResult(BaseModel):
    status: str
    model_version: str | None = None
    training_rows: int
    accuracy: float | None = None
    message: str


class MLPredictRequest(BaseModel):
    description: str
    merchant: str | None = None
    amount: float
    direction: TransactionDirection


class MLPredictResult(BaseModel):
    category_id: uuid.UUID | None
    confidence: float
    model_version: str | None
    source: str


class MLStatus(BaseModel):
    model_exists: bool
    model_version: str | None
    min_training_rows: int
