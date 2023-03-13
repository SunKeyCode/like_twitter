from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import asyncpg

import configs.app_config as config


async def creat_test_db():
    conn = await asyncpg.connect("postgresql://admin:admin@localhost/admin")
    await conn.execute("DROP DATABASE IF EXISTS tests")
    await conn.execute("CREATE DATABASE tests")
    await conn.close()

if config.TESTING == 'True':
    # asyncio.run(creat_test_db())
    DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        db_name=config.DB_NAME_TEST,
    )
    async_engine = create_async_engine(DB_URL, pool_size=20)
else:
    DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        db_name=config.DB_NAME,
    )
    async_engine = create_async_engine(DB_URL, pool_size=20, echo=True)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
