from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models import Transaction
from src.schemas import Transaction as TransactionSchema


def test_main(fx_test_client: TestClient):
    resp = fx_test_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"Hello": "World"}


def test_pong(fx_test_client: TestClient):
    resp = fx_test_client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "pong"}


def test_get_transactions(
    fx_test_client: TestClient, fx_tx: Transaction, fx_tx_schema: TransactionSchema
):
    resp = fx_test_client.get("/transactions/")
    assert resp.status_code == 200
    result = resp.json()
    assert result == [fx_tx_schema.model_dump()]


def test_create_transaction(
    fx_test_client: TestClient, fx_tx_schema: TransactionSchema, db: Session
):
    data = fx_tx_schema.model_dump()
    resp = fx_test_client.post("/transactions/", json=data)
    result = resp.json()
    assert result == data
    assert resp.status_code == 200
    tx = db.query(Transaction).one()
    assert tx.tx_id == fx_tx_schema.tx_id
    assert tx.tx_result == fx_tx_schema.tx_result
    assert tx.signer == fx_tx_schema.signer
    assert tx.nonce == fx_tx_schema.nonce
    assert tx.payload == fx_tx_schema.payload
    assert tx.created_at == fx_tx_schema.created_at
