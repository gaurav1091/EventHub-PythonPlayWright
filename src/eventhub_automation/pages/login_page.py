from playwright.sync_api import Page, expect

from eventhub_automation.core.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.email_input = page.get_by_placeholder("you@email.com")
        self.password_input = page.get_by_placeholder("••••••")
        self.sign_in_button = page.get_by_role("button", name="Sign In")
        self.register_link = page.get_by_role("link", name="Register")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/login")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()

    def assert_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Sign in to EventHub")).to_be_visible()
