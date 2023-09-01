import typing
from functools import lru_cache

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from src.config import config
from src.crud import create_transaction, get_transactions
from src.database import SessionLocal
from src.schemas import Transaction


@lru_cache()
def get_settings():
    return config


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.post("/transactions/", response_model=Transaction)
def create_tx(tx: Transaction, db: Session = Depends(get_db)):
    return create_transaction(db, tx)
