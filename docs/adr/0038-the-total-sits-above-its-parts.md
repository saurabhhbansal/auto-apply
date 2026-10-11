# The total sits above its parts, and the Fork sees the lead

**Status:** accepted

## Context

`0036`'s cost section named this and deliberately did not decide it:

> **A page can carry two vouched sums, one inside the other.** Amex can render a lead of
> `~17.5 hours` and a merged Bullet of `~8 hours` over `c1+c3+c4`, with nothing on the page or in
> either block saying the second is wholly contained in the first. Both trace clean. Not decided
> here — it is a compose-time question and it goes to the map as fog.

Each half was made honest in isolation and neither looked at the pair. `0034` §5 vouches the merge
sum against its three claims; `0036` vouches the lead's sum against the entry's claims. `0016`'s
Return door and `check_number_trace` both confirm each figure traces — which is exactly why neither
would ever notice. A reader who adds them gets ~25.5 hours, which happened nowhere.

`0037` is what made it look routine rather than incidental. It recorded the maker's second motive for
merging — *"what if each of them just saves one hour, and combined we are saving three hours? We
would want a bigger number over there"* — and it made merging the **default** rather than an option.
So a merge exists to produce a figure, and it arrives on most entries that have a lead at all.

### What the page actually looks like

The framing above is wrong in one respect, and correcting it is most of this ADR. Here is the Amex
column once `0032`, `0034` and `0037` land:

```
The whole Amex Offers monthly reporting cycle was run by hand; automating five
of its steps gave back ~17.5 hours a month.
  • Replaced hand-written business-review insights with a custom GPT…       (no figure)
  • Unified Scorecard, Forecast, Pipeline and Plan behind a custom GPT…     (no figure)
  • Automated the mapping, the deck's data cuts and the summary draft,
    cutting ~8 hours a month                                                (c1+c3+c4 → 8h)
  • Owned ~60 of ~150 KPIs and automated the slowest, halving a
    ~10-hour refresh                                                        (c7 → 5h)
  • Swapped hand rework for a rebuilt compilation, ~85%                     (c2 → 4.5h)
```

The merged Bullet's `~8` is inside the lead's `~17.5`. So is `c7`'s 5 hours. So is `c2`'s 4.5.
**Every figure below the lead is inside the lead**, because the lead is the sum of exactly those five
claims. Merging did not create the containment; the arc did. A merge only makes one of the parts
bigger.

And that structure is the one that was asked for. `0034` §5 records the objection that put the sum on
a merged Bullet in the first place:

> *"If we are saying 17.5 hours at the top, and then one line says seven hours and the next two say
> nothing, the 10.5 hours that are left don't get added up."*

That is a description of total-above, parts-below, offered as the requirement.

## Decision

### 1. A total above its parts is the correct page

There is no composition rule and no new check. The merged Bullet may carry a figure the lead already
counts, exactly as an unmerged Bullet may.

A total on top with its parts underneath is how every report a reader has seen is laid out, and
`0032` put the aggregate on top precisely so it would read that way — the frameworks survey behind
`0032` found that **every published aggregate is a lead, not a close**, and this is why. The
double-add scenario
requires a reader to take in a sentence that says *five of its steps gave back ~17.5 hours a month*
and then treat the bullets directly beneath it as savings in addition to it.

The one thing genuinely particular to the merged line — that `~8` is itself a sum of three, and so
the only figure on the page that is an aggregate rather than one claim's own number — was put to the
maker as the reason this might not be an ordinary part. It was not: it reads as a part.

**The availability question is never reached.** The ticket asked whether a subset check is even
buildable, given that `0036` §3 refused the machine-readable `claims:` field and `0033` forbids
arithmetic across units — `c3` crosses units inside the `~8` and the lead crosses them again. Both
are true, and both are beside the point. The check is not refused because it is unreachable. It is
refused because **there is nothing for it to enforce**: it would fire on the page working as designed.

### 2. The merge Fork shows the lead's figure and its Evidence line

What is exposed here is not the containment. It is that the **overlap judgement is made twice, by
different moves, months apart, and the second one never sees the first.**

The two sums are readings of the same five claims, so they have to be consistent, and consistency has
an arithmetic shape: `17.5 − 8` must equal `c2 + c7`. The addition is not where it breaks. `0036` §3
already stores one overlap call in the lead's Evidence line:

> *Mapping step and compilation confirmed separate stages.*

Then `0034` §5's Fork fires on a later run and asks a second one:

> *"`c1` saves ~2.5h, `c4` ~4.5h, `c3` ~55 min — call it ~8 hours a month? **And is the mapping step
> already inside the deck cuts?**"*

`c1` against `c4` is a pair the ingest session never flagged, because the agent flagged `c1` against
`c2`. Answer *yes, it is* and the merge lands at ~6 while the lead still says 17.5, having counted
`c1` on its own. Both trace clean. Neither is checkable by anything.

So where the entry has a lead, the Fork carries it:

> *"The lead for this entry says ~17.5 hours a month over `c1`, `c2`, `c3`, `c4`, `c7`, with the
> mapping step and the compilation confirmed separate stages. For this merge: `c1` saves ~2.5h,
> `c4` ~4.5h, `c3` ~55 min — call it ~8 hours a month? And is the mapping step already inside the
> deck cuts?"*

One line of context in a prompt that already exists. It is the only place in the system where the two
sums are ever in the same room.

### 3. A Fork answer that contradicts the lead amends it in the same write-back

