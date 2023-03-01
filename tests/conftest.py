import pytest

from fastapi.testclient import TestClient

from routes_ import app

pytestmark = pytest.mark.anyio

storage = {}


@pytest.fixture(scope="module")
def main_storage():
    return storage


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    with TestClient(app) as client:
        yield client
