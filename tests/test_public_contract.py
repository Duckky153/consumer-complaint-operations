from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from complaint_ops.pipeline import DASHBOARD_DATA_PREFIX, run_pipeline


def read_dashboard_script(path: Path) -> tuple[str, dict]:
    script = path.read_text(encoding="utf-8")
    assert script.startswith(DASHBOARD_DATA_PREFIX)
    assert script.endswith(";\n")
    return script, json.loads(script[len(DASHBOARD_DATA_PREFIX) : -2])


@pytest.mark.requirement("R5")
def test_public_payload_excludes_unnecessary_sensitive_fields(
    tmp_path: Path,
    fixture_source: Path,
    make_config,
) -> None:
    config = make_config(tmp_path)
    run_pipeline(config, source=fixture_source)
    payload_text, payload = read_dashboard_script(config.paths.dashboard_data)

    prohibited = [
        "complaint_id",
        "complaint_what_happened",
        "consumer complaint narrative",
        "zip_code",
        "ZIP code",
        "state",
        "tags",
        "submitted_via",
        "route_hours",
        "company_response",
    ]
    for term in prohibited:
        assert term not in payload_text
    assert {"state", "tags", "submitted_via"}.isdisjoint(
        config.paths.sanitized_csv.read_text(encoding="utf-8").splitlines()[0].split(",")
    )
    assert len(payload["records"]) == 12


@pytest.mark.requirement("R5")
def test_public_page_has_no_runtime_third_party_dependencies(
    project_root: Path,
) -> None:
    html = (project_root / "docs" / "index.html").read_text(encoding="utf-8")
    script = (project_root / "docs" / "app.js").read_text(encoding="utf-8")

    assert 'src="./vendor/chart.umd.min.js"' in html
    assert 'src="./dashboard-data.js"' in html
    assert re.search(r'src="\./app\.js(?:\?[^"]+)?"', html)
    assert re.search(r'href="\./styles\.css(?:\?[^"]+)?"', html)
    assert "Content-Security-Policy" in html
    assert "script-src 'self'" in html
    assert "connect-src 'none'" in html
    assert html.index('src="./dashboard-data.js"') < html.index("src=\"./app.js")
    assert "fetch(" not in script
    assert "window.COMPLAINT_DASHBOARD_DATA" in script
    assert "innerHTML" not in script
    assert "eval(" not in script
    assert (project_root / "docs" / "vendor" / "chart.umd.min.js").is_file()
    assert (project_root / "docs" / "vendor" / "Chart.js-LICENSE.md").is_file()


@pytest.mark.requirement("R6")
def test_public_page_links_to_the_project_source_code(project_root: Path) -> None:
    html = (project_root / "docs" / "index.html").read_text(encoding="utf-8")
    css = (project_root / "docs" / "styles.css").read_text(encoding="utf-8")

    assert 'href="https://github.com/Duckky153/consumer-complaint-operations"' in html
    assert "View source code on GitHub" in html
    assert 'class="github-mark"' in html
    assert ".footer-source-link" in css
