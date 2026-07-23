import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import CustomerFactory, EventFactory
from eventhub_automation.data.lifecycle import TestDataManager
from eventhub_automation.pages.bookings_page import BookingsPage
from eventhub_automation.pages.event_detail_page import EventDetailPage
from eventhub_automation.pages.events_page import EventsPage


@pytest.mark.e2e
@pytest.mark.api
def test_api_created_event_appears_in_ui(
    authenticated_page,
    settings,
    test_data: TestDataManager,
):
    events_page = EventsPage(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)
    event = EventFactory.workshop(title_prefix="Codex Hybrid Event")

    test_data.create_event(event)

    events_page.load()
    events_page.search(event.title)
    events_page.assert_event_visible(event.title)
    events_page.open_event(event.title)

    event_detail_page.assert_event_details_visible(event.title, event.category, "$99")
    event_detail_page.assert_description_visible(event.description)


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.booking
def test_api_created_booking_appears_in_ui_my_bookings(
    authenticated_page,
    settings,
    test_data: TestDataManager,
):
    bookings_page = BookingsPage(authenticated_page, settings.base_url)
    event = EventFactory.workshop(title_prefix="Codex Hybrid Booking Event")
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex Hybrid Customer",
        email_prefix="codex.hybrid.customer",
    )

    api_event = test_data.create_event(event)
    api_booking = test_data.create_booking(api_event["id"], customer, quantity=2)
    booking_reference = api_booking["bookingRef"]

    bookings_page.load()
    bookings_page.assert_booking_visible(booking_reference)
    bookings_page.open_booking_details(booking_reference)
    bookings_page.assert_booking_details_visible(
        booking_reference,
        event.title,
        customer.full_name,
        "$198",
    )


@pytest.mark.e2e
@pytest.mark.api
def test_ui_created_event_is_visible_in_api(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
    test_data: TestDataManager,
):
    from eventhub_automation.flows.admin_event_flow import AdminEventFlow

    admin_event_flow = AdminEventFlow(authenticated_page, settings.base_url)
    event = EventFactory.workshop(title_prefix="Codex Hybrid UI Event")

    try:
        admin_event_flow.create_event(event, "15 Dec 2026")
        api_event = authenticated_api_client.find_event_by_title(event.title)

        assert api_event is not None
        assert api_event["title"] == event.title
        assert api_event["category"] == event.category
    finally:
        test_data.delete_event_by_title_if_present(event.title)


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.booking
def test_api_cancelled_booking_is_removed_from_ui_my_bookings(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
    test_data: TestDataManager,
):
    bookings_page = BookingsPage(authenticated_page, settings.base_url)
    event = EventFactory.workshop(title_prefix="Codex Hybrid Cancel Booking Event")
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex Hybrid Cancel Customer",
        email_prefix="codex.hybrid.cancel",
    )

    api_event = test_data.create_event(event)
    api_booking = test_data.create_booking(api_event["id"], customer)
    booking_id = api_booking["id"]
    booking_reference = api_booking["bookingRef"]

    bookings_page.load()
    bookings_page.assert_booking_visible(booking_reference)

    cancel_response = authenticated_api_client.cancel_booking(booking_id)

    assert cancel_response.status_code == 200

    bookings_page.load()
    bookings_page.assert_booking_not_visible(booking_reference)


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.booking
def test_api_created_event_can_be_booked_in_ui_and_cleaned_by_api(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
    test_data: TestDataManager,
):
    events_page = EventsPage(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)
    event = EventFactory.workshop(title_prefix="Codex Hybrid UI Booking Event")
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex Hybrid UI Booking Customer",
        email_prefix="codex.hybrid.ui.booking",
    )

    test_data.create_event(event)

    events_page.load()
    events_page.search(event.title)
    events_page.open_event(event.title)
    event_detail_page.fill_customer(customer)
    event_detail_page.confirm_booking()
    booking_reference = event_detail_page.get_booking_reference()

    api_booking_response = authenticated_api_client.get_booking_by_reference(booking_reference)
    api_booking = api_booking_response.json()["data"]
    test_data.track_booking(api_booking["id"])

    assert api_booking["customerName"] == customer.full_name
    assert api_booking["event"]["title"] == event.title
