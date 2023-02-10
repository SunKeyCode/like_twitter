import asyncio
from datetime import datetime, date
from typing import List, Union

from sqlalchemy import (
    Column, Integer, String, Sequence, ForeignKey, Date, delete
)
from sqlalchemy.orm import relationship, Mapped, join, mapped_column, selectinload, \
    joinedload
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import BYTEA, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError

from database import Base, async_session, async_engine, async_sessionmaker
from custom_exceptions import DbIntegrityError


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Sequence("user_id"), primary_key=True)
    user_name: str = Column(String(20), nullable=False, unique=True)
    first_name: str = Column(String(50), nullable=True)
    last_name: str = Column(String(50), nullable=True)
    reg_date: date = Column(Date, default=datetime.today)

    # delete orphan???
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author", lazy="raise")

    async def add_user(
            self,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            async with session.begin():
                session.add(self)

    async def get_followers(
            self,
            only_id=False,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        """
        Returns followers of user.

        :param a_session:
        :param only_id:
        :return:
        """

        sub_query = select(Follower.follower_id).where(Follower.user_id == self.user_id)
        async with a_session() as session:
            query_result = await session.execute(
                select(User).where(User.user_id.in_(sub_query))
            )
            # limit and offset !!!!!!!!!!!!!!!!!

            followers = query_result.scalars().all()
            return followers

    async def user_follows(
            self,
            only_id=False,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        """
        Returns users that user follows.

        :param a_session:
        :param only_id:
        :return:
        """

        if only_id:
            query_param = User.user_id
        else:
            query_param = User

        sub_query = select(Follower.user_id).where(Follower.follower_id == self.user_id)
        async with a_session() as session:
            query = select(query_param).where(User.user_id.in_(sub_query))
            query_result = await session.execute(query)
            # limit and offset !!!!!!!!!!!!!!!!!

            followers = query_result.scalars().all()
            return followers

    @classmethod
    async def get_user(
            cls,
            user_id: int,
            a_session: async_sessionmaker[AsyncSession] = async_session,
            with_tweets=False
    ):
        async with a_session() as session:
            query_result = await session.execute(
                select(cls)
                .where(cls.user_id == user_id)
            )
            user: User = query_result.scalars().one_or_none()

        return user

    async def follow(
            self,
            user: Union["User", int],
            a_session: async_sessionmaker[AsyncSession] = async_session
    ) -> bool:
        if isinstance(user, User):
            user_id = user.user_id
        elif isinstance(user, int):
            user_id = user
        else:
            raise TypeError

        add_check_query = select(Follower) \
            .where(Follower.follower_id == self.user_id) \
            .where(Follower.user_id == user_id)

        async with a_session() as session:
            async with session.begin():
                follower_association = Follower()
                follower_association.follower_id = self.user_id
                follower_association.user_id = user_id
                session.add(follower_association)

            check = await session.execute(add_check_query)

        if check.one_or_none():
            return True
        else:
            return False

    async def unfollow(
            self,
            user: Union["User", int],
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        if isinstance(user, User):
            user_id = user.user_id
        elif isinstance(user, int):
            user_id = user
        else:
            raise TypeError

        async with a_session() as session:
            async with session.begin():
                await session.execute(
                    delete(Follower)
                    .where(Follower.follower_id == self.user_id)
                    .where(Follower.user_id == user_id)
                )

    def to_json(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def __repr__(self):
        return f"User(id={self.user_id}, user_name={self.user_name})"


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id: int = Column(Integer, Sequence("tweet_id"), primary_key=True)
    author_id: int = Column(ForeignKey("table_users.user_id"), nullable=False)
    content: str = Column(String, nullable=False)
    picture_id: int = Column(ForeignKey("table_pictures.picture_id"), nullable=True)

    likes: Mapped[List["Like"]] = relationship(lazy="raise")

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="raise")

    async def add_tweet(
            self, a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            async with session.begin():
                session.add(self)

    @classmethod
    async def tweet_by_id(
            cls,
            tweet_id: int,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            query = select(cls) \
                .where(cls.tweet_id == tweet_id) \
                .options(selectinload(cls.likes).selectinload(Like.user),
                         selectinload(cls.author))
            query_result = await session.execute(query)
            tweet = query_result.scalars().unique().one_or_none()

        return tweet

    @classmethod
    async def tweets_list(
            cls,
            users: List[int],
            a_session: async_sessionmaker[AsyncSession] = async_session,
    ) -> List[User] | List[int]:

        async with a_session() as session:
            query = select(cls) \
                .where(cls.author_id.in_(users)) \
                .options(selectinload(cls.likes).selectinload(Like.user),
                         selectinload(cls.author))
            query_result = await session.execute(
                # select(cls).where(cls.author_id.in_(users))
                query
            )
            tweets = query_result.scalars().all()

            # limit and offset !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        return tweets

    def __repr__(self):
        return f"Tweet(id={self.tweet_id}, " \
               f"author={self.author_id}, text={self.content})"

    def to_json(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


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

    async def add_like(
            self,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            try:
                async with session.begin():
                    session.add(self)
            except ForeignKeyViolationError:
                print("*" * 50)
            except IntegrityError as exc:

                raise DbIntegrityError(exc.orig)

    @classmethod
    async def remove_like(
            cls,
            tweet_id,
            user_id,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):

        # select_query = select()
        delete_query = delete(Like) \
            .where(Like.user_id == user_id) \
            .where(Like.tweet_id == tweet_id).returning()

        async with a_session() as session:
            async with session.begin():
                deleted_row = await session.execute(delete_query)

        return deleted_row.rowcount


class Picture(Base):
    __tablename__ = "table_pictures"

    picture_id: int = Column(Integer, Sequence("picture_id"), primary_key=True)
    name: str = Column(String, nullable=False)
    binary_data = Column(BYTEA, nullable=False)

    # picture_path = Column(String, nullable=False) ????

    async def add(self, a_session: async_sessionmaker[AsyncSession] = async_session):
        async with a_session() as session:
            async with session.begin():
                session.add(self)


class Follower(Base):
    __tablename__ = "table_followers"
    # constraint user_id != follower_id
    # on_delete???
    user_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(ForeignKey("table_users.user_id"), primary_key=True)


async def create_test_data(a_session: async_session):
    async with a_session() as session:
        async with session.begin():
            user1 = User(user_name="MAIN TEST USER")
            user2 = User(user_name="user2")
            user3 = User(user_name="user3")

            session.add(user1)
            session.add(user2)
            session.add(user3)

    await user2.follow(user1)
    await user3.follow(user1)


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await create_test_data(async_session)


if __name__ == '__main__':
    asyncio.run(create_all())
