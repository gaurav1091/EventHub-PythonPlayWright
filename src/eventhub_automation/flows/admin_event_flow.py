from playwright.sync_api import Page

from eventhub_automation.core.logger import get_logger
from eventhub_automation.data.users import EventData
from eventhub_automation.pages.admin_events_page import AdminEventsPage
from eventhub_automation.pages.event_detail_page import EventDetailPage
from eventhub_automation.pages.events_page import EventsPage

LOGGER = get_logger("flows.admin_events")


class AdminEventFlow:
    def __init__(self, page: Page, base_url: str) -> None:
        self.admin_events_page = AdminEventsPage(page, base_url)
        self.events_page = EventsPage(page, base_url)
        self.event_detail_page = EventDetailPage(page)

    def create_event(self, event: EventData, display_date: str) -> None:
        LOGGER.info("Creating admin event %s", event.title)
        self.admin_events_page.load()
        self.admin_events_page.create_event(event)
        self.admin_events_page.assert_event_row_visible(event, display_date)

    def open_published_event(self, event_title: str) -> None:
        LOGGER.info("Opening published event %s", event_title)
        self.events_page.load()
        self.events_page.search(event_title)
        self.events_page.assert_event_visible(event_title)
        self.events_page.open_event(event_title)

    def delete_event_if_present(self, event_title: str) -> None:
        self.admin_events_page.load()
        if self.admin_events_page.event_exists(event_title):
            LOGGER.info("Cleaning up admin event %s", event_title)
            self.admin_events_page.delete_event(event_title)
