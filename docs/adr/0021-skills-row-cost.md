# What a Skills category row costs, and what the second pass actually does

**Status:** accepted — **the decision stands, two of its numbers do not.** On
2026-08-10 the Skills list's `itemsep` went from `0pt` to `4pt`, because a row was
setting 2pt tighter than `\small`'s own leading and the skill lines read tighter than
every other line on the page. `SKILLS_ROW_PT` is **14.00pt**, not the 10.00 measured
below, and `docs/calibration.md`'s entry for that date is the measurement.

Two passages here now describe a page that no longer compiles that way, and are left
as written because they are the record of what was decided:

- **§1's headline argument** — *"a row at 0.714 of a line"*, and a 4-row section
  occupying 2.86. A row is exactly one Bullet line now, and `ceil((14n + 12w) / 14)`
  equals `n + w` at every wrap count the two-line cap can reach, so the points
  arithmetic and a per-row round-up agree on every composition that can occur. The
  decision to charge in points stands anyway: it is derived from a measurement, so the
  next template change that moves a row off 14.00pt makes it bite again with nothing
  to re-derive. What §1 rejected — folding the two constants into one line count —
  is still rejected.
- **§4's table.** Four reserved rows cost **6** lines, not 5, and the row of it that
  carried the finding is gone: composing one row fewer than reserved now hands back
  **one line** rather than nothing, because the rounding no longer has a fraction to
  absorb. The rest of §4 is untouched — the pass still settles up in both directions,
  and it still cannot loop.

## Context

Map #34 gave, at charting, that the Packer **reserves four Skills rows and hands the unused ones
back** in a second packing pass. `0020` settled what goes *in* the rows. Both were decided without
anyone compiling the macro, and the reservation arithmetic rested on an assumption nobody had
checked: that a category row's cost is expressible as `N x <one number>`, where the number is a
count of **Bullet lines**.

Issue #36 sent that assumption to a prototype
(`prototype/skills-row-cost`, a local throwaway branch
not published with this repo). It patches `0020`'s skills block into the template source in memory,
imports `tests/calibration/probe.py` rather than forking it, and measures two ways: typeset height
in points by whole-page differential, and whole lines by the same geometric overflow criterion
`docs/calibration.md` uses for `PAGE_LINES`.

### What it measured

A row is **10.00pt** — `0.714` of a 14.00pt Bullet line. Rows two through six are uniform to
within **0.00pt**: `\small`'s 12pt leading less `\resumeItem`'s `\vspace{-2pt}`, with
`\resumeSkillsListStart`'s zeroed glue contributing nothing.

So `N x <one number>` is **true in points and false in lines**. That distinction is the whole
ticket: handing back "one row" hands back 0.714 of a line, and 0.714 of a line is not a thing the
page budget can give to a Bullet.

### What the maker decided, looking at the compiled page

The prototype rendered a stress page — a two-skill row, a row near the character budget, a row
deliberately past it, and the long-label case. On seeing it the maker made two calls that the
measurement could not make:

- **A row may wrap.** `0020` §6's fit formula was written to *prevent* a second line; it now
  *predicts* one.
- **Never past two lines.** A row that would run to three sheds skills instead.

That turns a row's height into a function of its **content** rather than of the macro. Measured on
a ladder:

| characters of skills | typeset lines | measured |
|---|---|---|
| 18 | 1 | 10.00pt |
| 103 | 2 | 22.00pt |
| 184 | 2 | 22.00pt |
| 286 | 3 | 34.00pt |

**10.00pt for the first line, 12.00pt for each one after** — the second line pays `\small`'s full
leading, because `\vspace{-2pt}` is charged once per row and not once per line.

## Decision

### 1. Two measured constants in `config.py`, and one stated exception to its rounding rule

```python
SKILLS_ROW_PT = 10.00        # a category row's first typeset line
SKILLS_ROW_WRAP_PT = 12.00   # each typeset line after the first
```

These are measurements of the template, and re-measuring them is `docs/calibration.md`'s job, so
they belong beside the other five rather than in `pack.py` next to `SKILLS_LINES`. `SKILLS_LINES`
sits in `pack.py` because charging the old breadth list one line was the *Packer spending* a
measurement; these are the measurement itself.

