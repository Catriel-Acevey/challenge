from datetime import timedelta

import jwt
from fastapi import status

from app.core import security

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


# ─── Token validation tests (covers _credentials_exception fix) ────


def test_expired_token_returns_401(client):
    """An expired JWT should return 401, not 500."""
    expired_token = security.create_access_token(
        data={"sub": "expired@example.com"},
        expires_delta=timedelta(seconds=-1),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]


def test_invalid_token_returns_401(client):
    """A malformed/junk token should return 401, not 500."""
    headers = {"Authorization": "Bearer invalid.token.here"}

    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]


def test_token_with_wrong_secret_returns_401(client):
    """A token signed with a different secret should return 401."""
    payload = {"sub": "hacker@example.com", "exp": 9999999999}
    fake_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {fake_token}"}

    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]


def test_token_without_sub_returns_401(client):
    """A validly-signed JWT missing 'sub' should return 401."""
    token = security.create_access_token(
        data={"no_sub": "value"},
        expires_delta=timedelta(minutes=5),
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]


def test_delete_with_expired_token_returns_401(client):
    """DELETE endpoint should also return 401 on expired token, not 500."""
    expired_token = security.create_access_token(
        data={"sub": "del_expired@example.com"},
        expires_delta=timedelta(seconds=-1),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = client.delete("/api/v1/notifications/1", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_valid_token_on_protected_endpoint_succeeds(client, auth_headers):
    """Sanity: a valid token still works after the other tests."""
    response = client.get("/api/v1/users/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
