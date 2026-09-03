# Two-Minute Demo Script

Target speaking time: approximately two minutes at a calm pace.

> This is my Consumer Complaint Operations Dashboard, an independent portfolio
> project built from the CFPB's public Consumer Complaint Database.
>
> I built it to answer one practical question: with public complaint data, what
> should an operations analyst review first? It uses all 84,194 published
> checking and savings complaints received in 2025.
>
> A Python and pandas pipeline keeps only the needed fields, checks the data,
> and stores one complaint per row in SQLite. SQL calculates the metrics. The
> dashboard needs no account or backend, so anyone can open it.
>
> The default view shows complaint volume, responses marked not timely,
> reported-relief response mix, and issue concentration. Managing an account is
> the largest issue at 44,959 complaints, or 53.4 percent. Deposits and
> withdrawals is its leading detail, so I would review that workflow first. The
> data identifies a starting point; it does not prove the cause.
>
> I can filter the complete view by month, account type, issue, or company.
> January has 18,367 complaints, but two company-and-issue combinations account
> for 62.3 percent of them. Without those combinations, January is only 1.14
> times the other-month median. I would investigate those clusters instead of
> assuming there was a system-wide staffing problem. I can also narrow the 609
> responses marked not timely for review.
>
> The main limitation is that complaint counts are not company defect rates.
> The public data has no customer, transaction, or market-share denominators, so
> I would not use it to rank companies.
>
> I documented the requirements, metric definitions, and handoff. Automated
> checks stop invalid data, reconcile the figures, and test the filters and
> layouts in a real browser.