They do not obey `config.py`'s stated unit rule — *"that element's typeset height divided by
14.00pt and rounded UP"* — and the docstring has to say why:

> A Skills row is the first element that is **never charged alone**. The section charges N of them
> at once, so the rounding happens once, at the sum. Rounding each row up on its own would charge
> 4 lines for a 4-row section that occupies 2.86.

**Rejected:** a single `SKILLS_ROW_LINES = Fraction(5, 7)`. It hides that the first line and the
later ones cost different amounts, which is exactly the fact the wrap decision made load-bearing.

**Rejected:** keeping both numbers in `pack.py`. A number that moves when the template moves cannot
live outside the file the calibration procedure writes, or the next geometry change silently leaves
it stale — which is the whole argument `config.py`'s docstring already makes.

This is the seventh and eighth name. `0020` spent the sixth on `BOLD_CHARS_PER_BULLET`, and
`config.py`'s *"a sixth constant has nowhere to live"* remark is aimed at **splitting**
`ENTRY_HEADER_LINES` so a macro can stop measuring under it — not at charging genuinely new
elements that no existing constant describes.

### 2. The section is charged `ceil(section points / 14pt)`

```
section points = sum over rows of (SKILLS_ROW_PT + SKILLS_ROW_WRAP_PT x (lines - 1))
charge         = ceil(section points / 14) + SECTION_LINES
```

Checked against real page capacity on five résumé shapes at every wrap count from none to all four
— 40 measured cells. **Worst slack +0**, never negative.

| composed | section points | charged, heading included |
|---|---|---|
| 4 rows, none wrap | 40.00 | 5 |
| 4 rows, 1 wraps | 52.00 | 6 |
| 4 rows, 2 wrap | 64.00 | 7 |
| 4 rows, 3 wrap | 76.00 | 8 |
| 4 rows, all wrap | 88.00 | 9 |

**Rejected: one line per row, the charting assumption.** It **over-promises by up to three lines**
as soon as rows wrap — measured, on three of the five shapes. This is not a conservative
simplification that costs a little whitespace; it is a two-page PDF, surfacing at `render.py`'s
page-count assert and blaming the template.

**Rejected: the sum of typeset lines.** It holds at worst slack +0 and needs no points, which is
genuinely simpler. It over-charges by up to two lines on a wrapping section, and two lines is two
Bullets of evidence — the same magnitude of loss the `\resumeEducationRow` split in #31 was worth
making to reclaim.

### 3. A row wraps to at most two lines, and the formula decides before the compile

`0020` §6's formula generalises from a yes/no to a count:

```
lines = ceil( (len(label) + 2) / BOLD_CHARS_PER_BULLET  +  len(text) / CHARS_PER_BULLET )
```

A row whose `lines` exceeds 2 **sheds skills until it does not**, lowest JD-prominence first — the
same truncation `0020` already describes, at a budget of two rows' worth of characters rather than
one.

**The direction of error is the point.** Both character rates are worst-case — the widest realistic
label at 83 characters, the widest realistic prose at 103 — so the predicted width is never under
the real one, so the predicted line count is never under the real one. The prototype's 286-character
row is predicted at 4 lines and typesets at 3. That costs a skill that would have fitted, and it is
the right way round: a formula that under-counted would hand the Packer a budget promising a line
the page does not have, and nothing downstream would catch it before the page-count assert.

### 4. The second pass is a **reconcile**, not a hand-back

The charted phrase does not describe what happens. Under the charge in §2, reserving four
single-line rows costs 5 lines, and then:

