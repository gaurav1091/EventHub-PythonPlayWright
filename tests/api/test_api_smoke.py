from uuid import uuid4

import pytest

from eventhub_automation.api.assertions import (
    assert_error,
    assert_status,
    assert_success,
    assert_validation_error,
    parse_data_list,
)
from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.api.models import EventResource
from eventhub_automation.core.config import Settings


@pytest.mark.api
def test_health_check_returns_database_status(api_client: EventHubClient):
    response = api_client.health_check()
    body = assert_status(response, 200)

    assert body["status"] == "ok"
    assert body["dbStatus"] == "connected"


@pytest.mark.api
def test_config_returns_public_feature_flags(api_client: EventHubClient):
    response = api_client.config()
    body = assert_status(response, 200)

    assert "showExploreLinks" in body


@pytest.mark.api
def test_user_can_login_and_fetch_profile(api_client: EventHubClient, settings: Settings):
    login_response = api_client.login(settings.user_email, settings.user_password)
    login_body = assert_success(login_response)

    assert login_body["user"]["email"] == settings.user_email
    assert login_body["token"]

    profile_response = api_client.me()
    profile_body = assert_success(profile_response)

    assert profile_body["user"]["email"] == settings.user_email


@pytest.mark.api
def test_invalid_login_is_rejected(api_client: EventHubClient, settings: Settings):
    response = api_client.login(settings.user_email, "WrongPassword@123")
    assert_error(response, 400, "Invalid email or password")


@pytest.mark.api
def test_auth_me_requires_token(api_client: EventHubClient):
    response = api_client.me()
    assert_error(response, 401, "Unauthorized")


@pytest.mark.api
def test_unknown_user_login_is_rejected(api_client: EventHubClient):
    response = api_client.login(f"unknown+{uuid4().hex[:8]}@example.com", "Test@1234")
    assert_error(response, 400, "Invalid email or password")


@pytest.mark.api
def test_register_rejects_invalid_email(api_client: EventHubClient):
    response = api_client.register("not-an-email", "Test@1234")
    assert_validation_error(response, {"email"})


@pytest.mark.api
def test_register_rejects_weak_password(api_client: EventHubClient):
    response = api_client.register(f"weak+{uuid4().hex[:8]}@example.com", "weak")
    assert_validation_error(response, {"password"})


@pytest.mark.api
def test_user_can_register_and_fetch_profile(api_client: EventHubClient):
    email = f"registered+{uuid4().hex[:8]}@example.com"
    response = api_client.register(email, "Test@1234")
    body = assert_success(response, 201)

    assert body["user"]["email"] == email
    assert body["token"]

    profile_response = api_client.me()
    profile_body = assert_success(profile_response)

    assert profile_body["user"]["email"] == email


@pytest.mark.api
def test_events_api_lists_static_events(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.list_events()
    events = parse_data_list(response, EventResource)
    event_titles = {event.title for event in events}

    assert {"Dilli Diwali Mela", "World Tech Summit"}.issubset(event_titles)
