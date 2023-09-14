import datetime
import uuid

from celery.result import AsyncResult
from sqlalchemy.orm import Session

from src.crud import create_transaction
from src.schemas import Transaction, TransactionStatus
from src.tasks import sync_tx_result


# FIXME hang run with main_test
def test_sync_tx_result(
    celery_session_worker, db: Session, fx_kms_signer, fx_test_client
):
    tx_id = "bc1ad2658ba6f9a494f0137340f4f82266e65f4942d0a40db2ab54b34b24c001"
    schema = Transaction(
        tx_id=tx_id,
        nonce=10000,
        tx_result=TransactionStatus.STAGING,
        signer=fx_kms_signer.address,
        payload="payload",
        created_at=datetime.datetime.utcnow(),
        task_id=uuid.uuid4(),
    )
    create_transaction(db, schema)
    group_task: AsyncResult = sync_tx_result.delay()
    group_task.get()
    inner_task: AsyncResult = group_task.children[0]  # type: ignore
    inner_task.get()
    task_id = schema.task_id
    resp = fx_test_client.get(f"/transactions/tasks/{task_id}/")
    result = resp.json()
    assert result["task_id"] == str(task_id)
    assert result["nonce"] == 10000
    assert result["tx_result"] != TransactionStatus.STAGING
