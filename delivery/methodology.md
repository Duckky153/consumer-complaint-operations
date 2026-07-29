# Methodology and Analytical Limitations

## Population

The analysis includes all 84,194 complaints in the extracted CFPB public
database snapshot where:

- `Product = Checking or savings account`
- `Date received >= 2025-01-01`
- `Date received < 2026-01-01`

The live API's `date_received_max` behaved as an inclusive calendar date. An
early prototype request using the next year's January 1 therefore crossed the
intended boundary. The final pipeline requests `2025-12-31` while retaining
the explicit exclusive `2026-01-01` analytical boundary in configuration and
tests.

## Unit of analysis

One row is one published CFPB complaint, keyed locally by `complaint_id`.
Complaint IDs are used for uniqueness validation but are not included in the
public dashboard data.

## Metric definitions

| Metric | Definition |
|---|---|
| Published complaints | Count of complaint rows in the selected scope |
| Response exceptions | Count and share of rows where CFPB `Timely response? = No` |
| Closed with reported relief | Count and share of rows where the company response is `Closed with monetary relief` or `Closed with non-monetary relief`; this is non-directional response mix |
| Leading category share | Complaints in the highest-volume issue divided by selected complaint rows; when one issue is selected, the highest-volume sub-issue uses the selected-issue denominator |
| Monthly complaint volume | Complaint rows grouped by calendar month of `Date received` |
| January sensitivity | January volume remaining after removing its two largest company-issue clusters, compared with the median of the other 11 months |

`Company response to consumer = Untimely response` is one response-category
value. It is not the same field as `Timely response? = No`; the dashboard keeps
the raw response category outside the public filtering payload and uses the
dedicated timely-response field for exception analysis.

SQL definitions live in [`../sql/metrics.sql`](../sql/metrics.sql). The
default dashboard values are loaded from those SQL views. Client-side filters
recompute the same definitions from the same normalized, dictionary-encoded
records.

The company filter exposes the 53 companies with at least 100 complaints,
ordered by published volume. This is a usability boundary for the control, not
a data exclusion: the default view and every population-level metric include
all 471 companies and all 84,194 complaints. The default dashboard does not
rank companies or compare their response rates.

## Data-quality method

The pipeline:

1. requests only the bounded source population;
2. reads only an allowlist of structured fields needed for the decision or a
   stable control; state, tags, channel, narratives, ZIP code, and company
   public-response prose are never ingested;
3. trims strings and converts empty values to null;
4. parses received and sent dates in UTC;
5. converts complaint IDs to integers;
6. derives received month, route hours for local chronology validation, timely
   flag, and relief flag;
7. sorts by complaint ID for deterministic output;
8. stops on critical contract failures; and
9. writes a quality report and source manifest before generating the dashboard.

Stable automated checks cover:

- required schema;
- complaint-ID uniqueness;
- required-field completeness;
- date-window validity;
- exact product scope;
- timely-field allowed values;
- route-date consistency, including a hard failure for negative intervals;
- monthly volume profiling with a warning above twice the annual monthly
  median;
- source hash and row-count provenance; and
- privacy exclusions in public output.

The browser asset contains minimized, dictionary-encoded record-level
analytical vectors so all four filters can work offline. It is not
aggregate-only. Complaint IDs, exact routing time, raw response category,
narratives, ZIP code, state, tags, and submission channel are absent from that
public asset.

## Analytical limitations

1. **Not a statistical sample.** CFPB states that published complaints are not
   necessarily representative of all consumers' experiences.
2. **No exposure denominator.** Company counts are not divided by customers,
   accounts, transactions, product usage, or market share.
3. **Complaint propensity varies.** Consumers differ in awareness, access,
   willingness, and ability to file.
4. **Publication rules shape the data.** Only complaints eligible for
   publication enter the database, and publication timing can lag.
5. **Consumer accounts are not independently verified by this project.**
   Narrative text is excluded, and the dashboard does not judge factual or
   legal merit.
6. **Timely is a source field.** The project does not reconstruct the CFPB's
   operational timeliness determination.
7. **Relief is a response category, not proof of fault.** Monetary or
   non-monetary relief does not by itself establish wrongdoing or consumer
   satisfaction.
8. **Category definitions can change.** CFPB product and issue taxonomies have
   changed over time. The analysis stays within one completed calendar year to
   reduce cross-era comparison risk.
9. **Static snapshot.** The public site is not a live operational connection.
   Rebuilding may capture later corrections or opt-outs and therefore produce
   a new hash or row count.
10. **No causality.** Trends and differences identify areas for investigation,
    not causes or expected intervention effects.
11. **January 2025 is unusual.** Its 18,367 complaints are 3.0 times the
    calendar-year monthly median of 6,108.5. The source data alone cannot
    distinguish a true event, coordinated filing activity, or publication and
    processing effects, so the spike is retained and flagged rather than
    removed or labeled seasonal.
12. **Not internal workload.** Published complaints do not measure a
    company's complete case inventory, backlog, staffing demand, process
    ownership, or service-level performance.
13. **Intake categories are not root causes.** CFPB issues and sub-issues are
    consumer-selected intake labels. They generate hypotheses for
    investigation; they do not prove which workflow failed.
14. **Small selections are unstable.** Below 30 selected complaints, the
    dashboard shows exact counts but withholds priority language and qualifies
    rate interpretation.
15. **Taxonomy edge cases are retained.** 553 rows, or 0.66% of the bounded
    product-year population, carry credit-report-style issue labels within the
    checking-or-savings product. The project treats this as source taxonomy
    evidence, not a reason to silently recode or delete the rows.

## Safe interpretation

Use the dashboard to prioritize discovery questions and identify which
internal denominators and workflow outcomes are needed next. Do not use it by
itself to rank companies, claim consumer-harm prevalence, infer legal
violations, forecast future complaint volume, or change staffing or policy.
