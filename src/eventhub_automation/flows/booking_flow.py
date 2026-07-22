from playwright.sync_api import Page

from eventhub_automation.core.logger import get_logger
from eventhub_automation.data.users import BookingCustomer
from eventhub_automation.pages.bookings_page import BookingsPage
from eventhub_automation.pages.event_detail_page import EventDetailPage
from eventhub_automation.pages.events_page import EventsPage

LOGGER = get_logger("flows.booking")


class BookingFlow:
    def __init__(self, page: Page, base_url: str) -> None:
        self.events_page = EventsPage(page, base_url)
        self.event_detail_page = EventDetailPage(page)
        self.bookings_page = BookingsPage(page, base_url)

    def book_event_from_listing(
        self,
        event_name: str,
        customer: BookingCustomer,
        quantity: int = 1,
    ) -> str:
        LOGGER.info("Booking event from listing: event=%s quantity=%s", event_name, quantity)
        self.events_page.load()
        self.events_page.open_event(event_name)
        return self.book_current_event(customer, quantity)

    def book_filtered_city_event(
        self,
        city: str,
        event_name: str,
        customer: BookingCustomer,
        quantity: int = 1,
    ) -> str:
        LOGGER.info(
            "Booking event from filtered discovery: city=%s event=%s quantity=%s",
            city,
            event_name,
            quantity,
        )
        self.events_page.load()
        self.events_page.filter_by_city(city)
        self.events_page.open_event(event_name)
        return self.book_current_event(customer, quantity)

    def book_current_event(self, customer: BookingCustomer, quantity: int = 1) -> str:
        self.event_detail_page.select_ticket_quantity(quantity)
        self.event_detail_page.fill_customer(customer)
        self.event_detail_page.confirm_booking()
        self.event_detail_page.assert_booking_confirmed()
        booking_reference = self.event_detail_page.get_booking_reference()
        LOGGER.info("Created booking %s for %s", booking_reference, customer.full_name)
        return booking_reference

    def cancel_booking_if_present(self, booking_reference: str) -> None:
        self.bookings_page.load()
        if self.bookings_page.booking_exists(booking_reference):
            LOGGER.info("Cleaning up booking %s", booking_reference)
            self.bookings_page.cancel_booking(booking_reference)
