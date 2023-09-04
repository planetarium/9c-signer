import typing

from redis import StrictRedis
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import max as max_

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


def get_next_nonce(db: Session, redis: StrictRedis, address: str) -> int:
    cache_key = f"{address}_nonce"
    if redis.exists(cache_key):
        return redis.incr(cache_key)
    nonce = db.query(max_(Transaction.nonce)).filter_by(signer=address).scalar()
    if nonce is None:
        nonce = 0
    redis.set(cache_key, nonce, nx=True)
    return redis.incr(cache_key)
