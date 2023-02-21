import asyncio
import logging
from datetime import datetime, date
from typing import List

from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Identity
)
from sqlalchemy.orm import relationship, Mapped, selectinload, joinedload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, async_session, async_engine, async_sessionmaker

logger = logging.getLogger("main.models")
MEDIA_PATH = "static/images/{user}/"


class Follower(Base):
    __tablename__ = "table_followers"
    # constraint user_id != follower_id
    # on_delete???
    user_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(ForeignKey("table_users.user_id"), primary_key=True)


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Identity(always=True), primary_key=True)
    user_name: str = Column(String(20), nullable=False, unique=True)
    first_name: str = Column(String(50), nullable=True)
    last_name: str = Column(String(50), nullable=True)
    reg_date: date = Column(Date, default=datetime.today)

    # delete orphan???
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author", lazy="raise")

    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="table_followers",
        primaryjoin=user_id == Follower.user_id,
        secondaryjoin=user_id == Follower.follower_id,
        viewonly=True,
    )

    following: Mapped[List["User"]] = relationship(
        secondary="table_followers",
        primaryjoin=user_id == Follower.follower_id,
        secondaryjoin=user_id == Follower.user_id,
        viewonly=True
    )

    def __repr__(self):
        return f"User(id={self.user_id}, user_name={self.user_name})"


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id: int = Column(Integer, Identity(always=True), primary_key=True)
    author_id: int = Column(ForeignKey("table_users.user_id"), nullable=False)
    content: str = Column(String, nullable=False)
    # добавить дату и время добавления твита,
    # чтобы использовать это для сортировки
    # order_by дата/время, количество лайков

    likes: Mapped[List["Like"]] = relationship(lazy="raise")

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="raise")

    attachments: Mapped[List["Media"]] = relationship(
        secondary="table_media_tweet_relation",
        lazy="raise",
    )

    @classmethod
    async def tweet_by_id(
            cls,
            tweet_id: int,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            query_result = await session.execute(
                select(cls)
                .where(cls.tweet_id == tweet_id)
                .options(
                    joinedload(cls.likes).selectinload(Like.user),
                    joinedload(cls.author),
                    selectinload(cls.attachments)
                )
            )
            tweet = query_result.scalars().unique().one_or_none()

        return tweet

    def __repr__(self):
        return f"Tweet(id={self.tweet_id}, " \
               f"author={self.author_id}, text={self.content})"


class Like(Base):
    __tablename__ = "table_likes"
    tweet_id: Mapped[int] = Column(
        ForeignKey("table_tweets.tweet_id"),
        primary_key=True,
    )
    user_id: Mapped[int] = Column(
        ForeignKey("table_users.user_id"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(lazy="raise")


class Media(Base):
    __tablename__ = "table_media"

    media_id: int = Column(Integer, Identity(always=True), primary_key=True)
    name: str = Column(String, nullable=False)
    path: str = Column(String, default=MEDIA_PATH.format(user="unknown_user"))

    # -----------------------------------------------
    # оставить только path, там будет path + filename


class MediaTweetRelation(Base):
    __tablename__ = "table_media_tweet_relation"

    tweet_id: Mapped[int] = Column(ForeignKey("table_tweets.tweet_id"),
                                   primary_key=True)
    media_id: Mapped[int] = Column(ForeignKey("table_media.media_id"), primary_key=True)


async def create_test_data(a_session: async_sessionmaker[AsyncSession]):
    async with a_session() as session:
        async with session.begin():
            logger.debug("Creating test users")
            user1 = User(user_name="MAIN TEST USER")
            user2 = User(user_name="user2")
            user3 = User(user_name="user3")

            session.add_all([user1, user2, user3])


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await create_test_data(async_session)


if __name__ == '__main__':
    asyncio.run(create_all())
