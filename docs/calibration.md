# Calibrating the page-budget constants

`tools/config.py` holds the numbers that decide how much evidence fits on one
page. They are **measured against the compiled template, never estimated**. This
is the procedure that measures them, and the reasoning you need to judge the
output.

Re-run it **whenever `templates/resume.tex.j2` changes** its geometry, fonts,
margins or macros — and commit any change to the constants **on its own**. A
different `PAGE_LINES` means different claims win slots, so a constant change is a
selection event, not a layout tweak.

## What the constants mean

The unit is **one rendered Bullet line** — 14.00pt on the current template. Every
other cost is that element's real typeset height in the same unit.

| Constant | What it charges for |
|---|---|
| `BULLET_LINE_PT` | One rendered Bullet line, in points — the unit the rest are in |
| `PAGE_LINES` | Bullet-line-equivalents the whole page holds, overhead included |
| `HEADER_LINES` | The Static profile header: name plus the contact/links line |
| `SECTION_LINES` | One section heading and its rule — five call sites, and the Summary's is the one with no condition on it |
| `ENTRY_HEADER_LINES` | One job's Entry header — and one Education row, which has its own macro but is charged the same |
| `PROJECT_HEADER_LINES` | One project's header — a single row: name, stack, link and dates (`docs/adr/0057-the-page-reads-like-a-resume.md` §3) |
| `CHARS_PER_BULLET` | Characters of plain prose that fit on one Bullet line |
| `BOLD_CHARS_PER_BULLET` | The same count in **bold**, which charges a Skills row's label |
| `SKILLS_ROW_PT` | A Skills category row's first typeset line, **in points** — the list glue rides here |
| `SKILLS_ROW_WRAP_PT` | Each typeset line after the first, **in points** |
| `LEAD_LINES` | The entry arc's lead line — fixed at 1 by decision, not derived |
| `LEAD_CHARS` | Characters of plain prose that fit on the lead's one line |
| `SUMMARY_LINES` | The Summary's prose — fixed at 2 by decision, not derived; its heading is charged `SECTION_LINES` on top |
| `SUMMARY_CHARS` | Characters of plain prose that fit in those two lines |

The budget the Packer spends is `PAGE_LINES` minus the fixed overhead:

```
overhead = HEADER_LINES
         + SUMMARY_LINES      <- every page carries one; see below
         + SECTION_LINES      <- \section{Summary}, on every page, for the same reason
         + SECTION_LINES      x (Experience? + Projects? + Education?)
         + ENTRY_HEADER_LINES x (placed jobs + Education rows)
         + PROJECT_HEADER_LINES x placed projects
         + the Skills section  <- its own heading included; see below
```

**The Skills section is charged as a whole, in points.**

```
row lines      = ceil( (len(label) + 2) / BOLD_CHARS_PER_BULLET
                       + len(skills)    / CHARS_PER_BULLET )
section points = sum over rows of (SKILLS_ROW_PT + SKILLS_ROW_WRAP_PT x (lines - 1))
charge         = ceil(section points / BULLET_LINE_PT) + SECTION_LINES
```

That is the one place the "round each element up" rule does not apply, and it is
**never charged alone** — the section charges N rows at once, so the rounding happens
once, at the sum. Below two rows the section is not a section: its heading costs
`SECTION_LINES`, so one surviving row spends three lines of page to show one, and the
whole thing goes instead. See `docs/adr/0021-skills-row-cost.md`.

**At today's two numbers the exception buys nothing, and that is a fact about the
numbers rather than about the design.** It was written when a row measured 10.00pt —
0.714 of a Bullet line, so a 4-row section occupied 2.86 and rounding each row up
would have charged 4. A row is 14.00pt now, and `ceil((14n + 12w) / 14)` equals
`n + w` for every wrap count the two-line cap can reach. The sum-rounding and the
per-row rounding agree on every composition that can occur. It stays because this is a
measurement pipeline: the next template change that moves a row off 14.00pt makes the
exception bite again, with nothing to re-derive. What would be wrong is folding the two
constants into one line count, which `0021` §1 explicitly rejected.

**A supporting section is charged the same way, out of the same constant.**
Certifications, Positions of Responsibility and Extracurriculars are on the page only
when the posting calls for them or the width pass leaves room, and each of their rows
is the same element as a Skills row — `\resumeItem` with a bold label, in the same
list geometry:

```
charge = ceil(SKILLS_ROW_PT x rows / BULLET_LINE_PT) + SECTION_LINES
```

1 row costs 3 lines, 2 costs 4, 3 costs 5, 4 costs 6. `SKILLS_ROW_WRAP_PT` never
appears because **a supporting row is capped at one typeset line** — which is what
lets the charge be a function of a row count rather than of composed text, and why
these sections need no second Packer pass. There is deliberately **no constant of
their own**: what `config.py` may never gain is a second name for an element already
charged, so the probe carries the check instead — *a supporting row costs the same as
a Skills row*, beside *an Education row costs the same lines as an Entry header*. If
it fails, tighten a macro. See
`docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md` §6.

**The Summary is charged unconditionally, and it is the one element whose character
budget is not a rate.** Every page carries one — the Packer runs before a word is
composed and cannot see whether it arrived, so `SUMMARY_LINES` comes off the budget
whatever happens (`docs/adr/0044-the-page-opens-on-a-summary.md` §5), and since that
ADR's Addendum a flat `SECTION_LINES` for its heading comes off beside it. Like
`LEAD_LINES` it is fixed by decision rather than derived, and like `LEAD_LINES` the
probe still prices the element and fails loudly if it exceeds what it is charged.

**What it prices is the heading and the prose together, because neither is separately
priceable.** `\section` contributes its space through `\addvspace`, which *merges*
with the skip already on the vertical list rather than adding to it — so the glue
between a heading and what follows it belongs to neither on its own. Cut only the
prose and `\section{Summary}` welds to `\section{Experience}`, where the two headings'
skips merge and the differential reads 38.00pt for a block nowhere near that; cut only
the heading and the prose lands on the header's glue instead. So `SUMMARY_BLOCK`
removes the pair: the section measures **54.39pt against (2 + 2) x 14.00 = 56.00pt**,
which is also exactly what the budget spends on it.

`SUMMARY_CHARS` is measured differently from every other character count here, and
the difference is that it bounds **two** lines. For a one-line element, *how many
characters fit* and *how many typeset lines is this* are the same question, so a
worst-case pt/char and a division answer it. A paragraph breaks at word boundaries,
and that division assumes a first line filled to the last scaled point — which comes
out about a word generous (**231 predicted against the 227 that actually fit**, same
sample, same width). So the probe boxes **every word-prefix of every sample** in a
`\parbox` at the Summary's real `\linewidth` and takes the longest that measures
inside the ceiling, worst sample winning as everywhere else. The tape and the runtime
gate then measure one quantity by construction.

**A Bullet may take two typeset lines, and it is charged two.** The Packer grants a
slot a width of 1 or 2 and spends the integer; there is no constant for the second
line's real height, because nothing would ever spend one. The measurement is here as
a fact instead: **a Bullet's second typeset line is 12.00pt**, the same number as
`SKILLS_ROW_WRAP_PT` and for the same reason — a line *inside* an item pays `\small`'s
plain leading, while the item's first line also pays the list's inter-item glue. So a
two-line Bullet measures **26.00pt against the 28.00pt it is charged**: it over-charges
by 2.00pt and never under-promises, which is the only direction this file allows. A
Skills row's first line is the same 14.00pt as a Bullet's, and since 2026-08-10 that is
not a coincidence — see that date's entry below. See `docs/adr/0025-bullet-wrap-cost.md`.

