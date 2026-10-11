# The Overflow check: fail the run on a margin overflow, at a threshold TeX enforces

**Status:** accepted

## Context

`0017` guarded the **Static profile** header, whose over-width failure is *silent* — a centred line
breaks legally and LaTeX warns about nothing. It closed by naming the opposite case and handing it
on: over-long **Entry headers** (`\resumeSubheading`) and **Education rows** (`\resumeEducationRow`)
are built on `tabular*` with `l`/`r` columns, which do not line-break. They **overflow the right
margin** and LaTeX says so, every time, on stderr and in the log.

Measured against the current Template (issue #33):

| content | `Overfull \hbox` | page height | pages |
|---|---|---|---|
| ordinary synthetic entry | none | — | 1 |
| long Entry title | 69.37pt (alignment) | unchanged | 1 |
| long institution | 55.07pt (alignment) | unchanged | 1 |
| long degree | 68.93pt (alignment) | unchanged | 1 |
| moderately long institution | 1.54pt (alignment) | unchanged | 1 |
| 140-character single token in a Bullet | 931.80pt (paragraph) | unchanged | 1 |

The height is untouched in every case, so the page budget is not implicated and the page-count
assert never fires. This is a purely **visual** defect — on a document whose entire purpose is to be
read — and nothing fails the run: `pdflatex` reports an overfull box as a *warning*, so it exits 0
even under `-halt-on-error`, and nothing in the Renderer reads the string.

Four things were open. Whether to fix this in the Renderer or the Template; whether any overflow
fails or only a visible one; whether Bullets are in scope; and how the failure names the file the
maker has to edit.

## Decision

### The Renderer fails the run — the Template is not changed to absorb it

The rejected alternative was to make the two macros wrap or shrink instead of overflowing, which
would need no check at all. It is rejected on cost, not on principle: `l`/`r` columns would have to
become `p{}` columns, or the content would have to change size, and **either one moves typeset
heights**. That invalidates the **Page-budget constants**, owes a full recalibration
(`docs/calibration.md`), and — because the constants decide selection — makes this a recorded event
that changes which Entries reach the page. A visual defect in an over-long job title does not
justify re-deriving the page budget.

Note what does *not* carry over from `0017`. There, absorbing the overflow in the layout was
rejected partly because it would make a wrapped header *legal and invisible*. That objection is
absent here: LaTeX warns either way, so nothing would go quiet. The decision rests on the
recalibration cost alone.

The consequence is that the failure tells the maker to shorten a job title or an institution name,
which is the honest fix — those strings are theirs, and a title that does not fit the page is a
title that reads badly on it.

### The threshold lives in `\hfuzz`, not in `render.py`

The measured overshoots span 1.54pt to 931.80pt. Failing on everything refuses to render over an
overhang no reader could see; failing on nothing is the status quo. So there is a threshold, and the
question is only where it is written down.

It goes in the Template, as `\hfuzz`, and the Renderer fails on **anything TeX still reports**. This
is the same move `0017` made — *ask TeX, do not model TeX* — one level down: rather than parsing
`pt` values out of log lines and comparing them in Python, the number is set once, in TeX's own
units, and TeX applies it. `render.py` then needs no constant of its own and no arithmetic, and the
check reduces to "did the log mention an overfull box in a shipped part of the document".

**`\hfuzz` changes what is reported, never what is typeset.** No glyph moves, so unlike the Template
fix above this costs nothing and owes no recalibration. It does not disturb the **Header-fit check**,
which reads heights out of `\typeout` markers and never looks at overfull warnings.

**The value is `2pt`, and it is the softest part of this ADR.** It is a judgement about what a reader
can see — roughly 0.7mm — not a measurement. It is tempting to argue from the data that any value in
(1.54, 55.07) selects the same cases, the way `WRAP_NOISE_PT` is a floor between two numbers an order
of magnitude apart; that argument does not hold here. That gap is an artifact of which examples were
measured, not a real bimodality, and content exists at every width in between. Anyone with a reason
to prefer a different value should change it and say why in this section.

### Bullets are in scope

Bullets wrap normally, so ordinary prose never overflows — a Bullet containing a long URL breaks
fine. A single unbreakable token does overflow, and `CHARS_PER_BULLET` does not cover the case: at
103 characters the length lint refuses the measured 140-character token, but a ~100-character single
token passes the lint and still overflows.

They are in scope because including them is *cheaper than excluding them*. A check that reads the log
catches them for free; keeping them out would mean deliberately discarding `in paragraph` reports and
keeping `in alignment` ones. There is no reason to write that code.

This makes the Overflow check the second lint on a Bullet's width, after `CHARS_PER_BULLET`, and the
two are not redundant: the length lint is pre-compile, counts characters, and catches long prose
before a compile is spent; this one is post-compile, measures the typeset box, and catches the
narrow case a character count cannot see.

### The log's line numbers are mapped back to the element that produced them

An overfull report carries `at lines 287--292`, indexing into `resume.tex` — **a file the Renderer
writes itself**. So the Renderer can say which Entry, which Education row, or which Bullet overflowed,
and therefore which file the maker has to open: a Bank entry for an Entry header,
`bank/profile.md` for an Education row. Without that the message can only quote a line number in a
generated file, which is useless to the maker and points at the wrong artifact — `resume.tex` is
overwritten on the next run.

*Corrected in implementation:* this section originally sent a **Bullet** to its Bank entry too. The
claim ref does name that entry, but the prose that overflowed is the prose Opus composed, so the fix
is a rephrase in `bullets.md` — which is also where `CHARS_PER_BULLET`, the other lint on a Bullet's
width, already sends it. The Skills line goes to the same file for the same reason.

The mapping is by **inert marker comments** emitted into `resume.tex` alongside each element, with a
report attributed to the nearest preceding marker. A LaTeX comment on its own line contributes
nothing to the typeset output — not even an inter-token space — so this too owes no recalibration,
provided markers sit between macro calls and never inside an argument list.

The cost accepted is a coupling: the check knows something about the Template's structure, which
nothing else in `render.py` does. That is the same coupling `0017` already took on for the
`AUTOAPPLY:headerfit:` markers, and it is bounded the same way — the Template emits, the Renderer
reads, and a missing marker is a hard failure rather than a silently unattributed report.

One region must be **excluded**: the header-fit instrumentation at the end of the document measures
each header line inside a `\parbox`, which line-breaks for real and will therefore report an overfull
box of its own if a header line holds an over-long unbreakable token. That box is never shipped. It
is already delimited by `BEGIN`/`END` marker comments, so the exclusion costs nothing. The *shipped*
header overflowing is a real defect and stays in scope — it is only the measurement copy that is
dropped, so the same content is not reported twice.

### It runs after the Header-fit check and before the page-count assert

Ordering here is **by convention, not load-bearing**, and the implementation should say so rather
than borrow `0017`'s certainty. An overflow leaves the page height untouched, so it can neither cause
nor be caused by a second page; the Overflow check and the page-count assert are independent, and
either order reports the same facts.

The convention it follows: failures the maker fixes **in their own data** come before the one that
blames the Template's calibration. The page-count assert is last because its message is an
instruction to re-run the calibration procedure, and it has earned the right to be that certain only
once everything about the content has been cleared.

## Consequences

- The Renderer gains a ninth step and a second post-compile reason to refuse a PDF. The docstring's
  ordered list grows accordingly.
- `\hfuzz = 2pt` is a new number in the Template that is **not** a Page-budget constant and must not
  be mistaken for one: it does not participate in calibration, and changing it cannot change
  selection. The Template's own preamble notes which of its numbers are calibrated; this one belongs
  outside that set.
- Overflows between 0.1pt (pdfTeX's default `\hfuzz`) and 2pt stop being reported in the log at all,
  including to a human reading it. That is the point, and it is the reason the value is stated as a
  judgement above rather than smuggled in as a tolerance.
- `\resumeSubheading` and `\resumeEducationRow` keep their non-wrapping `l`/`r` columns, and
  `ENTRY_HEADER_LINES` keeps its meaning. This ADR deliberately leaves the Template's geometry alone.
- `Overfull \vbox` is not covered. A vertical overflow is a height failure, which is the page-count
  assert's business.
