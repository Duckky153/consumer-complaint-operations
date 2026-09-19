# Salesforce JR358388 — CCO readiness review

Reviewed September 19, 2026 against the locally captured exact job description (observed September 19), TABLEAU-SPEC.md, source code, source snapshot and fresh local tests. This review does not revalidate the vacancy or application status.

**Verdict: the existing web project and Tableau CSV foundation are verified; the CCO Tableau extension is not ready to present as delivered Tableau work.** Hotel remains the flagship; CCO is the supporting second project. The key contribution here is careful analytical investigation, SQL reconciliation and honest interpretation of public data.

## Make, fix and update

| Priority | Work | Reason for the role | Acceptance evidence |
|---|---|---|---|
| P0 — make | Real Hyper extract, editable TWB and self-contained TWBX | Hands-on Tableau and a working technical demonstration | Open package from a separate folder without relying on the source CSV; reconcile its numbers; inspect included fields |
| P0 — make | Two readable Tableau pages: Overview and Investigation | Explain one decision to executive and analyst audiences | Overview shows counts, not-timely rate, relief mix and monthly context; Investigation shows issue/sub-issue detail, selected denominator and proposed internal validation |
| P0 — make | Shared month, account, issue and company filters; three sensitivity modes; repeatable reset | Demonstrate trustworthy self-service exploration | Observe controls on both pages in native Tableau; baseline/exclude January/exclude fixed January clusters behave consistently; reset restores all controls |
| P0 — verify | Native Tableau tests and final-package evidence | Source/XML tests cannot prove interactive behavior | Baseline and documented slices match SQL; zero, below-30 and Unknown states are readable; reopen final package and bind screenshots/results to its SHA-256 |
| P1 — update | Persona discovery and executive/analyst walkthrough | Requirements discovery, customized demos and business communication | Ask what decision is pending, who acts, what internal denominator/outcome is available, and what evidence would change the recommendation; demonstrate one investigation and a validation next step |
| P1 — update | Architecture, refresh and sharing explanation | Customer data architecture and product judgment | Distinguish implemented local snapshot from proposed enterprise access, governed refresh and Salesforce integration; document source ownership, validation failure handling and privacy constraints |
| P1 — make | Plain-English manual Tableau rebuild and teach-back guide | Peer teaching and personally demonstrable hands-on ability | Owner recreates a sheet/calculation, changes a filter, traces a figure to SQL and explains the sensitivity behavior; completion must be observed separately |
| P1 — update | README, metric dictionary, traceability, delivery evidence and AI contribution record | Clear handoff and truthful technical claims | Every delivered claim maps to a real artifact/test; no web screenshot is labeled Tableau; no claim of independently demonstrated mastery without evidence |

The accepted specification already supplies the appropriate scope. No additional project, predictive model, company leaderboard, CRM deployment or AI feature is required for this supporting artifact. The captured JD lists Tableau, CRM Analytics **or** Tableau Next for hands-on experience; it does not require building all three here. Certifications and AI/ML familiarity are broader preparation topics, not missing CCO features.

## Fixed during this review

The SQL/export reconciler previously checked account type plus issue instead of the required company plus issue. Added CAPITAL ONE FINANCIAL CORPORATION / Managing an account while preserving all six existing scopes. Its source totals are 6,428 complaints, 0 not timely and 176 relief responses. A regression test now deliberately changes a company label while leaving overall metrics unchanged and verifies that reconciliation fails.

Updated the contribution wording to avoid director framing and presenting unobserved owner understanding as an achieved result. The web demo now identifies the AI-assisted contribution explicitly. These are preparation aids, not proof of owner rehearsal.

## Tests run and limits

- `uv run --locked pytest -q`: **22 passed**, including the company-attribution regression.
- `uv run --locked python -m complaint_ops.tableau`: **7 SQL/export scopes passed**, all 84,194 observations preserved; ten allowed fields; pinned source hash unchanged. Export SHA-256 remains `70e708b0fef16c9dd2045001ef2d65e18c861153c9e6284b24c08e385029cc51`.
- Rebuilt the missing ignored local SQLite database from the pinned sanitized CSV using existing normalization and SQL definitions. No API extraction or website regeneration.
- `uv run --locked python scripts/verify_delivery.py`: **20 checks passed**, including source hash, SQLite/public totals, monthly rates, January clusters, data minimization, assets and JavaScript syntax. Receipt is this owned checkout's `evidence/local-verification.json`; the canonical checkout's existing edit was preserved.
- `npm run test:browser`: **passed** in Chromium at 360/768/1440 widths, with filters, reset, 29-row warning, zero results, keyboard skip link, accessible tables, links, charts and direct-file loading. This is the permitted project test suite, not interactive browser automation. It does not certify native Tableau or a fresh visual design review.
- No TWB, TWBX or Hyper artifact exists in this checkout. Tableau Public is installed, but no native CCO interaction, package reopen or screenshot gate can pass before a CCO workbook exists.

## Native acceptance numbers

Counts below are independently reconciled source SQL / CSV results, **not native Tableau results**. Rates must use selected counts as denominators, never averages of group percentages.

| Scope | Complaints | Not timely | Relief responses |
|---|---:|---:|---:|
| Baseline | 84,194 | 609 | 12,977 |
| Managing an account | 44,959 | 363 | 7,114 |
| June | 5,557 | 135 | 1,030 |
| CAPITAL ONE FINANCIAL CORPORATION / Managing an account | 6,428 | 0 | 176 |
| Checking account / Managing an account | 36,185 | 238 | 5,988 |
| Exclude all January | 65,827 | 571 | 11,716 |
| Exclude January's fixed two clusters | 72,750 | 609 | 12,857 |

January itself is 18,367; the two fixed company/issue clusters total 11,444; the residual is 6,923. Membership must remain fixed under later filters and must never exclude the same companies' non-January records.

Use the browser's existing edge cases as additional native targets: February / Checking account / Problem caused by your funds being low / JPMORGAN CHASE & CO. gives 29 rows; January / CD (Certificate of Deposit) / Closing an account / NAVY FEDERAL CREDIT UNION gives zero. Validate Unknown sub-issues explicitly, and show no percentage when the denominator is zero.

## Recommended story

“An operations analyst needs to decide which public complaint pattern to validate internally. Managing an account is the largest issue in this snapshot. Before treating January's spike as a broad operating problem, isolate its two dominant clusters and compare the remaining pattern. Then request internal case outcomes and customer or transaction denominators to determine whether a targeted process review is warranted.”

For an executive, emphasize the decision, uncertainty and next evidence request. For an analyst, show the filters, denominator, SQL trace and sensitivity. Complaint volume is not a company performance or harm rate; relief is a response category, not proof of satisfaction. There is no measured savings or causal improvement claim.

## Boundary and next action

Readiness assessment and the narrow reconciliation repair are complete. The Tableau build remains outstanding. Implement the approved two-page native workbook next, then run the gates above before describing this extension as delivered. Resume work, employer-assigned panel demo, new accounts, public release and GitHub push remain outside this review. No external actions were taken.
