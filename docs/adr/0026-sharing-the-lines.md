# A place for everything that qualifies, and depth top-first

**Status:** accepted

## Context

Map #47 raised the per-Entry cap to **6** as a given. `0024` settled what that does to the ranking —
slot cap 6, ranking window 3, qualifying claims only. `0025` settled what a wrapping Bullet costs and
where its lines come from. Neither says **who gives up a line when six will not fit for everyone**,
and `0024` explicitly deferred two of its costs here: *a deep-but-flat entry spending six lines to
show one good thing*, and *a job at 1 Bullet beside a project at 6*.

### The crossing point is four entries

The page gives **32 lines** to Entry headers and Bullets. A header is `ENTRY_HEADER_LINES = 2`. So at
*n* entries the page has `32 − 2n` lines for Bullets and a cap of 6 wants `6n`. They cross at
**exactly four**: 24 available, 24 wanted.

At a cap of 3 the crossing sat at eight entries, well past any bank the maker had. At 6 it sits on
top of the bank he has. **"The page is full" stops being a terminal condition reached rarely and
becomes the normal condition** — which is why the sharing rule, invisible until now, has to be
designed.

### The decision is invisible on the only bank there is

`runs/zs-btsa` has four entries wanting 19 Bullets against 24 lines — **five spare**. Every candidate
rule the ticket named produces the identical page:

```
today (4 entries) — 24 bullet lines, 19 wanted
  greedy in score order   amex 6, auto-apply 5, xlscout 5, sweatpact 3   residue 5
  round-robin             amex 6, auto-apply 5, xlscout 5, sweatpact 3   residue 5
  soft cap at 3           amex 6, auto-apply 5, xlscout 5, sweatpact 3   residue 5
```

So this ADR is decided **blind**. Nothing re-renders differently, and no page tells the maker whether
he chose right. §5 is what buys that back.

### What today's Packer does, and where it goes at six

`pack_page` walks strict score order. Each entry takes `min(slots, free − header)`; an entry that
will not fit is **shrunk** — it drops its own lowest Bullet — and shrinking never reaches backwards.
The first entry that will not fit at the uniform minimum (header + 1) stops the walk. Ahead of all
that, the **Experience floor** reserves the minimum block for the two most recent jobs.

Together: **the top entry takes everything it qualifies for, and the bottom entry pays.** Modelled on
the current bank plus plausible additions:

```
5 entries — greedy   amex 6, auto 5, xlscout 5, zs-intern 4, sweatpact 2
6 entries — greedy   amex 6, auto 5, xlscout 5, zs-intern 4, side-tool 2, sweatpact DROPPED
7 entries — greedy   amex 6, auto 5, xlscout 5, zs-intern 4, side-tool 2, and TWO dropped
```

The sixth entry is where an Entry stops appearing on the résumé at all. That is what the maker
refused, in one sentence: **crossing the floor means it is relevant, and relevant belongs on the
page.**

## Decision

### 1. The Entry floor — every qualifying entry is reserved its minimum block first

An Entry with at least one Claim at or above the **Bullet floor** is reserved `ENTRY_HEADER_LINES + 1`
lines before anything competes for depth. **Crossing the floor buys presence.** What an Entry then
competes for is *width*, never *whether it appears*.

This generalises what the **Experience floor** already did for the two most recent jobs to everything
that qualifies, and it is the same elasticity `0025` §2 applied one level down to widths — *evidence
outranks room*; now *presence outranks depth*.

**It has a hard ceiling.** A minimum block is 3 lines, so 32 lines seat **10 entries**. Below that,
nothing falls off. At 11 the guarantee breaks and §3 says who is cut.

### 2. The remainder goes top-first, in Entry-score order

After the reservation, a second walk in the order `order_entries` already produces grants each placed
Entry up to `slots − 1` further Bullets from whatever is left, taking its fill before the next Entry
is offered anything.

