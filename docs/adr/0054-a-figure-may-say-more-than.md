# A figure may say "more than", and a year is not a figure

**Status:** accepted

## Context

Two facts came off `runs/auxo-ai` in the same run, for the same underlying reason: the
softening vocabulary had exactly one form, and `check_number_trace` had no idea what a
year was.

**The denominator.** `american-express/c7`'s Evidence says *"over 150 KPIs"*, at
`provenance: estimated`. A Bullet may render an estimated figure only softened, and the
only softened form was `~`. `~150` misstates *over 150*; `150` is flat and refused. So
the figure was unwritable and the line shipped as *"the ~60 KPIs this team owned"* — the
**denominator gone**, on a page whose own rubric (`0039`) calls the denominator the
first fact a Bullet should reach for. The previous run had said *"~60 of a diagnostics
scorecard's ~150 KPIs"*, so this was a regression the rule caused.

**The year.** `american-express/c2` wanted to name the 2026 reporting format. `2026`
traces to the Claim's prose, the Claim is `estimated`, so the check demanded it render
softened. `~2026` is not a thing anyone can write, so the year was dropped.

The year case is the sharper one because **the two halves of `render.py` already
disagreed**. `is_year` exists, is documented as *"a date, not an outcome"*, and had
exactly one call site — in `figure_spans`, which declined to bold it (`0046` §3).
`check_number_trace` never called it and treated the same token as an impact figure.

## Decision

### 1. A lower bound is a softened form

`~N`, `N+`, `over N`, `more than N` and `at least N` all satisfy `check_tier`.

The tier exists to stop a figure being stated **more precisely than its source**. A
lower bound does not do that: *over 150* claims no precision the estimate lacks, and it
is a different and often truer statement than *about 150*. A softening vocabulary with
one word in it makes some true facts unwritable, and unwritable true facts leave the
page — which is the failure this repairs.

**It is not a licence to change the value.** `over 80%` against a claim storing `30%`
traces to nothing and fails exactly as `80%` would.

### 2. A bare year is not an impact figure

`numbers()` skips a match `is_year` recognises: four digits in `YEAR_WINDOW`, no
tilde, no unit, no separator, no decimal point. **One definition, one call site each** —
the emphasis pass and the trace check now agree, where before they contradicted each
other about the same token.

A softening tilde, a unit, a thousands separator or a decimal point still say the maker
wrote a quantity, so `~2,100 lines` is a figure and traces as one.

## Consequences

- **`~150 KPIs` becomes `over 150 KPIs`, and the denominator goes back on the page.**
- **A year may be stated inside an estimated Claim**, which it could not be before.
- **Dates on the page are still governed elsewhere** — an Entry's `ended` is checked
  against the bank, and the Static profile header is the maker's. Nothing here weakens
  that; what it stops is one check treating a date as a claim about magnitude.
- **The blind spot is unchanged and deliberate**: `p99`, `EC2` and `OAuth2` are still
  identifiers rather than figures, by the same lookbehind.
