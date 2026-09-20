# CCO Tableau architecture and product fit

## What actually runs

Pinned sanitized CFPB CSV → Python quality/normalization → ten-field CSV → typed Hyper extract → two-page Tableau workbook. SQLite independently computes source metrics. A verifier extracts the packaged Hyper into a temporary directory and checks 11 source cohorts plus every CSV row and its multiplicity. The TWBX contains exactly the TWB and Hyper. The editable standalone TWB refers to `../data/processed/tableau-complaints.hyper`.

One complaint is one observation. IDs are validated only in the local source pipeline; none are included in CSV/Hyper/TWBX. Narratives, ZIP/state, tags, channels, raw responses and routing intervals are excluded. Dates, issue/category/company labels and aggregate flags remain. Packaging is not anonymization or access control: recipients of a TWBX can inspect its included data. Distribution requires a separate owner decision.

Five string parameters select account type, issue, company, month and sensitivity globally. All summary calculations condition on the same Selected cohort predicate. Breakdown sheets additionally filter that predicate to True. Summary/note/reset sheets retain source rows so a zero-match selection still renders zero counts, undefined rates, a message and a working reset. Reset changes all five parameters and clears its own selected mark, making repeat use possible.

The two January company/issue clusters are computed once over the whole pinned January population, with deterministic alphabetical tie breaks. The flag is 1 only on their January observations. Changing a view parameter cannot redefine cluster membership. No FIXED expression or table calculation silently changes the population.

The workbook has 11 supporting worksheets and exactly two dashboards. Readable wrapped category headers use scrollable lists; all categories remain available. Bar selection is not a filter action. Dropdowns are the shared cohort controls.

## Refresh contract

This release has no scheduled refresh, live source connection, credentials, CRM writeback, row-level security or production monitoring. Rebuilding uses the existing pinned source and fails if its SHA-256 changes. Source extraction date is July 29, 2026; the observations cover 2025. It is not a current complaint monitor.

A future refresh needs a separately approved snapshot: preserve the old source/evidence, review fields/date bounds/known-value behavior, profile category drift and duplicates, recompute the global January clusters for the chosen contract, regenerate CSV/Hyper/parameter lists, rerun SQL/package/native tests, and produce a new hash-bound release receipt. Do not append new observations silently or update the pin merely to bypass a mismatch. The current locked build deliberately refuses a different source.

For enterprise use, first establish a source owner, refresh cadence, recipient roles and access model. Then evaluate governed Tableau Server/Cloud publishing, secure connections, certified data definitions, failed-refresh notifications and permission tests. These are proposed capabilities, not implemented project features. A package is suitable for this local portfolio demonstration; it is not a substitute for governed production distribution.

## Salesforce discussion

The captured role asks for hands-on Tableau, CRM Analytics or Tableau Next experience and customer data architecture. This project demonstrates local Tableau analysis, SQL/data modeling and evidence-based discovery. It does not claim CRM Analytics, Tableau Next, Agentforce or customer-environment integration.

If a customer wanted CRM context, first agree on complaint-to-case matching, lawful source use, internal transaction/customer denominators, historical timing and access controls. Relate or aggregate data at explicit grains to prevent one public complaint from multiplying through one-to-many case/activity joins. Validate unmatched and multiple-match records separately. Choose products after discovery of workflow, users, governance and latency; do not assume every Tableau use case needs a CRM writeback or AI feature.

## Official implementation references

- [Hyper creation](https://tableau.github.io/hyper-db/docs/guides/hyper_file/create_update/): native typed extract API used with usage telemetry disabled.
- [Packaged workbooks](https://help.tableau.com/current/pro/desktop/en-us/save_savework_packagedworkbooks.htm): TWBX distribution includes workbook resources.
- [Parameter actions](https://help.tableau.com/current/pro/desktop/en-us/actions_parameters.htm): native actions power reset.

Tableau XML generation is a local, explicit build method validated in installed Tableau Public 2026.2.2. It is not a promise that undocumented XML formatting will remain compatible with every future Tableau release. Re-run native gates after a version change.
