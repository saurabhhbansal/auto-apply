# Fit orders the page; force orders the block

**Status:** accepted

## Context

`runs/auxo-ai/allocation.md`, the biggest block on the page, in the order it printed and the order
`bullets.md` therefore composed in:

```
### american-express — job — ended 2026-07 — entry score 0.95 — lead — 5 bullets
  1.00  c5        Replaced hand-written business-review insights with a custom GPT…   ← no figure
  1.00  c6        Built a custom GPT over historical scorecard, forecast, pipeline…   ← 2 lines, no figure
  0.85  c1+c3+c4  Automated the merchant-account mapping… cutting ~8 hours a month    ← the strongest line
  0.70  c7        Owned ~60 of a new diagnostics scorecard's KPIs… halve its refresh
  0.50  c2        Rewrote the scorecard compilation… cutting rework ~85%
```

**Every quantified outcome on the page's biggest block sits at position 3 or below, under two
unquantified lines, because 1.00 > 0.85.** A screener reading the first bullet of each block — which
is what a thirty-second read *is* — meets the weakest argument in the entry first.

This is not a scoring bug. `c5` and `c6` genuinely answer AuxoAI's *"AI-driven business copilots"*
responsibility head-on and belong on the page at 1.00; `runs/auxo-ai/scores.md` says so in reasons
that survive reading. The fault is upstream of the numbers.

### One ordering is doing two jobs

`tools/pack.py`:

```python
@property
def ordered_claims(self) -> list[Claim]:
    return sorted(self.claims, key=lambda claim: claim.order_key)
```

```python
@property
def order_key(self) -> tuple:
    """Best first: score descending, then claim id ascending."""
    return (-self.score, int(self.id[1:]))
```

That one ordering decides **which** units clear `BULLET_FLOOR` and reach the page, *and* **where**
they sit top-to-bottom inside the entry. `render.py`'s `check_structure` then requires `bullets.md`
to match `allocation.md`'s order exactly, so the score reaches the reader's eye unchanged.

Score order is right for **selection** — it is the whole selection model, `0001` and `0024`. It is
not obviously right for **reading order**, and on this page it demonstrably is not. **Fit and force
are different quantities and one ordering is currently serving both.** Nothing in `scores.md`
carries the second one, exactly as `0037` §2 found that nothing in it carries *lands alone*.

## Decision

### 1. `scores.md` gains an `## Openers` table: one entry, one unit, judged on force

A fourth table beside `## Leads` and `## Merges`, written at §2 before a word is composed:

```markdown
## Openers

| entry | unit |
|---|---|
| american-express | c1+c3+c4 |
| xlscout | c3 |
| auto-apply | c1 |
```

- **One row per entry that placed, exactly one unit named** — a claim id, or a `+`-joined merge
  group from `## Merges`. A unit is what takes a Bullet slot (`0037` §6), so a claim that sits
  *inside* a merge group is not one.
- **The question is force, not fit:** *which of this entry's lines would make a stranger reading
  only one of them want to read the rest?*
- **Naming the top-scoring unit is the common and correct answer.** The table exists so that answer
  is **made rather than inherited.**

The grain is `0035` §2's, not `0037` §8's: one row per entry, never withheld. That is the right
shape here for the reason `0037` gave for refusing it for merges, read the other way round — a merge
is a group and has no per-entry question, whereas *which line opens this block* is a question every
placed entry answers whether or not anyone asks it. Today it is answered by the score, silently, on
every run.

### 2. The pre-pass runs after selection, and cannot reach it

`Entry.ordered_units` is the print order — the declared unit at index 0, everything else holding its
existing score order — and `Entry.units` stays exactly what it was: score order, and the only thing
selection reads. `pack_page` reserves, windows at `[: entry.slots]` and leapfrogs out of `units`,
**then** permutes the units it chose into `ordered_units` order, carrying each slot's granted width
with it.

