from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from complaint_ops.pipeline import run_pipeline


@pytest.mark.requirement("R1")
def test_repeated_builds_are_deterministic(
    tmp_path: Path,
    fixture_source: Path,
    make_config,
) -> None:
    first = run_pipeline(make_config(tmp_path / "first"), source=fixture_source)
    second = run_pipeline(make_config(tmp_path / "second"), source=fixture_source)

    assert first["manifest"]["row_count"] == 12
    assert second["manifest"]["row_count"] == 12
    assert (
        first["manifest"]["sanitized_csv_sha256"]
        == second["manifest"]["sanitized_csv_sha256"]
    )
    assert (
        first["dashboard"]["sql_metrics"]
        == second["dashboard"]["sql_metrics"]
    )


@pytest.mark.requirement("R2")
def test_sql_overview_reconciles_to_known_fixture(
    tmp_path: Path,
    fixture_source: Path,
    make_config,
) -> None:
    config = make_config(tmp_path)
    result = run_pipeline(config, source=fixture_source)

    with sqlite3.connect(config.paths.sqlite) as connection:
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

    assert overview == (12, 83.33, 2, 16.67, 50.0, 6)
    assert result["dashboard"]["sql_metrics"]["overview"] == {
        "complaint_count": 12,
        "timely_response_rate": 83.33,
        "not_timely_count": 2,
        "not_timely_rate": 16.67,
        "relief_response_rate": 50.0,
        "relief_response_count": 6,
        "top_three_issue_share": 75.0,
    }


@pytest.mark.requirement("R3")
def test_dashboard_payload_supports_consistent_global_filters(
    tmp_path: Path,
    fixture_source: Path,
    make_config,
) -> None:
    payload = run_pipeline(
        make_config(tmp_path), source=fixture_source
    )["dashboard"]

    assert payload["meta"]["row_count"] == len(payload["records"]) == 12
    assert payload["meta"]["record_columns"] == [
        "received_month",
        "sub_product",
        "issue",
        "sub_issue",
        "company",
        "is_timely",
        "has_relief",
    ]
    assert "2025-01" in payload["dictionaries"]["received_month"]
    assert "Checking account" in payload["dictionaries"]["sub_product"]
    assert "Managing an account" in payload["dictionaries"]["issue"]
    assert "Example Bank A" in payload["dictionaries"]["company"]
    assert sum(
        month["complaint_count"]
        for month in payload["sql_metrics"]["monthly"]
    ) == 12
