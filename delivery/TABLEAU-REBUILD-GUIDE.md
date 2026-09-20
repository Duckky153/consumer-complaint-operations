# Rebuild and explain CCO in Tableau

There are two distinct exercises: reproduce the verified software, and manually rebuild an analysis to demonstrate your own understanding. Neither exercise requires publishing or creating an account.

## Reproduce the release

From the owned salesforce-tableau checkout, with the pinned sanitized CSV already present:

```sh
uv sync --locked --extra dev
uv run --locked python -m complaint_ops.tableau
uv run --locked python -m complaint_ops.hyper
uv run --locked python -m complaint_ops.workbook
uv run --locked python scripts/verify_tableau.py
uv run --locked pytest -q
npm run test:browser
```

For a fresh checkout, browser testing additionally needs Node.js and the pinned browser dependencies: run `npm ci` and `npx playwright install chromium` before `npm run test:browser`. These are local test dependencies, not a browser-control MCP.

The first command installs this project's locked dependencies. The next three create the minimized CSV, Hyper and TWB/TWBX. The verifier compares the packaged data against source SQL; pytest checks contracts and failure cases. The browser command tests the preserved web dashboard. Native GUI verification is a separate gate described below. Hyper and ZIP bytes can change on rebuild; rebind native evidence to the actual release hash, not an older receipt.

Never run the original web builder's live extraction command to reproduce this pinned Tableau release. A fresh checkout needs an authorized local copy of `data/raw/complaints_2025_checking_savings.csv` with the hash in TABLEAU-SPEC.md. The source is intentionally excluded from Git.

## Manual exercise: begin with one useful sheet

1. Open Tableau Desktop Public Edition and connect to `data/processed/tableau-complaints.hyper`. Select its Extract table. Keep `date_received` as a date, category fields as dimensions, and four count/flag fields as whole-number measures.
2. Make a new sheet. Put `received_month` on Rows and SUM(`complaint_count`) on Columns; use bars and show labels. You should see 12 months and January 18,367. Name it Monthly complaints.
3. Duplicate the sheet, replace the measure with SUM(`not_timely`), and name it Monthly not-timely exceptions. June is 135.
4. Create `Not timely rate` as `IF SUM([complaint_count]) > 0 THEN SUM([not_timely])/SUM([complaint_count]) END`. Format as percentage, two decimals. Explain why it is 0.72% overall. Repeat with `has_relief` for relief mix (15.41%).
5. Build a simple issue count bar sheet. On a separate sheet place `sub_issue` on Rows and count/rate on Text. Missing source sub-issues are the explicit category Unknown. Do not combine similar category labels.

Stop and explain the grain, numerator and denominator before proceeding. This is a practice checkpoint, not a completed assessment.

## Rebuild the five shared controls

Use string parameters with List allowable values. Add all values from the named field, then the explicit All choice. Current defaults:

| Parameter | Values | Default |
|---|---|---|
| Account type | `sub_product` plus All account types | All account types |
| Issue | `issue` plus All issues | All issues |
| Company | `company` plus All companies | All companies |
| Month | `received_month` plus All months | All months |
| January sensitivity | Baseline; Exclude January; Exclude January top two clusters | Baseline |

Create a Boolean calculated field named Selected cohort:

```text
([Account type] = "All account types" OR [sub_product] = [Account type])
AND ([Issue] = "All issues" OR [issue] = [Issue])
AND ([Company] = "All companies" OR [company] = [Company])
AND ([Month] = "All months" OR [received_month] = [Month])
AND (
 [January sensitivity] = "Baseline"
 OR ([January sensitivity] = "Exclude January" AND [received_month] <> "2025-01")
 OR ([January sensitivity] = "Exclude January top two clusters" AND [january_top_cluster] = 0)
)
```

In the editor, insert parameter fields from the Parameters pane to disambiguate names from data fields. The generated workbook uses fully qualified `[Parameters].[Issue]`, etc.

Create Selected complaints as `ZN(SUM(IF [Selected cohort] THEN [complaint_count] ELSE 0 END))`. Repeat with not_timely and has_relief for Selected not timely and Selected relief. Change rates to divide those selected aggregates by Selected complaints, only when that denominator is greater than zero. These conditional aggregates preserve a visible zero result.

Use Selected cohort=True on monthly, issue and sub-issue breakdowns. **Do not add that row filter to KPI, selection-note or reset sheets.** Otherwise zero matches can erase the note/reset. Show a text note when selected count is zero, warn below30, and explain the denominator otherwise. Add a small-group star to issue/sub-issue labels below30; it is a communication threshold, not a significance test.

## Assemble two pages

Make Overview and Investigation, each 1200 × 850. Use a readable heading, five controls and the five KPIs on both pages. Overview contains the two monthly charts. Investigation contains issue counts/rates and a scrollable sub-issue table. Format row headers with sufficient width and wrapping; use Fit Width for the lists. State source limitations and the proposed internal validation step without requiring hover. See the delivered screenshots for exact layout.

Do not create separate parameters per page: both pages must use the same five objects. Company is a selector, not a ranking. Bar selection is not wired as a cohort filter.

## Build a reset that also works on an empty view

1. Create the dimension Reset label with the constant string `"Reset view"`, and five constant dimensions: Reset Account type=`"All account types"`, Reset Issue=`"All issues"`, Reset Company=`"All companies"`, Reset Month=`"All months"`, Reset January sensitivity=`"Baseline"`.
2. Make an unfiltered Text worksheet containing Reset label. Place each reset constant on Detail. Add it to both dashboards.
3. On each dashboard, choose Dashboard → Actions → Add Action → Change Parameter. Source is the Reset view sheet, run on Select, corresponding source reset constant → target parameter, aggregation Attribute, and keep current value when selection clears. Repeat for all five parameters.
4. For repeat clicks, add a constant dimension Clear reset selection=`"Clear selection"` to Detail. Add a filter action whose source and target are only Reset view. Run on Select, clearing selection shows all values, Selected Fields mapping Clear reset selection (source) → Reset label (target). Their values differ: the selected mark clears and the reset sheet returns. Do not target the other dashboard sheets.
5. Change controls, reset, change them again, and reset again with one click. Try all five controls together on an empty view. Confirm it stays on the same dashboard and restores the five defaults.

## Package and accept

Use File → Save As for a local Tableau Packaged Workbook (.twbx), not Save to Tableau Public. Package the Hyper. Copy the TWBX to a separate directory and open it there. Confirm the source is its extracted Data/tableau-complaints.hyper, then check the values in the package evidence table.

Native acceptance: baseline; Managing an account; June; Capital One + Managing an account; Checking + Managing an account; both January modes; a company with fewer than30 complaints; zero matches; Unknown sub-issue; cross-page continuity; repeated reset. Baseline must return to84,194 /609 /12,977. No percentage should appear for an empty denominator. Capture the final workbook/package hashes and screenshots only after the final build.

Use [Tableau's parameter guide](https://help.tableau.com/current/pro/desktop/en-us/parameters_create.htm) and [parameter-action guide](https://help.tableau.com/current/pro/desktop/en-us/actions_parameters.htm) for the editor dialogs. Window → Presentation Mode hides authoring panels for the walkthrough.

## Personal teach-back gate

Without reading a script, explain the selected grain, both rate definitions, fixed January flag, why company counts are not rates, one SQL trace, empty-state behavior and AI contribution. Rebuild one sheet and one calculation, then diagnose an intentionally wrong denominator. Record only observed results; this release does not certify personal mastery.
