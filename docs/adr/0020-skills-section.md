# The Skills section: per-JD category rows, bank-owned identity, run-owned case

**Status:** accepted

## Context

Map #34 gave, at charting, that the Technical Skills section becomes **categorised rows** — one
row per category with a bold label — and that the Packer **reserves four rows and hands the
unused ones back** in a second packing pass. Neither of those is decided here. What was left open
was everything about what goes *in* the rows: where the categories come from, what a skill is
called, whether the JD filter survives four rows instead of one line, and what `bullets.md` and
`render.py` exchange.

### What the bank actually holds

25 Claims carry a free-form `skills:` line; 39 distinct skills across them. Roughly a third are
not technologies at all:

```
layout preservation   session management       business rules encoding
PDF processing        PDF layout               data standardization
fuzzy string matching model evaluation         web application
Cross-team coordination   User acceptance testing   Debugging
```

Eight are lowercase phrases (`prompt engineering`, `layout preservation`, `model evaluation`,
`session management`, `web application`, `business rules encoding`, `data standardization`,
`fuzzy string matching`); the rest are proper nouns in their own correct casing — `pytest`,
`iOS Shortcuts`, `PyMuPDF`, `Next.js`.

### What the ZS run actually did

The run that motivated this shipped:

```
Python, Google BigQuery, prompt engineering, Custom GPT configuration, Claude Code, Google Gemini API
```

Exactly 103 characters — dead on `CHARS_PER_BULLET`. The ticket recorded this as *the filter
yielded six*. It did not: `runs/zs-btsa/gaps.md` lists Excel, TypeScript, PostgreSQL and model
evaluation as having **passed** the filter and then been cut by the truncation. The filter yielded
ten or more and one line held six. **Truncation was the binding constraint, not the filter** — and
that inverts the case for loosening the filter.

What genuinely reached nothing on ZS was `Next.js`, `Supabase`, `LaTeX` and `pytest`. On a
BI-and-analytics consulting posting that is the filter working.

### One correction to the ticket

The ticket states that `render.py` checks each listed skill appears **verbatim** in its Claim's
`skills:` line. It does not — `tools/render.py:827` lowercases and strips both sides:

```python
carried = {name.strip().lower() for name in claim.skills}
if skill.name.strip().lower() not in carried:
```

Case is *already* outside what the check constrains. That collapses most of the spelling question
before it is asked.

## Decision

### 1. Categories are named per JD, from the posting's own vocabulary

Not a fixed taxonomy owned by the repo. A fixed `Languages / Frameworks / Data & Cloud / Tools`
set has **no row for a third of the bank** — `Cross-team coordination` and
`User acceptance testing` have nowhere to go, and those are exactly what a diffuse consulting
posting asks for. The fixed option therefore either drops them or grows a catch-all row that
becomes a junk drawer.

Consistency across runs is a weak requirement here: two résumés are never compared side by side,
but every one of them is scanned against the posting it was written for.

Two guardrails, because per-JD naming is where a padded row gets invented:

- **A row label must be traceable to words in the JD.**
- **A row needs at least two skills, or it is not a row.**

A skill appears in **exactly one** row. Listing `Python` under both `Languages` and
`Data & Analytics` spends scarce characters twice and reads as padding.

### 2. The run categorises cold — guardrails only

No default taxonomy in the `tailor` skill, and no worked examples.

A default list in a prescriptive file gets read as *the* answer, and per-JD naming would decay
back into a fixed taxonomy by habit. Worked examples were the stronger alternative — §5 teaches
everything else that way — but a real example means the maker's own bank and postings inside
`.claude/skills/`, which ships in the public repo: `0019` drew that boundary. Building the
examples out of the fictional fixture bank instead avoids the boundary and teaches the wrong
lesson, because the fixture bank does not have the real bank's vocabulary problem — a third of it
not being technologies at all is the entire difficulty.

### 3. The bank owns a skill's identity; compose time owns its case

Two different things were tangled under "the one true spelling."

**Identity** — is `Google BigQuery` the same skill as `BigQuery`? Is `PostgreSQL` the same as
`Postgres`? **The bank decides, and compose time may not touch it.** No expanding, no contracting,
no respelling, no re-wording. This keeps `check_skills_trace` exactly as strict as it is, and that
strictness is load-bearing: the calibration run's `Python (helios-payments/c2)` — against a Claim
whose `skills:` line reads `PostgreSQL, SQL, Airflow`, with Python two entries away — is caught by
this check and by nothing else. Any looser match reopens that hole.

