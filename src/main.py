import pickle
import typing
from functools import lru_cache

from fastapi import Depends, FastAPI
from redis import StrictRedis
from sqlalchemy.orm import Session

from src.config import Settings, config
from src.crud import get_transactions
from src.database import SessionLocal
from src.kms import Signer
from src.schemas import SignRequest, Transaction
from src.tasks import sign


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


@app.post("/transactions/")
def sign_tx(
    action: SignRequest,
    settings: Settings = Depends(get_settings),
):
    headless_url = str(settings.headless_url)
    serialized = pickle.dumps(action)
    task = sign.delay(serialized, headless_url)
    return {"task_id": task.id}
