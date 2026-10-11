# The softening tilde typesets as `$\sim$`

**Status:** accepted — what the mark binds to and what it defends against are recorded in
`docs/adr/0033-a-range-collapses-to-its-midpoint.md`, which this ADR does not restate. The
measurements below are unaffected.

## Context

`~` is how an Estimated number is softened — `Cut ~4 hours`. It has a glossary entry in
`CONTEXT.md`, it is the mark the Number-trace check reads to decide whether a figure is allowed to
round, and it is the only thing on the page that says a figure is an estimate rather than a
measurement. So it has to *look* right, not merely compile.

`render.py` escaped it to `\textasciitilde{}`, which is correct. The template loads no `fontenc`,
so that typesets in OT1 Computer Modern, where the glyph is a **raised** tilde: it prints up near
cap height and reads as a floating accent rather than an approximation sign. `runs/zs-btsa` shipped
`Cut ~4 hours` that way.

Ticket #37 named three candidates. A prototype — branch `prototype/37-tilde`,
`templates/prototype-tilde/` — compiled six: those three, the shipped state as a datum, and one
that came out of the measurements. Each was rendered into the real `zs-btsa` page and into a
specimen sheet, and each was measured rather than argued about.

### What was measured

At `\small`, the size `\resumeItem` sets. x-height is 4.31pt and cap height 6.83pt.

| | fix | glyph sits at | text layer | template | re-calibration |
|---|---|---|---|---|---|
| `base` | `\textasciitilde{}` | 6.68pt — raised | U+02DC | — | — |
| `A` | `$\sim$` | 3.67pt — mid-x | U+223C | untouched | no |
| `B` | `\usepackage[T1]{fontenc}` | 6.63pt — **still raised** | U+007E | preamble, document-wide | yes |
| `C` | `\texttildelow{}` (`textcomp`) | 1.23pt — at the baseline | U+007E | one package | no |
| `D` | `\raisebox{-0.5ex}{\textasciitilde}` | 4.53pt, 0.21pt past a `p` | U+02DC | untouched | no |
| `E` | `${\sim}$` | 3.67pt — mid-x | U+223C | untouched | no |

All six still render `zs-btsa` on one page.

### Two things the ticket assumed that measurement contradicts

**T1 does not fix the defect.** The ticket calls `\usepackage[T1]{fontenc}` "the standard fix" and
budgets a full re-calibration for it. Its tilde measures 6.63pt against a 6.89pt cap height — the
same raised glyph in a different encoding. On Computer Modern it buys the re-calibration and not
the fix. This is the whole reason the expensive option was not taken: not that it cost too much,
but that it did not work.

**The maths-spacing objection to `$\sim$` is unfounded.** The ticket expects `$\sim$` to be padded
because `\sim` is a relation and TeX puts thick space around relations. It does — *between atoms in
a math list*. Measured, the spacing attributable to every candidate is `0.00pt`: a lone atom has no
neighbour to be spaced against. `A`'s extra width over `base` is the cmsy glyph being wider
(7.78pt against 5.00pt), and nothing else.

### A fourth axis the ticket did not name

The template sets `\pdfgentounicode=1`, and `0007` §2 makes machine-readability the reason this
lineage is LaTeX at all. Extracted from the compiled page, the six candidates emit three different
codepoints — and **the shipped state emits U+02DC, MODIFIER LETTER SMALL TILDE**. The defect was
never only visual; the text layer an ATS reads has never carried a tilde either.

No candidate is both correctly placed and ASCII. The two that extract as U+007E are exactly the two
that are visually wrong.

## Decision

### 1. `LATEX_ESCAPES["~"]` becomes `$\sim$`

```python
"~": r"$\sim$",
```

One entry of the escape table in `tools/render.py`. It was chosen off the compiled page: `A` and
`E` were the only two that read correctly at résumé size. `C` sits down at the baseline and reads as
a swung dash — the mark a dictionary uses to stand in for a headword, not an approximation sign.
`D` lands at the right height but visibly hand-placed, and `-0.5ex` is a guess rather than a
measurement, so it would have to be re-guessed at every font change. `B` and `base` stay raised.

### 2. `templates/resume.tex.j2` is not touched, so no re-calibration is owed

