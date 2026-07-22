import pytest

from eventhub_automation.data.factories import CustomerFactory
from eventhub_automation.flows.booking_flow import BookingFlow
from eventhub_automation.pages.bookings_page import BookingsPage
from eventhub_automation.pages.event_detail_page import EventDetailPage


@pytest.mark.e2e
@pytest.mark.booking
def test_user_can_book_view_and_cancel_ticket(authenticated_page, settings):
    booking_flow = BookingFlow(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)
    bookings_page = BookingsPage(authenticated_page, settings.base_url)
    booking_reference = ""
    customer = CustomerFactory.booking_customer()

    try:
        booking_reference = booking_flow.book_event_from_listing("World Tech Summit", customer)

        event_detail_page.assert_booking_confirmation(customer.full_name, 1, "$1,500")
        event_detail_page.view_my_bookings()

        bookings_page.assert_booking_visible(booking_reference)
        bookings_page.open_booking_details(booking_reference)
        bookings_page.assert_booking_details_visible(
            booking_reference,
            "World Tech Summit",
            customer.full_name,
            "$1,500",
        )

        bookings_page.load()
        bookings_page.cancel_booking(booking_reference)
        bookings_page.assert_booking_not_visible(booking_reference)
        booking_reference = ""
    finally:
        if booking_reference:
            booking_flow.cancel_booking_if_present(booking_reference)


@pytest.mark.e2e
@pytest.mark.booking
def test_user_can_book_event_from_filtered_discovery(authenticated_page, settings):
    booking_flow = BookingFlow(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)
    bookings_page = BookingsPage(authenticated_page, settings.base_url)
    booking_reference = ""
    customer = CustomerFactory.booking_customer(
        name_prefix="Codex Filtered",
        email_prefix="codex.filtered",
    )

    try:
        booking_reference = booking_flow.book_filtered_city_event(
            "Delhi",
            "Dilli Diwali Mela",
            customer,
            quantity=2,
        )

        event_detail_page.assert_booking_confirmation(customer.full_name, 2, "$600")
        event_detail_page.view_my_bookings()

        bookings_page.assert_booking_visible(booking_reference)
        bookings_page.cancel_booking(booking_reference)
        bookings_page.assert_booking_not_visible(booking_reference)
        booking_reference = ""
    finally:
        if booking_reference:
            booking_flow.cancel_booking_if_present(booking_reference)
