# CCO Salesforce update — build state

Updated 2026-09-19T19:54:25-04:00. Phase: baseline audited; owned worktree established; minimized Tableau data foundation implemented and verified. Tableau extension is **not complete**.

## Verified baseline

- Canonical repo `/Users/dakshitraj/KAIROS/consumer-complaint-operations`, current branch publish-source-link at d6a27ac. GitHub main independently reads the same commit. Local main is older (ffdb509); do not use it as the latest source.
- Existing canonical modified `evidence/local-verification.json` was inspected and preserved; it is not incorporated into this checkout.
- Canonical baseline tests:16 passed. Source CSV matches recorded SHA-256 and84194-row snapshot; no new extraction.
- New owned Orca checkout `/Users/dakshitraj/orca/workspaces/consumer-complaint-operations/salesforce-tableau`, branch `refs/heads/Duckky153/salesforce-tableau` from origin/main/d6a27ac. Creation instance `ca082934-618e-409a-bfdd-9bad67241ca7`. No separate agent conversation was started.
- This checkout has its own uv environment and dependency lock; its own baseline test run also passes16 tests. Pinned sanitized CSV was copied into its ignored data/raw directory, not shared via a writable symlink.

## Tableau data foundation implemented

Run `uv sync --locked --extra dev`, `uv run --locked pytest -q` and `uv run --locked python -m complaint_ops.tableau`. The build requires the pinned sanitized snapshot at `data/raw/complaints_2025_checking_savings.csv`; this worktree already contains a verified local copy. It stops if the source hash differs rather than silently refreshing data.

`src/complaint_ops/tableau.py` produces `data/processed/tableau-complaints.csv` (ignored, rebuildable). Its ten fields exclude complaint IDs and the source's other restricted fields. Existing normalization/quality gates are retained. Original rows are never removed; January's two fixed source-wide clusters are marked for later view sensitivity.

**22 tests pass** (16 existing plus 6 export/edge-case tests). Seven source-SQL/export scopes reconcile: baseline, Managing an account, June, CAPITAL ONE FINANCIAL CORPORATION/Managing an account, Checking account/Managing an account, excluding January and excluding January's two largest clusters. Baseline84194/609/12977 and January cluster11444 match the retained findings. Evidence: `evidence/tableau-data-verification.json`; field dictionary: `delivery/TABLEAU-DATA-DICTIONARY.md`.

No Tableau workbook or Hyper extract has been built in this update yet. The existing live web dashboard is unchanged.

## Next implementation

Follow TABLEAU-SPEC.md: build the real Hyper/TWB/TWBX, verify native interactions, update field/metric/architecture/demo/rebuild documentation and review. Do not describe the web dashboard as an actual Tableau workbook.

## Orca and continuation

Use this project's salesforce-tableau worktree for the update. Read AGENTS.md, SALESFORCE-ROLE-BRIEF.md, TABLEAU-SPEC.md and this file at the start of a new conversation. Saved files transfer context; this does not imply the full earlier chat is automatically loaded. Hotel is finalized; CCO is the active next project. Resume and employer-assigned demo remain deferred. No new push/publication is authorized here.

## Sidebar organization

Native Orca **Active Projects** group contains **Hotel Booking Decision Studio** and **Consumer Complaint Operations**. Hotel workspaces are labeled **Final review · completed** and **Earlier build · reference**, with histories retained. Continue CCO in **Salesforce Tableau update**. This is sidebar metadata; no repository folders were moved or worktrees deleted.

## Role readiness review — September 19

Completed source/code/documentation review against the exact captured JD. Added missing company/issue SQL reconciliation and a regression proving that company misattribution is detected even when totals are unchanged. Fresh 22 pytest tests, 7 Tableau CSV reconciliation scopes, 20 local delivery checks and the responsive Chromium interaction suite pass. Native CCO Tableau gates remain untested because workbook/Hyper artifacts do not yet exist. See [prioritized work and native acceptance targets](2026-09-19-ROLE-READINESS-REVIEW.md). Next: implement the approved native workbook, packaging and role-focused delivery guides; then verify native interactions. No new source extraction, push or publication.
