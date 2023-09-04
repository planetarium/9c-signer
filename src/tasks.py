import hashlib
import pickle

import bencodex
from celery import Celery
from dateutil import parser

from src.config import config
from src.crud import create_transaction
from src.database import SessionLocal
from src.kms import Signer
from src.schemas import Transaction as TransactionSchema

celery = Celery()
celery.conf.update(config)
celery.conf.broker_url = config.celery_broker_url
celery.conf.result_backend = config.celery_result_backend


db = SessionLocal()


@celery.task()
def sign(serialized_action: bytes, headless_url: str, nonce: int) -> None:
    action = pickle.loads(serialized_action)
    signer = Signer(config.kms_key_id)
    unsigned_tx = signer.unsigned_tx(action, nonce, headless_url)
    signature = signer.sign_tx(unsigned_tx)
    signed_tx = signer.sign_transaction(headless_url, unsigned_tx, signature)
    tx_id = hashlib.sha256(signed_tx).hexdigest()
    tx = bencodex.loads(signed_tx)
    created_at = parser.parse(tx[b"t"])
    tx_schema = TransactionSchema(
        tx_id=tx_id,
        tx_result=None,
        payload=signed_tx.hex(),
        signer=signer.address,
        nonce=nonce,
        created_at=created_at,
    )
    create_transaction(db, tx_schema)
