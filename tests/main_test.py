from celery.result import AsyncResult
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models import Transaction
from src.schemas import Transaction as TransactionSchema
from src.schemas import TransactionStatus


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
    expected = fx_tx_schema.model_dump()
    expected["task_id"] = str(expected["task_id"])
    assert result == [expected]


def test_sign_tx(celery_session_worker, fx_test_client: TestClient, db: Session):
    assert db.query(Transaction).count() == 0
    action = "6475373a747970655f69647532313a707265706172655f7265776172645f61737365747375363a76616c7565736475313a616c6c647531333a646563696d616c506c61636573313a0075373a6d696e746572736e75363a7469636b65727532313a52554e4553544f4e455f5341454852494d4e4952336569323235363565656c647531333a646563696d616c506c61636573313a0075373a6d696e746572736e75363a7469636b65727532313a52554e4553544f4e455f5341454852494d4e495232656931303533373565656c647531333a646563696d616c506c61636573313a1275373a6d696e746572736e75363a7469636b657275373a4352595354414c656931303331383030303030303030303030303030303030303030303065656c647531333a646563696d616c506c61636573313a0075373a6d696e746572736e75363a7469636b65727532313a52554e4553544f4e455f5341454852494d4e495231656933383334363065656575313a7232303acfcd6565287314ff70e4c4cf309db701c43ea5bd6565"  # noqa
    payload = {
        "plainValue": action,
        "staging": True,
    }
    resp = fx_test_client.post("/transactions/", json=payload)
    result = resp.json()
    task_id = result["task_id"]
    chain_task_id = result["chain_task_id"]
    task: AsyncResult = AsyncResult(chain_task_id)
    task.get()
    resp = fx_test_client.get(f"/transactions/{task_id}/")
    result = resp.json()
    assert result["task_id"] == str(task_id)
    assert result["nonce"] == 1
    assert result["tx_result"] == TransactionStatus.INVALID
