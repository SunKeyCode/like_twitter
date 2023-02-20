from typing import Union, List
from datetime import datetime
import logging
import asyncio
import os

import aiofiles
from sqlalchemy import delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload, subqueryload, aliased, \
    contains_eager
from fastapi import UploadFile

from models import User, Follower, Tweet, Media, Like, MEDIA_PATH
from schemas import CreateUserModel, CreateTweetModelIn
from profiler import profile

logger = logging.getLogger("main.crud")


async def create_user(session: AsyncSession, user_data: CreateUserModel):
    user = User(**user_data.dict())
    async with session.begin():
        session.add(user)

    return user


async def create_tweet(
        session: AsyncSession,
        tweet_data: CreateTweetModelIn,
):
    tweet_as_dict = tweet_data.dict()
    tweet_media_ids = tweet_as_dict.pop("tweet_media_ids")
    tweet = Tweet(**tweet_as_dict)

    async with session.begin():
        if tweet_media_ids:
            for media_id in tweet_media_ids:
                # проверка на существование media в базе !!!!!!!!!!!!!
                media = await session.get(Media, media_id)
                tweet.attachments.append(media)
            session.add(tweet)
        else:
            session.add(tweet)

    return tweet


async def create_like(
        tweet_id: int,
        user_id: int,
        session: AsyncSession
):
    async with session.begin():
        new_like = Like(tweet_id=tweet_id, user_id=user_id)
        session.add(new_like)


async def create_media(
        session: AsyncSession,
        files: List[UploadFile],
        user_id: int
):
    path = MEDIA_PATH.format(user=user_id)

    if not os.path.exists(path):
        os.mkdir(path)
        logger.debug(f"Created path: {path}")

    medias = []

    for file in files:
        timestamp = datetime.timestamp(datetime.now())
        # обработать filename
        # from werkzeug.utils import secure_filename
        # или написать свой вариант
        new_filename = "{:.4f}_{}".format(timestamp, file.filename)

        content = await file.read()
        async with aiofiles.open(
                file="".join(
                    [MEDIA_PATH.format(user=user_id), new_filename]
                ),
                mode="wb"
        ) as file_to_write:
            await file_to_write.write(content)

        media = Media(name=new_filename, path=path)
        medias.append(media)

    async with session.begin():
        session.add_all(medias)

    return medias


async def get_user_test(session: AsyncSession, user_id):
    statement = select(User).where(User.user_id == user_id)
    statement = statement.options(
        selectinload(User.followers),
        selectinload(User.following),
    )

    user = await session.scalars(statement)

    # await asyncio.sleep(0.1)
    return user.one_or_none()


async def read_user(
        session: AsyncSession,
        user_id: int,
        include_relations: str = None,
):
    statement = select(User).where(User.user_id == user_id)
    if include_relations == "followers":
        statement = statement.options(
            selectinload(User.followers),
        )
    elif include_relations == "following":
        statement = statement.options(
            selectinload(User.following),
        )
    elif include_relations == "all":
        statement = statement.options(
            selectinload(User.followers),
            selectinload(User.following),
        )

    user = await session.scalars(statement)
    return user.one_or_none()


@profile
async def read_feed(
        session: AsyncSession,
        user_id: int,

):
    sub_query = select(Follower.user_id).where(Follower.follower_id == user_id)
    following_query = select(User.user_id).where(User.user_id.in_(sub_query))

    aliased_likes = aliased(Like)

    tweets = await session.scalars(
        select(
            Tweet,
            func.count(Tweet.likes.of_type(aliased_likes))
            .over(partition_by=Tweet.tweet_id).label("like_count")
        )
        .where(Tweet.author_id.in_(following_query))
        .outerjoin(Tweet.likes.of_type(aliased_likes))
        .options(
            contains_eager(Tweet.likes.of_type(aliased_likes))
            .joinedload(aliased_likes.user),
            selectinload(Tweet.author),
            selectinload(Tweet.attachments),
        )
        .order_by(
            desc("like_count")
        )
    )

    return tweets.unique().all()
    # ---------------------------------------
    # limits and offsets


async def follow_user(
        session: AsyncSession,
        user_who_follow: Union["User", int],
        user_id: int
):
    if isinstance(user_who_follow, User):
        who_fallow_id = user_who_follow.user_id
    elif isinstance(user_who_follow, int):
        who_fallow_id = user_who_follow
    else:
        raise TypeError

    async with session.begin():
        follower_association = Follower()
        follower_association.follower_id = who_fallow_id
        follower_association.user_id = user_id
        session.add(follower_association)


async def unfollow(
        session: AsyncSession,
        user_who_unfollow: Union["User", int],
        user_id: int
):
    if isinstance(user_who_unfollow, User):
        who_unfollow_id = user_who_unfollow.user_id
    elif isinstance(user_who_unfollow, int):
        who_unfollow_id = user_who_unfollow
    else:
        raise TypeError

    async with session.begin():
        await session.execute(
            delete(Follower)
            .where(Follower.follower_id == who_unfollow_id)
            .where(Follower.user_id == user_id)
        )


async def delete_tweet(
        session: AsyncSession,
        tweet_id: int,
        user_id: int
):
    select_query = select(Tweet).where(
        Tweet.tweet_id == tweet_id, Tweet.author_id == user_id
    )

    async with session.begin():
        tweet_query_result = await session.scalars(select_query)
        tweet = tweet_query_result.one_or_none()
        if tweet:
            await session.delete(tweet)
            return True
        else:
            return False


async def delete_like(
        session: AsyncSession,
        tweet_id: int,
        user_id: int,
) -> None:
    select_query = select(Like).where(
        Like.tweet_id == tweet_id, Like.user_id == user_id
    )
    async with session.begin():
        like_query_result = await session.scalars(select_query)
        like = like_query_result.one_or_none()
        if like:
            await session.delete(like)