Six assumptions are checked on every run of the probe rather than asserted here:
an Education row costs exactly `ENTRY_HEADER_LINES`; **a two-line Bullet costs no
more than two Bullet lines**; one more Skills row always costs the same; the
row-lines formula above never *under*-counts what TeX actually typeset; **the Summary
and its heading cost no more than the four lines charged**; and **the Summary-fit ceiling
separates a two-line Summary from a three-line one**, which is what makes
`render.py`'s gate a gate rather than a number that always passes. The first
three have to hold, because splitting a constant in two so one macro can stop
measuring under it would let the pair drift apart silently — if any fails the fix is
to **tighten the template**. The last is the direction of error that matters:
over-counting costs a skill that would have fitted, while under-counting hands the
Packer a budget promising a line the page does not have.

The wrapped-Bullet check is the one with no constant behind it at all, which is what
makes it load-bearing: if a font or margin change pushed that second line past
14.00pt, charging 2 would begin over-promising and the only symptom would be a
two-page PDF blaming the constants. It also asserts that its 202-character sample
*did* wrap, since a check measuring a one-line Bullet would pass while measuring
nothing.

The Education check earns its keep: an Education row is typeset by its own
`\resumeEducationRow` macro rather than by the `\resumeSubheading` an Entry header
uses, so nothing but that check keeps the two in step.

`HEADER_LINES` rests on a third assumption of the same kind — that the name and
the contact/links line each fit on **one** typeset line. That one is not the
probe's to hold, because it is a fact about the maker's `bank/profile.md` rather
than about the template, and it is silent: a centred line breaks legally, so a
wrapped header costs 12pt or 23pt and LaTeX says nothing. The **Header-fit check**
in `tools/render.py` enforces it on every run
(`docs/adr/0017-header-fit-check.md`). It is why the number below stays 3 rather
than being raised to cover a wrap, and why no sixth constant was needed.

## Running it

Prerequisite: `pdflatex` on `PATH`, from TinyTeX or a full TeX Live. On a machine
without it, install TinyTeX:

```sh
curl -sL https://yihui.org/tinytex/install-bin-unix.sh | sh
tlmgr install preprint titlesec marvosym enumitem hyperref fancyhdr babel-english
```

Then:

```sh
python tests/calibration/probe.py           # measure and print the report
python tests/calibration/probe.py --keep    # also leave the PDFs in out/ to look at
```

It exits non-zero if the constants it derives do not hold. Copy the derived values
into `tools/config.py`, update the "Last calibrated" line, and commit.

The probe lives under `tests/` rather than `tools/` because it is development
machinery, like pytest — the running system's tools are exactly `config.py`,
`pack.py`, `bank.py` and `render.py`. It does not import `render.py` either:
calibration has to isolate the template, so a bug in escaping or in the lints must
not be able to move a constant.

## How each number is measured

**One Bullet line, and the interior elements.** Every measurement rides inside a
Bullet hole, so the template is never edited or spliced to be measured. A probe
Bullet carries `\typeout{...\the\pagetotal}`; `\pagetotal` is TeX's running height
of the current page, so the gap between two markers is the real typeset height of
whatever sits between them. One synthetic résumé — two jobs then one project —
puts a marker on either side of each element that needs measuring.

Two traps in reading those numbers, both found the hard way:

- **The first gap in an entry is bigger than the rest.** `\pagetotal` is read as
  the item's line is contributed, and the list's top glue lands between the first
  and second readings. So the Bullet height comes from the *interior* gaps, and
  that glue is charged to `ENTRY_HEADER_LINES`, where it belongs.
- **`\pagetotal` is meaningless at the bottom of the page.** By the time a marker
  in the last element fires, the page has been shipped out and the reading refers
  to somewhere else entirely — it will happily report 813pt of content on a 722pt
  page. So the Skills line and the Education rows, which have nothing after them,
  are measured by overflow instead (below).

**`CHARS_PER_BULLET`.** `\sbox` gives the exact typeset width of a real sentence at
the template's font and size, so this is measured rather than assumed. Six
realistic résumé bullets are measured and the **widest** wins — the lint is a
character count, and it has to hold for whichever Bullet Opus actually writes.

What is deliberately *not* in that sample set is an adversarial string like
`WWW MMM WWW`. It wins every time and drags the budget down by about 40% — it took
the Letter-width measurement from 103 to 61 — and it
is not English: no Bullet Opus writes looks like that. Calibrating against it would
cost real lines on every résumé to defend against prose nobody will write.

**`BOLD_CHARS_PER_BULLET`.** The same method over `\textbf{<label>:}`, from six
realistic category labels, widest wins. It exists because bold is genuinely wider —
6.056pt per character against 4.915pt plain — so charging a row's label at the plain
rate would predict a narrower line than the one TeX sets, which is the direction
that ends in a two-page PDF. The colon rides inside the bold run; the space after it
is charged at the bold rate too, which is the safe rounding.

**`LEAD_CHARS`.** The same `\sbox` method as `CHARS_PER_BULLET`, widest sample wins,
but measured against the lead's own `\linewidth` rather than a Bullet's — the lead
continues `\resumeSubheading`'s `\item` one list level shallower than a Bullet's
nested itemize, so it typesets wider and reusing `CHARS_PER_BULLET` would under-count.
`LEAD_LINES` is not measured at all — it is fixed at 1 by decision
(`docs/adr/0032-the-entry-arc.md` §4) — but the probe still measures what one lead
line actually costs, by the same whole-page differential `SKILLS_ROW_PT` uses, and
fails loudly if that ever exceeds `BULLET_LINE_PT` by more than half a point.

**`SUMMARY_CHARS`, and the Summary's height.** The character count is measured
directly rather than from a rate, as above. The block's height is a **differential**:
the same page compiled twice, once from the committed template and once from it with
the `\resumeSummary` call site cut out, differenced at the first Bullet's marker.
That is the only honest way to price an element that sits directly under another one
with no gap to put a marker in — a `\pagetotal` reading taken inside the Summary's
own text lands 9.87pt above where its material begins, and charges the glue
`\end{center}` contributes to `HEADER_LINES` instead. The differential attributes
glue the two share to neither, and it is what shows `HEADER_LINES` coming back at
**36.91pt, unmoved**, on a page that now carries a block underneath it.

`SUMMARY_LINES` is not measured at all — fixed at 2 by decision
(`docs/adr/0044-the-page-opens-on-a-summary.md` §1). The differential now cuts the
`\section{Summary}` heading with the prose, for the reason above, so what it prices is
the whole section against `SECTION_LINES + SUMMARY_LINES`.

**`SKILLS_ROW_PT` and `SKILLS_ROW_WRAP_PT`.** Both by whole-page differential, since
the Skills rows sit at the bottom of the page with nothing after them to put a
marker in. The row cost is the marginal difference between documents at 0 through 6
rows; the first difference carries the `\section` heading and is dropped, and the
rest must be uniform or the section's cost stops being a sum over rows.

That it is a **marginal** cost is why the list's `itemsep` lands in `SKILLS_ROW_PT`
rather than anywhere else: `itemsep` is contributed before every row but the first, so
each row *after* the first carries it and the first row's own share is folded into the
dropped heading difference. Every row is then charged the marginal figure, which
over-charges the first row by the `itemsep` and never under-charges anything — the one
direction this document allows.

The wrap cost comes from a ladder of one-row documents at rising character counts,
each differenced against the one-line rung so the heading cancels. The increment is
read as the **smallest positive step** on that ladder, and the other rungs must be
whole multiples of it — which is how each rung's line count comes out of the
measurement rather than out of the character formula the measurement exists to
check.

**`PAGE_LINES`, and the one thing that is easy to get wrong.** The tempting
criterion is "does it still compile to one page". It is the wrong one.

TeX does not break a page the moment content passes `\textheight`. `\raggedbottom`
makes the page box stretchable, the `itemize` glue has shrink in it, and there are
penalties against breaking inside a list — so pdfTeX **compresses the vertical
glue and keeps going**, with no overfull warning to tell you. Measured on this
template, bullets 29 through 35 push the last baseline down by a *total of 5pt*:
six Bullets' worth of material absorbed by squeezing. The PDF is one page, every
line is present, and the leading is visibly tighter than the same résumé one
Bullet shorter. Budget against that cliff and every résumé rides on how much TeX
felt like shrinking.

