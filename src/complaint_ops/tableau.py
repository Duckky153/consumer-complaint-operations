"""Minimized Tableau export from the pinned, already-sanitized CFPB snapshot."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pandas as pd

from .pipeline import normalize
from .quality import assess_quality

PINNED_SHA256 = "964912efdcfe70f2376591d40781f64832e879c73ff7d629fdadb6115541053b"
EXPORT_COLUMNS = ["date_received", "received_month", "sub_product", "issue", "sub_issue",
                  "company", "complaint_count", "not_timely", "has_relief", "january_top_cluster"]


def prepare_tableau(source: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    frame = normalize(source)
    assess_quality(frame, expected_product="Checking or savings account",
                   start=pd.Timestamp("2025-01-01", tz="UTC"),
                   end_exclusive=pd.Timestamp("2026-01-01", tz="UTC"))
    january = frame.loc[frame.received_month.eq("2025-01")]
    clusters = (january.groupby(["company", "issue"], dropna=False).size()
                .reset_index(name="complaints")
                .sort_values(["complaints", "company", "issue"], ascending=[False, True, True])
                .head(2))
    keys = set(zip(clusters.company, clusters.issue))
    result = frame.loc[:, ["date_received", "received_month", "sub_product", "issue", "sub_issue", "company"]].copy()
    result["date_received"] = result.date_received.dt.strftime("%Y-%m-%d")
    for field in ["sub_product", "issue", "sub_issue", "company"]:
        result[field] = result[field].fillna("Unknown")
    result["complaint_count"] = 1
    result["not_timely"] = 1 - frame.is_timely
    result["has_relief"] = frame.has_relief
    result["january_top_cluster"] = [int(month == "2025-01" and (company, issue) in keys)
                                    for month, company, issue in zip(frame.received_month, frame.company, frame.issue)]
    return result[EXPORT_COLUMNS], clusters.to_dict(orient="records")


def reconcile(source: pd.DataFrame, exported: pd.DataFrame) -> list[dict]:
    # Independently derive the reference from sanitized source fields in SQL.
    cases = [
        ("all", "1=1", pd.Series(True, index=exported.index)),
        ("Managing an account", "issue='Managing an account'", exported.issue.eq("Managing an account")),
        ("June", "substr(date_received,1,7)='2025-06'", exported.received_month.eq("2025-06")),
        ("Checking account / Managing an account", "sub_product='Checking account' AND issue='Managing an account'",
         exported.sub_product.eq("Checking account") & exported.issue.eq("Managing an account")),
        ("Exclude January", "substr(date_received,1,7)<>'2025-01'", exported.received_month.ne("2025-01")),
        ("Exclude January top two clusters", "NOT (substr(date_received,1,7)='2025-01' AND (company,issue) IN (SELECT company,issue FROM raw WHERE substr(date_received,1,7)='2025-01' GROUP BY company,issue ORDER BY count(*) DESC,company,issue LIMIT 2))", exported.january_top_cluster.eq(0)),
    ]
    checks = []
    with sqlite3.connect(":memory:") as connection:
        source.to_sql("raw", connection, index=False)
        for label, condition, mask in cases:
            expected = connection.execute(f"SELECT count(*), coalesce(sum(timely='No'),0), coalesce(sum(company_response IN ('Closed with monetary relief','Closed with non-monetary relief')),0) FROM raw WHERE {condition}").fetchone()
            selected = exported.loc[mask]
            actual = (len(selected), int(selected.not_timely.sum()), int(selected.has_relief.sum()))
            checks.append({"scope": label, "sql": list(expected), "export": list(actual), "passed": expected == actual})
    if not all(check["passed"] for check in checks):
        raise ValueError("SQL/export reconciliation failed")
    return checks


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source_path = root / "data/raw/complaints_2025_checking_savings.csv"
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if digest != PINNED_SHA256:
        raise ValueError("Snapshot differs from pinned source; review lineage before replacing it")
    source = pd.read_csv(source_path, dtype={"complaint_id": "Int64"})
    result, clusters = prepare_tableau(source)
    output = root / "data/processed/tableau-complaints.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, lineterminator="\n")
    reread = pd.read_csv(output)
    checks = reconcile(source, reread)
    evidence = {"phase": "Tableau data foundation; native workbook not yet built", "source_sha256": digest,
                "export_sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "rows": len(result),
                "fields": EXPORT_COLUMNS, "grain": "one published complaint; original ID excluded",
                "january_clusters": clusters, "january_cluster_rows": int(result.january_top_cluster.sum()),
                "cohort_metric_order": ["complaints", "not_timely", "reported_relief"], "checks": checks,
                "passed": all(check["passed"] for check in checks)}
    (root / "evidence/tableau-data-verification.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"rows": len(result), "passed_cohorts": len(checks), "january_cluster_rows": evidence["january_cluster_rows"]}))


if __name__ == "__main__":
    main()
