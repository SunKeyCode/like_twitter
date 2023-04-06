from random import choice
from operator import itemgetter

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.asyncio

other_users = ["user2", "user3", "user4", "user5"]
headers = {}


async def test_create_all(create_all):
    """Creates database and initiates tables"""
    await create_all.__anext__()
    # await create_all


def test_create_user(test_client: TestClient, storage):
    """Create main user"""
    data = {
        "user_name": "test_user",
        "hashed_password": 123,
    }

    response = test_client.post("/api/users", json=data)

    storage["main_user_id"] = response.json()["user_id"]

    assert response.status_code == 201


def test_cannot_create_user_with_same_username(test_client: TestClient):
    """Checks that we can not create user with same username"""
    data = {
        "user_name": "test_user",
        "hashed_password": 123,
    }
    response = test_client.post("/api/users", json=data)
    response_body = response.json()

    assert response.status_code == 400
    assert not response_body["result"]


def test_read_user(test_client: TestClient, storage):
    """Checks created user"""
    user_id = storage["main_user_id"]
    response = test_client.get(f"/api/users/{user_id}")
    user_data = response.json()

    assert response.status_code == 200
    assert user_data["user"]["name"] == "test_user"


@pytest.mark.parametrize("user_name", other_users)
def test_create_users_to_follow(test_client: TestClient, storage: dict, user_name):
    """Creates 4 users to follow them in the next test"""
    data = {
        "user_name": user_name,
        "hashed_password": 1,
    }
    # create other users
    response = test_client.post("/api/users", json=data)

    user = {
        "username": user_name,
        "id": response.json()["user_id"]
    }
    if storage.get("users_to_follow"):
        storage["users_to_follow"].append(user)
    else:
        storage["users_to_follow"] = [user]

    assert response.status_code == 201


@pytest.mark.parametrize("index", [i for i in range(len(other_users))])
def test_follow_user(test_client: TestClient, storage: dict, index):
    users_to_follow = storage["users_to_follow"]
    # authenticate user
    headers = {
        "api-key": str(storage["main_user_id"])
    }

    response = test_client.post(
        f"/api/users/{users_to_follow[index]['id']}/follow",
        headers=headers,
    )
    assert response.status_code == 200


def test_read_user_with_followers(test_client: TestClient, storage):
    """
    Checks that main user follows all users of other_user list. Saves user2 in
    storage to check unfollowing in the next test.
    """
    user_id = storage["main_user_id"]
    response = test_client.get(f"/api/users/{user_id}")
    user_data = response.json()
    user_2_id = 0
    for user in user_data["user"]["following"]:
        if user["name"] == "user2":
            user_2_id = user["id"]
            break
    storage["user_2_id"] = user_2_id
    assert response.status_code == 200
    assert len(user_data["user"]["following"]) == len(other_users)
    assert user_2_id > 0


def test_unfollow_user(test_client: TestClient, storage: dict):
    """Unfollow user2"""

    # authenticate user
    headers = {
        "api-key": str(storage["main_user_id"])
    }

    user_2_id = storage["user_2_id"]

    response = test_client.delete(
        f"/api/users/{user_2_id}/follow",
        headers=headers,
    )
    assert response.status_code == 200


def test_read_user_with_followers_without_user2(test_client: TestClient, storage):
    """Checks that user2 not in following list of main user"""

    user_id = storage["main_user_id"]

    headers = {
        "api-key": str(storage["main_user_id"])
    }

    response = test_client.get(
        f"/api/users/{user_id}",
        headers=headers,
    )
    user_data = response.json()

    user_2_in_following_list = False

    for user in user_data["user"]["following"]:
        if user["name"] == "user2":
            user_2_in_following_list = True
            break

    assert response.status_code == 200
    assert len(user_data["user"]["following"]) == len(other_users) - 1
    assert not user_2_in_following_list


def test_create_media(test_client: TestClient, storage):
    """Checks file uploading"""
    headers = {
        "api-key": str(storage["main_user_id"])
    }

    with open("for_tests.txt", "w") as file:
        file.write("content of file")

    file = {'file': open("for_tests.txt", "rb")}

    response = test_client.post(
        "/api/medias",
        files=file,
        headers=headers
    )

    response_data: dict = response.json()

    media_id = response_data.get("media_id")
    if media_id:
        storage["tweet_media_ids"] = [media_id]
    else:
        storage["tweet_media_ids"] = []
    assert response.status_code == 201
    assert media_id is not None
    assert response.json()["result"]


