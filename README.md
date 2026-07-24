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

Named environment and suite profiles are available:

```bash
pytest --env qa --suite smoke
pytest --suite api-regression -n auto --dist loadscope
pytest --suite contract
pytest tests/ui/visual --suite visual --run-visual --browser-name chromium
```

## Docker Quick Start

Build the test image:

```bash
docker compose build
```

Run the default suite in Docker:

```bash
docker compose run --rm eventhub-tests
```

Run a targeted Docker command:

```bash
docker compose run --rm eventhub-tests pytest tests/api -m api
docker compose run --rm eventhub-tests pytest tests/ui --browser-name firefox
```

Docker uses `.env` for EventHub credentials and writes reports back to local `reports/` and `test-results/`.

## Structure

```text
eventhub_pytest_framework/
  config/
  docs/
  src/eventhub_automation/
    api/
      assertions.py
      eventhub_client.py
      models.py
    core/
    data/
    flows/
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
- Environment profiles make target URLs explicit and reviewable.
- API clients sit beside UI page objects, enabling hybrid setup/cleanup and faster validations.
- API assertions and typed models keep service tests consistent without hiding raw responses.
- Suite profiles and marker standards keep local, CI, smoke, regression, and release runs consistent.
- Contract tests validate API response schemas with typed models and shared assertions.
- Visual regression tests compare reviewed baselines in a dedicated opt-in suite.
- Reports, traces, screenshots, and videos are generated only when useful.


## Quality Gates


Run local checks before pushing:

```bash
ruff check src tests conftest.py
mypy src tests conftest.py
detect-secrets scan --baseline .secrets.baseline
pip-audit
pytest
```

Optional pre-commit hooks are configured in `.pre-commit-config.yaml`:

```bash
pre-commit install
pre-commit run --all-files
```

GitHub Actions runs linting, typing, security checks, API tests, and a Chromium/Firefox UI browser matrix. The workflow has been validated successfully in GitHub Actions. CI expects these repository secrets: `EVENTHUB_BASE_URL`, `EVENTHUB_USER_EMAIL`, and `EVENTHUB_USER_PASSWORD`.  # pragma: allowlist secret

CI uses pytest-xdist for faster feedback: API jobs run with automatic workers, and each UI browser job runs with two workers. Manual workflow runs include a worker-count choice for serial debugging or parallel execution.


## Reporting

The framework writes pytest-html, JUnit XML, logs, failure screenshots, Playwright traces, and Allure result files. GitHub Actions publishes the Allure HTML report to GitHub Pages and adds the report link to the workflow summary. Use `allure serve reports/allure-results` when the Allure CLI is installed locally.

## Accessibility

Accessibility smoke tests use axe through Playwright and are marked with `accessibility`.

## Visual Regression

Visual checks are marked with `visual` and are intentionally opt-in so regular UI reports only show the selected functional tests. To update a baseline, run the visual suite, review the image under `reports/visual/`, and replace the matching file under `tests/ui/visual/baselines/` only when the UI change is expected.
