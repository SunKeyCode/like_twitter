import os
from logging import getLogger
from logging.config import dictConfig

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from configs import app_config
from configs.logger_config import LOGGER_CONF

logger = getLogger("main.session")
dictConfig(LOGGER_CONF)

TESTING = os.environ.get("TESTING")

logger.debug("TESTING_CONFIG=%s", TESTING)

if TESTING == "True":
    db_name = app_config.DB_NAME_TEST
else:
    db_name = app_config.DB_NAME

DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
    user=app_config.DB_USER,
    password=app_config.DB_PASSWORD,
    host=app_config.DB_HOST,
    db_name=db_name,
)

async_engine = create_async_engine(DB_URL, pool_size=20, echo=False)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
