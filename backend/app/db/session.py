from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG")
TESTING = os.environ.get("TESTING")
DB_NAME = os.environ.get("DB_NAME")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        db_name=DB_NAME,
)

async_engine = create_async_engine(DB_URL, pool_size=20, echo=False)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
