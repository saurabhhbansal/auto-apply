# A beat earns its own line by landing alone, and the cap counts units

**Status:** accepted

## Context

This is the ticket the map was chartered around. The maker read `runs/auxo-ai` back and objected to
the Amex column — six Bullets, six separate automations of pieces of the same monthly reporting
cycle, each carrying its own saving, with the addition left to a reader who will not do it. The map
named the mechanism in one sentence:

> **It fills to six** because nothing ever asks whether the sixth atom is worth a line *given the
> five above it*.

The line that does it is `tools/pack.py:229`:

```python
return min(MAX_BULLETS, len(self.qualifying_claims))
```

An entry's size is a **count of claims**, clipped by a **constant**, and then clamped again by
whatever the distribution pass has left over. All three are quantities the entry itself has no say
in. An entry that is naturally a four-line entry has no way to be one.

### Four tickets answered most of the brief before this one was taken

The same thing happened here that happened on #75
and #76, and it is worth being explicit
about how little was left:

- **`0032`** took both ends of the arc out of the column. The situation and the aggregate ride in an
  unbulleted lead line, so the story exists and the ~17.5 hours surfaces without any Bullet
  asserting it.
- **`0034`** made merging real: declared at scoring time in a `## Merges` table, **reserved** rather
  than wanted, self-financing at `W ≤ N`, at most three claims, and a coordination rather than a
  synthesis. Its §6 verifier — adjudicable, context-stripped, no pass verdict — closes the
  **citation** half of this ticket's drop-in-disguise question.
- **`0035`** put the lead inside the reserved minimum and named leapfrogging inside an entry: *an
  entry takes its **units** best-first and skips one that does not fit the lines it has left.*
- **`0036`** settled how the aggregate is collected at ingest.

So the machinery for *"these are the same argument twice"* already existed. What was left is what
**worth** actually is, whether `0010` moves, and what the cap counts.

### The brief as the maker sharpened it

> *"We consider an entry a whole thing. If we know that something can be fitted in four lines — four
> bullets, a lead and a header — then we do it in that. **We don't have to always go for filling out
> maximum available space.**"*

And, grilling this ticket, the rule underneath it:

> *"Everything can be given its own space on the resume if you see it independently. When you see it
> collectively as three things merged together, if that is creating the same impact as something
> would have as an individual line, it is better off as a combined set statement than an atomic
> link… The interviewer knows, 'okay, these were three things he worked on, and together they
> created an impact of this much,' rather than 'he did this, he did this, he did this.'"*

## Decision

### 1. Merging is the whole of worth. There is no second mechanism

Charting fixed two halves of this: the middle beats are governed by **worth, not by a budget**, and
worth is served by **merging, not dropping**. This ADR adds the closing half — **there is nothing
else.** A beat that says something the placed beats do not **always** earns its line.

The reason is the maker's own founding rule for the map:

> *"I would want to include everything that I did there, not just three things out of five"* — a
> dropped item is one an interviewer may ask about.

A marginal-worth **stop** — *this is a genuinely different thing, it just isn't worth a line given
the four above it* — has no domain left to live in. If the fifth thing really is a different thing,
dropping it breaks that rule. If it is not a different thing, merging already handles it and nothing
falls off the page.

**`0026` §4's parked gate is closed rather than re-parked.** That section refused a score gate on the
fourth Bullet onward and left the door open on the record:

> *There is a coherent sentence behind the gate, recorded because it may come back: **presence is
> owed to anything above the floor; depth has to be earned above a higher bar.** … If a six-Bullet
> entry reads badly once the maker has seen one, this is a one-line change against a page he can look
> at, which is more than this ADR had.*

That trigger has now fired — the maker has seen a six-Bullet entry and complained about it, and this
map exists because of it. The gate is declined anyway, on grounds `0026` did not have. A depth gate
orders by **score**, and score is fit-to-JD. On `runs/auxo-ai` the claims that merge are `c1` (0.85),
`c4` (0.85) and `c3` (0.60), while `c7` (0.70) stands alone. A gate at 0.70 keeps `c1` and `c4` apart
as separate Bullets and cuts `c3` off the page entirely — it separates the three that belong together
and drops one of them. Exactly backwards, on the entry the rule was written for.

**This is also why the map's fourth worry dissolves rather than gets a rule.** *What stops merging
from filling six slots with six merges* was a fear about a budget-shaped rule, and it does not
survive a worth-shaped one: if an entry holds twelve claims and none of them lands alone, six merges
is the correct page for it. The brake is the trigger in §2, the report in §5, and the maker's eye —
not a count.

