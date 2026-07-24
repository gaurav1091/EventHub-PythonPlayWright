from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

MAX_HISTORY_RUNS = 50


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the EventHub flakiness dashboard.")
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--site-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    run_reports = _load_current_run_reports(args.artifacts_dir)
    if not run_reports:
        raise SystemExit(f"No flakiness reports found under {args.artifacts_dir}")

    dashboard_dir = args.site_dir / "flakiness"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    history_path = dashboard_dir / "history.json"
    existing_history = _load_history(history_path)
    current_run = _combine_run_reports(run_reports, args.run_id)
    history = _merge_history(existing_history, current_run)

    history_path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")
    (dashboard_dir / "latest.json").write_text(
        json.dumps(current_run, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (dashboard_dir / "index.html").write_text(_render_dashboard(history), encoding="utf-8")


def _load_current_run_reports(artifacts_dir: Path) -> list[dict[str, Any]]:
    reports = []
    for report_path in artifacts_dir.rglob("reports/flakiness/run.json"):
        reports.append(json.loads(report_path.read_text(encoding="utf-8")))
    return reports


def _load_history(history_path: Path) -> dict[str, Any]:
    if not history_path.exists():
        return {"schema_version": 1, "runs": []}
    return json.loads(history_path.read_text(encoding="utf-8"))


def _combine_run_reports(run_reports: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    sorted_reports = sorted(run_reports, key=lambda report: str(report["job_name"]))
    first_report = sorted_reports[0]
    tests = []
    for report in sorted_reports:
        for test in report["tests"]:
            enriched_test = dict(test)
            enriched_test["job_name"] = report["job_name"]
            enriched_test["suite"] = report["suite"]
            enriched_test["browser"] = report["browser"]
            tests.append(enriched_test)

    return {
        "schema_version": 1,
        "run_id": run_id,
        "run_attempt": first_report.get("run_attempt", ""),
        "run_url": first_report.get("run_url", ""),
        "generated_at": first_report.get("generated_at", ""),
        "branch": first_report.get("branch", ""),
        "commit_sha": first_report.get("commit_sha", ""),
        "environment": first_report.get("environment", ""),
        "jobs": [
            {
                "job_name": report["job_name"],
                "suite": report["suite"],
                "browser": report["browser"],
                "totals": report["totals"],
            }
            for report in sorted_reports
        ],
        "totals": _sum_totals([report["totals"] for report in sorted_reports]),
        "tests": sorted(tests, key=lambda test: (str(test["job_name"]), str(test["nodeid"]))),
    }


def _sum_totals(totals_list: list[dict[str, int]]) -> dict[str, int]:
    totals = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "flaky": 0,
        "quarantined": 0,
        "reruns": 0,
    }
    for job_totals in totals_list:
        for key in totals:
            totals[key] += int(job_totals.get(key, 0))
    return totals


def _merge_history(history: dict[str, Any], current_run: dict[str, Any]) -> dict[str, Any]:
    previous_runs = [
        run for run in history.get("runs", []) if run.get("run_id") != current_run["run_id"]
    ]
    merged_runs = [current_run, *previous_runs]
    return {"schema_version": 1, "runs": merged_runs[:MAX_HISTORY_RUNS]}


def _render_dashboard(history: dict[str, Any]) -> str:
    runs = history.get("runs", [])
    latest_run = runs[0] if runs else {}
    flaky_tests = _top_flaky_tests(runs)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EventHub Flakiness Dashboard</title>
    <style>
      body {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 32px;
        color: #172033;
        background: #f7f8fb;
      }}
      main {{ max-width: 1180px; margin: 0 auto; }}
      h1, h2 {{ margin: 0 0 12px; }}
      p {{ color: #5f6b7a; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        margin: 20px 0 28px;
      }}
      .metric {{
        background: #fff;
        border: 1px solid #dfe4ea;
        border-radius: 8px;
        padding: 16px;
      }}
      .metric strong {{ display: block; font-size: 28px; }}
      table {{
        width: 100%;
        border-collapse: collapse;
        background: #fff;
        border: 1px solid #dfe4ea;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 28px;
      }}
      th, td {{
        padding: 10px 12px;
        border-bottom: 1px solid #e8edf3;
        text-align: left;
        vertical-align: top;
      }}
      th {{
        background: #eef2f7;
        font-size: 13px;
        text-transform: uppercase;
        color: #4d5a69;
      }}
      tr:last-child td {{ border-bottom: 0; }}
      code {{ font-size: 12px; }}
      a {{ color: #2454d6; }}
    </style>
  </head>
  <body>
    <main>
      <h1>EventHub Flakiness Dashboard</h1>
      <p>
        Tracks retries, flaky markers, quarantine markers, and failed tests across the last
        {MAX_HISTORY_RUNS} published runs.
      </p>
      {_render_latest_summary(latest_run)}
      <h2>Run History</h2>
      {_render_runs_table(runs)}
      <h2>Most Flaky Tests</h2>
      {_render_flaky_tests_table(flaky_tests)}
    </main>
  </body>
</html>
"""


def _render_latest_summary(latest_run: dict[str, Any]) -> str:
    totals = latest_run.get("totals", {})
    return f"""
      <div class="grid">
        {_metric("Total", totals.get("total", 0))}
        {_metric("Passed", totals.get("passed", 0))}
        {_metric("Failed", totals.get("failed", 0))}
        {_metric("Reruns", totals.get("reruns", 0))}
        {_metric("Flaky", totals.get("flaky", 0))}
        {_metric("Quarantined", totals.get("quarantined", 0))}
      </div>
    """


def _metric(label: str, value: Any) -> str:
    return f'<div class="metric"><span>{html.escape(label)}</span><strong>{value}</strong></div>'


def _render_runs_table(runs: list[dict[str, Any]]) -> str:
    rows = []
    for run in runs:
        totals = run.get("totals", {})
        run_label = html.escape(str(run.get("run_id", "")))
        run_url = str(run.get("run_url", ""))
        run_cell = f'<a href="{html.escape(run_url)}">{run_label}</a>' if run_url else run_label
        rows.append(
            "<tr>"
            f"<td>{run_cell}</td>"
            f"<td>{html.escape(str(run.get('generated_at', '')))}</td>"
            f"<td>{html.escape(str(run.get('branch', '')))}</td>"
            f"<td>{totals.get('total', 0)}</td>"
            f"<td>{totals.get('failed', 0)}</td>"
            f"<td>{totals.get('reruns', 0)}</td>"
            f"<td>{totals.get('flaky', 0)}</td>"
            f"<td>{totals.get('quarantined', 0)}</td>"
            "</tr>"
        )
    return _table(
        ["Run", "Generated", "Branch", "Total", "Failed", "Reruns", "Flaky", "Quarantine"],
        rows,
    )


def _render_flaky_tests_table(flaky_tests: list[dict[str, Any]]) -> str:
    rows = []
    for test in flaky_tests:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(test['nodeid']))}</code></td>"
            f"<td>{test['runs_seen']}</td>"
            f"<td>{test['failures']}</td>"
            f"<td>{test['reruns']}</td>"
            f"<td>{test['flaky_marked_runs']}</td>"
            "</tr>"
        )
    return _table(["Test", "Runs Seen", "Failures", "Reruns", "Flaky Marked Runs"], rows)


def _table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_html = (
        "".join(rows) if rows else f"<tr><td colspan='{len(headers)}'>No data yet.</td></tr>"
    )
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"


def _top_flaky_tests(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    test_stats: dict[str, dict[str, Any]] = {}
    for run in runs:
        for test in run.get("tests", []):
            nodeid = str(test["nodeid"])
            stats = test_stats.setdefault(
                nodeid,
                {
                    "nodeid": nodeid,
                    "runs_seen": 0,
                    "failures": 0,
                    "reruns": 0,
                    "flaky_marked_runs": 0,
                },
            )
            stats["runs_seen"] += 1
            stats["failures"] += 1 if test.get("outcome") == "failed" else 0
            stats["reruns"] += int(test.get("reruns", 0))
            stats["flaky_marked_runs"] += 1 if test.get("flaky") else 0

    return sorted(
        test_stats.values(),
        key=lambda test: (test["reruns"], test["failures"], test["flaky_marked_runs"]),
        reverse=True,
    )[:20]


if __name__ == "__main__":
    main()
