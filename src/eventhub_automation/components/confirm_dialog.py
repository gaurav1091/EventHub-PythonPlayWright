from playwright.sync_api import Page, expect


class ConfirmDialog:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.confirm_button = page.get_by_test_id("confirm-dialog-yes")

    def confirm(self) -> None:
        expect(self.confirm_button).to_be_visible()
        self.confirm_button.click()
