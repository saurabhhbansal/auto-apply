# A Bullet reaches for the fact that sizes the work

**Status:** accepted

## Context

A survey of nine open-source JD-driven résumé tools was read against this repo, and the
uncomfortable finding was that `tonykipkemboi/resume-optimization-crew`'s committed output —
which ships lines like *"Successfully implemented process improvements that resulted in measurable
efficiency gains"*, a clause with no measurement in it — **reads more like a résumé than
`runs/auxo-ai/resume.pdf` does.** The three mechanisms it buys that with are already refused here
on purpose: a trailing benefit clause is `0027` §4's deleted move 3, JD vocabulary lifted into a
sentence is `0027` §3, and both are `0034`'s synthesis ban in a new coat.

The two that are not refused are the subject of this ADR, and neither of them needs a word the bank
does not already hold.

### The bank records the stakes; the page throws them away

`bank/jobs/american-express.md`, `## c4`, `**Evidence:**`, verbatim:

> *"The review deck is Amex Offers' monthly business-review meeting, held virtually with **the
> directors, the VPs and senior leadership** … Building the
> deck's data cuts by hand meant opening **4--5 Excel files** … every cycle."*

What reached `runs/auxo-ai/bullets.md`, inside the `c1+c3+c4` merge:

> *"Automated the merchant-account mapping, the monthly leadership email and the review deck's data
> cuts, cutting ~8 hours a month"*

Every word of it is true. And the fact a hiring reader would actually weigh — **that this work's
output was read by senior leadership** — is recorded, provenanced, in-bank, downgrade-legal, and on
the floor. `c5`'s Evidence carries the same audience and the same thing happens to it.

More of the same, all out of `**Evidence:**` blocks, none of it on that page:

| claim | fact in `**Evidence:**` | what the page said |
|---|---|---|
| `c1` | *"newly mapped **41 accounts** that had never been matched before"*; *"accuracy … came out around **98%**"* | (inside the merge, both gone) |
| `c2` | *"the artefact that is the **source of truth for every analysis** in the Amex Offers analytics domain"*; *"against a **fixed** scorecard delivery date"* | *"Rewrote the scorecard compilation to generate the new reporting format directly, cutting rework ~85%"* |
| `c7` | *"there are over **150** of them"*; *"**Leadership asked for it**"*; *"a completely new launch"* | *"Owned ~60 of a new diagnostics scorecard's KPIs, automating the heaviest to halve its refresh"* |

`c7` is the sharpest. **~60 means nothing without the 150.** A reader cannot tell whether that is
40% of the deliverable or 4%.

### It is variance, not absence — which is why it is cheap to fix

Three runs, one bank, all composed under the current rubric:

```
runs/zs-btsa/bullets.md        (2026-08-01)  "Took ~60 of ~150 KPIs on a new diagnostics
                                              scorecard…"                       ← denominator kept
runs/mckinsey-shape/bullets.md (2026-08-09)  "…fuzzy-matched them in Python, newly mapping
                                              ~41 accounts"                     ← the 41 kept
runs/auxo-ai/bullets.md        (2026-08-10)  "Owned ~60 of a new diagnostics scorecard's
                                              KPIs…"                            ← both lost
```

The composer *can* reach for these facts and sometimes does. What it does not have is **a named
rule that says to.** Read `tailor` §5's rubric as a list of directives about this fact class and
what is actually there is:

- *"No scale, volume or duration the Evidence does not state"* — a **prohibition**;
- *"Keep a personal project's scale visible"* — **projects only**;
- *"Keep the detail that makes the claim specific — especially what the posting never asked
  about"* — the right instinct, but it names no fact class, so *"4--5 source spreadsheets"* and
  *"read by senior leadership"* are equally covered and equally optional.

**The rubric is exhaustive about what a Bullet may not say and nearly silent about what it should
reach for.** That asymmetry is what this ADR closes.

### Two smaller things read off the same page

