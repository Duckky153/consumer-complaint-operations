from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Scope:
    date_received_min: str
    date_received_max_exclusive: str
    product: str


@dataclass(frozen=True)
class ProjectPaths:
    sanitized_csv: Path
    sqlite: Path
    quality_report: Path
    source_manifest: Path
    dashboard_data: Path


@dataclass(frozen=True)
class PipelineConfig:
    root: Path
    source: dict[str, str]
    scope: Scope
    paths: ProjectPaths


def load_config(path: Path) -> PipelineConfig:
    """Load and resolve the checked-in pipeline contract."""
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    root = path.resolve().parent.parent
    scope = Scope(**raw["scope"])
    project_paths = ProjectPaths(
        **{name: root / value for name, value in raw["paths"].items()}
    )
    return PipelineConfig(
        root=root,
        source=dict(raw["source"]),
        scope=scope,
        paths=project_paths,
    )

