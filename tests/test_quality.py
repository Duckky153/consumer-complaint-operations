from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from complaint_ops.pipeline import load_source, normalize
from complaint_ops.quality import DataQualityError, assess_quality


def quality(frame: pd.DataFrame):
    return assess_quality(
        frame,
        expected_product="Checking or savings account",
        start=pd.Timestamp("2025-01-01", tz="UTC"),
        end_exclusive=pd.Timestamp("2026-01-01", tz="UTC"),
    )


@pytest.mark.requirement("R4")
def test_quality_gate_rejects_duplicate_complaint_grain(
    fixture_source: Path,
) -> None:
    frame = normalize(load_source(fixture_source))
    duplicate = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)

    with pytest.raises(DataQualityError, match="duplicate_complaint_ids"):
        quality(duplicate)


@pytest.mark.requirement("R4")
def test_quality_gate_rejects_out_of_scope_dates(
    fixture_source: Path,
) -> None:
    frame = normalize(load_source(fixture_source))
    frame.loc[0, "date_received"] = pd.Timestamp("2026-01-01", tz="UTC")

    with pytest.raises(DataQualityError, match="outside_date_window"):
        quality(frame)


@pytest.mark.requirement("R4")
def test_optional_issue_null_is_disclosed_not_imputed(
    fixture_source: Path,
) -> None:
    frame = normalize(load_source(fixture_source))
    frame.loc[0, "issue"] = pd.NA

    result = quality(frame)

    assert result.status == "passed"
    assert result.report["warnings"]["missing_issue"] == 1
    assert result.report["completeness"]["issue"]["null_count"] == 1


@pytest.mark.requirement("R4")
def test_quality_gate_rejects_negative_routing_time(
    fixture_source: Path,
) -> None:
    frame = normalize(load_source(fixture_source))
    frame.loc[0, "route_hours"] = -1

    with pytest.raises(DataQualityError, match="negative_route_hours"):
        quality(frame)


@pytest.mark.requirement("R4")
def test_monthly_volume_spike_is_disclosed_as_warning(
    fixture_source: Path,
) -> None:
    frame = normalize(load_source(fixture_source))
    spike = frame.iloc[[0]].copy()
    spike.loc[:, "complaint_id"] = 9001
    frame = pd.concat([frame, spike], ignore_index=True)

    result = quality(frame)

    assert result.status == "passed_with_warnings"
    assert result.report["warnings"]["monthly_volume_anomalies"] == {
        "2025-01": 3
    }
