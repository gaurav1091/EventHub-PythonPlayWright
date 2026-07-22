from playwright.sync_api import Page, expect

from eventhub_automation.core.base_page import BasePage


class AdminBookingsPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.status_filter = page.locator("select")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/admin/bookings")

    def filter_by_status(self, status: str) -> None:
        self.status_filter.select_option(label=status)

    def assert_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Manage Bookings")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Ref")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Customer")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Event")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Status")).to_be_visible()

    def assert_status_options_visible(self) -> None:
        expect(self.status_filter).to_contain_text("All Statuses")
        expect(self.status_filter).to_contain_text("Confirmed")
        expect(self.status_filter).to_contain_text("Cancelled")
