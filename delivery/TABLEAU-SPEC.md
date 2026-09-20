# CCO Tableau extension — implementation specification

September 19, 2026. This applies the previously accepted CCO extension for Salesforce JR358388. The existing web project remains the reference; this is an additive local Tableau delivery.

## User and decision

A financial-services operations analyst uses public complaints to choose a question to validate against internal data. An executive needs the short interpretation and limits. Neither audience can infer a company's true defect rate, staffing demand or customer harm from this dataset.

## Source and model

Use the existing sanitized 2025 checking/savings snapshot: 84,194 rows; SHA-256 `964912efdcfe70f2376591d40781f64832e879c73ff7d629fdadb6115541053b`. Its retained manifest describes extraction July 29, 2026 UTC. This is a pinned historical snapshot, not a new API extraction. Keep the snapshot byte-identical; generate independent worktree outputs.

One observation per complaint. Complaint ID is for local uniqueness checks only, excluded from Tableau. Export only date/month, account type, issue/sub-issue, company label, complaint count, not-timely flag, relief flag and a documented January-cluster flag. Preserve unknown sub-issues as an explicit label. Do not include consumer narratives, ZIP, state, tags, submission channel, raw company response, routing dates/hours or contact details. Publish neither row data nor workbook without separate authorization.

## Compact Tableau scope

1. **Overview:** published complaints, not-timely count/rate, reported-relief mix, monthly volume and monthly not-timely exceptions. A short finding, denominator and public-data limitation must be readable without hovering.
2. **Investigation:** issue/sub-issue counts and rates, selected cohort count, and a concise proposed internal validation step. Company is a filter, not a performance leaderboard. Keep small-base and empty states clear.
3. **January sensitivity control:** baseline / exclude January / exclude January's two largest company-issue clusters. The two clusters are determined once from the full pinned January population with deterministic tie-breaking. Other filters do not silently change what “two clusters” means. Removing the clusters affects only their January records. Original observations remain unchanged. Labels must distinguish these two exclusion methods.

These are two compact pages, not four separate dashboards. The monthly view is part of the overview. Shared account-type, issue, company, month and sensitivity scope must apply consistently. Reset restores the same baseline. Use large text, restrained colors and plain-language headings learned from the hotel review.

## Metric contract and checks

Complaint count is selected rows. Not timely means the dedicated timely-response field equals No. Relief means closed with monetary or non-monetary relief; it is response mix, not customer success or fault. Rates use selected complaint count; never average group percentages. Preserve the original known-value quality contract and document any unknown handling explicitly.

Reconcile source, SQL, Tableau export and native workbook at baseline and at least three meaningful slices: Managing an account; June; a documented company/issue combination. Also test both January modes, zero matches, fewer than30 rows, unknown sub-issue, cross-page consistency and reset. Check January18367, leading two clusters11444, residual6923 against the actual source before using them. Distinguish source-time findings from current company conditions.

## Delivery

- Allowlisted CSV and real Hyper extract with field dictionary and source lineage.
- Editable TWB and self-contained TWBX that opens with packaged data.
- SQL reference calculations, independent reconciliation and meaningful edge-case tests.
- Native Tableau screenshots and evidence bound to the actual final workbook hash.
- Executive interpretation and analyst investigation walkthrough.
- Refresh/sharing/product-fit explanation distinguishing local snapshot functionality from proposed enterprise governance and Salesforce integration.
- Plain-English manual rebuild guide and accurate contribution notes.

## Completion boundary

Do not call this update complete from generated XML, a passing test count or screenshots alone. Observe filters, sensitivity and reset in Tableau, reopen the package independently and check numbers. Personal learning remains separate. No fresh source extraction, public Pages deployment, GitHub push, accounts, paid services, resume or employer demo in this scope.

## Subsequent distribution authorization

September 19, 2026: after finalization, the owner requested “Github and whatever else you have to do.” This authorizes publication of the reviewed project and minimized packaged Tableau workbook in the existing public repository and its downloadable release. Raw source CSVs and complaint IDs stay excluded. The original no-publication gate above describes the initial build phase.