**Case** — `prompt engineering` sitting among `Python`, `Google BigQuery`, `Claude Code`. This is
what made the ZS line fail to read as one list, and it is the smaller problem wearing the bigger
one's clothes. It changes no identity, and the check already ignores it.

So compose time normalises **case and nothing else**:

> Capitalise the first letter, unless the name's own correct form starts lowercase.

`prompt engineering` → `Prompt engineering`. `pytest` stays `pytest`; `iOS Shortcuts` stays
`iOS Shortcuts`. **Not Title Case** — Title Case is precisely where `pytest` becomes `Pytest` and
`iOS` becomes `Ios`. A proper noun's spelling is not a style choice.

**Nothing changes in `check_skills_trace`, in the bank, in `ingest`, or in `bank-audit`.** The
open question on map #34 of whether the ingestion side has to start caring about skill naming
resolves to **no**.

In practice the mixed-case row largely stops happening on its own, because categorisation groups
practices with practices and proper nouns with proper nouns. What remains is the stranded
lowercase phrase in a row of proper nouns, which is the ZS case, and which the rule fixes.

### 4. "List only what the JD asks for" survives, unchanged — plus a two-row floor

The filter stays as `tailor` §5 states it. Two reasons, and the second is the decisive one:

- It was never the bottleneck. Truncation was (see Context).
- **An unused row hands back to a Bullet.** So letting rows go empty costs nothing, while
  loosening the filter to fill them buys a padded row *with* a Bullet line. That trade only runs
  one way.

Loosening also directly contradicts the rule's own reason: a skill the posting never mentions is
spending a scarce line on nothing.

The diffuse JD that would most struggle to fill four rows is the one decision 1 rescues. ZS's ten
surviving skills against per-JD categories:

```
AI & GenAI          Prompt engineering, Custom GPT configuration, Google Gemini API, Claude Code
Data & Analytics    Google BigQuery, PostgreSQL, Excel, Model evaluation
Languages           Python, TypeScript
Delivery & Testing  Cross-team coordination, User acceptance testing
```

Four rows fill, and the fourth fills **only** because per-JD categories admit the non-technology
skills a fixed taxonomy had no row for.

**The floor:** a `\section{Technical Skills}` heading costs `SECTION_LINES = 2`, so a section with
one surviving row spends three lines to show one. **Fewer than two rows and the whole section
goes**, heading included, and all four reserved lines hand back. The Template already drops the
section when there is nothing to put in it; this extends the same judgement one step.

### 5. `bullets.md` grows a `###` row heading; `skills_line` becomes `skill_rows`

```markdown
## Skills

### AI & GenAI
- Prompt engineering (american-express/c5)
- Custom GPT configuration (american-express/c5)
- Google Gemini API (xlscout/c3)

### Data & Analytics
- Google BigQuery (american-express/c4)
- PostgreSQL (sweatpact/c1)
```

**`SKILL_LINE` does not change.** `- <skill> (<entry-slug>/c<n>)` is byte-identical to today, so
the citation resolution, the trace check and the per-line error messages carry over untouched. The
only new grammar is the `###` row heading, and `HEADING` cannot collide with it: `^##\s+` requires
whitespace after the second `#`, which `### AI` does not have.

Row order on the page is `###` order; order within a row is line order — the JD-prominence
ordering rule now applies within a row.

Two new failures, both naming a line, per the file's governing rule that anything unparseable is a
hard failure: a `-` line with no open `###` above it, and a `###` with no lines under it.

**Rejected:** `- AI & GenAI: Prompt engineering (ref), Custom GPT configuration (ref)` — one file
line per page row, more compact, and it loses the thing that matters most. A single bad citation
would fail a line carrying four skills, and the message could not say which one.

**The Template's hole.** `skills_line` retires. `skill_rows` replaces it: a list of
`{label, text}`, both pre-escaped, `text` pre-joined with `", "` exactly as `skills_line` is
today.

```latex
\BLOCK{if skill_rows}
\section{Technical Skills}
  \resumeSkillsListStart
\BLOCK{for row in skill_rows}
%% AUTOAPPLY:element:skills:\VAR{loop.index}
    \resumeItem{\textbf{\VAR{row.label}:} \VAR{row.text}}
\BLOCK{endfor}
  \resumeSkillsListEnd
\BLOCK{endif}
```

