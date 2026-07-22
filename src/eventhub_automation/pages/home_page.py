from playwright.sync_api import Page, expect

from eventhub_automation.components.navigation_bar import NavigationBar
from eventhub_automation.core.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.navbar = NavigationBar(page)

    def assert_user_logged_in(self, email: str) -> None:
        self.navbar.assert_user_logged_in(email)

    def assert_featured_events_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Featured Events")).to_be_visible()
        expect(self.page.get_by_role("heading", name="Dilli Diwali Mela")).to_be_visible()
        expect(self.page.get_by_role("heading", name="World Tech Summit")).to_be_visible()

    def go_to_events(self) -> None:
        self.navbar.go_to_events()

    def go_to_bookings(self) -> None:
        self.navbar.go_to_bookings()

    def logout(self) -> None:
        self.navbar.logout()
