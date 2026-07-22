import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import CustomerFactory, EventFactory
from eventhub_automation.pages.bookings_page import BookingsPage
from eventhub_automation.pages.event_detail_page import EventDetailPage
from eventhub_automation.pages.events_page import EventsPage


@pytest.mark.e2e
@pytest.mark.api
def test_api_created_event_appears_in_ui(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
):
    events_page = EventsPage(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)
    event = EventFactory.workshop(title_prefix="Codex Hybrid Event")
    event_id = 0

    try:
        create_response = authenticated_api_client.create_event(event)
        event_id = create_response.json()["data"]["id"]

        events_page.load()
        events_page.search(event.title)
        events_page.assert_event_visible(event.title)
        events_page.open_event(event.title)

        event_detail_page.assert_event_details_visible(event.title, event.category, "$99")
        event_detail_page.assert_description_visible(event.description)
    finally:
        if event_id:
            authenticated_api_client.delete_event(event_id)


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.booking
def test_api_created_booking_appears_in_ui_my_bookings(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
):
    bookings_page = BookingsPage(authenticated_page, settings.base_url)
    event = EventFactory.workshop(title_prefix="Codex Hybrid Booking Event")
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex Hybrid Customer",
        email_prefix="codex.hybrid.customer",
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

        bookings_page.load()
        bookings_page.assert_booking_visible(booking_reference)
        bookings_page.open_booking_details(booking_reference)
        bookings_page.assert_booking_details_visible(
            booking_reference,
            event.title,
            customer.full_name,
            "$198",
        )
    finally:
        if booking_id:
            authenticated_api_client.cancel_booking(booking_id)
        if event_id:
            authenticated_api_client.delete_event(event_id)
