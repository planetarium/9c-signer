import datetime
import typing
import uuid
from enum import Enum

from pydantic import BaseModel, field_serializer, field_validator


class TransactionStatus(str, Enum):
    CREATED = "CREATED"
    STAGED = "STAGED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    INVALID = "INVALID"


class Transaction(BaseModel):
    tx_id: str
    tx_result: TransactionStatus
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


class TransactionResult(BaseModel):
    txStatus: TransactionStatus
    exceptionName: typing.Optional[str] = None

    @classmethod
    @field_validator("txStatus")
    def validate_tx_status(cls, v: str) -> TransactionStatus:
        if v.upper() == "SUCCESS":
            return TransactionStatus.SUCCESS
        if v.upper() == "INVALID":
            return TransactionStatus.INVALID
        return TransactionStatus.FAILED
