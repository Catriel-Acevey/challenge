"""Integration tests for notifications CRUD endpoints."""

from fastapi import status

NOTIFICATIONS_URL = "/api/v1/notifications"


# ─── Helpers ───────────────────────────────────────────────────────


def _create_notification(client, auth_headers, **overrides):
    """Helper to create a notification with sensible defaults."""
    payload = {
        "title": "Test Notification",
        "content": "This is a test",
        "channel": "email",
        "recipient": "test@example.com",
    }
    payload.update(overrides)
    return client.post(NOTIFICATIONS_URL, json=payload, headers=auth_headers)


# ─── CREATE ────────────────────────────────────────────────────────


class TestCreateNotification:
    def test_create_email_notification_success(self, client, auth_headers):
        response = _create_notification(client, auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Test Notification"
        assert data["content"] == "This is a test"
        assert data["channel"] == "email"
        assert data["recipient"] == "test@example.com"
        assert data["status"] == "sent"
        assert data["id"] is not None
        assert data["user_id"] is not None

    def test_create_sms_notification_success(self, client, auth_headers):
        response = _create_notification(
            client,
            auth_headers,
            channel="sms",
            recipient="+5491155551234",
            content="Short msg",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["channel"] == "sms"
        assert response.json()["status"] == "sent"

    def test_create_push_notification_success(self, client, auth_headers):
        response = _create_notification(
            client,
            auth_headers,
            channel="push",
            recipient="a" * 20,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["channel"] == "push"
        assert response.json()["status"] == "sent"

    def test_create_notification_invalid_email_returns_400(self, client, auth_headers):
        response = _create_notification(
            client,
            auth_headers,
            recipient="not-an-email",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_notification_no_persistence_on_failure(self, client, auth_headers):
        """When validation fails, no row should be persisted."""
        response = _create_notification(
            client,
            auth_headers,
            recipient="bad-email",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify no notifications exist for this user
        list_response = client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == 0

    def test_create_notification_requires_auth(self, client):
        response = client.post(
            NOTIFICATIONS_URL,
            json={
                "title": "No Auth",
                "content": "Should fail",
                "channel": "email",
                "recipient": "a@b.com",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_notification_missing_fields(self, client, auth_headers):
        response = client.post(
            NOTIFICATIONS_URL,
            json={"title": "Incomplete"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_notification_empty_title(self, client, auth_headers):
        response = client.post(
            NOTIFICATIONS_URL,
            json={
                "title": "",
                "content": "Body",
                "channel": "email",
                "recipient": "a@b.com",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ─── LIST ──────────────────────────────────────────────────────────


class TestListNotifications:
    def test_list_empty(self, client, auth_headers):
        response = client.get(NOTIFICATIONS_URL, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_returns_created_notifications(self, client, auth_headers):
        _create_notification(client, auth_headers)
        _create_notification(
            client,
            auth_headers,
            title="Second",
            channel="sms",
            recipient="+5491155551234",
            content="Hi",
        )

        response = client.get(NOTIFICATIONS_URL, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_only_own_notifications(self, client, auth_headers):
        """User A should not see User B's notifications."""
        _create_notification(client, auth_headers)

        # Register a second user
        payload = {
            "email": "other_user@example.com",
            "username": "otheruser",
            "password": "securepassword123",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        other_token = reg.json()["token"]["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.get(NOTIFICATIONS_URL, headers=other_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


# ─── GET BY ID ─────────────────────────────────────────────────────


class TestGetNotification:
    def test_get_existing_notification(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        response = client.get(f"{NOTIFICATIONS_URL}/{notif_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == notif_id

    def test_get_nonexistent_notification(self, client, auth_headers):
        response = client.get(f"{NOTIFICATIONS_URL}/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_users_notification(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        # Register second user
        payload = {
            "email": "other@example.com",
            "username": "other",
            "password": "securepassword123",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        other_headers = {
            "Authorization": f"Bearer {reg.json()['token']['access_token']}"
        }

        response = client.get(f"{NOTIFICATIONS_URL}/{notif_id}", headers=other_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── UPDATE ────────────────────────────────────────────────────────


class TestUpdateNotification:
    def test_update_title(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        response = client.put(
            f"{NOTIFICATIONS_URL}/{notif_id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Title"
        # Content should remain unchanged
        assert response.json()["content"] == "This is a test"

    def test_update_content(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        response = client.put(
            f"{NOTIFICATIONS_URL}/{notif_id}",
            json={"content": "New content"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["content"] == "New content"

    def test_update_nonexistent_notification(self, client, auth_headers):
        response = client.put(
            f"{NOTIFICATIONS_URL}/99999",
            json={"title": "x"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_users_notification(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        payload = {
            "email": "other2@example.com",
            "username": "other2",
            "password": "securepassword123",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        other_headers = {
            "Authorization": f"Bearer {reg.json()['token']['access_token']}"
        }

        response = client.put(
            f"{NOTIFICATIONS_URL}/{notif_id}",
            json={"title": "Hacked"},
            headers=other_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─── DELETE ────────────────────────────────────────────────────────


class TestDeleteNotification:
    def test_delete_existing_notification(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        response = client.delete(
            f"{NOTIFICATIONS_URL}/{notif_id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        get_response = client.get(
            f"{NOTIFICATIONS_URL}/{notif_id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_notification(self, client, auth_headers):
        response = client.delete(f"{NOTIFICATIONS_URL}/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_users_notification(self, client, auth_headers):
        created = _create_notification(client, auth_headers)
        notif_id = created.json()["id"]

        payload = {
            "email": "other3@example.com",
            "username": "other3",
            "password": "securepassword123",
        }
        reg = client.post("/api/v1/auth/register", json=payload)
        other_headers = {
            "Authorization": f"Bearer {reg.json()['token']['access_token']}"
        }

        response = client.delete(
            f"{NOTIFICATIONS_URL}/{notif_id}", headers=other_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_requires_auth(self, client):
        response = client.delete(f"{NOTIFICATIONS_URL}/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
