# Requirement-to-Test Traceability

Automated tests use `@pytest.mark.requirement("R#")`. The mapping below keeps
the acceptance criteria visible instead of treating a green test count as
complete evidence by itself.

| Requirement | Automated evidence | What it proves | Additional local gate |
|---|---|---|---|
| R1 — Reproducible pipeline | `test_repeated_builds_are_deterministic` | Same fixture rows produce the same sanitized hash and SQL metrics; all build artifacts are created | Real API build and manifest review |
| R2 — Diagnostic summary | `test_sql_overview_reconciles_to_known_fixture` | Exception, reported-relief, and volume definitions reconcile to known fixture results and SQLite | Real-data SQL-to-dashboard reconciliation |
| R3 — Trends, drivers, filters | `test_dashboard_payload_supports_consistent_global_filters`; `test_dashboard_exposes_required_accessible_views`; `test_small_base_interpretation_threshold_is_executable`; `test_default_anomaly_and_known_filter_slice_are_reproducible` | Public data has the required filter dimensions; HTML has four decision-relevant charts; the 30-row interpretation gate executes; January's two leading clusters and the 281-row four-filter slice reproduce exactly | Real-browser default, issue, multi-filter, small-base, empty, and reset exercise at three widths |
| R4 — Data quality | `test_quality_gate_rejects_duplicate_complaint_grain`; `test_quality_gate_rejects_out_of_scope_dates`; `test_quality_gate_rejects_negative_routing_time`; `test_optional_issue_null_is_disclosed_not_imputed`; `test_monthly_volume_spike_is_disclosed_as_warning` | Critical defects stop the build while expected sparsity and unusual monthly volume remain visible | Review real 84,194-row quality report |
| R5 — Privacy/security | `test_public_payload_excludes_unnecessary_sensitive_fields`; `test_public_page_has_no_runtime_third_party_dependencies` | Public data excludes IDs, free text, exact routing time, and raw response category; runtime assets are local; runtime connections are disabled; CSP and safe DOM rules exist | Source scan, vendored hash check, browser network inspection |
| R6 — Delivery/handoff | `test_client_ready_delivery_set_is_present`; `test_dashboard_direct_open_contract` | Named deliverables and manual-only deployment gate are present; generated data is executable, loads before the app, and requires no HTTP fetch | Pytest, JS syntax, local verifier, browser screenshots, link and overflow checks |

## Commands

```bash
.venv/bin/pytest -ra
node --check docs/app.js
.venv/bin/python scripts/verify_delivery.py
```

## Why some gates remain browser-based

Source-level tests can prove that breakpoints, accessible labels, filter code,
and local assets exist. They cannot prove actual browser geometry or rendered
Chart.js output. R6 therefore requires real-browser checks at 360, 768, and
1440 CSS pixels in addition to pytest.

## Publication gate

CI and Pages workflows are prepared, but the Pages workflow is manual-only.
No public CI run, repository, deployment, or URL can be claimed until the owner
approves publication and the resulting external evidence is verified.
