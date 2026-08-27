# tests/test_users.py
import pytest
from fastapi import status

BASE_URL = "/api/v1/users"


# --- FIXTURES ---

@pytest.fixture
def sample_user(client, auth_headers):
    """Fixture that creates a standard user via API before running a test."""
    payload = {
        "email": "sample_user@example.com",
        "username": "sampleuser",
        "password": "securepassword123",
    }
    response = client.post(BASE_URL, json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


# --- CONNECTION & CREATION TESTS ---

def test_setup_conexion(client):
    """Basic test to validate that the client and API respond."""
    response = client.get(BASE_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user_success(client, auth_headers):
    # 1. ARRANGE
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "securepassword123",
    }

    # 2. ACT
    response = client.post(BASE_URL, json=payload, headers=auth_headers)

    # 3. ASSERT
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "password" not in data


def test_create_user_duplicate_email(client, auth_headers):
    # 1. ARRANGE: Create initial user
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "securepassword123",
    }
    response_first = client.post(BASE_URL, json=payload, headers=auth_headers)
    assert response_first.status_code == status.HTTP_201_CREATED

    # 2. ACT: Attempt to create another user with the same email
    payload_duplicate_email = {
        "email": "testuser@example.com",
        "username": "different_username",
        "password": "anotherpassword123",
    }
    response_duplicate = client.post(
        BASE_URL, json=payload_duplicate_email, headers=auth_headers
    )

    # 3. ASSERT: Verify bad request response
    assert response_duplicate.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response_duplicate.json()["detail"].lower()


# --- GET USERS TESTS ---

def test_get_users_success(client, sample_user, auth_headers):
    # 1. ACT: Retrieve all users
    response = client.get(BASE_URL, headers=auth_headers)

    # 2. ASSERT: Verify list contains at least the sample user
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user_by_id_success(client, sample_user, auth_headers):
    # 1. ACT: Fetch user by ID using the fixture data
    user_id = sample_user["id"]
    response = client.get(f"{BASE_URL}/{user_id}", headers=auth_headers)

    # 2. ASSERT: Verify status and retrieved data
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == sample_user["email"]


def test_get_user_by_id_not_found(client, auth_headers):
    # 1. ACT: Attempt to fetch a non-existent user ID
    non_existent_id = 99999
    response = client.get(f"{BASE_URL}/{non_existent_id}", headers=auth_headers)

    # 2. ASSERT: Verify 404 status code
    assert response.status_code == status.HTTP_404_NOT_FOUND


# --- UPDATE USER TESTS ---

def test_update_user_success(client, sample_user, auth_headers):
    # 1. ARRANGE: Prepare update payload
    user_id = sample_user["id"]
    update_payload = {
        "email": "updated_user@example.com",
        "username": "updateduser",
        "pokemon_team": [1, 4],
    }

    # 2. ACT: Update the user's data
    response = client.put(
        f"{BASE_URL}/{user_id}", json=update_payload, headers=auth_headers
    )

    # 3. ASSERT: Check updated values
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == update_payload["email"]
    assert data["username"] == update_payload["username"]
    assert data["pokemon_team"] == ["bulbasaur", "charmander"]


def test_update_user_not_found(client, auth_headers):
    # 1. ACT: Attempt to update a non-existent user ID
    non_existent_id = 99999
    update_payload = {
        "email": "nobody@example.com",
        "username": "nobody",
        "pokemon_team": [],
    }
    response = client.put(
        f"{BASE_URL}/{non_existent_id}",
        json=update_payload,
        headers=auth_headers,
    )

    # 2. ASSERT: Verify 404 status code
    assert response.status_code == status.HTTP_404_NOT_FOUND


# --- DELETE USER TESTS ---

def test_delete_user_success(client, sample_user, auth_headers):
    # 1. ACT: Delete the user created by the fixture
    user_id = sample_user["id"]
    response = client.delete(f"{BASE_URL}/{user_id}", headers=auth_headers)

    # 2. ASSERT: Verify 204 status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Double check that fetching the user now returns 404
    get_res = client.get(f"{BASE_URL}/{user_id}", headers=auth_headers)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_not_found(client, auth_headers):
    # 1. ACT: Attempt to delete a non-existent user ID
    non_existent_id = 99999
    response = client.delete(
        f"{BASE_URL}/{non_existent_id}", headers=auth_headers
    )

    # 2. ASSERT: Verify 404 status code
    assert response.status_code == status.HTTP_404_NOT_FOUND