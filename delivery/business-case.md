# Business Case and Intended User

## Business problem

Public complaint data can generate plausible hypotheses without proving what
an institution should change. A useful external diagnostic must distinguish:

- published volume: how many complaints entered the public database;
- movement: when volume rose or fell;
- concentration: which intake categories account for most published volume;
- response signals: whether responses were marked timely and whether they
  reported monetary or non-monetary relief; and
- decision limits: what the dataset cannot prove.

The project therefore answers one bounded question:

> Which public complaint themes and response exceptions deserve validation
> with internal operating data first?

It does not attempt to judge legal compliance, predict consumer harm, rank
companies, measure internal workload or staffing need, or automate complaint
decisions.

## Intended user

**Primary user:** a financial-services risk or operations analyst preparing an
external complaint-signal diagnostic before an internal process-review
workshop.

The analyst needs a default view that identifies robust and anomaly-dependent
signals without interaction, plus a small number of filters for follow-up. The
analyst should be able to identify a high-volume intake category, examine its
sub-issues and response signals, and define the internal evidence needed for
root-cause investigation.

**Repository audience:** a recruiter or interviewer assessing whether the
builder can connect a business outcome to requirements, data controls, simple
architecture, tests, analysis, and a client-ready handoff. The recruiter is
not a product user.

## Intended outcome

The dashboard should support a defensible prioritization conversation:

1. identify which complaint themes remain important after sensitivity checks;
2. decompose unusual periods rather than generalizing them;
3. inspect response exceptions and reported-relief mix;
4. narrow by month, account type, issue, or company;
5. define an internal validation request; and
6. keep limitations visible before acting.

## Success definition

Success is not a polished chart alone. The project succeeds when:

- the data population is exact and reproducible;
- the default view is decision-ready;
- every metric has a plain-English definition and a transparent SQL source;
- data-quality failures stop the build;
- the public artifact minimizes exposed complaint fields;
- requirement-linked tests pass;
- analytical limitations are visible; and
- the owner can explain the project without claiming work he did not perform.