**The floor buys presence; score buys depth.** That is the governing sentence, and it is the same
shape as `0024`'s — *an entry is ranked on its best evidence and gets its width from its depth* — with
one clause added in front of it.

```
6 entries — 32 lines
  greedy (today)             amex 6, auto 5, xlscout 5, zs 4, side 2, sweatpact DROPPED
  Entry floor, top-first     amex 6, auto 5, xlscout 5, zs 2, side 1, sweatpact 1
  Entry floor, spread        amex 4, auto 4, xlscout 3, zs 3, side 3, sweatpact 3

7 entries — 32 lines
  greedy (today)             amex 6, auto 5, xlscout 5, zs 4, side 2, and TWO dropped
  Entry floor, top-first     amex 6, auto 5, xlscout 3, zs 1, side 1, older 1, sweatpact 1
```

**Who actually pays for the guarantee, measured rather than assumed.** At six entries `sweatpact`'s
three lines come out of `zs-intern` (4 → 2) and `side-tool` (2 → 1); the top three are untouched. At
seven, the two rescued entries' six lines come out of `xlscout` (5 → 3), `zs-intern` (4 → 1) and
`side-tool` (2 → 1); the top two are untouched. **The guarantee is paid from the bottom of the placed
set upward, never from the top** — a property of top-first, and the reason the strongest evidence on
the page never funds the weakest entry's presence.

**The bill, stated plainly: the bottom of a crowded page becomes stubs.** An Entry at its reserved
line spends 3 lines — two of header — to say one thing. That is the price of the guarantee, and it is
also the direct answer to the cost `0024` deferred here: **a job at 1 Bullet beside a project at 6 is
now the design rather than an accident.** It is what "presence is owed, depth is earned" looks like
when the page is short.

### 3. The Experience floor folds into the Entry floor

It stops being a rule of its own and becomes the **head of the reservation queue**: *the two most
recent jobs, then Entry-score descending*. Below 10 entries the queue order changes nothing, because
everyone is reserved. At 11+ it does its one original job — stopping a projects-heavy pool from
shipping an empty Experience section — and everything below it is cut lowest-score-first, the same
principle governing every other cut on the page.

**One reservation concept where there were two.** Today `pack_page` reserves the floor and then runs a
pool that reserved entries re-enter on different terms (`extra = min(wanted − 1, free)` for the
reserved, `min(wanted, free − header)` for everyone else). Under the Entry floor there is one
reservation pass and one distribution pass, and every Entry travels the same path through both.

**`floor_log` and its second `pack_page` call go.** That machinery exists to answer *what did the
Experience floor actually change*, by packing the page a second time without it — an honest answer
that is now unobtainable in the interesting case and unnecessary in every other. §5's `Share:` line
reports the reservation and the distribution outright, so nothing is lost and the Packer stops
packing the page twice per run.

### 4. No score gate on the fourth Bullet

The fourth Bullet onward does **not** have to clear a higher bar than the **Bullet floor**. Rejected
on the record because it is the one candidate that changes the page that exists:

```
today (4 entries)
  no gate            amex 6, auto-apply 5, xlscout 5, sweatpact 3   residue 5
  4th+ needs 0.70    amex 6, auto-apply 4, xlscout 4, sweatpact 3   residue 7
```

A 0.70 gate removes exactly `auto-apply/c5` and `xlscout/c4`, both 0.50, and returns two lines that
`0025`'s width pass would spend on prose. So the gate trades *two more Bullets* against *two
better-written Bullets* — the map's two founding complaints pointed at each other.

It loses on three counts. The complaint that opened #47 was **eight qualifying claims dropped onto a
page with twelve idle lines**; a gate re-introduces that drop under a new name, on a page with room.
The Entry floor has already taken the gate's real job, which was stopping the top entry from starving
the page. And `0024` §4 had just settled the floor at 0.50 deliberately, so a second threshold with
nothing to calibrate it against is exactly the fault #47's destination names — *numbers nobody chose*.

