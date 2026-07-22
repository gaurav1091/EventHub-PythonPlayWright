from playwright.sync_api import Page, expect

from eventhub_automation.components.confirm_dialog import ConfirmDialog
from eventhub_automation.core.base_page import BasePage
from eventhub_automation.data.users import EventData


class AdminEventsPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.confirm_dialog = ConfirmDialog(page)
        self.add_event_button = page.get_by_role("button", name="+ Add Event")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/admin/events")

    def assert_loaded(self) -> None:
        expect(self.page.get_by_text("All Events")).to_be_visible()
        expect(self.add_event_button).to_be_visible()

    def assert_featured_events_table_visible(self) -> None:
        expect(self.page.get_by_role("columnheader", name="Title")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Category")).to_be_visible()
        expect(self.page.get_by_role("columnheader", name="Actions")).to_be_visible()
        expect(
            self.page.get_by_role("row", name="Dilli Diwali Mela Featured Festival Delhi")
        ).to_be_visible()
        expect(
            self.page.get_by_role("row", name="World Tech Summit Featured Conference")
        ).to_be_visible()
        expect(self.page.get_by_text("Read-only").first).to_be_visible()

    def create_event(self, event: EventData) -> None:
        self.page.get_by_label("Title*").fill(event.title)
        self.page.get_by_role("textbox", name="Describe the event…").fill(event.description)
        self.page.get_by_label("Category*").select_option(label=event.category)
        self.page.get_by_label("City*").fill(event.city)
        self.page.get_by_label("Venue*").fill(event.venue)
        self.page.get_by_label("Event Date & Time*").fill(event.date_time)
        self.page.get_by_label("Price ($)*").fill(event.price)
        self.page.get_by_label("Total Seats*").fill(event.total_seats)
        self.add_event_button.click()

    def assert_event_row_visible(self, event: EventData, display_date: str) -> None:
        event_row = self._event_row(event.title)
        expect(event_row).to_be_visible()
        expect(event_row.get_by_text(event.category, exact=True)).to_be_visible()
        expect(event_row.get_by_text(event.city, exact=True)).to_be_visible()
        expect(event_row.get_by_text(display_date, exact=True)).to_be_visible()
        expect(event_row.get_by_text(f"${event.price}", exact=True)).to_be_visible()

    def assert_event_row_not_visible(self, event_title: str) -> None:
        expect(self.page.get_by_text(event_title, exact=True)).not_to_be_visible()

    def delete_event(self, event_title: str) -> None:
        self._event_row(event_title).get_by_role("button", name="Delete").click()
        self.confirm_dialog.confirm()
        self.assert_event_row_not_visible(event_title)

    def event_exists(self, event_title: str) -> bool:
        return self.page.get_by_text(event_title, exact=True).count() > 0

    def _event_row(self, event_title: str):
        return self.page.get_by_text(event_title, exact=True).locator("xpath=ancestor::tr[1]")
