from playwright.sync_api import Page

from eventhub_automation.core.logger import get_logger
from eventhub_automation.pages.home_page import HomePage
from eventhub_automation.pages.login_page import LoginPage

LOGGER = get_logger("flows.auth")


class AuthFlow:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.login_page = LoginPage(page, base_url)
        self.home_page = HomePage(page)

    def sign_in(self, email: str, password: str) -> Page:
        LOGGER.info("Signing in user %s", email)
        self.login_page.load()
        self.login_page.login(email, password)
        self.home_page.assert_user_logged_in(email)
        return self.page
