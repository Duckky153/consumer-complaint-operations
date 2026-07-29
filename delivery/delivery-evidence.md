# Delivery Evidence

## Release state

**Source candidate:** local commit `38aa385`, fully verified  
**Public repository:** publication approved; URL verification in progress  
**GitHub Pages:** deployment approved; URL verification in progress

Publication was explicitly approved after the local quality and browser gates
passed. The public history excludes private interview and résumé-preparation
material.

## Completion audit against the requested delivery

| Requested outcome | Authoritative evidence | Status |
|---|---|---|
| Business case and intended user | `delivery/business-case.md` | Local pass |
| Approximately six requirements with acceptance criteria | Six requirements in `delivery/requirements.md` | Local pass |
| Process and data-flow diagrams | Two Mermaid diagrams in `delivery/architecture.md` | Local pass |
| Reproducible data pipeline | `config/pipeline.json`, `scripts/build_dashboard.py`, `src/complaint_ops/`, and deterministic fixture test | Local pass |
| Data-quality controls | `src/complaint_ops/quality.py` plus real quality report | Local pass |
| SQL metrics | Seven checked-in views in `sql/metrics.sql` | Local pass |
| Responsive black-and-white dashboard | `docs/` plus three reviewed browser screenshots | Local pass |
| Tests mapped to requirements | 15 pytest cases marked R1–R6 and `delivery/test-traceability.md` | Local pass |
| Methodology and analytical limitations | `delivery/methodology.md` | Local pass |
| Executive findings and recommendations | `delivery/findings.md` with SQLite-reconciled figures | Local pass |
| Clean README and delivery evidence | `README.md` and this document | Local pass |
| Security and privacy considerations | Field allowlist, minimized public data asset, CSP, vendored dependency, and `delivery/security-privacy.md` | Local pass |
| AI-assistance disclosure | `delivery/ai-assistance.md` | Local pass |
| Two-minute demo | `delivery/demo-script.md` | Local pass |
| Privacy-clean public history | Operator instructions, private interview preparation, and résumé preparation are absent | Prepared; verification pending |
| Python/pandas/SQLite/pytest/HTML/CSS/JS/Chart.js | Runtime, source, tests, assets, and version evidence | Local pass |
| GitHub Actions and Pages | CI plus manual deployment workflow; deployment depends on a fresh quality job | Prepared; verification pending |
| Public repository and live dashboard | Owner approval is recorded; push, CI, Pages, and URL checks remain | In progress |

The local scope is complete. Publication evidence will be recorded only after
the repository, CI, deployment, and live dashboard have been checked.

## Source evidence

- Controlling source: CFPB Consumer Complaint Database API
- Scope: checking or savings account complaints received in calendar year 2025
- Final row count: 84,194
- Sanitized CSV SHA-256:
  `964912efdcfe70f2376591d40781f64832e879c73ff7d629fdadb6115541053b`
- Source manifest: `evidence/source-manifest.json`
- Data-quality report: `evidence/data-quality-report.json`
- SQLite metrics: `data/processed/complaints.db` and `sql/metrics.sql`

## Data and metric evidence

- Real-data build completed with quality status `passed_with_warnings`.
- Critical checks: zero duplicate IDs, zero required nulls, zero wrong-product
  rows, zero out-of-window rows, zero invalid timely values, and zero negative
  source chronology intervals.
- Fifty-one missing sub-issue values are reported rather than filled.
- January's 18,367 complaints exceed twice the 6,108.5 monthly median. The
  month is retained and disclosed rather than deleted or called seasonal. Two
  company-issue clusters explain 11,444 complaints (62.3%); the residual is
  6,923, or 1.14 times the February–December median.
- Baseline SQL metrics reconcile to 84,194 rows.
- Consumer narratives, ZIP codes, state, tags, submission channel, and company
  public-response prose never enter the ingested frame.
- The public data asset omits complaint IDs, exact source chronology, and raw
  response categories. Its seven encoded record fields are only those required
  for browser filtering and the visible metrics.

## Automated release gates

Recorded on 2026-07-28 EDT:

| Gate | Result | Evidence |
|---|---|---|
| Requirement-linked pytest suite | Passed | 15 tests passed; tests carry R1–R6 markers |
| JavaScript syntax | Passed | `node --check docs/app.js` and `node --check docs/dashboard-data.js` |
| Local delivery verifier | Passed | 20 checks, zero failures in `evidence/local-verification.json` |
| SQL reconciliation | Passed | `(84,194 complaints; 609 not timely; 0.72% exception rate; 12,977 reported relief; 15.41% relief share)` |
| Chart-source reconciliation | Passed | public month, issue-detail, and 12 monthly not-timely outputs match the SQLite views |
| January sensitivity reconciliation | Passed | two leading company-issue pairs total 11,444; residual 6,923; all figures match SQLite |
| Secret scan | Passed | gitleaks scanned the tracked history and found no leaks |
| Field minimization | Passed | state, tags, and submission channel are excluded at ingestion; the public data asset contains seven filter/metric fields and no complaint IDs, exact chronology, or raw response categories |
| Temporal anomaly disclosure | Passed | January 2025 appears in the quality report and the dashboard warning |
| Interpretation guardrails | Passed | issue drill-down, 30-row minimum, anomaly decomposition, non-directional relief wording, and company-ranking warning are executable |
| Direct-open data contract | Passed | generated data is executable JavaScript, loads before `app.js`, contains all 84,194 records, and the application contains no `fetch()` call |
| Runtime dependency check | Passed | Chart.js, CSS, JavaScript, and dashboard data are local; CSP disables runtime connections |
| Public-page branding scan | Passed | no Deloitte name or branding appears in `docs/` |
| Deployment gate contract | Passed | manual dispatch only; deployment depends on a fresh pytest and JavaScript quality job |
| Diff whitespace check | Passed | `git diff --check` returned clean |

