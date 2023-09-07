import datetime
import uuid
from typing import Generator

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from pytest_postgresql.janitor import DatabaseJanitor
from pytest_redis import factories

from src.config import config
from src.crud import create_transaction
from src.database import Base, SessionLocal, engine
from src.main import app
from src.models import Transaction
from src.schemas import Transaction as TransactionSchema

redis_proc = factories.redis_proc(port=6379)
DB_OPTS = sa.engine.url.make_url(str(config.database_url)).translate_connect_args()


@pytest.fixture(scope="session")
def database():
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("username")
    pg_pass = DB_OPTS.get("password")
    pg_db = DB_OPTS["database"]

    janitor = DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, 9.6, pg_pass)
    janitor.init()
    yield
    janitor.drop()


@pytest.fixture
def db(database) -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def fx_test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def fx_tx_schema() -> TransactionSchema:
    return TransactionSchema(
        tx_id="tx_id",
        tx_result=None,
        payload="payload",
        signer="signer",
        nonce=1,
        created_at=datetime.datetime.utcnow(),
        task_id=uuid.uuid4(),
    )


@pytest.fixture
def fx_tx(db, fx_tx_schema: TransactionSchema) -> Transaction:
    return create_transaction(db, fx_tx_schema)
