# A Bullet is a sentence, and the posting does not write it

**Status:** accepted

## Context

Reading `runs/zs-btsa` back, the maker found the prose bad in three specific ways (#47, #51):

1. **The sentences are badly written.** `xlscout/c1` rendered as *"Took the tool to other product
   teams to test on their manuals, then fixed the failures that exposed"* — not a sentence.
   `auto-apply/c7` as *"Built the system through Claude Code skills, hooks and MCP, which produced its
   written design record"* — a relative clause with nothing to attach to.
2. **The line is too cramped to write well in.** `CHARS_PER_BULLET = 103`, and all twelve composed
   Bullets landed at **98–103**. Not some of them: all of them, jammed against the cap.
3. **The rubric bends words toward the JD.** Move 1 — *"swap a word for the JD's word where the two
   denote the same thing"* — pulls the sentence toward the posting's vocabulary and away from the
   work's.

And one fault he explicitly did **not** claim: shown that *"Automated the monthly business-review deck data
cuts…"* rendered as *"Cut ~4 hours of Excel pivoting… by building its data cuts off BigQuery"*, he did
not object to the house verb replacing his own word. A rubric that only protects his vocabulary has
missed the complaint.

### The method was candidates, not argument

Arguing about rules in the abstract is what produced the rubric being replaced. Four real Claims —
`american-express/c4` (the uncontested control), `american-express/c7` (three facts, one line),
`xlscout/c1` and `auto-apply/c7` (the two broken sentences) — were each written six genuinely
different ways by Fable, with verified character counts: **CONTROL** (today's rubric exactly, 96–103),
**ROOM** (78–92), **WIDE** (two lines, 150–200), **SITUATION-FIRST** (before-state leads),
**MAKER'S WORDS** (the Assertion minimally re-angled, no JD vocabulary), **BLUNT** (55–75, one clause).

### The first answer was not the answer

The maker's first read was that **the WIDE ones won almost everywhere** — *"they actually tell what
changed rather than having incomplete information."* Taken at face value that would have made the
second line the default, which `0025` forbids: the residue on this bank is **five lines against
nineteen Bullets**, and *"on a full page nothing wraps."*

So it was tested against a one-liner carrying the same information in a different shape:

| | |
|---|---|
| WIDE (157) | *Replaced ~4-5 hours of hand-built Excel pivoting each cycle by automating the monthly business review deck's data cuts off scorecard data and BigQuery tables* |
| SITUATION-FIRST (102) | *Each cycle took ~4-5 hours of hand-built Excel pivoting; automated the review deck's data cuts instead* |

**Good enough.** That is the finding the rest of this ADR rests on: the complaint was *incomplete
information*, and length was a proxy for it. **The fault is the shape of the sentence, not the width
of the line.** 103 characters survives.

## Decision

### 1. A Bullet is a complete sentence that says what changed

The standard is **completeness**, not compression and not length. A line that stops before its own
argument is finished has failed, however many facts it packed in; a line that finishes in 66
characters has not failed for being short.

This is what the three faults have in common. `xlscout/c1`'s Bullet is ungrammatical *because* it was
compressed past the point where the sentence still worked, and *"the failures that exposed"* is the
visible stump. Grammaticality is not a style preference here — it is the tripwire that fires when a
line has been cut past completeness.

**Write to say the thing, then check the budget.** Not the reverse. A composed set where every line
lands at 98–103 is evidence of a rubric being followed, not of nineteen sentences that happened to
need the same room.

### 2. No fixed shape — six in a column must not read like a form

**Rejected: lead with the before-state.** It was the obvious rule to take from the maker's picks, and
three of the four SITUATION-FIRST candidates used the identical construction — *"this was the
situation; did X instead"*, semicolon and all. Under `0024` an entry now gets **up to six Bullets in a
column**. Six of those in a row read like a template rather than like someone who did six different
things. A preference is not a formula.

**Rejected: lead with the change** — the rule as it stood. It is what cost the before-state, and the
before-state is often the thing that makes a line land. Charging every sentence into a house verb is
the same error in the other direction.

So the shape is the writer's, chosen for how the line reads and for how it sits beside its
neighbours. What survives of the old rule is only its floor: **`Worked on`, `Was responsible for` and
`Helped build` are still forbidden** — they spend the reader's first four words saying nothing, and
they are where scope inflation hides. That was never the disputed part.

### 3. The posting may tell you which of your own words to reach for; it may never supply one

Move 1 narrows to exactly this. The test is **the Evidence**, not the `skills:` line and not
plausibility.

`BigQuery` **passes** on `american-express/c4` — the Evidence says *"the internal data platform, essentially
Google BigQuery."* Both words are the maker's; the posting only made one of them
the one worth choosing. This is why the maker never objected to it, in any candidate, and it is the
whole legitimate content of move 1.

*User acceptance testing* **fails** on `xlscout/c1`, and fails instructively, because the Claim's
`skills:` line literally carries it and ZS literally asks for test cases and post-go-live support:

| | |
|---|---|
| what was done | *Took the translation tool to other product teams, fixing the layout failures it turned up* (89) |
| bent to the posting | *Ran user acceptance testing across product teams and handled post-go-live fixes on the translation tool* (103) |

Every word of the second is defensible and the sentence is a job description. The Evidence describes
going round the teams because he wanted to know whether the thing worked; it does not describe running
a UAT process. **A skill on the `skills:` line licenses the skill appearing in the Skills rows. It does
not license building the sentence out of the posting's phrase for it.**

Note the second reading of that table, because it explains fault 2's real cause: **the bent line is 14
characters longer.** Bending toward the posting was eating the budget the sentence then did not have to
be written in.

### 4. The JD decides which claims get a line. It does not decide what goes in the sentence

**Move 3 — *"Drop detail this JD does not buy; spend the line on what the posting asks for"* — is
deleted.** The maker: *"we don't want to have only things that the JD mentions, we want that there
should be more stuff too that is likely relevant."*

The structural reason it has to go: **the posting already had its say.** The Fit rubric scores every
Claim against the JD, and that is what decides which claims reach the page at all — `c4` is on the page
*because* ZS asks for a cloud platform. Composition then applied the same filter a second time, to the
inside of the sentence, and what survived was the part that overlaps the posting — which is the part
the posting already knew.

| | |
|---|---|
| JD-filtered (today) | *Cut ~4-5 hours of Excel pivoting from Amex's monthly review by automating its data cuts off BigQuery* (100) |
| carrying its own detail | *Automated the monthly review deck's data cuts, replacing ~4-5 hours of pivoting across 4-5 Excel files* (102) |

Same length. ZS never asks about *4-5 Excel files*, and it is the only thing in either line that tells
a reader what the work was.

**So you still cut, and the line is still 103 characters — but you cut for length, and what goes is
whatever the sentence survives losing.** Generic scaffolding before specific detail; a noun already
named before a fact stated once. The four worked overruns in the old rubric's table are all still
correct, and for this reason rather than the one they were filed under: not one of them lost a fact.

**Rejected: loosen move 3 to "detail that is likely relevant."** It is the maker's own phrasing and it
is not writable — *likely relevant to whom, judged how* — and it reinstates the posting as the arbiter
of the sentence's interior, which is the thing that failed.

### 5. A claim asks for the second line when the detail that makes it specific will not fit

This is the rubric line `0025` explicitly left open — *"when a claim deserves to ask"* — and it falls
straight out of §4. Not because the claim scores well, not because it is long, not because it has many
facts:

> *Went unasked to Xlscout's other product teams to prove the tool generalised, fixing the layouts that
> broke* — **106**

Three characters over. *Unasked* is the point of `xlscout/c1` — going wider was the maker's own move,
not an assignment — and it is precisely what the deleted move 3 cut first, because ZS has no bullet
point for it. **Width is earned when compressing to one line costs the thing worth saying.**

Declared as `width: 2` in `scores.md` at scoring time (`0025` §3), judged on the Claim's substance
before any allocation is known and before a word is composed. `0025` §2 still governs what happens
next: **evidence outranks room**, the want is granted only out of what the evidence left over, and a
Bullet denied its width is rewritten to one line rather than dropped.

### 6. What survives untouched

The constraints this ticket inherited and could not break, restated so the rewrite is not read as
loosening them:

- **Downgrade-only, Claim-level trace.** Better writing may not add a fact. Every claim in the line is
  present in or entailed by the cited Claim's Evidence — the maker defends this in the interview.
- **One Bullet, one Claim, one citation.** A prettier sentence that fuses two claims is not a candidate.
  **Superseded by `0034`:** a Bullet may cite up to three Claims, and what replaces this rule is that a
  merged Bullet **coordinates** its claims and never **synthesises** them — it may not assert anything
  about their relationship that no Evidence states.
- **Numbers move one way only.** `estimated` renders softened, always. A *soften* answer at the
  Checkpoint moves one step further down.
- **Keep a personal project's scale visible.**
- **Six Bullets in one entry make six different arguments.** `0024` raised the cap; the rule scales
  with it.
- **`CHARS_PER_BULLET` is a measurement of the Template, not a policy.** `0025` refused raising it on
  the record; nothing here reopens that.

## Rejected

**Rejected: raise `CHARS_PER_BULLET`, or make the second line the default.** The first is `0025`'s
refusal and stands. The second died on the maker's own answer — the 102-character one-liner was good
enough — and could not have been afforded anyway: five spare lines against nineteen Bullets.

**Rejected: protect the maker's vocabulary.** The obvious reading of "the rubric bends words toward the
JD", and wrong. He was shown `Cut` replacing his `Automated` and did not object, in the charting
grilling and again across every candidate for `american-express/c4`. The bend he objects to is of the
**sentence**, not of a word's ownership. §3 draws the line where he actually drew it: at whether the
Evidence carries the word, not at who said it first.

**Rejected: a worked example bank of good Bullets in `tailor/SKILL.md`.** Considered because the
candidates in this ticket are the most concrete thing the rubric has ever had. Refused because
examples become templates — the §2 failure mode of this ADR, at a larger scale, with the twenty-four
candidates read as a menu. The rubric keeps its short illustrative lines and states rules.

## Consequences

- **`tailor/SKILL.md` §5's composition rubric is rewritten.** *Three moves are allowed, and only
  three* is gone: move 1 survives narrowed (§3), move 2 — *reorder to lead with the part this JD asks
  about* — goes with move 3, because ordering the sentence for the posting is the same act as filling
  it for the posting; move 3 is deleted (§4). **Lead with the change** stops being mandatory and keeps
  only its floor. **Write for `CHARS_PER_BULLET`** stops being an instruction to fill the line.
- **§5 gains the width test** (§5 above) and §2 gains the `width` column — the latter is `0025`'s
  change and lands with the code under #53.
- **`tools/lengths.py`'s under-fill flag becomes advisory, not a defect.** `0025` had it flag "a
  granted second line left mostly empty". Under §1 a short line is not a failure; what the flag is for
  is a *granted width* nobody used, which is a width-declaration error at §2, not a prose error.
- **No code change and no constant change.** This ADR is entirely a change to what Opus is told. The
  page arithmetic is `0024`, `0025` and `0026`'s; #53 builds all four.
- **#52 inherits a sharper question.** *Does the bad writing start at the Assertion?* now has a worked
  answer for `american-express/c4` — the Assertion reads well, the Bullet composed from it was worse,
  and §4 names the mechanism: the JD filter applied to the sentence's interior. Whether that accounts
  for `xlscout/c1` and `auto-apply/c7` too is still #52's read to do.
- **No re-render is owed here.** The rubric governs the next run; `runs/zs-btsa` is re-rendered under
  #53 with all of the map's decisions in place at once.

## Addendum, 2026-08-13 — §2's "No house shape" is reversed

`docs/adr/0047-the-bullet-is-an-xyz-sentence.md` gives the Bullet a house shape:
**X, Y, Z** — impact first, the measure attached to it, the method last. §2 of this
ADR forbade exactly that, and is superseded on this point.

**What is reversed is the "no fixed shape" half only.** §2's other half — *no opening
word twice on one page* — is untouched, still enforced by `render.py`, and gets easier
rather than harder, because an XYZ page carries fewer Bullets.

The honest framing, which `docs/research/bullet-frameworks.md` established when it
went looking for evidence for this section and came back with evidence against it:
§2's *"six of those in a row read like a template"* was **this project's own aesthetic
position, held against the style authorities**. Purdue OWL requires that *"each bullet
must be in parallel form"*; the Microsoft Writing Style Guide requires that all items
in a list be *"consistent in structure"*. The survey's verdict was that this ADR ran
together two separable things — repeating the **opener**, a recognised fault, and
repeating the **grammatical shape**, a recognised virtue — and that only the first
ever needed forbidding. `0047` acts on that finding.

**§1, §3, §4 and §6 are untouched and still outrank the formula.** A Bullet is still a
complete sentence that says what changed; the posting still may not supply a word to
one; the JD still decides which claims get a line and not what goes in the sentence;
it is still one Bullet, one Claim, one citation. Where XYZ and rule 2 meet, rule 2
wins — which is why `0047` §2 composes no Y for a Claim that carries no figure.

## Addendum, 2026-08-13 — §3 is reversed for Bullets; §4 is not

`docs/adr/0050-the-posting-names-the-work-it-never-supplies-it.md` §1 extends `0044`'s
Summary relaxation to every Bullet. §3 above — *the posting may never supply a word* —
no longer binds a Bullet, on `0044`'s exact terms:

> **A keyword is a name for something; a fact is a claim about the candidate. The
> posting supplies names. It supplies no facts.**

**§4 is explicitly NOT reversed**, and the two are the easiest thing here to confuse.
The posting may now supply the *word* for a thing the Evidence carries; it still does
not decide *which* things the sentence mentions. Filtering a Bullet's interior by the
JD still leaves only the part the posting already knew, and the detail that makes a
claim specific is still kept — especially what the posting never asked about.

§1, §2's opener half, and §6 are untouched, and the interview test binds every
renaming: a name for his own work the maker cannot defend in the room is a re-scoping
wearing a synonym.
