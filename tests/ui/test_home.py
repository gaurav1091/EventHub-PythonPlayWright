import pytest

from eventhub_automation.pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_shows_featured_events(authenticated_page):
    home_page = HomePage(authenticated_page)

    home_page.assert_featured_events_visible()
