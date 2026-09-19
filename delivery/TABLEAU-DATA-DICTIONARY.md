# Tableau export fields

One row per published complaint in the pinned 2025 checking/savings snapshot. The CSV excludes original complaint IDs. Row order is deterministic from locally validated IDs; row numbers are not business identifiers.

| Field | Meaning |
|---|---|
| date_received | Calendar receipt date, YYYY-MM-DD |
| received_month | Receipt month, YYYY-MM |
| sub_product | Account type; missing becomes Unknown |
| issue | Published issue category; missing becomes Unknown |
| sub_issue | Published detail; missing becomes Unknown |
| company | Published company label; not a customer-base denominator |
| complaint_count |1 per observation |
| not_timely |1 only when the dedicated Timely response field is No |
| has_relief |1 for monetary/non-monetary relief response categories; response mix only |
| january_top_cluster |1 for January records in the full snapshot's two largest company-issue clusters |

January cluster membership is fixed before interactive filtering. Ties sort by company, then issue, alphabetically. Filtering to a company or issue must not redefine the two clusters. The same company's non-January rows remain unmarked. Excluding January entirely is a separate view mode.

Rates use SUM(flag)/SUM(complaint_count), with no rate for zero rows and cautious interpretation below30. The current input quality contract rejects invalid timely-response values; they are not silently interpreted as No. See `evidence/tableau-data-verification.json` for source hash, export hash, actual cluster counts and independent SQL results.

No consumer narrative, ZIP/state, tags, submission channel, original complaint ID, raw company response or routing date/interval appears in the export. These restrictions continue into Hyper and Tableau packaging.