### 2. The trigger is *does not land alone*, never similarity

The obvious rule was that similar things group together, and it is wrong. The counter-example is on
the entry that started the map:

| | how alike | scores | merge? |
|---|---|---|---|
| `c5` + `c6` | both custom GPTs — **the most similar pair in the entry** | 1.00, 1.00 | **no** |
| `c1` + `c3` + `c4` | a fuzzy-matching pipeline, an email drafter, a deck's data cuts | 0.85, 0.60, 0.85 | **yes** |

`c5` and `c6` are the two claims the entry wins this posting on — AuxoAI's first responsibility is
AI-driven business copilots, and those are the two copilots. Fusing them turns the strongest thing on
the page into half a list item. `c1`, `c3` and `c4` are three quite different pieces of work, and
what actually holds them together is that **none of them is more than a few hours saved on one step
of the reporting cycle.**

> **A claim earns its own line when standing alone makes it land harder than it would inside a merge.
> The default is together; separateness is what has to be earned.**

The burden inverts, and the maker's sentence is why: *"everything can be given its own space on the
resume if you see it independently."* Independence is not a reason for anything, because it is always
available. Something has to be bought by the separation — impact, importance, standing out.

**Two things a merge buys, both named by the maker.** The reader gets one account rather than a list
of small impacts. And the figures add up to a number worth reading:

> *"What if each of them just saves one hour, and combined we are saving three hours? We would want a
> bigger number over there."*

**Similarity keeps a job, a smaller one.** It is what makes a merged line *readable* — three things
sharing a verb, under `0034` §4's coordination rule. It decides **how** to write a merge, never
**whether** to make one.

**Score cannot stand in for this**, and the table says so plainly: 0.85, 0.60 and 0.85 merge while
0.70 does not. Fit-to-JD and lands-on-its-own are different measurements, and nothing in `scores.md`
carries the second. The judgement has to be made fresh, which is what makes §3 the expensive section.

**`0034`'s worked reason is superseded.** Its example row reads *"three automations of the same
reporting cycle — one argument, not three"* — a similarity reason, written before this rule existed.
The `reason` column survives; what goes in it changes:

```markdown
| american-express | c1+c3+c4 | 2 | none of the three lands alone — each is a few hours saved on one step of the cycle |
```

### 3. `0010` does not move on the judgement, and `width` is why

The ticket demanded this be settled out loud — *"routing around it silently is the failure mode to
avoid"* — because `0030` had surfaced the conflict and honestly declined to resolve it, its checks
being unable to form an opinion:

> **Prose quality gets no mechanism in v1.** An automated reviewer was rejected because *"it is the
> same model, reading the same JD, carrying the same blind spots"*, handing back false confidence.

**Nothing grades a merge.** No second pass reads `## Merges` and disagrees with it — that is
precisely the reviewer `0010` refused, and it would hand back exactly the false confidence `0010`
warned about, on a judgement even less adjudicable than a Fit score.

The precedent that makes this comfortable is **`width`**. `0027` §5 already lets the model declare
*"compressing this to one line would cost the thing worth saying"* — a pure judgement, unmeasurable,
about how much room a claim's substance deserves, declared at scoring time in `scores.md` before any
allocation is known, adjudicated by nothing. Nobody read that as reopening `0010`. Deciding that
three claims share a sentence is the same species of call at group scale, in the same file, under the
same discipline.

> **`0010` fenced off *evaluating* output. It never fenced off *authoring* it.**

The whole system is the model making judgements — every Fit score, every reason on it, every composed
sentence, every `width`. What `0010` refused was the model **checking its own judgements and handing
back a verdict**, because a check that reliably says *"looks fine"* actively suppresses the suspicion
that would otherwise make the maker look. A merge declaration produces no verdict about anything
already decided. It is a first-pass call, made before a word is composed.

So `0010`'s core stands untouched: the automated reviewer stays rejected, prose quality still gets no
mechanism, and the Omission view's structural cut still refuses to consult the number under
suspicion.

### 4. `0010` is refined in exactly one clause: an inclusion that merges is not self-revealing

`0010` keeps what *placed* out of the Checkpoint, deliberately:

> **Only omissions.** What placed is deliberately excluded: the maker is about to read the PDF, and
> that *is* the report on what placed… **Inclusions are self-revealing; omissions are not**, and the
> view exists for what the page cannot show.

