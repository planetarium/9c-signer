import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from src.database import Base


class Transaction(Base):
    __tablename__ = "transaction"

    tx_id = Column(String, primary_key=True)
    tx_result = Column(String, nullable=True)
    payload = Column(String, nullable=False)
    signer = Column(String, nullable=False, index=True)
    nonce = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint(signer, nonce),)
