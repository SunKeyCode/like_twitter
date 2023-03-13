import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs import app_config
from db.base import *
from fastapi.testclient import TestClient

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
    user=app_config.DB_USER,
    password=app_config.DB_PASSWORD,
    host=app_config.DB_HOST,
    db_name=app_config.DB_NAME_TEST,
)

async_engine = create_async_engine(DB_URL, pool_size=10)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)

crud_cache = {}


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
def crud_storage():
    return crud_cache


@pytest.fixture(scope="session")
async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def db_session():
    session = async_session()
    yield session
    session.close()
