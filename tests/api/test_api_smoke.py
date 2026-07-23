from uuid import uuid4

import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.core.config import Settings


@pytest.mark.api
def test_health_check_returns_database_status(api_client: EventHubClient):
    response = api_client.health_check()
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["dbStatus"] == "connected"


@pytest.mark.api
def test_config_returns_public_feature_flags(api_client: EventHubClient):
    response = api_client.config()
    body = response.json()

    assert response.status_code == 200
    assert "showExploreLinks" in body


@pytest.mark.api
def test_user_can_login_and_fetch_profile(api_client: EventHubClient, settings: Settings):
    login_response = api_client.login(settings.user_email, settings.user_password)
    login_body = login_response.json()

    assert login_response.status_code == 200
    assert login_body["success"] is True
    assert login_body["user"]["email"] == settings.user_email
    assert login_body["token"]

    profile_response = api_client.me()
    profile_body = profile_response.json()

    assert profile_response.status_code == 200
    assert profile_body["success"] is True
    assert profile_body["user"]["email"] == settings.user_email


@pytest.mark.api
def test_invalid_login_is_rejected(api_client: EventHubClient, settings: Settings):
    response = api_client.login(settings.user_email, "WrongPassword@123")
    body = response.json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Invalid email or password"


@pytest.mark.api
def test_auth_me_requires_token(api_client: EventHubClient):
    response = api_client.me()
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"] == "Unauthorized"


@pytest.mark.api
def test_unknown_user_login_is_rejected(api_client: EventHubClient):
    response = api_client.login(f"unknown+{uuid4().hex[:8]}@example.com", "Test@1234")
    body = response.json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Invalid email or password"


@pytest.mark.api
def test_register_rejects_invalid_email(api_client: EventHubClient):
    response = api_client.register("not-an-email", "Test@1234")
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Validation failed"
    assert "email" in error_fields


@pytest.mark.api
def test_register_rejects_weak_password(api_client: EventHubClient):
    response = api_client.register(f"weak+{uuid4().hex[:8]}@example.com", "weak")
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Validation failed"
    assert "password" in error_fields


@pytest.mark.api
def test_user_can_register_and_fetch_profile(api_client: EventHubClient):
    email = f"registered+{uuid4().hex[:8]}@example.com"
    response = api_client.register(email, "Test@1234")
    body = response.json()

    assert response.status_code == 201
    assert body["success"] is True
    assert body["user"]["email"] == email
    assert body["token"]

    profile_response = api_client.me()
    profile_body = profile_response.json()

    assert profile_response.status_code == 200
    assert profile_body["success"] is True
    assert profile_body["user"]["email"] == email


@pytest.mark.api
def test_events_api_lists_static_events(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.list_events()
    body = response.json()
    event_titles = {event["title"] for event in body["data"]}

    assert response.status_code == 200
    assert body["success"] is True
    assert {"Dilli Diwali Mela", "World Tech Summit"}.issubset(event_titles)
