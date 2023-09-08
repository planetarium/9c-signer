import datetime
import hashlib
import pickle

import bencodex
from celery import Celery, group
from celery.result import GroupResult
from gql.transport.exceptions import TransportQueryError
from httpx import RequestError
from redis import StrictRedis

from src.config import config
from src.crud import (
    create_transaction,
    get_next_nonce,
    get_transaction,
    get_transactions,
    put_transaction,
)
from src.database import SessionLocal
from src.graphql import check_transaction_result, stage_transaction
from src.kms import Signer
from src.schemas import SignRequest
from src.schemas import Transaction as TransactionSchema
from src.schemas import TransactionStatus

celery = Celery()
celery.conf.update(config)
celery.conf.broker_url = config.celery_broker_url
celery.conf.result_backend = config.celery_result_backend


db = SessionLocal()
redis = StrictRedis(host=config.redis_url.host, port=config.redis_url.port, db=0)


@celery.task(bind=True)
def sign(self, serialized_action: bytes) -> str:
    action: SignRequest = pickle.loads(serialized_action)
    signer = Signer(config.kms_key_id)
    created_at = datetime.datetime.now(datetime.timezone.utc)
    nonce = get_next_nonce(db, redis, signer.address)
    unsigned_tx = signer.unsigned_tx(nonce, action.plainValue, created_at)
    signature = signer.sign_tx(bencodex.dumps(unsigned_tx))
    signed_tx = signer.attach_sign(unsigned_tx, signature)
    serialized = bencodex.dumps(signed_tx)
    tx_id = hashlib.sha256(serialized).hexdigest()
    payload = serialized.hex()
    tx_schema = TransactionSchema(
        tx_id=tx_id,
        tx_result=TransactionStatus.CREATED,
        payload=payload,
        signer=signer.address,
        nonce=nonce,
        created_at=created_at,
        task_id=self.request.id,
    )
    create_transaction(db, tx_schema)
    return tx_id


@celery.task(
    autoretry_for=(RequestError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def stage(tx_id: str, headless_url: str) -> str:
    tx = get_transaction(db, tx_id)
    try:
        stage_transaction(headless_url, tx.payload)
    except TransportQueryError:
        tx.tx_result = TransactionStatus.INVALID
    else:
        tx.tx_result = TransactionStatus.STAGED
    put_transaction(db, tx)
    return tx_id


@celery.task()
def sync_tx_result() -> GroupResult:
    transactions = get_transactions(db, TransactionStatus.STAGED)
    return group(
        tx_result.s(transaction.tx_id, str(config.headless_url))
        for transaction in transactions
    )()


@celery.task(
    autoretry_for=(RequestError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def tx_result(tx_id: str, headless_url: str):
    result = check_transaction_result(headless_url, tx_id)
    tx = get_transaction(db, tx_id)
    tx.tx_result = result.txStatus
    if result.exceptionName is not None:
        tx.exc = result.exceptionName
    put_transaction(db, tx)
