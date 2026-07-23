from uuid import uuid4

import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import EventFactory


@pytest.fixture()
def second_user_api_client(settings):
    client = EventHubClient(settings.api_base_url)
    email = f"sandbox+{uuid4().hex[:8]}@example.com"
    response = client.register(email, "Test@1234")

    assert response.status_code == 201
    return client


@pytest.mark.api
def test_invalid_bearer_token_is_rejected(settings):
    client = EventHubClient(settings.api_base_url, token="invalid-token")
    response = client.me()
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"] == "Invalid or expired token"


@pytest.mark.api
def test_user_cannot_access_another_users_private_event(
    authenticated_api_client: EventHubClient,
    second_user_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Private Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        response = second_user_api_client.get_event(event_id)
        body = response.json()

        assert response.status_code == 404
        assert body["success"] is False
        assert "not found" in body["error"]
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
def test_user_cannot_delete_another_users_private_event(
    authenticated_api_client: EventHubClient,
    second_user_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Protected Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        response = second_user_api_client.delete_event(event_id)
        body = response.json()

        assert response.status_code == 404
        assert body["success"] is False
        assert "not found" in body["error"]

        owner_response = authenticated_api_client.get_event(event_id)
        assert owner_response.status_code == 200
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
def test_event_data_is_isolated_per_user(
    authenticated_api_client: EventHubClient,
    second_user_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Isolated Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        second_user_events = second_user_api_client.list_events().json()["data"]
        second_user_titles = {item["title"] for item in second_user_events}

        assert event.title not in second_user_titles
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_booking_data_is_isolated_per_user(
    authenticated_api_client: EventHubClient,
    second_user_api_client: EventHubClient,
):
    from eventhub_automation.data.factories import CustomerFactory

    event = EventFactory.workshop(title_prefix="Codex API Private Booking Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.private.booking")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        booking_response = authenticated_api_client.create_booking(event_id, customer)
        booking_body = booking_response.json()
        booking_id = booking_body["data"]["id"]
        booking_reference = booking_body["data"]["bookingRef"]

        second_user_bookings = second_user_api_client.list_bookings().json()["data"]
        second_user_booking_ids = {booking["id"] for booking in second_user_bookings}
        second_user_get_response = second_user_api_client.get_booking(booking_id)
        second_user_ref_response = second_user_api_client.get_booking_by_reference(
            booking_reference
        )

        assert booking_id not in second_user_booking_ids
        assert second_user_get_response.status_code == 403
        assert second_user_ref_response.status_code == 403
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)