**The marker id is the 1-based row number, not the label** — following the Education row
precedent. A label is run-authored text, and a `%` or a stray character inside a marker comment is
a class of breakage the Template's own preamble warns about. The label is not lost: `render.py`
already carries human wording separately from the marker id, so the Overflow check reports *"the
AI & GenAI skills row"* while the marker stays `skills:3`.

### 6. A sixth Page-budget constant, measured: `BOLD_CHARS_PER_BULLET`

`CHARS_PER_BULLET = 103` is a character count derived from a width — 507.09pt of Bullet text at
4.915pt per character, taken from the widest realistic sentence. **Bold is wider than regular**, so
`\textbf{AI \& GenAI:}` is not twelve characters' worth of line, and charging
`len(label) + 2 + len(text)` against 103 over-promises. Over-promising is the one direction
`config.py` forbids.

So a second measured character count, in the same unit and measured by the same procedure: **how
many bold characters fill one line.** A row fits when

```
(len(label) + 2) / BOLD_CHARS_PER_BULLET  +  len(text) / CHARS_PER_BULLET  <=  1
```

**Rejected:** one flat `CHARS_PER_SKILLS_ROW` measured against a worst-case label — simpler
arithmetic, but a short label like `Languages` would permanently forfeit the room a long one
needed. **Rejected:** charging the label at the plain rate and leaning on the slack that is
already there (the row sits one list level shallower, so it is genuinely wider than a Bullet) —
that is the estimate-instead-of-measure the file forbids in capitals.

`config.py`'s docstring says a sixth constant has nowhere to live. That remark is aimed at
*splitting* `ENTRY_HEADER_LINES` in two so a macro can stop measuring under it — not at charging a
genuinely new element that no existing constant describes.

## Consequences

- **Truncation stops being the binding constraint.** Four skills plus a label runs about 90
  characters against roughly a 103-character budget *per row*. On ZS, nothing would have
  truncated. It becomes an edge case rather than the thing that shaped every run. A skill
  truncated off a row is still a Gap report line — *you have it, the page did not* — unchanged.
- **The two-skill guardrail applies after truncation, not only before it.** A row cut down to one
  skill stops being a row and hands back; if that takes the section under two rows, the section
  goes. The cascade terminates.
- **The Template's invariant #2 must be rewritten.** *"The Skills line is NEVER NARROWER than a
  Bullet, so `CHARS_PER_BULLET` is a safe budget to truncate it against"* stays true about width
  and stops being true about characters the moment a bold label is on the line.
- **`tools/lengths.py` reports one figure per row** instead of a single `skills line` figure.
- **`docs/calibration.md` gains a probe** for the bold character rate, measured the way the plain
  rate was — from the widest realistic label, not an average.
- **`render.py`'s `parse_bullets` returns rows, not a flat skill list.** The `## Skills` heading
  stays mandatory and stays last; its "write the heading with no lines under it" escape hatch
  still works, and now lands on the floor in decision 4 rather than on an empty `\resumeItem`.
- **Nothing about the bank changes**, and neither `ingest` nor `bank-audit` gains a
  responsibility. The bank's genuine redundancies — `LaTeX` beside `TeX`, `PDF processing` beside
  `PDF layout` beside `layout preservation`, `iOS` beside `iOS Shortcuts` — are bank hygiene and
  belong to `bank-audit`, not to how a row is typeset.
- **This ADR supersedes nothing.** It extends `0007` (rendering approach) and leaves `0005`'s
  no-derived-index rule untouched — per-JD categories store nothing, so there is nothing new to
  rot.

## Addendum, 2026-08-13 — §3 gains one bounded exception

`docs/adr/0050-the-posting-names-the-work-it-never-supplies-it.md` §2 relaxes §3's
*no expanding, contracting or respelling* in exactly one direction:

> **Generalisation is licensed. Specialisation is not. Substitution is not.**

A row may carry the posting's term where that term names a **class the bank's skill is
a member of** — `PostgreSQL → SQL`, `Kafka → event streaming`. It may not reach a
sibling (`PostgreSQL → MySQL`), a specialisation (`Python → Django`), or a different
subject. The row still cites the Claim whose `skills:` line carries the specific
instance, so nothing arrives untraceable, and case normalisation is unchanged.