Where the pre-pass runs is load-bearing and was nearly got wrong. Applied *inside* the unit list, it
would change the order in which the distribution pass considers candidates, and on a page whose last
line runs out mid-entry a different consideration order drops a different unit — an opener
declaration would be able to push a Claim off the page. Applied after, it cannot: the set is fixed
before anything moves.

So **selection stays exactly as it is**, and byte-identically: entry score, slot count, the page
budget, which units placed, and the widths `grant_widths` handed out (it spends its residue in
`Unit.order_key` order — score, not position). `tests/test_pack.py` asserts this across three
variants of one fixture, and it is the test that stops this stage leaking into selection.

`render.py` needs nothing. `check_structure` already requires `bullets.md` to match
`allocation.md`'s order, so the new order flows through unchanged.

### 3. Three refusals, and one tolerated absence

`pack.py` refuses the run when:

1. **a placed entry has no `## Openers` row** — a table that skips an entry is the inheritance this
   table exists to stop, wearing a table's clothes;
2. **the named unit did not place** — an opener is chosen from the units that reach the page, and
   which those are is the allocation's call;
3. **the name is not a unit** — a claim id that sits inside a merge group (name the group), a
   `+`-joined group no `## Merges` row declares, a claim below the Bullet floor, an id the claims
   table never scores, or four ids joined together. Each refusal names which of those it is, because
   they want different fixes and the first is much the commonest.

Refusal 1 is decided **after packing**, because whether an entry placed is the Packer's own answer.
That makes the table mildly awkward to write — which entries place is not knowable at §2 — and the
resolution is that **a row for an entry that did not place costs nothing**: write one for every entry
that could place. The alternative, requiring a row for every scored entry the way `## Leads` does,
would put rows against entries scoring all zeros, which is noise standing in for rigour.

**The table absent entirely is not a refusal**, exactly as `parse_leads` tolerates an absent
`## Leads` table. A run folder scored before this ADR still packs, and `## Silent calls` says out
loud, once per placed entry, that the opener was *inherited, not chosen*. This is the one place the
rule is weaker than §1 asks for, and it is priced below.

### 4. The move is a Silent call, printed on every placed entry

`allocation.md`'s `## Silent calls` — *every call the Packer made by rule rather than by score* — is
the existing idiom for exactly this, and the line is written whether or not anything moved:

```
- Opener: american-express/c1+c3+c4 moved to the top of american-express, from position 3 by score
- Opener: xlscout/c3 declared to open xlscout, and already first by score — nothing moved
- Opener: sweatpact has no `## Openers` row, so it opens on sweatpact/c4, its best unit by
  score — inherited, not chosen
```

`0026` §5's rule for `Share:` and `0025` §7's for `Room:`, applied again: **a signal is only readable
if its absence never has to be interpreted.** The *nothing moved* line is the one that matters most —
it is the difference between an answer given and an answer never asked for, which is the whole
content of §1.

## Rejected

**A `force` column beside `score`.** The obvious design, and worse. It is a second per-claim
judgement on every row of a table that already carries `score`, `width` and `reason` for every claim
including the zeros; it invites the two numbers to drift; and it would have to be defined against
`BULLET_FLOOR` and the Epsilon band, which are `0024`'s and are absolute. **One named unit per entry
asks the one question that changes the page and asks it once.** This is `0037` §8's grain argument
in its other direction: there, per-entry rows were refused because a merge is a group; here, a
per-claim column is refused because opening is a property of the block.

**Sorting selection on force instead of fit.** It would put the strongest line first by construction
and destroy the selection model doing it: `BULLET_FLOOR`, the `[:3]` ranking window and the Entry
score are all defined on Fit (`0024` §1–§3), and an entry ranked on force would be ranked on
something no rubric anchors.

**Letting the Packer choose the opener by rule** — the unit whose Claim stores a `number:`, say, or
the widest one. The Packer is bank-blind (`0006`) and `scores.md` carries no such field, so the only
rules available are proxies for force that are not force. Worse, it would be a rule that reliably
produces a plausible answer, which is `0010`'s objection: nobody would ever look at it again.

**A second model reading the block and picking the opener.** `0010`'s rejected reviewer, and `0037`
§3's grounds apply unchanged — *which of these lines lands hardest* fails the adjudicable-question
condition outright.

**Rescoping this to the first entry only.** Considered, since a thirty-second read arguably only
reaches the top block. Refused: the reader meets the first line of *each* block, which is `0030`'s
own argument for making the opener check page-wide, and an entry-by-entry rule with an exception at
the top is a rule nobody can state.

## The cost, stated rather than waved past

**A new judgement per entry per run, and nothing checks it.** This is `0037` §3's trade taken again,
one grain smaller: a wrong opener buries the entry's best argument at position 3, reads perfectly
well, traces perfectly cleanly, and is reported as placed. The only thing between it and the PDF is
the maker reading three lines in `## Silent calls`. Unlike a merge, a wrong opener costs nothing but
position — no claim is dropped and no sentence is fused — which is why this is priced as a cost and
not as a fork.

