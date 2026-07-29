#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHART_HASH = (
    "48444a82d4edcb5bec0f1965faacdde18d9c17db3063d042abada2f705c9f54a"
)
DASHBOARD_DATA_PREFIX = "window.COMPLAINT_DASHBOARD_DATA = "


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    evidence: str,
) -> None:
    checks.append({"name": name, "passed": passed, "evidence": evidence})


def main() -> None:
    manifest = json.loads(
        (ROOT / "evidence" / "source-manifest.json").read_text(encoding="utf-8")
    )
    quality = json.loads(
        (ROOT / "evidence" / "data-quality-report.json").read_text(
            encoding="utf-8"
        )
    )
    dashboard_path = ROOT / "docs" / "dashboard-data.js"
    dashboard_text = dashboard_path.read_text(encoding="utf-8")
    dashboard = json.loads(dashboard_text[len(DASHBOARD_DATA_PREFIX) : -2])
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    script = ROOT / "docs" / "app.js"
    chart = ROOT / "docs" / "vendor" / "chart.umd.min.js"
    config = json.loads(
        (ROOT / "config" / "pipeline.json").read_text(encoding="utf-8")
    )

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "quality_status",
        quality["status"] in {"passed", "passed_with_warnings"},
        quality["status"],
    )
    add_check(
        checks,
        "critical_data_checks",
        quality["critical_checks"]["status"] == "passed",
        json.dumps(quality["critical_checks"], sort_keys=True),
    )

    with sqlite3.connect(ROOT / "data" / "processed" / "complaints.db") as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM complaints"
        ).fetchone()[0]
        overview = connection.execute(
            """
            SELECT
                complaint_count,
                timely_response_rate,
                not_timely_count,
                not_timely_rate,
                relief_response_rate,
                relief_response_count
            FROM metric_overview
            """
        ).fetchone()

    counts_match = (
        manifest["row_count"]
        == quality["row_count"]
        == dashboard["meta"]["row_count"]
        == row_count
    )
    add_check(
        checks,
        "row_count_reconciliation",
        counts_match,
        f"manifest={manifest['row_count']}, quality={quality['row_count']}, "
        f"dashboard={dashboard['meta']['row_count']}, sqlite={row_count}",
    )
    add_check(
        checks,
        "sql_overview_reconciliation",
        list(overview)
        == [
            dashboard["sql_metrics"]["overview"]["complaint_count"],
            dashboard["sql_metrics"]["overview"]["timely_response_rate"],
            dashboard["sql_metrics"]["overview"]["not_timely_count"],
            dashboard["sql_metrics"]["overview"]["not_timely_rate"],
            dashboard["sql_metrics"]["overview"]["relief_response_rate"],
            dashboard["sql_metrics"]["overview"]["relief_response_count"],
        ],
        str(overview),
    )
    add_check(
        checks,
        "source_hash",
        sha256(ROOT / config["paths"]["sanitized_csv"])
        == manifest["sanitized_csv_sha256"],
        manifest["sanitized_csv_sha256"],
    )
    add_check(
        checks,
        "source_scope",
        manifest["scope"] == config["scope"]
        and manifest["scope"]["date_received_min"] == "2025-01-01"
        and manifest["scope"]["date_received_max_exclusive"] == "2026-01-01",
        json.dumps(manifest["scope"], sort_keys=True),
    )
    add_check(
        checks,
        "temporal_warning_disclosed",
        quality["warnings"]["monthly_volume_anomalies"] == {"2025-01": 18367}
        and 'id="volume-signal"' in html,
        json.dumps(quality["warnings"]["monthly_volume_anomalies"], sort_keys=True),
    )
    add_check(
        checks,
        "source_field_minimization",
        {"state", "tags", "submitted_via"}.isdisjoint(
            manifest["sanitized_columns"]
        ),
        f"sanitized columns={manifest['sanitized_columns']}",
    )
    add_check(
        checks,
        "chartjs_hash",
        sha256(chart) == EXPECTED_CHART_HASH,
        sha256(chart),
    )

    public_columns = set(dashboard["meta"]["record_columns"])
    prohibited_columns = {
        "complaint_id",
        "complaint_what_happened",
        "zip_code",
        "state",
        "tags",
        "submitted_via",
        "route_hours",
        "company_response",
    }
    add_check(
        checks,
        "public_field_minimization",
        public_columns.isdisjoint(prohibited_columns),
        f"public columns={sorted(public_columns)}",
    )
    add_check(
        checks,
        "record_count_reconciliation",
        len(dashboard["records"]) == row_count,
        f"encoded_records={len(dashboard['records'])}",
    )

    record_columns = dashboard["meta"]["record_columns"]

    def public_dimension_counts(dimension: str) -> dict[str, int]:
        dimension_index = record_columns.index(dimension)
        encoded_counts = Counter(
            int(record[dimension_index]) for record in dashboard["records"]
        )
        dictionary = dashboard["dictionaries"][dimension]
        return {
            dictionary[encoded_value]: count
            for encoded_value, count in encoded_counts.items()
        }

    chart_count_dimensions = {
        "received_month": (
            "monthly",
            "received_month",
        ),
        "issue": (
            "issues",
            "issue",
        ),
    }
    chart_count_matches: dict[str, bool] = {}
    for dimension, (metric_name, metric_label) in chart_count_dimensions.items():
        sql_counts = {
            str(row[metric_label]): int(row["complaint_count"])
            for row in dashboard["sql_metrics"][metric_name]
        }
        chart_count_matches[dimension] = public_dimension_counts(dimension) == sql_counts
    add_check(
        checks,
        "chart_dimension_reconciliation",
        all(chart_count_matches.values()),
        json.dumps(chart_count_matches, sort_keys=True),
    )

    month_index = record_columns.index("received_month")
    timely_index = record_columns.index("is_timely")
    month_groups: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for record in dashboard["records"]:
        month_code = int(record[month_index])
        month_groups[month_code][0] += 1
        month_groups[month_code][1] += int(record[timely_index])
    month_dictionary = dashboard["dictionaries"]["received_month"]
    public_not_timely_rates = {
        month_dictionary[month_code]: round(100 * (count - timely) / count, 2)
        for month_code, (count, timely) in month_groups.items()
    }
    sql_not_timely_rates = {
        str(row["received_month"]): float(row["not_timely_rate"])
        for row in dashboard["sql_metrics"]["monthly"]
    }
    add_check(
        checks,
        "monthly_chart_rate_reconciliation",
        public_not_timely_rates == sql_not_timely_rates,
        json.dumps(public_not_timely_rates, sort_keys=True),
    )

    company_index = record_columns.index("company")
    issue_index = record_columns.index("issue")
    january_code = dashboard["dictionaries"]["received_month"].index("2025-01")
    january_records = [
        record
        for record in dashboard["records"]
        if int(record[month_index]) == january_code
    ]
    pair_counts = Counter(
        (int(record[company_index]), int(record[issue_index]))
        for record in january_records
    )
    pair_labels = [
        (
            (
                dashboard["dictionaries"]["company"][company_code],
                dashboard["dictionaries"]["issue"][issue_code],
            ),
            count,
        )
        for (company_code, issue_code), count in pair_counts.most_common(2)
    ]
    expected_pairs = [
        (
            (
                "NAVY FEDERAL CREDIT UNION",
                "Problem caused by your funds being low",
            ),
            6970,
        ),
        (
            (
                "CAPITAL ONE FINANCIAL CORPORATION",
                "Managing an account",
            ),
            4474,
        ),
    ]
    january_residual = len(january_records) - sum(
        count for _, count in pair_labels
    )
    add_check(
        checks,
        "january_driver_reconciliation",
        len(january_records) == 18367
        and pair_labels == expected_pairs
        and january_residual == 6923,
        json.dumps(
            {
                "january_count": len(january_records),
                "top_pairs": pair_labels,
                "residual": january_residual,
            },
            sort_keys=True,
        ),
    )
    add_check(
        checks,
        "issue_filter_contract",
        'id="issue-filter"' in html
        and '["issue-filter", "issue"]' in script.read_text(encoding="utf-8"),
        "issue filter is present and bound to the shared record set",
    )
    add_check(
        checks,
        "content_security_policy",
        "Content-Security-Policy" in html
        and "script-src 'self'" in html
        and "connect-src 'none'" in html,
        "local scripts only; runtime connections disabled",
    )
    add_check(
        checks,
        "direct_open_data_contract",
        dashboard_text.startswith(DASHBOARD_DATA_PREFIX)
        and dashboard_text.endswith(";\n")
        and 'src="./dashboard-data.js"' in html
        and html.index('src="./dashboard-data.js"') < html.index("src=\"./app.js")
        and "fetch(" not in script.read_text(encoding="utf-8"),
        "data asset loads before app.js; no fetch call requires an HTTP server",
    )

    required_assets = [
        ROOT / "docs" / "styles.css",
        ROOT / "docs" / "app.js",
        chart,
        dashboard_path,
    ]
    add_check(
        checks,
        "required_static_assets",
        all(path.is_file() and path.stat().st_size > 0 for path in required_assets),
        ", ".join(f"{path.name}:{path.stat().st_size}" for path in required_assets),
    )

    node = subprocess.run(
        ["node", "--check", str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    add_check(
        checks,
        "javascript_syntax",
        node.returncode == 0,
        node.stderr.strip() or "node --check passed",
    )
    dashboard_node = subprocess.run(
        ["node", "--check", str(dashboard_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    add_check(
        checks,
        "dashboard_data_javascript_syntax",
        dashboard_node.returncode == 0,
        dashboard_node.stderr.strip() or "node --check passed",
    )

    failures = [check for check in checks if not check["passed"]]
    receipt = {
        "verified_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "status": "passed" if not failures else "failed",
        "checks": checks,
        "failure_count": len(failures),
    }
    output = ROOT / "evidence" / "local-verification.json"
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
