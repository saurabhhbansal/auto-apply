# A Bullet that can wrap, and how the budget learns what it cost

**Status:** accepted

## Context

Map #47 gave, at charting, that a Bullet **may run to a second typeset line** — the maker's call,
taken over keeping every Bullet to one line and fixing the prose inside 103 characters, and taken
knowing it costs a full line off the budget each time. `0024` settled the other half of the same
map's arithmetic: the slot cap rises to 6 and the ranking window stays at 3.

Neither decision says how the page budget ever finds out what a Bullet cost, and the pipeline as
built is shaped so it cannot.

### The loop closes on itself

A Bullet's height is a constant today — one line, guaranteed by the `CHARS_PER_BULLET` lint in
`render.py`, which fails the run on an over-budget line. That constant is what lets the **Packer**
allocate slots *before* Opus writes a word. Make the height a function of the prose and the order
inverts:

```
pack ─► allocate slots ─► compose ─► cost is now known ─► which changes the allocation
  ▲                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

**`0021` solved a version of this, and the solution does not transfer.** It composes the Skills
**Category rows** *between* the two packing passes and reconciles, which works because a row's
content does not depend on the allocation: Opus can write the rows without knowing what the page has
room for. A Bullet is the opposite — Opus composes exactly the Bullets the allocation names, in the
order it names them (`tailor/SKILL.md` §5, and `render.py` checks all three). There is no point in
the pipeline where Bullets can be written and then costed.

### What the run actually looks like

All twelve Bullets in `runs/zs-btsa` are **98–103 characters**. Not some of them: all of them, jammed
against the cap. The complaint that started the map is structural rather than incidental.

At a cap of 6 the same bank wants 19 slots, against a 32-line budget of which 8 go to the four Entry
headers — so **5 lines** are left over. That residue, not the whole budget, is what this ADR spends.

### What a wrapping Bullet costs, measured

Measured against the committed template by the `\pagetotal` interior-gap method `docs/calibration.md`
already uses for the interior elements:

| characters | Bullet height | typeset lines |
|---|---|---|
| 40 | 14.00pt | 1 |
| 103 | 14.00pt | 1 |
| 110 | 14.00pt | 1 |
| 150 | 24.06pt | 2 |
| 200 | 26.00pt | 2 |
| 250 | 38.00pt | 3 |

**A Bullet's second typeset line costs 12.00pt** — the same number as `SKILLS_ROW_WRAP_PT`, for the
same reason: it is `\small`'s bare leading, because `\resumeItem`'s `\vspace{-2pt}` is charged once
per item and not once per line. The *first* line is 14.00pt rather than 10.00pt only because Bullets
sit in a stock `itemize` while the Skills list zeroes its glue (`templates/resume.tex.j2:198`).

Two readings of that table are worth keeping. The 150-character row measures 24.06pt against the
200-character row's 26.00pt for the same two lines — the difference is the depth of a descender on
the last line, so **26.00pt is the worst case** and the one a budget must charge against. And 110
characters still typesets on one line, because `CHARS_PER_BULLET` is measured from the *widest*
realistic prose rather than an average; the formula over-counts and never under-counts, which is the
direction `0021` §3 already argued for.

## Decision

### 1. The Packer grants the second line; Opus writes to the width it is given

The allocation names which slots are two lines wide, and composition writes into that width. The
order stays **allocate, then compose**, so block height remains true by construction and the
Checkpoint stays where `0021` §6 put it — after the last pass, describing the page that renders.

**Rejected: Opus asks for the second line**, a per-Bullet width emitted alongside the prose the way
`--skills-rows` carries the row shape, reconciled by a third pass. It reads as the closest fit to the
existing seam and it is the wrong shape twice over. The Skills analogy breaks because a row can be
composed *between* the passes and a Bullet cannot, so the re-costing can only land after the
Checkpoint — the exact position `0021` moved the Checkpoint out of. And it makes the page a function
of **the prose**: a rephrase four characters longer would cost a line and drop somebody's evidence.
`0021` conceded that coupling on Skills rows and called it a real narrowing, but the loss there was a
skill in a breadth list. Here it is the expensive real estate, and it inverts the direction the whole
system runs in.

**Rejected: a third pass in any form.** Same reason. Every post-composition re-costing puts the
Checkpoint in front of a page that then changes.

**Rejected: nothing wraps, and `CHARS_PER_BULLET` simply rises.** Recorded so it is refused on
the record rather than forgotten. The line width is a **measurement of the Template**, not a policy —
raising it means changing the template's geometry and re-calibrating every constant, and it would
widen *every* Bullet rather than the ones that need it.

### 2. Evidence outranks room

**A slot never loses its place because it asked to be wide.** When the lines run short the *width* is
surrendered first and the Bullet is written to one line; only when every width has been given up does
the page start dropping Bullets.

This is the **Elastic block** rule applied one level down. An entry that will not fit drops its own
lowest Bullet; a slot that will not fit drops its own second line first. The failure it forbids is
the one the maker named at the grilling: a highly relevant Bullet dropped *for having wrapped*, in
order to seat a marginal one below it. Under this rule that cannot happen — the relevant Bullet is
rephrased into one line and stays.

Mechanically it is a **width pass that runs after `pack_page`**, spending only the lines the evidence
did not want. That placement is what makes the rule true rather than merely intended, and it buys
three things: the width pass touches neither the **Experience floor**'s reservation, nor the shrink
rule, nor the uniform minimum block, so whatever #49 decides about sharing slots composes with this
unchanged.

**The bill, stated plainly: on a full page nothing wraps.** The room comes out of what is left after
the evidence is seated, so the crowded page — the one carrying the most evidence — is also the one
where every sentence is back at 103 characters. That is the trade: evidence over prose, at the
margin.

**Rejected: wraps compete with slots for the same lines.** It is the honest reading of "it costs a
full line off the budget", each line does exactly one job, and the trade — *one more piece of
evidence, or one sentence that reads properly* — becomes a real editorial choice. It loses because
the maker will not pay for it in evidence: a claim losing its slot because a *different* claim's
sentence was declared wide is the wrong thing for this page to do.

### 3. The want is a `width` column in `scores.md`

```
| entry | claim | type | ended | score | width | reason |
```

`width` is `1` or `2`, validated as strictly as `score` — anything else stops the run and names the
row, like every other column in that table. Opus declares it **at scoring time**, judged on the
claim's substance: can this be said properly in one line, or not.

Three properties earn it that position. It is judged **before Opus knows the allocation** and before
a word is composed, so it cannot be steered toward the Bullet Opus happens to like. It keeps the seam
the system runs on — Opus judges, the script counts — with `pack.py` still reading exactly one file.
And it costs nothing in determinism: `scores.md` is written before any pass and is a function of the
bank and the JD alone.

**Rejected: a score threshold**, claims at or above some score getting the room, decided inside
`pack.py` from the table as it stands. It needs no new column and nothing can game it, and it answers
the wrong question. A Claim's score says *how well this fits the JD*; width has to say *can this be
said in 103 characters*. Those come apart constantly — `american-express/c4` scores 1.00 and may be
sayable in sixty characters, while a 0.60 claim can be a two-clause monster.

**Rejected: the maker decides, at a Fork.** A width question on the Checkpoint of every run, over a
page with five lines to give. Far too noisy for the size of the call.

**A line count, not a character estimate.** The estimate was the maker's first instinct and the
conclusion is what gets recorded, because a character count would put **two numbers on one job**.
`render.py`'s lint has to enforce one of them: enforce the estimate and Opus asking for 120 then
writing 145 fails a run over prose that fits the page perfectly; enforce the derived line count and
the estimate is decoration. The Packer has exactly one question — one line or two — and every
character estimate collapses into it through `ceil(chars / CHARS_PER_BULLET)`. Line counts are also
already the currency at this boundary: `--skills-rows 1,2,1,1` carries typeset line counts, and
`tools/lengths.py` is what turns characters into them.

**The schema is the cap.** A `width` of 3 is refused at parse rather than clamped, which is where
`MAX_ROW_LINES = 2` put the equivalent line for Skills rows.

**What this ADR does not settle: *when* a claim deserves to ask.** That is a rubric line and it
belongs beside the composition rubric #51 is rebuilding. This ADR settles only that the want exists,
lives in `scores.md`, and is the Packer's input.

### 4. The residue goes in claim-score order

Descending by claim score, claim id ascending on a tie — `Claim.order_key`, the ordering the Packer
already runs on, and the tie `claim_tie_log` already knows how to report.

Every contender has already declared it needs the room, so score is deciding **precedence among
equals in need**, which is the thing score is good at. On `runs/zs-btsa` there are exactly five claims
at 1.00 and exactly five lines of residue, so the room goes to `american-express/c4,c5,c6`,
`xlscout/c3` and `auto-apply/c7`.

**The consequence, recorded rather than smoothed over:** `sweatpact` never gets a wide line on any
run, because its three claims all sit at the 0.50 **Bullet floor**. Its Bullets are the *hardest* ones
to write — a 0.50 claim is where the connection to the posting has to be made carefully — and they
are permanently denied the room to make it. What keeps this acceptable is that nothing is lost by it:
a width grant is a want, not evidence, and `sweatpact` writing to 103 characters is exactly today's
behaviour.

**Rejected: one width per placed entry before any entry gets a second.** It produces an evener page,
and it introduces a second ordering principle into the Packer — the same argument #49 is having about
slots, decided here in miniature and in a different currency, with a real risk of the two landing on
opposite rules.

### 5. A two-line Bullet is charged two lines, and `config.py` gains no name

26.00pt at worst against 28.00pt charged: over-charges by 2.00pt, never under-promises.

`tests/calibration/probe.py` gains one check — **a two-line Bullet never measures above
`2 x BULLET_LINE_PT`** — and `docs/calibration.md` records the 12.00pt in its measurement block as a
fact rather than as a name.

**Rejected: a `BULLET_WRAP_PT = 12.00` constant.** Symmetrical with `SKILLS_ROW_WRAP_PT` and dead
weight: nothing would ever spend it, because `pack.py` charges the integer 2 rather than points.
`config.py` is the set of numbers the Packer and the Renderer read, and a number neither reads is one
more thing the next calibration has to keep true for no return. The check is what actually protects
the page — if a font or margin change ever pushed that second line above 14.00pt, charging 2 would
begin over-promising and the failure would surface as a two-page PDF blaming the constants. This is
the shape of the two checks already there (*an Education row costs exactly `ENTRY_HEADER_LINES`*, *one
more Skills row always costs the same*), both of which hold a measured fact without naming it,
because the fix on failure is to tighten the template.

**Rejected: charging Bullets in points, as the Skills section is charged.** `0021` §1's stated
exception exists because a Skills row is never charged alone. A Bullet *is* the unit, and the reclaim
does not pay: 2pt per wrap, so five wraps on the real page reclaim 10pt — under one line — in
exchange for making the entire page budget fractional.

### 6. The granted width rides on the claim line in `allocation.md`

```
- american-express/c4 — 1.00 — 2 lines — Monthly business-review data cuts built off …
- american-express/c7 — 0.85 — 1 line — Built the whole system through Claude Code skills …
```

Written on **every** claim, wide or not: a field that is always present is one a reader cannot misread
as defaulted, and it makes the parse uniform.

`render.py` reads the width from the allocation rather than from `scores.md`, and the distinction is
load-bearing — a *declared* want is not a *granted* line, and only the allocation knows which wants
survived. The width sits against the claim it belongs to because `allocation.md` is *"a document for a
person that a script also reads"*.

**Rejected: the widths as a positional list on the entry heading**, mirroring `--skills-rows`. One
parse point per entry instead of per claim, at the cost of making a human count list positions against
the bullets below.

**The cost, recorded the way `0023` recorded its equivalent.** This **narrows `parse_allocation`'s
"the prose is ignored on purpose" property**. Today only the ref is read and everything past the first
em-dash is free text; now the claim line's third field is contract, and changing its wording in
`pack.py` means changing the regex and the fixture in `tests/test_render.py`. That is the second place
`allocation.md`'s wording is load-bearing, after the `Skills:` line.

Then the length lint generalises to one line rather than a new check:

```python
if len(bullet.text) > width * config.CHARS_PER_BULLET:   # was: > config.CHARS_PER_BULLET
```

Same failure, same message shape, same remedy — *rephrase this one Bullet N characters shorter*. It is
still never truncated and never dropped.

**Composing under the granted width does not fail.** It wastes whitespace and cannot over-promise, and
failing a run because a sentence came out crisp would be absurd. `tools/lengths.py` reports it as a
finding, the way it already flags an over-cap Skills row. The wasted stub — a slot granted two lines
and filled with 110 characters — is a **rubric** failure rather than a schema one (*if you take the
second line, use it*), and it belongs with #51.

### 7. One aggregate `Room:` line in Silent calls, and the Omission view is unchanged

A width granted or surrendered is a call made by rule rather than by score, so it belongs beside the
shrink lines and the **Skills reconcile**:

```
- Room: 5 line(s) left after the Bullets were seated. Second lines went to
  american-express/c6, american-express/c5, american-express/c4, xlscout/c3,
  auto-apply/c7 in score order. 3 claim(s) asked and were written to one line:
  xlscout/c2, auto-apply/c1, sweatpact/c3
