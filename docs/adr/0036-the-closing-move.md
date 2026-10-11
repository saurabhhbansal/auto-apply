# The closing move asks the situation and proposes the sum

**Status:** accepted

## Context

`0032` put an optional `## lead` block in the Entry file holding the two ends of the arc, fixed its
four parts — `number:`, `provenance:`, `**Situation:**`, `**Aggregate:**` — and handed two things to
this ticket by name: *"how `ingest` asks for it, and how the four existing entries are amended through
the Return door is #76's."*

Charting had already settled the interaction. The agent does the arithmetic and hands it back as a
question — *"these five look like about 17 hours a month — is that fair?"* — and the maker's **yes** is
what makes the fact spoken, so `0015`'s *no fact may appear in the entry file that was not spoken*
holds and the tier stays `estimated`. The maker judges; the maker never produces.

So the shape of the fact was fixed and the shape of the exchange was fixed. What was open is where in
`0014`'s session the exchange happens, what the agent has to read in order to have anything to
propose, what survives in the file afterwards, what happens when there is nothing to sum, and how any
of it reaches four entries written before the block existed.

### What the agent is actually being asked to compute

Not one of the five figures that make up Amex's ~17.5 hours is in a `number:` field.

| claim | `number:` | where the saving is | reading |
|---|---|---|---|
| `c1` | `~75%` | prose: *"from 3--4 hours to about 1 hour"* | ~2.5h — a **subtraction** |
| `c2` | `~85%` | prose: *"from 5--6 hours of hand rework to about 1 hour"* | ~4.5h — a subtraction |
| `c3` | `50--60 min per month` | the field | ~55 min — **crosses units** |
| `c4` | `~4--5 hours per cycle` | the field | ~4.5h |
| `c7` | `~50%` | prose: *"from around 10 hours to around 5"* | ~5h — a subtraction |

Three percentages whose absolute saving exists only in the Assertion prose; one figure in minutes
against a total in hours, which `0033` forbids converting anywhere except inside an aggregate; and
"per cycle" written three times, "per month" once, "monthly refresh" once, with nothing in the file
stating that a cycle is a month.

`0034` §5 already named this species of figure correctly — **a reading, not arithmetic** — and that is
why the maker vouches rather than rubber-stamps. This ADR decides what they are shown in order to
vouch.

## Decision

### 1. The aggregate is a sum, or it is absent

There is no non-numeric closing beat. An entry either has two or more claims whose figures can be
added, or it has no `**Aggregate:**` at all.

The map's own table listed `xlscout`'s closing beat as *"~95% usable, writers running it themselves"*,
and that is not a sum — `~95%` is `c1`'s own number, already in `c1`, and *writers running it
themselves* is `c5`'s point. It reads like a closing beat and contains no addition.

It is refused on `0015`'s asymmetry, one level up. **A sum has a right answer the maker can check.**
They can look at five lines and say *no, `c1` is inside `c2`*. *What did it all come to* has no right
answer, so their yes carries no information, and the fact then lands in the one file with no lint
behind it on the strength of a nod. That is `0013`'s drafting failure wearing a question's clothes.

`xlscout` therefore gets a **situation-only lead**, and `~95%` stays where it already traces cleanly:
in `c1`'s Bullet.

### 2. One exchange, and the total is the last thing shown

The agent prints the per-claim readings, names the pairs it suspects overlap, and lets the total
arrive as the consequence:

> *"Reading the figures off your files: `c1` about 2.5 hours (3--4h down to ~1h), `c2` about 4.5,
> `c4` about 4.5, `c7` about 5, `c3` about 55 minutes. `c5` and `c6` carry no figure. That comes to
> about 17.5 hours a month — except `c1` is the mapping step in the scorecard and `c2` is the
> scorecard compilation, so those might be the same work counted twice. Are they?"*

There are three separable ways the agent can be wrong and they need different things from the maker:
a **misread** (caught by looking), a **cadence error** (caught by knowing), and **double-counting**
(caught only if someone points at the two Assertions). The itemisation is what makes all three
visible at once; the overlap pairs are not a separate topic, they are what the table is *for*.

**Rejected: two rounds** — confirm the readings, then ask about overlap. It separates the two
judgements cleanly, and it stops one *yes* ratifying five readings that were skimmed. It loses because
it is `0014`'s banned interrogating register arriving at the end of a long session, at the point of
maximum fatigue, which is where reflexive approval is cheapest.

**The cost is real and is accepted:** one *yes* covers five readings, one cadence assumption and one
overlap judgement together.

### 3. The working goes in prose, and no field is added

The block keeps what `0032` gave it. The working lands in an `**Evidence:**` line — the shape `0034`
§5's `## merge` block already uses for the same species of fact:

