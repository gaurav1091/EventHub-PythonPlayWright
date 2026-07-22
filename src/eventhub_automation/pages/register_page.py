from playwright.sync_api import Page, expect

from eventhub_automation.core.base_page import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self.sign_in_link = page.get_by_role("link", name="Sign in")

    def load(self) -> None:
        self.page.goto(f"{self.base_url}/register")

    def assert_password_requirements_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Create your account")).to_be_visible()
        expect(self.page.get_by_text("At least 8 characters")).to_be_visible()
        expect(self.page.get_by_text("One uppercase letter")).to_be_visible()
        expect(self.page.get_by_text("One number")).to_be_visible()
        expect(self.page.get_by_text("One special character")).to_be_visible()

    def go_to_sign_in(self) -> None:
        self.sign_in_link.click()