There is a coherent sentence behind the gate, recorded because it may come back: **presence is owed to
anything above the floor; depth has to be earned above a higher bar.** It also escapes `0024` §4's
objection to raising the floor — raising the floor to 0.70 deletes `sweatpact` from the page, whereas
a *depth* gate cannot, because the Entry floor protects it. If a six-Bullet entry reads badly once the
maker has seen one, this is a one-line change against a page he can look at, which is more than this
ADR had.

> **Closed by `0037` §1, not re-parked.** That trigger fired — the maker read a six-Bullet entry back
> and complained, which is what chartered #70 — and the gate is declined anyway, on grounds this ADR
> did not have. A depth gate orders by **score**, and score is fit-to-JD: on `runs/auxo-ai` a 0.70
> gate separates `c1` (0.85) from `c4` (0.85) and drops `c3` (0.60), which is `0037`'s merge group
> taken apart backwards. Worth is served by merging instead, and it is not a threshold.

### 5. The Omission view keeps its three claim reasons; the Entry line gains one; Silent calls gains `Share:`

Walking every way a Claim can lose under §1–§3, the three existing reasons are still exhaustive:

| how it loses | wording | change |
|---|---|---|
| below 0.50 | *below the 0.50 bullet floor* | none |
| sits past position 6 | *beyond the N-bullet cap on an entry* | `3` → `6`, no edit — it reads `MAX_BULLETS` |
| Entry got fewer lines than slots earned | *dropped when X was shrunk to fit the page* | none |

The hole is at Entry level, and it is pre-existing: `omission_view` writes `{slug} — entry score {s} —
best claim {ref} ({score}) — {Opus's reason}`, where the reason explains the **claim** and never why
the **entry** lost. Under §1 that case has exactly one cause, so it can finally be stated:

```
- sweatpact — entry score 0.50 — no room to reserve a block; the page seated 10 entries —
  best claim sweatpact/c1 (0.50) — <the reason Opus wrote>
```

The structural reason sits where the claim lines carry theirs — between the score and the prose — so
both halves of the Omission view read the same way.

And **Silent calls gains one aggregate `Share:` line, on every run**, the direct counterpart of the
`Room:` line `0025` §7 put beside it:

```
- Share: 20 line(s) for Bullets after 6 header(s). Every qualifying entry reserved 1;
  the remaining 14 went in score order — american-express +5, auto-apply +4, xlscout +4,
  zs-intern +1. 2 entry(s) placed at their reserved line only: side-tool, sweatpact
```

Always printed, for the reason `0025` §7 gave: on a crowded page *"placed at their reserved line
only"* is the signal that the bank has outgrown the page, and a signal is only readable if its absence
never has to be interpreted. It is also the one thing this decision otherwise lacks — **something to
look at.** The rule was chosen blind (Context), and the `Share:` line is what turns the next full page
into evidence about whether top-first was right.

`allocation.md`'s wording stays contract in exactly the two places it already was — the `Skills:` line
and the claim line's width field. `render.py` does not parse Silent calls, so `Share:` costs nothing
in coupling.

### 6. No new constant

The Entry floor's reservation is `ENTRY_HEADER_LINES + 1` — the **Elastic block**'s minimum, which
already exists and which `0024` §5 noted the Experience floor was tied to rather than to the cap. The
ceiling of 10 entries is `PAGE_LINES // (ENTRY_HEADER_LINES + 1)`, derived and never written down.

**This decision adds zero numbers to the selection knobs**, which is worth stating on a map whose
destination is *Bullets stop being decided by numbers nobody chose*. `MAX_BULLETS = 6`, `BULLET_FLOOR
= 0.50` and `EPSILON = 0.05` remain the whole set.

