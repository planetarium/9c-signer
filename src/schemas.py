import datetime
import typing
import uuid
from enum import Enum

from pydantic import BaseModel, field_serializer


class TransactionResult(str, Enum):
    CREATED = "CREATED"
    STAGED = "STAGED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    INVALID = "INVALID"


class Transaction(BaseModel):
    tx_id: str
    tx_result: TransactionResult
    payload: str
    signer: str
    nonce: int
    created_at: datetime.datetime
    task_id: uuid.UUID
    exc: typing.Optional[str] = None

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()


class SignRequest(BaseModel):
    plainValue: str
    staging: bool = True
