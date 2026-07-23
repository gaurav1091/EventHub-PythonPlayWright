# EventHub Pytest Automation Framework

![EventHub Automation Tests](https://github.com/gaurav1091/EventHub-PythonPlayWright/actions/workflows/tests.yml/badge.svg)

Enterprise-grade starter framework for automating the EventHub practice app with Python, Pytest, and Playwright.

## Current Scope

- UI automation first: auth, event discovery, event details, bookings, booking management, and admin event management.
- Hybrid UI + API automation: API clients support fast setup/cleanup, while UI tests validate user-facing behavior.
- Inspired by the attached `PytestPython` project, but cleaned up for maintainability, scalability, and test data hygiene.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
playwright install
cp .env.example .env
pytest
```

See [Test Execution](docs/test_execution.md) for reporting, logging, browser, marker, and artifact commands.

## Structure

```text
eventhub_pytest_framework/
  config/
  docs/
  src/eventhub_automation/
    api/
    core/
    data/
    pages/
  tests/
    api/
    ui/
      admin/
      auth/
      bookings/
      events/
  reports/
  test-results/
```

## Framework Principles

- Tests describe business behavior; page objects handle UI interaction.
- Locators live in page classes, not in tests.
- Configuration comes from environment variables and CLI options, not hard-coded credentials.
- API clients sit beside UI page objects, enabling hybrid setup/cleanup and faster validations.
- Reports, traces, screenshots, and videos are generated only when useful.


## Quality Gates


Run local checks before pushing:

```bash
ruff check src tests conftest.py
mypy src tests conftest.py
pytest
```

Optional pre-commit hooks are configured in `.pre-commit-config.yaml`:

```bash
pre-commit install
pre-commit run --all-files
```

GitHub Actions runs linting, typing, API tests, and a Chromium/Firefox UI browser matrix. The workflow has been validated successfully in GitHub Actions. CI expects these repository secrets: `EVENTHUB_BASE_URL`, `EVENTHUB_USER_EMAIL`, and `EVENTHUB_USER_PASSWORD`.


## Reporting

The framework writes pytest-html, JUnit XML, logs, failure screenshots, Playwright traces, and Allure result files. Use `allure serve reports/allure-results` when the Allure CLI is installed locally.
