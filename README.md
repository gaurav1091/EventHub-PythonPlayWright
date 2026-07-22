# EventHub Pytest Automation Framework

Enterprise-grade starter framework for automating the EventHub practice app with Python, Pytest, and Playwright.

## Current Scope

- UI automation first: auth, event discovery, event details, bookings, booking management, and admin event management.
- Designed to grow into a hybrid UI + API framework without rewriting test architecture.
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
- API clients will sit beside UI page objects, enabling hybrid setup/cleanup and faster validations.
- Reports, traces, screenshots, and videos are generated only when useful.
