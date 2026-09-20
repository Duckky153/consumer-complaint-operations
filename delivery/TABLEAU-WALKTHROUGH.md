# CCO — discovery and five-minute Tableau walkthrough

This is the supporting portfolio project for Salesforce JR358388. Hotel Booking Decision Studio is the flagship. This is an independent public-data investigation, not a Salesforce/customer deployment or an employer-assigned exercise.

## Open and orient

Open `tableau/Consumer Complaint Operations.twbx` in Tableau Desktop Public Edition. It includes its data and needs no Tableau account for local use. Choose Window → Presentation Mode for a clear view. The two tabs are Overview and Investigation. Use the left-side dropdowns and January radio list for filtering; clicking bars selects marks but does not change the shared cohort. On Mac, dropdowns support typing a name prefix. Company has many labels; typing is easier than scrolling.

## Discovery before demonstration

Ask the analyst: “Which process decision are you trying to make, who owns it, and what case outcomes and transaction denominators can you validate internally?” Ask the executive: “What evidence would justify a targeted review, and what would make you reject that hypothesis?” Ask the data owner: “Who owns category definitions, source changes, access and refresh failure handling?”

State the agreed decision: choose an investigation to validate, not rank companies or infer staffing demand. Ask whether the audience wants the short interpretation or the data trace. The public dataset cannot supply internal business outcomes.

## Executive path — about two minutes

1. **Reset view.** Baseline: 84,194 published complaints, 609 not timely (0.72%), and 12,977 relief responses (15.41%). Timeliness and relief are separate indicators. The denominator is all selected complaints, not customers.
2. **Investigate January.** Original January volume is 18,367. Choose “Exclude top 2 groups” (the full-snapshot company/issue pairs): January becomes 6,923 and the annual selection is 72,750. The fixed clusters account for 11,444 January observations. Choose “Exclude January” separately: annual selection is 65,827. These are sensitivity views; original data is preserved.
3. **Recommend a next evidence request.** Reset and choose Managing an account: 44,959 complaints. Request current internal case outcomes and transaction volumes before proposing a process change. No savings or causal improvement has been measured.

Close: “This identifies where to ask better questions. It cannot establish a company's defect rate, consumer harm or a current operating failure.”

## Analyst path — another three minutes

1. With Managing an account selected, switch to Investigation. The same 44,959 / 363 / 7,114 counts carry across. Scroll the sub-issue table: Deposits and withdrawals has 17,379 complaints; similarly named source categories remain distinct.
2. Choose CAPITAL ONE FINANCIAL CORPORATION: 6,428 / 0 / 176. Explain why 0 not timely in this selection does not establish company quality or a comparative performance rate.
3. Reset. Select June: 5,557 / 135 / 1,030; not-timely rate 2.43%. Compare the figure to `evidence/tableau-package-verification.json`, where independently computed source SQLite values match the packaged Hyper engine.
4. Reset. Choose TRUEBILL, INC: 2 complaints, 0 not timely, 1 relief response. The small-base warning explains why 50% relief mix is fragile. Choose an impossible combination to show zero counts and undefined (blank) rates, not a misleading 0%.
5. Reset again. Explain the ten-field allowlist and fixed cluster flag, then state the refresh and sharing boundaries from TABLEAU-ARCHITECTURE.md.

## Questions to be able to answer

- Why SUM(flags)/SUM(complaint_count), not AVG(group rates)? Groups have different denominators.
- Why retain January? Its concentration is a question to investigate; removing original observations would hide evidence.
- Why no company leaderboard? Customer/transaction exposure is absent.
- Why no live integration? The implemented artifact is a pinned local extract; enterprise architecture is a proposal requiring discovery and separate access authorization.
- What did AI do? Codex substantially implemented and tested the pipeline/workbook/docs. Personal hands-on understanding must be demonstrated separately.

No rehearsal result is claimed. Use the rebuild guide to make the walkthrough personally defensible.
