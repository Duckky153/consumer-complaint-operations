# Two-Minute Demo Script

Target speaking time: approximately two minutes at a calm pace.

> This is my Consumer Complaint Operations Dashboard, an independent portfolio
> project built from the CFPB's public Consumer Complaint Database.
>
> I started with the operating question, not the charts: where should a
> risk or operations analyst focus internal validation first when only
> external public signals are available? I bounded the analysis to every
> published checking or savings account complaint received in 2025—84,194
> records.
>
> The architecture is intentionally simple. A Python 3.12 and pandas pipeline
> reads an allowlist of structured CFPB fields, normalizes dates and categories,
> runs data-quality checks, and writes a sanitized local dataset. SQLite holds
> one complaint per row, and checked-in SQL views calculate the baseline
> metrics. A build step generates a compact local JavaScript data snapshot
> consumed by a static HTML, CSS, JavaScript, and Chart.js site. There is no
> backend, account system, cloud database, or runtime data request, so the page
> works when opened directly or hosted on GitHub Pages.
>
> The default view shows published volume, response exceptions, reported-relief
> response mix, and issue concentration. Managing an account represents 44,959
> complaints, or 53.4 percent, and still leads after excluding January.
> Deposits and withdrawals plus debit and ATM-card problems together represent
> 32.3 percent of all complaints, so those are my first internal-validation
> lanes. This identifies questions; it does not prove root causes.
>
> I can filter the complete view by month, account type, issue, or company.
> The dashboard does more than flag January's 18,367 complaints. Two
> company-issue clusters contribute 11,444, or 62.3 percent. Without them,
> January is only 1.14 times the other-month median. That tells me not to turn
> the spike into a broad staffing conclusion. It also shows 609 not-timely
> responses, with the June peak concentrated in one source company label.
> Those are focused validation leads, not rankings.
>
> The most important limitation is that complaint counts are not company defect
> rates. The data lacks customer, account, transaction, and market-share
> denominators and is not a statistical sample of consumer harm.
>
> This was AI-assisted. I defined the business outcome, requirements, controls,
> architecture boundaries, and release gates. AI accelerated implementation.
> I verified the data, SQL definitions, requirement-linked tests, and the
> handoff. The quality controls reject impossible data and preserve unusual
> patterns as warnings; they do not silently clean away inconvenient evidence.
