# A number leaves the Bullet only when the maker has said so

**Status:** accepted

## Context

`runs/auxo-ai` is the first run composed under `0024`, `0025` and `0027`, and by every standard
those ADRs set it is a good page: 17 Bullets across five entries, every prose fault `0028` traced
gone, `xlscout/c1` carrying *unasked*. Read back as a **page** rather than as a column of lines, it
argues nothing with a number (#54, #55).

### The page makes no quantified argument

Every figure that reached the page:

```
american-express/c7    ~60 of ~150 KPIs      scope
auto-apply/c7          ~2,100 lines of prose scope
xlscout/c1             about ten people      scope
xlscout/c3             four models           scope
```

Percentages: none. Time saved: none. Money: none. A reader gets *built X* seventeen times and never
once *which did Y, by this much*.

### One Claim had the figure and the Bullet dropped it

`bank/jobs/american-express.md`:

```
## c4
number: ~4--5 hours per cycle
provenance: estimated

**Assertion:** Automated the monthly business-review deck data cuts off scorecard data and internal data platform tables,
replacing about 4--5 hours of hand-built Excel pivoting per cycle.

**Evidence:** … what the automation bought was the hours and the repeatability.
```

What shipped, at **100 of 103 characters**:

> Replaced a stack of hand-built Excel pivots with data cuts generated from the scorecard and BigQuery

The Evidence says in as many words that the hours were the thing the work bought. The line spent its
budget on *"a stack of"* and on naming two data sources, and dropped them.

This is not a marginal call. `0027` used **this exact Claim** as its uncontested control, and every
candidate it ran — CONTROL, WIDE, SITUATION-FIRST — kept the figure:

| | |
|---|---|
| WIDE (157) | *Replaced ~4-5 hours of hand-built Excel pivoting each cycle by automating the monthly business review deck's data cuts off scorecard data and BigQuery tables* |
| SITUATION-FIRST (102) | *Each cycle took ~4-5 hours of hand-built Excel pivoting; automated the review deck's data cuts instead* |

The SITUATION-FIRST line fits in 102 characters **with** the number. This was not a budget problem.

### Where it enters

`.claude/skills/tailor/SKILL.md`, in the composition rubric's *Numbers move one way only* paragraph:

> Dropping the number entirely is always allowed and is often the right call when the line is tight
> and the posting does not care about that metric.

Two escape hatches in one sentence, and both fired wrongly here. The line was not tight — three
characters spare — and the posting asks for *"data pre-processing"* and *"analyze data to provide
insights"*, so it does care.

Note what the rubric protects and what it does not. Two paragraphs later it is emphatic that a
rephrase which drops a **fact** is a different Bullet:

> **a rephrase that has to drop a fact is a different Bullet, and needs the Claim re-read, not the
> sentence trimmed.**

A stored `number:` is a fact — the most defensible one the Claim owns, the only one with a
`provenance:` tier behind it and a lint guarding its truth. It was the one fact the rubric let go
for free.

## Decision

### 1. The number is head, not tail

The rubric's *"cut the tail, never the head"* rule already names what survives an overrun — *"The
change and its number stay"* — but it says so illustratively, inside a table of four worked
overruns. It becomes binding, and the ordering is stated outright: **the number is the last thing a
Bullet gives up, not the first.**

A line that will not fit with its figure in it loses something else. If nothing else will go, the
Claim is re-read rather than the sentence trimmed, which is the standard `0027` already set for every
other fact in the line.

### 2. The escape narrows to two cases

A Claim's `number:` may be absent from its Bullet only when:

- **the Checkpoint answered *soften*** for that Claim — which `checkpoint.md` already records and
  `SKILL.md` already routes (*"the Bullet drops the figure or states the claim qualitatively"*); or
- **the Claim's own Evidence undercuts the figure in this JD's angle** — the `sweatpact/c4` shape,
  where the Evidence says the prediction layer was opportunistic and that composing it would spend
  the claim's truth upward to chase the posting.

*"The line is tight"* and *"the posting does not care about that metric"* are **deleted as grounds.**
The first is answered by §1: tightness decides which *other* words go. The second is `0027` §4's
deleted move 3 growing back — **the JD decides which claims get a line, it does not decide what goes
in the sentence** — and it is named as such here, because it is the same error the previous rubric
was rewritten to remove. It re-entered through a paragraph about numbers rather than a paragraph
about relevance, which is exactly why it survived that rewrite.

The second ground is written from a **shape** rather than from a number the bank currently holds:
`sweatpact/c4` carries no `number:` at all, and its Evidence-over-score-reason call is recorded in
`runs/auxo-ai`'s own *Decided by rule* section. Stated so nobody later reads it as a worked case.

### 3. A dropped number is a *Decided by rule* line, not a Fork

`0002` made the Checkpoint conditional deliberately, and a halt per dropped figure would undo that —
this is a compose-time judgement about one sentence, not a load-bearing unadjudicable choice.

`checkpoint.md` already carries a **Decided by rule** section holding exactly this kind of call. The
`auxo-ai` run has one:

> - **`sweatpact/c4` composed on its Assertion, not its score reason.** …

So dropping a figure writes one line there, naming the Claim and which of §2's two grounds it stood
on. Existing file, existing section, no new artifact, no halt.

**A *soften* answer still owes its line.** The Checkpoint records the soften elsewhere in the same
file, and having one section be the check's whole input beats teaching it two. One extra sentence, on
a rare path.

### 4. `render.py` fails a silent drop

The half with teeth, and it needs no judgement — it is a `number:` field on one side and a regex on
the other. **A Bullet whose Claim carries a figure in `number:` and whose text carries none fails the
run and names the Claim**, unless `checkpoint.md`'s *Decided by rule* section names that Claim's ref.

This is deliberately the mirror of the check already sitting next to it. `check_number_trace` fails a
figure that traces to nothing; `check_number_kept` fails a figure that traced to something and then
vanished. Same file, same failure style, same message shape: name the Claim, say what to do.

Three narrowings, each of which follows from the check being arithmetic:

- **It reuses `numbers()`.** A drop check that disagreed with the trace check about what counts as a
  number is the bug this ADR is about.
- **A `number:` with no figure in it does not arm the check.** The field is human-readable text and
  need not be a figure at all (*"half the fleet"*); where it is not, there is nothing for a Bullet to
  keep. Same blind spot `check_number_trace` already carries and documents.
- **A missing `checkpoint.md` reads as "nothing recorded".** The file is written on every run, but a
  check that crashed on its absence would fail runs for the wrong reason and name the wrong file.

> **The `0010` conflict, surfaced rather than routed around.** `0010` ruled that *"prose quality gets
> no mechanism in v1"*, on the grounds that a weak line is visible on the page and a mis-selection is
> not. **This does not reopen it.** A missing figure is not a judgement about prose; it is a field
> present in one file and absent in another. What `0010` rejected was a second Opus reading the JD.
> It did not rule out arithmetic.

## The cost, stated rather than waved past

**The check cannot see *which* figure stayed, and `runs/auxo-ai` already contains the case.** Run
against that page, §4 names four Bullets — `american-express/c1` (`~75%`), `/c4`
(`~4--5 hours per cycle`), `/c3` (`50--60 min per month`) and `xlscout/c1` (`~95%`), so the fault is
three times larger than the one Claim this ADR opens on. The fifth, `american-express/c7`, **passes**:
its stored `number: ~50%` is gone and the line carries `~60 of a new diagnostics scorecard's ~150
KPIs` instead, which is scope, and nothing mechanical tells one figure from the other. So the exact
substitution the page-level complaint is about — an outcome number traded for a scope number — is the
one thing the check cannot see. That is governed by §1 and §2, which are prose; §4 catches the cruder
version, the figure that went missing entirely. Recorded rather than papered over: §4 is a backstop
under a rule, not the rule.

**The escape now costs a sentence.** Every legitimate drop writes a line in `checkpoint.md` or the
run fails, including the *soften* path where the maker has already said their piece elsewhere in the
same file. That is the price of the check having one input instead of two, and it is paid on the rare
path rather than the common one.

**`~4--5 hours` still cannot render as a range.** The **Number-trace check** softens per figure, so
`~4-5 hours` renders the `5` flat and fails on an `estimated` Claim. Keeping this Claim's number
means composing the endpoint the maker is willing to defend — `~5 hours` — until #54's open question
about ranges is settled. So this ADR makes a figure compulsory that the pipeline can still only
render in one of its two shapes.

## Rejected

**A Fork per dropped figure.** The obvious way to make the maker the one who decides, and it undoes
`0002`: the Checkpoint halts only on what is load-bearing and unadjudicable, and *"this sentence came
out without its number"* is neither. A run that halted per figure would be answered reflexively,
which is the rubber-stamp the Checkpoint refused to be.

**Keeping *"the posting does not care about that metric"*, loosened.** There is no phrasing of it that
is not `0027` §4 undone. The Fit rubric already spent the posting when it decided the Claim gets a
line at all; consulting it again about the inside of the sentence leaves the part that overlaps the
posting, which is the part the posting already knew.

**Keeping *"the line is tight"* as a ground.** Answered by §1, and false in the case that produced
this ADR: the shipped line had three characters spare and `0027`'s own candidate fit the number in
102.

**A second figure detector for the drop check.** Rejected on sight — see §4.

**Firing on a `number:` field that is present but empty.** `bankcheck.py` is where an empty field is
refused, and only if it turns out to exist in the real bank. A render-time check for it would put the
bank's schema rules in the renderer.

**Discounting the check for a Claim already at 103 characters with its number in.** That is
`check_lengths`' problem and it already fails loudly. §1 says the number stays and something else in
the sentence goes.

## Consequences

- **`SKILL.md`'s *Numbers move one way only* paragraph is rewritten** to carry §1 and §2, and the
  Checkpoint section that documents *Decided by rule* gains §3's duty.
- **`render.py` gains `check_number_kept`** beside `check_number_trace`, and learns to read
  `checkpoint.md`'s *Decided by rule* refs — reusing the cited-ref pattern `parse_bullets` already
  has, so the ref grammar has one definition.
- **One existing test changes meaning.** `tests/test_render.py` carried *"No number at all is always
  a legal downgrade"* as a passing case. It is now a failure unless the drop is recorded — the
  decision, visible in a diff.
- **`CONTEXT.md`'s **Downgrade-only (no silent upgrade)** entry stops saying render may drop a number
  freely**, and **Provenance** cross-references it.
- **The bar on the re-render:** `american-express/c4` carries its figure. If it does not, §2 did not
  narrow far enough, and that is a finding for #55 rather than a Bullet to tune by hand.
- **The re-compose is four Bullets, not one.** The read that produced this ADR found `c4` by eye;
  pointed at the page, the check names `american-express/c1`, `/c3`, `/c4` and `xlscout/c1`. Reading
  seventeen lines for a fact that is *absent* is exactly what a person is bad at and a regex is good
  at, which is the strongest argument §4 has.
- **`0010` stands.** Nothing here evaluates prose; the one thing added is a comparison between a
  field and a regex.
