# A range collapses at compose time, and the page never carries one

**Status:** accepted

## Context

`bank/jobs/american-express.md` holds four estimates the maker gave as ranges — *3 to 4 hours*,
*5 to 6 hours*, *50 to 60 minutes*, *4 to 5 hours*. None of them can render as written, and the
question of what they render as instead has now outlived two maps (#47,
#54) as fog. #70
put it on the critical path: the entry arc's closing beat is an aggregate of those savings, and an
aggregate of five ranges is a range, so the beat cannot be rendered until this is settled.

`0029` recorded the state of play and deferred:

> **`~4--5 hours` still cannot render as a range.** The Number-trace check softens per figure, so
> `~4-5 hours` renders the `5` flat and fails on an `estimated` Claim. Keeping this Claim's number
> means composing the endpoint the maker is willing to defend — `~5 hours` — until #54's open
> question about ranges is settled.

### Where ranges actually live

Not where the ticket assumed. Only two of the six `number:` fields in the bank hold a range; four
Claims hold one in their **prose**:

```
c1  number: ~75%                    prose: "from 3--4 hours to about 1 hour"
c2  number: ~85%                    prose: "from 5--6 hours ... to about 1 hour"
c3  number: 50--60 min per month    prose: 50--60, three times
c4  number: ~4--5 hours per cycle   prose: 4--5, three times
c7  number: ~50%                    prose: "around 10 hours to around 5"   ← not a range
```

`check_number_trace` accepts a rendered figure that matches the stored `number:` **or** one written
in the Claim's prose, so all four are live trace sources. This is the fact that decides §1.

### `--` is a safe discriminator, measured rather than assumed

Every `digit--digit` occurrence in `bank/` is a range. The bank's sentence dash is written ` -- `,
always spaced, and there is no instance anywhere of a spaced dash falling between two figures. So a
range is *two figures joined by `--` with no surrounding whitespace* — a syntactic test, not a
semantic one.

It cleanly excludes the two shapes that look adjacent and are not. `~60 of ~150 KPIs` is two
independent scope figures with no dash between them. `around 10 hours to around 5` is a
**transition** — a before and an after — and so is the *to about 1 hour* half of `c1` and `c2`. A
transition is two facts; a range is one fact stated loosely.

### What the page does today

Both range-derived figures on `runs/auxo-ai` are the **high endpoint**:

```
c4  stored ~4--5 hours per cycle   →  "ending ~5 hours of Excel pivoting"
c3  stored 50--60 min per month    →  "saving ~60 minutes"
```

Neither was a decision anyone made. The endpoint is shorter than a midpoint, the high one is bigger
than the low one, and nothing in the pipeline objected — `0029` licensed the move in writing.

### The threat model, stated for the first time

> **The system exists to stop 5 hours becoming 50, not to police half an hour.**

This has never been written down. It is the reason a midpoint may be approximate at all, the reason
`0022` chose a softening mark rather than a precision rule, and — see §3 — the reason the composer
is trusted to pick which single figure a range becomes.

## Decision

### 1. The bank keeps the range; the composer does the arithmetic

`bank/` stores what the maker said. `~4--5 hours per cycle` stays exactly as written, and the
collapse happens at compose time.

The alternative — storing `~4.5` in the `number:` field — is **dominated**, and the prose finding
above is why. It would fix `c3` and `c4` and leave `c1`, `c2` and `c7` untouched, because their
ranges are in Assertion and Evidence sentences that `0016`'s Return door and *amend, never
regenerate* protect. The composer and the trace check would still have to understand `3--4 hours`.
So it buys a bank edit and needs this ADR's machinery anyway. It would also leave the file
contradicting itself: `number: ~4.5 hours` two lines above an Evidence sentence that still says
*4--5 hours*.

There is a second reason, and it draws a line worth having. #70
settled that the arc's **aggregate** is computed by the agent, handed back as a question, and stored
only once the maker says yes — which makes it **spoken** under `0015` and keeps the tier
`estimated`. A midpoint does not get that treatment, and the distinction is stateable rather than
arbitrary: the aggregate needs judgement — *are these the same cycle, do they add up* — while a
midpoint is judgement-free arithmetic on two figures the maker already spoke. Judgement routes
through the maker; arithmetic does not.

### 2. Same unit, always — the midpoint never converts

The collapse is arithmetic on two numbers in one unit. The unit is not touched.

```
~4--5 hours per cycle   →  ~4.5 hours
3--4 hours              →  ~3.5 hours
5--6 hours              →  ~5.5 hours
50--60 min per month    →  ~55 minutes
```

`50--60 min` is the case that looks like it wants an exception. `~1 hour` is not its midpoint; it is
the midpoint converted to another unit and then rounded up 9%, and `traces_to` treats the unit as
part of the claim on purpose — `40%` and `40` are deliberately two different numbers to it. Accepting
`~1 hour` there would put a unit-conversion table inside `render.py`.

**The exception is unnecessary, because conversion is not a Bullet's problem.** A Bullet about that
email says `~55 minutes` and never reaches for hours. Conversion is forced only when that claim is
summed with `~4.5 hours` and `~5.5 hours` — that is, inside the **aggregate**, which §1 already
routes through the maker's yes. So the conversion is judged by a person and lands in the bank as a
spoken fact, and no check ever does arithmetic across units.

Every range in the bank has integer endpoints, so every midpoint lands on `.0` or `.5`. No precision
rule is owed.

### 3. The check enforces one figure instead of two; it has no opinion on which one

This is the load-bearing split, and it follows directly from the threat model.

**A range contributes three traceable values: its two endpoints and its midpoint.** The endpoints
already trace, since they are literal tokens; the midpoint is what this ADR adds. Three values, not
the interval — `~4.5`, `~4` and `~5` all trace against `4--5`; `~4.2` does not. Nothing needs the
interior, and opening it would leave the check with no opinion at all.

**The midpoint is the composition rubric's default, not a law.** *Always the midpoint* is written
into `SKILL.md` as guidance; composing an endpoint instead stays available and is the model's call on
the line. Enforcing the midpoint was considered and rejected — see below — on the threat model: half
an hour either way is not what this system exists to catch, and a rule that fires on it spends
credibility it will need for the order-of-magnitude case.

**What *is* enforced: the page never carries a range.** `4--5` may not appear in a Bullet. It
collapses to one figure, and which figure is the composer's.

That rule becomes explicit rather than accidental. Today a range in a Bullet fails only as a side
effect — `numbers("~4--5")` yields `~4` softened and `5` flat, and the bare `5` trips `check_tier` on
an `estimated` Claim. A **`measured`** range would sail straight through onto the page. So this gets
its own detector and its own message, naming the collapse rather than the tier.

### 4. A midpoint renders softened, whatever the tier

`check_tier` already forces this for every range in the bank, since all four sit on `estimated`
Claims. The rule is stated on its own grounds anyway, because the reason is different and the bank
will not always look like this: **a midpoint is a figure nobody measured.** A `measured` range may
not print `4.5` flat.

Endpoints are unaffected — they are figures the maker stated, and they keep following the tier
exactly as they do now.

### 5. The tilde binds to the range, not to its first endpoint

In `~4--5 hours` the maker's tilde covers the whole range. `NUMBER` currently binds it to the `4` and
leaves the `5` bare, which is precisely the accident §3 replaces. One leading `~` softens both ends;
`~4--~5` is not a form anyone writes and is not one this recognises.

### 6. `check_number_kept` does not move

`0029` §4's mirror check arms when the Claim stores a figure and the Bullet renders none. A collapse
still leaves a figure in the line, so nothing changes. One implementation constraint follows: the
range pairing must not make `~4--5 hours per cycle` look figure-less to `numbers()`, or `c3` and `c4`
would quietly stop being guarded — the check would silently unarm on exactly the two Claims this ADR
is about.

## Rejected

**Storing the midpoint in the `number:` field.** Dominated — see §1. It fixes two Claims of four,
leaves the prose ranges needing this machinery regardless, edits the one file with no lint, and
leaves `number:` disagreeing with the Evidence three lines below it.

**Enforcing the midpoint — a range as an atomic token whose endpoints stop tracing.** The strongest
version, and genuinely tempting: it would have caught both drifts on `runs/auxo-ai`, it is pure
arithmetic, and it kills the flattering-endpoint move `0029` licensed. Rejected on the threat model.
`4` and `5` are both things the maker said; a check that refuses one of them is calling a true
statement false in order to police half an hour, which is the thing this system explicitly does not
exist to do. Sometimes `~5 hours` is the better line, and that is a judgement about a sentence, which
`0010` keeps out of the checks' hands. What the drift on `auxo-ai` actually shows is that nothing had
ever *said* the midpoint was the default — which §3 now does, in the rubric, where prose judgements
belong.

**Permitting the whole interval.** The symmetric error. Any softened value between the endpoints
would trace, which sounds harmless under the threat model but leaves the check with no opinion on a
figure it is the only guard for. Nothing in the bank needs `~4.2`, and three values are as easy to
implement as a comparison.

**A unit-conversion table so `50--60 min` may render `~1 hour`.** Rejected in §2: conversion is the
aggregate's problem, the aggregate routes through the maker, and `traces_to` holds that a unit is
part of the claim.

**Rounding toward the less flattering endpoint.** One of the three candidates the ticket named, and
it dies with enforcement: once the midpoint is a default rather than a law, a directional rule is a
second law layered on a suggestion. It is also the wrong shape for the threat model, which is about
magnitude, not about which way a small error leans.

**Copying the threat model into `0022`.** `0022`'s body is measurements in points and codepoints —
a typesetting decision. The threat model is not a typesetting fact, and two homes drift. `0022` gets
a pointer instead; see Consequences.

## Consequences

- **`render.py` learns what a range is.** `numbers()` gains the `--`-pairing, `traces_to` gains the
  midpoint as a third traceable value per range, and a new check refuses a range in a Bullet's text
  with its own message. `check_number_kept` and `check_number_trace`'s existing branches are
  untouched — see §6 for the one constraint the pairing must respect.
- **`SKILL.md`'s *Numbers move one way only* section (line ~1168) gains the collapse**: a range never
  goes on the page, the midpoint is the default, an endpoint is available and is the composer's call.
- **`CONTEXT.md`'s `"~"` glossary entry gains the binding rule and the threat model**, and a
  cross-reference to this ADR. This is where a reader goes first to ask what the mark is for, and
  today it answers only what it looks like.
- **`0022` gains a status-line amendment pointing here**, on the `0007` precedent — *"accepted —
  §Constants amended 2026-08-01, recorded in that section."* Its measurements stand untouched.
- **Two Bullets on `runs/auxo-ai` move, both downward.** `american-express/c4` goes `~5 hours` →
  `~4.5 hours` and `/c3` goes `~60 minutes` → `~55 minutes` if the rubric's default is taken. Both
  are currently the high endpoint. This is the bar on the re-render, not a hand edit.
- **No re-calibration is owed.** `~4.5 hours` carries one tilde, exactly as `~5 hours` did, and the
  four extra characters are charged at `CHARS_PER_BULLET`'s normal rate. The template is not touched,
  so `0022` §2's *"must not run a re-calibration on this ticket's account"* holds here too.
- **`0029`'s deferral is discharged.** Its Consequences paragraph beginning *"`~4--5 hours` still
  cannot render as a range"* is answered: it still cannot render *as a range*, and it can now render
  as `~4.5`.
- **The arc's closing beat is unblocked.** Five ranges now have a single figure each, so the
  aggregate is a sum rather than an interval — which is the reason #70
  pulled this out of the fog.
- **The bank is not migrated.** Nothing in `bank/` changes; §1 is the decision that it does not.
