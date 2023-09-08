import typing
import uuid

from redis import StrictRedis
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import max as max_

from src.models import Transaction
from src.schemas import Transaction as TransactionSchema
from src.schemas import TransactionStatus


def get_transaction(db: Session, tx_id: str) -> Transaction:
    tx = db.query(Transaction).filter(Transaction.tx_id == tx_id).one()
    return tx


def get_transaction_by_task_id(
    db: Session, task_id: uuid.UUID
) -> typing.Optional[Transaction]:
    tx = db.query(Transaction).filter(Transaction.task_id == task_id).first()
    return tx


def get_transactions(
    db: Session, status: TransactionStatus
) -> typing.List[Transaction]:
    return db.query(Transaction).filter(Transaction.tx_result == status).all()


def create_transaction(db: Session, tx: TransactionSchema) -> Transaction:
    transaction = Transaction(
        tx_id=tx.tx_id,
        nonce=tx.nonce,
        signer=tx.signer,
        payload=tx.payload,
        created_at=tx.created_at,
        task_id=tx.task_id,
        tx_result=tx.tx_result,
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


def put_transaction(db: Session, tx: Transaction) -> Transaction:
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
