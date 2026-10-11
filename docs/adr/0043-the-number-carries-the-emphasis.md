# Bold marks the figure, and the Template owns the bolding

**Status:** accepted

## Context

`runs/auxo-ai/resume.tex`, as it rendered before this ADR. Sixteen Bullets, four leads, four Skills
rows, and **the only bold on the page is the four Skills row labels** — `\textbf{Generative AI:}`
and its three siblings. Everything a hiring reader is meant to weigh is set in the same 11pt roman
as everything around it:

```
\resumeItem{Owned $\sim$60 of a new diagnostics scorecard's $\sim$150 KPIs, automating the heaviest to halve its refresh}
\resumeItem{Automated the merchant-account mapping, newly matching $\sim$41 accounts, plus the monthly leadership email and the review deck's data cuts, cutting $\sim$8 hours a month}
```

Nine figures reach that page — `~17.5 hours`, `~41`, `~150`, `~60`, `~85%`, `~95%`, `~8 hours`,
`~2,100`, and the halving in *"halve its refresh"*. A thirty-second read finds none of them,
because nothing on the line tells the eye where to stop.

`0010` fixed this system's attention on **selection** and gave prose *"no mechanism in v1"*. This
is neither selection nor prose: it is **typography**, the one lever that changes what a skimming
reader takes off the page without changing a word of what the page says.

### The constraint this decision had to answer, not route around

`tools/render.py:escape_latex`, docstring, verbatim:

> *"Opus writes plain prose and never LaTeX, so nothing it writes can break a compile or smuggle in
> formatting. **Emphasis lives in the Template, never in the data** (`docs/adr/0007-rendering-approach.md`)."*

That sentence is why this ADR does not simply let the composer write `**…**`. Read `0007`'s actual
worry rather than its slogan and it is two things: a compile that breaks, and formatting smuggled
in through the data. Both are about the model's output reaching pdfTeX unchecked. Neither says the
*choice* of what to emphasise cannot be derived — only that the *typesetting* of it must not come
from the model.

## Decision

### 1. The bolded span is the Bullet's figure, and there is at most one

One span per Bullet: the number, plus the noun that gives a bare figure meaning.

| line | bolded |
|---|---|
| `…the review deck's data cuts, cutting ~8 hours a month` | **~8 hours a month** |
| `Owned ~60 of a new diagnostics scorecard's ~150 KPIs, automating the heaviest…` | **~60** |
| `Rewrote the scorecard compilation…, cutting the hand rework ~85%` | **~85%** |
| `Drove Claude Code past chat use: three agent skills, ~2,100 lines of prose…` | **~2,100 lines** |
| `A custom GPT drafts business-review insights an analyst reviews, in a deck senior leadership reads` | *nothing* |

**Why the figure and nothing else.** The figure is the only thing on a Bullet that is already
*mechanically identified*. `numbers()` scans every rendered line and `check_number_trace` resolves
each hit against the cited Claim's stored value at equal-or-softer provenance, before the page is
filled. A span anchored to a figure is therefore, by construction, prose the run has **already
proved traces to the bank**. Bolding cannot introduce content because it does not choose content —
it re-typesets a substring that was already there and already checked. Nothing else on the line has
that property.

**Which figure, where a line carries two.** The one the Claim was composed around — its stored
`number:`, or the group's `## merge` sum for a merged Bullet. Where no rendered figure traces to
that (`american-express/c7` stores `~50%` and its Bullet says *halve*), the **leftmost** figure
takes it instead. Both are traced; the preference only decides which figure argues the claim rather
than sizes it. That is why `~60 of ~150` bolds `~60`: `0039` put the denominator on the page to
size the work, not to be the work.

**A Bullet with no figure gets no bold, and that is the design.** Six of `auxo-ai`'s sixteen
Bullets are qualitative. A page where every line carries a bold run has no emphasis — it has a
second body font.

### 2. A keyword is never bolded inside a Bullet

Three reasons, in the order they bind:

1. **`0027` §3 and §4.** The posting *"may tell you which of your own words to reach for. It may
   never supply one"*, and *"the JD decides which claims get a line, not what goes in the
   sentence."* Bolding a term *because this posting names it* supplies no word — but it lets the
   posting choose where the reader's eye lands, which is §4's failure in a different medium. The
   sentence's interior stops being the maker's the moment the JD picks its stressed syllable.
