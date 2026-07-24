import allure
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page


def assert_no_critical_accessibility_violations(page: Page) -> None:
    results = Axe().run(page)
    all_violations = results.response["violations"]
    violations = [violation for violation in all_violations if violation["impact"] == "critical"]

    if all_violations:
        allure.attach(
            str(all_violations),
            name="accessibility-violations",
            attachment_type=allure.attachment_type.TEXT,
        )

    assert not violations