So the criterion is geometric: **content must leave a bottom margin at least as
large as the top margin.** That is what the eye checks anyway, it is stable, and it
is why the probe reads the last baseline's position out of the PDF.

`PAGE_LINES` is then read off the compiled page rather than computed from
`\textheight`:

```
PAGE_LINES = min over résumé shapes of (measured capacity + that shape's overhead)
```

The minimum is what makes it safe. Each element cost is individually rounded up,
and how much of that rounding is available to absorb the page-level rounding
depends on how many Entries the page holds — so a budget calibrated only on a full
six-entry page over-promises on a two-job one. The sweep includes `(2, 0)` for
exactly that reason.

**Verification.** The probe then re-derives the budget for each shape and compares
it against the measured capacity. **Slack must never be negative.** A negative
number is a budget that promises a line the page does not have, and it surfaces
downstream as a two-page PDF that the page-count assert blames on the template.
Positive slack of a line is the inherent cost of integer line charges and is
reported rather than tuned away.

That sweep varies the *Entry count*. Since a Skills row may wrap, the section's cost
is a function of its content too, so the charge is verified along that axis as well
— every wrap count from none to all four, on the `(2, 0)` shape. That shape has the
least per-Entry rounding slack to absorb the page's own rounding, which makes it the
one that catches an over-promise.

## Re-measured 2026-08-10 — the Skills rows stopped setting tighter than the page

The maker read a compiled page and found the skill lines set closer together than
everything above them. They were: **a Skills row sat 10.00pt below the row above it,
where `\small`'s own leading is 12.00pt and an Experience Bullet keeps 14.00pt from the
Bullet above it.** Measured on the committed template, baseline to baseline:

```
Bullet -> next Bullet      14.00pt
Skills row -> next row     10.00pt      <- 2pt tighter than the type is set for
supporting row -> next     10.00pt
```

**The cause is a `\vspace` meeting the wrong list.** `\resumeItem` carries a
`\vspace{-2pt}`, and it was sized for the stock `itemize` the Bullets sit in, which
contributes 4pt between items — so a Bullet lands at `12 + 4 - 2 = 14.00pt`.
`\resumeSkillsListStart` zeroed its glue, including `itemsep`, which left the `-2pt`
with nothing to come out of: `12 + 0 - 2 = 10.00pt`. The Skills and supporting rows
were the only lines on the page set tighter than their own leading, and the zeroing
that did it was aimed at `topsep` — the ~11pt that would have pushed a one-row section
to two lines of budget — with `itemsep` swept along for free.

**The fix restores 4pt of `itemsep` and nothing else.** `topsep`, `partopsep` and
`parsep` stay at zero, so the section heading's gap and the section's own overhead are
untouched — the probe reads the first row at the same `\pagetotal` before and after.
It is rigid rather than rubber because the calibration reads natural heights, and a
spring here would make a row's cost depend on how hard TeX squeezed the page.

`itemsep=4pt` rather than `2pt`, and the difference is not the budget — **the two cost
the same** at every row count from one to six, since `ceil(12n/14) = ceil(14n/14) = n`.
`2pt` would put a row at `\small`'s bare 12.00pt leading, which fixes the tightness but
leaves a wrapped row's second line the same distance from the row below it as from its
own first line — nothing tells the eye where one row ends. `4pt` gives the Skills rows
the same 14.00/12.00 split the Bullets already have, which is the arrangement that
reads, and it is what the maker asked for: the skill lines match the Experience lines.

**Exactly one constant moved.** `RESULT: constants hold`, `PAGE_LINES` still **53**, and
every other height identical to the scaled point — nothing outside one list's glue
changed.

```
SKILLS_ROW_PT  14.00   (was 10.00)        SKILLS_ROW_WRAP_PT  12.00   (unchanged)

Skills row, first line    14.00pt        Skills row \linewidth   514.40pt (unchanged,
Skills row, each after    12.00pt                                +24.09pt on a Bullet)
supporting row            14.00pt = SKILLS_ROW_PT exactly
```

The ladder that sets the wrap cost, re-measured — the row heights all moved by the one
`itemsep`, and the *increments* between them did not:

| characters of skills | typeset lines | measured |
|---|---|---|
| 18 | 1 | 14.00pt |
| 103 | 2 | 26.00pt |
| 184 | 2 | 26.00pt |
| 286 | 3 | 38.00pt |

**The bill is one line of evidence, charged to every page that carries a Skills
section.** Four rows and their heading cost **6** where they cost 5, and the sweep pays
it on every shape:

| jobs | projects | predicted | actual | slack |
|---|---|---|---|---|
| 2 | 0 | 32 | 33 | +1 |
| 2 | 1 | 28 | 29 | +1 |
| 3 | 1 | 26 | 27 | +1 |
| 3 | 2 | 24 | 25 | +1 |
| 4 | 3 | 20 | 20 | 0 |
| 5 | 2 | 20 | 20 | 0 |
| 6 | 1 | 20 | 20 | 0 |

One line lower than the A4 sweep below, on all seven shapes, and `PAGE_LINES` unmoved —
which is the honest shape of this change. The page did not shrink; the Skills section
grew into it.

The charge across wrap counts, on `(2, 0)`:

| composition | charged | predicted | actual | slack |
|---|---|---|---|---|
| no section | 0 | 38 | 39 | +1 |
| 2 rows | 4 | 34 | 35 | +1 |
| 4 rows, none wrap | 6 | 32 | 33 | +1 |
| 4 rows, 1 wraps | 7 | 31 | 32 | +1 |
| 4 rows, 2 wrap | 8 | 30 | 31 | +1 |
| 4 rows, all wrap | 10 | 28 | 30 | +2 |

All nine sanity checks pass. Two of them are the ones this change was most likely to
break, and neither did: *a supporting row costs the same as a Skills row* now reads
**14.00pt against 14.00** — the two call sites share the list, so they moved together —
and *one more Skills row always costs the same* still measures rows two through six
uniform to **0.00pt**, because a rigid `itemsep` is contributed identically before each
of them.

**What this did retire is `SKILLS_ROW_PT`'s old headline argument.** `0021` §1 justified
charging the section in points with *"a row at 0.714 of a line"*; at 14.00pt a row is
exactly one Bullet line, and `ceil((14n + 12w) / 14)` equals `n + w` for every wrap
count the two-line cap can reach. The points arithmetic and a per-row round-up now agree
on every composition that can occur. The mechanism stays, for the reason given in the
Skills-charge section above: it is derived from a measurement, so the next change that
moves a row off 14.00pt makes it bite again with nothing to re-derive.

## Re-measured 2026-08-10 — the page became A4, and only the widths moved

`\documentclass` went from `letterpaper` to `a4paper`. This is the first change this
document has recorded that touches **neither an element nor a macro**, and the result
reads that way: every measured height came back **identical to the scaled point** —
one Bullet line 14.00pt, an Entry header 27.84pt, a section heading 23.86pt, the
profile header 36.91pt, the Summary block 26.70pt, an Education row 27.28pt, a Skills
row 10.00pt and 12.00pt. An A4 page typesets the same elements; what changed is the
paper under them.

A4 is **17.8pt narrower and 50.1pt taller** than US Letter (595 x 842 against 612 x
792, in PostScript points). The template sets its margins as `\addtolength`s off the
class default rather than absolutely, so the text block moves with the paper: every
width comes down by 16.78pt and `\textheight` goes up by 50.08pt.

```
\textheight              772.78pt   (was 722.70)
Bullet \linewidth        490.31pt   (was 507.09)
Skills row \linewidth    514.40pt   (was 531.18)
Lead \linewidth          514.40pt   (was 531.18)
Summary \linewidth       525.24pt   (was 542.03)
```

