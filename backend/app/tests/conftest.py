import asyncio

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm.exc import FlushError
from starlette import status
from starlette.exceptions import HTTPException

from api.dependencies import get_db_session
from configs import app_config
from custom_exc.db_exception import DbIntegrityError
from db.base import Base
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


@pytest.fixture(scope="module")
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def storage():
    return {}


@pytest.fixture(scope="module")
def engine():
    return create_async_engine(DB_URL)


@pytest.fixture(scope="module")
def async_session(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope="module")
async def create_all(engine):
    await drop_db(DB_URL)
    await create_db(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield 1

    await drop_db(DB_URL)


@pytest.fixture(scope="function")
def db_session(async_session):
    session = async_session()
    yield session


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
