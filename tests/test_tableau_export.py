import pandas as pd
import pytest

from complaint_ops.tableau import EXPORT_COLUMNS, prepare_tableau, reconcile
from complaint_ops.quality import DataQualityError


def rows():
    return pd.DataFrame([
        {"complaint_id": i+1, "date_received": day, "product": "Checking or savings account",
         "sub_product": "Checking account", "issue": "Managing an account", "sub_issue": None,
         "company": company, "date_sent_to_company": day, "company_response": response, "timely": timely}
        for i, (day, company, response, timely) in enumerate([
            ("2025-01-02", "A", "Closed with explanation", "No"),
            ("2025-01-03", "B", "Closed with monetary relief", "Yes"),
            ("2025-01-04", "C", "Closed with explanation", "Yes"),
            ("2025-06-02", "A", "Closed with non-monetary relief", "Yes"),
        ])])


def test_privacy_unknown_and_independent_sql():
    source = rows()
    output, _ = prepare_tableau(source)
    assert list(output.columns) == EXPORT_COLUMNS
    assert "complaint_id" not in output and "company_response" not in output
    assert output.sub_issue.tolist() == ["Unknown"] * 4
    assert all(c["passed"] for c in reconcile(source, output))


def test_clusters_deterministic_and_january_only():
    source = rows()
    output, clusters = prepare_tableau(source.sample(frac=1, random_state=7))
    assert [c["company"] for c in clusters] == ["A", "B"]
    assert output.january_top_cluster.tolist() == [1, 1, 0, 0]
    assert len(output) == len(source)  # sensitivity marks, never drops originals


def test_dedicated_timely_flag_not_response_category():
    source = rows()
    source.loc[0, "company_response"] = "Untimely response"
    source.loc[0, "timely"] = "Yes"
    output, _ = prepare_tableau(source)
    assert output.loc[0, "not_timely"] == 0


def test_invalid_timely_rejected():
    source = rows()
    source.loc[0, "timely"] = "Maybe"
    with pytest.raises(DataQualityError):
        prepare_tableau(source)


def test_reconciliation_detects_changed_metric():
    source = rows()
    output, _ = prepare_tableau(source)
    output.loc[0, "not_timely"] = 0
    with pytest.raises(ValueError, match="reconciliation failed"):
        reconcile(source, output)


def test_company_issue_slice_detects_misattributed_company():
    source = rows()
    source.loc[3, "company"] = "CAPITAL ONE FINANCIAL CORPORATION"
    output, _ = prepare_tableau(source)
    checks = reconcile(source, output)
    company_check = next(c for c in checks if c["scope"].startswith("CAPITAL ONE"))
    assert company_check["sql"] == [1, 0, 1]
    # Overall metrics and all previous scopes are unchanged by this defect.
    output.loc[3, "company"] = "A"
    with pytest.raises(ValueError, match="reconciliation failed"):
        reconcile(source, output)