**The strongest-by-fit claim no longer leads its block, by design.** On `runs/auxo-ai` the intended
outcome is that `c1+c3+c4` (0.85) opens Amex above `c5` and `c6` (1.00, 1.00) — the two claims that
answer AuxoAI's central responsibility head-on. A screener who reads only the first line of that
block now meets the automation argument rather than the copilot argument. That is a genuine bet: it
says a quantified line at 0.85 recruits a reader better than an unquantified line at 1.00, and it
can be wrong on a posting where the top-anchor match is the whole case. **The maker reads the page
and can say so; there is no mechanism, and `0010` is why.**

**The tolerated absent table is a hole in §1.** A run whose `scores.md` simply has no `## Openers`
section gets score order and a Silent call, which is precisely the *inherited* outcome this ADR
exists to stop — the only difference is that it now says so. The alternative was refusing every run
folder written before this ADR and every fixture in `tests/test_pack.py`, which buys strictness with
a fleet of edits and a rule that cannot be replayed against history. `parse_leads` set this
precedent and it is being followed rather than improved on.

**One more thing in `scores.md` that a re-run rewrites whole.** `0027`-era `scores.md` was one
table; it is now four, and every one of them is rewritten from scratch on a re-run so the diff means
something. The openers are the first of the four whose correctness depends on an output the file
does not contain — the allocation — so a re-run that changes what places can turn a previously valid
table into a refusal. The refusal names the entry and the fix is one row.

## Consequences

- **`tools/pack.py`**: `OPENERS_COLUMNS`, `OPENER_UNIT` and `parse_openers` join `parse_leads` and
  `parse_merges`; `Entry.opener` and `Entry.ordered_units` are new; `pack_page` permutes each
  placement through `open_on_the_declared_unit` and logs it; `check_openers` runs after packing.
  `Entry.units`, `Entry.slots`, `Entry.score`, `qualifying_claims`, `reservation_queue`,
  `grant_widths` and `omission_view` are untouched.
- **`tests/test_pack.py`** gains the parser's refusals and the invariant test: entry score, slot
  count, page budget and the set of placed units are identical across *no table*, *opener = top* and
  *opener = last*, while the print order is not.
- **`.claude/skills/tailor/SKILL.md` §2** gains the `## Openers` table beside `## Merges`, and
  *"`pack.py` reads all three from `scores.md` alone"* becomes four.
- **`tools/render.py`, `tools/config.py`, `templates/resume.tex.j2`**: nothing. No page line is
  spent and no constant moves.
- **`CONTEXT.md`**: **Unit** gains the sentence that print order is declared and selection is not.
- **`runs/auxo-ai` re-composes with a different first line in three of its four blocks**, which is
  the read this ADR is judged on.
