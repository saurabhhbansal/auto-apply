# The Renderer checks the Skills section against what the budget charged

**Status:** accepted

## Context

`0021` §5 decided that the composed Skills rows reach the Packer as an **argument** —
`--skills-rows 1,2,1,1` — rather than as a file it reads. That decision is right and is not
reopened here: the Packer reads exactly one file, `scores.md`, and that is what keeps it
bank-blind and on the arithmetic side of the seam. Reading `bullets.md` would have it parsing
composed prose and citations, which is the thing it exists not to know about.

But an argument is typed, and typed by hand. Nothing connects the number the Packer spent to the
section that is about to typeset. Every other input to the budget is tied down:

- the Bullets, by `check_structure` — *"no extra Bullet, no unfilled slot, in the Packer's page
  order"*, because *"an extra Bullet spends a line the budget never granted"*;
- the Education rows, by `render.py` importing `pack.EDUCATION_ROWS` and comparing it against the
  rows it is about to typeset, since the Packer cannot count them;
- everything else, by being a measurement of the template.

The Skills section, after `0021`, was the one thing on the page whose charge nothing checked.

### What that costs when it goes wrong

Two failure modes, and the first is the expensive one.

**Under-charged** — a stale `--skills-rows`, or the flag forgotten entirely so the reservation is
rendered. The page is budgeted for less than it holds, so a Bullet the allocation granted has
nowhere to go and the PDF runs to two pages. That surfaces at `render.py`'s page-count assert,
whose message is deliberately certain:

> the **Page-budget constants** in `tools/config.py` are miscalibrated against
> `templates/resume.tex.j2`. Re-run the procedure in `docs/calibration.md` …

The certainty was earned honestly — every Bullet passed the length lint and the header fitted, so
at the time that message was written nothing else *could* have caused it. `0021` added something
that can, and the message now sends the maker off to re-measure a template that is fine. A wrong
answer delivered confidently is worse than no answer.

**Over-charged** — the section is billed for lines it does not use, and evidence is left off the
page for room nobody spent. Silent, and it looks like an ordinary allocation.

The forgotten-flag case is not hypothetical. `tailor` §3 is now three steps where it was one, and
the reservation is a complete, well-formed `allocation.md` that renders without complaint.

## Decision

### 1. `allocation.md` carries a machine-readable `Skills:` line

Three forms, one per state the second pass can leave the section in:

```
Skills: 4 row(s), 1,2,1,1 typeset line(s) each, charged 6 line(s) including the heading.
Skills: no section — 0 composed row(s) is under the 2-row floor, so the section goes …
Skills: 4 row(s) reserved at one typeset line each, charged 5 line(s) … This is a RESERVATION …
```

It is also the line a person reads to see what the section cost, which is why it sits in the
budget paragraph rather than in a comment.

### 2. The Renderer refuses a reservation

Pass one's allocation is a budget for four rows nobody composed. Rendering it puts a page on paper
that was costed against a guess, and the failure names the command that fixes it.

### 3. The Renderer refuses a section the allocation did not charge for

`render.py` recomputes each composed row's typeset line count with its own formula and compares
the list against the one `allocation.md` records. A mismatch is a hard failure naming both shapes
and quoting the `--skills-rows` argument that would be correct.

It runs inside `check_structure`, beside the Bullets-match-the-allocation check, because it is the
same claim about the same thing: **the page is exactly what the budget was charged for.**

**One deferral.** If a composed row exceeds `MAX_ROW_LINES`, this check returns without failing.
Such a row has no legal allocation — the Packer refuses to be told about one — so quoting
`--skills-rows 3,1` back at the maker would send them to a command that rejects the argument. The
length lint two steps later says the useful thing instead: *drop the skills this JD leans on
least*.

## The cost, stated rather than waved past

**`parse_allocation` reads only the two machine-written shapes on purpose.** Its docstring says
why:

> `allocation.md` is a document for a person that a script also reads, and tightening this to
> reject prose would make every wording change a breakage.

The `Skills:` line is now **the first line of `allocation.md` whose wording `render.py` depends
on.** Reword it in `pack.py` and the Renderer stops reading it. That is a real narrowing of a
property the file was designed to have, and it is accepted here rather than explained away.

Three things bound it:

- **It is one line, and it is anchored.** The regexes match `^Skills: ` and the two shapes after
  it; the prose around them is still free.
- **It fails loudly, not silently.** A wording change that breaks the parse raises *"no `Skills:`
  line — this is not an allocation.md written by tools/pack.py"*, which names the cause.
- **`tests/test_render.py` writes the line by hand**, so a change to `pack.py`'s wording that the
  Renderer cannot read fails the suite rather than the next real run.

## Rejected

**Leave it unchecked.** The status quo, and the reason this ADR exists. It trades a loud failure
for a confident wrong answer at the page-count assert.

**Have `pack.py` recompute the rows from `bullets.md`.** Directly against `0021` §5, and against
the seam: the Packer would be parsing composed prose and citations.

**A second, machine-only file carrying the shape.** A derived copy of something `allocation.md`
already states — *"a second derived copy rots on every hand-edit"* is `0005`'s rejection of the
same shape, and `0006` refuses *"two representations of one fact"* at the artifact layer for the
same reason. Two copies of a number is how they come to disagree.

**A checksum or an opaque token instead of the readable line.** Tighter to parse and impossible to
reword by accident — and it puts a field in a document for a person that the person cannot read.
The line as written does both jobs.

## Consequences

- **`render.py` gains `parse_allocation_skills` and `check_skills_allocation`**, and
  `PageContents` gains an `allocated_skill_rows` field. Roughly forty lines.
- **The forgotten second pass is now a named failure** rather than a two-page PDF blamed on the
  constants. `tailor` §6 lists both new failures with what to do about them.
- **`pack.py`'s `Skills:` wording is contract.** Changing it means changing the two regexes in
  `render.py` and the fixture in `tests/test_render.py` — and the suite says so on the way past.
- **The page-count assert's message is trustworthy again.** By the time it can fire, the Bullets,
  the Education rows and the Skills section have all been checked against what was charged, so
  "the constants are miscalibrated" is once more the only thing left.
- **This ADR extends `0021` and supersedes nothing.** `0021` decided how the row shape reaches the
  Packer; this decides what holds it to the page afterwards. It also amends `0018`'s neighbour,
  `parse_allocation`, in one narrow place — recorded above rather than left in a commit message.
