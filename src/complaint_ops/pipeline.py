from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pandas as pd

from .config import PipelineConfig
from .quality import QualityResult, assess_quality


SOURCE_COLUMNS = {
    "Date received": "date_received",
    "Product": "product",
    "Sub-product": "sub_product",
    "Issue": "issue",
    "Sub-issue": "sub_issue",
    "Company": "company",
    "Date sent to company": "date_sent_to_company",
    "Company response to consumer": "company_response",
    "Timely response?": "timely",
    "Complaint ID": "complaint_id",
}

TEXT_COLUMNS = (
    "product",
    "sub_product",
    "issue",
    "sub_issue",
    "company",
    "company_response",
    "timely",
)

RELIEF_RESPONSES = {
    "Closed with monetary relief",
    "Closed with non-monetary relief",
}

DASHBOARD_DATA_PREFIX = "window.COMPLAINT_DASHBOARD_DATA = "


def build_export_url(config: PipelineConfig) -> str:
    # The live export currently treats date_received_max as an inclusive
    # calendar date, despite older schema wording that describes it as "< max".
    api_max_inclusive = (
        date.fromisoformat(config.scope.date_received_max_exclusive)
        - timedelta(days=1)
    ).isoformat()
    query = urlencode(
        {
            "date_received_min": config.scope.date_received_min,
            "date_received_max": api_max_inclusive,
            "product": config.scope.product,
            "field": "all",
            "format": "csv",
        }
    )
    return f"{config.source['endpoint']}?{query}"