def test_create_tweet(test_client: TestClient, storage: dict):
    """Creates tweet with attached file"""
    media_ids = storage.get("tweet_media_ids")
    data = {
        "tweet_data": "some text written some user",
        "tweet_media_ids": media_ids
    }
    headers = {
        "api-key": str(storage["main_user_id"])
    }
    response = test_client.post(
        "/api/tweets", json=data,
        headers=headers
    )

    response_data: dict = response.json()
    tweet_id = response_data.get("tweet_id")
    if tweet_id is None:
        tweet_id = 0
    storage["tweet_id"] = tweet_id
    assert response.status_code == 201
    assert tweet_id > 0


def test_like(test_client: TestClient, storage: dict):
    """Likes tweet"""
    tweet_id = storage["tweet_id"]
    headers["api-key"] = str(storage["main_user_id"])
    response = test_client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["result"]


def test_like_twice(test_client: TestClient, storage: dict):
    tweet_id = storage["tweet_id"]
    headers["api-key"] = str(storage["main_user_id"])
    response = test_client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers=headers
    )
    assert response.status_code == 400
    assert not response.json()["result"]


def test_delete_like_and_add_again(test_client: TestClient, storage: dict):
    tweet_id = storage["tweet_id"]
    headers["api-key"] = str(storage["main_user_id"])
    test_client.delete(f"/api/tweets/{tweet_id}/likes", headers=headers)
    response = test_client.post(f"/api/tweets/{tweet_id}/likes", headers=headers)

    assert response.status_code == 201
    assert response.json()["result"]


def test_delete_tweet(test_client: TestClient, storage: dict):
    headers["api-key"] = str(storage["main_user_id"])
    tweet_id = storage["tweet_id"]
    response = test_client.delete(f"/api/tweets/{tweet_id}", headers=headers)
    assert response.status_code == 202


def test_crete_tweets_by_user3(test_client: TestClient, storage: dict):
    """User3 creates 2 tweets"""
    user_id = None
    for user in storage["users_to_follow"]:
        if user["username"] == "user3":
            user_id = user["id"]
            break

    headers["api-key"] = str(user_id)
    tweets = []
    for i in range(2):
        data = {
            "tweet_data": f"tweet_{i + 1} of user3",
        }
        response = test_client.post(
            "/api/tweets", json=data,
            headers=headers
        )
        response_data = response.json()
        tweet_id = response_data.get("tweet_id")

        assert tweet_id is not None

        tweet = {
            "tweet_id": tweet_id,
            "likes": 0,
        }
        tweets.append(tweet)

    storage["other_tweets"] = tweets

    assert len(tweets) == 2


def test_crete_tweets_by_user4(test_client: TestClient, storage: dict):
    """User4 creates 2 tweets and likes one tweet of user3 to check
    sort ordering in the next test"""
    user_id = None
    for user in storage["users_to_follow"]:
        if user["username"] == "user4":
            user_id = user["id"]
            break

    headers["api-key"] = str(user_id)
    tweets = []
    for i in range(2):
        data = {
            "tweet_data": f"tweet_{i + 1} of user4",
        }
        response = test_client.post(
            "/api/tweets", json=data,
            headers=headers
        )
        response_data = response.json()
        tweet_id = response_data.get("tweet_id")

        assert tweet_id is not None

        tweet = {
            "tweet_id": tweet_id,
            "likes": 0,
        }
        tweets.append(tweet)

    # add like to last tweet
    for tweet in storage["other_tweets"][1:0:-1]:
        response = test_client.post(
            f"/api/tweets/{tweet['tweet_id']}/likes",
            headers=headers
        )
        assert response.status_code == 201
        tweet["likes"] += 1

    storage["other_tweets"].extend(tweets)

    assert len(tweets) == 2


def test_feed(test_client: TestClient, storage: dict):
    """Get feed of main user, checks sorting order and tweet's count"""
    headers["api-key"] = str(storage["main_user_id"])

    # add likes for all other tweets except first
    for tweet in storage["other_tweets"][:0:-1]:
        response = test_client.post(
            f"/api/tweets/{tweet['tweet_id']}/likes",
            headers=headers
        )
        assert response.status_code == 201
        tweet["likes"] += 1

    # sort tweets in storage by likes and tweet_id
    sorted_storage_tweet_list = sorted(
        storage["other_tweets"],
        key=itemgetter("likes", "tweet_id"),
        reverse=True,
    )

    response = test_client.get("/api/tweets", headers=headers)
    response_data = response.json()
    response_tweet_list = [tweet["id"] for tweet in response_data["tweets"]]

    assert response.status_code == 200
    assert len(response_data["tweets"]) == len(storage["other_tweets"])
    assert response_tweet_list == [
        tweet["tweet_id"] for tweet in sorted_storage_tweet_list
    ]


def test_delete_not_my_tweet(test_client: TestClient, storage: dict):
    headers["api-key"] = str(storage["main_user_id"])
    tweet = choice(storage["other_tweets"])
    response = test_client.delete(f"/api/tweets/{tweet['tweet_id']}", headers=headers)
    assert response.status_code == 400
