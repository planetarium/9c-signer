import datetime
import enum
import typing

from pydantic import BaseModel, field_serializer


class Transaction(BaseModel):
    tx_id: str
    tx_result: typing.Optional[str] = None
    payload: str
    signer: str
    nonce: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()


class SignedTransaction(BaseModel):
    payload: str


class NetworkEnum(str, enum.Enum):
    MAIN = "main"
    INTERNAL = "internal"


class SignRequest(BaseModel):
    plainValue: str
    staging: bool = True
    network: NetworkEnum = NetworkEnum.MAIN
