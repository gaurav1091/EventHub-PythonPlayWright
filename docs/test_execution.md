# Test Execution

## Common Commands

Run the full suite:

```bash
pytest
```

Run smoke tests:

```bash
pytest -m smoke
```

Run E2E tests:

```bash
pytest -m e2e
```

Run API tests:

```bash
pytest -m api
```

Run a product area:

```bash
pytest -m auth
pytest -m events
pytest -m booking
pytest -m admin
```

Run against Firefox:

```bash
pytest --browser-name firefox
```

Run with pytest-xdist parallel workers:

```bash
pytest tests/api -m "api and not quarantine" -n auto --dist loadscope
pytest tests/ui -m "not quarantine" --browser-name chromium -n 2 --dist loadscope
```

Keep a run serial when debugging or when validating tests that intentionally share mutable backend state:

```bash
pytest tests/ui --browser-name chromium
```

## Docker Commands

Build the Docker image:

```bash
docker compose build
```

Run the default test command:

```bash
docker compose run --rm eventhub-tests
```

Run API tests:

```bash
docker compose run --rm eventhub-tests pytest tests/api -m api
```

Run UI tests against Firefox:

```bash
docker compose run --rm eventhub-tests pytest tests/ui --browser-name firefox
```

Run API tests in parallel:

```bash
docker compose run --rm eventhub-tests pytest tests/api -m api -n auto --dist loadscope
```

The Docker service reads `.env` and mounts `reports/` plus `test-results/` so reports, logs, screenshots, Allure results, and traces are available on the host machine after the run.

## Reports And Artifacts

The framework generates these artifacts:

- `reports/report.html`: self-contained pytest HTML report
- `reports/junit.xml`: CI-friendly JUnit XML report
- `reports/test-run.log`: pytest log file
- `reports/artifacts/`: screenshots attached to failed HTML report entries
- `test-results/traces/`: Playwright traces retained on failure
- `reports/allure-results/`: Allure-compatible result files

Open a retained Playwright trace with:

```bash
playwright show-trace test-results/path-to-trace.zip
```

Open an Allure report when the Allure CLI is installed:

```bash
allure serve reports/allure-results
```

Allure reports are grouped automatically from pytest markers:

- `api`: service/API contract coverage
- `auth`: login, registration, and session behavior
- `events`: event discovery, filtering, and details
- `booking`: booking creation, lookup, cancellation, and seat behavior
- `admin`: admin event management
- `e2e`: cross-page user journeys
- `smoke`: critical health checks and core user confidence tests
- `regression`: broader coverage intended for scheduled or pre-release runs
- `backend_gap`: known backend behavior gaps, normally paired with strict `xfail`
- `serial`: intentionally excluded from parallel execution plans until isolated

Browser-specific UI runs add the browser as an Allure parameter so Chromium and Firefox executions are reported separately.


## Local Quality Gates

Run static checks before a full regression:

```bash
ruff check src tests conftest.py
mypy src tests conftest.py
```

Install and run pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

## CI

GitHub Actions workflow: `.github/workflows/tests.yml`

The workflow runs:

- Ruff lint checks
- mypy type checks
- API tests
- UI and hybrid tests across Chromium and Firefox
- Parallel pytest workers for CI speed, using xdist `loadscope`
- Report and Playwright artifact upload for every test job
- Allure HTML report publishing to GitHub Pages for push and manual workflow runs

Push and pull request runs use these worker defaults:

- API tests: `-n auto --dist loadscope`
- UI Chromium: `-n 2 --dist loadscope`
- UI Firefox: `-n 2 --dist loadscope`

Manual workflow runs include a **Parallel pytest workers** choice. Use `1` for serial/debug runs, or `2`, `4`, or `auto` for parallel execution.

After a GitHub Actions run finishes, open the workflow run summary and use the **Allure Report** link. Pull request runs do not publish the report to Pages.

Before using the hosted report link, configure the repository Pages source as **GitHub Actions** in GitHub repository settings.

Configure these repository secrets before enabling CI:

- `EVENTHUB_BASE_URL`
- `EVENTHUB_USER_EMAIL`
- `EVENTHUB_USER_PASSWORD`


## Flaky And Quarantine Policy

Default test runs exclude tests marked `quarantine`. Quarantined tests must have a linked reason in the test name, marker reason, or tracking ticket before being merged.

Run quarantined tests intentionally with:

```bash
pytest --run-quarantine
```

Use `@pytest.mark.flaky` only for tests with a documented intermittent external dependency. Prefer fixing selectors, waits, and test data isolation before adding retry behavior.

Known backend behavior gaps should use `@pytest.mark.backend_gap` plus `pytest.mark.xfail(..., strict=True)` so the suite tells us when the backend behavior changes.

Use `@pytest.mark.serial` only when a test cannot yet be made data-isolated. Serial tests should be rare, documented, and tracked for isolation work before being allowed into default parallel CI.

## API Test Style

Prefer the shared API assertion helpers over repeating raw response checks:

```python
body = assert_success(response, 201)
assert_validation_error(response, {"email"})
assert_error_contains(response, 404, "not found")
```

Use typed API models when asserting stable resource fields:

```python
event = parse_data(response, EventResource)
assert event.title == "World Tech Summit"
```

Raw `requests.Response` objects are still available from the client when a test needs to inspect non-standard payloads or backend gaps.

## Test Data Lifecycle

Use the `test_data` fixture for API-backed setup and cleanup. It tracks created event and booking IDs, cleans bookings before events, and keeps UI E2E tests focused on user-visible assertions rather than cleanup mechanics.