> **Qualified by `0035` §3.** The reservation is no longer uniform: an Entry with a lead takes
> `ENTRY_HEADER_LINES + LEAD_LINES + 1`. No constant is added, but the ceiling stops being derivable
> from the constants alone — it is a number between 8 and 10 depending on how many placed Entries
> carry leads.

## The cost, stated rather than waved past

**The stub tail.** At seven entries and beyond the bottom of the page is a row of Entries spending
three lines each to say one thing, and at eight the top entries start losing depth too (`amex 6,
auto-apply 4, then six Entries at 1`). There is a bank size past which this page shape is simply
wrong, and neither this ADR nor any sharing rule can fix it — it is a claim about **how many Entries
belong on a one-page résumé**, which is a bank question, not a packing one. Left unfixed on purpose;
the `Share:` line is what will make it visible when it arrives.

**Nothing wraps on a contended page, and that is not this ADR's doing.** `0025` §2 spends only the
lines the evidence did not want, so from five entries onward the residue is zero under *every* rule
here — greedy included. The wrap feature effectively stops firing once the bank passes four entries.
That is a property of the cap rise, recorded here because a reader will otherwise blame the Entry
floor for it. §4's gate was the only lever that would have bought residue back, and it was refused.

**A weak Entry's presence is real page.** Three lines to show one 0.50 Claim is 9% of the Entry budget
spent on the least relevant thing on the page. Accepted because the maker's rule is that the **Bullet
floor** is where relevance is decided, and re-deciding it in the Packer would put the same judgement
in two places — the overloading `0024` just took off `MAX_BULLETS`.

**Untestable today.** Recorded in Context and repeated here because it is the honest headline: every
rule considered produces the same `runs/zs-btsa`, so this was chosen on principle alone.

## Rejected

**Nothing changes — greedy in score order, and a deep Entry can push a weak one off the page.**
Simplest, keeps *the page is full* a terminal condition rather than a negotiation, and it is what the
code does today. Refused by the maker directly: a Claim above the **Bullet floor** has already been
judged relevant, and the page owes what is relevant a place.

**Round-robin the lines** — every placed Entry gets its floor, then the pool competes for line 2, then
line 3. Produces the evenest page and needs no second concept. It loses twice. It **repeals the cap
raise**: at six entries nothing reaches six and at eight nothing reaches three, so the change #47
granted stops firing exactly when the bank is rich enough to need it. And it severs the half of
`0024`'s governing sentence that map had just decided — *gets its width from its depth* — while
`0025` §4 had already refused round-robin's twin in the width currency, *"one width per placed entry
before any entry gets a second"*, flagging the risk of the two landing on opposite rules. This is that
risk arriving.

**A soft cap under the hard one** — six is reachable, but an Entry takes its 4th, 5th and 6th only
once every placed Entry has three. Better than round-robin in that it does not touch a small bank at
all. It still caps depth at three on any bank of six or more, which is the same repeal one bank size
later, and it puts a second number in the rule with nothing to measure it against. Three has a
pedigree — it is the ranking window and the old cap — but "the ranking window is also the depth tier"
is a coincidence dressed as a principle.

**Score-gated depth.** §4.

**Raise the guaranteed minimum to 2 Bullets**, to kill the stub. It halves the ceiling to eight
entries, it spends the extra line unconditionally whether or not it was needed, and `0024`'s Rejected
section already refused this exact shape for the Experience floor for those reasons. The stub is ugly;
it is not as ugly as the entry being absent, which is the comparison the maker made.

**Keep the Experience floor beside the Entry floor as a separate rule.** It would be redundant below
ten entries and identical above them once the queue is ordered. Two rules where one does the work, and
a `floor_log` counterfactual that no longer has a counterfactual to report.

## Consequences

- **`tools/pack.py`**: `pack_page` restructured into a reservation pass over every Entry with slots —
  queued *two most recent jobs, then score order* — followed by a top-first distribution pass in score
  order. `experience_floor` becomes the queue head rather than a separate reservation. `floor_log` and
  the second `pack_page` call are deleted. `omission_view`'s Entry lines gain a structural reason. A
  `Share:` line joins the Silent calls. Carried by **#53**, with `0024`'s and `0025`'s changes, because
  all three land on the same function.