def load_source(source: str | Path) -> pd.DataFrame:
    """Read only allowlisted CFPB columns; narratives and ZIP codes never enter the frame."""
    return pd.read_csv(
        source,
        usecols=list(SOURCE_COLUMNS),
        dtype="string",
        keep_default_na=True,
    ).rename(columns=SOURCE_COLUMNS)


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize source types at the one-complaint grain."""
    normalized = frame.copy()
    for column in TEXT_COLUMNS:
        normalized[column] = normalized[column].str.strip()
        normalized[column] = normalized[column].replace("", pd.NA)

    normalized["complaint_id"] = pd.to_numeric(
        normalized["complaint_id"], errors="coerce"
    ).astype("Int64")
    normalized["date_received"] = pd.to_datetime(
        normalized["date_received"], utc=True, errors="coerce"
    )
    normalized["date_sent_to_company"] = pd.to_datetime(
        normalized["date_sent_to_company"], utc=True, errors="coerce"
    )
    normalized["route_hours"] = (
        normalized["date_sent_to_company"] - normalized["date_received"]
    ).dt.total_seconds() / 3600
    normalized["received_month"] = normalized["date_received"].dt.strftime("%Y-%m")
    normalized["is_timely"] = normalized["timely"].eq("Yes").astype("int8")
    normalized["has_relief"] = (
        normalized["company_response"].isin(RELIEF_RESPONSES).astype("int8")
    )
    normalized = normalized.sort_values("complaint_id", kind="stable").reset_index(
        drop=True
    )
    return normalized


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_dashboard_script(path: Path, payload: dict[str, Any]) -> None:
    """Write public data as an executable local asset for file:// and HTTP use."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    path.write_text(
        f"{DASHBOARD_DATA_PREFIX}{serialized};\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_sanitized_csv(frame: pd.DataFrame, path: Path) -> None:
    safe = frame[
        [
            "complaint_id",
            "date_received",
            "product",
            "sub_product",
            "issue",
            "sub_issue",
            "company",
            "date_sent_to_company",
            "company_response",
            "timely",
        ]
    ].copy()
    safe["date_received"] = safe["date_received"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    safe["date_sent_to_company"] = safe["date_sent_to_company"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    safe.to_csv(path, index=False, lineterminator="\n")


def build_sqlite(frame: pd.DataFrame, path: Path, metrics_sql: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    sqlite_frame = frame.copy()
    sqlite_frame["date_received"] = sqlite_frame["date_received"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    sqlite_frame["date_sent_to_company"] = sqlite_frame[
        "date_sent_to_company"
    ].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    with sqlite3.connect(path) as connection:
        sqlite_frame.to_sql("complaints", connection, index=False, if_exists="replace")
        connection.executescript(
            """
            CREATE UNIQUE INDEX idx_complaints_id ON complaints(complaint_id);
            CREATE INDEX idx_complaints_month ON complaints(received_month);
            CREATE INDEX idx_complaints_company ON complaints(company);
            CREATE INDEX idx_complaints_issue ON complaints(issue);
            CREATE INDEX idx_complaints_subproduct ON complaints(sub_product);
            """
        )
        connection.executescript(metrics_sql.read_text(encoding="utf-8"))


def _query_records(connection: sqlite3.Connection, view: str) -> list[dict[str, Any]]:
    cursor = connection.execute(f"SELECT * FROM {view}")
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _display_value(value: object) -> str:
    return "Not specified" if pd.isna(value) else str(value)


def build_dashboard_payload(
    frame: pd.DataFrame,
    *,
    database: Path,
    config: PipelineConfig,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    with sqlite3.connect(database) as connection:
        overview = _query_records(connection, "metric_overview")[0]
        monthly = _query_records(connection, "metric_monthly")
        issues = _query_records(connection, "metric_issues")
        subproducts = _query_records(connection, "metric_subproducts")
        companies = _query_records(connection, "metric_companies")
        issue_detail = _query_records(connection, "metric_issue_detail")

    dictionaries: dict[str, list[str]] = {}
    dictionary_columns = (
        "received_month",
        "sub_product",
        "issue",
        "sub_issue",
        "company",
    )
    encoded_columns: dict[str, dict[str, int]] = {}
    for column in dictionary_columns:
        values = sorted(
            value
            for value in frame[column].fillna("Not specified").unique().tolist()
            if isinstance(value, str)
        )
        dictionaries[column] = values
        encoded_columns[column] = {value: index for index, value in enumerate(values)}

    records: list[list[int | float | None]] = []
    for row in frame.itertuples(index=False):
        values = {
            "received_month": _display_value(row.received_month),
            "sub_product": _display_value(row.sub_product),
            "issue": _display_value(row.issue),
            "sub_issue": _display_value(row.sub_issue),
            "company": _display_value(row.company),
        }
        records.append(
            [
                encoded_columns[column][values[column]]
                for column in dictionary_columns
            ]
            + [
                int(row.is_timely),
                int(row.has_relief),
            ]
        )

    top_three_count = sum(int(item["complaint_count"]) for item in issues[:3])
    overview["top_three_issue_share"] = round(
        100 * top_three_count / len(frame), 2
    )

    return {
        "meta": {
            "title": "Consumer Complaint Operations Dashboard",
            "source_name": config.source["name"],
            "source_url": config.source["database_page"],
            "source_license": config.source["license"],
            "scope": {
                "date_received_min": config.scope.date_received_min,
                "date_received_max_exclusive": config.scope.date_received_max_exclusive,
                "product": config.scope.product,
            },
            "generated_at": manifest["generated_at"],
            "source_sha256": manifest["sanitized_csv_sha256"],
            "row_count": len(frame),
            "record_columns": [
                *dictionary_columns,
                "is_timely",
                "has_relief",
            ],
        },
        "sql_metrics": {
            "overview": overview,
            "monthly": monthly,
            "issues": issues,
            "subproducts": subproducts,
            "companies": companies,
            "issue_detail": issue_detail,
        },
        "dictionaries": dictionaries,
        "records": records,
    }


def run_pipeline(
    config: PipelineConfig,
    *,
    source: str | Path | None = None,
) -> dict[str, Any]:
    """Build sanitized data, quality evidence, SQLite metrics, and dashboard data."""
    source_location: str | Path = source or build_export_url(config)
    source_frame = load_source(source_location)
    frame = normalize(source_frame)
    quality: QualityResult = assess_quality(
        frame,
        expected_product=config.scope.product,
        start=pd.Timestamp(config.scope.date_received_min, tz="UTC"),
        end_exclusive=pd.Timestamp(
            config.scope.date_received_max_exclusive, tz="UTC"
        ),
    )

    write_sanitized_csv(frame, config.paths.sanitized_csv)
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    manifest: dict[str, Any] = {
        "generated_at": generated_at,
        "source_endpoint": config.source["endpoint"],
        "source_request": str(source_location),
        "scope": {
            "date_received_min": config.scope.date_received_min,
            "date_received_max_exclusive": config.scope.date_received_max_exclusive,
            "product": config.scope.product,
        },
        "row_count": len(frame),
        "sanitized_columns": list(SOURCE_COLUMNS.values()),
        "excluded_public_fields": [
            "Consumer complaint narrative",
            "ZIP code",
            "Company public response",
            "State",
            "Tags",
            "Submitted via",
            "Date sent to company / route hours",
            "Company response to consumer (raw category)",
        ],
        "sanitized_csv_sha256": _sha256(config.paths.sanitized_csv),
        "quality_status": quality.status,
    }
    _write_json(config.paths.source_manifest, manifest)
    _write_json(config.paths.quality_report, quality.report)

    build_sqlite(frame, config.paths.sqlite, config.root / "sql" / "metrics.sql")
    dashboard_payload = build_dashboard_payload(
        frame,
        database=config.paths.sqlite,
        config=config,
        manifest=manifest,
    )
    _write_dashboard_script(config.paths.dashboard_data, dashboard_payload)
    return {
        "manifest": manifest,
        "quality": quality.report,
        "dashboard": dashboard_payload,
    }
