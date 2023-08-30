from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import fixture

from src.main import create_app


@fixture
def fx_app() -> FastAPI:
    return create_app()


@fixture
def fx_test_client(fx_app: FastAPI) -> TestClient:
    return TestClient(fx_app)
