# CCO Tableau version: build state

Finalized September 19, 2026, 21:04 EDT. **The Tableau version is complete.** No remaining software blockers were identified. The workbook is published in this public repository and as the downloadable release [`tableau-2026-09-19`](https://github.com/Duckky153/consumer-complaint-operations/releases/tag/tableau-2026-09-19).

Release software commit: `841ec2b`. Finalization preserves the exact native-tested workbook and packaged data. Fresh final checks: 26 tests, 11 source-SQL/package comparisons, browser regression suite, package integrity, and hashes of the workbook, Hyper and all 15 native screenshots pass. The final independent visual/source review remains applicable to this unchanged release.

## Readability revision

Shorter headings, larger chart/category text, taller monthly charts, a left filter rail, paired count/rate groups, plain investigation headers, full-width scrolling tables and a bordered reset target. January uses a visible three-choice list; “Exclude top 2 groups” aliases the same fixed full-population company/issue rule. Four unfiltered selected-value sheets give larger readbacks for compact native dropdowns. Long selected labels break at a word boundary. The full-January reference stays explicit under filtered views.

Fresh native acceptance covers 15 screenshots, including long company/issue names, cross-page state, both sensitivity modes, repeated reset of all five changed controls, small/empty/Unknown groups, and table scrolling. Independent visual/source review found no blocking issues. Original native receipt/screenshots remain historical and are not evidence for this new hash.

## Delivered

- `tableau/Consumer Complaint Operations.twbx`: self-contained local package (two dashboards, 15 supporting worksheets, five shared controls).
- `tableau/Consumer Complaint Operations.twb`: editable workbook; companion Hyper at `data/processed/tableau-complaints.hyper`.
- Source→CSV→Hyper preparation, independent SQL reconciliation, package verifier and failure-case tests.
- [Walkthrough](TABLEAU-WALKTHROUGH.md), [architecture/refresh/sharing](TABLEAU-ARCHITECTURE.md), [manual rebuild guide](TABLEAU-REBUILD-GUIDE.md), [field dictionary](TABLEAU-DATA-DICTIONARY.md).

## Verified

26 pytest tests pass. Seven CSV/source SQL scopes and seven Hyper scopes pass; packaged Hyper passes 11 source-SQL scopes and a full observation/multiplicity comparison. All 84,194 observations and the pinned source hash are preserved. Existing web verification: 20 checks and responsive Chromium suite pass.

Final TWBX SHA-256: `01ed72476006210e4d898bc1aabb517bb4edad75b9545b1053ae6f344238b778`. Native evidence: `evidence/native-tableau-readability-verification.json`; screenshots: `evidence/screenshots/tableau-readable/`. A byte-identical TWBX was copied to a separate temporary directory and opened there, and Tableau's Hyper process read its extracted package data, whose hash matches the generated Hyper.

Native gates: baseline; Managing an account on both pages; June; Capital One/Managing; Checking/Managing; both January modes; January residual 6,923; small base 2; empty selection with undefined rates; Unknown 51; repeated reset on both pages, including all five controls changed. Wrapped headers, scrollable lists and readable notes verified. Baseline 84,194 / 609 / 12,977; January 18,367 / 11,444 / 6,923.

Independent read-only review identified CSV/Hyper provenance binding and missing artifact tests; both repaired. Initial native open exposed XML child ordering; corrected before release. Native review exposed truncated labels; widths/wrapping and scrollable row heights repaired. Final independent review found no remaining blockers. Its browser-install prerequisite documentation correction was applied.

## Reproduce

Follow [Reproduce locally](../README.md#reproduce-locally) in the README, including "Rebuild the Tableau files". The pinned sanitized CSV must already exist locally. Do not rerun live extraction to reproduce this release. Rebuilding artifacts requires new hash-bound native evidence before a new release claim.

## Status

Next use: open the packaged workbook and follow the [walkthrough](TABLEAU-WALKTHROUGH.md).

## Starting baseline

- Starting point: GitHub `main` at `d6a27ac`, the published web dashboard.
- Baseline tests: 16 passed. The source CSV matched its recorded SHA-256 and 84,194-row snapshot; no new extraction was run.
