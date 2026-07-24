import pytest

from eventhub_automation.api.assertions import (
    assert_error,
    assert_status,
    parse_data,
    parse_data_list,
)
from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.api.models import ApiEnvelope, EventResource, UserResource
from eventhub_automation.core.config import Settings


@pytest.mark.api
@pytest.mark.contract
def test_health_check_contract(api_client: EventHubClient):
    body = assert_status(api_client.health_check(), 200)

    assert body.keys() >= {"status", "dbStatus", "timestamp"}
    assert isinstance(body["status"], str)
    assert isinstance(body["dbStatus"], str)
    assert isinstance(body["timestamp"], str)


@pytest.mark.api
@pytest.mark.contract
def test_config_contract(api_client: EventHubClient):
    body = assert_status(api_client.config(), 200)

    assert body.keys() >= {"showExploreLinks"}
    assert isinstance(body["showExploreLinks"], bool)
    if "showDashboard" in body:
        assert isinstance(body["showDashboard"], bool)


@pytest.mark.api
@pytest.mark.contract
def test_login_response_contract(api_client: EventHubClient, settings: Settings):
    response = api_client.login(settings.user_email, settings.user_password)
    envelope = ApiEnvelope.model_validate(response.json())
    user = UserResource.model_validate(response.json()["user"])

    assert response.status_code == 200
    assert envelope.success is True
    assert user.email == settings.user_email
    assert isinstance(response.json()["token"], str)
    assert response.json()["token"]


@pytest.mark.api
@pytest.mark.contract
def test_unauthorized_error_contract(api_client: EventHubClient):
    body = assert_error(api_client.me(), 401, "Unauthorized")
    envelope = ApiEnvelope.model_validate(body)

    assert envelope.success is False
    assert envelope.error == "Unauthorized"


@pytest.mark.api
@pytest.mark.contract
def test_events_list_contract(authenticated_api_client: EventHubClient):
    events = parse_data_list(authenticated_api_client.list_events(), EventResource)

    assert events
    assert all(event.id > 0 for event in events)
    assert all(event.title for event in events)


@pytest.mark.api
@pytest.mark.contract
def test_event_detail_contract(authenticated_api_client: EventHubClient):
    event = parse_data(authenticated_api_client.get_event(1), EventResource)

    assert event.id == 1
    assert event.title == "World Tech Summit"
    assert event.available_seats is not None
