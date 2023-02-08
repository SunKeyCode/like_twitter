import asyncio
from datetime import datetime, date
from typing import List

from sqlalchemy import (
    Column, Integer, String, Sequence, ARRAY, ForeignKey, Date, delete
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, async_session, async_engine, async_sessionmaker


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Sequence("user_id"), primary_key=True)
    user_name: str = Column(String(20), nullable=False, unique=True)
    first_name: str = Column(String(50), nullable=True)
    last_name: str = Column(String(50), nullable=True)
    reg_date: date = Column(Date, default=datetime.today)

    # followers: Mapped[List["User"]] = relationship(secondary="table_followers")

    tweets: Mapped[List["Tweet"]] = relationship(back_populates="user")

    @classmethod
    async def get_user(cls, a_session: async_session, user_id: int):
        async with a_session() as session:
            query_result = await session.execute(
                select(cls)
                .where(cls.user_id == user_id)
            )
            user = query_result.scalars().one_or_none()
        return user

    async def follow(
            self,
            user: "User",
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            async with session.begin():
                follower_association = Follower()
                follower_association.follower_id = self.user_id
                follower_association.user_id = user.user_id
                session.add(follower_association)

    async def unfollow(
            self,
            user: "User",
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            async with session.begin():
                await session.execute(
                    delete(Follower)
                    .where(Follower.follower_id == self.user_id)
                    .where(Follower.user_id == user.user_id)
                )


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id: int = Column(Integer, Sequence("tweet_id"), primary_key=True)
    user_id: int = Column(ForeignKey("table_users.user_id"), nullable=False)
    tweet_text: str = Column(String, nullable=False)
    picture_id: int = Column(ForeignKey("table_pictures.picture_id"), nullable=True)
    likes: List[int] = Column(ARRAY(Integer), nullable=True)  # ???

    user: Mapped["User"] = relationship(back_populates="tweets")


class Picture(Base):
    __tablename__ = "table_pictures"

    picture_id: int = Column(Integer, Sequence("picture_id"), primary_key=True)
    name: str = Column(String, nullable=False)
    binary_data = Column(BYTEA, nullable=False)
    # picture_path = Column(String, nullable=False) ????


class Follower(Base):
    __tablename__ = "table_followers"
    # constraint user_id != follower_id
    # on_delete???
    user_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(ForeignKey("table_users.user_id"), primary_key=True)


# followers_table = Table(
#     # constraint user_id != follower_id
#     "table_followers",
#     Base.metadata,
#     Column(
#         "user_id",
#         ForeignKey("table_users.user_id", ondelete="CASCADE"),
#         primary_key=True
#     ),
#     Column(
#         "follower_id",
#         ForeignKey("table_users.user_id", ondelete="CASCADE"),
#         primary_key=True
#     ),
# )


async def create_test_data(a_session: async_session):
    async with a_session() as session:
        async with session.begin():
            user1 = User()
            user1.user_name = "USER1"
            user2 = User(user_name="USER2")
            user3 = User(user_name="USER3")

            session.add(user1)
            session.add(user2)
            session.add(user3)

    await user2.follow(user1)
    await user3.follow(user1)
    await user2.unfollow(user1)


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await create_test_data(async_session)


if __name__ == '__main__':
    asyncio.run(create_all())
