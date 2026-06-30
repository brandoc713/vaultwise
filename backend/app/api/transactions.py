from datetime import date
from io import StringIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Correction, Transaction, TransactionStatus
from app.schemas import TransactionRead, TransactionUpdate

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def serialize_transaction(transaction: Transaction) -> TransactionRead:
    return TransactionRead(
        id=transaction.id,
        statement_id=transaction.statement_id,
        account_id=transaction.account_id,
        date=transaction.date,
        posted_date=transaction.posted_date,
        description=transaction.description_redacted,
        merchant=transaction.merchant,
        amount=transaction.amount,
        direction=transaction.direction,
        category_id=transaction.category_id,
        confidence=transaction.confidence,
        status=transaction.status,
        manual_override=transaction.manual_override,
    )


def filtered_query(
    db: Session,
    account_id: UUID | None,
    category_id: UUID | None,
    status: TransactionStatus | None,
    start_date: date | None,
    end_date: date | None,
    search: str | None,
):
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if status:
        query = query.filter(Transaction.status == status)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Transaction.merchant.ilike(pattern), Transaction.description_redacted.ilike(pattern)))
    return query.order_by(Transaction.date.desc(), Transaction.created_at.desc())


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    account_id: UUID | None = None,
    category_id: UUID | None = None,
    status: TransactionStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[TransactionRead]:
    rows = filtered_query(db, account_id, category_id, status, start_date, end_date, search).all()
    return [serialize_transaction(row) for row in rows]


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
) -> TransactionRead:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    previous_category_id = transaction.category_id
    previous_merchant = transaction.merchant

    if payload.category_id is not None:
        category = db.get(Category, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        transaction.category_id = payload.category_id
    if payload.merchant is not None:
        transaction.merchant = payload.merchant
    if payload.status is not None:
        transaction.status = payload.status

    transaction.manual_override = True
    transaction.confidence = 1.0

    if transaction.category_id:
        db.add(
            Correction(
                transaction_id=transaction.id,
                previous_category_id=previous_category_id,
                new_category_id=transaction.category_id,
                previous_merchant=previous_merchant,
                new_merchant=transaction.merchant,
            )
        )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return serialize_transaction(transaction)


@router.get("/export.csv")
def export_transactions(
    account_id: UUID | None = None,
    category_id: UUID | None = None,
    status: TransactionStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> Response:
    rows = filtered_query(db, account_id, category_id, status, start_date, end_date, search).all()
    output = StringIO()
    output.write(
        "transaction_id,account_id,statement_id,date,posted_date,description,merchant,amount,direction,category_id,confidence,status,manual_override\n"
    )
    for row in rows:
        values = [
            row.id,
            row.account_id,
            row.statement_id,
            row.date,
            row.posted_date or "",
            row.description_redacted,
            row.merchant or "",
            f"{row.amount:.2f}",
            row.direction.value,
            row.category_id or "",
            f"{row.confidence:.2f}",
            row.status.value,
            str(row.manual_override).lower(),
        ]
        output.write(",".join(csv_escape(str(value)) for value in values) + "\n")
    return Response(content=output.getvalue(), media_type="text/csv")


def csv_escape(value: str) -> str:
    if any(character in value for character in [",", '"', "\n"]):
        return '"' + value.replace('"', '""') + '"'
    return value
