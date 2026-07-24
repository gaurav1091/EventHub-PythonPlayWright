from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def build_flakiness_run_report(
    *,
    reports: list[dict[str, Any]],
    marker_map: dict[str, list[str]],
    started_at: str,
    output_path: Path,
    suite_name: str,
    browser_name: str | None,
    environment_name: str,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tests = _summarize_tests(reports, marker_map)
    totals = _summarize_totals(tests)
    run_report = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "started_at": started_at,
        "run_id": os.getenv("GITHUB_RUN_ID", f"local-{started_at}"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "local"),
        "run_url": _github_run_url(),
        "job_name": os.getenv("EVENTHUB_JOB_NAME", "local"),
        "suite": suite_name,
        "browser": browser_name or "not_applicable",
        "environment": environment_name,
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "totals": totals,
        "tests": tests,
    }
    output_path.write_text(json.dumps(run_report, indent=2, sort_keys=True), encoding="utf-8")
    return run_report


def _summarize_tests(
    reports: list[dict[str, Any]],
    marker_map: dict[str, list[str]],
) -> list[dict[str, Any]]:
    grouped_reports = defaultdict(list)
    for report in reports:
        grouped_reports[str(report["nodeid"])].append(report)

    tests = []
    for nodeid, node_reports in sorted(grouped_reports.items()):
        call_reports = [report for report in node_reports if report["when"] == "call"]
        terminal_reports = [
            report
            for report in node_reports
            if report["outcome"] in {"passed", "failed", "skipped"}
        ]
        final_report = (call_reports or terminal_reports or node_reports)[-1]
        reruns = sum(1 for report in node_reports if report["outcome"] == "rerun")
        report_markers = {
            marker
            for report in node_reports
            for marker in report.get("markers", [])
            if isinstance(marker, str)
        }
        markers = sorted(set(marker_map.get(nodeid, [])) | report_markers)
        final_outcome = str(final_report["outcome"])
        tests.append(
            {
                "nodeid": nodeid,
                "outcome": final_outcome,
                "attempts": reruns + 1,
                "reruns": reruns,
                "duration_seconds": round(
                    sum(float(report["duration"]) for report in node_reports),
                    3,
                ),
                "markers": markers,
                "flaky": reruns > 0 or "flaky" in markers,
                "quarantined": "quarantine" in markers,
                "failure_phase": final_report["when"] if final_outcome == "failed" else None,
                "failure": final_report.get("longrepr"),
            }
        )
    return tests


def _summarize_totals(tests: list[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "total": len(tests),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "flaky": 0,
        "quarantined": 0,
        "reruns": 0,
    }
    for test in tests:
        outcome = str(test["outcome"])
        if outcome in {"passed", "failed", "skipped"}:
            totals[outcome] += 1
        if test["flaky"]:
            totals["flaky"] += 1
        if test["quarantined"]:
            totals["quarantined"] += 1
        totals["reruns"] += int(test["reruns"])
    return totals


def _github_run_url() -> str:
    server_url = os.getenv("GITHUB_SERVER_URL")
    repository = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    if server_url and repository and run_id:
        return f"{server_url}/{repository}/actions/runs/{run_id}"
    return ""
