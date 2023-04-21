import random

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from configs import app_config
from crud import crud_media, crud_tweet, crud_user
from db_models.tweet_model import Tweet
from db_models.user_model import User
from schemas.tweet_schema import CreateTweetModelIn
from schemas.user_schema import BriefInfoUserModel, CreateUserModel

pytestmark = pytest.mark.asyncio

other_users = ["user2", "user3", "user4", "user5"]


async def test_create_all(create_all) -> None:
    await create_all.__anext__()


async def test_create_user(db_session, storage) -> None:
    fake_user = CreateUserModel(user_name="test_user", password="123")
    user = await crud_user.create_user(db_session, fake_user)
    storage["main_user_id"] = user.user_id
    assert user.user_id is not None


async def test_create_user_with_same_username(db_session) -> None:
    fake_user = CreateUserModel(user_name="test_user", password="123")
    with pytest.raises(IntegrityError):
        await crud_user.create_user(db_session, fake_user)


async def test_read_user(db_session, storage) -> None:
    stored_user_id = storage["main_user_id"]
    user_from_db: User | None = await crud_user.read_user(
        session=db_session, user_id=stored_user_id, include_relations=None
    )
    if user_from_db is None:
        raise AssertionError

    assert user_from_db.user_name == "test_user"


@pytest.mark.parametrize("user_name", other_users)
async def test_create_users_to_follow(db_session, storage, user_name) -> None:
    user_model = CreateUserModel(user_name=user_name, password="123")
    new_user: User = await crud_user.create_user(db_session, user_model)

    if storage.get("other_users"):
        storage["other_users"].append(BriefInfoUserModel.from_orm(new_user))
    else:
        storage["other_users"] = [BriefInfoUserModel.from_orm(new_user)]

    assert new_user.user_id is not None


async def test_users_count(db_session) -> None:
    all_users = await crud_user.read_all(db_session)
    assert len(all_users) == 5


async def test_follow_users(db_session, storage) -> None:
    for user in storage["other_users"]:
        await crud_user.follow_user(
            session=db_session, user_who_follow=storage["main_user_id"], user_id=user.id
        )
        if storage.get("following"):
            storage["following"].append(user)
        else:
            storage["following"] = [user]

    user_from_db: User | None = await crud_user.read_user(
        session=db_session, user_id=storage["main_user_id"], include_relations="all"
    )

    if user_from_db is None:
        raise AssertionError

    assert len(user_from_db.following) == 4


async def test_unfollow_users(db_session, storage) -> None:
    for _ in range(2):
        to_unfollow: BriefInfoUserModel = storage["following"].pop()
        await crud_user.unfollow(
            session=db_session,
            user_who_unfollow=storage["main_user_id"],
            user_id=to_unfollow.id,
        )

    user_from_db: User | None = await crud_user.read_user(
        session=db_session, user_id=storage["main_user_id"], include_relations="all"
    )

    if user_from_db is None:
        raise AssertionError

    assert len(user_from_db.following) == 2


async def test_create_media(db_session, storage) -> None:
    file_name = "test_file.txt"
    storage["file_content"] = "content of file"
    with open(file_name, "w") as file:
        file.write(storage["file_content"])

    file_data = {
        "content": open(file_name, "rb").read(),
        "filename": file_name,
    }

    media = await crud_media.create_media(
        session=db_session, user_id=storage["main_user_id"], file_data=file_data
    )

    storage["media_id"] = media.media_id

    assert media.media_id is not None


async def test_create_tweet(db_session, storage) -> None:
    tweet_data = CreateTweetModelIn.parse_obj(
        {"tweet_data": "some text", "tweet_media_ids": [storage["media_id"]]}
    )
    tweet = await crud_tweet.create_tweet(
        session=db_session, tweet_data=tweet_data, author=storage["main_user_id"]
    )
    assert tweet.author_id == storage["main_user_id"]


