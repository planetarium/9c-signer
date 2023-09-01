import typing

from sqlalchemy.orm import Session

from src.models import Transaction
from src.schemas import Transaction as TransactionSchema


def get_transaction(db: Session, tx_id: str) -> typing.Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.tx_id == tx_id).first()


def get_transactions(db: Session) -> typing.List[Transaction]:
    return db.query(Transaction).all()


def create_transaction(db: Session, tx: TransactionSchema) -> Transaction:
    transaction = Transaction(
        tx_id=tx.tx_id,
        nonce=tx.nonce,
        signer=tx.signer,
        payload=tx.payload,
        created_at=tx.created_at,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
