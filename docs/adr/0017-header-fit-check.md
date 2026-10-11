# The Header-fit check: guard the header by measurement, not by a constant

**Status:** accepted

## Context

`HEADER_LINES = 3` charges the **Static profile** header — name plus the contact/links line — three
Bullet lines, measured at 36.91pt against a 42.00pt charge. That measurement was taken against the
probe's synthetic profile, whose contact line is 116 characters and fits on one line.

A longer contact line wraps to a second line and **nothing notices**. Measured: the synthetic
profile puts `\pagetotal` at the first Bullet at 85.72pt; a longer but entirely plausible one puts
it at 97.72pt. The wrap costs 12.00pt, of which the 5.09pt of slack inside the charge absorbs part,
leaving the budget over-promising by **6.91pt** — half a Bullet line, charged to nobody. That is
precisely the failure `tools/config.py` is written to prevent, and it surfaces downstream as a
two-page PDF that the page-count assert blames on the constants.

Two properties make this the one place it could happen. First, the header is **maker-supplied and
never rewritten per run**, so unlike a Bullet — guarded pre-compile by `CHARS_PER_BULLET` — a wrap
set once is wrong on every résumé forever. Second, and the sharp part: **the header is the only
element in the template whose over-width failure is silent.** A centred line breaks *legally*, so
LaTeX issues no warning. Every other too-wide element in this template overflows instead and
screams — a long Education row produces `Overfull \hbox (55.07pt too wide)` and leaves the page
height untouched, which is a visual bug rather than a budget one and is deliberately out of scope
here.

The name line has the identical flaw and is in scope: `\Huge \scshape` at 39 characters measures
561.40pt against the 542.03pt available, and wraps.

## Decision

### The header is guarded by a check, not paid for by a constant

Two alternatives were rejected before this one.

**Charging the worst case — `HEADER_LINES = 4` — is rejected.** It is spec-clean (a two-line header
is a property of the template, not of the bank, so it does not violate `config.py`'s rule the way
calibrating against the maker's real profile would), and it is a one-line diff. But it burns
**19.09pt on every résumé that does not wrap** — one of the 22 spendable Bullet lines on a
seven-entry page — which is the trade of issue #31 run backwards. Worse, it makes a wrapped header
*legal and invisible*: the header would silently grow to two lines on a one-page résumé and nobody
would learn.

**A character-count constant — the `CHARS_PER_BULLET` analogue — is rejected.** It would be
pessimistic, since worst-case pt/char at `\small` is 5.328 and puts the budget at 101 characters
against the ~119 real contact lines achieve. And it would be **two** constants, not one: the name
line is a different font at ~14.4 pt/char. The block would go from five names to seven, against a
model that `SPEC.md` §8 and this repo's own docstrings fix at five.

The asymmetry that justifies treating the header differently from a Bullet: a Bullet is prose Opus
writes fresh every run, so its lint *must* be a character count Opus can self-check without LaTeX.
The header is a fixed file rendered through markup we control, so it is exactly measurable, and
accepting an 18-character haircut to avoid measuring it buys nothing.

### Detect by height — which is TeX's own verdict — and report by width

Whether a line breaks is not a fixed tolerance like `\hfuzz`; it depends on how much the line's
interword glue can shrink, which is content-dependent. Modelling that in `render.py` would be
guesswork, and a strict width comparison gets it wrong in the conservative direction: a 119-character
contact line measures 542.11pt against a 542.03pt line — 0.08pt over — and does **not** wrap.

So the check does not judge a width. It **asks TeX**. Each header line is defined once as a macro,
then measured twice: as an `\hbox` (always one line — the reference) and inside
`\parbox{\linewidth}{\centering …}` (line-broken by TeX for real). Taller means it broke. No
tolerance constant, no shrink modelling — it is TeX's own line-breaking decision, read back out of
the log. Validated on ten cases spanning both lines, narrow and wide glyphs, and both borderlines:
**exact agreement with TeX in all ten**, including the 542.11pt case a width comparison fails.

Height detects the wrap but cannot say how much to cut, so the same macros also report their natural
width and the available width. Those are read only on the failure path, purely so the message can say
"shorten by about 15 characters" rather than "it is too long, guess". The check therefore **detects
by height and reports by width**.

### It rides the real compile, and runs before the page-count assert

The measurement lives in the template and is read from the log `render.py` already has, rather than
in a second throwaway compile. This costs nothing per run, and it measures the document actually
shipped — a dedicated compile would measure the header in a synthetic context, which is the *same
mistake* that created this issue. Confirmed non-invasive: the instrumented and un-instrumented
templates produce **byte-identical page drawing streams**, so no glyph moves, `HEADER_LINES` stays
at 3, and no recalibration is owed.

*(Two details the implementation had to add to reach that, neither of which changes the decision.
The measurement is placed **after the last section** rather than beside the header: measuring the
`\Huge \scshape` name line in a box up there loads one font the shipped page never uses, which
shifts the `/F` resource number of every font after it — same glyphs, same positions, different
bytes. And `\href` is redefined to its visible text for the duration of the measurement, since it
would otherwise allocate a link annotation for a box that is never shipped. With both, the whole
PDF — not merely the drawing stream — comes out **byte-identical**, rather than the 12 bytes larger
this ADR first recorded. Widths are unaffected to the scaled point.)*

The accepted cost is that this is **post-compile**, so a bad profile burns one compile before
failing, unlike the pre-compile lints. That is the right trade for a check that fires roughly never:
the header is set once in `bank/profile.md` and then correct forever.

Ordering is load-bearing rather than incidental. The Header-fit check runs **before** the page-count
assert, because a wrapped header can tip the page to two and the assert's message blames the
constants — the exact misdiagnosis this ADR exists to remove.

## Consequences

- `HEADER_LINES = 3` stops being an assumption about what the maker typed and becomes a guarantee.
  Its docstring should say so.
- Glyph depth still varies the header height without wrapping — a descender in the name costs up to
  1.34pt, measured — but that sits well inside the 5.09pt of slack, so it needs no handling.
- The template gains two header-line macros, a measuring macro, and four `\typeout`s per line
  (one value each, because pdfTeX wraps the `.log` at 79 columns). It is the first thing in the
  template that exists to be *read back* by `render.py` rather than typeset, and the reason is
  the silence described above.
- Over-wide **Education** rows and **Entry headers** remain unguarded. They overflow rather than
  wrap, so they cost the budget nothing, and LaTeX already warns — a generic "fail on any
  `Overfull \hbox`" check would cover them. Tracked in issue #33, where the open question is
  whether there is a threshold: measured overshoots span 1.54pt (invisible) to 69pt (a wrecked
  résumé).
