r"""Page-budget constants — the one named block both the Packer and the Renderer read.

RAW, and it has to be: this docstring names LaTeX macros, and `\resumeEntryLead` and
`\vspace` are a carriage return and a vertical tab to Python. They were, silently,
until 2026-08-10 — an `\small` added that day made the same mistake somewhere Python
warns about instead of somewhere it does not.

No logic and no I/O: this file is a set of numbers, and anything computed at import
time would make them a function of the environment rather than a measurement of the
template.

THESE VALUES ARE MEASURED, NEVER ESTIMATED. They come from the procedure in
docs/calibration.md, run against templates/resume.tex.j2. Re-run it whenever the
template's geometry, fonts, margins or macros change, and commit a change to these
numbers on its own — it changes which evidence wins a slot on the page.

The unit is ONE RENDERED BULLET LINE, BULLET_LINE_PT below. Every cost here is that
element's typeset height divided by it and rounded UP: rounded down, the budget
would promise a line the page does not have.

ONE STATED EXCEPTION, and it is the Skills rows'. A Skills row is the first element
that is NEVER CHARGED ALONE — the section charges N of them at once, so the rounding
happens once, at the sum. So those two are left in points and the Packer rounds the
sum (docs/adr/0021-skills-row-cost.md §1).

THE EXCEPTION NOW BUYS NOTHING AT THESE VALUES, and that is worth saying plainly
rather than leaving for someone to rediscover. It was written when a row measured
10.00pt — 0.714 of a line — so a 4-row section occupied 2.86 and rounding each row up
on its own would have charged 4. A row is 14.00pt now, exactly one Bullet line, and
`ceil((14n + 12w) / 14)` equals `n + w` for every wrap count the two-line cap can
reach. The sum-rounding and the per-row rounding agree on every composition that can
occur.

It stays anyway, and not out of sentiment: this is a MEASUREMENT pipeline, and the
coincidence is a fact about today's two numbers rather than about the design. The
next template change that moves a row off 14.00pt makes the exception bite again with
nothing to re-derive. What would be wrong is to fold the two constants into one line
count, which is the thing 0021 §1 explicitly rejected.

AND ONE MEASURED FACT THAT DELIBERATELY EARNS NO NAME HERE. A Bullet's second typeset
line is 12.00pt, so a two-line Bullet measures 26.00pt against the 28.00pt it is
charged. There is no `BULLET_WRAP_PT` because nothing would ever spend one — the
Packer charges the integer 2. The calibration probe holds the fact instead (*a
two-line Bullet costs no more than two Bullet lines*), which is what would catch a
template change turning that charge into an over-promise
(docs/adr/0025-bullet-wrap-cost.md §5).

Last calibrated: 2026-10-11, against templates/resume.tex.j2 at blob 15f3cf0 — check
it with

    git hash-object templates/resume.tex.j2

If the hash no longer matches, the template has changed since the constants were
measured: re-run docs/calibration.md. Not every edit moves a number — a comment or a
heading's text does not — but a reader cannot tell from the hash which kind of edit
it was. The history of every move, and why, is in docs/calibration.md under
"Template history".
"""

# --------------------------------------------------------------------------
# Page-budget constants
# --------------------------------------------------------------------------

#: One rendered Bullet line, in points — the unit every other constant is expressed
#: in. It was always here, in the docstring above, and is a name now because the
#: Skills section's charge divides by it: a Skills row is measured in points and the
#: Packer converts the sum (docs/adr/0021-skills-row-cost.md §2).
BULLET_LINE_PT = 14.00

#: Total Bullet-line-equivalents one page holds, including all fixed overhead.
#: Read off the compiled page, not off \textheight: the calibration sweep measures
#: the real capacity of seven résumé shapes and takes the largest value that
#: over-promises on none of them.
#:
#: 54 rather than the 53 it read until 2026-08-11, and THE PAGE DID NOT GROW. The
#: Summary's heading came with a 3pt trim to the header's trailing glue, and 3pt is
#: what the three crowded shapes — (4,3), (5,2), (6,1) — were short of implying 54
#: like the other four already did. All seven agree now. The budget still went DOWN a
#: line on every shape, because the heading itself costs SECTION_LINES: see
#: docs/calibration.md's entry for that date.
PAGE_LINES = 54

#: The Static profile header — name plus the contact/links line. Measured 33.91pt,
#: which charges a one-line name above a one-line contact line. Either can wrap
#: silently, since a centred line breaks legally and LaTeX warns about nothing; the
#: Header-fit check in render.py refuses the run instead of paying for it here.
#:
#: 33.91pt where it read 36.91pt until 2026-08-11, and the 3pt is the Summary
#: heading's. \end{center} leaves 3pt more glue behind it than the page's own spacing
#: grammar wants, and the Template now trims it inside the centre box, where a
#: \section's \addvspace still merges with what is left. The differential charges that
#: trim here because it is inside the header, which is also where it belongs — the
#: header was the loose thing; the first heading under it is only what revealed it.
#: The constant is unmoved at 3, with more slack under it than before.
HEADER_LINES = 3

