from playwright.sync_api import Page, expect

from eventhub_automation.components.confirm_dialog import ConfirmDialog
from eventhub_automation.core.base_page import BasePage


class BookingsPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.confirm_dialog = ConfirmDialog(page)
        self.clear_all_button = page.get_by_role("button", name="Clear all bookings")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/bookings")

    def assert_booking_visible(self, booking_reference: str) -> None:
        expect(self.page.get_by_text(booking_reference, exact=True)).to_be_visible()

    def assert_booking_not_visible(self, booking_reference: str) -> None:
        expect(self.page.get_by_text(booking_reference, exact=True)).not_to_be_visible()

    def assert_booking_details_visible(
        self,
        booking_reference: str,
        event_name: str,
        customer_name: str,
        total: str,
    ) -> None:
        expect(self.page.get_by_text(booking_reference)).to_be_visible()
        expect(self.page.get_by_role("heading", name=event_name)).to_be_visible()
        expect(self.page.get_by_text(customer_name)).to_be_visible()
        expect(self.page.get_by_text(total).last).to_be_visible()

    def open_booking_details(self, booking_reference: str) -> None:
        booking_card = self._booking_card(booking_reference)
        booking_card.get_by_role("button", name="View Details").click()

    def cancel_booking(self, booking_reference: str) -> None:
        booking_card = self._booking_card(booking_reference)
        booking_card.get_by_role("button", name="Cancel Booking").click()
        self.confirm_dialog.confirm()
        expect(self.page.get_by_text(booking_reference, exact=True)).not_to_be_visible()

    def booking_exists(self, booking_reference: str) -> bool:
        return self.page.get_by_text(booking_reference, exact=True).count() > 0

    def _booking_card(self, booking_reference: str):
        return self.page.get_by_text(booking_reference, exact=True).locator(
            "xpath=ancestor::*[.//button[normalize-space()='Cancel Booking']][1]"
        )
