import hashlib
import pickle

import bencodex
from celery import Celery
from dateutil import parser

from src.config import config
from src.crud import create_transaction
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


@celery.task()
def sign(serialized_action: bytes, headless_url: str, nonce: int) -> None:
    action: SignRequest = pickle.loads(serialized_action)
    signer = Signer(config.kms_key_id)
    unsigned_tx = signer.unsigned_tx(action, nonce, headless_url)
    signature = signer.sign_tx(unsigned_tx)
    signed_tx = signer.sign_transaction(headless_url, unsigned_tx, signature)
    tx_id = hashlib.sha256(signed_tx).hexdigest()
    des = bencodex.loads(signed_tx)
    created_at = parser.parse(des[b"t"])
    payload = signed_tx.hex()
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
