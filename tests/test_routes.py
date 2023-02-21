from fastapi.testclient import TestClient


# def override_get_db():
#     db = async_session()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# app.dependency_overrides[get_db_session] = override_get_db

# client = TestClient(app)


def test_create_user(test_client: TestClient):
    data = {
        "user_name": "test_user"
    }
    response = test_client.post("/api/users", json=data)
    assert response.status_code == 201


def test_cannot_create_user_with_same_username(test_client: TestClient):
    data = {
        "user_name": "test_user"
    }
    response = test_client.post("/api/users", json=data)
    response_body = response.json()
    assert response.status_code == 400
    assert not response_body["result"]


def test_read_user(test_client: TestClient):
    response = test_client.get("/api/users/1")
    assert response.status_code == 200


def test_read_user2(test_client: TestClient):
    response = test_client.get("/api/users/2")
    assert response.status_code == 200