**The opener rule's residue is in the verbs.** `render.py` enforces one opening word per page,
deliberately (`0030`: *"the two on the run that motivated this were in different entries, which is
why the rule is the page and not the block"*). `runs/auxo-ai`'s sixteen openers:

```
Replaced  Built  Automated  Owned  Rewrote
Benchmarked  Took  Swapped  Shipped  Pinned
Wrote  Split  Drove  Designed  Made
Synced
```

*Made every tailored résumé ship with a gap report* and *Took the translation tool to Xlscout's
other product teams* are the constraint paying out — the fourth-choice verb, reached for because
the first three were spent.

**A project lead can be a scene with nothing in it.** `runs/auxo-ai/bullets.md` shipped:

> `sweatpact` — *"Exists because informal gym promises between friends accepted any excuse; weekly
> intentions did not reliably survive."*

That is `bank/projects/sweatpact.md`'s `**Situation:**` transcribed. It has no subject, names
nothing built, and on the widest line of the page (`LEAD_CHARS = 117`) it tells a reader nothing
about what SweatPact *is* — which `0032` §1 and `tailor` §5 both say is the one thing a project
lead owes. `auto-apply`'s lead has the same shape: *"Built to end reworking one résumé file by hand
for every application…"*. Both entries' `## lead` blocks are situation-only, with no `aggregate:`,
which is `0032` §5's permitted shape — so the fault is in the composition, not in the bank.

## Decision

### 1. Name the five fact classes, and reach for the strongest one the sentence can afford

`tailor` §5 gains a rule, placed directly after *"The JD decides which claims get a line, not what
goes in the sentence"* — that rule already says *keep the specific detail*, and this one says which
detail. Before composing, read the cited Claim's Evidence for these five, in this order:

1. **the denominator** — the whole the work was a part of. *~60 KPIs* is unreadable; *~60 of ~150*
   is a share.
2. **who consumed the output, and how senior** — *"held with the directors, the VPs and senior
   leadership"*.
3. **how far it spread** — teams, people, documents, how much of it held up.
4. **what it would have cost to get wrong** — *"silently corrupted anything cut by those fields"*,
   *"against a fixed delivery date"*, *"the source of truth for every analysis in the domain"*.
5. **whether it was a first** — *"a completely new launch"*, *"newly mapped 41 accounts that had
   never been matched before"*, *"went unasked"*.

The order is not a ranking of importance; it is the order to read for, cheapest reach first. All
five come off the same page of Evidence, and the ordered list is what stops the read being *"is
there anything good in here"*, which is the read that produced the variance above.

### 2. It adds nothing and licenses nothing

Every one of the five is **downgrade-only composition out of Evidence already in the bank**, which
is why this ADR changes no check and creates no constant. `0003`'s ratchet, `0027` §6's Claim-level
trace and `render.py`'s number trace all bind a reach fact exactly as they bind any other clause.

Two consequences of that, stated so the rule cannot be read as a licence:

- **A claim whose Evidence carries none of the five composes without one.** The absence is a
  `bank-audit` finding (§6), never an invention, and never a reason to go looking in a neighbouring
  claim — `0027` §6's *no importing a fact from a neighbouring claim, however true* is untouched.
- **Titles and audiences are the maker's words as written.** *"the directors, the VPs and senior
  leadership"* may shorten to *"senior leadership"* — a downgrade — and may never become *"the
  C-suite"* or *"executive leadership"*, which are upgrades wearing a summary's clothes.

### 3. The number outranks the reach, and one line reaches once

`0029`'s *"the number is the last thing a Bullet gives up"* stands exactly as written. A reach fact
is what a line spends its **remaining** characters on: it is cut before a figure, never instead of
one, and the two legal grounds for a figure leaving are still `0029` §3's two and no others.

**Do not reach twice in one line.** One sizing fact per Bullet. Two is the sentence becoming a
specification, and the second is what `0027` §4's cut-for-length table takes first. This is the one
place the rule has a brake, and it is needed: five named classes against a 103-character line is an
invitation to write the line as a list of qualifiers.

### 4. A Bullet does not have to open on a verb

The opener rule bites hardest on a full page — with `MAX_BULLETS = 6` and four entries, up to
nineteen distinct opening words against one bank — and the wrong way out is a rarer verb. The
release valve already exists and is already legal under `0027` §2's *no house shape*; it is simply
never said out loud. `runs/zs-btsa` does it twice, well:

> *"**A Python fuzzy-matching pipeline** took over the hand mapping of merchant names, ~3 hours a
> cycle to ~1"*
> *"**Translating a manual meant** copying every line out by hand and pasting it back; the pipeline
> does it in place…"*

**When the opener check fires, the first thing to try is a different sentence, not a different
word.** `0030`'s page scope is untouched — see `## Rejected`.

### 5. On a project with no `aggregate:`, the lead still names the thing

`tailor` §5's *"A lead is a frame, not a scene"* paragraph gains one line. A situation-only lead
that opens on the before-state has spent the widest line on the page before it has said what the
entry is.

> *"A gym-accountability app that puts a weekly money stake on a goal, with GPS check-ins verified
> server-side"*

Every word of that is in `bank/projects/sweatpact.md` `## c1`'s Evidence — *"a committed weekly
goal, GPS check-ins verified server-side, and a flat weekly stake owed to the other person when the
goal is missed"* — so it is a composition change and not an ingestion one. The before-state rides in
a clause or does not ride. `0032` §5's permission for a situation-only lead is unchanged; what
changes is what such a lead has to achieve before it spends its line.

### 6. The supply side: ingestion asks for it, and the audit notices when it is not there

§2 says the composer never invents a sizing fact. That only works if the bank has them, and for
entries ingested before this rule existed nothing ever asked. Two changes close the loop.

**`ingest` §3's depth pass gains two questions**, in that section's register — jogging, specific,
never *"are you sure?"*:

- **the denominator** — *"~60 KPIs — out of how many?"*, *"how much of the deliverable was that?"*
- **the reach** — *"who ended up using it, and are they still?"*

Both sit under the existing **Numbers** rule (*"Never ask for a number"*) rather than beside it:
these are questions about the shape of the work whose answers happen to carry figures, which is
exactly that section's stated mechanism. **A denominator that arrives this way is Evidence prose,
not the claim's `number:` field.** `number:` stays the outcome figure — `~150 KPIs` is precisely the
kind of hollow figure the *"So what?"* test exists to keep out of it, and is worth every word of its
place in the Evidence.

The rest of that list is already excellent on stakes, and on this bank it worked: the Group
President audience, the 150 KPIs and the 41 accounts are all in the bank *because* it asked.

**`bank-audit` gains a fourth Shallowness check**, entry-level and print-only like the other three:
**an entry no Claim of which carries a sizing fact at all.** Each individual claim may say what
changed perfectly well, so checks 1 and 2 pass; what it renders as is a column of true, unweighable
sentences. It is entry-level for check 3's reason — one claim without a denominator is normal, a
whole job without one is a depth pass that never asked.

## Rejected

**Rescoping the opener check to the entry.** The obvious way to relieve opener pressure, and it is
refused: `0030` argued the page scope from a run where the two collisions were in *different*
entries — *"a composer obeying `0027` §2 to the letter still ships them"* — and that argument holds
unchanged. §4 gives the rubric a way out that costs nothing; it does not give the check a looser
threshold. `0030` §2's rule applies as written: if the page comes back worse, the answer is the
rubric restated harder, not a rescoped check.

**A `reach:` or `scale:` field in the Claim schema.** It would make the five classes findable
mechanically and would let the audit's check 4 be arithmetic instead of a reading. Refused for
`0004`'s reason and `bank-audit`'s: *"Any why / who / what it replaced field — the Claim schema has
no such fields. Checking for them invents structure the bank does not have."* A denominator is a
sentence in the Evidence, not a slot, and a slot would immediately be filled to be filled.

**A check in `render.py` that a Bullet carries a sizing fact.** There is nothing countable here.
Every candidate test is a reading of prose, which is `0010`'s refused reviewer, and the one thing a
script could count — a digit on the line — is `0029`'s number, already checked, and would mark
*"read by senior leadership"* as a failure. This lands as a rubric paragraph with nothing
measuring it, which is a bill and not a design; it is priced below.

**Requiring a sizing fact on every Bullet.** §2's whole point is that a claim whose Evidence has
none composes without one. A requirement would make the composer find one, and the only place left
to find it is the neighbouring claim or the model's own general knowledge.

**Fixing the shape of the reach — "always lead with the denominator".** `0027` §2 refused a house
shape for the sentence and the same argument holds one level down: six lines that all open on a
fraction read like a form. The five are a list to read Evidence for, not a template to fill.

## The cost, stated rather than waved past

**Nothing measures this, and the record says that is how it goes wrong.** `0027` wrote *"write to
say the thing, then check the budget"*, nothing measured it, and the fill rate across two composed
pages went **from 95.9% to 96.5%** — the wrong way. `0037` §7 hit the same wall and bought one
arithmetic count to sit beside its rubric paragraph. There is no equivalent count available here:
§6's audit check is a *reading* of the bank done by a person's agent on demand, not a lint on the
run, and it fires on the supply side rather than on the page. **This ADR is a rubric paragraph plus
a maintenance pass, and the honest expectation is that it works less well than a check would.**

**It pushes every line toward the cap, and `0030`'s spread check is what will feel it.** A reach
fact costs characters on a page where fourteen of fourteen one-line Bullets already measured 95–103.
The check fires at *one in three at or under 88*, and this rule makes that harder to satisfy. That
is the rubric working, not a check to rescope: the fix is `0027` §4's cut-for-length — scaffolding
before detail, a noun already named before a fact stated once — and if a line genuinely cannot hold
both a figure and a reach fact, §3 says which one goes.

**The fourth Shallowness check is the first thing ever added to a list that says it is closed.**
`bank-audit` §2 reads *"Inventing a fourth check is this section's failure mode, and it arrives
disguised as helpfulness"*, and this decision is doing exactly the thing that warning names. What
distinguishes it from the shapes that warning is aimed at — a thin `skills` line, a terse Assertion,
prose you would have written differently — is that it was not derived from taste: an entry of
unweighable sentences was on a rendered page, the fact that would have fixed it was in the bank, and
nothing anywhere said so. It is also **entry-level**, so it cannot swamp the list the way a
per-claim check would. That is the argument; it is not a proof, and the check earns its place only
if the maker finds its findings actionable.

**Check 4 and *"a missing number is not a defect"* live one paragraph apart and will be confused.**
They are genuinely different — a sizing fact is prose, so an entry whose every claim carries a
`number:` can still fail check 4 and an entry with no figure anywhere can pass — but the distinction
has to be held by whoever runs the sweep, and the failure mode is the sweep quietly becoming a
number audit. The `## What is not a check` section says so explicitly; nothing enforces it.

**The ingestion interview gets longer.** `0014` sized that list against what a person will sit
through, and two more questions per claim is a real charge against an already-long sitting. They are
placed under **Numbers** rather than added to the pressure list twice over, and the register rule —
jogging, specific — is what keeps them one question rather than a sub-interview.

## Consequences

- **`.claude/skills/tailor/SKILL.md` §5** gains the reach rule after *"The JD decides which claims
  get a line"*; the prohibition *"No scale, volume or duration the Evidence does not state"* gains
  the clause *"— and where the Evidence does state one, see the reach rule above"*; *"No opening
  word twice on one page"* gains §4's release valve; *"A lead is a frame, not a scene"* gains §5's
  line. *"Keep a personal project's scale visible"* is left exactly as it stands — it stops being an
  orphan and becomes the project-side instance of a general rule.
- **`.claude/skills/ingest/SKILL.md` §3** gains the two questions and the `number:` boundary under
  **Numbers**.
- **`.claude/skills/bank-audit/SKILL.md`** goes from three checks to four; `## What is not a check`
  gains the sentence separating check 4 from a missing `number`; the printed sweep gains a
  `No sizing fact anywhere in the entry` group; *"Inventing a fourth check"* is reworded to
  *"Inventing a check"* and names this ADR as the one addition the list has taken.
- **`CONTEXT.md`**: **Shallowness checks** goes to four and **Shallow entry** gains its second way.
- **No code change, no constant change, no new check.** `pack.py`, `render.py`, `config.py` and the
  Template are untouched by this ADR.
- **`0030` is not narrowed.** The opener check keeps its page scope and its wording; §4 changes what
  the composer does when it fires.
- **`0032` is not narrowed.** A situation-only lead is still legal; §5 says what one owes.
- **The runs re-compose.** `runs/auxo-ai` and `runs/mckinsey-shape` are the read: does
  `american-express/c7` regain its *~150*, does the `c1+c3+c4` merge or `c5` acquire its audience,
  and does anything acquire a fact its Evidence does not carry. **The last of those is a failure of
  this ADR and the answer is to revert it, not to patch it.**
