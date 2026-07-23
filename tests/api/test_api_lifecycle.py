import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import CustomerFactory, EventFactory


@pytest.mark.api
def test_get_event_by_valid_static_id(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.get_event(1)
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["id"] == 1
    assert body["data"]["title"] == "World Tech Summit"


@pytest.mark.api
def test_get_event_by_invalid_id_returns_not_found(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.get_event(999999999)
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.api
def test_delete_non_existing_event_returns_not_found(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.delete_event(999999999)
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.api
def test_static_event_cannot_be_deleted(authenticated_api_client: EventHubClient):
    response = authenticated_api_client.delete_event(1)
    body = response.json()

    assert response.status_code == 403
    assert body["success"] is False
    assert body["error"] == "Cannot delete a static event"


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
    assert {"category", "venue", "city", "eventDate", "price", "totalSeats"}.issubset(error_fields)


@pytest.mark.api
def test_event_creation_requires_title(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Missing Title Event")
    payload = authenticated_api_client._event_payload(event)
    payload.pop("title")

    response = authenticated_api_client.create_event_with_payload(payload)
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert "title" in error_fields


@pytest.mark.api
@pytest.mark.xfail(reason="API currently accepts arbitrary event categories")
def test_event_creation_rejects_invalid_category(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Invalid Category Event")
    payload = authenticated_api_client._event_payload(event)
    payload["category"] = "InvalidCategory"
    event_id = 0

    try:
        response = authenticated_api_client.create_event_with_payload(payload)
        body = response.json()
        if response.status_code == 201:
            event_id = body["data"]["id"]

        assert response.status_code == 400
        assert body["success"] is False
        assert "category" in body["error"].lower()
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
def test_event_creation_rejects_negative_price(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Negative Price Event")
    payload = authenticated_api_client._event_payload(event)
    payload["price"] = -1

    response = authenticated_api_client.create_event_with_payload(payload)
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert "price" in error_fields


@pytest.mark.api
def test_event_creation_rejects_zero_seats(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Zero Seats Event")
    payload = authenticated_api_client._event_payload(event)
    payload["totalSeats"] = 0

    response = authenticated_api_client.create_event_with_payload(payload)
    body = response.json()
    error_fields = {detail["field"] for detail in body["details"]}

    assert response.status_code == 400
    assert body["success"] is False
    assert "totalSeats" in error_fields


@pytest.mark.api
def test_event_update_rejects_invalid_payload(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Invalid Update Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        response = authenticated_api_client.session.put(
            f"{authenticated_api_client.base_url}/events/{event_id}",
            json={"title": event.title, "price": -1},
            timeout=15,
        )
        body = response.json()
        error_fields = {detail["field"] for detail in body["details"]}

        assert response.status_code == 400
        assert body["success"] is False
        assert "price" in error_fields
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


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


@pytest.mark.api
@pytest.mark.booking
def test_booking_creation_rejects_invalid_event_id(authenticated_api_client: EventHubClient):
    customer = CustomerFactory.booking_customer(email_prefix="codex.invalid.event")
    response = authenticated_api_client.create_booking(999999999, customer)
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.api
@pytest.mark.booking
def test_booking_creation_rejects_quantity_zero(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Quantity Zero Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.quantity.zero")
    event_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        response = authenticated_api_client.create_booking(event_id, customer, quantity=0)
        body = response.json()
        error_fields = {detail["field"] for detail in body["details"]}

        assert response.status_code == 400
        assert body["success"] is False
        assert "quantity" in error_fields
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_booking_creation_rejects_quantity_greater_than_max(
    authenticated_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Quantity Max Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.quantity.max")
    event_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        response = authenticated_api_client.create_booking(event_id, customer, quantity=11)
        body = response.json()
        error_fields = {detail["field"] for detail in body["details"]}

        assert response.status_code == 400
        assert body["success"] is False
        assert "quantity" in error_fields
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_booking_creation_rejects_invalid_customer_email(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Invalid Customer Email Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.invalid.customer")
    invalid_customer = customer.__class__(customer.full_name, "not-an-email", customer.phone)
    event_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        response = authenticated_api_client.create_booking(event_id, invalid_customer)
        body = response.json()
        error_fields = {detail["field"] for detail in body["details"]}

        assert response.status_code == 400
        assert body["success"] is False
        assert "customerEmail" in error_fields
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_lookup_invalid_booking_reference_returns_not_found(
    authenticated_api_client: EventHubClient,
):
    response = authenticated_api_client.get_booking_by_reference("NO-SUCH-REF")
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert "not found" in body["error"]


@pytest.mark.api
@pytest.mark.booking
def test_cancel_already_cancelled_booking_returns_not_found(
    authenticated_api_client: EventHubClient,
):
    event = EventFactory.workshop(title_prefix="Codex API Double Cancel Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.double.cancel")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        booking_response = authenticated_api_client.create_booking(event_id, customer)
        booking_id = booking_response.json()["data"]["id"]

        first_cancel_response = authenticated_api_client.cancel_booking(booking_id)
        second_cancel_response = authenticated_api_client.cancel_booking(booking_id)
        booking_id = 0
        body = second_cancel_response.json()

        assert first_cancel_response.status_code == 200
        assert second_cancel_response.status_code == 404
        assert body["success"] is False
        assert "not found" in body["error"]
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_get_booking_by_id(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Get Booking Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.get.booking")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        booking_response = authenticated_api_client.create_booking(event_id, customer)
        booking_id = booking_response.json()["data"]["id"]

        get_response = authenticated_api_client.get_booking(booking_id)
        body = get_response.json()

        assert get_response.status_code == 200
        assert body["success"] is True
        assert body["data"]["id"] == booking_id
        assert body["data"]["customerEmail"] == customer.email
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_list_bookings_includes_newly_created_booking(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API List Booking Event")
    customer = CustomerFactory.booking_customer(email_prefix="codex.list.booking")
    event_id = 0
    booking_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        booking_response = authenticated_api_client.create_booking(event_id, customer)
        booking_id = booking_response.json()["data"]["id"]

        list_response = authenticated_api_client.list_bookings()
        booking_ids = {booking["id"] for booking in list_response.json()["data"]}

        assert list_response.status_code == 200
        assert booking_id in booking_ids
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.api
@pytest.mark.booking
def test_user_cannot_book_more_seats_than_available(authenticated_api_client: EventHubClient):
    event = EventFactory.workshop(title_prefix="Codex API Overbook Event")
    event = event.__class__(
        title=event.title,
        description=event.description,
        category=event.category,
        city=event.city,
        venue=event.venue,
        date_time=event.date_time,
        price=event.price,
        total_seats="2",
    )
    customer = CustomerFactory.booking_customer(email_prefix="codex.overbook")
    event_id = 0

    try:
        event_response = authenticated_api_client.create_event(event)
        event_id = event_response.json()["data"]["id"]
        response = authenticated_api_client.create_booking(event_id, customer, quantity=3)
        body = response.json()

        assert response.status_code == 400
        assert body["success"] is False
        assert "available" in body["error"]
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)