So the constants split cleanly by what they are derived from. **Every height-derived
constant is unchanged** — `BULLET_LINE_PT 14.00`, `HEADER_LINES 3`, `SECTION_LINES 2`,
`ENTRY_HEADER_LINES 2`, `SKILLS_ROW_PT 10.00`, `SKILLS_ROW_WRAP_PT 12.00`. **Every
width-derived one came down, and `PAGE_LINES` went up:**

```
CHARS_PER_BULLET       99   (was 103)     BOLD_CHARS_PER_BULLET   80   (was 83)
LEAD_CHARS            114   (was 117)     SUMMARY_CHARS          220   (unchanged)
PAGE_LINES             53   (was 50)
```

`SUMMARY_CHARS` staying at 220 is a coincidence of rounding rather than a fact about
the page: the worst sample's fitting prefix landed on the same word boundary at both
widths. The naive-rate column it is measured against moved as expected — **231
predicted against the 227 that actually fit**, where the Letter measurement read 239.

That is the trade, and it is a good one for this template: **three more lines of page
and four fewer characters per line.** The page is taller by more than it is narrower,
and the sweep says so — every shape gained 2 lines of real capacity.

`PAGE_LINES` is still read off the compiled page rather than off `\textheight`, and
the gap between the two widened: `floor(\textheight / one Bullet)` is now **55** where
the sweep binds at **53**. The binding shapes are the crowded ones — `(4,3)`, `(5,2)`,
`(6,1)` — which is the usual pattern, since a page with more Entries has less per-Entry
rounding slack to absorb the page's own.

| jobs | projects | predicted | actual | slack |
|---|---|---|---|---|
| 2 | 0 | 33 | 34 | +1 |
| 2 | 1 | 29 | 30 | +1 |
| 3 | 1 | 27 | 28 | +1 |
| 3 | 2 | 25 | 26 | +1 |
| 4 | 3 | 21 | 21 | 0 |
| 5 | 2 | 21 | 21 | 0 |
| 6 | 1 | 21 | 21 | 0 |

The charge across wrap counts, on `(2, 0)`:

| composition | charged | predicted | actual | slack |
|---|---|---|---|---|
| no section | 0 | 38 | 39 | +1 |
| 2 rows | 4 | 34 | 35 | +1 |
| 4 rows, none wrap | 5 | 33 | 34 | +1 |
| 4 rows, 1 wraps | 6 | 32 | 33 | +1 |
| 4 rows, 2 wrap | 7 | 31 | 32 | +1 |
| 4 rows, all wrap | 9 | 29 | 30 | +1 |

All nine sanity checks pass and the run reports `RESULT: constants hold`. Two of them
are worth reading rather than counting, because the narrower line changed what they
measured without changing whether they hold:

- **The row-lines formula now over-counts on two rungs instead of one.** It predicts
  1, 2, 3, 4 lines where TeX typeset 1, 2, 2, 3 — the 184-character rung moved from
  `2->2` to `2->3`. Over-counting is the safe direction and costs a skill at worst;
  the check is that it never under-counts, and it does not.
- **A Skills row is 24.09pt wider than a Bullet**, exactly as before. Both widths came
  down by the same 16.78pt, so the relationship the two character rates rest on is
  untouched.

## Re-measured 2026-08-10 — the Summary added, two new constants, nothing moved

`docs/adr/0044-the-page-opens-on-a-summary.md` put a new element at the **top** of the page: one
unbulleted `\small` paragraph between the Static profile header and the first `\section`. Unlike
`\resumeEmph` the day before, this one has real geometry, so the interesting question was whether
it moves `HEADER_LINES` — the constant it now sits directly underneath.

**It does not.** `RESULT: constants hold`, `HEADER_LINES` back at **36.91pt → 3**, and every other
element identical to the sweep below. What is new is two constants and one line of overhead:

```
Summary block             26.70pt        Summary \linewidth   542.03pt
                                         (+34.93pt on a Bullet, +10.84pt on a lead)

SUMMARY_LINES  2 (fixed, not derived)          SUMMARY_CHARS  220
2-line \parbox 20.89pt   ceiling 28.00pt   3-line \parbox 32.89pt
```

Three things in that run are worth keeping:

**The trailing `\vspace` was tuned by the measurement, not by eye.** At `-6pt` the block measured
**28.70pt against the 28.00pt** two Bullet lines charge — an over-promise, and the one direction
this document forbids. `-8pt` brings it to 26.70pt and clears by 1.30pt. `\section`'s own
`\titleformat` opens with `\vspace{-4pt}`, so the gap below the Summary is the two together.

**`HEADER_LINES` survives because of how the Summary is priced, not by luck.** The cheap
measurement — a `\pagetotal` reading taken at the first token of the Summary's text — reports
46.78pt where the header is 36.91pt. The 9.87pt difference is glue `\end{center}` contributes when
the next paragraph starts, and taking that reading would have charged all of it to `HEADER_LINES`
and pushed it to 4. The probe uses a **differential** instead: the same page built from the
template with the `\resumeSummary` call site removed, differenced at the first Bullet's marker.

**A marker inside the Summary fires twice.** The Template expands `\summaryLine` a second time
inside the Summary-fit `\parbox` at the end of the document, so `read_markers` now keeps the
**first** reading — the second reports `\pagetotal` at the bottom of a finished page.

The sweep, with the Summary's two lines in the overhead:

| jobs | projects | predicted | actual | slack |
|---|---|---|---|---|
| 2 | 0 | 30 | 30 | 0 |
| 2 | 1 | 26 | 26 | 0 |
| 3 | 1 | 24 | 24 | 0 |
| 3 | 2 | 22 | 22 | 0 |
| 4 | 3 | 18 | 18 | 0 |
| 5 | 2 | 18 | 18 | 0 |
| 6 | 1 | 18 | 18 | 0 |

Two lines lower than the sweep below, on every shape, and `PAGE_LINES` is still 50. That is the
bill for the element, and it is paid in evidence: `runs/auxo-ai` was `Spent 32, 0 left` before
this and re-packs at 30.

The charge across wrap counts, on `(2, 0)`:

| composition | charged | predicted | actual | slack |
|---|---|---|---|---|
| no section | 0 | 35 | 35 | 0 |
| 2 rows | 4 | 31 | 32 | +1 |
| 4 rows, none wrap | 5 | 30 | 30 | 0 |
| 4 rows, 1 wraps | 6 | 29 | 29 | 0 |
| 4 rows, 2 wrap | 7 | 28 | 29 | +1 |
| 4 rows, all wrap | 9 | 26 | 27 | +1 |

## Re-measured 2026-08-10 — `\resumeEmph` added, nothing moved

`docs/adr/0043-the-number-carries-the-emphasis.md` added one macro to the Template:

```latex
\newcommand{\resumeEmph}[1]{\textbf{#1}}
```

The probe was re-run because this file says to run it whenever the Template's macros change.
**Every constant came back unchanged and the run reported `RESULT: constants hold`** — same
`PAGE_LINES 50`, same `CHARS_PER_BULLET 103`, same `BOLD_CHARS_PER_BULLET 83`, same Skills
figures, and every slack column identical to the sweep below.

That is the expected result rather than a lucky one: `\resumeEmph` expands to the `\textbf` the
Skills labels and `\resumeSubheading` already set, so it adds no glue, no box, no list level and
no font that was not already loaded. No element changes shape, and the probe measures elements.

What *did* change is what a Bullet is charged, and that is not a constant: a bolded run inside a
Bullet is charged at `BOLD_CHARS_PER_BULLET` by the same formula the Skills rows use, in
`render.py:bullet_line_cost`. The constant was always right; the lint had simply never spent it on
a Bullet.

## Re-measured 2026-08-11 — emphasis widened, no macro touched, one check added

`docs/adr/0046-every-impact-figure-and-the-declared-keyword.md` widened emphasis from one span
per Bullet to every impact figure plus up to two declared keywords, and put keyword emphasis in
the Summary. **It adds no macro.** `\resumeEmph` is `0043`'s and is unchanged; what changed is how
many times per line `render.py` calls it, which is not a property of the Template.