That premise fails here, and `0034` already recorded it failing. The demonstration is one line:

> *Automated the Tier/Portfolio mapping, the review deck's data cuts and the leadership summary
> draft, cutting ~8 hours a month*

It reads well. So would the line that fused `c5` and `c6`. **Nothing on the page distinguishes them**
— you would have to already know which claims were separately strong to see that the second one had
buried the entry's whole case.

So merging manufactures a third kind of fault, and `0010`'s two-row table has no place for it:

| | how it fails | visible? |
|---|---|---|
| selection | the wrong evidence won the page | no — the Omission view |
| prose | the right evidence, weakly written | yes — it is on the page |
| **grouping** | **the right evidence, wrongly fused** | **no — and the page reports it as placed** |

The refinement is exactly one clause wide. The Checkpoint shows omissions, **plus the one class of
inclusion that is not self-revealing.** Nothing else in `0010` moves, and §5 is the shape of it.

### 5. Every merge is shown at the Checkpoint, and the reason is the reviewable part

**Where.** Its own short section in `allocation.md`, **beside** the Omission view rather than inside
it — nothing was omitted, so it is not an omission. And not in Silent calls, which are *"every call
the **Packer** made by rule rather than by score"*; a merge is Opus's call.

The division of labour is `0010`'s own, unchanged: the Packer prints it and **carries Opus's reason
across verbatim, never writing a reason of its own.**

```markdown
## Merges

Every Bullet on this page that fuses more than one Claim, with what made them one
line. Shown, not asked — a disagreement is a bank edit and a re-run, never an override.

- american-express/c1+c3+c4 — 2 lines — none of the three lands alone: each is a few
  hours saved on one step of the monthly cycle — ~8 hours a month [vouched]
```

**The reason is what gets reviewed, not the group.** `0010`'s argument for putting reasons in the
Omission view transfers verbatim: `0.42` cannot be judged by eye, because there is no calibration for
whether 0.42 was right, but `0.42 — "Kafka here was ops-only; the JD wants stream-processing design"`
can be judged in about a second, *because it turns the question into a claim about the maker's own
history, which they are the world expert on.* `merged c1+c3+c4` cannot be judged. *"None of the three
lands alone — each is a few hours on one step"* can.

**Every merge appears, including the ones already vouched.** `0026` §5's rule for `Share:` and `0025`
§7's for `Room:`, applied again: always printed, because a signal is only readable if its absence
never has to be interpreted.

**What halts and what does not.** A merge carrying a **summed figure** keeps `0034` §5's Fork and
still blocks — the sum is a fact entering the bank, and `0015` requires the maker to speak it. A merge
with **no figure** is shown and never blocks. `0002` and `0010` both refuse a gate that is approved
every time, because it decays into a rubber stamp while still looking like a safeguard, and being late
costs one re-run.

**The hole this closes.** Under `0034` alone, a figureless merge fired no Fork, wrote no `## merge`
block, and appeared nowhere the maker reads. So the merges *least* checkable by arithmetic — two
qualitative claims fused because the model judged neither landed — were exactly the ones nobody ever
saw.

**Falling out mechanically:** the Placed section lists **units**, so `american-express` reads
`5 bullets` with `c1+c3+c4` as one row at two lines.

### 6. The cap counts units

`Entry.slots` becomes `min(MAX_BULLETS, units)`. Against `runs/auxo-ai`, where Amex has seven
qualifying claims and one merge group:

| what the cap counts | Amex on AuxoAI |
|---|---|
| **claims** (today) | 7 wanted, capped to 6, `c2` dropped *"beyond the 6-bullet cap"* |
| **units** | 5 units across 7 lines — all place, **`c2` returns to the page** |
| lines | 7 lines, capped to 6 — something drops again |
| nothing — delete the cap | 5 units, all place |

**Lines is refused**: it reinstates the drop through a different door, and on this bank it would cut
`c2` all over again immediately after merging bought it back — `0034` §3's *"the freed line is what
puts `c2` on the page"*, undone by arithmetic one ADR later.

**Deleting the cap is refused**, though it is the purest reading of this ticket's title and was nearly
taken. It removes a rail on a bank of four entries where the rail has bitten exactly once. That is a
decision made **blind**, which is the fault `0026` was burned by — every candidate rule it considered
produced the identical page, and it had nothing to look at.

> **Six stops being the target and becomes a backstop**, and what makes that safe is the substance of
> this ADR rather than the number: the entry no longer fills to the cap because something finally asks
> whether the beat is worth a line. The number was never the fault.

