import pytest

from eventhub_automation.pages.event_detail_page import EventDetailPage
from eventhub_automation.pages.events_page import EventsPage


@pytest.mark.events
def test_user_can_filter_events_by_city(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)

    events_page.load()
    events_page.filter_by_city("Delhi")

    events_page.assert_event_visible("Dilli Diwali Mela")


@pytest.mark.events
def test_user_can_search_events_by_name(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)

    events_page.load()
    events_page.search("World")

    events_page.assert_event_visible("World Tech Summit")
    events_page.assert_event_not_visible("Dilli Diwali Mela")


@pytest.mark.events
def test_search_with_no_results_shows_empty_state(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)

    events_page.load()
    events_page.search("NoSuchEvent")

    events_page.assert_empty_state_visible()
    events_page.clear_filters()
    events_page.assert_event_visible("World Tech Summit")


@pytest.mark.events
def test_user_can_filter_events_by_category(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)

    events_page.load()
    events_page.filter_by_category("🎙 Conference")

    events_page.assert_event_visible("World Tech Summit")
    events_page.assert_event_not_visible("Dilli Diwali Mela")


@pytest.mark.events
def test_event_detail_shows_booking_summary(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)

    events_page.load()
    events_page.open_event("World Tech Summit")

    event_detail_page.assert_event_details_visible("World Tech Summit", "Conference", "$1,500")
    event_detail_page.assert_ticket_summary("$1,500", 1, "$1,500")


@pytest.mark.events
def test_ticket_quantity_updates_total(authenticated_page, settings):
    events_page = EventsPage(authenticated_page, settings.base_url)
    event_detail_page = EventDetailPage(authenticated_page)

    events_page.load()
    events_page.open_event("World Tech Summit")
    event_detail_page.select_ticket_quantity(2)

    event_detail_page.assert_ticket_summary("$1,500", 2, "$3,000")