2. **Keywords already have their own real estate, and it is already bold.** The Skills rows exist
   so a Nice-to-have survives its Entry losing the page (`0020`), and their labels are this page's
   existing `\textbf`. A technology bolded in a Bullet *and* listed in a row is one word twice at
   one weight.
3. **It is the surveyed tools' failure mode.** The research survey behind `0039` recorded
   `resume-optimization-crew` shipping *"Collaboration with cross-functional stakeholders"* beside
   *"Cross-functional collaboration and team leadership"*. Keyword bolding is that instinct with a
   font weight on it.

So: no technology, no skill, no JD term, no role noun is ever bolded inside a Bullet.

### 3. The span is chosen in the maker's prose; the Template does the bolding

`templates/resume.tex.j2` gains one macro:

```latex
\newcommand{\resumeEmph}[1]{\textbf{#1}}
```

It is a named macro rather than a bare `\textbf` at the call site so the Template keeps owning what
emphasis *looks like* — small caps or a semibold later is one line there and no change in
`render.py`. That is `0007`'s rule kept rather than bent.

`tools/render.py` gains `emphasis_span()`, `extend_over_unit()` and `emphasised_latex()`, called
from `fill_template`. **Split first, escape the parts, then wrap.** Escaping is per-character and
context-free, so escaping three slices and joining them is identical to escaping the whole string —
while matching the span in the *escaped* text would mean matching `$\sim$8 hours a month` and
re-deriving offsets that `escape_latex` had already moved. The macro name is a constant in
`render.py`, never anything a run composed, so nothing Opus writes can reach pdfTeX as markup.

**`bullets.md` does not change, and neither does anything the composer writes.** The cold read
(§5.05) still reads plain sentences; the number trace still reads plain prose; the opener,
spelling and spread checks are untouched. The page and the file differ in exactly one respect —
the typesetting — which is where `0007` puts the difference.

### 4. Bold costs characters, and the length lint charges them

`docs/calibration.md` measured it: **bold is 6.056pt per character against plain's 4.915pt.** That
is why `BOLD_CHARS_PER_BULLET = 83` already exists beside `CHARS_PER_BULLET = 103` for a Skills
row's label. A Bullet that sets its figure in bold has the identical problem, and `check_lengths`
counted characters flat — under-counting in the one direction `calibration.md` forbids:
*"under-counting hands the Packer a budget promising a line the page does not have."*

**No new constant, because no new element.** The charge is `calibration.md`'s own row-lines formula
with the label swapped for the emphasis span:

```
cost = plain characters / CHARS_PER_BULLET + bold characters / BOLD_CHARS_PER_BULLET
```

A bold character costs `103/83 = 1.241` plain-character-equivalents, so a 15-character span drops a
one-line Bullet's real ceiling from 103 to about 99. The price lands on the prose: **lines get
shorter.** `tools/lengths.py` charges the same way so the maker meets the number while composing
rather than at the compile, and it imports the arithmetic rather than re-deriving it.

`LEAD_CHARS` is untouched — a lead carries no emphasis (§5).

### 5. The limits, and what is never bolded

- **At most one span per Bullet** — per Bullet, not per line, so a two-line Bullet still gets one.
  Two emphases in one sentence is a specification, `0027` §2's failure mode wearing a font weight.
- **A span is never the whole line.** `emphasised_latex` raises rather than typesetting it; nothing
  composes it today, so the guard is against a later rule change.
- **The span never crosses punctuation.** In `~150 KPIs, automating the heaviest` the comma is
  where the figure stops being the figure.
- **A unit noun is taken only where it is one.** `~60 of a new diagnostics scorecard's` stops at
  *of*: a preposition or an article says there is no unit noun here. The `a month` / `per cycle`
  rate tail is the one place a stopword sits inside a span, and only after a noun was taken.
- **Never bolded:** a lead line (`0032` made it the entry's frame, and a frame in bold competes
  with what it frames); a Skills row's skills (its label is the row's emphasis); an Entry header,
  Education row or the profile header (fixed furniture, already carrying the `\textbf` the Template
  wanted); any technology, skill or JD term (§2); any figure that is not the cited Claim's own
  where one of its own is on the line.

### 6. The probe runs, and the constants must not move

