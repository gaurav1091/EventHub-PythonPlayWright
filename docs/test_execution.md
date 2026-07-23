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

Run against Firefox:

```bash
pytest --browser-name firefox
```

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
- Report and Playwright artifact upload for every test job

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

## Test Data Lifecycle

Use the `test_data` fixture for API-backed setup and cleanup. It tracks created event and booking IDs, cleans bookings before events, and keeps UI E2E tests focused on user-visible assertions rather than cleanup mechanics.
