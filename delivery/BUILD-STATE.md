# CCO Salesforce update — build state

Updated 2026-09-19T20:22:00-04:00. **Local Tableau implementation and listed native acceptance checks complete.** Owner rehearsal/acceptance remain separate. No GitHub push or publication.

## Delivered

- `tableau/Consumer Complaint Operations.twbx`: self-contained local package (two dashboards, 11 supporting worksheets, five shared controls).
- `tableau/Consumer Complaint Operations.twb`: editable workbook; companion Hyper at `data/processed/tableau-complaints.hyper`.
- Source→CSV→Hyper preparation, independent SQL reconciliation, package verifier and failure-case tests.
- [Walkthrough](TABLEAU-WALKTHROUGH.md), [architecture/refresh/sharing](TABLEAU-ARCHITECTURE.md), [manual rebuild guide](TABLEAU-REBUILD-GUIDE.md), [field dictionary](TABLEAU-DATA-DICTIONARY.md).

## Verified

26 pytest tests pass. Seven CSV/source SQL scopes and seven Hyper scopes pass; packaged Hyper passes 11 source-SQL scopes and a full observation/multiplicity comparison. All 84,194 observations and the pinned source hash are preserved. Existing web verification: 20 checks and responsive Chromium suite pass.

Final TWBX SHA-256: `50a713b3a885d77ddeefe3b0757f2981283cf634e012ed2ce1c5454feff38cbb`. Native evidence: `evidence/native-tableau-verification.json`; screenshots: `evidence/screenshots/tableau/`. A byte-identical TWBX opened from `/tmp/cco-portable-final/` and Tableau's Hyper process read its extracted package data, whose hash matches the generated Hyper.

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

Current task: plan/build/test/review authorized by owner. Scope: owned salesforce-tableau checkout only. Software is complete at the documented local scope; next is owner walkthrough/manual rebuild. Exactly two projects: hotel flagship plus CCO supporting analytics project. Resume and employer-assigned exercise remain deferred. No account, public release, GitHub push or live-site changes were performed or authorized. The earlier readiness review is historical; this record supersedes its missing-workbook status.

GitNexus guide was read; its suggested npx refresh was not run because no supported installed wrapper is available and automatic package installation was prohibited. Direct source/artifact review was used; no graph-index verification is claimed.

## Verified baseline

- Canonical repo `/Users/dakshitraj/KAIROS/consumer-complaint-operations`, current branch publish-source-link at d6a27ac. GitHub main independently reads the same commit. Local main is older (ffdb509); do not use it as the latest source.
- Existing canonical modified `evidence/local-verification.json` was inspected and preserved; it is not incorporated into this checkout.
- Canonical baseline tests:16 passed. Source CSV matches recorded SHA-256 and84194-row snapshot; no new extraction.
- New owned Orca checkout `/Users/dakshitraj/orca/workspaces/consumer-complaint-operations/salesforce-tableau`, branch `refs/heads/Duckky153/salesforce-tableau` from origin/main/d6a27ac. Creation instance `ca082934-618e-409a-bfdd-9bad67241ca7`. No separate agent conversation was started.
- This checkout has its own uv environment and dependency lock; its own baseline test run also passes16 tests. Pinned sanitized CSV was copied into its ignored data/raw directory, not shared via a writable symlink.
