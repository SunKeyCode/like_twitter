import pytest
from fastapi.testclient import TestClient

from routes import app

from database import async_session


# pytestmark = pytest.mark.anyio


# @pytest.fixture
# def db_session():
#     session = async_session()
#     try:
#         yield session
#     finally:
#         session.close()

# except IntegrityError as exc:
#     raise custom_exceptions.DbIntegrityError(exc.args)
# except FlushError as exc:
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail=exc.args
#     )


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    with TestClient(app) as client:
        yield client
