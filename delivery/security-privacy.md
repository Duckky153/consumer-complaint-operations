# Data Quality, Privacy, and Security

## Public-data minimization

The CFPB source is public, but the project republishes only fields needed for
the operating decision.

| Source field | Local sanitized CSV | SQLite | Public data asset | Reason |
|---|---:|---:|---:|---|
| Complaint ID | Yes | Yes | No | Local uniqueness control only |
| Date received / month | Yes | Yes | Month only | Trend and scope |
| Product / sub-product | Yes | Yes | Sub-product only | Scope and filter |
| Issue / sub-issue | Yes | Yes | Yes | Investigation hypotheses |
| Company | Yes | Yes | Yes | Optional volume filter |
| Company response | Yes | Yes | No | Relief is reduced to a flag; raw category is not needed in the browser |
| Timely response | Yes | Yes | Encoded flag | Response-quality metric |
| Date sent to company | Yes | Yes | No | Local chronology control only; not the intended user's operation |
| State | No | No | No | Not needed; lacks population denominator |
| Tags / submitted via | No | No | No | Not needed for the bounded decision |
| Consumer narrative | No | No | No | Unnecessary sensitive free text |
| ZIP code | No | No | No | Unnecessary geography |
| Company public response prose | No | No | No | Unnecessary free text |

## Security controls

- **No secrets:** the source is public and unauthenticated; the project has no
  API key, token, environment secret, or account.
- **No input surface:** the public site is read-only and has no form
  submission, upload, database write, or authentication.
- **No runtime requests:** Chart.js 4.5.1 is pinned and vendored. Dashboard
  data is a generated sibling JavaScript asset loaded before the application,
  so the page works from disk or the same origin without `fetch`.
- **Restrictive browser policy:** the page declares a Content Security Policy
  limiting scripts, styles, images, and fonts to local assets and disabling
  runtime connections.
- **Safe DOM updates:** source-derived labels are inserted with `textContent`.
  The dashboard script does not use `innerHTML`, `eval`, or dynamic script
  construction.
- **Dependency evidence:** the vendored Chart.js file has SHA-256
  `48444a82d4edcb5bec0f1965faacdde18d9c17db3063d042abada2f705c9f54a`.
  Its MIT license is checked in.
- **Pinned Python dependencies:** direct runtime and test dependencies are
  exact versions in `pyproject.toml`.
- **Least privilege CI:** the quality workflow needs read-only repository
  contents. The separate Pages workflow is manual and receives only the
  permissions required to deploy. Its deploy job cannot begin until a fresh
  Python 3.12 pytest and JavaScript syntax job passes.

## Data-quality result

The current real-data build reports:

- 84,194 rows at one-complaint grain;
- zero duplicate complaint IDs;
- zero required-field nulls;
- zero wrong-product rows;
- zero out-of-window rows;
- zero invalid timely values;
- zero negative routing intervals;
- zero missing issue values;
- 51 missing sub-issue values, retained as `Not specified`; and
- one disclosed temporal warning: January 2025 has 18,367 complaints, more
  than twice the 6,108.5 monthly median.

Sub-issue sparsity is disclosed rather than imputed. The January warning is
analytical context, not a deletion or a failed source-integrity check.

## Residual risk

- Public categorical combinations can still describe small groups. The
  browser asset contains minimized, dictionary-encoded record-level analytical
  vectors so filters work offline; it is not aggregate-only. It contains no
  complaint identifiers, exact routing times, raw response categories,
  narratives, ZIP codes, state, tags, channel, or free text. Interpretive copy
  is withheld below 30 selected complaints.
- The Content Security Policy is declared in HTML because GitHub Pages does not
  provide project-controlled response headers. Some directives, such as
  framing control, are stronger as HTTP headers and therefore remain a hosting
  limitation.
- Vendoring reduces runtime supply-chain exposure but creates an explicit
  maintenance obligation to review future Chart.js security releases.
- A later CFPB correction or consumer narrative opt-out can change the source
  snapshot. The manifest hash makes that drift visible.
