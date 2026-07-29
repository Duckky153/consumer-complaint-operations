# Executive Findings and Recommendations

All figures below reconcile to the current 84,194-row SQLite build. These are
external discovery signals and validation requests—not claims of causation,
wrongdoing, company performance, staffing need, or intervention impact.

## Executive summary

`Managing an account` is the robust first investigation lane: 44,959
complaints, or 53.4% of the product-year population, and still 55.8% after
excluding January. Its two largest sub-issues—deposits and withdrawals plus
debit/ATM-card problems—total 27,171 complaints, or 32.3% of the year.

The secondary annual pattern is not robust. January contains 18,367
complaints, but two company-issue clusters contribute 11,444, or 62.3%. After
removing those clusters, January falls to 6,923 complaints, only 1.14 times the
February–December median. `Problem caused by your funds being low` ranks
second for the full year but falls to fifth outside January.

Response timeliness is a guardrail rather than the main prioritization signal:
609 complaints, or 0.72%, are marked not timely. June contains 135 exceptions;
96 are associated with one source company label. Reported relief appears in
12,977 complaints, or 15.41%, but relief is a non-directional response
category—not proof of success, fault, or customer satisfaction.

## Finding 1 — The account-management hypothesis survives sensitivity testing

`Managing an account` is the largest issue with 44,959 complaints. Its two
largest sub-issues are:

| Sub-issue | Complaints | Share of all complaints |
|---|---:|---:|
| Deposits and withdrawals | 17,379 | 20.6% |
| Problem using a debit or ATM card | 9,792 | 11.6% |

Together they account for 27,171 complaints, or 32.3% of the full population.
They remain 33.2% after excluding January, so the investigation hypothesis is
not created by the January anomaly.

**Recommendation:** use deposit/withdrawal and debit/ATM workflows as the first
external-signal hypotheses. Request internal transaction and account
denominators, process step and channel, repeat contacts, reopens, resolution
time, consumer feedback, and policy exceptions before choosing an
intervention.

## Finding 2 — January is concentrated, not a general capacity signal

January contains 18,367 complaints, 3.0 times the annual monthly median.
However, its two largest company-issue pairs are:

| January company-issue cluster | Complaints | Share of January |
|---|---:|---:|
| Navy Federal + problem caused by funds being low | 6,970 | 37.9% |
| Capital One + managing an account | 4,474 | 24.4% |
| **Combined** | **11,444** | **62.3%** |

Without those two clusters, January contains 6,923 complaints—1.14 times the
other-month median of 6,076. `Problem caused by your funds being low` is 41.2%
of January and falls from the second-largest annual issue to fifth when
January is excluded.

**Recommendation:** validate the two clusters against source revisions,
incident or campaign context, internal intake, and company-label normalization.
Do not generalize January into a broad staffing forecast and do not interpret
the named companies as a performance ranking.

## Finding 3 — Response exceptions are concentrated in June

609 of 84,194 complaints are marked not timely, a 0.72% exception rate. June
contains 135 exceptions at 2.43%; July contains 87 at 1.36%. One source company
label, Block, Inc., accounts for 96 of June's 135 exceptions and 50 of July's
87—146 of 222 combined, or 65.8%.

**Recommendation:** treat June–July as a focused validation lead. Confirm the
source label, case mix, response-clock definition, and internal chronology
before inferring a broad process deterioration or comparing companies.

## Finding 4 — Reported relief changes the questions, not the ranking

The reported-relief baseline is 15.41%. To avoid cherry-picking, the dashboard
compares relief share only among the six highest-volume issue details. Within
that volume-selected set, debit/ATM-card complaints are highest at 19.73%
(1,932 of 9,792), while overdraft-fee complaints are lowest at 6.66% (653 of
9,811).

The annual baseline is also sensitive to January's two dominant clusters:
those clusters have a 1.05% relief-category share, while the rest of the annual
population is 17.67%.

**Recommendation:** use relief only as response-mix context when forming
questions. Compare like-for-like case types with internal outcomes; do not
treat a higher or lower public relief share as good, bad, successful, or
fault-indicating by itself.

## Company interpretation guardrail

The company filter supports deliberate drill-down, but the default dashboard
does not show a company leaderboard. Company counts lack customer, account,
transaction, market-share, product-mix, and complaint-propensity denominators.
Source company labels are not normalized into corporate families.

## Suggested validation sequence

1. **Validate the robust lane:** deposit/withdrawal and debit/ATM workflows.
2. **Decompose the anomaly:** investigate January's two dominant clusters.
3. **Review exceptions:** validate the concentrated June–July not-timely rows.
4. **Use response mix carefully:** compare relief categories only within
   comparable case types.
5. **Request internal evidence:** denominators, workflow steps, outcomes,
   repeats, reopens, age, resolution time, feedback, and controllability.
6. **Rebuild on a controlled cadence:** record row count and hash and
   investigate unexpected source changes before replacing the snapshot.
