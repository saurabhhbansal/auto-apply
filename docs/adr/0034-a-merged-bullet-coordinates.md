# A merged Bullet coordinates what it cites, and never synthesises it

**Status:** accepted

## Context

Charting on #70 settled that the middle beats are governed by **worth, not by a budget**, and that
worth is served by **merging rather than dropping** — *"I would want to include everything that I did
there, not just three things out of five"*. Five claims may become three Bullets, and nothing the
maker did falls off the page.

That breaks the rule everything else in `0027` is built on:

> **One Bullet, one Claim, one citation.** A prettier sentence that fuses two claims is not a
> candidate. — `0027` §6

The rule was written to stop the composer inventing connections for rhetoric. The merge the maker
wants is the opposite failure mode — one that loses nothing. So the rule breaks for a reason it never
considered, and this ADR says what replaces it (#74).

### #72 moved the ground before this was answered

`0032` took **both ends of the arc out of the column**: an Entry may carry one unbulleted lead line
holding the situation and the aggregate, and the Bullets are purely the middle. It resolved the
closing beat by **not merging at all** — the ~17.5 hours is a fact the maker speaks into the bank,
and the tailor writes its sentence.

That is the whole reason this ADR is affordable. Charting's claim that *the closing beat and the merge
are the same operation at two scales* looked like it had been split by `0032`. §5 below shows it was
not: both ends up as sums the maker spoke, living in the bank as non-competing facts, with the tailor
writing the sentence. One mechanism, applied twice, exactly as charting said.

**And `0032` did not fix the complaint that started the map.** `runs/auxo-ai` left **4 lines unspent**
(`allocation.md`, Room), so the lead is affordable out of the residue and the Amex entry renders the
lead *plus* all six Bullets. `0032`'s own cost section says it: *"the lead took a slot, it did not
stop the entry filling."*

## Decision

### 1. Merging happens at compose time, whatever it costs

**Rejected: the merge lives in the bank.** It was the recommendation put to the maker, and on the
strongest available argument — it is what won `0032` for the aggregate, and it costs nothing
structurally. A Claim that *is* the merge (*"Automated the monthly reporting cycle end to end — the
mapping step, the compilation, the deck cuts and the summary email"*) keeps `0027` §6 literally
intact: one Bullet, one Claim, one citation, `check_number_trace` untouched, `pack.py` untouched, and
every difficulty below evaporates.

It loses on the maker's objection, which is sharper than the one that motivated the ticket:

> *"If we already have the points and the language fixed before the compose, it kind of defeats the
> purpose of having a tailored resume. When the JD comes, we have a single point that covers
> everything, and it would be the top thing that comes up."*

A rollup Claim is the most complete thing in its entry, so it scores at or near the top against
**every** posting. It would not merely fix the fusion — it would win the entry's first slot
permanently, on every run, and the entry would stop being tailored at all. The fusion has to be
chosen against the posting in front of it: a data-engineering JD merges the two custom GPTs and keeps
the pipelines apart, a GenAI JD does the reverse.

**Everything below is the bill for that, and it is paid deliberately.** The maker: *"irrespective of
whatever the cost is — that is what the product is, so that is where the vision should lie."*

### 2. The merge is declared at scoring time, in its own table

`scores.md` gains a second table. **The claims table is untouched** — every claim is still scored on
its own merits, own row, own reason.

```markdown
## Merges

| entry | claims | width | reason |
|---|---|---|---|
| american-express | c1+c3+c4 | 2 | three automations of the same reporting cycle — one argument, not three |
```

> **The worked reason is superseded by `0037` §2.** This one argues from **similarity**, which turns
> out to be the wrong trigger — it would merge `c5` and `c6`, the entry's two 1.00s and its whole case
> for that posting. The column survives; what goes in it becomes *why none of them lands alone*:
> `none of the three lands alone — each is a few hours saved on one step of the cycle`.

Validated as strictly as every other column in that file, each failure naming the row: **2 or 3 claim
ids** (§3), all in one entry, all present in the claims table, no claim in two merges, `width` of `1`
or `2`. A merged claim's own `width` column must read `1` — the group declares the width, so anything
else is ambiguous and stops the run.

Three properties earn it that position, and they are `0025` §3's, because this is the same shape as
the `width` want. It is judged **before the allocation is known and before a word is composed**, so
it cannot be steered toward the sentence the model happens to like. It keeps the seam — the model
judges what is one argument, the script does the arithmetic — with `pack.py` still reading exactly
one file (`0006`). And it costs nothing in determinism: `scores.md` is a function of the bank and the
JD alone.

**Keeping it out of the claims table is what protects `0024` and `0026`.** Collapsing a merge into a
single scored row was the cheaper parse, and it would have made merging decide whether the *entry*
places: `0024` ranks an entry on its **best 3 qualifying claims**, so three rows becoming one moves
the entry score. It would also cost the Omission view the individual scores of claims that rode
along. In a separate table, **`0024` and `0026` never learn that merging exists.**

**For ordering, a group scores as the maximum of its members.** `0026` shares the remainder top-first
by score and `0025` §4 hands residue out in claim-score order; both need a number. Max, because a
merge is at least as strong as its best claim, and because the mean would punish precisely the merge
most worth making — one strong automation pulling two small ones onto the page with it.

`bullets.md` takes the same joiner:

```markdown
## american-express
- american-express/c1+c3+c4: Automated the Tier/Portfolio mapping, the review deck's data cuts and the leadership summary draft, cutting ~8 hours a month
- american-express/c5: Replaced hand-written business-review insights with a custom GPT…
```

### 3. A merge is reserved and self-financing, and it can never be denied

**A merge group of N claims declares a width W, and the group is charged W lines at the reservation
phase** — before `grant_widths` runs, guaranteed. Not a want.

The rule that makes this safe is **W ≤ N**. A merge never costs the page more than its claims cost
unmerged, so it is always affordable and can never be refused. *(Narrowed by `0035` §4: not at an
Entry's **reserved** line, where the unmerged claims would have cost one line rather than N, so W ≤ N
does not hold. There a `width: 2` group is skipped for the best one-line unit, and its claims are
reported in the Omission view.)* `c1+c3+c4` at `width: 2` reserves two
lines where three claims would have reserved three; **the freed line is what puts `c2` on the page**,
and `c2` is what `runs/auxo-ai` cut — *"beyond the 6-bullet cap on an entry"*.

This is why merging is the mechanism for *"include everything that I did there"* rather than merely a
prose improvement. It hands room back.

**A want would have made merging destroy evidence.** Under `0025` §2 width is granted out of what the
evidence did not take, and *"on a full page nothing wraps"*. Three claims merged into one slot on a
full page would have had `grant_widths` refuse the second line and three claims' facts written into
**one** 103-character line — worse than not merging, which held three lines and said everything. That
is the silent drop #77 exists to forbid, arriving through the arithmetic.

**`0025` §2 is not overridden.** *Evidence outranks room* survives untouched, because a merge is not
asking the page for room.

**The caps, and where they came from.** A merge takes **at most 3 claims**, refused at parse the way
`0025` §3 refuses a `width` of `3`. The maker's reason is on the record:

> *"If we have five claims and we are merging into one, it would be allowed to take four lines. Four
> lines is more of a paragraph, which we don't want."*

**`0025` §3's cap does not move.** Width stays `1` or `2`, schema-enforced, exactly as written. With
`N ∈ {2,3}` and `W ≤ 2`, the constraint `W ≤ N` is satisfied automatically and needs no separate
expression. A merge of 2 at width 2 is legal and arithmetically free — it buys the page nothing and
makes the prose one argument instead of two, which is a real reason. It also means merging is not
purely a room-saving device, and #77 has one more door to close.

### 4. A merged Bullet is a coordination, not a synthesis

`0027` §6's other half is the **downgrade-only, Claim-level trace**: every claim in the line is
present in or entailed by the cited Claim's Evidence. Singular. Across three, *entailed by* gets
slippery. The line this ADR was written against:

> *Automated the monthly reporting cycle end to end — the mapping step, the deck cuts and the
> leadership summary — cutting ~8 hours a month*

Three different things are wrong with it, in three different ways. **"end to end"** asserts these
three *are* the cycle; `c2`, the compilation rewrite, is also part of it and is not cited, so the
claim is flatly false. **"the monthly reporting cycle"** asserts the three are one thing; no Evidence
says so — `c1` says *the Amex Offers scorecard*, `c4` says *the review deck*, `c3` says *the monthly
leadership summary email*. **"~8 hours"** is arithmetic across three claims and appears in no Evidence
anywhere (§5 takes that one).

So the rule:

> **A merged Bullet is a coordination of its claims, not a synthesis of them.** Each part of the
> sentence traces to one of its cited Claims. The sentence may join them — a shared verb, a list, one
> subject — but it may not assert anything about their *relationship* that no Evidence states.

> **The merge does the compression; the lead does the synthesis.**

That second line is what makes the first affordable rather than merely strict. The synthesis is
**already on the page**: `0032`'s lead says *"the whole monthly reporting cycle was hand-run;
automating it gave back ~17.5 hours a month"*, and the maker spoke it. The Bullet does not need to
assert the relationship, because the frame above it already did. So:

> *Automated the Tier/Portfolio mapping, the review deck's data cuts and the leadership summary
> draft, cutting ~8 hours a month*

Every conjunct traces. Nothing is invented. And the only judgement the model makes is *these three
are worth one line* — which is #77's, not this ADR's — so `0010`'s refusal to let the model form
conclusions about the maker's history holds without needing a new exception.

**The cost, which the maker was shown before agreeing:** a coordination reads flatter than a
synthesis. *"Automated the deck cuts, the summary draft and the mapping step"* is a list; *"automated
the reporting cycle end to end"* is a sentence. Merged lines will be duller than the ones a free hand
would write, and that is the price of not inventing.

### 5. The summed figure is spoken at the Checkpoint and stored in the bank

**`render.py` cannot check a merged sum.** Not with difficulty — cannot. The real values behind
`c1+c3+c4`:

| | what is stored | what it contributes |
|---|---|---|
| `c1` | `number: ~75%` | **~2.5h** — nowhere in the file. `3--4 hours → about 1 hour` in the **Assertion prose**, minus |
| `c4` | `number: ~4--5 hours per cycle` | ~4.5h (midpoint, `0033`) |
| `c3` | `number: 50--60 min per month` | ~55 **minutes** |

Three separate walls. `c1`'s contribution is a subtraction over a before/after pair in prose. `c3` is
in different units, and `0033` ruled one decision ago that *"conversion is forced only inside the
aggregate… so no check ever does arithmetic across units"*. And a checker would have to know that
`~75%` does not participate while the prose hours do.

That is a **reading**, not arithmetic — precisely what #76 says of the lead's aggregate: *"anything
doing this is reading, not adding, which is the part that can be wrong."*

So the maker vouches, once per merge group, at the Checkpoint. The first run wanting `c1+c3+c4` fires
a Fork — *"`c1` saves ~2.5h, `c4` ~4.5h, `c3` ~55 min — call it ~8 hours a month? And is the mapping
step already inside the deck cuts?"* — and the answer writes back through `0008`'s add path and
`0016`'s Return door as a **non-competing block**, the same species as `0032`'s `## lead`:

```
## merge c1+c3+c4
number: ~8 hours per month
provenance: estimated

**Evidence:** c1 ~2.5h (3--4h -> ~1h), c4 ~4.5h, c3 ~55 min. Separate stages, no overlap.
Spoken at the checkpoint of runs/auxo-ai.
```

**It is not a Claim.** It is never scored, never ranked, never a candidate for a slot — which is what
keeps §1's objection answered: a stored sum cannot win the entry's top line, because it never
competes for one. `number:` and `provenance:` carry exactly the meaning they carry on a Claim, so an
`estimated` sum renders softened under `0022` and may only move down under `0029`.

Every later run merging that group cites the stored figure and **`check_number_trace` works
unchanged** — it is one more traceable number. **The bank accumulates merge sums lazily, driven by
real runs**, which is the only tractable version: Amex's seven claims admit **56** distinct 2- and
3-claim merges, and none of them can be pre-spoken.

**Rejected: the verifier vouches for the sum.** It would have to do the same reading — dig `c1`'s
saving out of prose, convert minutes — and then agree with itself. This is where `0010`'s
false-confidence argument is at its strongest, because **arithmetic has a right answer a model can
get silently wrong**, unlike the entailment questions §6 hands it.

**Rejected: no sum; the merged Bullet carries its strongest constituent figure.** The maker's
objection, kept because it is the reason the sum exists:

> *"If we are saying 17.5 hours at the top, and then one line says seven hours and the next two say
> nothing, the 10.5 hours that are left don't get added up."*

The lead states the total; the Bullets are supposed to decompose it. And the figure is what an
interviewer asks about — *"a question is coming on this line, and you're prepared for it rather than
being clueless."*

### 6. A verifier that can only raise suspicions, never reassure

`0010` rejected an automated reviewer, and this ADR **refines that rejection rather than routing
around it**.

`0010`'s argument was narrow and specific: *"the same model, reading the same JD, carrying the same
blind spots, asked to disagree with itself"* — about **scores**. What it rejected was a second Opus
forming an **unadjudicable** judgement. §4's question is a different species: *does this text say
something that text does not say* is entailment against a fixed passage, and it has a right answer
the maker can check by reading.

So a sub-agent verifies merged Bullets, under four constraints:

- **Merged Bullets only.** That is where invention is concentrated, and it keeps the blast radius
  small.
- **Context stripped.** It receives the line and the cited Claims' Evidence. No JD, no `scores.md`, no
  run folder. The stripping is not hygiene, it is the whole answer to `0010` — it cannot carry the
  posting's blind spots into a judgement if it has never seen the posting.
- **It has no pass verdict.** One output shape: *"this line asserts X; I could not find X in the
  Evidence."* No score, no approval, no "looks fine". **A clean run prints nothing at all.**
- **Its findings are put in front of the maker.** They never silently gate.

The third constraint is the load-bearing one, because `0010`'s sharpest sentence still applies:

> *"a check that reliably says 'looks fine' actively suppresses the suspicion that would otherwise
> make the maker look."*

A verifier that passes nineteen lines in twenty trains the eye to skim, and it has caught nothing —
same model family, same priors as the composer. **Removing its ability to reassure removes the
failure mode.** Silence is its normal output rather than approval, so there is nothing to be
reassured by.

And this is the shape `0010`'s own conclusion asks for: *"the question is not what algorithm evaluates
this, but what gets put in front of the maker, and when."*

**Two questions are in its brief**, and they are the same species:

1. **Entailment.** Does the line assert anything about the cited Claims or their relationship that
   their Evidence does not carry? This covers §4's rule, and it covers **misattribution** — *does
   `c1`'s Evidence attach `~75%` to the deck cuts?* — which is what §7 hands it.
2. **Coverage.** Is **every** cited Claim represented in the line? §4's rule says each part traces to
   one of the cited Claims; it does not say each cited Claim has a part. Without this question a
   Bullet could cite `c1+c3+c4` and mention two of them — reported as placed, actually dropped, which
   is #77's *merge becomes a drop in disguise* arriving through the citation rather than the prose.
   `render.py` cannot see it and the stored sum cannot catch it, since `~8 hours` renders identically
   whether or not `c3` is named.

### 7. A second halt, in the lint band, and the correction is a proposal

**The Checkpoint runs before the Bullets are composed** (`tailor/SKILL.md`'s pipeline, and `0021` §6
put it there so the Checkpoint describes the page that renders). The verifier reads composed prose, so
it cannot run until after the Checkpoint has closed.

§5's merge-sum Fork has no such problem — merge groups come from `scores.md` and the sum comes from
the bank, both known before composing — so **that one goes in the existing Checkpoint**. Only the
verifier is stranded.

So the verifier sits **between composition and `render.py`**, where the checks already live, and it is
the one check that **asks instead of failing**. `tailor/SKILL.md`'s pipeline calls Forks *the only
halt*; it becomes *the Checkpoint and the verifier*, stated plainly rather than smuggled.

**One correction pass runs first, and it produces a proposal, not an edit.** The composer rewrites the
flagged line once. That rewrite **never reaches the page on its own authority** — satisfied verifier
or not, the halt fires and both versions are shown:

```
american-express/c1+c3+c4

  as written   Automated the monthly reporting cycle end to end — the mapping step,
               the deck cuts and the leadership summary — cutting ~8 hours a month
  proposed     Automated the Tier/Portfolio mapping, the review deck's data cuts and
               the leadership summary draft, cutting ~8 hours a month

  flagged: "one monthly reporting cycle", "end to end" — not in c1, c4 or c3's Evidence

  1. Take the proposal
  2. Keep it as written — the Evidence carries it       -> recorded in checkpoint.md
  3. It's true and missing from the bank — add it       -> write-back, keep as written
```

**Numbered options, never free text.** The maker: *"they just have to select one, two, or three,
rather than having to type 'go ahead'."*

**This is what answers the maker's one caution**, which was the sharpest objection raised in the whole
grilling:

> *"The model quietly watering down its own lines just to prevent the verifier from complaining
> should not happen. If the first pass creates good lines and a second self-correction pass gives me
> bad lines, I don't want it at all."*

A correction that ships silently could keep cutting until the verifier stops complaining — the drop in
disguise, arriving through the fix rather than the fault. **Making the correction a proposal makes
that structurally impossible: no rewritten merged line reaches the PDF without having been read beside
the original.** The self-correction pass stops being an autonomous editor and becomes the thing that
pre-fills the answer.

Two guards on the proposal itself, both already binding rather than new. It may not drop a cited claim
— §6's coverage question. It may not drop the stored merge figure — `check_number_kept` fails the run.

**"Don't merge these three" is not among the options**, and the reason is arithmetic rather than
policy. By the time the verifier runs, `c1+c3+c4` are reserved **two** lines. Un-merging needs
**three**, and there is nothing to take the third from. Un-merging is a `scores.md` decision, which
means a re-run, not an answer.

### 8. What the two number checks do

**`check_number_kept`: the group's stored sum discharges its constituents.** It arms once per cited
Claim with a stored `number:`, so a Bullet citing `c1`, `c4` and `c3` would owe **three figures in one
line** — undeliverable. `~8 hours a month` *is* `~2.5h + ~4.5h + ~55 min`; the sum is the receipt.

- A merged Bullet whose group has a stored `## merge` block **must render that figure**, and the
  members' individual numbers are kept inside it.
- A group with **no** stored sum falls back to today's rule, per claim. An unsummable merge of two
  numbered claims must therefore carry both figures or record the drop as a *Decided by rule* line.
  **That pressure is correct** — it pushes toward asking for the sum, which is the thing that is
  actually true.

**`check_number_trace` widens by one clause:** a figure traces if it traces to **any** cited Claim, or
to the group's stored sum. The tier check runs against whichever it matched.

**No cap on how many figures a merged Bullet may carry.** Considered and refused: capping at one would
nearly close the blind spot below and serve §5's decomposition directly, but it would forbid a line
like `c7`'s current *"Owned ~60 of ~150 KPIs and automated the slowest, halving a ~10-hour refresh"*
from ever being merged, and three figures are doing real work in it.

### 9. Nothing new in the Omission view — and one of `0010`'s premises fails

A merged claim is **placed**. `allocation.md`'s Placed section already lists every claim by ref, so a
merge appears as one line:

```
### american-express — job — ended 2026-07 — entry score 0.95 — 5 bullets
- american-express/c1+c3+c4 — 0.85 — 2 lines — three automations of the same reporting
  cycle; one argument, not three
```

**No new category, and the Omission view does not change** — a merged claim never enters it, the same
way `0032` ruled the lead can never be an omission. `gaps.md` is untouched: a merged claim did not
miss the page.

> **`0037` §5 adds a section beside it.** Still not an omission and still not a category — but a merge
> that carries **no figure** fired no Fork under §5 below, wrote no `## merge` block, and so appeared
> nowhere the maker reads. `allocation.md` gains a `## Merges` section next to the Omission view, and
> the Checkpoint surfaces it: summed merges keep their Fork and still halt, figureless ones are shown
> and never halt.

**But `0010`'s premise for excluding inclusions fails here**, and it is recorded rather than left
implicit:

> *"the maker is about to read the PDF, and that **is** the report on what placed… Inclusions are
> self-revealing."*

**Not for a merged claim.** Nothing in *"Automated the mapping, the deck cuts and the leadership
summary draft"* tells a reader that `c3` is in it — the ref is stripped at render. So for merges the
Placed section stops being pure duplication and becomes **the only place the decomposition is
visible.** It earns its line rather than merely having one.

## The cost, stated rather than waved past

**`0029` §4's blind spot triples on a merged line, and only a model looks at it.** `0029` already
documents that the check *"cannot see which figure stayed"*. This passes every arithmetic check on the
page:

> *Automated the review deck's data cuts and the leadership summary, cutting **~75%** of the build*

`~75%` is `c1`'s **mapping accuracy**, attached here to the deck. It traces, because `c1` is cited, so
`render.py` waves it through. §6's verifier is the only thing standing between that line and the PDF,
and §6 is a model. This is the first place in the system where a truth guarantee rests on a
judgement rather than on arithmetic, and it is named here rather than discovered later.

**`0027` §6 is now half a rule.** *One Bullet, one Claim, one citation* is gone; the downgrade-only
Claim-level trace survives, generalised to a coordination. What §6 was actually protecting — the
composer inventing connections for rhetoric — is now protected by §4's rule plus a model, where it
used to be protected by a structural impossibility. That is a genuine weakening, and it was accepted
on the maker's *"irrespective of whatever the cost is"*.

**A second halt is a real cost to a run.** `0002` made the Checkpoint conditional precisely so an
aligned run renders straight through. A run with two merged Bullets can now stop twice: once at the
Checkpoint for the sums, once in the lint band for the verifier. The first is bounded — a merge group
is asked about once, ever — but the second fires per run per flagged line.

**Merged lines will be duller.** §4's cost, restated because it is the one the maker will actually
feel on the page.

**A stored merge sum can go stale and nothing catches it.** `## merge c1+c3+c4` records ~8 hours
against three Claims as they read when it was spoken. If `c4`'s figure is later amended through the
Return door, the sum is wrong and no check compares them. Not grilled, not solved; on the map as fog.

**`0010` is refined for trace and untouched for worth.** §6 answers *is this line entailed by that
Evidence*, which is adjudicable. #77 still owns `0010` for *is this line earning its place*, which is
not, and nothing here settles that in advance.

## Rejected

**The merge lives in the bank as a rollup Claim.** §1 — the full argument and the maker's reason are
there. It is the option that would have cost nothing, and it loses because it would win the entry's
top slot on every posting.

**The merge is discovered while composing, and lines are handed back to a third Packer pass.** Closest
to how the work feels — you do not really know three claims fuse until you try the sentence. It loses
on `0025` §1's blanket refusal of a third pass (*"every post-composition re-costing puts the
Checkpoint in front of a page that then changes"*) and on `0006`, since it makes the Packer read
composed prose.

**The Packer never learns about the merge**, composing three lines into six slots and wasting the
residue. Cheapest by far, and it throws away the room recovery that is the entire point (§3).

**A merge collapsed into one row of the claims table.** The minimal parse change, and it would have
let merging move the entry score through `0024`'s ranking window (§2).

**A verifier that hard-fails the run.** Refused because a nondeterministic gate means the same JD
against the same bank can render on Monday and fail on Tuesday — the one property `render.py`'s checks
have that makes them trustworthy. A Checkpoint-style halt keeps the page deterministic: a model that
can only add a question cannot change what renders.

**No self-correction pass — bare findings and a re-run.** It fully satisfies the maker's caution by
construction, since nothing is ever rewritten. It loses because it costs a whole run per finding and
buys nothing the proposal shape does not (§7).

## Consequences

- **`0027` §6 loses *one Bullet, one Claim, one citation*** and keeps the downgrade-only Claim-level
  trace, generalised by §4 to a coordination across cited Claims.
- **`scores.md` gains a `## Merges` table**; the claims table is unchanged. `pack.py` parses and
  validates it, still reading exactly one file.
- **`pack.py`'s reservation gains a second non-unit object.** A merge group reserves `width` lines
  before `grant_widths` runs, ordered by the max of its members' scores. `0032` §6 already made the
  lead the first.
- **`bullets.md` line refs may carry a `+`-joined claim list**; `render.py`'s ref parsing and
  `resolve_claim` follow.
- **`0004`'s Entry schema gains an optional `## merge <ids>` block** with `number:` and `provenance:`,
  beside `0032`'s `## lead`. `bankcheck.py` parses and validates it; a merge block whose ids are not
  all Claims in that entry is a schema error.
- **`0008`'s write-back gains a third destination shape** — a merge sum is neither *framing*, *add*
  nor *revise*, it is a non-competing entry-level fact. It reaches the bank the same way an **add**
  does and, like `0032`'s lead, it is not marked `needs-interview`.
- **`tailor/SKILL.md`'s pipeline no longer calls Forks the only halt.** The verifier is the second,
  in the lint band, after composition. `0002`'s Checkpoint itself is unchanged — it keeps the merge-sum
  Fork, which is knowable before composing.
- **`0010` is refined, on the record.** §6 states the conditions under which a model may check
  another model's output in this system: adjudicable question, context stripped, no pass verdict,
  findings put in front of the maker.
- **`render.py` gains the widened trace, the sum-discharges-constituents rule, and the verifier
  hand-off.**
- **`tailor/SKILL.md` §5 gains §4's coordination rule** and the merge declaration in §2's scoring
  step.
- **`0030` is untouched.** Its checks read *Bullets*, and a merged Bullet is a Bullet. Most merges are
  `width: 2` and so already outside §2's spread rule.
- **`0024`, `0026` and the Omission view are untouched** (§2, §9).
- **No re-calibration is owed.** No constant moves and the template is not edited.
- **#77 inherits a sharper question and one closed door.** *What stops merging from filling six slots
  with six merges* is still entirely its own, and §3's free 2-into-2 merge gives it one more case to
  handle. §6's coverage question closes *what stops the merge from becoming a drop in disguise* — for
  the citation half of it.
- **The verifier is new machinery, not a rule change**, and #78 carries it: a sub-agent, a stripped
  context, a halt point, and an option set.

## Addendum, 2026-08-13 — §4's ban on synthesis is lifted

`docs/adr/0053-the-bank-is-the-source-of-facts-not-of-words.md` §2 reverses §4 above
for the Bullet. *The merge does the compression, the entry's lead does the synthesis*
no longer holds: a merged Bullet may assert what its cited claims have in common and
lead on it.

The reason is empirical rather than theoretical. Under §4 a three-claim merge could
only be written as three clauses, because every word had to trace — and `runs/auxo-ai`
duly produced *"Took the pipeline unasked to other teams, ~95% of manuals came out
usable; pinned translated tables to their source box as images; shipped it as a
Streamlit app the manual writers ran themselves"*. True, traceable, verifier-clean, and
not a sentence. The rule that kept the page honest was the rule that made it unreadable.

**§8's arithmetic is untouched** — the stored `## merge` sum still discharges the
group's figures, and a group with no sum still composes qualitatively. **§7's verifier
survives, re-scoped**: it now asks whether the line states a *fact* the Evidence does
not carry, and is told explicitly that framing is not a fault. Left as written it would
have flagged every well-written merged line on the page.