Showing the lead makes a disagreement visible; it does not say what to do about one. Without §3, the
maker answers *call it ~6, the mapping is inside the deck cuts*, the `## merge` block is written, and
the lead is not — so a figure the maker just disowned prints on the résumé being composed in that
very run.

This is not the staleness case on the map's fog list. There, a claim is amended later and nothing
notices. Here the system **knows** the lead is wrong, **has** the corrected overlap answer, and the
maker is standing in front of it.

Nothing new is opened to do it. `0008`'s add path is already writing the merge block, the Fork
already halts (`0034` §5, kept by `0037` §5 for summed merges), and adding to a `## lead` block is an
**amend** under `0016`'s *amend, never regenerate* — the same class as `0036` §7's adding the block in
the first place. One more write on a path that is already open and already stopped.

### 4. The Merges view does not change

`0037` §5's section in `allocation.md` keeps its columns. No lead total is printed beside a merge row.

That section exists so the **reason** can be judged, on `0010`'s argument that a judgement is
reviewable when it turns into a claim about the maker's own history. *"This ~8 is part of the ~17.5"*
is not that. It is a claim about the page's own arithmetic, it is true of `c7`'s line and `c2`'s line
as well, and neither of those gets a row. Printing it would flag as notable the relationship §1 has
just settled as normal.

The case it would half-catch is real and is left where it belongs: a **later** run merges the same
group, no Fork fires because the sum is stored, and in the meantime `c7` was amended and the lead
re-vouched — so the two stored sums disagree with nobody in the room. That is the staleness patch,
which already covers the lead against its own claims. A total on a display row would not detect it,
only let it be spotted by eye, and half a fix in a second place is worse than one problem.

## The cost, stated rather than waved past

**A second reading is vouched inside one Fork.** `0036` §2 chose a single exchange over two and
accepted that *one yes carries five readings*; §3 now puts a sixth thing inside a Fork that was
already carrying a sum and an overlap question. The mitigation is that the amend is only reached when
the maker has **already** said the lead is wrong — it is the consequence of their answer, not a new
question — but the new total is arithmetic the agent does and they vouch in the same breath.

**The amend rewrites prose, not a field.** `0036` §3's refusal of the `claims:` field lands here a
second time. To amend the lead, the agent has to recover its constituents from the `**Evidence:**`
line and rewrite that sentence, `number:` and `**Aggregate:**` together. `0036` named this refusal as
the sharpest thing in it; §3 of this ADR is the second decision to pay for it and the first to pay at
compose time.

**Reconciliation happens only when a Fork fires.** A run that reuses a stored merge sum reconciles
nothing. The two sums are checked against each other exactly once, on the run that first speaks the
merge.

**§1 rests on the reader reading the lead.** If the lead line were ever dropped from a placed entry,
the parts below would be unlabelled parts of an absent total. It cannot be: `0032` fixed that
*a placed Entry keeps its lead — bullets give way, not the frame.* Recorded here because §1 now
depends on that rule holding, and it did not before.

## Rejected

**A composition rule** — the merged Bullet does not restate a figure the lead already counts. §1. It
was one of the map's three candidates. It loses twice over: it deletes the merge sum on every entry
that has a lead, and the merge sum exists on the maker's own objection recorded in `0034` §5. It also
has no principled stopping point, since `c7`'s and `c2`'s figures are restated by the lead in exactly
the same sense.

**A `render.py` subset check** over the two block kinds. §1. Nothing to enforce — it would fire on
the page working as designed. The two obstacles the ticket named (`0036` §3's refused `claims:` field,
`0033`'s ban on cross-unit arithmetic) are real but never reached.

**Saying it on the page** — *"…cutting ~8 hours a month of that"*. §1. Cheap in characters and it
does remove the ambiguity outright. It loses because it is owed equally to `c7`'s line and `c2`'s,
which is three pieces of bookkeeping on a one-page résumé to restate what the sentence above the
bullets already says.

**The lead's total on every Merges row.** §4. The cheapest option the ticket named. It loses because
containment is not a signal once §1 has settled it, and because it would not detect the one case it
was reaching for.

**Filing the contradiction as staleness** and catching it at a future Return session. §3. It keeps the
Fork narrow and puts all stored-sum drift in one place. It loses because the maker is in the room with
the right answer and the wrong figure is about to print.

**An amendment to `0034` §5 and `0036` §3 instead of a new ADR.** *Not a defect* is itself a decision
and needs somewhere to live: `0036` put this on the record as an open worry, and a resolution that
exists only as two edited prompts leaves the next reader finding the worry documented and the answer
nowhere.

## Consequences

- **`0034` §5's Fork gains the lead**, where the entry has one: the stored `number:` and the
  `**Evidence:**` line, shown before the merge's own readings.
- **`0034` §5's write-back gains a lead amend** when the Fork's answer contradicts the lead —
  `number:`, `**Aggregate:**` and `**Evidence:**` together, through `0008`'s add path as an `0016`
  amend.
- **`0036` §3's `**Evidence:**` line is now read at compose time**, not only written at ingest. It is
  the lead's only machine-unreadable record of what it summed, and it is now load-bearing in two
  places.
- **`0037` §5's Merges view is unchanged.**
- **No composition rule, no new `render.py` check, no new field, no constant, and no
  re-calibration.**
- **The staleness fog patch is unchanged in scope.** This ADR closes the in-the-room case; the
  later-run case, where a stored merge sum and a re-vouched lead drift apart with no Fork, stays open
  and still covers both block kinds.
- **`0032`'s *a placed Entry keeps its lead* becomes load-bearing for §1**, not only for the frame.
- **`.claude/skills/tailor/SKILL.md` carries §2 and §3**, as part of
  #78.
