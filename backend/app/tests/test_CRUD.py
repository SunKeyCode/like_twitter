import random

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db_models.user_model import User
from db_models.tweet_model import Tweet
from schemas.user_schema import CreateUserModel, BriefInfoUserModel
from schemas.tweet_schema import CreateTweetModelIn
from crud import crud_user, crud_tweet, crud_media
from configs import app_config

pytestmark = pytest.mark.asyncio

other_users = ["user2", "user3", "user4", "user5"]


async def test_create_all(create_all):
    await create_all


async def test_create_user(db_session, crud_storage: dict):
    fake_user = CreateUserModel(user_name="test_user", hashed_password="123")
    user = await crud_user.create_user(db_session, fake_user)
    crud_storage["main_user_id"] = user.user_id
    assert user.user_id is not None


async def test_create_user_with_same_username(db_session):
    fake_user = CreateUserModel(user_name="test_user", hashed_password="123")
    with pytest.raises(IntegrityError):
        await crud_user.create_user(db_session, fake_user)


async def test_read_user(db_session, crud_storage):
    stored_user_id = crud_storage["main_user_id"]
    user_from_db: User = await crud_user.read_user(
        session=db_session,
        user_id=stored_user_id,
        include_relations=None
    )
    assert user_from_db.user_name == "test_user"


@pytest.mark.parametrize("user_name", other_users)
async def test_create_users_to_follow(db_session, crud_storage: dict, user_name):
    user_model = CreateUserModel(user_name=user_name, hashed_password="123")
    new_user: User = await crud_user.create_user(db_session, user_model)

    if crud_storage.get("other_users"):
        crud_storage["other_users"].append(BriefInfoUserModel.from_orm(new_user))
    else:
        crud_storage["other_users"] = [BriefInfoUserModel.from_orm(new_user)]

    assert new_user.user_id is not None


async def test_users_count(db_session):
    all_users = await crud_user.read_all(db_session)
    assert len(all_users) == 5


async def test_follow_users(db_session, crud_storage: dict):
    for user in crud_storage["other_users"]:
        await crud_user.follow_user(
            session=db_session,
            user_who_follow=crud_storage["main_user_id"],
            user_id=user.id
        )
        if crud_storage.get("following"):
            crud_storage["following"].append(user)
        else:
            crud_storage["following"] = [user]

    user_from_db: User = await crud_user.read_user(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        include_relations="all"
    )

    assert len(user_from_db.following) == 4


async def test_unfollow_users(db_session, crud_storage: dict):
    for _ in range(2):
        to_unfollow: BriefInfoUserModel = crud_storage["following"].pop()
        await crud_user.unfollow(
            session=db_session,
            user_who_unfollow=crud_storage["main_user_id"],
            user_id=to_unfollow.id
        )

    user_from_db: User = await crud_user.read_user(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        include_relations="all"
    )

    assert len(user_from_db.following) == 2


async def test_create_media(db_session, crud_storage: dict):
    file_name = "test_file.txt"
    crud_storage["file_content"] = "content of file"
    with open(file_name, "w") as file:
        file.write(crud_storage["file_content"])

    file_data = {
        "content": open(file_name, "rb").read(),
        "filename": file_name,
    }

    media = await crud_media.create_media(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        file_data=file_data
    )

    crud_storage["media_id"] = media.media_id

    assert media.media_id is not None


async def test_create_tweet(db_session, crud_storage: dict):
    tweet_data = CreateTweetModelIn.parse_obj(
        {
            "tweet_data": "some text",
            "tweet_media_ids": [crud_storage["media_id"]]
        }
    )
    tweet = await crud_tweet.create_tweet(
        session=db_session,
        tweet_data=tweet_data,
        author=crud_storage["main_user_id"]
    )
    assert tweet.author_id == crud_storage["main_user_id"]


async def test_read_tweet_with_media(db_session, crud_storage: dict):
    tweet = (await crud_tweet.read_tweets(
        session=db_session,
    ))[0]

    with open(
            app_config.MEDIA_ROOT.as_posix() + tweet.attachments[0].link, "r"
    ) as file:
        file_content = file.read()

    assert tweet.author_id == crud_storage["main_user_id"]
    assert tweet.content == "some text"
    assert len(tweet.attachments) == 1
    assert file_content == crud_storage["file_content"]