**`Entry.score` does not move.** Its window is the top three qualifying **claims** (`0024` §2).
Merging does not change what a claim is worth to the posting, and the one question the Entry score
answers — *when the page runs out of lines, who gets shrunk first* — is unchanged.

**The Omission view's cap reason** rewords to *beyond the 6-unit cap on an entry*. On `runs/auxo-ai`
it stops firing at all: `american-express/c2` places.

### 7. An entry that fills to the cap with no merge is reported, never failed

The ticket pointed this challenge at itself, and it is the right one:

> Whether anything checks it at all, or whether — like `0027` before `0030` — this lands as a
> paragraph in `SKILL.md` with nothing measuring it. `0030` is on the record that two composed pages
> under such a paragraph moved the number the wrong way.

That record is specific and damning: `0027` wrote *"write to say the thing, then check the budget"*,
nothing measured it, and the fill rate went **from 95.9% to 96.5%** across two composed pages. §1–§6
are a rubric paragraph plus a report. The likely failure is that the model declares no merges,
entries keep filling to the cap, and nothing notices.

There is exactly one arithmetic thing available, and `0030`'s method is to take it. **An entry that
places at `MAX_BULLETS` units with no row in `## Merges` gets a line in the merges section.** It is a
count over `scores.md`: no opinion, no reading of the JD, and it cannot say *"looks fine"* — it fires
or it does not. `0030` §2's species exactly.

`american-express` on `runs/auxo-ai` is that shape today — six units, zero merges — so the rule fires
on the page that prompted the map.

**It reports and never fails.** `0030` §2 made the spread a hard failure in `render.py`, and the
asymmetry runs the other way here. A rewritten-shorter sentence is a cheap, local answer to the spread
rule; the only way past a *merge* failure is to produce a merge, and a coerced merge is precisely the
bad merge §3 has no check for. A report puts the maker's eye on the entry; a failure buys a fused
sentence nobody wanted.

**Where it is weak, said now rather than discovered later.** It only fires **at the cap**. An entry
that should have merged two of its four claims never trips it, because four units is not a suspicious
number. This catches the shape of the complaint that opened the map and nothing subtler. That is more
than `0027`'s paragraph had and far less than a check, and `0030` §2's rule applies unchanged: if the
page comes back worse, the answer is **the rubric restated harder, not a looser threshold.**

### 8. Only merging entries get a row

`0035` §2 set the opposite discipline one ticket ago, and it was considered here:

> **Every entry gets a row**, so a forgotten lead and an absent one are different bytes.

**Refused.** That argument was specific to a **bank fact**: the model must never be able to silently
withhold a lead, because *"a per-run this JD doesn't need it is `0032` §6's refused trade wearing a
relevance costume."* A merge has no bank fact behind it — it is a per-run composition judgement — so
there is nothing to withhold, and the argument does not carry over.

And the grain refuses it independently. `0034` made a `## Merges` row a **group**, not an entry.
Per-entry `n` rows put two grains in one table, which is what `0035` itself refused when it declined
to let the lead ride as a repeated column: *grain decides the shape.*

The practical version is the **"so what?" test** (`0003`), applied to the system's own reporting the
way `0010` applied it to the coverage ratio. §7 already fires on the case where silence is suspicious,
and it fires whether the silence was considered or careless. A run of `n` rows buys the difference
between *thought about it and declined* and *never looked* — which reads as rigour and changes nothing
anyone would do, since either way the same entry is in front of the maker for the same reason.

## The cost, stated rather than waved past

**The most consequential judgement on the page has no check, and §3 declines to give it one on
principle.** A wrong merge buries the strongest claim in a list, reads perfectly well, traces
perfectly cleanly, and is reported as placed. The only thing between it and the PDF is the maker
reading one line of reason at the Checkpoint. `0034` already recorded that `0029` §4's blind spot
**triples** under merging and that only a model looks at it; this ADR widens the same blind spot again
by making merging the *default* rather than an option, and then refuses to narrow it. That is the
deliberate trade, and it is the largest one this map has made.

**Six stops being an arithmetic guarantee.** Six merged units at two lines each is twelve lines — half
the Bullet budget — for one entry. It is unreachable on this bank (it needs twelve-plus qualifying
claims in one entry, none of them landing alone) and §5's report is what would surface it if it
arrived. But the cap now counts **arguments**, not page cost, and someone reading `MAX_BULLETS = 6`
beside a twelve-line entry will need §6 to explain it.

