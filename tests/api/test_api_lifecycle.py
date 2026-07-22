import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import CustomerFactory, EventFactory


@pytest.mark.api
def test_events_api_can_create_update_get_and_delete_event(
    authenticated_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Event")
    updated_event = EventFactory.workshop(title_prefix=event.title)
    updated_event = updated_event.__class__(
        title=event.title,
        description="Updated by API lifecycle test.",
        category=event.category,
        city="Bangalore",
        venue="Updated API Lab",
        date_time=event.date_time,
        price="199",
        total_seats=event.total_seats,
    )
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        create_body = create_response.json()
        event_id = create_body["data"]["id"]

        assert create_response.status_code == 201
        assert create_body["success"] is True
        assert create_body["data"]["title"] == event.title

        update_response = authenticated_api_client.update_event(event_id, updated_event)
        update_body = update_response.json()

        assert update_response.status_code == 200
        assert update_body["success"] is True
        assert update_body["data"]["city"] == "Bangalore"
        assert update_body["data"]["price"] == "199"

        get_response = authenticated_api_client.get_event(event_id)
        get_body = get_response.json()

        assert get_response.status_code == 200
        assert get_body["success"] is True
        assert get_body["data"]["description"] == "Updated by API lifecycle test."
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)

    get_deleted_response = authenticated_api_client.get_event(event_id)
    assert get_deleted_response.status_code == 404


@pytest.mark.api
def test_created_event_appears_in_list_and_disappears_after_delete(
    authenticated_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Listed Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        list_response = authenticated_api_client.list_events()
        listed_titles = {item["title"] for item in list_response.json()["data"]}

        assert create_response.status_code == 201
        assert event.title in listed_titles

        delete_response = authenticated_api_client.delete_event(event_id)
        event_id = 0

        assert delete_response.status_code == 200

        list_after_delete_response = authenticated_api_client.list_events()
        titles_after_delete = {item["title"] for item in list_after_delete_response.json()["data"]}

        assert event.title not in titles_after_delete
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
def test_invalid_event_creation_returns_validation_error(
    authenticated_api_client: EventHubClient,
):
    response = authenticated_api_client.create_event_with_payload({"title": "Invalid API Event"})
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Validation failed"
    assert {"category", "venue", "city", "eventDate", "price", "totalSeats"}.issubset(
        error_fields
    )


@pytest.mark.api
@pytest.mark.booking
def test_bookings_api_can_create_lookup_and_cancel_booking(
    authenticated_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Booking Event")
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex API Customer",
        email_prefix="codex.api.customer",
    )
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]

        booking_response = authenticated_api_client.create_booking(event_id, customer, quantity=2)
        booking_body = booking_response.json()
        booking_id = booking_body["data"]["id"]
        booking_reference = booking_body["data"]["bookingRef"]

        assert booking_response.status_code == 201
        assert booking_body["success"] is True
        assert booking_body["data"]["quantity"] == 2
        assert booking_body["data"]["totalPrice"] == "198"
        assert booking_body["data"]["customerName"] == customer.full_name

        lookup_response = authenticated_api_client.get_booking_by_reference(booking_reference)
        lookup_body = lookup_response.json()

        assert lookup_response.status_code == 200
        assert lookup_body["success"] is True
        assert lookup_body["data"]["id"] == booking_id

        cancel_response = authenticated_api_client.cancel_booking(booking_id)
        cancel_body = cancel_response.json()
        booking_id = 0

        assert cancel_response.status_code == 200
        assert cancel_body["success"] is True
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_booking_decrements_available_seats(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Seat Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.api.seat")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]

        booking_response = authenticated_api_client.create_booking(event_id, customer, quantity=3)
        booking_id = booking_response.json()["data"]["id"]

        event_after_booking_response = authenticated_api_client.get_event(event_id)
        event_after_booking = event_after_booking_response.json()["data"]

        assert booking_response.status_code == 201
        assert event_after_booking["availableSeats"] == 22
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_cancelling_booking_releases_available_seats(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Cancel Seat Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.api.cancel")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        booking_response = authenticated_api_client.create_booking(event_id, customer, quantity=4)
        booking_id = booking_response.json()["data"]["id"]

        cancel_response = authenticated_api_client.cancel_booking(booking_id)
        booking_id = 0

        event_after_cancel_response = authenticated_api_client.get_event(event_id)
        event_after_cancel = event_after_cancel_response.json()["data"]

        assert booking_response.status_code == 201
        assert cancel_response.status_code == 200
        assert event_after_cancel["availableSeats"] == 25
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)
