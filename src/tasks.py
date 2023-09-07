import datetime
import hashlib
import pickle

import bencodex
from celery import Celery
from httpx import RequestError
from redis import StrictRedis

from src.config import config
from src.crud import create_transaction, get_next_nonce
from src.database import SessionLocal
from src.graphql import stage_transaction
from src.kms import Signer
from src.schemas import SignRequest
from src.schemas import Transaction as TransactionSchema
from src.schemas import TransactionResult

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
        tx_result=TransactionResult.CREATED,
        payload=payload,
        signer=signer.address,
        nonce=nonce,
        created_at=created_at,
        task_id=self.request.id,
    )
    create_transaction(db, tx_schema)
    return payload


@celery.task(
    autoretry_for=(RequestError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def stage(payload: str, headless_url: str):
    stage_transaction(headless_url, payload)
