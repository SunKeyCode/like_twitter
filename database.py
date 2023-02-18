from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_URL = "postgresql+asyncpg://admin:admin@localhost/admin"
async_engine = create_async_engine(DB_URL)  # echo=True
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
