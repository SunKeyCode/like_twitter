import asyncio
from datetime import datetime, date
from typing import List, Union

from sqlalchemy import (
    Column, Integer, String, Sequence, ForeignKey, Date, delete, func
)
from sqlalchemy.orm import relationship, Mapped, join, mapped_column, selectinload, \
    joinedload, subqueryload, remote, foreign
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import BYTEA, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from asyncpg.exceptions import ForeignKeyViolationError

from database import Base, async_session, async_engine, async_sessionmaker
from custom_exceptions import DbIntegrityError

MEDIA_PATH = "static/images/{user}/"


class Follower(Base):
    __tablename__ = "table_followers"
    # constraint user_id != follower_id
    # on_delete???
    user_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(ForeignKey("table_users.user_id"), primary_key=True)


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Sequence("user_id"), primary_key=True)
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
        # backref="following"
    )

    following: Mapped[List["User"]] = relationship(
        secondary="table_followers",
        primaryjoin=user_id == Follower.follower_id,
        secondaryjoin=user_id == Follower.user_id
    )

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

    @classmethod
    async def get_user(
            cls,
            user: Union[int, "User"],
            include_relations: str = None,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        statement = select(cls).where(cls.user_id == user)
        if include_relations == "followers":
            statement = statement.options(
                selectinload(cls.followers),
            )
        elif include_relations == "following":
            statement = statement.options(
                selectinload(cls.following),
            )
        elif include_relations == "all":
            statement = statement.options(
                selectinload(cls.followers),
                selectinload(cls.following),
            )

        async with a_session() as session:
            user = await session.scalars(statement)
            return user.one_or_none()

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

        # cath IntegrityError or check presence in the database???

        select_query = select(Follower).where(
            Follower.follower_id == self.user_id,
            Follower.user_id == user_id
        )
        try:
            async with a_session() as session:
                async with session.begin():
                    is_already_follow = await session.scalar(select_query)

                    if is_already_follow:
                        return False
                    else:
                        follower_association = Follower()
                        follower_association.follower_id = self.user_id
                        follower_association.user_id = user_id
                        session.add(follower_association)

                        return True
        except IntegrityError as exc:
            # сделать кастом эксепшн
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

    def __repr__(self):
        return f"User(id={self.user_id}, user_name={self.user_name})"


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id: int = Column(Integer, Sequence("tweet_id"), primary_key=True)
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

    async def add_tweet(
            self,
            tweet_media: list[int],
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            async with session.begin():
                if tweet_media:
                    for media_id in tweet_media:
                        # проверка на существование media в базе !!!!!!!!!!!!!
                        media = await session.get(Media, media_id)
                        self.attachments.append(media)
                    session.add(self)
                else:
                    session.add(self)

    @classmethod
    async def delete_tweet(cls, tweet_id: int, user: int | User,
                           a_session: async_sessionmaker[AsyncSession] = async_session):

        if isinstance(user, User):
            select_query = select(Tweet).where(
                Tweet.tweet_id == tweet_id, Tweet.author == user
            )
        elif isinstance(user, int):
            select_query = select(Tweet).where(
                Tweet.tweet_id == tweet_id, Tweet.author_id == user
            )
        else:
            raise ValueError

        async with a_session() as session:
            async with session.begin():
                tweet_query_result = await session.scalars(select_query)
                tweet = tweet_query_result.one_or_none()
                if tweet:
                    await session.delete(tweet)
                    return True
                else:
                    return False

    @classmethod
    async def tweet_by_id(
            cls,
            tweet_id: int,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):
        async with a_session() as session:
            query_result = await session.execute(
                select(cls, func.count(cls.likes))
                .where(cls.tweet_id == tweet_id)
                .options(
                    joinedload(cls.likes).selectinload(Like.user),
                    joinedload(cls.author),
                    selectinload(cls.attachments)
                ).group_by(cls.tweet_id)
            )
            tweet = query_result.scalars().unique().one_or_none()

        return tweet

    @classmethod
    async def feed(
            cls,
            user: Union[int, "User"],
            a_session: async_sessionmaker[AsyncSession] = async_session,

    ):
        sub_query = select(Follower.user_id).where(Follower.follower_id == user)
        following_query = select(User.user_id).where(User.user_id.in_(sub_query))

        async with a_session() as session:
            tweets = await session.scalars(
                select(
                    cls, func.count(Like.user_id).over(partition_by=cls.tweet_id)
                )
                .where(cls.author_id.in_(following_query))
                .options(
                    joinedload(cls.likes).subqueryload(Like.user),
                    selectinload(cls.author),
                    selectinload(cls.attachments)
                )
                .order_by(
                    func.count(Like.user_id).over(partition_by=cls.tweet_id).desc()
                )
            )
            # ---------------------------------------
            # order by like count

            return tweets.unique().all()
            # ---------------------------------------
            # limits and offsets

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

    @classmethod
    async def add_like(
            cls,
            tweet_id: int,
            user: int | User,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):

        if isinstance(user, User):
            select_query = select(Like).where(
                Like.tweet_id == tweet_id, Like.user == user
            )
            user_id = user.user_id
        elif isinstance(user, int):
            select_query = select(Tweet).where(
                Like.tweet_id == tweet_id, Like.user_id == user
            )
            user_id = user
        else:
            raise ValueError

        async with a_session() as session:
            async with session.begin():
                like_query_result = await session.scalars(select_query)
                like_exists = like_query_result.one_or_none()
                if like_exists:
                    return False
                else:
                    new_like = Like(tweet_id=tweet_id, user_id=user_id)
                    # --------------------------
                    # ловить IntegrityError ????
                    session.add(new_like)
                    return True

    @classmethod
    async def remove_like(
            cls,
            tweet_id,
            user: int | User,
            a_session: async_sessionmaker[AsyncSession] = async_session
    ):

        if isinstance(user, User):
            select_query = select(Like).where(
                Like.tweet_id == tweet_id, Like.user == user
            )
        elif isinstance(user, int):
            select_query = select(Tweet).where(
                Like.tweet_id == tweet_id, Like.user_id == user
            )
        else:
            raise ValueError

        async with a_session() as session:
            async with session.begin():
                like_query_result = await session.scalars(select_query)
                like = like_query_result.one_or_none()
                if like:
                    await session.delete(like)
                    return True
                else:
                    return False


class Media(Base):
    __tablename__ = "table_media"

    media_id: int = Column(Integer, Sequence("media_id"), primary_key=True)
    name: str = Column(String, nullable=False)
    path: str = Column(String, default=MEDIA_PATH.format(user="unknown_user"))

    # -----------------------------------------------
    # оставить только path, там будет path + filename

    @classmethod
    async def add_many(cls,
                       user: int | User,
                       medias: list["Media"],
                       a_session: async_sessionmaker[AsyncSession] = async_session):

        if isinstance(user, int):
            path = MEDIA_PATH.format(user=user)
        elif isinstance(user, User):
            path = MEDIA_PATH.format(user=user.user_id)
        else:
            raise ValueError

        async with a_session() as session:
            async with session.begin():
                pass

    async def add(self,
                  user: int | User,
                  a_session: async_sessionmaker[AsyncSession] = async_session
                  ):
        if isinstance(user, int):
            self.path = MEDIA_PATH.format(user=user)
        elif isinstance(user, User):
            self.path = MEDIA_PATH.format(user=user.user_id)
        else:
            raise ValueError

        async with a_session() as session:
            async with session.begin():
                session.add(self)


class MediaTweetRelation(Base):
    __tablename__ = "table_media_tweet_relation"

    tweet_id: Mapped[int] = Column(ForeignKey("table_tweets.tweet_id"),
                                   primary_key=True)
    media_id: Mapped[int] = Column(ForeignKey("table_media.media_id"), primary_key=True)


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
