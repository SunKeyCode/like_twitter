from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_engine
from db.base_class import Base
from db_models.user_model import User


async def create_test_data(a_session: AsyncSession):
    async with a_session.begin():
        user1 = User(user_name="MAIN TEST USER", hashed_password="123")
        user2 = User(user_name="user2", hashed_password="123")
        user3 = User(user_name="user3", hashed_password="123")

        a_session.add_all([user1, user2, user3])


async def create_all(session):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await create_test_data(session)