async def test_add_like(db_session: AsyncSession, crud_storage: dict):
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_before = len(tweet.likes)

    await crud_tweet.add_like(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        tweet_id=tweet.tweet_id
    )

    db_session.expire(tweet)

    tweet_after: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_after = len(tweet_after.likes)

    assert likes_count_after == likes_count_before + 1


async def test_add_like_twice(db_session, crud_storage):
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]

    with pytest.raises(IntegrityError):
        await crud_tweet.add_like(
            session=db_session,
            user_id=crud_storage["main_user_id"],
            tweet_id=tweet.tweet_id
        )


async def test_remove_like(db_session, crud_storage):
    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_before = len(tweet.likes)

    await crud_tweet.remove_like(
        session=db_session,
        tweet_id=tweet.tweet_id,
        user_id=crud_storage["main_user_id"]
    )

    db_session.expire(tweet)

    tweet: Tweet = (await crud_tweet.read_tweets(session=db_session))[0]
    likes_count_after = len(tweet.likes)
    print(likes_count_after)
    assert likes_count_after == likes_count_before - 1


async def test_delete_tweet(db_session, crud_storage: dict):
    tweets = await crud_tweet.read_tweets(session=db_session)
    tweets_count_before = len(tweets)
    tweet_id = tweets[0].tweet_id

    await crud_tweet.delete_tweet(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        tweet_id=tweet_id
    )

    tweets_count_after = len(await crud_tweet.read_tweets(session=db_session))

    assert tweets_count_before == tweets_count_after + 1


async def test_create_tweets_by_other_users(db_session, crud_storage: dict):
    tweet_counts = 2
    total_tweets = 0
    for user in crud_storage["following"]:
        for i in range(tweet_counts):
            tweet_data = CreateTweetModelIn.parse_obj(
                {"tweet_data": f"tweet_{i + 1} of {user.name}"}
            )

            tweet = await crud_tweet.create_tweet(
                session=db_session,
                tweet_data=tweet_data,
                author=user.id
            )

            if crud_storage.get("tweets_for_feed"):
                crud_storage["tweets_for_feed"].append(tweet.tweet_id)
            else:
                crud_storage["tweets_for_feed"] = [tweet.tweet_id]

            total_tweets += 1

    tweets = await crud_tweet.read_tweets(session=db_session)

    assert len(tweets) == total_tweets


async def test_have_tweets_in_feed(
        db_session: AsyncSession, crud_storage: dict
):
    feed = await crud_tweet.read_feed(
        session=db_session,
        user_id=crud_storage["main_user_id"]
    )

    assert len(feed) == len(crud_storage["tweets_for_feed"])
    for tweet in feed:
        assert tweet.tweet_id in crud_storage["tweets_for_feed"]


async def test_feed_sorting(db_session: AsyncSession, crud_storage: dict):
    tweets_for_feed: list[int] = crud_storage["tweets_for_feed"][:]
    users: list[BriefInfoUserModel] = crud_storage["other_users"][:]
    sorted_tweet_id_list = []

    while tweets_for_feed and users:
        tweet_id = tweets_for_feed.pop()
        for user in users:
            await crud_tweet.add_like(
                session=db_session,
                tweet_id=tweet_id,
                user_id=user.id
            )
        sorted_tweet_id_list.append(tweet_id)
        users.pop()

    feed = await crud_tweet.read_feed(
        session=db_session,
        user_id=crud_storage["main_user_id"]
    )
    tweet_id_list_from_feed = [tweet.tweet_id for tweet in feed]

    assert tweet_id_list_from_feed == sorted_tweet_id_list


async def test_delete_tweet_that_does_not_belong_to_user(
        db_session: AsyncSession, crud_storage: dict
):
    tweet_id = random.choice(crud_storage["tweets_for_feed"])
    result: bool = await crud_tweet.delete_tweet(
        session=db_session,
        user_id=crud_storage["main_user_id"],
        tweet_id=tweet_id
    )

    assert not result
