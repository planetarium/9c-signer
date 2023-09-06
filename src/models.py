import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Transaction(Base):
    __tablename__ = "transaction"

    tx_id: Mapped[str] = mapped_column(String, primary_key=True)
    tx_result: Mapped[str] = mapped_column(String, nullable=True)
    payload: Mapped[str] = mapped_column(String, nullable=False)
    signer: Mapped[str] = mapped_column(String, nullable=False, index=True)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    __table_args__ = (UniqueConstraint(signer, nonce),)
