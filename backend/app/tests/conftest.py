import asyncio
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import create_database, drop_database, database_exists
from fastapi.testclient import TestClient

from configs import app_config
from tests.utils.db import create_db, drop_db
from db.base import *

os.environ.setdefault("TESTING", "True")

from main import app

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
    user=app_config.DB_USER,
    password=app_config.DB_PASSWORD,
    host=app_config.DB_HOST,
    db_name=app_config.DB_NAME_TEST,
)

async_engine = create_async_engine(DB_URL)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)

testing_cache = {}


@pytest.fixture(scope='session')
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def storage():
    return testing_cache


@pytest.fixture(scope="session", autouse=True)
async def create_all():
    await drop_db(DB_URL)
    await create_db(DB_URL)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield None
    await drop_db(DB_URL)


@pytest.fixture(scope="session")
def db_session():
    session = async_session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    print("Testing =", os.environ.get("TESTING"))
    with TestClient(app) as client:
        yield client