## Real-browser acceptance evidence

The dashboard was exercised in two real browser surfaces against a local HTTP
server using the real 84,194-record output. Functional filter checks were
repeated after the content audit, and Chrome produced the final visual evidence.

The first owner handoff also exposed an important usability failure: opening
`docs/index.html` directly in Chrome showed the page shell but no metrics or
filter choices. The original app attempted to fetch a sibling JSON file, which
Chrome blocks for a `file://` page. The repair replaces that request with a
generated `dashboard-data.js` asset loaded before the app. An R6 regression
test executes that asset, verifies all 84,194 records, checks load order, and
proves the app has no remaining fetch dependency. Chrome automation cannot
control local-file tabs under its security policy, so the repaired HTTP path
was re-exercised in Chrome while the executable-data regression test verified
the direct-file path independently.

The owner rejected the first editorial visual direction as overly aesthetic
and insufficiently professional. The presentation layer was rebuilt as a
restrained operations dashboard: one sans-serif system, compact section
hierarchy, conventional filter and KPI cards, neutral surfaces, tighter
spacing, and simplified chart labels. The subsequent data review refreshed the
source year, strengthened privacy and quality controls, added the issue
drill-down and bounded company control, and clarified the relevant CFPB
response fields without reintroducing decorative UI.

The owner's next review correctly identified that rendering alone did not make
the charts complete. Sparse month labels hid most of the calendar, the issue
chart made smaller categories nearly invisible, and the response chart used a
100,000-count scale that visually erased three outcomes. The final value audit
removed that response chart and the route-within-one-day KPI because neither
supported a defensible operating decision from public data. The corrected
dashboard shows monthly volume and response exceptions, issue concentration,
and reported-relief response mix with exact denominators and explicit
limitations.

| Width | Page overflow | Rendering evidence |
|---|---:|---|
| 360 CSS px | 0 px | one-column filters and charts; two-column KPI grid; 44 px selects; 48 px reset button; wide tables scroll inside their cards |
| 768 CSS px | 0 px | two-column filters; two-column KPI grid; four charts stack at 687 px |
| 1440 CSS px | 0 px | four KPI cards and two-column analytical layout |

Behavior checked:

- default metrics rendered as 84,194 complaints, 609 response exceptions
  (0.7%), 12,977 reported-relief responses (15.4%), and a 53.4% leading issue
  share, with exact supporting counts;
- selecting `Managing an account` returned 44,959 complaints and correctly
  changed the concentration dimension to its sub-issues;
- a combined January, checking-account, managing-an-account, and Bank of
  America filter returned 281 records, matching SQLite;
- reset restored all 84,194 records and cleared all four controls;
- the company control contains 53 volume-ordered companies with at least 100
  complaints, plus the all-company option; unfiltered metrics retain all 471;
- all four Chart.js canvases rendered at non-zero dimensions;
- all 12 months were visibly labeled, and every chart stated its unit and
  decision context;
- issue and reported-relief charts showed exact counts and denominators beside
  percentages;
- the repaired build exposed 13 month choices, 5 account-type choices, 12
  issue choices, and 54 company-control choices, including the all-values
  choices;
- the January warning disclosed both dominant company-issue clusters and the
  residual comparison instead of presenting a general capacity claim;
- selecting `Managing an account` changed the issue dimension to sub-issues;
  its top-three breakdown reconciled to 32,388 of 44,959 complaints, or 72.0%;
- in the 281-record four-filter view, the volume and sub-issue tables
  reconciled to the same 281 records; company concentration language was
  suppressed because a company filter was already active;
- a deliberately selected 29-record view withheld rate and share
  interpretation, switched the relevant charts to counts, and displayed the
  30-row threshold;
- a deliberately empty filter combination produced explicit zero-result
  metrics and chart messages without a runtime failure;
- shortened visual issue labels remain paired with complete ARIA descriptions
  and complete fallback-table labels;
- the first chart fallback expanded to a 12-row, two-column data table;
- keyboard Tab focus exposed the skip link with a three-pixel outline;
- the official CFPB source link pointed to the intended HTTPS destination;
- site-owned console errors and warnings were zero. Unrelated extension errors
  were separated by their `chrome-extension://` origin;
- the reduced-motion and print-resize contracts are present and covered by the
  R3/R6 delivery test.

Reviewed screenshots:

- `evidence/screenshots/desktop-1440.jpg`
- `evidence/screenshots/tablet-768.jpg`
- `evidence/screenshots/mobile-360.jpg`

## Publication evidence pending

The delivery record still requires:

1. the public repository URL and commit SHA;
2. the successful GitHub Actions CI run;
3. the verified GitHub Pages URL at desktop and mobile widths.
