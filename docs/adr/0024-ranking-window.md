# Six Bullets to an entry, three claims to rank it

**Status:** accepted

## Context

The map (#47) granted the per-Entry cap a rise to **6** before any ticket opened: an Entry takes up
to six Bullets where the Claims qualify and the page has room. That was a given, not a question.
The question is what else moves with it.

`MAX_BULLETS = 3` (`tools/pack.py:88`) was doing **two jobs**:

- **`tools/pack.py:176`** — `min(MAX_BULLETS, claims ≥ 0.50)`, the **slot cap**. The one the maker
  raised.
- **`tools/pack.py:169`** — `self.ordered_claims[:MAX_BULLETS]`, the window the **Entry score**
  averages over. `CONTEXT.md` defended it deliberately: *"it ranks an entry on what it can actually
  put in its three Bullet lines, so a single dead-on claim can't outrank a broadly relevant job."*

Raise the constant and both move. On `runs/zs-btsa` that reorders the competition pool:

| Entry | top 3 (today) | top 6 |
|---|---|---|
| `american-express` | 1.00 | 0.90 |
| `auto-apply` | **0.92** | 0.71 |
| `xlscout` | **0.90** | 0.78 |
| `sweatpact` | 0.50 | 0.38 |

`auto-apply` and `xlscout` swap, and the **Epsilon tie band** does not catch it — the gap widens
from 0.02 to 0.07, so what is a tie today becomes an ordering. Nobody asked for that.

### What the Entry score is actually for

Tracing every read of it settles more than the table does. `Entry.score` is used in exactly three
places: `order_entries` sorts on it (`tools/pack.py:353`), the ε band groups on it, and
`allocation.md` prints it. It does **not** decide how many Bullets an Entry gets — `Entry.slots`
does that independently, off `min(cap, claims ≥ BULLET_FLOOR)`. And the page's *visible* order is
not the competition order either: every `job` renders under Experience and every `project` under
Projects, whatever the pool decided.

So the Entry score answers one question and only one: **when the page runs out of lines, who gets
shrunk first.**

That reframes the choice. It is not "how good is this entry" in the abstract — it is "what claim
does this entry have on scarce page." Depth already has its own answer to that, in `slots`: more
qualifying claims, more slots, no ranking involved.

### A mean over the top *N* stops behaving when *N* outruns the claims

At a window of 3 most entries genuinely have three claims, so "top 3" is the top 3. At 6 almost
nothing does — on this bank three of four entries have fewer qualifying claims than that — so "mean
of top 6" quietly becomes **"average quality of the entire entry."** Which flips an incentive:

```
xlscout, with one honest 0.55 claim added to the bank:
  window 3:   0.90 → 0.90    unchanged
  window 6:   0.78 → 0.74    demoted
```

Under a 6-wide window, **ingesting more evidence pushes an entry down the page.** That is not a
rounding artefact; it is what a mean does when the window outruns the claims. A top-3 mean can
never fall when a claim is added, because a new claim either misses the window or displaces
something smaller. A top-6 mean can. And the other half of this system is a skill whose entire job
is to add claims.

### The window was reading claims that can never render

`ordered_claims` is every claim, not the qualifying ones. So a claim below the 0.50 **Bullet
floor** — one that cannot take a slot on any page, at any cap — still counts toward the mean that
ranks the entry. An entry scoring `0.90 / 0.20 / 0.20` ranks at **0.43** on the strength of two
claims that will never appear.

The docstring at `tools/pack.py:169` already disowns the principle that licenses this:

> *An entry with fewer than 3 claims averages what it has: padding with phantom zeros would rank an
> entry on claims it never wrote.*

It refuses to invent zeros, then accepts real 0.20s, which reach the page exactly as often as a
phantom zero does. At a window of 3 this rarely bit, because an entry's top three are usually all
above the floor — it does not change a single number on `runs/zs-btsa`. At 6 it bites constantly,
because the window reaches down into exactly the claims the floor excluded.

## Decision

### 1. The slot cap rises to 6. The ranking window stays at 3.

`MAX_BULLETS = 6` keeps the name and means what it says. The window is no longer expressed in terms
of it.

**An entry is ranked on its best evidence and gets its width from its depth.** Peak quality decides
the queue; depth decides how many slots the entry earns once it places, via `min(6, qualifying)`.
Those are separate questions and they now have separate answers, which is what the single constant
was preventing.

> **Narrowed by `0037` §6.** The cap counts **units**, not claims — `min(MAX_BULLETS, units)` — so a
> merged group of three claims spends one of the six. Six stops being the target and becomes a
> backstop, because `0037` §2 is what now decides whether a beat is worth a line. §2's ranking window
> is untouched and still averages the top three qualifying **claims**.

### 2. The window is qualifying claims only

The mean is over the top three claims **at or above the Bullet floor**, averaging fewer where there
are fewer. Window and slots now read the same set — claims that could actually take a Bullet —
differing only in their cap. `CONTEXT.md`'s sentence about ranking an entry on what it can put on
the page becomes literally true again.

On `runs/zs-btsa` this changes nothing: no entry's top three contains a sub-floor claim. It is a
rule-shape decision, taken while the rule is cheap to change.

### 3. The 3 is a literal, not a named constant

`Entry.score` reads the window in one place and nothing else reads it. It stays a literal there,
with the reasoning in the docstring and in this ADR. `MAX_BULLETS` remains the only new entry in
the selection-knobs block.

The knobs block holds numbers you might **tune**. The 3 is not one — it is what *Entry score*
**means**, and turning it is redefining the metric rather than adjusting it. Parking it beside the
floor and the tie band would advertise a dial that is not a dial.

### 4. The Bullet floor stays at 0.50

At a cap of 3 the cap bound first almost everywhere; at 6 the **floor** becomes the real selector,
and on `runs/zs-btsa` the marginal fifth and sixth Bullets are precisely the 0.50s. It stays
anyway, on one distinction: **the floor and the budget answer different questions.** The floor asks
*is this worth showing at all*; the page asks *is there room*. A 0.51 sixth Bullet only reaches the
page when lines are spare — 19 Bullets wanted against 24 available on this bank — so it fills a
line that would otherwise be white space. Making the floor answer both questions is the same
overloading this ADR just took off `MAX_BULLETS`.

### 5. The Experience floor stays at ≥ 1 Bullet

No code change: the reservation is `ENTRY_HEADER_LINES + 1`, tied to the **Elastic block**'s
minimum rather than to the cap, and `experience_floor` reads `entry.slots` only as a yes/no test
whose answer the cap does not change. The floor guards against an *empty* Experience section, and
it still guards that.

## The cost, stated rather than waved past

**A deep-but-flat entry can spend six lines to show one good thing.** An entry with one 1.00 and
five 0.50s earns six slots on count alone. The new Entry score ranks it at 0.67 so it queues
mid-pack, but nothing stops it taking six lines once it places. This is real and it is not fixed
here — it is a claim about **proportion between blocks**, which no floor and no window can express.
It is deferred to #49 along with its sibling: a job at 1 Bullet beside a project at 6.

**The one-element mean gets sharper, not softer.** `0008` noted the odd ordering a one-claim entry
produces, since its Entry score is the mean of a one-element set. Restricting the window to
qualifying claims *removes* the sub-floor claims that were accidentally dragging such entries down.
An entry with one 1.00 and two 0.20s went from 0.43 to 1.00 — top of the pool, for a block worth
three lines. That is accepted because thinness is a **bank** problem with a **bank** check already
pointed at it (**Shallow entry**), and the ranking is the wrong place to punish it.

**Two numbers that used to be visibly one are now visibly two.** Someone will read `MAX_BULLETS =
6` beside `[:3]` and try to reunite them. §3 is why the literal carries its reasoning inline.

## Rejected

**Follow the window to 6.** The constant keeps one meaning and `CONTEXT.md`'s sentence stays
literally true. Rejected on the incentive: adding an honest claim demotes the entry that owns it,
on a system whose other capability exists to add claims. It also ranks an entry on claims that may
never render, and reorders `runs/zs-btsa` for a reason nobody asked for.

**A third named constant, `RANK_WINDOW = 3`.** Honest and readable, and the shape this ADR was
expected to take. Rejected because the value is read once, in the method that defines the metric,
and putting it in the knobs block advertises it as tunable when changing it is a redefinition.

**Window = `self.slots`.** No new constant, reads a property that already exists, and it is the
most plausible misreading of "don't name a new constant" — which is why it is refused on the
record. It is the follow-to-6 answer wearing different clothes: `slots` is `min(6, qualifying)`, so
it carries the same demotion (xlscout 0.78 → 0.74).

**Define the window by the Fit rubric's anchors** — the mean of everything at 0.70 or above, so no
count is invented at all. It dies on `sweatpact`, where nothing clears 0.70 and the Entry score is
undefined. And it is the average answer again.

**Raise the Bullet floor to 0.70**, the next rubric anchor up and the only principled place to move
it. It deletes `sweatpact` from the page entirely — all three of its qualifying claims are 0.50, so
it earns zero slots and never places — and costs `xlscout` and `auto-apply` one Bullet each. Fewer
Bullets, on a map whose complaint was too few Bullets. Anything between the anchors (0.55, 0.60) is
a number nobody chose, which is the fault #47's destination names.

**Raise the Experience floor to ≥ 2 or ≥ 3 Bullets**, to close the job-at-1-beside-project-at-6
look. The reservation is taken **unconditionally, before anything competes**, so it spends page
whether or not it was needed — and spends more of a budget that six-slot entries made tighter. It
also needs partial-reservation logic for a job with fewer qualifying claims than the reservation,
where today's rule drops the job out of the floor wholesale.

## Consequences

- **`tools/pack.py`**: `MAX_BULLETS = 6` with a rewritten comment that no longer explains the Entry
  score; `Entry.score` becomes `ordered_claims`-filtered-by-floor sliced `[:3]`, with the docstring
  carrying §1–§3. `Entry.slots` and the Omission view's `f"beyond the {MAX_BULLETS}-bullet cap"`
  follow the constant to 6 with no edit. Carried by #53, not by this ticket, because #50's wrap
  decision lands on the same lines.
- **`CONTEXT.md`**: **Entry score** rewritten to state the window, its contents and why it is three
  when the block holds six; **Slot** and **Elastic block** follow the cap; **Bullet floor** keeps
  its number but loses the *"soft cap of ~3"* in its own justification.
- **The Claim-merge duty shifts its footing.** `0016` and `CONTEXT.md` argue it from *"duplicates
  take two of three bullet slots"* — at six that is two of six, and weaker. The other half gets
  **stronger**: with the window at three qualifying claims, two near-duplicates that both score
  well occupy two of the three positions the entry is *ranked* on. The duty survives on the
  ranking. Written down because a reader who sees only the six will conclude it relaxed.
- **`SPEC.md`** keeps its v1 normative text and gains *Extended* parentheticals at the rollup and
  allocation steps, per the convention `0020` and `0021` set.
- **`tests/test_pack.py`, `.claude/skills/ingest/SKILL.md`, `.claude/skills/tailor/SKILL.md`** all
  cite the 3 and are updated by #53.
- **This ADR extends `0006` and supersedes it in one place.** `0006`'s rollup — *"entry score =
  mean of its top 3 claim scores"* — survives as to the 3 and is narrowed to qualifying claims; its
  *"Slots = `min(3, claims ≥ 0.50)`"* and *"header + 1..3 bullets"* are superseded by 6. `0007`,
  `0008` and `0016` cite the old numbers in passing and are left standing as the record of what was
  decided when.
