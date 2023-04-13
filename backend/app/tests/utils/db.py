from copy import copy

from configs import app_config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
    user=app_config.DB_USER,
    password=app_config.DB_PASSWORD,
    host=app_config.DB_HOST,
    db_name=app_config.DB_NAME_TEST,
)


def _set_url_database(url: URL, database):
    """Set the database of an engine URL.

    :param url: A SQLAlchemy engine URL.
    :param database: New database to set.

    """
    if hasattr(url, "_replace"):
        # Cannot use URL.set() as database may need to be set to None.
        ret = url._replace(database=database)
    else:  # SQLAlchemy <1.4
        url = copy(url)
        url.database = database
        ret = url
    assert ret.database == database, ret
    return ret


async def create_db(url):
    url = make_url(url)
    database = url.database

    url = _set_url_database(url, database=app_config.DB_NAME)

    async_engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with async_engine.begin() as conn:
        query = "CREATE DATABASE {}".format(database)
        await conn.execute(text(query))

    await async_engine.dispose()


async def drop_db(url):
    url = make_url(url)
    database = url.database

    url = _set_url_database(url, database=app_config.DB_NAME)

    async_engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with async_engine.connect() as conn:
        # Disconnect all users from the database we are dropping.
        version = conn.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        query = """
                    SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{database}'
                    AND {pid_column} <> pg_backend_pid();
                    """.format(
            pid_column=pid_column, database=database
        )
        await conn.execute(text(query))

        # Drop database
        query = f"DROP DATABASE IF EXISTS {database}"
        await conn.execute(text(query))

    await async_engine.dispose()
