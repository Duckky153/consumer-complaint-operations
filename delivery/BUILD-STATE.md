# CCO Tableau version: build state

Updated 2026-09-19T19:40:45.128557-04:00. Phase: baseline audited; owned worktree and implementation contract established. Tableau extension is **not complete**.

## Verified baseline

- Starting point: GitHub `main` at `d6a27ac`, the published web dashboard.
- Existing canonical modified `evidence/local-verification.json` was inspected and preserved; it is not incorporated into this checkout.
- Canonical baseline tests:16 passed. Source CSV matches recorded SHA-256 and84194-row snapshot; no new extraction.
- This checkout has its own uv environment and dependency lock; its own baseline test run also passes16 tests. Pinned sanitized CSV was copied into its ignored data/raw directory, not shared via a writable symlink.

## Next implementation

Follow TABLEAU-SPEC.md: first add minimized export and independent SQL reconciliation; then build the real Hyper/TWB/TWBX, verify native interactions, update field/metric/architecture/demo/rebuild documentation and review. Do not describe the web dashboard as an actual Tableau workbook.