The probe was run anyway, on this file's own rule — a reader who finds a mismatched blob hash
cannot tell from the hash what kind of edit they are looking at, and the Template *was* edited (a
comment). **`RESULT: constants hold`**, every constant unmoved: `PAGE_LINES 53`,
`CHARS_PER_BULLET 99`, `BOLD_CHARS_PER_BULLET 80`, `SUMMARY_CHARS 220`, `LEAD_CHARS 114`,
`SKILLS_ROW_PT 14.00`, `SKILLS_ROW_WRAP_PT 12.00`, and every slack column identical.

**What it did add is a sanity check, and that check is the whole reason no constant was needed.**
`render.py` now charges bold characters against three different budgets — `CHARS_PER_BULLET` for a
Bullet, `SUMMARY_CHARS` for the Summary — using one number:

```
BOLD_PENALTY = CHARS_PER_BULLET / BOLD_CHARS_PER_BULLET = 99 / 80 = 1.2375
```

That is legitimate only if the penalty is a property of the **font** rather than of the **column**,
and it is: both constants are the same Bullet text width divided by a pt-per-character rate, so the
width cancels and what survives is bold's 6.056pt against plain's 4.915pt — a ratio of 1.2323. The
alternative was a measured `BOLD_SUMMARY_CHARS`, which would have been a fifteenth constant charging
no new element.

So the probe now checks the direction that matters — *a bold character is charged at least what it
measures, at any width* — and reports it:

```
[ok] a bold character is charged at least what it measures, at any width
     (CHARS_PER_BULLET/BOLD_CHARS_PER_BULLET = 1.2375 against a measured
      6.056/4.915 = 1.2323 pt/char)
```

The two `floor`s that produced the constants push it the safe way, which is why there is slack
rather than an exact match. **If this ever fails, a bold character is being charged less than it
costs and the Summary's tape is reading generous** — fix it by re-deriving the two character
constants, never by loosening the check.

## Re-measured 2026-08-11 — the Summary got a heading, and `PAGE_LINES` moved

`docs/adr/0044-the-page-opens-on-a-summary.md` §1 refused a `\section{Summary}` heading and priced
the refusal: *"a heading costs `SECTION_LINES = 2` on top of the prose."* The maker reopened it and
paid. That ADR's Addendum records the decision; this is the measurement.

**`RESULT: constants hold`, and exactly one constant moved: `PAGE_LINES` 53 → 54.** Every element
height came back identical to the scaled point — one Bullet line 14.00pt, an Entry header 27.84pt, a
section heading 23.86pt, an Education row 27.28pt, a Skills row 14.00/12.00pt — and every `\linewidth`
is unchanged, so `CHARS_PER_BULLET 99`, `BOLD_CHARS_PER_BULLET 80`, `LEAD_CHARS 114`,
`BOLD_LEAD_CHARS 80` and `SUMMARY_CHARS 220` all hold.

### The spacing was measured before anything moved

The page has a grammar, read off the compiled `runs/auxo-ai` baseline to baseline:

```
above the Experience heading   24.91pt      Skills heading -> its first row      17.33pt
above Projects                 24.97pt      Experience heading -> Entry header   17.90pt
above Skills                   23.91pt
above Education                24.41pt
```

Dropped in untuned, the new heading landed **27.70pt** under the contact line — 3pt looser than any
other heading on the page — while the paragraph under it sat at **17.32pt**, dead on the grammar
with nothing tuned, because that distance is now set by the heading's own after-skip.

So the tuning went the *other way* from the one this document recorded on 2026-08-10.
`\resumeSummary`'s leading `\vspace{-6.5pt}` is **gone**, not re-aimed: it existed to pull a
heading-less paragraph up to a heading's first-row distance, and there is a heading now. The
trailing `\vspace{-1.5pt}` is unchanged and still measured, putting the `Experience` rule 24.91pt
under the Summary's last baseline.

**What the -6.5pt was really absorbing was `\end{center}`'s own trailing glue**, and that is now
trimmed where it is generated: `\headerContactLine\vspace{-3pt}`, *inside* the centre box.

**It has to go inside the box, and that is a fact about `\addvspace` rather than a preference.**
`\section` contributes its space with `\addvspace`, which merges with the skip already on the
vertical list instead of adding to it. Anything placed between `\end{center}` and the heading stops
the merge and makes the two add — measured, a bare `\vspace{0pt}` in that gap costs **+11.96pt**,
and `\vspace{-3pt}` costs +8.96pt. Inside the box the merge is untouched and -3pt means -3pt.

```
name                -> contact line          12.95pt
contact line        -> Summary rule          24.71pt   (grammar: 23.91-24.97)
Summary rule        -> Summary's first line  17.33pt   (grammar: 17.33 / 17.90)
Summary's last line -> Experience rule       24.91pt   (unchanged)
```

### Three numbers moved and only one of them is a new value

**`SECTION_LINES` charges the heading at a fifth call site and gains no twin.** It is the same
`\section`, the same `\titleformat`, the same 23.86pt. What differs is the *condition*: Experience,
Projects and Education are charged when the page holds that kind of content, Skills charges its own
heading inside `skills_charge`, and `\section{Summary}` is on every page that renders — so
`bullet_budget` adds it flat, beside `HEADER_LINES` and `SUMMARY_LINES`.

**`HEADER_LINES` is unmoved at 3 and its measurement is 33.91pt where it was 36.91pt.** The 3pt trim
is inside the header, so the differential charges it there — which is where it belongs. The header
was the loose thing; the first heading under it is only what revealed it.

**`PAGE_LINES` is 54, and the page did not grow.** The rule is unchanged: the smallest implied value
wins. Four of the seven shapes already implied 54 and the three crowded ones implied 53; the 3pt the
header gave back is what carried those three over.

| jobs | projects | capacity | implied `PAGE_LINES` | was |
|---|---|---|---|---|
| 2 | 0 | 31 | 54 | 54 |
| 2 | 1 | 27 | 54 | 54 |
| 3 | 1 | 25 | 54 | 54 |
| 3 | 2 | 23 | 54 | 54 |
| 4 | 3 | 19 | 54 | **53** |
| 5 | 2 | 19 | 54 | **53** |
| 6 | 1 | 19 | 54 | **53** |

### The Summary is now priced with its heading, and cannot honestly be priced without it

`\addvspace` merges the glue between a heading and what follows it, so neither half stands alone.
Cut only the prose and `\section{Summary}` welds to `\section{Experience}`, where the two headings'
skips merge and the differential reads **38.00pt** for a block nowhere near that; cut only the
heading and the prose lands on the header's glue instead. So the probe's `SUMMARY_CALL` became
`SUMMARY_BLOCK` and removes the pair.

The check that replaces *a two-line Summary costs no more than two Bullet lines*:

```
[ok] the Summary and its heading cost no more than the four lines charged
     (54.39pt against (2 + 2) x 14.00 = 56.00pt)
```

**The Summary-fit gate is untouched**, because it reads a `\parbox` height and no glue at all:
20.89pt <= 28.00pt < 32.89pt, exactly as before. `SUMMARY_CHARS` is measured against that same
ceiling and is unchanged at 220.

### The bill is one line of evidence, on every page

The heading costs 2 and the page gained 1. Every shape's budget is one lower than it was, and the
sweep now runs with **zero slack on all seven** rather than +1 on the four light ones — the honest
reading of `PAGE_LINES` going up while the budget goes down.

| jobs | projects | predicted | actual | slack |
|---|---|---|---|---|
| 2 | 0 | 31 | 31 | 0 |
| 2 | 1 | 27 | 27 | 0 |
| 3 | 1 | 25 | 25 | 0 |
| 3 | 2 | 23 | 23 | 0 |
| 4 | 3 | 19 | 19 | 0 |
| 5 | 2 | 19 | 19 | 0 |
| 6 | 1 | 19 | 19 | 0 |

