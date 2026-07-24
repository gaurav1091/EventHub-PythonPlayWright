import base64
import os
import re
import shutil
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from pytest_html import extras as html_extras
from pytest_metadata.plugin import metadata_key

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.core.config import Settings
from eventhub_automation.core.environments import get_environment_profile
from eventhub_automation.core.logger import get_logger
from eventhub_automation.core.suites import get_suite_profile
from eventhub_automation.data.lifecycle import TestDataManager, managed_test_data
from eventhub_automation.flows.auth_flow import AuthFlow

LOGGER = get_logger("pytest")
REPORTS_DIR = Path("reports")
ARTIFACTS_DIR = REPORTS_DIR / "artifacts"
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
TRACES_DIR = Path("test-results") / "traces"

ALLURE_MARKER_FEATURES = {
    "api": ("API", "Service Contracts"),
    "auth": ("Authentication", "Identity"),
    "events": ("Events", "Event Discovery"),
    "booking": ("Bookings", "Booking Lifecycle"),
    "admin": ("Administration", "Event Management"),
    "e2e": ("End To End", "User Journeys"),
    "smoke": ("Smoke", "Critical Paths"),
    "regression": ("Regression", "Full Coverage"),
    "backend_gap": ("Backend Gaps", "Known Product Gaps"),
    "serial": ("Execution Policy", "Serial Tests"),
    "accessibility": ("Accessibility", "Automated WCAG Signals"),
    "visual": ("Visual Regression", "Screenshot Baselines"),
    "contract": ("API Contracts", "Schema Validation"),
}

ALLURE_MARKER_SUITES = (
    "contract",
    "visual",
    "accessibility",
    "api",
    "e2e",
    "smoke",
    "auth",
    "events",
    "booking",
    "admin",
    "regression",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--browser-name", action="store", default=None, help="chromium/firefox/webkit")
    parser.addoption("--env", action="store", default=None, help="environment profile name")
    parser.addoption("--suite", action="store", default=None, help="suite profile name")
    parser.addoption(
        "--run-quarantine",
        action="store_true",
        default=False,
        help="include tests marked quarantine",
    )
    parser.addoption(
        "--run-visual",
        action="store_true",
        default=False,
        help="include visual regression tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    clean_reports = os.getenv("EVENTHUB_CLEAN_REPORTS", "true").lower() in {"1", "true", "yes"}
    is_xdist_worker = hasattr(config, "workerinput")
    if clean_reports and not is_xdist_worker:
        shutil.rmtree(REPORTS_DIR, ignore_errors=True)
        shutil.rmtree(TRACES_DIR.parent, ignore_errors=True)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    config.stash[metadata_key]["Project"] = "EventHub Pytest Automation"
    config.stash[metadata_key]["Base URL"] = Settings().base_url


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    suite_name = config.getoption("--suite")
    suite_profile = get_suite_profile(suite_name) if suite_name else None
    mark_expression = config.option.markexpr or ""
    run_visual = (
        config.getoption("--run-visual") or suite_name == "visual" or "visual" in mark_expression
    )
    if config.getoption("--run-quarantine"):
        skip_quarantine = None
    else:
        skip_quarantine = pytest.mark.skip(reason="quarantined; rerun with --run-quarantine")

    if suite_profile or not run_visual:
        selected_items = []
        deselected_items = []
        for item in items:
            keywords = set(item.keywords)
            excluded_by_suite = suite_profile and not suite_profile.includes(keywords)
            excluded_visual = not run_visual and "visual" in keywords

            if excluded_by_suite or excluded_visual:
                deselected_items.append(item)
            else:
                selected_items.append(item)

        if deselected_items:
            config.hook.pytest_deselected(items=deselected_items)
            items[:] = selected_items

    for item in items:
        if skip_quarantine and "quarantine" in item.keywords:
            item.add_marker(skip_quarantine)


def pytest_runtest_setup(item: pytest.Item) -> None:
    allure.dynamic.epic("EventHub")
    allure.dynamic.parent_suite("EventHub Automation")
    allure.dynamic.suite(_allure_suite_name(item))
    for marker_name, (feature, story) in ALLURE_MARKER_FEATURES.items():
        if marker_name in item.keywords:
            allure.dynamic.feature(feature)
            allure.dynamic.story(story)
            allure.dynamic.tag(marker_name)

    browser_name = item.config.getoption("--browser-name")
    if browser_name:
        allure.dynamic.parameter("browser", browser_name)


def _allure_suite_name(item: pytest.Item) -> str:
    configured_suite = item.config.getoption("--suite")
    workflow_suite = os.getenv("EVENTHUB_SUITE_NAME")
    if configured_suite:
        return configured_suite
    if workflow_suite:
        return workflow_suite

    for marker_name in ALLURE_MARKER_SUITES:
        if marker_name in item.keywords:
            return marker_name
    return "all"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        funcargs = getattr(item, "funcargs", {})
        page = funcargs.get("page") or funcargs.get("authenticated_page")
        if page:
            screenshot_path = ARTIFACTS_DIR / f"{item.name}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            screenshot_bytes = screenshot_path.read_bytes()
            screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
            extras.append(html_extras.png(screenshot))
            allure.attach(
                screenshot_bytes,
                name=item.name,
                attachment_type=allure.attachment_type.PNG,
            )

    report.extras = extras


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest) -> Settings:
    settings = Settings()
    environment = request.config.getoption("--env")
    browser_name = request.config.getoption("--browser-name")
    base_url = request.config.getoption("--base-url")
    headed = request.config.getoption("--headed")

    if environment:
        profile = get_environment_profile(environment)
        settings.environment = profile.name
        settings.base_url = profile.base_url
        settings.api_base_url = profile.api_base_url
    if browser_name:
        settings.browser = browser_name
    if base_url:
        settings.base_url = base_url.rstrip("/")
    if headed:
        settings.headless = False
    return settings


@pytest.fixture(scope="session")
def browser(playwright: Playwright, settings: Settings) -> Generator[Browser, None, None]:
    LOGGER.info("Launching %s browser; headless=%s", settings.browser, settings.headless)
    browser_type = getattr(playwright, settings.browser)
    browser = browser_type.launch(headless=settings.headless, slow_mo=settings.slow_mo_ms)
    yield browser
    browser.close()


@pytest.fixture()
def context(
    browser: Browser,
    request: pytest.FixtureRequest,
) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(ignore_https_errors=True)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        trace_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
        trace_path = TRACES_DIR / f"{trace_name}.zip"
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()
    context.close()


@pytest.fixture()
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page


@pytest.fixture()
def authenticated_page(page: Page, settings: Settings) -> Page:
    return AuthFlow(page, settings.base_url).sign_in(settings.user_email, settings.user_password)


@pytest.fixture()
def api_client(settings: Settings) -> EventHubClient:
    return EventHubClient(settings.api_base_url)


@pytest.fixture()
def authenticated_api_client(api_client: EventHubClient, settings: Settings) -> EventHubClient:
    response = api_client.login(settings.user_email, settings.user_password)
    assert response.status_code == 200
    assert response.json()["success"] is True
    return api_client


@pytest.fixture()
def test_data(authenticated_api_client: EventHubClient) -> Generator[TestDataManager, None, None]:
    yield from managed_test_data(authenticated_api_client)
