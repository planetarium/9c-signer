import logging
import pickle
import typing
import uuid
from functools import lru_cache

from celery import chain
from fastapi import Depends, FastAPI
from fastapi_restful.tasks import repeat_every
from redis import StrictRedis
from sqlalchemy.orm import Session

from src.config import Settings, config
from src.crud import get_transaction_by_task_id, get_transactions
from src.database import SessionLocal
from src.kms import Signer
from src.schemas import SignRequest, Transaction, TransactionStatus
from src.tasks import sign, stage, sync_tx_result

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


@lru_cache()
def get_settings():
    return config


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_signer():
    signer = Signer(config.kms_key_id)
    return signer


def get_redis():
    redis = StrictRedis(host=config.redis_url.host, port=config.redis_url.port, db=0)
    return redis


app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=config.sync_interval, logger=logger)
def schedule_sync_tx_result():
    logger.info("start scheduled sync")
    task = sync_tx_result.delay()
    logger.info(f"send task({task.id})")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/ping")
async def pong():
    return {"msg": "pong"}


@app.get("/transactions/", response_model=typing.List[Transaction])
def transactions(db: Session = Depends(get_db)):
    return get_transactions(db, status=TransactionStatus.CREATED)


@app.get("/transactions/{task_id}/", response_model=typing.Optional[Transaction])
def get_transaction(task_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_transaction_by_task_id(db, task_id)


@app.post("/transactions/")
def sign_tx(
    action: SignRequest,
    settings: Settings = Depends(get_settings),
):
    headless_url = str(settings.headless_url)
    serialized = pickle.dumps(action)
    chain_task = chain(sign.s(serialized), stage.s(headless_url))()
    task_id = chain_task.parent.id
    chain_task_id = chain_task.id
    return {"task_id": task_id, "chain_task_id": chain_task_id}
