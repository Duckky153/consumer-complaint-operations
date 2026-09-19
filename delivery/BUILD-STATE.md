# CCO Salesforce update — build state

Updated 2026-09-19T19:40:45.128557-04:00. Phase: baseline audited; owned worktree and implementation contract established. Tableau extension is **not complete**.

## Verified baseline

- Canonical repo `/Users/dakshitraj/KAIROS/consumer-complaint-operations`, current branch publish-source-link at d6a27ac. GitHub main independently reads the same commit. Local main is older (ffdb509); do not use it as the latest source.
- Existing canonical modified `evidence/local-verification.json` was inspected and preserved; it is not incorporated into this checkout.
- Canonical baseline tests:16 passed. Source CSV matches recorded SHA-256 and84194-row snapshot; no new extraction.
- New owned Orca checkout `/Users/dakshitraj/orca/workspaces/consumer-complaint-operations/salesforce-tableau`, branch `refs/heads/Duckky153/salesforce-tableau` from origin/main/d6a27ac. Creation instance `ca082934-618e-409a-bfdd-9bad67241ca7`. No separate agent conversation was started.
- This checkout has its own uv environment and dependency lock; its own baseline test run also passes16 tests. Pinned sanitized CSV was copied into its ignored data/raw directory, not shared via a writable symlink.

## Next implementation

Follow TABLEAU-SPEC.md: first add minimized export and independent SQL reconciliation; then build the real Hyper/TWB/TWBX, verify native interactions, update field/metric/architecture/demo/rebuild documentation and review. Do not describe the web dashboard as an actual Tableau workbook.

## Orca and continuation

Use this project's salesforce-tableau worktree for the update. Read AGENTS.md, SALESFORCE-ROLE-BRIEF.md, TABLEAU-SPEC.md and this file at the start of a new conversation. Saved files transfer context; this does not imply the full earlier chat is automatically loaded. Hotel is finalized; CCO is the active next project. Resume and employer-assigned demo remain deferred. No new push/publication is authorized here.
