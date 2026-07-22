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

Open a retained Playwright trace with:

```bash
playwright show-trace test-results/path-to-trace.zip
```
