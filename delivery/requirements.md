# Requirements and Acceptance Criteria

The six requirements are intentionally small enough for one portfolio project
and complete enough to demonstrate professional delivery discipline.

## R1 — Reproducible bounded data pipeline

**User need:** As the project owner, I need the analytical population to be
rebuildable so the dashboard is not based on an unexplained spreadsheet.

Acceptance criteria:

- **R1-AC1:** The checked-in configuration defines the official CFPB endpoint,
  product, start date, and end boundary.
- **R1-AC2:** One command fetches or reads the source, allowlists fields,
  normalizes types, writes a sanitized CSV, builds SQLite, and generates the
  dashboard data.
- **R1-AC3:** Repeated builds from the same source rows produce the same
  sanitized-data SHA-256 and metric values.
- **R1-AC4:** The final population is all published `Checking or savings
  account` complaints received in calendar year 2025; there is no silent
  sampling.

## R2 — Decision-ready operating summary

**User need:** As a risk or operations analyst, I need the default view to
separate robust external signals from anomaly-dependent findings before I
filter.

Acceptance criteria:

- **R2-AC1:** The default view shows published complaint count, not-timely
  response count and rate, reported-relief count and rate, and the leading
  issue share. When one issue is selected, concentration switches to its
  leading sub-issue share.
- **R2-AC2:** Each KPI includes a nearby plain-English definition.
- **R2-AC3:** Default KPI values reconcile to the SQLite metric views and the
  normalized record count.
- **R2-AC4:** The page leads with an evidence-based finding and a bounded action.
- **R2-AC5:** Exception, reported-relief, and concentration cards show their
  exact supporting complaint counts.
- **R2-AC6:** The page states that the public data supports investigation
  hypotheses, not internal staffing, service-level, policy, or performance
  decisions.

## R3 — Explainable trends, drivers, and filters

**User need:** As a risk or operations analyst, I need to see what changed,
what drove an unusual pattern, and what internal evidence should be requested.

Acceptance criteria:

- **R3-AC1:** The dashboard shows monthly published volume and monthly
  not-timely response exceptions as separate charts with exact numerators.
- **R3-AC2:** It shows issue concentration, reported-relief share among the
  six highest-volume issue details, high-volume issue detail, and monthly
  exception detail.
- **R3-AC3:** Month, account-type, issue, and company filters update all cards,
  charts, tables, and narrative from one consistent record set.
- **R3-AC4:** A reset restores the complete 84,194-row view.
- **R3-AC5:** Every canvas chart has an accessible text label and an expandable
  data table.
- **R3-AC6:** Issue-detail and monthly-exception tables show exact counts and
  rates from the selected view. Reported relief is visibly labeled as
  non-directional response mix.
- **R3-AC7:** The company control is ordered by published complaint volume and limited to
  companies with at least 100 complaints so the 471-company long tail does not
  make the control unusable; the unfiltered view still includes every row.
- **R3-AC8:** Every chart visibly states its unit and key context. Monthly
  charts show all month labels; issue and reported-relief charts show exact
  counts and percentages beside their categories.
- **R3-AC9:** Below 30 selected complaints, the dashboard retains exact counts
  but withholds priority language and qualifies or withholds rate
  interpretation.
- **R3-AC10:** The default monthly-volume view decomposes January into its two
  largest company-issue clusters, shows the residual, and prohibits using the
  spike alone as a staffing signal.

## R4 — Data quality and analytical provenance

**User need:** As a decision maker, I need to know whether the data is safe to
use and where each number came from.

Acceptance criteria:

- **R4-AC1:** The build fails on missing required columns, duplicate complaint
  IDs, required-field nulls, invalid timely values, wrong product values, or
  out-of-window dates, or negative routing intervals.
- **R4-AC2:** The quality report records grain, row count, date range,
  completeness, distinct counts, warnings, and critical-check results.
- **R4-AC3:** The source manifest records the exact request, row count, scope,
  build timestamp, exclusions, and sanitized-data SHA-256.
- **R4-AC4:** The site displays source, period, product, population, snapshot
  timestamp, and a shortened data hash.
- **R4-AC5:** A stable monthly-volume rule reports—not deletes—months above
  twice the calendar-year monthly median so unusual source patterns remain
  visible for investigation.

## R5 — Public privacy and security minimization

**User need:** As the project owner, I need a public portfolio artifact that
does not expose unnecessary complaint detail or secrets.

Acceptance criteria:

- **R5-AC1:** Consumer narratives, ZIP codes, and company public-response prose
  are excluded during ingestion.
- **R5-AC2:** State, tags, and submitted-via values are excluded during
  ingestion. Complaint IDs are retained only for local uniqueness validation
  and do not enter the public dashboard data asset. Exact routing time and the
  raw company-response category also remain outside the public filtering
  payload because the revised decision does not require them.
- **R5-AC3:** The site is read-only, contains no account system or secrets, and
  makes no runtime third-party request.
- **R5-AC4:** Chart.js is pinned and vendored with its license; a restrictive
  Content Security Policy is declared.
- **R5-AC5:** Dynamic labels are inserted with `textContent`, not HTML parsing.

## R6 — Verified delivery and client-ready handoff

**User need:** As a recruiter or interviewer, I need evidence that the work was
specified, tested, visually checked, and explainable.

Acceptance criteria:

- **R6-AC1:** Automated tests map to R1–R6 and pass under Python 3.12.
- **R6-AC2:** Application and generated-data JavaScript syntax, required
  static-asset references, and load order pass automated checks.
- **R6-AC3:** The dashboard is checked in a real browser at 360, 768, and 1440
  CSS-pixel widths with no page-level horizontal overflow.
- **R6-AC4:** Filters, reset, chart rendering, tables, source link, keyboard
  focus, and reduced-motion behavior are verified.
- **R6-AC5:** The repository includes methodology, limitations, findings,
  recommendations, delivery evidence, AI disclosure, a two-minute demo,
  and a privacy-clean public handoff.
- **R6-AC6:** Repository creation and deployment occur only after recorded
  owner approval and retain a verifiable publication sequence.
- **R6-AC7:** Opening `docs/index.html` directly in Chrome loads the verified
  data, metrics, and filter choices without requiring a local HTTP server; the
  same static files also work when served over HTTP.
