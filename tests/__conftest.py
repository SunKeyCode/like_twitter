import pytest
import sqlalchemy_utils
import asyncio
import asyncpg
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from routes_ import app, get_db_session
import custom_exceptions
from models import Base

# from database import async_session

pytestmark = pytest.mark.anyio

DB_URL = "postgresql+asyncpg://admin:admin@localhost/tests"
async_engine = create_async_engine(DB_URL, pool_size=20, echo=True)
sync_engine = create_engine("postgresql://admin:admin@localhost/tests")
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


Base.metadata.create_all(sync_engine)


async def creat_test_db():
    conn = await asyncpg.connect("postgresql://admin:admin@localhost/admin")
    await conn.execute("DROP DATABASE IF EXISTS tests")
    await conn.execute("CREATE DATABASE tests")
    await conn.close()


async def override_get_db():
    db = async_session()
    print("()" * 150)
    try:
        yield db
    except IntegrityError as exc:
        raise custom_exceptions.DbIntegrityError(exc.args)
    finally:
        await db.close()


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    with TestClient(app) as client:
        yield client
