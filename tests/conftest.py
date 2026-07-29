from __future__ import annotations

from pathlib import Path

import pytest

from complaint_ops.config import PipelineConfig, ProjectPaths, load_config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SOURCE = PROJECT_ROOT / "tests" / "fixtures" / "complaints.csv"


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def fixture_source() -> Path:
    return FIXTURE_SOURCE


@pytest.fixture
def make_config():
    base = load_config(PROJECT_ROOT / "config" / "pipeline.json")

    def factory(output_root: Path) -> PipelineConfig:
        return PipelineConfig(
            root=PROJECT_ROOT,
            source=base.source,
            scope=base.scope,
            paths=ProjectPaths(
                sanitized_csv=output_root / "data" / "raw" / "complaints.csv",
                sqlite=output_root / "data" / "processed" / "complaints.db",
                quality_report=output_root / "evidence" / "quality.json",
                source_manifest=output_root / "evidence" / "manifest.json",
                dashboard_data=output_root / "docs" / "dashboard-data.js",
            ),
        )

    return factory
