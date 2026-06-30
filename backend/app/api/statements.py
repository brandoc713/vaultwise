from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Statement
from app.schemas import StatementRead
from app.services.ingestion import parse_statement, store_upload

router = APIRouter(prefix="/api/statements", tags=["statements"])


@router.get("", response_model=list[StatementRead])
def list_statements(db: Session = Depends(get_db)) -> list[Statement]:
    return db.query(Statement).order_by(Statement.created_at.desc()).all()


@router.post("/upload", response_model=StatementRead, status_code=201)
def upload_statement(
    account_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> StatementRead:
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")
    statement, message = store_upload(db, account_id, file)
    response = StatementRead.model_validate(statement)
    response.message = message
    return response


@router.get("/{statement_id}", response_model=StatementRead)
def get_statement(statement_id: UUID, db: Session = Depends(get_db)) -> Statement:
    statement = db.get(Statement, statement_id)
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found.")
    return statement


@router.post("/{statement_id}/parse", response_model=StatementRead)
def parse_statement_endpoint(statement_id: UUID, db: Session = Depends(get_db)) -> Statement:
    statement = db.get(Statement, statement_id)
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found.")
    return parse_statement(db, statement)