```
## lead
number: ~17.5 hours per month
provenance: estimated

**Situation:** The whole Amex Offers monthly reporting cycle was run by hand.

**Aggregate:** Five of the automations together gave back about 17.5 hours a month.

**Evidence:** c1 ~2.5h (3--4h -> ~1h), c2 ~4.5h (5--6h -> ~1h), c4 ~4.5h, c7 ~5h (~10h -> ~5h),
c3 ~55 min. Mapping step and compilation confirmed separate stages. c5 and c6 carry no figure.
Cadence confirmed monthly.
```

**Rejected: a `claims:` field** listing the constituents machine-readably. It was recommended, on the
argument that the lead's constituents are the one thing nothing can recover later — you cannot read
`c1, c2, c3, c4, c7` back out of `~17.5 hours` — and that a stored sum with checkable members is the
difference between the staleness problem being solvable and not. It is refused on the maker's call:
the block is three days old and already has four parts, and a fourth field plus the `bankcheck.py`
validation it implies is a larger thing than this ticket should be growing.

**The cost, stated rather than waved past.** `0034` put a stale merge sum on the map as fog. **The
lead is worse and this ADR does not fix it.** A merge sum only misleads on a run where that exact
group merges again; the lead is printed on **every** run. Amend `c7`'s figure through the Return door
and `~17.5 hours` is silently wrong on every résumé generated afterwards, with its constituents
sitting in prose where no check will reach them. The fog patch widens from merges to both.

### 4. One closing move, and it reaches back to what was said

The lead is collected in a single move after the last claim has landed or been parked, before
`0014`'s end-of-session step. Both halves in one exchange, one block, one write.

The tempting split is *situation early, aggregate late* — the aggregate cannot be asked until every
claim has its figure, and `0032` §3's two probes (*what did this look like when you got there*, *what
was this built against*) are almost verbatim two of `0014`'s wide-pass **angles**. It is wrong, for a
reason that is easy to miss:

> **The situation is by definition the condition the claims share, and you cannot know a condition is
> shared until you know what the claims are.**

Amex's opening is not a fact about `c1`. It is what was true across `c1`–`c7`. Asked in the wide pass
it is asked before it is answerable, and the agent would have to decide mid-pass whether an angle's
answer is becoming a claim or becoming the lead — which is a discriminator, which is the `type:`
dependence `0032` §3 refused arriving by a side door.

The counter is that *what did this look like when you got there* is the best memory-jogging opener in
the session, and asking it last means the maker has already spent an hour framing everything as
separate achievements. That counter dissolves, because **`0014` already asks it.** The angles are in
the wide pass today. What is missing is not the question — it is that the answer currently either
becomes a claim or evaporates. So the closing move **reaches back to what the maker said**, and where
the wide pass produced nothing shared it asks cold (§6).

**The cost:** the whole lead hangs off a move at the very end of a long session, so a session that
stops at claim 4 of 7 gets no lead. `0014` made stopping at any claim boundary a *normal state*, so
this will happen. The Return door catches it (§7), and §5 is what makes the catch cheap.

### 5. Nothing is written when there is nothing to sum, and a trigger does the remembering

An entry with no aggregate gains no marker. Not a field, not a null, not a note that the question was
asked and came back empty.

`0014` deleted the *rests on memory alone* marker because a field with no consumer that **reads like a
verdict** is treated as one by the next session. A recorded null is worse than that here, and for a
reason particular to the lead:

> **Whether an aggregate exists is a function of the claims, and the claims grow.**

`bank/projects/auto-apply.md` is `ended: present`. The day it gains a claim with a figure beside
another one, a null written in August 2026 is false — and false in the direction that stops anyone
looking. A parked claim's mark is durable because *that claim* is finished. *This entry has nothing to
sum* is a statement about a set that is still open.

What makes writing nothing affordable is that §1 hands the aggregate a mechanical trigger, computed
off the file every time rather than remembered:

> **Two or more claims carrying comparable figures, or the aggregate is not asked.**

| entry | claims with a figure | aggregate offered |
|---|---|---|
| `american-express` | 5 of 7 | **yes** |
| `xlscout` | 1 of 5 | no |
| `auto-apply` | 0 of 7 | no |
| `sweatpact` | 0 of 5 | no |

