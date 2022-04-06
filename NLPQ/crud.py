from typing import List

from sqlalchemy.orm import Session  # type: ignore

from .models import Transaction

def get_transaction_by_hash(session: Session, transaction_hash: str) -> Transaction:
    return session.query(Transaction).filter(Transaction.transaction_hash == transaction_hash).first()


def get_transactions(session: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
    return session.query(Transaction).offset(skip).limit(limit).all()