| composed | costs | pass two |
|---|---|---|
| section dropped (under `0020`'s two-row floor) | 0 | hands back **5** |
| 2 rows, neither wraps | 4 | hands back **1** |
| 3 rows, none wrap | 5 | **nothing** |
| 4 rows, none wrap | 5 | **nothing** |
| 4 rows, 1 wraps | 6 | **takes 1** |
| 4 rows, all wrap | 9 | **takes 4** |

Two things follow, and neither was visible at charting. **Composing one row fewer than reserved
hands back nothing** — the rounding absorbs it, and only dropping to two rows or dropping the
section moves a line. And **the pass can take lines as well as give them**, which "hand the unused
ones back" cannot express.

So the reservation stays **optimistic** — four rows at one line each — and pass two settles up in
whichever direction the composition landed.

**Rejected: reserving the worst case (9 lines).** It would permanently spend four lines of evidence
defending against a shape `0020` establishes is rare: four skills plus a label runs about 90
characters against a 103-character budget, and on `runs/zs-btsa` nothing would have wrapped at all.

**It cannot loop.** Pass two's budget differs from pass one's, but the rows are already composed and
a budget cannot change them, so there is no second reconcile to run. The pass executes exactly once
in each direction. This is the same argument the charting made for the hand-back; it survives the
sign change unaltered.

### 5. The row cost reaches the Packer as an argument, not a second file

```sh
python tools/pack.py runs/<jd-slug> --skills-rows 1,2,1,1
```

One integer per composed row: its typeset line count. `pack.py` still **reads exactly one file**,
`scores.md`, which is what keeps it bank-blind and on the arithmetic side of the seam. Pass one is
the same command with `--skills-rows` omitted, which means *reserve four single-line rows*.

**Rejected: reading `bullets.md`.** It carries composed prose and citations — the judgement side of
the seam — and the Packer would then be parsing the thing it exists not to know about.

The argument carries a judgement, which is unavoidable: *which* skills got categorised into *which*
rows is Opus's call. What the Packer receives is that judgement already reduced to arithmetic.

### 6. `allocation.md` records the final pass, plus one Silent call for the reconcile

Not both passes. `allocation.md` is *"the document a person checks the PDF against"*, and a file
showing two allocations does not say which one the PDF is.

The reconcile gets a **Silent call** line, since it is a call made by rule rather than by score:

```
- Skills reconcile: reserved 5 line(s) for 4 rows; the composed section cost 6
  (4 rows, 1 wrapping), so 1 line came off the page
```

The **Omission view is the final pass's**, which keeps its guarantee exact: everything that lost is
listed, once, against the allocation that actually shipped. A claim that held a slot in pass one and
lost it in pass two appears there like any other loss — its history is in the Silent call above,
which names the reconcile as the reason the budget moved.

### 7. A dropped row and a dropped section are the existing Gap class

The sixth question this ticket inherited from `0020`: *when a row is dropped rather than truncated,
what does the Gap report say?*

**Nothing new.** A row that falls under two skills, and a section that falls under two rows, are both
*skills the maker has that the page did not show* — the existing **you have it, the page did not**
class, which explicitly covers *"nothing to fix in the bank"*. A new class would tell the maker to go
do something, and there is nothing to do: the skills were traced, scored and beaten by the page.

## Consequences

- **`docs/calibration.md` gains a probe** for the two row constants and for the bold character rate
  `0020` asked for, and its constants table grows from five rows to eight. The prototype's
  measurement functions lift into `tests/calibration/probe.py` largely as they stand.
- **The probe gains a check**, in the spirit of the two it already has: *the Skills section's charge
  is never below its measured capacity, at every wrap count*. The wrap-blind charge failed exactly
  this and would have shipped.
- **`tools/pack.py` grows a second entry point** — `--skills-rows` — and `bullet_budget` stops
  charging `SKILLS_LINES = 1`. That constant retires.
- **`tools/lengths.py` reports one figure per row**, already required by `0020`, and now also flags a
  row predicted over two lines.
- **The `tailor` skill runs `pack.py` twice**, with the skills composed between the two, and shows
  the Checkpoint only after the second. The Angle statement and the Omission view describe the page
  that will render.
- **Material determinism holds, and gets more sensitive.** Selection is still a function of the bank
  and the JD alone: the composed rows are themselves a function of those two, so nothing enters the
  loop from outside, and the `scores.md` cross-run diff argument and **the bank is the only repair
  surface** both still read true — `scores.md` is written before either pass and neither pass
  touches it. What changes is the *coupling*: a skill name one character longer can wrap a row, cost
  the page a line, and drop an Entry. `0020`'s finding that truncation stops being the binding
  constraint is what keeps this rare rather than routine, and the two-line cap bounds the worst case
  at four lines. **This is a real narrowing of the guarantee's comfort, recorded rather than
  explained away.**
- **This ADR extends `0020` and supersedes nothing.** It settles the arithmetic `0020` deferred and
  corrects one thing the charting of #34 assumed — that pass two only ever gives lines back.