`docs/calibration.md`: *"Re-run it whenever `templates/resume.tex.j2` changes its geometry, fonts,
margins or macros."* This adds a macro, so it ran. `\resumeEmph` expands to `\textbf`, which the
Template already sets in `\resumeSubheading` and the Skills labels; it adds no glue, no box, no
list level and no font not already loaded, so no element changes shape.

**Measured, 2026-08-10: every constant unchanged and `RESULT: constants hold`.** `PAGE_LINES 50`,
`CHARS_PER_BULLET 103`, `BOLD_CHARS_PER_BULLET 83`, `ENTRY_HEADER_LINES 2`, both Skills row
figures, and every slack column identical to the 2026-08-09 sweep. `tools/config.py` is not
touched by this ADR — had a constant moved, the change owed was to the macro, because
`calibration.md` is explicit that a constant change is *"a selection event, not a layout tweak"*
and one is not smuggled in under a typography ticket.

## Rejected

**A `**…**` span the composer marks in `bullets.md`.** Considered seriously, because it is the only
way to bold an outcome phrase with no figure in it — *"in a deck senior leadership reads"* is the
most persuasive reach fact on the `auxo-ai` page and this ADR leaves it plain. Refused on `0007`,
and on a sharper problem than the slogan: **nothing could check it.** A marked span can be
validated for shape — contiguous, one per line, stripping reproduces the plain text — but not for
*judgement*, and whether this phrase is the impact is exactly a judgement. `0010` refused a second
judgement of prose on the record and §5.05's cold read is the only reader in the system. A marker
the composer places and no check can assess is a lint-shaped hole. If the loss ever becomes
intolerable, the reopening is an `## Emphasis` declaration in `scores.md` — made at scoring time,
checkable against the Claim, and out of the sentence — never markup in the prose.

**Bolding the JD's keywords.** §2.

**Italics, colour, small caps, or a second weight.** One emphasis to a page. `0007` put the
Template in charge of appearance and this spends exactly one of its levers.

**Raising `CHARS_PER_BULLET` to absorb the bold cost.** `0025` refused raising it on the record and
nothing here reopens it. Bold costs characters; the lines get shorter.

## The cost, stated rather than waved past

**Six of sixteen Bullets on `auxo-ai` carry no emphasis at all**, and one of them is the line
carrying the senior-leadership audience — the single most persuasive fact `0039` put on that page.
The ADR takes that loss on the grounds that an unemphasised true line is a smaller failure than an
unauditable emphasis rule, but it is a real loss and the next output review should look at it
again.

**The bold charge makes some sentences unwritable that were writable yesterday.** A line at 103
characters ending in a 16-character figure now costs 1.04 lines and is refused. On the `auxo-ai`
re-run nothing actually failed — the five Bullets carrying a bold span sat at 0.93–0.99 and had the
slack — but that is this bank's luck, not a property of the design. On a tighter page the lint will
start refusing lines that read well, and the fix is `0027`'s cut-for-length, not a wider constant.

**`lengths.py` now reads the bank.** It was a run-folder-only tool and is now one that loads
`bank/` to charge a span it cannot otherwise see. It degrades to the plain count where the bank is
missing rather than failing, which means the tape can read a few characters generous in exactly the
situation where nobody notices. `render.py` remains the gate.

## Consequences

- `templates/resume.tex.j2` gains `\resumeEmph`. `docs/calibration.md` gains a dated line recording
  that the macro was added and the measurement held.
- `tools/render.py`: `emphasis_span`, `extend_over_unit`, `emphasised_latex`, `bullet_line_cost`;
  `fill_template` emphasises; `check_lengths` takes `entries` and charges the weighted cost.
- `tools/lengths.py` loads the bank and charges the same way, importing the arithmetic.
- `tests/test_render.py` gains the emphasis block: the span is the Claim's figure, a bare figure
  takes its unit noun, the span stops at punctuation and takes a rate tail, a figureless Bullet
  gets nothing, the leftmost figure takes it when the stored number is unrendered, **bolding
  introduces no new text**, one span maximum, the bold run is charged at the bold rate, a Bullet
  that only fits plain is refused, the figure reaches the PDF inside the macro, and **emphasis
  moves no element marker**.
- Two existing tests changed with the behaviour: the end-to-end PDF test asserts on the prose
  around the macro rather than through it, and the length message keeps its `N x 103` clause while
  gaining a bold clause.
- **No `tools/config.py` change.** The probe re-derived every constant unmoved.