**The Checkpoint gets longer, and `0010` cut it tight on purpose.** Its own words: *"the cost is
length, and it is accepted… it would train the eye to skim the block — taking the omissions with
it."* This is the first thing ever added to that view. On this bank it is a line or two; the argument
against it was made deliberately, and it is being overridden rather than answered.

**Merged lines are flatter, and there will now be more of them.** `0034` §4 already priced the
coordination rule — *"a coordination reads flatter than a synthesis… merged lines will be duller than
the ones a free hand would write."* Making merging the default multiplies that cost across the column,
and it pushes directly against `0027` §2's *six in a column must not read like a form*: a list-shaped
line beside another list-shaped line is the form-shaped page that rule exists to prevent. The lead
carries the synthesis, which is what makes it affordable at all, but the interaction is real and the
re-render under #78 is where it becomes
visible.

**Nothing here fires unless the model declares merges at all.** §7 catches only the cap case. The
honest comparison is the one the ticket drew: `0027` wrote a paragraph and two composed pages measured
worse. This ADR writes a paragraph plus one count.

## Rejected

**A marginal-worth stop — a beat that says something new but is dropped anyway.** §1. It contradicts
the map's founding given and has no non-empty domain once merging exists.

**`0026` §4's score gate on the fourth Bullet, un-parked.** §1. Its trigger condition has fired and it
is declined on the numbers: at 0.70 it separates `c1` and `c4` and drops `c3`, which is the merge group
taken apart backwards.

**Similarity as the trigger.** §2. It merges the two 1.00s and buries the entry's whole case for this
posting.

**Borrowing `scores.md`'s Fit score as a proxy for standalone impact.** §2. The merging claims score
0.85/0.60/0.85 and the standalone one scores 0.70; the two measurements are not the same measurement.

**A cap on merges per entry.** The budget-shaped rule this map exists to replace, one level in, with a
number nobody chose — the exact fault the destination names.

**A cap on lines, and deleting `MAX_BULLETS` entirely.** §6.

**Failing the run on a cap-filled entry with no merge declared.** §7. The only way past it is a merge
made to get past it.

**A per-entry merge verdict, `y`/`n`, following `0035` §2.** §8.

**A second model reading `## Merges` and disagreeing.** §3. This is `0010`'s rejected reviewer with a
narrower input, and the judgement it would be second-guessing is *less* adjudicable than a Fit score,
not more. `0034` §6's four conditions — adjudicable question, stripped context, no pass verdict,
findings put in front of the maker — are what license a model checking a model here, and *is this
worth its own line* fails the first of them outright.

## Consequences

- **`tools/pack.py`**: `Entry.slots` becomes `min(MAX_BULLETS, units)`; `omission_view`'s cap reason
  rewords to *unit*; the Placed section lists units with merged groups as one row; a `## Merges`
  section joins the Omission view, printing Opus's reason verbatim plus §7's cap-filled-no-merge line.
  Carried by #78.
- **`.claude/skills/tailor/SKILL.md`**: the composition rubric gains §2's test as the rule governing
  the `## Merges` table, replacing `0034`'s similarity-worded example; the Checkpoint section gains the
  merges view and what halts on it.
- **`docs/adr/0010`** is refined in one clause — §4 — and nowhere else. Its automated-reviewer
  rejection, its prose abstention and its structural cut all stand.
- **`docs/adr/0024`** §1's `min(6, qualifying)` is narrowed to units; its `MAX_BULLETS` comment and
  `Entry.slots` docstring follow. §2's ranking window is untouched and stays claims.
- **`docs/adr/0026`** §4's parked depth gate is **closed**, not re-parked.
- **`docs/adr/0034`**'s worked `reason` example is superseded by §2, and the figureless-merge
  reporting hole its §5 left open is closed by §5 here.
- **`CONTEXT.md`**: **Slot**, **Elastic block** and **Omission view** follow the cap to units, and
  **Unit** — already in use in `0035` §4 — becomes a term. #78.
- **`runs/auxo-ai` re-renders with `american-express/c2` on the page**, which is the claim the map's
  opening arithmetic listed at ~4.5 hours and the Omission view cut for the cap.
- **Graduated out of the fog as its own ticket:** merging for a bigger number makes nested sums
  routine rather than incidental — Amex will regularly carry `~8 hours` on a Bullet inside `~17.5
  hours` in its lead, the second wholly containing the first, with nothing saying so.