#: One section heading and its rule (Summary, Experience, Projects, Skills,
#: Education). Measured 23.86pt.
#:
#: FIVE CALL SITES, ONE CONSTANT, and the Summary's is the one with no condition on
#: it. Experience, Projects and Education are charged when the page has that kind of
#: content, and Skills charges its own heading inside `skills_charge` because whether
#: it has one depends on what was composed. `\section{Summary}` is on every page that
#: renders, so `bullet_budget` adds it flat beside HEADER_LINES and SUMMARY_LINES
#: (docs/adr/0044-the-page-opens-on-a-summary.md, Addendum).
SECTION_LINES = 2

#: One Entry header — title, org, location, dates — plus the list glue around it.
#: Measured 27.84pt through \resumeSubheading; an Education row measures 27.28pt
#: through its own \resumeEducationRow. Both round to 2.
#:
#: TWO MACROS, ONE CONSTANT. This number charges both, so both must measure under
#: it — the calibration probe's "Education row costs the same lines as an Entry
#: header" check enforces that. If it fails, tighten a macro rather than SPLITTING
#: THIS CONSTANT IN TWO: a second name for the same element would let the two drift
#: apart silently. That is what the old remark about "a sixth constant has nowhere
#: to live" was aimed at, and the names below are not it — they charge genuinely new
#: elements no existing constant describes (docs/adr/0020-skills-section.md §6,
#: docs/adr/0021-skills-row-cost.md §1).
ENTRY_HEADER_LINES = 2

#: One PROJECT header — a single row: the name, its stack and link, and the dates —
#: plus the list glue around it, through \resumeProjectHeading. A job's second row
#: holds employer and location; a project has neither, and the row it used to spend
#: on `Personal project` / `Open source` is given back to the Bullets
#: (docs/adr/0057-the-page-reads-like-a-resume.md §3). Measured by the probe like
#: every other element here; a project header that wrapped onto a second row would be
#: caught by the Overflow check before it cost a line nobody granted.
PROJECT_HEADER_LINES = 1

#: Characters of plain prose that fit on one Bullet line, at the template's 490.31pt
#: Bullet text width. Measured from the widest realistic résumé sentence (4.915pt per
#: character), not an average. The bullet-length lint enforces it pre-compile, and it
#: also bounds a Skills row's comma list, which sits one list level shallower and is
#: therefore wider — so predicting a row's width at this rate never under-counts.
CHARS_PER_BULLET = 99

#: The same count for BOLD characters, which are wider. A Skills row is
#: `\textbf{<label>:} <skills>`, so charging the label at the plain rate would
#: over-promise — the one direction this file forbids. Measured the same way, from
#: the widest realistic label rather than an average
#: (docs/adr/0020-skills-section.md §6).
BOLD_CHARS_PER_BULLET = 80

#: A Skills category row's first typeset line, and each line after it. IN POINTS —
#: see the stated exception in the docstring above. The first line is DEARER,
#: because it pays the list's own inter-item glue and a line inside a row does not,
#: which is why these are two numbers rather than one
#: (docs/adr/0021-skills-row-cost.md §1).
#:
#: The first line reads 14.00 rather than the 10.00 it read until 2026-08-10, and it
#: is the same number as BULLET_LINE_PT ON PURPOSE: a Skills row and an Experience
#: Bullet are both one item in a list of the page's body text, and they now keep the
#: same distance from the item above. The old value set the rows 2pt tighter than
#: \small's own leading — see docs/calibration.md's entry for that date.
SKILLS_ROW_PT = 14.00
SKILLS_ROW_WRAP_PT = 12.00

#: The entry arc's lead line (docs/adr/0032-the-entry-arc.md §4) — one unbulleted
#: line, always. Fixed at 1 by decision, not derived from a measurement: the
#: calibration probe confirms it costs no more than one BULLET_LINE_PT (11.56pt
#: measured), which is what makes charging the integer 1 safe rather than assumed.
LEAD_LINES = 1

#: Characters of plain prose that fit on the lead's one line. Measured the same way
#: as CHARS_PER_BULLET — widest realistic sample wins — but against the lead's OWN
#: \linewidth, which is wider: the lead continues \resumeSubheading's own item, one
#: list level shallower than a Bullet's nested itemize, so it must not reuse
#: CHARS_PER_BULLET.
LEAD_CHARS = 114