- **`CONTEXT.md`**: **Elastic block** gains the Entry floor and the top-first remainder; **Experience
  floor** is rewritten as the head of the reservation queue rather than a rule of its own; **Slot**
  notes that presence is guaranteed and only width competes; **Omission view** gains the Entry-level
  reason.
- **`SPEC.md`** keeps its v1 normative text and gains *Extended* parentheticals at steps 4 and 5, per
  the convention `0020`, `0021` and `0024` set.
- **`tests/test_pack.py`** gains the reservation and ceiling cases and loses the `floor_log`
  counterfactual ones; **#53** carries it.
- **`.claude/skills/tailor/SKILL.md`** describes the allocation to Opus and needs the `Share:` line and
  the guarantee; **#53**.
- **This ADR extends `0024` and narrows it in one place.** `0024` §5 kept the Experience floor at ≥ 1
  Bullet with no code change; the **number** survives — every Entry now gets it — but the rule stops
  standing on its own. `0024`'s two deferred costs are answered here: the deep-but-flat Entry keeps its
  six (§2, it is paid for from the middle of the page, not the top), and the job-at-1-beside-a-
  project-at-6 is now intended rather than tolerated. `0025` is untouched: the width pass still runs
  after packing and still spends only what the evidence did not want.
- **`0006`'s packing rule is superseded in one clause.** *"The packer walks strict score order"* is now
  *reserve every qualifying Entry, then walk strict score order for the remainder*. The Elastic block,
  the no-backfill property and the uniform minimum all stand — an Entry still never surrenders a line
  to admit a weaker one below it, because the weaker one's line was reserved before either competed.

## Addendum, 2026-08-13 — the cap this ADR computed with is now named

`docs/adr/0048-the-depth-cap-is-a-line-budget.md` amends this ADR's cap, and the
amendment is best read as this ADR's own arithmetic being given a name.

§1 above sizes the page as *"32 − 2n lines for Bullets, and a cap of 6 wants 6n"*.
That `6n` is six **units** costing six **lines** — an identity that held only because
a Bullet was one line and a second was bought later out of the residue. `0047` §3 made
the width a charge, six units began wanting up to twelve lines, and the crossing point
§1 puts at four entries moved to two. Greedy top-first, chosen here on a page with
five spare lines, became a rule for dividing a page with none, and starved every Entry
below the first.

`0048` caps an Entry at **six Bullet lines**. **Every model in §2 above is unaffected**
— they are all computed at one line per Bullet, where the two caps are the same
number.

**§2's decision is kept.** *The floor buys presence; score buys depth* stands, and
round-robin stays rejected: with the cap corrected, greedy no longer produces the
starvation that would have been the argument for it. What §2 records as decided
**blind** — that greedy, round-robin and a soft cap all produced an identical page —
is no longer true under `0047`, and `0048` records the page each now produces.

**§2's bill is unchanged.** The guarantee is still paid from the bottom of the placed
set upward, and the bottom of a crowded page is still stubs.

## Addendum, 2026-08-13 — the floor's guarantee is bounded by the entry caps

`docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md` caps the competing set
at three jobs and two projects. §1 above — *crossing the floor buys presence* — now
reads: every qualifying Entry **within the caps** is reserved its minimum block.

**§3's Experience floor is untouched and outranks the cap.** The two most recent jobs
are seated before `MAX_EXPERIENCE` is filled by score, so a recent job scoring fourth
is not cut by the cap that was meant to remove the fifth.

**§1's ten-Entry ceiling is now unreachable**, because five is the most that can
compete. The cut-lowest-score-first rule above ten entries is kept for its reasoning
rather than for its behaviour.
