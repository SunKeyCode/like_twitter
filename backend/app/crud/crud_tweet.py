from sqlalchemy import func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased, contains_eager, selectinload

from db_models.follower_model import Follower
from db_models.like_model import Like
from db_models.media_model import Media
from db_models.tweet_model import Tweet
from db_models.user_model import User
from schemas.tweet_schema import CreateTweetModelIn


async def create_tweet(
        session: AsyncSession,
        tweet_data: CreateTweetModelIn,
        author: int | User
):
    tweet_as_dict = tweet_data.dict()
    tweet_media_ids = tweet_as_dict.pop("tweet_media_ids")
    tweet = Tweet(**tweet_as_dict)

    if isinstance(author, int):
        tweet.author_id = author
    elif isinstance(author, User):
        tweet.author_id = author.user_id
    else:
        raise TypeError

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


async def read_feed(
        session: AsyncSession,
        user_id: int,
        limit=0,
        offset=0

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
    await session.commit()
    return tweets.unique().all()
    # ---------------------------------------
    # TODO limits and offsets


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


async def add_like(
        tweet_id: int,
        user_id: int,
        session: AsyncSession
):
    async with session.begin():
        new_like = Like(tweet_id=tweet_id, user_id=user_id)
        session.add(new_like)


async def remove_like(
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
