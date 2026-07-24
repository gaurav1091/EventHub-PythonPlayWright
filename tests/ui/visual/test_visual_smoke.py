import pytest

from eventhub_automation.pages.login_page import LoginPage
from eventhub_automation.pages.register_page import RegisterPage
from eventhub_automation.visual import assert_visual_baseline

BASELINE_DIR = "tests/ui/visual/baselines"
ACTUAL_DIR = "reports/visual"
VISUAL_VIEWPORT = {"width": 1280, "height": 900}


@pytest.mark.visual
def test_login_page_visual_baseline(page, settings):
    page.set_viewport_size(VISUAL_VIEWPORT)
    login_page = LoginPage(page, settings.base_url)
    login_page.load()
    login_page.assert_loaded()

    assert_visual_baseline(
        page,
        baseline_path=f"{BASELINE_DIR}/login-page.png",
        actual_path=f"{ACTUAL_DIR}/login-page.png",
    )


@pytest.mark.visual
def test_register_page_visual_baseline(page, settings):
    page.set_viewport_size(VISUAL_VIEWPORT)
    register_page = RegisterPage(page, settings.base_url)
    register_page.load()
    register_page.assert_password_requirements_visible()

    assert_visual_baseline(
        page,
        baseline_path=f"{BASELINE_DIR}/register-page.png",
        actual_path=f"{ACTUAL_DIR}/register-page.png",
    )
