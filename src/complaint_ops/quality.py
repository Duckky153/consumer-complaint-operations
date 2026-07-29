from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = (
    "complaint_id",
    "date_received",
    "product",
    "company",
    "company_response",
    "timely",
)

EXPECTED_COLUMNS = REQUIRED_COLUMNS + ("issue",)


class DataQualityError(RuntimeError):
    """Raised when a stable, decision-critical data contract fails."""


@dataclass(frozen=True)
class QualityResult:
    status: str
    report: dict[str, Any]


def _rate(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def assess_quality(
    frame: pd.DataFrame,
    *,
    expected_product: str,
    start: pd.Timestamp,
    end_exclusive: pd.Timestamp,
) -> QualityResult:
    """Profile the normalized complaint grain and enforce stable contracts."""
    row_count = len(frame)
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    if missing_columns:
        raise DataQualityError(f"Missing required columns: {missing_columns}")

    duplicate_ids = int(frame["complaint_id"].duplicated(keep=False).sum())
    null_counts = {
        column: int(frame[column].isna().sum()) for column in REQUIRED_COLUMNS
    }
    wrong_product = int(frame["product"].ne(expected_product).sum())
    out_of_window = int(
        (
            frame["date_received"].lt(start)
            | frame["date_received"].ge(end_exclusive)
        ).sum()
    )
    invalid_timely = int((~frame["timely"].isin(["Yes", "No"])).sum())
    negative_route = int(frame["route_hours"].lt(0).fillna(False).sum())
    missing_sent_date = int(frame["date_sent_to_company"].isna().sum())
    monthly_counts = (
        frame.groupby("received_month", dropna=True)
        .size()
        .sort_index()
        .astype(int)
    )
    monthly_median = (
        float(monthly_counts.median()) if not monthly_counts.empty else 0.0
    )
    monthly_volume_anomalies = {
        str(month): int(count)
        for month, count in monthly_counts.items()
        if monthly_median and count > 2 * monthly_median
    }

    critical_failures = {
        "duplicate_complaint_ids": duplicate_ids,
        "required_nulls": sum(null_counts.values()),
        "wrong_product": wrong_product,
        "outside_date_window": out_of_window,
        "invalid_timely_values": invalid_timely,
        "negative_route_hours": negative_route,
    }
    failed = {key: value for key, value in critical_failures.items() if value}

    completeness = {
        column: {
            "null_count": int(frame[column].isna().sum()),
            "null_rate": _rate(int(frame[column].isna().sum()), row_count),
        }
        for column in frame.columns
        if column not in {"is_timely", "has_relief"}
    }

    report: dict[str, Any] = {
        "dataset_grain": "one published CFPB complaint per complaint_id",
        "row_count": row_count,
        "column_count": len(frame.columns),
        "date_received_min": (
            frame["date_received"].min().isoformat() if row_count else None
        ),
        "date_received_max": (
            frame["date_received"].max().isoformat() if row_count else None
        ),
        "distinct_companies": int(frame["company"].nunique(dropna=True)),
        "distinct_issues": int(frame["issue"].nunique(dropna=True)),
        "critical_checks": {
            **critical_failures,
            "status": "failed" if failed else "passed",
        },
        "warnings": {
            "missing_date_sent_to_company": missing_sent_date,
            "missing_issue": int(frame["issue"].isna().sum()),
            "monthly_volume_anomalies": monthly_volume_anomalies,
        },
        "temporal_profile": {
            "monthly_complaint_counts": {
                str(month): int(count)
                for month, count in monthly_counts.items()
            },
            "median_monthly_complaints": monthly_median,
            "anomaly_rule": "month count greater than 2x the calendar-year monthly median",
        },
        "completeness": completeness,
        "interpretation": (
            (
                "The dataset is safe for the documented aggregate use, with "
                "the reported temporal warning kept visible."
                if monthly_volume_anomalies
                else "The dataset is safe for the documented aggregate use."
            )
            if not failed
            else "The dataset is not safe for dashboard publication."
        ),
    }
    if failed:
        raise DataQualityError(f"Critical data-quality checks failed: {failed}")

    status = (
        "passed_with_warnings"
        if missing_sent_date or monthly_volume_anomalies
        else "passed"
    )
    report["status"] = status
    return QualityResult(status=status, report=report)