`config.py`'s constants are measured against the template. This decision changes an escape, not the
template, so the blob hash stands and the five constants stand. **#43 must not run a re-calibration
on this ticket's account** — its note that "if the tilde fix landed as `[T1]{fontenc}`, expect every
constant to move" is now void, and the Skills-row work is the only thing there that obliges a
re-measure.

Recorded for the record, since it was measured and should not have to be measured again: `[T1]`
would have moved the profile header 36.91 → 36.74pt and the Skills item 18.02 → 17.97pt, and given
the two-job/one-project page a line of capacity the budget would not spend. The five constants
would have landed on the same values anyway.

### 3. U+223C in the text layer is accepted

The rendered page carries **U+223C, TILDE OPERATOR** — never an ASCII `~`. This is a real cost and
not a free win, so it is recorded as accepted rather than waved past:

- It cannot be avoided while also fixing the glyph. The candidates that extract as U+007E are the
  ones that are visually wrong, and the section this mark appears in is prose a human reads.
- It is an improvement on what ships today. U+02DC is a *modifier letter* — a spacing accent. U+223C
  is the character that means "approximately", which is what the mark means here.
- Nothing downstream matches on it. A keyword search hunts the number and the unit, not the
  softener.

If a future ATS finding makes ASCII in the text layer load-bearing, the lever is
`\pdfglyphtounicode`, not another glyph — and that is a new decision, not this one.

### 4. `${\sim}$` is rejected, though it is the same document

`E` compiles to a **byte-identical PDF**. That is a real comparison and not a coincidence: the
template pins `SOURCE_DATE_EPOCH` and sets `\pdfinfoomitdate`, `\pdfsuppressptexinfo` and
`\pdftrailerid{}` precisely so that identical runs produce identical bytes.

The braces demote a Rel atom to an Ord, which changes inter-atom spacing — but only where the tilde
has a neighbour inside one math list:

| math list | `\sim` (Rel) | `{\sim}` (Ord) |
|---|---|---|
| `$\sim$` | 7.78pt | 7.78pt |
| `$4\sim5$` | 23.33pt | **17.78pt** |
| `$\sim\sim$` | 15.56pt | 15.56pt |

`escape_latex` substitutes **per character**. Every math list this pipeline emits therefore holds
exactly one atom, and even `~~` comes out as `$\sim$$\sim$` — two separate lists. The braces guard a
state the escaper cannot reach, so they would buy nothing and leave a later reader working out what
they defend against. They become worth adding only if some future escape rule emits math with
neighbours in one list.

## Consequences

- **`tools/render.py` changes by one line.** Nothing else in the running system moves.
- **`tools/config.py` and `docs/calibration.md` are untouched**, and the template's blob hash still
  matches. See decision 2 for what #43 no longer owes.
- **The Number-trace check is unaffected.** `NUMBER` matches a literal `~` in the prose of
  `bullets.md`, and escaping happens later, at template fill — so what the softener *renders* as was
  never what that check reads. `traces_to`'s rounding rule is untouched.
- **A maxed-out Bullet carrying a tilde is now slightly wider than the lint believes.**
  `CHARS_PER_BULLET` charges 4.915pt per character at its worst-case rate; `$\sim$` occupies
  7.78pt, so each tilde runs **2.87pt** past what it was charged — against `base`'s 0.09pt. A
  103-character Bullet with one tilde lands about 2pt over the 507.09pt text width. This is a
  narrow case and it is not silent: `\hfuzz=2pt` and the Overflow check fail the run rather than
  ship it. Left as a known edge rather than tuned away, because lowering the character budget for
  every Bullet to defend against the rare one that is both maxed out and softened would cost real
  evidence on every résumé.
- **`docs/adr/0007` gains a second reason to be read as the machine-readability decision.** The
  text layer is now something a rendering choice is weighed against, not only an argument for
  LaTeX.
- **This ADR supersedes nothing.** It extends `0007`. `0020` is untouched — that decision is about
  what goes in a Skills row, and this one is about a glyph.
- **The prototype is kept as a primary source** on `prototype/37-tilde`, with all six candidates
  whole rather than trimmed to the winner. `runs/_prototype-tilde/` holds its artifacts, behind the
  boundary `0019` draws; nothing generated by it is tracked.
