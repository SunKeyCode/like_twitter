import asyncio
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm.exc import FlushError
from starlette import status
from starlette.exceptions import HTTPException

from api.dependencies import get_db_session
from configs import app_config
from custom_exc.db_exception import DbIntegrityError
from db.base import *
from tests.utils.db import create_db, drop_db

from main import app

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
    user=app_config.DB_USER,
    password=app_config.DB_PASSWORD,
    # host=app_config.DB_HOST,
    host="localhost",
    db_name=app_config.DB_NAME_TEST,
)

async_engine = create_async_engine(DB_URL)

async_session_test = async_sessionmaker(bind=async_engine, expire_on_commit=False)

testing_cache: dict[str, Any] = {}


async def override_db_session():
    try:
        async with async_session_test() as session:
            yield session
    except IntegrityError as exc:
        raise DbIntegrityError(exc.args)
    except FlushError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.args[0],
        )


app.dependency_overrides[get_db_session] = override_db_session


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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
    session = async_session_test()
    yield session
    session.close()