The charge across wrap counts, on `(2, 0)`:

| composition | charged | predicted | actual | slack |
|---|---|---|---|---|
| no section | 0 | 37 | 37 | 0 |
| 2 rows | 4 | 33 | 33 | 0 |
| 4 rows, none wrap | 6 | 31 | 31 | 0 |
| 4 rows, 1 wraps | 7 | 30 | 30 | 0 |
| 4 rows, 2 wrap | 8 | 29 | 30 | +1 |
| 4 rows, all wrap | 10 | 27 | 28 | +1 |

Re-packed against today's other constants, `runs/auxo-ai` goes from `Spent 32, 0 left` to
`Spent 31`: **Room** falls from 3 lines to 2, and `auto-apply/c1` asks for a second line and is
written to one. Every other sanity check passes unchanged.

## Re-measured 2026-08-11 — the lead's bold twin, and the first new constant since the Summary

`docs/adr/0046-every-impact-figure-and-the-declared-keyword.md` left the entry arc's lead plain and
named the exact price of changing that: *"If this is reopened it is reopened as a calibration, with
`LEAD_CHARS`'s bold twin measured off a compiled page."* Its Addendum is that reopening, and this is
the measurement.

**`BOLD_LEAD_CHARS = 80`** — new in `tools/config.py`, beside `LEAD_LINES` and `LEAD_CHARS`. Every
other constant was re-derived and came back unmoved: **`RESULT: constants hold`**, `PAGE_LINES 53`,
`CHARS_PER_BULLET 99`, `BOLD_CHARS_PER_BULLET 80`, `SUMMARY_CHARS 220`, `LEAD_CHARS 114`,
`SKILLS_ROW_PT 14.00`, `SKILLS_ROW_WRAP_PT 12.00`, every element height identical to the scaled
point and every slack column unchanged. The Template moved only a comment.

It is measured the way `LEAD_CHARS` is measured — `\sbox` inside `\resumeEntryLead`'s own `\item`,
worst realistic sample wins — with `\textbf` around the box, so both counts come off the lead's one
514.40pt line:

```
6.396 pt/char ->  80 chars   bold ~30% GPU spend      <-- worst case wins
6.112 pt/char ->  84 chars   bold Gemini
5.910 pt/char ->  87 chars   bold Claude Code
5.845 pt/char ->  88 chars   bold ~150 KPIs
5.439 pt/char ->  94 chars   bold ~17.5 hours a month
```

**The sample family is the judgement here, and it is worth reading before touching the number.** The
family is the two shapes emphasis produces — a figure grown over its unit noun, and a declared term.
It deliberately excludes a bare all-caps acronym: `R&D` measures 8.796 pt/char and `GPT` 8.301,
because a three-character all-caps token has no lowercase letters to average against. That is the
`WWW MMM WWW` case `WIDTH_SAMPLES` already refuses, and taking it would give
`BOLD_LEAD_CHARS = 58` — which refuses `american-express`'s lead, 101 characters carrying one
19-character bold span, that typesets at 474.74pt inside a 514.40pt line.

**Two checks were added, and the second is the one a ratio cannot make.**

```
[ok] a bold character in a lead is charged at least what it measures
     (LEAD_CHARS/BOLD_LEAD_CHARS = 1.4250 against a measured 6.396/4.510 = 1.4180 pt/char)
[ok] a lead composed to the bold-aware budget still fits the lead's line
     (6 samples at the tape's edge, widest 102ch at 483.34pt against a 514.40pt line)
```

The first is the entry above's check at a third width. The second is new in kind: a safe *ratio*
spent against a *budget* that was too generous still puts a lead on a second line, and `LEAD_LINES`
charges one — so every lead sample is composed out to the last word the tape admits, with a real
bold span in it, and the width TeX gives the result is read back. That is the `SUMMARY_CHARS`
method (measure the thing, do not divide by a rate) applied one element over.

**A lead's penalty is 1.4250 where a Bullet's is 1.2375, and the entry above still holds.** Measured
per string, plain against bold, at this width: 1.1513, 1.1547, 1.1567, 1.1566, 1.1520, 1.1538. The
penalty *is* a property of the font. What differs is the sample family each of the two counts was
drawn from — `LEAD_CHARS` off lead sentences at 4.510 pt/char, `BOLD_LEAD_CHARS` off bold spans at
6.396 — and the Bullet's 1.2375 has the same shape for the same reason, a Skills label over a
Bullet sentence. **The derivation and the measurement disagree by 15%, in the safe direction, and
the measurement wins.** That is what the ADR meant by insisting on one.

## The measurement, as of 2026-08-09

Against `templates/resume.tex.j2` as committed alongside this document. Every
constant below except `LEAD_CHARS` is unchanged from the 2026-08-02 measurement —
the lead line continues `\resumeSubheading`'s own `\item` rather than opening a
second one, so it added no glue anywhere else the probe checks.

```
one Bullet line           14.00pt        \textheight          722.70pt
two-line Bullet           26.00pt        Bullet \linewidth    507.09pt
Entry header + glue       27.84pt        Skills row \linewidth 531.18pt
section heading           23.86pt        Lead \linewidth      531.18pt
Static profile header     36.91pt        one lead line         11.56pt
Education row             27.28pt
Skills row, first line    10.00pt
Skills row, each after    12.00pt

BULLET_LINE_PT 14.00   PAGE_LINES  50    HEADER_LINES  3    SECTION_LINES  2
ENTRY_HEADER_LINES   2         CHARS_PER_BULLET  103   BOLD_CHARS_PER_BULLET  83
SKILLS_ROW_PT  10.00           SKILLS_ROW_WRAP_PT  12.00
LEAD_LINES  1 (fixed, not derived)             LEAD_CHARS  117
```

The two-line Bullet is the one row with no constant beside it: 26.00pt measured
against 28.00pt charged, so the second line costs 12.00pt.

Sanity checks, all passing: an Education row costs 2 lines by overflow against
`ENTRY_HEADER_LINES = 2`; a 202-character Bullet wraps and measures 26.00pt against
`2 x 14.00 = 28.00pt`; a Skills row is 24.09pt wider than a Bullet; rows 2 through 6
are uniform to within **0.00pt**; the row-lines formula predicts 1, 2, 3, 4 lines
where TeX typeset 1, 2, 2, 3 — over-counting twice and never under; a one-line
lead measures 11.56pt against the 14.00pt it is charged; and **a supporting row
measures 10.00pt, which is `SKILLS_ROW_PT` exactly** — the check that lets the three
supporting sections be charged out of a constant named for another element.

| jobs | projects | predicted | actual | slack |
|---|---|---|---|---|
| 2 | 0 | 32 | 32 | 0 |
| 2 | 1 | 28 | 28 | 0 |
| 3 | 1 | 26 | 26 | 0 |
| 3 | 2 | 24 | 24 | 0 |
| 4 | 3 | 20 | 20 | 0 |
| 5 | 2 | 20 | 20 | 0 |
| 6 | 1 | 20 | 20 | 0 |

Every capacity is **two lines lower than the 2026-07-25 sweep**, and none of the
constants moved to make it so. The Skills section simply costs more than it did: a
one-line breadth list was charged 1 line plus its heading, and four category rows
are charged 5. That is the trade the section was redesigned to make, and this table
is the bill.

The charge across wrap counts, on `(2, 0)`:

| composition | charged | predicted | actual | slack |
|---|---|---|---|---|
| no section | 0 | 37 | 37 | 0 |
| 2 rows | 4 | 33 | 34 | +1 |
| 4 rows, none wrap | 5 | 32 | 32 | 0 |
| 4 rows, 1 wraps | 6 | 31 | 31 | 0 |
| 4 rows, 2 wrap | 7 | 30 | 31 | +1 |
| 4 rows, all wrap | 9 | 28 | 29 | +1 |

