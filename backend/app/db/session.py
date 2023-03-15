from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs import app_config


DB_URL = "postgresql+asyncpg://{user}:{password}@{host}/{db_name}".format(
        user=app_config.DB_USER,
        password=app_config.DB_PASSWORD,
        host=app_config.DB_HOST,
        db_name=app_config.DB_NAME,
)

async_engine = create_async_engine(DB_URL, pool_size=20, echo=False)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
