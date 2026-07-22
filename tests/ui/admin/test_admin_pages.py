import pytest

from eventhub_automation.pages.admin_bookings_page import AdminBookingsPage
from eventhub_automation.pages.admin_events_page import AdminEventsPage


@pytest.mark.admin
def test_admin_events_page_lists_featured_events(authenticated_page, settings):
    admin_events_page = AdminEventsPage(authenticated_page, settings.base_url)

    admin_events_page.load()

    admin_events_page.assert_loaded()
    admin_events_page.assert_featured_events_table_visible()


@pytest.mark.admin
def test_admin_bookings_page_filters_by_status(authenticated_page, settings):
    admin_bookings_page = AdminBookingsPage(authenticated_page, settings.base_url)

    admin_bookings_page.load()

    admin_bookings_page.assert_loaded()
    admin_bookings_page.assert_status_options_visible()
    admin_bookings_page.filter_by_status("Confirmed")
    admin_bookings_page.assert_loaded()