Slack is zero on every shape of the first table. It was not always: before the issue
#31 template change the column read 0, 1, 2, 3, 4, 4, 4 — growing with the Entry
count, because each Entry was charged a line of rounding it did not use. The next
section is the whole of that story.

## Two template values this calibration chose

**The Skills list zeroes the `itemize` glue around itself** (`topsep`, `partopsep`,
`parsep`) **and sets `itemsep` rigid.** A stock `itemize` wraps its rows in ~11pt of
top glue, enough to make a one-row section cost two lines of budget. Zeroing that is
correctness, not taste: it is what makes a row cost `SKILLS_ROW_PT` and nothing more,
and it is also why rows two through six measure uniform to within 0.00pt rather than
each carrying its own inter-item spring. `itemsep` is `4pt` rather than `0pt`, and
rigid rather than rubber, for the reasons in the 2026-08-10 entry below.

**Education gets its own macro, and that is what bought `ENTRY_HEADER_LINES` down
from 3 to 2.** This one was a decision rather than a measurement, and it is worth
the space because the reasoning is not recoverable from the numbers alone.

The first calibration charged 3 lines for an Entry header that measures 2.06.
Against a 28.00pt ceiling of two 14.00pt Bullet lines, an Entry header was 28.84pt
and an Education row 32.28pt, so both rounded up and each was charged about 13pt it
did not use — roughly a fifth of the page on a crowded résumé.

The obvious fix looked impossible. Tightening `\resumeSubheading`'s trailing
`\vspace` from `-7pt` to `-12pt` does make the constant 2, but it leaves **7.7pt
between the org/location line and the first Bullet** against `\small`'s own ~12pt
leading, so the org line's descenders run into the Bullet's ascenders. Measured
across the whole range, not just at the endpoints:

| `\vspace` | Entry header | Education row | org line → first Bullet | `ENTRY_HEADER_LINES` |
|---|---|---|---|---|
| `-7pt` (upstream) | 28.84pt | 32.28pt | 12.67pt | 3 |
| `-8pt` | **27.84pt** ✓ | 31.28pt | 11.67pt | 3 — Education blocks it |
| `-11pt` | 24.84pt | 28.28pt | 8.68pt | 3 — Education blocks it |
| `-12pt` | 23.84pt | 27.28pt | 7.69pt — collides | 2 |

The table is the argument. **The Entry header only ever needed to lose 0.84pt.**
What forced the ruinous `-12pt` was that the Education row rode the *same macro*
and is 3.44pt taller, dragging the requirement down with it.

So Education was split onto `\resumeEducationRow`, identical but for its trailing
`\vspace`. That split is free rather than a compromise: **nothing sits under an
Education row**, so the `-12pt` that collides with a Bullet costs no gap at all
there. The only space it tightens is between two stacked Education rows, measured
at 13.63pt — still above `\small`'s leading. Entry headers then need only `-8pt`,
costing one point of the gap above the first Bullet.

**`-9pt` does not work, though it reads as the safer choice.** `-8pt` clears the
ceiling by only 0.16pt, so a full point more margin is tempting. But at `-9pt` the
Entry header shrinks enough that an Education row's *marginal* cost measures one
line by overflow while still being charged two, and the probe's "Education row
costs the same lines as an Entry header" check fails. `-8pt` is the only value that
both reclaims the page and holds the invariant. That 0.16pt is a thin margin and a
later change to fonts, margins or the `tabular*` can push it back over — but the
failure is loud, because this procedure re-derives the constant as 3.

**Note what this did not add: a second name for the same element.**
`ENTRY_HEADER_LINES` still charges both. There are simply two macros now, each of
which must measure under it, and the sanity check is what holds them together. If it
ever fails, tighten a macro.

The four names added since — `BULLET_LINE_PT`, `BOLD_CHARS_PER_BULLET`,
`SKILLS_ROW_PT`, `SKILLS_ROW_WRAP_PT` — are not that. Each charges a genuinely new
element or unit no existing constant describes, which is a different thing from
splitting one element's charge in two so a macro can stop measuring under it.

Decided in #31, which
records the options weighed and the trade the maker took.

## 2026-10-10 — the one-row project header, and Education at the top

`docs/adr/0057-the-page-reads-like-a-resume.md` changed two things the budget sees.

**A project's header is one row.** `\resumeProjectHeading` measured 14.66pt at the job header's
`-8pt` tail, which rounds to two lines; at `-9pt` it measures 13.66pt and `PROJECT_HEADER_LINES = 1`.
The probe measures it across the boundary between two synthetic projects, and `section` is now
derived across a job-to-project boundary with the project header's cost, not the job's.

**Education may lead the page.** Where it sits changes nothing about its cost — but the spacing
that keeps its last row off the Experience heading did, and how is worth knowing. A `\vspace{4pt}`
after the list cost a whole line on the crowded shapes (`PAGE_LINES` 54 → 53), and so did
`\vspace{0pt}`: any glue node between two lists stops their skips merging. The fix gives the last
row its own `-8pt` tail instead (`\resumeEducationRowAbove`). The capacity sweep now measures every
shape **at both placements and keeps the smaller**, and `PAGE_LINES` stays 54 with zero slack on
all seven.

## 2026-10-11 — raw link targets and optional contact fields, nothing moved

The contact line's `\href` targets now take the raw value (`profile.email_url` and its
siblings, `entry.link_url`) and the visible text the escaped one, so `_` and `~` survive in
both. `phone`, `linkedin` and `github` became optional and drop with their separator. With
every field present the template renders byte-identical `.tex` to before, and the probe came
back `RESULT: constants hold`.

## Template history

Moved here from `tools/config.py`'s docstring on 2026-10-11, unchanged except where it named
a private run.

THE HASH DETECTS AN EDIT; WHETHER AN EDIT OWES A RE-MEASURE IS A QUESTION ABOUT WHAT
CHANGED. The blob moved on 2026-08-07 with no re-calibration: the Skills heading's
string went from `Technical Skills` to `Skills`, and a heading's text is not its
height — SECTION_LINES charges it either way
(docs/adr/0031-the-entry-header-is-built.md §8). It moved again on 2026-08-09 WITH a
re-calibration: the entry arc's lead line (`\resumeEntryLead`, `docs/adr/0032-the-entry-arc.md`
§4) is a macro with real geometry, so `LEAD_CHARS` below is newly measured — every
other constant was re-verified and came back unchanged, because the lead continues
`\resumeSubheading`'s own item rather than opening a second one. The blob moved a
third time the same day, rebalancing the macro's own leading and trailing `\vspace` —
the maker read a rendered page and found the gap above the lead too tight and the gap
below it too loose; LEAD_LINES and LEAD_CHARS are unchanged, only the split of the
lead's ~13pt budget between the two gaps. It moved a fourth time on 2026-08-10 for
`\resumeEmph`, WITH a re-calibration that came back entirely unmoved — a `\textbf`
the page already sets adds no glue, no box and no list level.

It moved a fifth time, the same day, for the Summary
(docs/adr/0044-the-page-opens-on-a-summary.md), and that one added an element rather
than restyling one. SUMMARY_LINES and SUMMARY_CHARS below are new; **every other
constant in this file was re-derived and came back unchanged**, including
HEADER_LINES, which the new block sits directly under. That is not luck — the probe
prices the Summary as a differential against the same page without it, so the glue
the two share is charged to neither.

`\resumeSummary`'s `\vspace` summed to -8pt and summed to -6pt for one measurement:
-6pt put the block at 28.70pt against the 28.00pt of two Bullet lines, which is the
one direction this file forbids. That block no longer exists in that shape — the
ELEVENTH move below put a heading over the prose and the paragraph now takes its
position from the heading's own after-skip — but the lesson survives it: a `\vspace`
here is a measurement, and loosening one without re-reading the number is how the
budget starts over-promising.

