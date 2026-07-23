from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from eventhub_automation.core.base_page import BasePage


class EventsPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.search_input = page.get_by_placeholder("Search events, venues…")
        self.category_filter = page.locator("select").nth(0)
        self.city_filter = page.locator("select").nth(1)
        self.event_cards = page.locator("article")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/events")

    def search(self, value: str) -> None:
        self.search_input.fill(value)

    def filter_by_category(self, category_label: str) -> None:
        self.category_filter.select_option(label=category_label)

    def filter_by_city(self, city_label: str) -> None:
        self.city_filter.select_option(label=city_label)

    def clear_filters(self) -> None:
        self.page.get_by_role("button", name="Clear filters").click()

    def open_event(self, event_name: str) -> None:
        event_link = self.page.get_by_role("link", name=event_name)
        href = event_link.get_attribute("href")
        event_link.click()
        if href:
            try:
                self.page.wait_for_url(f"**{href}", wait_until="domcontentloaded", timeout=5000)
            except PlaywrightTimeoutError:
                self.page.goto(f"{self.base_url}{href}", wait_until="commit")

    def assert_event_visible(self, event_name: str) -> None:
        expect(self.page.get_by_role("heading", name=event_name)).to_be_visible()

    def assert_event_not_visible(self, event_name: str) -> None:
        expect(self.page.get_by_role("heading", name=event_name)).not_to_be_visible()

    def assert_empty_state_visible(self) -> None:
        expect(self.page.get_by_text("No events found")).to_be_visible()
