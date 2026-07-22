from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str = "") -> None:
        self.page.goto(path)

    def assert_url_contains(self, text: str) -> None:
        expect(self.page).to_have_url(f"**{text}**")

    def assert_text_visible(self, text: str) -> None:
        expect(self.page.get_by_text(text)).to_be_visible()
