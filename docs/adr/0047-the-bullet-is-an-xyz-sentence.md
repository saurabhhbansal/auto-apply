# The Bullet is an XYZ sentence, and it is charged two lines

**Status:** accepted

## Context

The maker brought in an external résumé skill and asked for its bullet-writing method
to be adopted **as the method**, not derived from or blended with the one already
here: *accomplished [X], as measured by [Y], by doing [Z]* — Laszlo Bock, LinkedIn,
September 2014, later folded into *Work Rules!*.

`docs/research/bullet-frameworks.md` surveyed this family for #71 and recommended the
opposite of what is decided below — *"Take XYZ's ordering, not its formula"* — on the
ground that Bock's own showcase example is **186 characters** against this template's
**99**, and that a three-slot formula at 99 characters reproduces the compression
fault `0027` §1 was written against.

**The maker was shown that finding, with the measurement, and chose the formula
anyway, with the page cost stated.** This ADR records that choice and what it costs.
It is a reversal of a recommendation this repo commissioned, not an oversight of it.

### The measurement that makes it affordable

The survey's objection assumed a one-line Bullet. This template already typesets a
**two-line Bullet at 198 characters** (`2 × CHARS_PER_BULLET`), granted today by
`grant_widths` out of leftover room. **186 fits inside 198.**

So XYZ does not need a wider line, a smaller font or a different template. It needs
the second line to stop being a *want* and start being the *charge*. That is a change
to `pack.py`'s economics and to nothing in `templates/resume.tex.j2` — the blob hash
in `tools/config.py` stays valid, every measured constant holds, and no recalibration
is owed.

### What it costs, measured before deciding

`runs/auxo-ai` seats **16 Bullets in 18 Bullet-lines**. With every unit charged two
lines that page seats **9**.

## Decision

### 1. A Bullet is composed as X, Y, Z

**Impact first, the measure attached to it, the method last.** The change the work
produced opens the sentence; the figure that sizes it rides with it; how it was done
closes it.

> *Cut checkout p99 latency 40% by batching offset commits in the Go Kafka order-ingest consumer*

This **supersedes `0027` §2's "No house shape"** for the Bullet. That section is
reversed, not narrowed, and the reversal is recorded in an Addendum there.

Worth stating plainly, because it changes what this project is doing rather than only
what it produces: `0027` §2 was **this repo's own aesthetic position, held against the
style authorities**. The survey found Purdue OWL (*"each bullet must be in parallel
form"*) and the Microsoft Writing Style Guide (*"make all the items in a list
consistent in structure"*) both **mandate** what `0027` §2 forbade. A house shape moves
this page toward the documented convention. `0027` §2's live half — *do not open two
Bullets on the same word* — is untouched and is enforced by `render.py` as before.

### 2. Y is composed only where the Claim carries a figure

The formula mandates a measure. The bank does not always hold one, and **rule 2
outranks the formula everywhere the two meet**.

- A Claim with a stored `number:` composes X, Y and Z.
- A Claim with no figure composes **X and Z, and no Y**. It does not grow one, does
  not borrow a neighbouring claim's, and does not reach for a figure the Evidence
  merely implies.
- The absence is a signal, not a defect in the line: it is a Coverage-gap
  Notification at the Checkpoint and a `bank-audit` finding, exactly as it was.

**A missing Y never justifies an invented one.** This is the single way this decision
can go wrong, and it is the failure the maker would have to defend in the room.

### 3. A Bullet is charged its declared width, and the default is 2

The inversion, stated exactly:

| | today | from here |
|---|---|---|
| reservation | `HEADER + LEAD + 1` | `HEADER + LEAD + <the reserved unit's width>` |
| distribution | `1` for a non-merge unit, its declared width for a merge | **its declared width, for every unit** |
| `grant_widths` | raises non-merge units to 2 out of the residue | **grants nothing to a non-merge unit** |
| `width` in `scores.md` | a **want** the Packer may refuse | a **charge** the Packer honours |

**`width: 1` survives and is the load-bearing declaration.** It says: *this claim's
complete XYZ sentence finishes inside 99 characters.* The example in §1 is 93
characters and carries all three slots. Lean claims still cost one line, so a page
does not collapse to a fixed nine Bullets — how many it holds is a function of the
bank, which is the right thing for it to be a function of.

**The reserved slot no longer excludes a `width: 2` merge group.** `0035` §3–4 excluded
it because the guaranteed line was one line and a two-line group could not occupy it.
The guaranteed slot is now the reserved unit's own width, so the exclusion has nothing
left to do and is removed.

### 4. This moves a judgement from the Packer to the scorer, deliberately

Under `0025` §6 the width was a want and the arithmetic could refuse it, which is why
rule 1 (*you judge relevance; the scripts own the arithmetic*) held cleanly. From here
the declared width **is** a charge, so a scorer that declares 2 everywhere shrinks its
own page.

That is not a loophole to be closed with a cap. It is the same discipline the Fit
rubric already runs on — *score against the rubric, never relative to other claims* —
applied to width, and it fails the same visible way: the Omission view gets long, and
the maker reads it. `0024`'s cap and the Entry floor are unchanged and still bound the
page from the other end.

### 5. The spread rule is retained, not deleted

`0030` §2 — on a page of six or more one-line Bullets, one in three must land at or
below `CHARS_PER_BULLET − 15` — is written for one-line Bullets and explicitly exempts
two-line ones. On a mostly-two-line page it will rarely fire.

**It stays exactly as written.** It now binds the `width: 1` Bullets, which are the
ones most at risk of being written to the cap, because a claim declared at one line has
already asserted its sentence finishes early. Deleting a check because the common case
stopped reaching it would remove it from the case it now describes best.

## Consequences

- **Fewer Bullets on every page, and a much longer Omission view.** This is a
  selection event in `tools/config.py`'s sense — it changes which evidence reaches the
  page — even though it moves no constant in that file.
- **A thin bank is now more visible, not less.** An entry whose claims are all
  qualitative composes X–Z lines with no figures at two lines each, which reads as
  spending the page's most expensive real estate to say less. That is a true report of
  the bank's state and the fix is `ingest`, never a composed number.
- **`git diff` across a re-run of the three committed runs will be total.** Expected;
  the runs are records of what was true at the time, and re-running them is how the
  cost of this decision gets read rather than argued about.
- **No template change, no recalibration, no constant moved.**
- **`0025` and `0027` each gain an Addendum** recording what this reversed.