#: The same count for BOLD characters on that same line — LEAD_CHARS's twin, and the
#: constant docs/adr/0046-every-impact-figure-and-the-declared-keyword.md declined to
#: take and named the terms for taking later. It is here because the lead now carries
#: emphasis, and `check_lead_lengths` charges its bold spans at LEAD_CHARS /
#: BOLD_LEAD_CHARS.
#:
#: A SELECTION EVENT, not a layout tweak, in this file's own words: it shortens what a
#: lead may say whenever a lead says something bold, which changes which evidence
#: reaches the page. It is committed on its own, with nothing else in the change.
#:
#: MEASURED, and that is the point of it rather than an incidental. `0046` §6 proved
#: the bold penalty is a property of the FONT and not of the column — both counts are
#: one width over a pt/char rate, so the width cancels — and that proof is what let the
#: Summary be charged for bold with no constant of its own. The same reasoning would
#: have derived this number, and `0046` refused to derive it: *"If this is reopened it
#: is reopened as a calibration, with LEAD_CHARS's bold twin measured off a compiled
#: page."* So it is measured, at the lead's own 514.40pt, from the widest realistic
#: bold span a lead carries (6.396 pt/char, `~30% GPU spend`) — and the probe now
#: checks the width-independence claim at a third width instead of trusting it.
#:
#: THE MEASUREMENT COMES OUT DEARER THAN THE DERIVATION, and the difference is the
#: sample family rather than the font. A lead's penalty is 114/80 = 1.4250 where a
#: Bullet's is 99/80 = 1.2375, because LEAD_CHARS is measured off lead SENTENCES —
#: narrow prose at 4.510 pt/char — while this is measured off bold SPANS, which are
#: figures and technical names and run wide. Both are the worst realistic sample of
#: what the element actually sets in that weight, which is the rule everywhere here,
#: and the dearer number is the safe direction.
#:
#: 80 IS THE SAME NUMBER AS BOLD_CHARS_PER_BULLET AND THE TWO ARE UNRELATED. That one
#: is a Skills label with its colon at the Bullet's 490.31pt; this is a lead's bold
#: span at 514.40pt. A wider line divided by a wider worst case landed on the same
#: integer. Do not fold them together — the next re-measure moves them apart.
BOLD_LEAD_CHARS = 80

#: The Summary — one unbulleted paragraph under the page's first section heading
#: (docs/adr/0044-the-page-opens-on-a-summary.md). Fixed at 2 by decision, not
#: derived, the same standing LEAD_LINES has. What the calibration owes it is a check
#: rather than a derivation, and there are two: the whole section measures 54.39pt
#: against the 56.00pt it is charged, and a three-line Summary measures over the
#: ceiling render.py enforces (32.89pt) while a two-line one measures under it
#: (20.89pt).
#:
#: THIS IS NOT THE WHOLE CHARGE, AND THAT IS WHY THE FIRST CHECK READS 56 AND NOT 28.
#: Since 2026-08-11 the prose sits under a `\section{Summary}`, and SECTION_LINES
#: charges the heading — so the page pays 4 for this element, 2 here and 2 there. What
#: was NOT added is a constant of its own: the heading is the same `\section` every
#: other section uses, and a second name for an element already charged is the thing
#: this file refuses (see ENTRY_HEADER_LINES).
#:
#: THE TWO HALVES CANNOT BE MEASURED APART, which is a fact about `\section` rather
#: than a shortcut. It contributes its space through `\addvspace`, which MERGES with
#: the skip already on the vertical list instead of adding to it, so the glue between
#: the heading and the paragraph belongs to neither on its own. Cut only the paragraph
#: and the two headings that meet merge, reading 38.00pt for a block nowhere near it;
#: cut only the heading and the paragraph lands on the header's glue instead. So the
#: probe prices the pair, which is also exactly what the budget spends.
#:
#: CHARGED UNCONDITIONALLY, like HEADER_LINES and unlike LEAD_LINES. The Packer runs
#: before a word is composed and cannot see whether a Summary arrived, so the page
#: always carries one and bullet_budget always subtracts this — and, since the
#: Addendum, the heading with it
#: (docs/adr/0044-the-page-opens-on-a-summary.md §5).
SUMMARY_LINES = 2

#: Characters of plain prose that fit in those two lines, at the Summary's own
#: 525.24pt \linewidth — the widest on the page, because the block sits at top level
#: outside every itemize. Neither CHARS_PER_BULLET nor LEAD_CHARS may stand in for it.
#:
#: THE ONE COUNT HERE THAT IS NOT A RATE TIMES A WIDTH, and the reason is that it
#: bounds TWO lines rather than one. For a one-line element "how many characters fit"
#: and "how many typeset lines is this" are the same question, so a worst-case
#: pt/char and a division answer it. A paragraph breaks at word boundaries, and the
#: division assumes a first line filled to the last scaled point — which comes out
#: about a word generous: 231 against the 227 that actually fit, on the same sample.
#: So the probe boxes every word-prefix of every sample and takes the longest that
#: measures inside the ceiling, worst sample winning as everywhere else.
#:
#: It is the composer's tape, not the gate. The gate is render.py's `check_summary_fit`,
#: which reads the height TeX measured — because a Summary that runs to three lines
#: breaks legally, warns about nothing, and would spend a line of evidence nobody
#: granted (docs/adr/0044-the-page-opens-on-a-summary.md §6).
SUMMARY_CHARS = 220
