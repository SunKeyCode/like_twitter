import pytest
from fastapi.testclient import TestClient

other_users = ["user2", "user3", "user4", "user5"]


# проверить конфигурацию
def test_app_config():
    pass


def test_create_user(test_client: TestClient, main_storage):
    data = {
        "user_name": "test_user"
    }
    response = test_client.post("/api/users", json=data)
    main_storage["main_user_id"] = response.json()["user_id"]
    assert response.status_code == 201


def test_cannot_create_user_with_same_username(test_client: TestClient):
    data = {
        "user_name": "test_user"
    }
    response = test_client.post("/api/users", json=data)
    response_body = response.json()
    assert response.status_code == 400
    assert not response_body["result"]


def test_read_user(test_client: TestClient, main_storage):
    user_id = main_storage["main_user_id"]
    response = test_client.get(f"/api/users/{user_id}")
    user_data = response.json()
    assert response.status_code == 200
    assert user_data["user"]["user_name"] == "test_user"


@pytest.mark.parametrize("user_name", other_users)
def test_create_users_to_follow(test_client: TestClient, main_storage: dict, user_name):
    data = {
        "user_name": user_name
    }
    response = test_client.post("/api/users", json=data)
    if main_storage.get("users_to_follow"):
        main_storage["users_to_follow"].append(response.json()["user_id"])
    else:
        main_storage["users_to_follow"] = [response.json()["user_id"]]
    assert response.status_code == 201


# -------------------------------------------------
# здесь нужно залогиниться под test_user, чтобы продолжить тесты с фоловерами
# -------------------------------------------------

@pytest.mark.parametrize("index", [i for i in range(len(other_users))])
def test_follow_user(test_client: TestClient, main_storage: dict, index):
    users_to_follow = main_storage["users_to_follow"]
    response = test_client.post(f"/api/users/{users_to_follow[index]}/follow")
    assert response.status_code == 200


def test_read_user_with_followers(test_client: TestClient, main_storage):
    user_id = main_storage["main_user_id"]
    response = test_client.get(f"/api/users/{user_id}")
    user_data = response.json()
    user_2_id = 0
    for user in user_data["user"]["following"]:
        if user["user_name"] == "user2":
            user_2_id = user["user_id"]
    main_storage["user_2_id"] = user_2_id
    assert response.status_code == 200
    assert len(user_data["user"]["following"]) == len(other_users)
    assert user_2_id > 0


def test_unfollow_user(test_client: TestClient, main_storage: dict):
    user_2_id = main_storage["user_2_id"]
    response = test_client.delete(f"/api/users/{user_2_id}/follow")
    assert response.status_code == 200


def test_read_user_with_followers_without_user2(test_client: TestClient, main_storage):
    user_id = main_storage["main_user_id"]
    response = test_client.get(f"/api/users/{user_id}")
    user_data = response.json()
    have_user_2 = False
    for user in user_data["user"]["following"]:
        if user["user_name"] == "user2":
            have_user_2 = True

    assert response.status_code == 200
    assert len(user_data["user"]["following"]) == len(other_users) - 1
    assert not have_user_2


# не проходит из-за отсутствия залогиненного пользователя
def test_create_media(test_client: TestClient, main_storage):
    files = {'files': open('file.txt', 'rb')}
    response = test_client.post("/api/medias", files=files)
    response_data: dict = response.json()
    media_id = response_data.get("media_id")
    if media_id:
        main_storage["tweet_media_ids"] = [media_id]
    else:
        main_storage["tweet_media_ids"] = []
    assert response.status_code == 201
    assert media_id is not None
    assert response.json()["result"]


def test_create_tweet(test_client: TestClient, main_storage: dict):
    media_ids = main_storage.get("tweet_media_ids")
    data = {
        "tweet_data": "some text written some user",
        "tweet_media_ids": media_ids
    }
    response = test_client.post("/api/tweets", json=data)
    response_data: dict = response.json()
    tweet_id = response_data.get("tweet_id")
    if tweet_id is None:
        tweet_id = 0
    main_storage["tweet_id"] = tweet_id
    assert response.status_code == 201
    assert tweet_id > 0


def test_like(test_client: TestClient, main_storage: dict):
    tweet_id = main_storage["tweet_id"]
    response = test_client.post(f"/api/tweets/{tweet_id}/likes")
    assert response.status_code == 201
    assert response.json()["result"]


def test_like_twice(test_client: TestClient, main_storage: dict):
    tweet_id = main_storage["tweet_id"]
    response = test_client.post(f"/api/tweets/{tweet_id}/likes")
    assert response.status_code == 400
    assert not response.json()["result"]


def test_delete_like_and_add_again(test_client: TestClient, main_storage: dict):
    tweet_id = main_storage["tweet_id"]
    test_client.delete(f"/api/tweets/{tweet_id}/likes")
    response = test_client.post(f"/api/tweets/{tweet_id}/likes")
    assert response.status_code == 201
    assert response.json()["result"]


def test_delete_tweet(test_client: TestClient, main_storage: dict):
    response = test_client.delete("/api/tweets/<id>")
    assert False


# перелогиниваемся пользователем user3, создаем три твита
def test_crete_tweets_by_user3(test_client: TestClient, main_storage: dict):
    assert False


# перелогиниваемся пользователем user4, создаем три твита, ставим лайки твитам
# user3
def test_crete_tweets_by_user4(test_client: TestClient, main_storage: dict):
    assert False


# перелогиниваемся основным пользователем, ставим лайки твитам user3 и user4
# получаем ленту
def test_feed(test_client: TestClient, main_storage: dict):
    response = test_client.get("/api/tweets")
    assert response.status_code == 200
    # проверяем количество твитов
    # проверяем порядок сортировки по лайкам


def test_delete_not_my_tweet(test_client: TestClient, main_storage: dict):
    assert False