async def test_read_tweet_with_media(db_session, storage) -> None:
    tweet = (
        await crud_tweet.read_tweets(
            session=db_session,
        )
    )[0]

    with open(app_config.MEDIA_ROOT / tweet.attachments[0].link, "r") as file:
        file_content = file.read()

    assert tweet.author_id == storage["main_user_id"]
    assert tweet.content == "some text"
    assert len(tweet.attachments) == 1
    assert file_content == storage["file_content"]


async def test_add_like(db_session: AsyncSession, storage) -> None:
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_before = len(tweet.likes)

    await crud_tweet.add_like(
        session=db_session, user_id=storage["main_user_id"], tweet_id=tweet.tweet_id
    )

    db_session.expire(tweet)

    tweet_after: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_after = len(tweet_after.likes)

    assert likes_count_after == likes_count_before + 1


async def test_add_like_twice(db_session, storage) -> None:
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]

    with pytest.raises(IntegrityError):
        await crud_tweet.add_like(
            session=db_session, user_id=storage["main_user_id"], tweet_id=tweet.tweet_id
        )


async def test_remove_like(db_session, storage) -> None:
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_before = len(tweet.likes)

    await crud_tweet.remove_like(
        session=db_session, tweet_id=tweet.tweet_id, user_id=storage["main_user_id"]
    )

    db_session.expire(tweet)

    tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_after = len(tweet.likes)
    print(likes_count_after)
    assert likes_count_after == likes_count_before - 1


async def test_delete_tweet(db_session, storage) -> None:
    tweets = await crud_tweet.read_tweets(session=db_session)
    tweets_count_before = len(tweets)
    tweet_id = tweets[0].tweet_id

    await crud_tweet.delete_tweet(
        session=db_session, user_id=storage["main_user_id"], tweet_id=tweet_id
    )

    tweets_count_after = len(await crud_tweet.read_tweets(session=db_session))

    assert tweets_count_before == tweets_count_after + 1


async def test_create_tweets_by_other_users(db_session, storage) -> None:
    tweet_counts = 2
    total_tweets = 0
    for user in storage["following"]:
        for i in range(tweet_counts):
            tweet_data = CreateTweetModelIn.parse_obj(
                {"tweet_data": f"tweet_{i + 1} of {user.name}"}
            )

            tweet = await crud_tweet.create_tweet(
                session=db_session, tweet_data=tweet_data, author=user.id
            )

            if storage.get("tweets_for_feed"):
                storage["tweets_for_feed"].append(tweet.tweet_id)
            else:
                storage["tweets_for_feed"] = [tweet.tweet_id]

            total_tweets += 1

    tweets = await crud_tweet.read_tweets(session=db_session)

    assert len(tweets) == total_tweets


async def test_have_tweets_in_feed(db_session: AsyncSession, storage) -> None:
    feed = await crud_tweet.read_feed(
        session=db_session, user_id=storage["main_user_id"]
    )

    assert len(feed) == len(storage["tweets_for_feed"])
    for tweet in feed:
        assert tweet.tweet_id in storage["tweets_for_feed"]


async def test_feed_sorting(db_session: AsyncSession, storage) -> None:
    tweets_for_feed: list[int] = storage["tweets_for_feed"][:]
    users: list[BriefInfoUserModel] = storage["other_users"][:]
    sorted_tweet_id_list = []

    while tweets_for_feed and users:
        tweet_id = tweets_for_feed.pop()
        for user in users:
            await crud_tweet.add_like(
                session=db_session, tweet_id=tweet_id, user_id=user.id
            )
        sorted_tweet_id_list.append(tweet_id)
        users.pop()

    feed = await crud_tweet.read_feed(
        session=db_session, user_id=storage["main_user_id"]
    )
    tweet_id_list_from_feed = [tweet.tweet_id for tweet in feed]

    assert tweet_id_list_from_feed == sorted_tweet_id_list


async def test_delete_tweet_that_does_not_belong_to_user(
    db_session: AsyncSession, storage
) -> None:
    tweet_id = random.choice(storage["tweets_for_feed"])
    result: bool = await crud_tweet.delete_tweet(
        session=db_session, user_id=storage["main_user_id"], tweet_id=tweet_id
    )

    assert not result