`auto-apply` is never offered an aggregate — not because anyone recorded that it has none, but because
seven claims with no numbers in them cannot have one. If `c8` lands next month with a figure beside
`c9`'s, the offer appears on its own. This is `0016`'s accepted re-asking (*"the session may re-ask
angles that already came up empty"*) made almost free.

The **situation** half has no such trigger and is asked once at every closing move. It is a question
about the entry, not about its arithmetic.

**The cost:** an entry whose savings are real but live entirely in prose, with no `number:` field
anywhere, is never offered an aggregate and nobody notices. That is a bank the interview under-dug,
and the honest place to catch it is the next Return session, not a trigger that fishes.

### 6. Ask the situation. Propose the sum. This refines `0032` §2

`0032` §2 said the situation *"arrives the way the aggregate does … the agent reads the entry, offers
a sentence, and the maker's yes is what makes it spoken."*

**That is rule 3 of `ingest`** — *never arrive with a drafted Entry; a plausible draft gets nodded
through and is true forever* — and it is the worst instance of it in the system. *"The whole Amex
Offers monthly reporting cycle was run by hand"* is trivially inferable from `c1`–`c7`, it will sound
right, it will be approved, and it then sits at the **top of every résumé the bank ever produces** as
a statement of fact about the maker's own history that they never said. Unlike the sum, it has no
working to be checked against and no arithmetic that could come out wrong.

`0032` did not see the collision because it was reasoning about **compose** time, where it correctly
refused the same move for the same reason.

**The closing move is therefore asymmetric:**

| half | how it arrives | why |
|---|---|---|
| **Situation** | **asked, never proposed** | there is nothing to compute; the maker is the only source there has ever been |
| **Aggregate** | **computed and proposed** | nobody adds five prose subtractions across three cadences from memory |

This is charting's own *the maker is a bad source and a good judge*, applied to both halves properly
instead of to one. It is **true of a sum** — which is exactly why the agent must do the reading — and
**false of a situation**, where asking is just `0014`'s interview doing its ordinary job.

`0032` §2 stands in every other respect: both halves are spoken, both route through the maker, and the
lead's facts live in the bank.

### 7. The Return door gains a line in the readout, not a fourth trigger

`0016`'s readout already shows the maker what the agent can see. It gains the lead:

> *"Amex has 7 claims, 5 of them with figures, and no lead — want to do that now?"*

and the closing move becomes **independently runnable**. There is no new mode, no flag and no fourth
trigger beside `0013`'s three: the agent looks at the file, sees no `## lead` block, and says so — the
same act as greping the marks. `0016`'s *neither way is chosen by a flag — check whether the file is
there* extends one level down without amendment.

Adding a `## lead` block touches no claim ids, so it is an **amend** under `0016`'s *amend, never
regenerate*, in the same class as editing frontmatter after a promotion.

**On a return there is no wide pass to reach back to**, so §6 does the work: the situation is asked
cold. That is the same rule as a cold session, not a special case — §4's move reaches back to *what the
maker said*, and on a return nothing was said.

**What the four entries actually get:**

| entry | situation | aggregate |
|---|---|---|
| `american-express` | asked | offered — the ~17.5h |
| `xlscout` | asked | not offered (§5) |
| `auto-apply` | asked, likely nothing | not offered |
| `sweatpact` | asked, likely nothing | not offered |

Two of the four will honestly come away with nothing, which `0032`'s cost section already predicted.
Under §5 that costs no bytes and will be asked again next session.

`bankcheck.py` is the only verifier — the files are in the private `bank` repo under `0019` and CI
never reads them. This is the third time this map has paid that window knowingly, after `0031`'s
`dates:` migration and `0032`'s own.

### 8. The stored `**Aggregate:**` states its scope, and the tier is `estimated` by construction

`0032` §2's worked sentence was *"The automations together gave back about 17.5 hours a month."*
**The automations** — all seven, two of which contributed nothing. The tailor composes the page's lead
line from this block, so that phrasing reaches the résumé.

It is wrong in a way that is easy to miss because it is not inflation. The figure is if anything
**low**: `c5` and `c6` are automations of the same cycle that saved real time nobody ever counted, so
the honest total is above 17.5 by an unknown amount. What is wrong is that a vouched figure is
attributed to a set larger than the one that was vouched for, and *"so does that 17.5 include the
GPTs?"* is a question with no answer anywhere except the Evidence line.

So the stored sentence says **five**. Four characters of a 92-character budget buying the difference
between a figure that can be defended in a room and one that cannot.

Two things follow at no extra cost:

- **`provenance: estimated` is settled by construction, not by default.** `0015`'s fallback rule would
  have got there anyway, but the stronger statement is available and is worth having on the record: a
  sum built from three prose subtractions, one unit conversion and a human judgement about overlap is
  **never** `measured`, however its constituents are tiered. Nobody can later argue the sum inherits
  `measured` from a `measured` member.
- **The non-contributors become a free question.** Laying out the working means the closing move can
  add *"`c5` and `c6` have no hours on them — is there a figure for either?"* That is not new
  machinery. It is `0015`'s **"So what?" redirect** firing at the one moment in the session when the
  gap is most visible, with three landings already defined. Usually there will be no figure, and the
  entry is then honest about what it counted.

## The cost, stated rather than waved past

**The staleness hole is now the biggest unguarded thing on this map.** §3 accepted it deliberately. Of
every figure the system prints, the lead's sum is the one printed most often, derived from the most
sources, and checkable by nothing. `check_number_trace` will happily confirm `~17.5 hours` traces to
`lead.number` forever after `c7` has been amended to say something else.

**One `yes` carries five readings.** §2 chose a single exchange over two, so a skimmed table passes
whole. The mitigation is that the table is short and the overlap pairs are named in it, not that the
maker is expected to be careful.

**The lead hangs off the last move of the session.** §4's placement is forced by *the situation is
what the claims share*, and the price is that the most-printed line in the entry is collected when the
maker is most tired, in a session they may not finish.

**A page can carry two vouched sums, one inside the other.** Amex can render a lead of `~17.5 hours`
and a merged Bullet of `~8 hours` over `c1+c3+c4`, with nothing on the page or in either block saying
the second is wholly contained in the first. Both trace clean. Not decided here — it is a compose-time
question and it goes to the map as fog.

**Two entries get a real interview cost for a null result, repeatedly.** §5 chose re-asking over a
marker, so `auto-apply` and `sweatpact` are asked for a situation at every Return session and answer
*there isn't one* every time. The aggregate trigger spares them half of it; the situation half has no
trigger and cannot have one.

## Rejected

**A non-numeric aggregate** — *"~95% usable, writers running it themselves"*. §1. It loses because the
maker's yes carries no information over a claim with no right answer.

**Two exchanges, readings then overlap.** §2. Cleaner separation of two judgements; loses to `0014`'s
banned register at the point of maximum fatigue.

**A `claims:` field on the lead block.** §3. It was the recommendation, and it is the only thing that
would make the staleness problem solvable. Refused as too large a change to make in passing.

**Folding the aggregate into a `## merge` block** — `## merge c1+c2+c3+c4+c7`, with the lead citing it.
One object, one staleness rule, ids already in the heading, `bankcheck.py` validation already written.
It loses because `0034` §3 caps a merge at **3 claims** and a stored merge group **reserves Bullet
width and competes at compose time**. A five-id merge block is either a Bullet the entry never asked
for, or a special case meaning *this one is not really a merge* — which is re-opening a closed ADR to
save a field.

**Situation captured in the wide pass, aggregate at the end.** §4. The natural reading of where each
question lives, and it is where `0014`'s angles already are. It loses because the situation is only
judgeable once the claim list exists, and because it forces a mid-pass classification that is `0032`
§3's refused discriminator by another route.

**Recording the null** — a marker meaning *asked, there isn't one*. §5. It is the obvious fix for the
readout offering `auto-apply` a lead forever. It loses because the claims grow, so the null is not a
durable fact, and because `0014` already deleted a marker of exactly this shape.

**The agent proposing the situation from the entry's Evidence**, with the maker's yes as the gate —
`0032` §2's literal instruction. §6. It loses to `ingest`'s rule 3, at the highest-stakes point rule 3
covers.

**A dedicated one-off migration** for the four existing entries, outside the skill. Fastest way to get
leads into the bank today. It loses because it leaves the skill with no path for the fifth entry whose
session stopped early — the case §4 guarantees will happen.

**Keeping `**Aggregate:**` general and letting the Evidence carry the scope.** §8. The composer does
read Evidence, so the information is technically present. It loses because the sentence the composer
starts from is the one that reaches the page, and *the automations* is what it would carry.

## Consequences

- **`0032` §2 is refined.** The situation is **asked, never proposed**; the aggregate is proposed. The
  rest of §2 — both halves spoken, both maker-gated, the facts in the bank — stands.
- **`0032`'s `## lead` block gains an `**Evidence:**` line** carrying the per-claim readings, the
  overlap answer and the cadence. No new field; `0034` §5's shape reused.
- **`**Aggregate:**` names the size of the set it sums**, and `provenance:` on a lead is
  **`estimated` by construction**.
- **`ingest/SKILL.md` gains one closing move** between §6's stretch check and §7's ending — asked
  situation, proposed sum, and the aggregate gated on two or more comparable figures.
- **`ingest/SKILL.md` §5's "what never goes in the file" list gains the null lead**, for the same
  reason it already lists which shallowness check a parked claim failed.
- **`0016`'s readout gains a line** for a missing lead, and the closing move is independently
  runnable. No fourth trigger, no flag, no new mode. Adding a `## lead` block is an **amend**.
- **`0015`'s "So what?" redirect gains a second firing point** — a claim contributing nothing to its
  entry's sum.
- **The four existing entries are amended through the Return door** as part of `#78`, verified by
  `bankcheck.py` alone (`0019`).
- **The staleness fog patch widens from merge sums to merge sums and leads**, and the lead is the
  worse of the two.
- **New fog: two vouched sums on one page**, the merged Bullet's inside the lead's, with nothing
  saying so.
- **No re-calibration is owed.** No constant moves and the template is not edited by this ADR.
