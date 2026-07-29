from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess

import pytest


@pytest.mark.requirement("R3")
def test_dashboard_exposes_required_accessible_views(project_root: Path) -> None:
    html = (project_root / "docs" / "index.html").read_text(encoding="utf-8")
    css = (project_root / "docs" / "styles.css").read_text(encoding="utf-8")
    script = (project_root / "docs" / "app.js").read_text(encoding="utf-8")

    for element_id in [
        "month-filter",
        "subproduct-filter",
        "issue-filter",
        "company-filter",
        "volume-chart",
        "exception-chart",
        "issue-chart",
        "relief-chart",
        "issue-detail-table",
        "exception-detail-table",
    ]:
        assert f'id="{element_id}"' in html
    assert html.count('role="img"') == 4
    assert html.count("View chart data") == 4
    for signal_id in [
        "volume-signal",
        "exception-signal",
        "issue-signal",
        "relief-signal",
    ]:
        assert f'id="{signal_id}"' in html
    assert 'aria-live="polite"' in html
    assert 'id="metric-concentration-label"' in html
    assert 'id="issue-chart-title"' in html
    assert 'id="issue-chart-subtitle"' in html
    assert 'state.filters.issue === null ? "issue" : "sub_issue"' in script
    assert 'issueDimension === "issue"' in script
    assert "@media (max-width: 900px)" in css
    assert "@media (max-width: 680px)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert 'addEventListener("reset"' in script
    assert "minimumCount: 100" in script
    assert '"Share of selected complaints"' in script
    assert '"Not-timely response (%)"' in script
    assert '"Published complaints"' in script
    assert "All other issues" in script
    assert "MIN_INTERPRETIVE_COUNT = 30" in script
    assert "Do not generalize this into staffing demand" in script
    assert "Two company-issue clusters contributed" in script


@pytest.mark.requirement("R3")
def test_small_base_interpretation_threshold_is_executable(
    project_root: Path,
) -> None:
    result = subprocess.run(
        [
            "node",
            "-e",
            (
                "const fs=require('fs');const vm=require('vm');"
                "const source=fs.readFileSync('docs/app.js','utf8');"
                "const sandbox={console,Intl,Date,"
                "window:{addEventListener(){}},"
                "document:{addEventListener(){}}};"
                "vm.runInNewContext(source+';this.audit={canInterpret};',sandbox);"
                "if(sandbox.audit.canInterpret(0)||sandbox.audit.canInterpret(1)"
                "||sandbox.audit.canInterpret(29)||!sandbox.audit.canInterpret(30))"
                "process.exit(1);"
            ),
        ],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.requirement("R3")
def test_default_anomaly_and_known_filter_slice_are_reproducible(
    project_root: Path,
) -> None:
    data_text = (project_root / "docs" / "dashboard-data.js").read_text(
        encoding="utf-8"
    )
    prefix = "window.COMPLAINT_DASHBOARD_DATA = "
    payload = json.loads(data_text[len(prefix) : -2])
    columns = payload["meta"]["record_columns"]
    dictionaries = payload["dictionaries"]

    def label(record: list[int], dimension: str) -> str:
        return dictionaries[dimension][record[columns.index(dimension)]]

    january = [
        record
        for record in payload["records"]
        if label(record, "received_month") == "2025-01"
    ]
    pair_counts = Counter(
        (label(record, "company"), label(record, "issue"))
        for record in january
    )
    assert len(january) == 18_367
    assert pair_counts.most_common(2) == [
        (
            (
                "NAVY FEDERAL CREDIT UNION",
                "Problem caused by your funds being low",
            ),
            6_970,
        ),
        (
            (
                "CAPITAL ONE FINANCIAL CORPORATION",
                "Managing an account",
            ),
            4_474,
        ),
    ]
    assert len(january) - sum(count for _, count in pair_counts.most_common(2)) == 6_923

    expected = {
        "received_month": "2025-01",
        "sub_product": "Checking account",
        "issue": "Managing an account",
        "company": "BANK OF AMERICA, NATIONAL ASSOCIATION",
    }
    filtered = [
        record
        for record in payload["records"]
        if all(label(record, dimension) == value for dimension, value in expected.items())
    ]
    assert len(filtered) == 281


@pytest.mark.requirement("R6")
def test_client_ready_delivery_set_is_present(project_root: Path) -> None:
    required = [
        "README.md",
        "delivery/business-case.md",
        "delivery/requirements.md",
        "delivery/architecture.md",
        "delivery/methodology.md",
        "delivery/security-privacy.md",
        "delivery/findings.md",
        "delivery/test-traceability.md",
        "delivery/delivery-evidence.md",
        "delivery/ai-assistance.md",
        "delivery/demo-script.md",
        ".github/workflows/ci.yml",
        ".github/workflows/deploy-pages.yml",
    ]
    missing = [path for path in required if not (project_root / path).is_file()]
    assert not missing, f"Missing delivery artifacts: {missing}"

    requirements = (project_root / "delivery" / "requirements.md").read_text(
        encoding="utf-8"
    )
    for requirement_id in [f"R{number}" for number in range(1, 7)]:
        assert f"## {requirement_id} " in requirements

    pages_workflow = (
        project_root / ".github" / "workflows" / "deploy-pages.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in pages_workflow
    assert "push:" not in pages_workflow
    assert "needs: quality" in pages_workflow
    assert "python-version: \"3.12\"" in pages_workflow
    assert "run: pytest" in pages_workflow
    assert "node --check docs/app.js" in pages_workflow
    assert "node --check docs/dashboard-data.js" in pages_workflow


@pytest.mark.requirement("R6")
def test_dashboard_direct_open_contract(project_root: Path) -> None:
    html = (project_root / "docs" / "index.html").read_text(encoding="utf-8")
    app = (project_root / "docs" / "app.js").read_text(encoding="utf-8")
    data_asset = project_root / "docs" / "dashboard-data.js"

    assert data_asset.is_file()
    assert 'src="./dashboard-data.js"' in html
    assert html.index('src="./dashboard-data.js"') < html.index('src="./app.js')
    assert "fetch(" not in app

    result = subprocess.run(
        [
            "node",
            "-e",
            (
                "global.window = {};"
                "require('./docs/dashboard-data.js');"
                "const data = window.COMPLAINT_DASHBOARD_DATA;"
                "if (!data || data.meta.row_count !== 84194 || "
                "data.records.length !== 84194) process.exit(1);"
            ),
        ],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
