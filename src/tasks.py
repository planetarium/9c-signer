import datetime
import hashlib
import pickle

import bencodex
from celery import Celery
from redis import StrictRedis

from src.config import config
from src.crud import create_transaction, get_next_nonce
from src.database import SessionLocal
from src.graphql import stage_transaction
from src.kms import Signer
from src.schemas import SignRequest
from src.schemas import Transaction as TransactionSchema

celery = Celery()
celery.conf.update(config)
celery.conf.broker_url = config.celery_broker_url
celery.conf.result_backend = config.celery_result_backend


db = SessionLocal()
redis = StrictRedis(host=config.redis_url.host, port=config.redis_url.port, db=0)


@celery.task()
def sign(serialized_action: bytes, headless_url: str) -> None:
    action: SignRequest = pickle.loads(serialized_action)
    signer = Signer(config.kms_key_id)
    created_at = datetime.datetime.utcnow()
    nonce = get_next_nonce(db, redis, signer.address)
    unsigned_tx = signer.unsigned_tx(nonce, action.plainValue, created_at)
    signature = signer.sign_tx(bencodex.dumps(unsigned_tx))
    signed_tx = signer.attach_sign(unsigned_tx, signature)
    serialized = bencodex.dumps(signed_tx)
    tx_id = hashlib.sha256(serialized).hexdigest()
    payload = serialized.hex()
    tx_schema = TransactionSchema(
        tx_id=tx_id,
        tx_result=None,
        payload=payload,
        signer=signer.address,
        nonce=nonce,
        created_at=created_at,
    )
    create_transaction(db, tx_schema)
    if action.staging:
        stage_transaction(headless_url, payload)
