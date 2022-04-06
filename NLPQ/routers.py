from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore

from . import crud, models
from .database import SessionLocal, engine
from .schemas import TransactionBase


models.Base.metadata.create_all(bind=engine)
transactionrouter = APIRouter()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@transactionrouter.get("/transactions/", response_model=List[TransactionBase])
def read_transactions(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    transactions = crud.get_transactions(session=session, skip=skip, limit=limit)
    return [i.serialize for i in transactions]


@transactionrouter.get("/transactions/{transaction_hash}", response_model=TransactionBase)
def read_transaction(transaction_hash: str, session: Session = Depends(get_session)):
    transaction = crud.get_transaction_by_hash(session=session, transaction_hash=transaction_hash)
    if transaction is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return transaction.serialize