It moved a sixth time, the same day, for the three supporting sections
(docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md).
That one added an ELEMENT and still added no constant, which is the interesting
case and the one this file's own rule decides: a supporting row is the SAME element
as a Skills row — `\resumeItem` with a bold label, inside the same list geometry
with the same zeroed glue — so `SKILLS_ROW_PT` charges both call sites and what may
never be added here is a second name for an element already charged. The probe was
re-run in full: every constant came back unchanged, and it gained the check that
holds the claim, *a supporting row costs the same as a Skills row*, which measured
10.00pt against SKILLS_ROW_PT's 10.00 — 14.00 against 14.00 today, since the check is
that the two agree and not what they equal. If it ever fails, TIGHTEN A MACRO — do
not split the constant. It is the ENTRY_HEADER_LINES situation exactly, one section
down.

`SKILLS_ROW_WRAP_PT` deliberately does not charge a supporting row, and the reason
is not that one has never wrapped: a supporting row is CAPPED AT ONE TYPESET LINE
and `render.py` refuses a page holding one that measures over. That cap is what lets
the section's charge be a function of a row count rather than of composed text, and
it is why the supporting sections need no second Packer pass where the Skills section
does.

It moved a SEVENTH time, the same day, for the page itself: the document class option
went from `letterpaper` to `a4paper`. That is the first edit here that changes neither
an element nor a macro — every height in this file came back to the scaled point,
because an A4 page typesets the same elements. What moved is the PAPER: A4 is 17.8pt
narrower and 50.1pt taller than US Letter, and the template's margins are set as
additions to the class default rather than absolutely, so both the text width and the
text height move with it. So the three constants derived from a WIDTH all came down —
CHARS_PER_BULLET, BOLD_CHARS_PER_BULLET and LEAD_CHARS, by 3 or 4 characters each —
while PAGE_LINES, read off the page's measured capacity, went UP by 3. Every line is
narrower and the page holds three more of them. SUMMARY_CHARS held at 220 by the
rounding, not by anything about the page: the worst sample's fitting prefix landed on
the same word boundary at both widths.

It moved an EIGHTH time, the same day, and this one changed a number here: the Skills
list's `itemsep` went from 0pt to 4pt, so `SKILLS_ROW_PT` is 14.00 where it was 10.00.
That is the only constant that moved — `RESULT: constants hold`, `PAGE_LINES` still
53, every other height identical to the scaled point, since nothing outside that one
list's glue changed.

It is a TYPOGRAPHIC fix that happens to cost evidence, not a budget change that
happens to look different. `\resumeItem` carries a `\vspace{-2pt}` sized for the stock
`itemize` the Bullets sit in, which contributes 4pt between items; the Skills list
zeroed its glue and left the -2pt with nothing to come out of, so a row sat 10.00pt
below the one above it — 2pt TIGHTER THAN `\small`'S OWN LEADING, and the only place
on the page set that way. 4pt of `itemsep` puts a row at 14.00pt, the distance the
Experience Bullets already keep between items.

The bill is one line, and it is charged to every page that carries a Skills section:
four rows cost 6 lines with their heading where they cost 5. Do not tune the `itemsep`
back to buy the line back without reading `docs/calibration.md`'s entry for that date —
the number is what the rows are set at, not a lever.

It moved a NINTH time, on 2026-08-11, and this one moved only a COMMENT — the
`\resumeEmph` block now says what calls it, because
docs/adr/0046-every-impact-figure-and-the-declared-keyword.md widened emphasis from
one span per Bullet to every impact figure plus up to two declared keywords, and put
keyword emphasis in the Summary. No macro, no glue, no element. The probe ran anyway,
on the rule in the paragraph below, and came back `RESULT: constants hold` with every
height identical to the scaled point.

WHAT THAT ADR NEEDED FROM THIS FILE IS A NUMBER IT DID NOT ADD, and the reason
belongs here rather than only in the ADR. `render.py` now charges bold characters
against TWO budgets — CHARS_PER_BULLET for a Bullet and SUMMARY_CHARS for the
Summary — with one ratio, `CHARS_PER_BULLET / BOLD_CHARS_PER_BULLET`. That is sound
only because both of those counts are the SAME WIDTH divided by a pt-per-character
rate, so the width cancels and the ratio is a property of the FONT: bold's 6.056pt
against plain's 4.915pt. A `BOLD_SUMMARY_CHARS` would have been a fifteenth constant
charging no new element, which is what this file's own rule about ENTRY_HEADER_LINES
refuses one section up. The claim is not left as reasoning: the calibration probe
checks it in the direction that matters — *a bold character is charged at least what
it measures, at any width* — and a failure there means a bold character is being
charged less than it costs.

It moved a TENTH time, on 2026-08-11, and this one ADDED A CONSTANT — `BOLD_LEAD_CHARS`
below, the first new name here since the Summary. The Template again moved only a
comment: `\resumeEntryLead`'s, which now says the lead carries `\resumeEmph` and why its
bold budget is measured rather than borrowed. No macro, no glue, no element, and the
probe came back `RESULT: constants hold` with every other constant unmoved.

THE NEW NAME IS THE INTERESTING PART, because the paragraph above says one was not
needed. That paragraph is about the SUMMARY and it still stands: the Summary's bold is
charged at `BOLD_PENALTY` and always will be. The lead is a different case only because
`docs/adr/0046-every-impact-figure-and-the-declared-keyword.md` refused to bold it
without a measurement and wrote down the terms — *"If this is reopened it is reopened as
a calibration, with LEAD_CHARS's bold twin measured off a compiled page."* The maker
reopened it, so the measurement was taken rather than the ratio reused. It comes out
DEARER than the derivation — 114/80 = 1.4250 against a Bullet's 99/80 = 1.2375 — and the
reason is the sample family rather than the font, which the constant's own comment
below sets out.

THIS IS A SELECTION EVENT, and the rule three paragraphs from the top of this file is
why it is committed on its own with nothing bundled into it: a lead that says something
in bold may now say less, and what a lead may say decides which evidence frames an
entry. `docs/calibration.md`'s entry for that date holds the ladder behind the number
and the two checks that hold it.

It moved an ELEVENTH time, on 2026-08-11, and this one moved `PAGE_LINES` — the first
time that number has moved for anything but the paper it is printed on. The Summary
got a `\section{Summary}` heading, reversing `0044` §1's *"No `\section{Summary}`
heading"* (that ADR's Addendum records the reopening). Three numbers here are involved
and only one of them is a new value:

  `SECTION_LINES` charges the heading, at a fifth call site, and gains no twin. That is
  this file's own rule and the Summary heading is the easy case of it — same macro,
  same 23.86pt, nothing new to name.

  `HEADER_LINES` is unmoved at 3 and its MEASUREMENT moved, 36.91pt to 33.91pt. The
  Template trims 3pt of `\end{center}`'s trailing glue inside the centre box, because a
  heading under a centred header sat 27.70pt below the contact line where every other
  heading on the page keeps 23.91–24.97pt. It has to be trimmed THERE: `\section`
  contributes its space with `\addvspace`, which merges with the skip already on the
  list, and anything put between the two stops the merge and makes them add — measured,
  a bare `\vspace{0pt}` in that gap costs 11.96pt.

  `PAGE_LINES` is 54 where it was 53, AND THE PAGE DID NOT GROW. Four of the sweep's
  seven shapes already implied 54 and the three crowded ones implied 53; the 3pt the
  header gave back is what carried those three over. The rule is unchanged — the
  smallest implied value wins — and all seven now agree.

THE BUDGET WENT DOWN A LINE ON EVERY SHAPE, which is the honest way to read that: the
heading costs 2 and the page gained 1. Re-packed against today's other constants,
a real run went from `Spent 32, 0 left` to `Spent 31`, and the line came off a claim
that asked for two and is written to one. That is a SELECTION EVENT
under the rule at the top of this file — one fewer line of evidence, on every page,
bought with the word *Summary*.

A reader who finds a mismatched hash still re-calibrates, because they cannot tell
from the hash which kind of edit they are looking at.
