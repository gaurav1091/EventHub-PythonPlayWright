from playwright.sync_api import Page, expect

from eventhub_automation.core.base_page import BasePage
from eventhub_automation.data.users import BookingCustomer


class EventDetailPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.increment_button = page.get_by_role("button", name="+")
        self.decrement_button = page.get_by_role("button", name="−")
        self.full_name_input = page.get_by_placeholder("Your full name")
        self.email_input = page.get_by_placeholder("you@email.com")
        self.phone_input = page.get_by_placeholder("+91 98765 43210")
        self.confirm_booking_button = page.get_by_role("button", name="Confirm Booking")

    def select_ticket_quantity(self, quantity: int) -> None:
        for _ in range(quantity - 1):
            self.increment_button.click()

    def fill_customer(self, customer: BookingCustomer) -> None:
        self.full_name_input.fill(customer.full_name)
        self.email_input.fill(customer.email)
        self.phone_input.fill(customer.phone)

    def confirm_booking(self) -> None:
        self.confirm_booking_button.click()

    def view_my_bookings(self) -> None:
        self.page.get_by_role("button", name="View My Bookings").click()

    def assert_event_details_visible(self, event_name: str, category: str, price: str) -> None:
        expect(self.page.get_by_role("heading", name=event_name)).to_be_visible()
        expect(self.page.get_by_text(category).first).to_be_visible()
        expect(self.page.get_by_text(price).first).to_be_visible()
        expect(self.confirm_booking_button).to_be_visible()

    def assert_description_visible(self, description: str) -> None:
        expect(self.page.get_by_text(description)).to_be_visible()

    def assert_ticket_summary(self, unit_price: str, quantity: int, total: str) -> None:
        ticket_label = "ticket" if quantity == 1 else "tickets"
        expect(self.page.get_by_text(str(quantity), exact=True)).to_be_visible()
        expect(self.page.get_by_text(f"{unit_price} × {quantity} {ticket_label}")).to_be_visible()
        expect(self.page.get_by_text(total).last).to_be_visible()

    def assert_booking_confirmed(self) -> None:
        expect(self.page.get_by_text("Booking Confirmed!")).to_be_visible()

    def assert_booking_confirmation(self, customer_name: str, quantity: int, total: str) -> None:
        self.assert_booking_confirmed()
        expect(self.page.get_by_text(customer_name)).to_be_visible()
        expect(self.page.get_by_text(str(quantity), exact=True)).to_be_visible()
        expect(self.page.get_by_text(total).last).to_be_visible()

    def get_booking_reference(self) -> str:
        self.assert_booking_confirmed()
        return (
            self.page.get_by_text("Booking Ref")
            .locator("xpath=following-sibling::*[1]")
            .inner_text()
            .strip()
        )