```

One line for the whole pass, **every run**, so its absence never has to be interpreted. The Silent
calls section already prints *"Nothing was decided by rule on this run."* when it is empty, so it is
not a section that fears saying nothing happened — and on a crowded page *"no room to give"* is
exactly the signal that says the page is too full to write well in, which is the complaint that
started this map, surfacing as a line the maker can read.

**Rejected: printing the line only when something moved.** On a full page every declared want is
refused, so the always-on version says so on every run — true the first time and noise the tenth. It
loses because that repetition *is* the signal.

**The Omission view needs no new wording.** #47's fog expected a Claim to be able to lose *"for a
reason no current wording covers — the Bullets above it got long"*. Under §2 that cannot happen: the
width pass runs after packing and spends only lines the evidence did not want, so the set of placed
Claims is fixed before any second line is granted. **No Claim ever loses a slot to a wrap**, and the
three existing reasons still cover every loss.

## Consequences

- **`scores.md` gains a seventh column** and `parse_scores` a seventh validation. Every existing run
  folder's Score table is now malformed, which is correct: a table without widths cannot be packed
  under this ADR, and the parser's rule is that anything it cannot read stops the run and names the
  row rather than being silently defaulted.
- **`tools/pack.py` gains a width pass** after `pack_page`, and `Placement.lines` becomes
  `ENTRY_HEADER_LINES + sum(widths)` rather than `+ len(claims)`.
- **`tools/render.py`**: `PLACED_CLAIM` reads a third field, the length lint multiplies by it, and
  `check_structure`'s guarantee is unchanged — the allocation is still what makes block height true by
  construction.
- **`tools/lengths.py`** reports each composed Bullet against its granted width, flagging both an
  over-run and a granted second line left mostly empty.
- **`docs/calibration.md` gains a probe check** and records the 12.00pt second-line measurement. Its
  constants table does **not** grow: this is the first element measured for the budget's sake that
  earns no name.
- **`tailor/SKILL.md`** §2 tells Opus to declare a width, §5 tells it the width each Bullet is granted.
  The rubric for *when* to ask is #51's.
- **Material determinism holds, undiminished** — and this is the one place the answer came out better
  than #50 feared. Width is a function of `scores.md`, which is written before any pass and is a
  function of the bank and the JD alone. No composed prose reaches selection, so **a rephrase can
  never change which evidence makes the page**. `0021` had to concede that a skill name one character
  longer could wrap a row, cost a line and drop an Entry; the equivalent concession is not owed here.
  The `scores.md` cross-run diff argument and *the bank is the only repair surface* both read exactly
  as they did.
- **This ADR extends `0024` and supersedes nothing.** `0024` set the cap; this sets the height. The
  code for both lands together under #53.

## Addendum, 2026-08-13 — the want became a charge

`docs/adr/0047-the-bullet-is-an-xyz-sentence.md` inverts §6 of this ADR. A Bullet's
declared width is no longer a **want** that `grant_widths` pays for out of what the
evidence left over; it is a **charge** `pack_page` honours at reservation, and
`grant_widths` grants nothing to a non-merge unit.

The reason is `0047`'s and not this ADR's to defend: an XYZ sentence carries three
slots and cannot be composed against a second line that may or may not arrive. What
this ADR decided about *cost* is untouched — a two-line Bullet still costs two
Bullet lines, still measures 26.00pt against the 28.00 it is charged, and the
calibration probe still holds that fact.

**Two of this ADR's findings survive the inversion, and one does not.**

- §2's *a slot that asked and was refused is written to one line, never dropped* is
  **gone**. There is no refusal any more: a unit the page cannot seat at its declared
  width is leapfrogged by `pack_page` in favour of the next one down, and turns up in
  the Omission view rather than on the page at half its room.
- §4's *no Claim ever loses a slot to a wrap* **holds, for the opposite reason**. It
  used to hold because widths were handed out after placement; it holds now because a
  width is part of what a unit costs to place at all, so nothing is ever seated and
  then squeezed.
- §7's *"no room to give" run after run is the page too full to write well in* holds,
  and stops being a complaint. Under `0047` a page with no room left is the normal
  page, because the room went into the sentences rather than being left over from
  them.

One new behaviour worth recording, because a test now pins it: **a charged width is
indivisible, so an odd line can strand.** A page with one line left cannot seat a
two-line Bullet in it. The residue lands on 0 or 1 by the parity of what fitted, where
the grant pass used to run the purse to exactly 0. Neither number can buy a supporting
section, so `0045`'s white-space trigger is unaffected.
