import pickle
import typing
import uuid
from functools import lru_cache

from celery import chain
from fastapi import Depends, FastAPI
from redis import StrictRedis
from sqlalchemy.orm import Session

from src.config import Settings, config
from src.crud import get_transaction_by_task_id, get_transactions
from src.database import SessionLocal
from src.kms import Signer
from src.schemas import SignRequest, Transaction
from src.tasks import sign, stage


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


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/ping")
async def pong():
    return {"msg": "pong"}


@app.get("/transactions/", response_model=typing.List[Transaction])
def transactions(db: Session = Depends(get_db)):
    return get_transactions(db)


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
    if action.staging:
        chain_task = chain(sign.s(serialized), stage.s(headless_url))()
        task_id = chain_task.id
    else:
        task = sign.delay(serialized)
        task_id = task.id

    return {"task_id": task_id}
