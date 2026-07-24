import pytest

from eventhub_automation.accessibility import assert_no_critical_accessibility_violations
from eventhub_automation.pages.home_page import HomePage
from eventhub_automation.pages.login_page import LoginPage


@pytest.mark.accessibility
@pytest.mark.smoke
def test_home_page_has_no_critical_accessibility_violations(authenticated_page):
    HomePage(authenticated_page).assert_featured_events_visible()

    assert_no_critical_accessibility_violations(authenticated_page)


@pytest.mark.accessibility
@pytest.mark.auth
def test_login_page_has_no_critical_accessibility_violations(page, settings):
    login_page = LoginPage(page, settings.base_url)
    login_page.load()

    assert_no_critical_accessibility_violations(page)
