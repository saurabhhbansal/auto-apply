# The arc is a frame around the Bullets, not a shape inside them

**Status:** accepted

## Context

`runs/auxo-ai` renders the Amex entry as six Bullets at the cap, and the maker read it back and said
three things that turned out to be one thing (#70). Six separate automations of pieces of **the same
monthly reporting cycle**, each carrying its own saving, and the reader is left to do the addition —
which they will not. The figure that would actually land, **≈17.5 hours a month**, is on no page and
in no file.

The map's charting settled the shape as an **entry arc** — *situation → what you did → what it added
up to*, any beat allowed to be absent — and left this ticket to say what a beat is (#72).

### The research changed the question before it was answered

#72 was deliberately blocked on #71, because the maker asked for tried-and-tested frameworks to be
found *before* the shape was settled rather than cited afterwards. The survey is
`docs/research/bullet-frameworks.md`, summarised on #71, and two of its findings bear directly on
this decision.

**Nobody puts the situation in a bullet.** OPM's `Guide to SES Qualifications` — the strongest
provenance in the survey, published guidance from the body that runs the process — instructs
candidates to *"begin your ECQ statement with a brief summary of your executive experience"*, above
the accomplishments. Enelow and Kursmark, who founded the résumé-writing certifications, reach the
same structure independently: *"Before plunging into your achievements … start with a brief
description of the company, job scope, and key challenges, **followed by** bullet points."* In every
source that has an opening at all, it is a separate, unbulleted unit, and it is longer than the lines
below it.

**And nobody closes on the sum.** Every published aggregate is a **lead** — Enelow and Kursmark's
Career Track format carries the whole-tenure figure in the scope paragraph, OPM opens on a summary —
and the only ordering rule any source states is *most relevant, most impressive first*. The map's
*"closes on what it added up to"* has no external precedent as a closing beat.

### What that collides with here

`templates/resume.tex.j2:322-334` gives an entry a `\resumeSubheading` and then a flat list of
`\resumeItem`s. **There is no unbulleted entry text in this template**, so a situation had nowhere to
go but into a Bullet — and a Bullet carrying the condition all five Claims share breaks `0027` §6
(*one Bullet, one Claim, one citation*), which is load-bearing for `check_number_trace`, the Omission
view and the Packer's slot arithmetic.

`0027` §2 is the other rule in the way, and it was written against real evidence: three of four
SITUATION-FIRST candidates came back with the identical *"this was the situation; did X instead"*
construction, semicolon and all, and six of those in a column read like a form.

## Decision

### 1. The arc is a frame: one unbulleted lead line, and Bullets that are purely the middle

An Entry may be preceded by **one unbulleted lead line**, under the header and above the Bullets,
carrying the situation and the aggregate. Both ends of the arc leave the column. What the map called
an arc *across* the Bullets is a frame *around* them.

```
PRODUCT DEVELOPMENT INTERN                        Jan 2026 -- Jul 2026
American Express                             Gurgaon, Haryana, India
  The whole monthly reporting cycle was hand-run; automating it gave
  back ~17.5 hours a month.
  • Hand-mapping Tier, Portfolio and Account silently corrupted
    analyses; fuzzy match cut it ~75%
  • Automated the review deck's data cuts, ending ~4.5 hours of
    Excel pivoting
  • …
```

**This is what makes the rest of this ADR cheap.** The three hardest questions #72 asked — whether a
beat is a Claim, what the middle is made of, what `0027` §2 becomes — all dissolve once the ends
leave the column:

- **A beat is not a Claim.** The lead is not scored, not cited, does not compete for a Bullet slot,
  and is not a candidate for anything. `0027` §6 is untouched, `check_number_trace`'s Claim-level
  trace is untouched, and the Omission view gains no new object.
- **The middle is one kind of thing.** It is achievements, and only achievements, because there is
  nowhere else for a situation or a sum to be.
- **The construction `0027` §2 was written against can no longer occur.** No Bullet carries a
  before-state, so *"this was the situation; did X instead"* cannot recur six times in a column,
  because it cannot occur once.

**Rejected: the situation rides inside the first Bullet.** `0027`'s own worked candidate proves it
fits — *"Each cycle took ~4-5 hours of hand-built Excel pivoting; automated the review deck's data
cuts instead"* at 102 characters — and it would have cost no line, no macro and no schema. It loses
on fidelity: Amex's opening is the condition **all five Claims share**, and folding it into whichever
Claim leads reports it as that one Claim's situation. It is also the exact construction `0027` §2
objected to, reinstated as policy.

**Rejected: a bulleted opening line.** It keeps the template as it is, and it is what the map
assumed. It loses because a Bullet that cites the entry rather than a Claim is a new kind of object
everywhere it goes — a new trace rule, a new Packer slot, a row in the Omission view that never
competed for a score — and no source anywhere writes the situation as a bullet.

### 2. The lead's facts live in the bank; the tailor writes only its sentence

The Entry file gains one optional block:

```
## lead
number: ~17.5 hours per month
provenance: estimated

**Situation:** The whole Amex Offers monthly reporting cycle was run by hand.

**Aggregate:** The automations together gave back about 17.5 hours a month.
```

This is the charting decision about the aggregate — *the fact lives in the bank; the tailor writes
its sentence* — extended to the other half of the frame, because the two halves are the same species
of fact.

**Both halves are spoken.** *The monthly reporting cycle was hand-run* is nowhere in
`bank/jobs/american-express.md` today. It is inferable across `c1`–`c7`'s Evidence, and inferring it
at compose time is the model forming a judgement about the maker's own history — which `0010`
refuses on principle, and which would put an unspoken assertion on the page in the one file that has
no lint. So it arrives the way the aggregate does, by `0015`'s agent-proposes/maker-judges shape: the
agent reads the entry, offers a sentence, and the maker's yes is what makes it spoken. The maker
judges; the maker never produces.

> **Refined by `0036` §6.** The situation is **asked, never proposed** — only the aggregate is
> offered. *The agent reads the entry, offers a sentence* is `ingest`'s rule 3 (*never arrive with a
> drafted Entry*) at the highest-stakes point it covers, and unlike the sum the situation has no
> working to be checked against. The asymmetry is charting's own: the maker is a bad source and a
> good judge of a **sum**, and the only source there has ever been for a **situation**. Everything
> else in this section stands.

`number:` and `provenance:` carry exactly the meaning they carry on a Claim. An `estimated` aggregate
renders softened under `0022` and may only move down under `0029`. Nothing new is invented here — the
lead block borrows the two fields whose semantics the bank already fixes.

**How `ingest` asks for it, and how the four existing entries are amended through the Return door, is
#76's.** This ADR fixes the shape of what it asks for.

### 3. One beat, probed from two angles

`situation:` is **one flat field**. There is no second field for a problem-an-artifact-was-built-for,
and no discriminator anywhere.

The map raised the possibility that these are two beats: `american-express` opens on a standing
condition walked into, `xlscout` on a problem something was built against, and a project's version is
a gap nobody had filled. They read differently, and CCAR does split **Context** from **Challenge**.
But OPM's own annotated examples show the two interleaving and recurring inside one narrative rather
than occupying fixed slots, which is evidence the split is a way of reading rather than a structure.

And the deciding constraint is the map's: **no mode, no flag, no dependence on `type:`.** A schema
that distinguishes a condition from a problem forces the interview to classify the entry, which is
that dependence arriving by a side door.

**The interview probes both ways and keeps the stronger answer.** `ingest` asks *what did this look
like when you got there* and *what was this built against*, and writes one answer into one field.
That is a refinement of how the question is put, with nothing checkable behind it, and it is recorded
here as such.

### 4. Exactly one line, always

`LEAD_LINES = 1`, hard. `LEAD_CHARS` is **measured off the compiled template** by the procedure in
`docs/calibration.md` and belongs in `config.py` with the other measured geometry — the lead sits
outside the Bullet `itemize`, carrying no marker and less indent, so it will come out wider than
`CHARS_PER_BULLET = 103`.

The lead is the one line on the page carrying two facts by design, so the case for width is
structurally different from a Claim's. It is refused anyway. `0025` declined to make a second line
the default against a residue of five spare lines on nineteen Bullets, and that arithmetic has not
moved; a variable-cost lead would put a second elastic object into the Packer beside the entry
blocks; and the discipline every other line on this page lives under is a fixed budget with the
writing done to fit it.

**The bill, measured rather than assumed:**

| | chars |
|---|---|
| *The whole monthly reporting cycle was hand-run; automating it gave back ~17.5 hours a month.* | **92** |
| *Manuals had to be translated by hand, line by line; the pipeline got them ~95% usable, run by the writers themselves.* | **117** |

Amex fits comfortably. **xlscout does not**, and will lose something — most likely half of one half.
That is the cost, and it lands precisely where the research said the sources spend room. See the cost
section.

### 5. Absent costs nothing, and either half may be missing alone

An Entry with no `## lead` block renders no lead line and is charged no lead lines. The template takes
the guard already used for Bullets at `resume.tex.j2:326`:

```
\BLOCK{if entry.lead}
      \resumeEntryLead{\VAR{entry.lead}}
\BLOCK{endif}
```

**This is what makes the map's central claim true rather than asserted.** `auto-apply` and `sweatpact`
have neither end. They gain no block, so they render exactly as they render today, and the degradation
is free by construction — not by a rule anyone has to remember, and not by a mode.

`situation:` and `aggregate:` are independently optional. A job with a clear before-state and nothing
summable gets a situation-only lead; the map's own table records `auto-apply`'s closing beat as *"it
exists, which is the header"*, which is a lead with neither.

### 6. A placed Entry keeps its lead

The Packer reserves `LEAD_LINES` for a placed Entry that has a lead, **before** allocating its
Bullets. `pack.py`'s reservation minimum rises from `ENTRY_HEADER_LINES + 1` to
`ENTRY_HEADER_LINES + LEAD_LINES + 1` for those entries. If room is short, **Bullets give way, not the
frame.**

This inverts `0025`'s *evidence outranks room* for one object, and it is deliberate. The frame is what
makes the Bullets legible — an entry that renders its five automations without the sentence saying
they were one cycle is the page the map exists to stop printing. A frame that could silently not
appear on a tight page is a fix that works except when it matters.

**The bill:** Amex renders a lead plus five Bullets where it rendered six. And on a crowded page an
Entry can come out as a frame around two Bullets, which `0026` already accepts the general form of —
*"a job at 1 Bullet beside a project at 6 is the design rather than an accident."*

### 7. What checks the lead, and what does not

**The split is by kind, not by leniency.** `0030`'s set checks are page-level judgements about how a
column of comparable lines reads; `render.py`'s checks are arithmetic about facts. The lead is exempt
from the first and bound by the second.

| | |
|---|---|
| `0030` §2 spread | **Bullets only.** The threshold stays `CHARS_PER_BULLET − 15` = 88, underived and unchanged |
| `0030` §3 openers | **Bullets only** |
| `0030` §4 spelling | **Unchanged — page-wide.** Bullets, Skills rows and leads, as its scope already read |
| `render.py` | **Fails the run** on a lead over `LEAD_CHARS`; on a figure in the lead that does not trace to `lead.number`; on an `estimated` figure rendered flat |

The spread rule is the clearest case for exemption. Its threshold is *the Bullet's cap minus 15*, and
a lead's cap is a different number — held to a flat 88 the lead would have to finish 24 characters
under its own budget to count as short, so it would join the rule's denominator and almost never its
numerator, quietly tightening a rule written to catch writing-to-the-cap. Generalising the threshold
to *each line's own cap minus 15* was considered and rejected below.

The opener check follows it out for the same reason `0030` §3 exempts Skills row labels: the lead is
composed from a different source under a different set of rules. **The cost is named:** unlike a
Skills label, the lead sits directly above the Bullets in the same column, so a lead and a first
Bullet may open on the same word and nothing will say so.

The spelling check stays because it was **never a Bullets-only rule** — its scope is already
*anywhere in `bullets.md`*, Skills rows included — and because it is a suffix match rather than an
opinion. *One spelling convention per page* has to mean per page.

`render.py`'s checks stay because they are the guarantee this system is *about*. `bank/projects/auto-apply.md`'s
`c1` is a Claim that this build *"fails when a figure in a bullet cannot be traced back to a recorded
claim, and permits a figure to be softened but never hardened."* An untraced `~17.5 hours` reaching
the PDF would make that sentence false about the résumé printing it.

### 8. `0027` §2 is refined to its floor

The prohibition — *"No fixed shape — six in a column must not read like a form"* — is **deleted**.
What survives is what §2 always had teeth for:

> `Worked on`, `Was responsible for` and `Helped build` are forbidden. They spend the reader's first
> four words saying nothing, and they are where scope inflation hides.

Two reasons, and the first is structural. **§2's evidence has left the page.** It was written against
four SITUATION-FIRST candidates that led on the before-state; under §1 no Bullet leads on a
before-state, because no Bullet has one. A rule survives its evidence only if it has other work to do.

The second is external, and it runs the other way. The research found that Purdue OWL and the
Microsoft Style Guide both **mandate** parallelism in lists — *"each item must be grammatically
formatted the same"*. §2's *no fixed shape* has no support anywhere in the survey. Only its
repeated-**opener** half does, and that half is already enforced as arithmetic by `0030` §3.

**Rejected: inverting §2 into a parallelism preference.** It has the best external backing in the
survey and it would give the composer a positive instruction rather than a prohibition. It loses on
the maker's own reading, which is the evidence this repo actually has: six atoms in one column is
what started #70. Swapping an uncheckable rule for its uncheckable opposite is not a gain.

**What now stands against sameness in the column is `0030` §3 and nothing else.** Said plainly
because it is a real reduction: `0027` §2 could be pointed at any two Bullets that read alike, and
the opener check can only see the first word.

## The cost, stated rather than waved past

**The research's best finding is half-honoured.** Every source puts the situation in an unbulleted
lead *because it is longer* — room is the point of the unit, not merely its lack of a marker. §1 takes
the unbulleted part and §4 caps it at one line anyway. xlscout's natural lead is already 117 against a
cap that will land near 112, so the first real entry to meet this rule loses to it. The alternative
was a variable-width lead, refused for reasons `0025` settled on a page whose residue has not changed.
`#78` reads this one on a compiled page.

**The map's headline complaint is not fixed here.** *"It fills to six because nothing ever asks
whether the sixth atom is worth a line given the five above it."* Under §6 the Amex entry renders a
lead plus five Bullets — the lead took a slot, it did not stop the entry filling. **That is entirely
#77's**, and if #77 comes back empty this map changes the page's shape without changing what the maker
objected to.

**§8 rests on a single claim.** *The situation left the column* is true of the **opening** situation
and of nothing else. Nothing in this ADR stops a composer writing six Bullets of identical
construction for a reason §2 never anticipated, and after §8 only a first-word comparison will notice.

**The migration lands where this repo's tests cannot see it.** Four Entry files gain a `## lead` block
in the private `bank` repo under `0019`, and CI never reads them. `bankcheck.py` is the only verifier,
exactly as `0031` recorded for the `dates:` migration — and this ADR pays that window a second time,
knowingly, because the map said it would.

**Two entries will honestly have nothing to say.** `auto-apply` and `sweatpact` get the questions
asked and answered *there isn't one*. That is a real interview cost for a null result, and it is the
only way the null is on the record rather than merely absent.

## Rejected

**A trailing lead line — a true bookend.** The map's charting words taken literally: the situation
above, the sum below, the Bullets between. It puts the punchline after its evidence, which is where a
punchline belongs. It loses to the research — every published aggregate is a lead, not a close — and
to arithmetic: two optional objects instead of one, two macros, two budget lines, on a page with five
spare lines.

**The aggregate as the last Bullet.** It keeps `0027` §6 honest without effort, because the bank would
hold an aggregate Claim for it to cite, and only the opening end would need a macro. It loses on
asymmetry: one end of the frame would be furniture and the other would compete for a slot, so the
frame would be two different kinds of object and the sum could lose its line while the situation kept
one.

**Generalising `0030` §2's threshold to each line's own cap minus 15.** The consistent move once the
lead joins the rule, and it is what the constant always meant. It loses because the lead does not join
the rule (§7): with the lead exempt there is nothing to generalise, `SPREAD_SLACK` need not exist, and
`0030` §2 is left exactly as written. A constant not introduced is a constant not maintained.

**Composing the situation from the entry's Evidence at compose time.** It costs no ingest work and no
schema change, and the shared condition is usually visible across the Claims. It is `0010`'s refusal
in its plainest form: the model reading its own material and forming a judgement about the maker's
history, printed on a résumé as a statement of fact.

**Reusing the highest-scoring Claim's Evidence as the lead.** Zero cost of any kind. It abandons the
map's destination — the combined figure has nowhere to live — and it reports the entry's condition as
one Claim's situation, which is the fidelity fault §1 rejected the in-Bullet option over.

## Consequences

- **An Entry is a header, an optional lead line, and Bullets.** The lead is a fourth kind of thing on
  the page, after Bullets, Skills rows and the static furniture `0031` settled.
- **`0004`'s Entry schema gains an optional `## lead` block** with `situation:`, `aggregate:`,
  `number:` and `provenance:`. `bankcheck.py` parses and validates it; a lead with a `number:` and no
  `aggregate:` is a schema error.
- **`0027` §2 loses its prohibition and keeps its floor.** §6 is untouched by this ADR — merging is
  what breaks it, and that is #74's.
- **`0030` is untouched.** §2 and §3 read *Bullets*, which they already did; §4's *anywhere in
  `bullets.md`* already covers the lead. No constant moves, and `SPREAD_SLACK` is not created.
- **`config.py` gains `LEAD_LINES = 1` and a measured `LEAD_CHARS`.** The template is edited, so the
  blob hash moves **and a re-measure is owed** — unlike `0031` §8, this adds a macro with real
  geometry. `docs/calibration.md` runs before `#78` closes.
- **`pack.py`'s reservation minimum becomes `ENTRY_HEADER_LINES + LEAD_LINES + 1`** for an Entry with
  a lead. The Packer learns whether an Entry has one from `scores.md`, which is the only file it may
  read (`0006`); how that field reaches the table is #75's, which this ADR has otherwise shrunk to
  almost nothing.
- **`render.py` gains three checks on the lead** and none of `0030`'s three.
- **`ingest` gains two questions per entry** and the bank gains a migration through the Return door
  (`0016`), both #76's to specify.
- **The Omission view is unchanged.** The lead never competes, so it can never be an omission.
- **#75 has almost nothing left to decide.** Both ends of the arc left the column, so the middle is
  ordered by score exactly as it is today.
