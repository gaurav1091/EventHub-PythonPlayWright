from playwright.sync_api import Page, expect


class NavigationBar:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.events_link = page.get_by_test_id("nav-events")
        self.bookings_link = page.get_by_role("link", name="My Bookings")
        self.logout_button = page.get_by_role("button", name="Logout")

    def assert_user_logged_in(self, email: str) -> None:
        expect(self.page.get_by_text(email)).to_be_visible()

    def go_to_events(self) -> None:
        self.events_link.click()

    def go_to_bookings(self) -> None:
        self.bookings_link.click()

    def logout(self) -> None:
        self.logout_button.click()
