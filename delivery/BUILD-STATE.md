# CCO Salesforce update — build state

Finalized September 19, 2026, 21:04 EDT at the owner's request. **Complete and ready for local portfolio demonstration as the supporting Salesforce JR358388 project.** No remaining software blockers were identified. No GitHub push or publication.

Release software commit: `841ec2b`. Finalization preserves the exact native-tested workbook and packaged data. Fresh final checks: 26 tests, 11 source-SQL/package comparisons, browser regression suite, package integrity, and hashes of the workbook, Hyper and all 15 native screenshots pass. The final independent visual/source review remains applicable to this unchanged release. Presentation practice and personal mastery are separate from software readiness.

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

Final TWBX SHA-256: `01ed72476006210e4d898bc1aabb517bb4edad75b9545b1053ae6f344238b778`. Native evidence: `evidence/native-tableau-readability-verification.json`; screenshots: `evidence/screenshots/tableau-readable/`. A byte-identical TWBX opened from `/tmp/cco-readability-delivery/` and Tableau's Hyper process read its extracted package data, whose hash matches the generated Hyper.

Native gates: baseline; Managing an account on both pages; June; Capital One/Managing; Checking/Managing; both January modes; January residual6,923; small base2; empty selection with undefined rates; Unknown51; repeated reset on both pages, including all five controls changed. Wrapped headers, scrollable lists and readable notes verified. Baseline84,194/609/12,977; January18,367/11,444/6,923.

Independent read-only review identified CSV/Hyper provenance binding and missing artifact tests; both repaired. Initial native open exposed XML child ordering; corrected before release. Native review exposed truncated labels; widths/wrapping and scrollable row heights repaired. Final independent review found no remaining blockers. Its browser-install prerequisite documentation correction was applied.

## Reproduce

```sh
uv sync --locked --extra dev
uv run --locked python -m complaint_ops.tableau
uv run --locked python -m complaint_ops.hyper
uv run --locked python -m complaint_ops.workbook
uv run --locked python scripts/verify_tableau.py
uv run --locked pytest -q
npm run test:browser
```

The pinned sanitized CSV must already exist locally. Do not rerun live extraction. Rebuilding artifacts requires new hash-bound native evidence before a new release claim.

## Owner and continuation

Owner requested finalization after the readability correction. Local delivery is finalized in the owned salesforce-tableau checkout. Next use: open the packaged workbook and follow the walkthrough; the manual rebuild guide supports personal practice. Exactly two projects: hotel flagship plus CCO supporting analytics project. Resume and employer-assigned exercise remain deferred. No account, public release, GitHub push or live-site changes were performed or authorized. The earlier readiness review is historical; this record supersedes its missing-workbook status.

GitNexus guide was read; its suggested npx refresh was not run because no supported installed wrapper is available and automatic package installation was prohibited. Direct source/artifact review was used; no graph-index verification is claimed.

## Verified baseline

- Canonical repo `/Users/dakshitraj/KAIROS/consumer-complaint-operations`, current branch publish-source-link at d6a27ac. GitHub main independently reads the same commit. Local main is older (ffdb509); do not use it as the latest source.
- Existing canonical modified `evidence/local-verification.json` was inspected and preserved; it is not incorporated into this checkout.
- Canonical baseline tests:16 passed. Source CSV matches recorded SHA-256 and84194-row snapshot; no new extraction.
- New owned Orca checkout `/Users/dakshitraj/orca/workspaces/consumer-complaint-operations/salesforce-tableau`, branch `refs/heads/Duckky153/salesforce-tableau` from origin/main/d6a27ac. Creation instance `ca082934-618e-409a-bfdd-9bad67241ca7`. No separate agent conversation was started.
- This checkout has its own uv environment and dependency lock; its own baseline test run also passes16 tests. Pinned sanitized CSV was copied into its ignored data/raw directory, not shared via a writable symlink.
