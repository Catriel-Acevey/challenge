from fastapi import status


AUTH_URL = "/api/v1/auth"


def test_register_returns_user_and_token(client):
    payload = {
        "email": "new_user@example.com",
        "username": "newuser",
        "password": "securepassword123",
    }

    response = client.post(f"{AUTH_URL}/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["username"] == payload["username"]
    assert data["token"]["token_type"] == "bearer"
    assert data["token"]["access_token"]


def test_login_returns_token(client):
    payload = {
        "email": "login_user@example.com",
        "username": "loginuser",
        "password": "securepassword123",
    }
    client.post(f"{AUTH_URL}/register", json=payload)

    response = client.post(
        f"{AUTH_URL}/login",
        data={"username": payload["email"], "password": payload["password"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/v1/users/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED