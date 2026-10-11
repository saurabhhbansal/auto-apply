# The lead crosses the seam as a fact, and the minimum block pays for it

**Status:** accepted

## Context

#75 was charted to ask **who decides the order of an entry's Bullets, now that the first and last are
spoken for**. It named four things to settle: which component owns beat order, whether the closing
beat competes for a slot, what score an opening beat gets, and what all of it does to `0024`'s
ranking window and `0026`'s sharing rule.

By the time the ticket was taken, `0032` and `0034` had answered three and a half of them.

`0032` took **both ends of the arc out of the column**. The lead is not a Claim: not scored, not
cited, never a candidate for a slot. So beat order is not a question — the middle is achievements
only, and achievements are ordered by score exactly as they are today. The closing beat cannot lose
its slot because it never had one. The opening beat gets no score because nothing scores it. And both
ADRs state outright that `0024` and `0026` never learn any of this exists. `0032`'s final consequence
says so in as many words: *"#75 has almost nothing left to decide."*

### What was actually left, and who left it

**One thing was handed over by name.** `0032`'s consequences:

> `pack.py`'s reservation minimum becomes `ENTRY_HEADER_LINES + LEAD_LINES + 1` for an Entry with a
> lead. The Packer learns whether an Entry has one from `scores.md`, which is the only file it may
> read (`0006`); **how that field reaches the table is #75's**.

**One thing arrived after it and was never reconciled.** `0034` §3 charges a merge group its declared
width *"at the reservation phase — before `grant_widths` runs, guaranteed. Not a want."* But
`0026`'s reservation phase hands out exactly **one Bullet line** per Entry; depth arrives in a second,
score-ordered pass. `0034` was written against `0032`, not against `0026`, and it states twice that
`0026` is untouched — so what an Entry is guaranteed when its best unit is a two-line merge was left
open by both.

**And one thing collided.** `0026` §1: *"Crossing the floor buys presence. What an Entry then
competes for is width, never whether it appears."* `0032` §6: *"If room is short, Bullets give way,
not the frame."* Inside one Entry those agree. Across Entries they do not — a 4-line minimum block
seats **8** Entries on a 32-line budget where a 3-line block seats 10, so two Entries would be pushed
off the page by *other Entries' lead lines*, which is the one thing the Entry floor was built to
prevent.

### Everything below is decided against a page nobody has seen

The reservation only binds at the ceiling. The bank has **four** Entries. `runs/auxo-ai` spent 28 of
its 32 lines and left **4 unspent**, with every scored Entry placed. So the reservation has never
once been the thing that decided anything, and on any page the maker has read it never will be.

`0026` was decided blind and said so; this ADR is decided against the same absence and says so again.
What follows is written to keep the arithmetic coherent at a bank size that does not exist yet, and
to be cheap to revisit when one does.

### One fact found while grilling, because it was blamed on the wrong thing

The maker's objection to `runs/auxo-ai` includes the shape of the page — *"6, 5, 4, 3, 2, 1 of that
sort"* — and `sweatpact` rendering a single Bullet at the bottom. The actual allocation is `6 / 5 / 5
/ 1`, and **`sweatpact`'s single Bullet is not the Packer's doing**: four of its five Claims scored
`0.20`, below the Bullet floor, so it earned exactly one slot from `min(6, qualifying)`. There were
four spare lines on that page and nothing `sweatpact` owned could legally take one.

No packing rule reaches that. It is the **Shallow entry** case the map already holds as fog —
*"fewer than three claims — so it can never take three Bullet lines"* — and it is recorded here so
that nobody later reads the stub as evidence about the sharing rule.

## Decision

### 1. The lead is the bank's, and the model may not withhold it

An Entry renders its lead whenever the bank holds a `## lead` block for it. There is no per-run
judgement about whether the lead earns its line against *this* posting.

`0032` §6 already refused to trade the frame for room inside an Entry — *"Bullets give way, not the
frame"* — and a model-side *this JD does not need it* is the same trade wearing a relevance costume.
The lead is also what makes the Bullets legible: an Entry that renders five automations without the
sentence saying they were one cycle is the page #70 exists to stop printing. A discretion that can
suppress that sentence puts a hole in the fix exactly where the fix was aimed.

**What stays the model's is the sentence**, per `0032` §2 — the facts are the bank's, the prose is
composed per run. What is fixed here is only whether the line exists.

### 2. It crosses in a `## Leads` table, one row per Entry, and no reason column

`scores.md` gains a third table. The claims table is untouched.

```markdown
## Leads

| entry | lead |
|---|---|
| american-express | y |
| xlscout | y |
| auto-apply | n |
| sweatpact | n |
```

**Grain decides the shape, and it is the same rule that put merges in their own table.** A merge is
about a *set of claims* and has no per-claim home, so `0034` gave it one. A lead is a fact about an
**Entry**, and an Entry is not a row of the claims table — it is a group of them. Riding as a
repeated column would have followed the `ended` precedent (`0031` §3: *"a COPY of the Entry's own
`ended` field rather than a judgement"*, cross-checked across rows at `pack.py:369` and against the
bank at `render.py:826`), and that precedent is real. It is refused anyway: `type` and `ended` are
denormalised because the table was flat before `0034` made it not, and repeating a per-Entry boolean
across six claim rows is a redundancy invented rather than inherited.

**Every Entry gets a row, `y` or `n`.** Listing only the Entries that have a lead was the shorter
file, and it makes *the model forgot Amex's lead* and *Amex has no lead* the same bytes.
`parse_scores` refuses to skip anything it cannot read, for the stated reason that skipping would
drop a Claim silently from both the page and the Omission view; the same logic holds one level up.
A missing row, a duplicate row, a row for an Entry with no scored Claims, or a value that is not `y`
or `n` is a parse failure naming the Entry, exactly as every other malformed thing in that file is.

**No `reason` column.** `## Merges` has one because a merge is a judgement the model has to defend.
Nothing is judged here, and a reason column would invite the model to argue for a fact. Rule 3's
cross-run diff stays clean precisely because there is nothing to argue: a `y` that turns into an `n`
means *the bank changed*, which is already one of the four things that file is allowed to say.

**Validated against the bank downstream.** `allocation.md`'s Placed heading records the lead it
charged, and `render.py` fails a run where that disagrees with the Entry's `## lead` block — the
`0031` §4 shape, applied to the second bank fact the Packer is handed.

### 3. The lead sits inside the reserved minimum, and the ceiling stops being a constant

The reservation minimum is `ENTRY_HEADER_LINES + LEAD_LINES + 1` for an Entry with a lead and
`ENTRY_HEADER_LINES + 1` for one without. `0032` §6 taken literally.

So an Entry's lead can cost a **different** Entry its place on the page, and the Entry floor's
guarantee is weakened by exactly that much. Three things make it the right trade.

**It is what `0032` §6 says**, and the alternative readings each break something the maker settled
harder. **It keeps `0026` §3's fold** — one reservation pass, one concept, every Entry travelling the
same path through both passes, which is the simplification that ADR spent a section on. And **the
ceiling it costs is already disowned**: `0026`'s own cost section records *"there is a bank size past
which this page shape is simply wrong, and neither this ADR nor any sharing rule can fix it."*
Losing two seats off a ceiling that is documented as broken is cheap.

**What this actually changes in the code is nothing about the ceiling**, because the ceiling was
never written down. `0026` §6 derived it — `PAGE_LINES // (ENTRY_HEADER_LINES + 1)` — and the
Omission view already prints `seated = len(placements)`, a count of what happened rather than a
constant. So `pack.py:909`'s *"the page seated N entries"* needs no edit and stays true. What moves is
`0026`'s **prose**: the ceiling is now a number between 8 and 10 depending on how many placed Entries
carry leads, and it can no longer be derived from the constants alone.

### 4. The guaranteed slot is one line, not one unit

The Entry's reserved Bullet line holds the Entry's best unit **that fits in one line** — its
highest-scoring unmerged Claim, or a two-Claim merge declared at `width: 1`. A `width: 2` merge group
cannot occupy it, and waits for the distribution pass.

**`0034` §3's safety invariant does not reach the reservation.** Its case for *always affordable,
never denied* is **W ≤ N**: *"a merge never costs the page more than its claims cost unmerged."* That
is true against the Entry's full allocation, where three Claims would have taken three lines. It is
**false at the reserved minimum**, where the unmerged Claims would have cost **one** line, because
only one was ever reserved. A merge in the guaranteed slot costs the page more than not merging,
which is the exact thing W ≤ N exists to rule out.

Second: `0034` §2 kept merges out of the claims table specifically so a merge could not move an Entry
score and decide whether the Entry places. Letting a merge widen the minimum block would hand the same
reach back through the other door — a per-run judgement about *this* posting deciding whether some
*other* Entry appears at all. §3 already spends the ceiling on a **bank fact the maker spoke once**;
spending it again on a per-run judgement is a different thing.

**So the general rule for the distribution pass**, which `0034` left implicit: an Entry takes its
units best-first, each charged its declared width, and **a unit that does not fit the lines the Entry
has left is skipped in favour of the next one down.**

That is leapfrogging *inside* an Entry — a lower-scoring unit placing while a higher-scoring one does
not — and it is named rather than smuggled, because `0006` refused leapfrogging between Entries on
fairness grounds. It is accepted here on arithmetic: the alternative is spending the Entry's last
line on nothing. The displaced group's Claims land in the Omission view under the reason that already
exists, *dropped when `<entry>` was shrunk to fit the page*.

### 5. No rule against a lead with one Bullet under it

A lead with a single Bullet beneath it is a synthesis showing one fifth of its evidence — *"automating
it gave back ~17.5 hours a month"* over a line naming one automation. It reads badly and the maker
said so.

**It is not fixed here.** A parity rule — *a lead Entry takes zero extra Bullet lines, or two or more,
never exactly one* — was drafted and refused. It would put a second opinion about how big an Entry
should be into the packing arithmetic, which has no idea what the Entry says; and it would not have
touched the case that prompted it, since `sweatpact` has no lead and lost its Bullets to the floor
(Context).

The question underneath it is real and it belongs to **#77**, in the maker's own words:

> *"We consider an entry a whole thing. If we know that something can be fitted in four lines — four
> bullets, a lead and a header — then we do it in that. We don't have to always go for filling out
> maximum available space."*

That is a sharper statement of #77's brief than *when a middle beat earns its place*, and it is where
the fix belongs: an Entry's size is `min(6, qualifying)` clamped by leftover lines, and both halves of
that are selection decisions, not packing ones.

### 6. The middle stays in score order — #75's own question, answered by not moving

Bullets render in descending Claim score, a merge group ordered by the **maximum** of its members
(`0034` §2). No narrative ordering, no reserved first or last position, nothing composed about the
sequence. `0032` removed both ends of the arc from the column, so the only thing left inside it is one
kind of object, and the Packer's existing order is correct for it.

Written as a decision rather than an omission because #75 was chartered to settle it, and *nothing
changes* is an answer that has to be on the record to stop the next map re-asking it.

## The cost, stated rather than waved past

**A lead is written once and never tuned.** §1 means the sentence composed for a data-engineering
posting renders unchanged against a research posting. The prose is per-run, so the composer can angle
it; the *facts* cannot move, and an Entry whose stored situation is beside the point for some future
JD spends a line saying so anyway.

**`0026` §6's proudest line is half spent.** It claimed *"this decision adds zero numbers to the
selection knobs"*, with the ten-Entry ceiling *derived and never written down*. No constant is added
here either — `LEAD_LINES` is `0032`'s — but the ceiling is no longer derivable from the constants,
and a reader of `0026` will not find that out from `0026`.

**`0034` §3's *never denied* is contradicted, and this is the first place a merge can lose.** At an
Entry's reserved line a `width: 2` group does not place. What survives of §3 is the harm it was
actually guarding against: its fear was `grant_widths` refusing the second line and three Claims'
facts being crushed into one 103-character line, *"the silent drop #77 exists to forbid, arriving
through the arithmetic."* Nothing is compressed here. The group does not place, and the Omission view
reports every Claim in it. Denied and reported, not denied and hidden.

**The model enumerates the bank twice in one file.** Every Entry appears in the claims table and again
in `## Leads`. That is the price of the explicit `n`, and it is one more thing that can be forgotten —
caught at parse rather than at render, which is the point.

**Everything above is untested against a page.** The reservation binds at eight Entries and the bank
has four. `0026` bought its blindness back with the `Share:` line; the same line covers this, and it
needs one edit to say so (Consequences).

## Rejected

**A `lead` column on the claims table.** The `ended` precedent exactly — a bank fact riding a
judgement table, cross-checked across rows and against the bank, with no new parse block. Refused on
grain: an Entry is a group of rows, not a row, and repeating a boolean across six of them is a
redundancy invented rather than inherited. `type` and `ended` are grandfathered, not a pattern to
extend.

**Listing only the Entries that have a lead.** Half the rows and no `n` to write. It makes a forgotten
lead indistinguishable from an absent one, in the one file whose parser refuses to skip anything.

**The model decides whether a lead earns its line this run.** It would let a posting-specific
judgement hand a line back to the Bullets when the situation is beside the point. It is `0032` §6's
refused trade with a different justification, and it can suppress the sentence in exactly the case the
map was built for.

**The lead paid out of the Entry's own first Bullet** — minimum block stays three lines for everyone,
`header + lead + 0 bullets` with a lead, ceiling holds at 10, nothing in `0026` moves. It was
genuinely attractive and it is the most faithful reading of *Bullets give way, not the frame*. It
loses on what it renders at the ceiling: `0034` §4 fixed the division of labour as *the merge does the
compression, **the lead does the synthesis***, and a lead standing alone is a synthesis with its
evidence deleted — a total with nothing underneath saying what it totals. A missing Entry is an
absence; an unsupported aggregate is a page claiming something it cannot back.

**The parity rule — a lead Entry takes zero extra lines or two, never one.** §5. It is the maker's own
sentence turned into arithmetic and it keeps `0026`'s ceiling intact, which is why it was recommended
before the `sweatpact` finding. It loses because it aims packing arithmetic at a selection problem,
and because the case that motivated it is a Bullet-floor case that no packing rule touches.

**The guaranteed slot holds a whole unit.** §4. The literal reading of `0034` §3, and it makes an
Entry's minimum block 4 or 5 lines. It hands a per-run merge judgement the power to push a different
Entry off the page.

## Consequences

- **`scores.md` gains a `## Leads` table** — one row per Entry, `entry | lead`, `y` or `n`, no reason.
  `pack.py` parses and validates it: every Entry in the claims table present exactly once, no Entry
  absent, no unknown Entry, no value outside `y`/`n`. Every failure names the Entry, as `ScoreTableError`
  already does for every row.
- **`Entry` gains a `lead` flag**, set from that table and read only by the reservation.
- **`pack_page`'s reservation minimum becomes per-Entry**: `ENTRY_HEADER_LINES + LEAD_LINES + 1` with a
  lead, `ENTRY_HEADER_LINES + 1` without. `reservation_queue` is untouched — the queue decides *who* is
  reserved, not *how much*.
- **`Placement.lines` gains `LEAD_LINES`** for a lead-carrying Entry, and `allocation.md`'s Placed
  heading records the lead it charged so `render.py` can check the copy against the bank.
- **The `Share:` line loses its literal.** It reads *"Every qualifying entry reserved 1"*; it has to
  report the lead lines charged, or the one line that exists to make the sharing rule visible will
  under-report what the page spent. `0026` §5 is otherwise unchanged.
- **`pack.py:909`'s Omission line needs no edit.** It already prints `seated`, a count rather than a
  constant, so *"the page seated N entries"* stays true with a variable ceiling.
- **`0026` is extended, not superseded.** §1's *crossing the floor buys presence* survives with a
  weaker guarantee: presence is bought at a minimum block that is no longer uniform. §2's top-first
  distribution, §3's fold, §4's refusal of a depth gate and §5's Omission reasons are untouched.
  `0026` §6's *zero numbers* claim needs the qualification in the cost section above.
- **`0024` is untouched.** The ranking window never sees a lead; the lead is not a Claim.
- **`0034` §3 is narrowed in one clause.** *Never denied* holds everywhere except an Entry's reserved
  line, where a `width: 2` group is skipped for the best one-line unit. Its W ≤ N invariant is
  unchanged and its reason for existing — no silent compression — is preserved.
- **`0006`'s no-leapfrogging is qualified for units inside one Entry** (§4). Between Entries it is
  untouched.
- **`0032` §6 is confirmed as written**, and the cross-Entry consequence it did not state is stated
  here: a lead can cost a different Entry its place at the ceiling.
- **No re-calibration is owed, and no constant is added.** `LEAD_LINES` arrives with `0032`; nothing
  here measures anything.
- **`CONTEXT.md`**: **Elastic block** gains the per-Entry minimum; **Score table** gains the `## Leads`
  table beside `0034`'s `## Merges`. Carried by **#78**.
- **`.claude/skills/tailor/SKILL.md`** gains the `## Leads` table in its scoring step, beside the merge
  declaration. **#78**.
- **#77 inherits the maker's framing** — *an entry is a whole thing; we don't fill to the maximum
  available space* — which is a sharper brief than the one it carries, and the `sweatpact` finding,
  which rules the stub out of its scope and into the bank's.
