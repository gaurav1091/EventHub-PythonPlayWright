import pytest

from eventhub_automation.pages.home_page import HomePage
from eventhub_automation.pages.login_page import LoginPage
from eventhub_automation.pages.register_page import RegisterPage


@pytest.mark.auth
@pytest.mark.smoke
def test_registered_user_can_login(page, settings):
    login_page = LoginPage(page, settings.base_url)
    home_page = HomePage(page)

    login_page.load()
    login_page.login(settings.user_email, settings.user_password)

    home_page.assert_user_logged_in(settings.user_email)


@pytest.mark.auth
def test_user_can_logout(authenticated_page):
    home_page = HomePage(authenticated_page)
    login_page = LoginPage(authenticated_page, "")

    home_page.logout()

    login_page.assert_loaded()


@pytest.mark.auth
def test_register_page_shows_password_requirements(page, settings):
    register_page = RegisterPage(page, settings.base_url)
    login_page = LoginPage(page, settings.base_url)

    register_page.load()
    register_page.assert_password_requirements_visible()
    register_page.go_to_sign_in()

    login_page.assert_loaded()
