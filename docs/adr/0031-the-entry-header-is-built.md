# The entry header is built, not typed

**Status:** accepted

## Context

`runs/auxo-ai` at `e93d01c` is the third composition of that page — the re-run under `0030`, on a
bank and a JD that did not move. Everything the last four tickets went after is gone from it: every
stored figure is on the page, the spread came off the cap, the openers are seventeen different
words, one spelling throughout (#54, #62).

Every one of those faults was in a **Bullet**. Read the page for the parts that are *not* Bullets and
four more turn up, and they have one thing in common: nothing anywhere looks at them (#64).

**Everything that competes for a slot is guarded.** A Bullet is scored, packed, width-granted,
length-checked, spread-checked, opener-checked, spelling-checked, number-traced, skills-traced and
overflow-checked. **Everything that never competes is passed through verbatim from a file nobody
validates** — the Entry header line, the Skills section heading, the Education rows. So the guarded
half of the page is immaculate and the unguarded half is where every visible inconsistency on it
lives.

### Fault A — two date formats, four lines apart

From the shipped `resume.tex`:

```
{Product Development Intern}{Jan 2026 -- Jul 2026}
{Data Scientist Intern}{June 2025 -- July 2025}
```

`Jan`/`Jul` above `June`/`July`, on the same page, in the same column, in adjacent blocks. The source
is `dates:` in the Entry frontmatter — free text, typed once at ingestion and copied to the page
untouched. `bankcheck.py` does not look at it, and `bank.py`'s `dates` property returns it as
written.

**And the bank already holds the same fact in a validated form.** `scores.md` carries an `ended`
column that `pack.py:330` refuses unless it matches `YYYY-MM` or `present`, and the recency
tie-break sorts entries on it (`pack.py:227`). So an Entry's end date exists **twice**: once
machine-readable and strictly checked, once as prose nobody reads. On this run they agree. Nothing
makes them.

### Fault B — two location shapes

```
American Express   Gurgaon, Haryana, India      city, state, country
Xlscout            Mohali, Punjab               city, state
auto-apply         Open source                  not a location at all
sweatpact          Open source
```

Two jobs, two shapes. The two projects are a third thing, and correctly so.

### Fault C — a non-technical row under a technical heading

```latex
\section{Technical Skills}
  \resumeItem{\textbf{Collaboration:} Cross-team coordination, User acceptance testing,
              Business rules encoding}
```

`0020` decided a **Category row**'s label is *"named per JD, from the posting's own vocabulary"*, and
the AuxoAI posting states communication and collaboration as plainly as any technical must-have. So
the row is right and the label is right. The heading above it is hardcoded in
`templates/resume.tex.j2` and is the thing that is now wrong. **`0020` freed the labels and left the
heading behind.**

### Fault D — the Education block is unpriced

`bank/profile.md` yields two `\resumeEducationRow`s at `ENTRY_HEADER_LINES = 2` each, and
`pack.py:514` charges the Education `\section` heading whenever there are rows at all. With
`HEADER_LINES = 3` that is **9 of `PAGE_LINES = 50` spent before a single piece of evidence
competes**, against the 32 lines every job and project on the page shared between them. One of those
rows is `Guru Nanak Public School — CBSE Grade 12`.

Education never competes, by `0013` §7, and **that is not reopened here**. What the maker has no way
to see is what the static half of the page costs the evidential half. The arithmetic is over
constants that already exist and nothing prints it.

## Decision

### 1. `dates:` stops being prose

Entry frontmatter loses `dates:` and gains two fields:

```
started: 2026-01
ended:   2026-07        # or `present`
```

Both `YYYY-MM`; `ended` also takes the literal lowercase `present`. **Both are required, for a
project as much as for a job** — an entry with no start date has nothing to render, and the header
typesets the same way in Experience and in Projects.

`started` must not be after `ended`, which is the only ordering error the format admits and is
therefore worth the one comparison it costs.

**This corrects `0004` §3**, which named `dates` among the Entry's scalar metadata, and `0005`,
whose example prints `dates: 2023-01 – 2024-06`. The fact those recorded is unchanged: an Entry
carries its start and its end, for recency and for the header. What changes is that the fact is now
stored in the shape the rest of the build already validates instead of in prose.

### 2. The renderer composes the display string, and there is one house format

```
Jan 2026 -- Jul 2026
Jul 2026 -- Present
```

Three-letter month, four-digit year, `--` (the template's existing en-dash, unchanged), `Present`
for an open end. **Twelve three-letter months, no exceptions** — `Sep`, not `Sept`; uniform beats
idiomatic in a column of dates. `Present` is capitalised because it sits where a capitalised month
otherwise sits, and `allocation.md` keeps lowercase `present`, which is a machine field
`pack.py` already treats as a sort key.

The format is stated literally here because **this ADR is now the only place it exists in prose**.
It is composed by `bank.Entry.display_dates` and reaches the template through the existing `dates`
hole, so nothing downstream of the Renderer learns a new word.

Two entries cannot disagree about the shape of a date, because neither of them writes one.

### 3. The month pattern is owned by `bank.py` and restated in `pack.py`

The pattern already exists, as `pack.ENDED`. It is **borrowed, not invented**: `bank.py` gains
`MONTH_PATTERN` and `ENDED_PATTERN` and `pack.py`'s `ENDED` is restated from them.

**Restated, not imported, and that is forced.** `0006`'s seam says the Packer may import nothing but
the stdlib and `config`, which is what makes its bank-blindness a fact about the code rather than a
promise. `pack.py` already restates `CLAIM_ID` and `ENTRY_SLUG` for exactly this reason, with a
comment naming `bank.py` as the owner and calling the widening a two-file edit. This is the third
member of that set and follows it.

**The drift is closed by a test, not by a comment.** The suite is not bound by the seam:
`tests/test_bank.py` reads both files and asserts the two patterns are the same string. A drift
fails there rather than in a run six weeks later where a date the Packer accepts is a date the bank
refuses.

`config.py` is **not** the shared home. Its docstring is a contract — *"a set of numbers", "MEASURED,
NEVER ESTIMATED"* — and a regex living in it weakens that however well labelled, which is the same
argument `0030` §6 used to keep two judgement constants out of it.

### 4. The bank owns `ended`; `scores.md` copies it, and a disagreement halts the run

`scores.md`'s `ended` column **stays**. `pack.py` reads that file and only that file; `0006`'s seam
is not reopened, and the Packer gains no route to the bank.

But the column stops being a judgement and becomes **a copy of a bank field**. So `render.py` checks
the copy: it already parses `allocation.md` and already loads the bank, and comparing the two costs
one comparison per placed Entry. **A disagreement fails the run and names the Entry.** Two files
disagreeing about when a job ended is not a taste question, and `render.py`'s whole convention is
that a disagreement between artifacts halts and names the offender — it is the same standing
`check_structure` gives an allocation that has moved on from the bank.

This closes the last route by which the page can disagree with itself about when a job ended.

### 5. Location gets a stated shape, and the check advises rather than refuses

**`City, Region, Country` for a real place.** A location that is not a place — `Remote`,
`Open source`, `Self-hosted` — is whatever the maker writes and is left alone. That exemption is not
a type rule: a job can be `Remote` as easily as a project can be `Open source`, so what earns the
comparison is **carrying a comma at all**, which is the only signal a machine has that a value was
written as an address.

`bankcheck.py` **reports** — it does not fail — when the bank's addresses are not all written to the
same depth, compared by comma count and listed by entry.

**This is the one item here where the right answer is the maker's taste**, and the check is written
to admit it. `Gurgaon, Haryana, India` and `Mohali, Punjab` are both correct addresses; what is
wrong is the pair of them in one column. `Remote` is not a third shape of address — it is a
different kind of answer, and the check is silent about it. A rule that refused the bank would be the repo overruling a
person about their own address — and a comma count is a weak enough proxy that it would be wrong
sooner or later. Everything else in this ADR is a shape a machine can settle. This one is a nudge,
and it is labelled as one.

### 6. `Technical Skills` becomes `Skills`

One word in `templates/resume.tex.j2`. Never wrong, whatever `0020` lets a label be, and it costs no
recalibration: the heading's height is `SECTION_LINES` regardless of the string it carries.

### 7. `bankcheck.py` prints what the Static profile costs

Not a failure and not a rule. One line on every run of `tools/bankcheck.py`, above `bank parses`:

```
Static profile: header 3 + Education heading 2 + 2 row(s) at 2 = 9 of 50 page lines.
```

**The heading is in the sum because `pack.py` charges it in the sum** — `bullet_budget` counts an
Education `\section` whenever `EDUCATION_ROWS > 0`, and the Template drops the section whole when
`profile.education` is empty. The heading exists because the rows do, so it is part of their price.

It reads `HEADER_LINES`, `SECTION_LINES`, `ENTRY_HEADER_LINES` and `PAGE_LINES` from `config.py` and
counts the `### e<n>` rows in `bank/profile.md`. It touches no data and reopens nothing: `0013` §7
stands, Education still never competes, and the maker is simply told the number. What he does about
the Grade-12 row is his business — which was the whole finding.

Where there is no `bank/profile.md`, the line says so and the check still passes. An empty bank
parses, and a fresh clone has no profile.

### 8. No recalibration is owed

Nothing here changes the template's geometry, fonts, margins or a macro. §6 changes a heading's
**text**, not its height, and `SECTION_LINES` charges the heading either way.

**Say it explicitly, because the template's blob hash changes.** `config.py`'s docstring pins the
template at a blob hash and instructs a re-run of `docs/calibration.md` when it stops matching. This
is the **first template edit that moves the hash without owing a re-measure** — `0022` faced the
near miss and got to say *"the template is not touched, so the blob hash stands"*, which is not
available here.

So the hash line is updated to the new blob, the five constants are not re-measured, and the
docstring gains the one sentence that keeps the pin honest: **the hash detects an edit, and whether
an edit owes a re-measure is a question about what changed.** A heading's string is not its height.
A reader who finds a mismatched hash still re-calibrates, because they cannot know which kind of
edit they are looking at — the pin is doing its job. The obligation this ADR discharges is to
record, at the one edit where the answer was *no*, why it was no.

## The cost, stated rather than waved past

**The migration lands where this repo's tests cannot see it.** The bank is private under `0019`, so
the four Entry files are edited and committed in the `bank` repo, and nothing in CI ever reads them.
The mitigation is that `bankcheck.py` is the migration's verifier and the schema change ships first:
an unmigrated entry fails the parse by name, loudly, on the next run of any skill. But an
unmigrated bank is a broken bank until the maker runs it, and that is a real window.

**`parse_allocation` narrows for the third time.** `render.py`'s reader ignores the Packer's prose on
purpose, so that a wording change is not a breakage — and §4 makes a third field contract, after
`0023`'s `Skills:` line and `0025` §6's granted width. The cost is the same each time and it is
compounding: changing the `### <slug> — <type> — ended <date> —` wording in `pack.py` now means
changing a regex in `render.py` and a fixture in `tests/test_render.py`. What buys it is that the
alternative is no check at all, since the allocation is the only artifact that carries the Packer's
copy of the date.

**`started` is required for an entry that may not have a clean one.** A side project that accreted
over a spring has no honest start month, and this makes the maker pick one. The alternative — an
optional `started` and a display string that copes with its absence — buys a half-empty header
column and a second format for the renderer to compose, which is what §2 exists to prevent. The
maker picks the month the work began in earnest, and no reader will ever know the difference.

**The location advisory can be ignored forever.** It prints, nothing enforces it, and a check nobody
acts on is a line of output that trains its reader to skip the block it sits in — which is the same
block §7's cost line lands in. Accepted knowingly: both are advisories on hand-edited personal data,
and the alternative for either is a rule this ADR has already argued should not exist.

## Rejected

**A Skills heading named per JD, from the posting's own vocabulary.** The consistent move — it is
exactly what `0020` did to the row labels, and the heading is the last hardcoded string in that
section. It loses to cost: a new template variable, a new escape path, a new hole for
`StrictUndefined` to fail on, and a heading that could come out named something odd on a bad run —
all to replace a word that is **already always true**. `Skills` is right for a technical row and
right for a collaboration row, which is more than a per-JD heading can promise.

**Keeping `dates:` and linting its format instead.** It would catch fault A and nothing else: the
same fact would still be stored twice, in two shapes, and `bankcheck.py` would be enforcing a
display convention on a file the maker hand-writes. A lint that demands `Jan 2026 -- Jul 2026` is a
worse version of composing it.

**Deriving `scores.md`'s `ended` from the bank at pack time.** It removes the copy entirely, and it
breaks `0006`: the Packer would have to read the bank, which is the one thing its design forbids.
The copy stays and is checked instead.

**Failing the run on a location shape.** See §5. A comma count is a proxy for a judgement about an
address, and the maker's own address is not the repo's to refuse.

**Holding the location rule to `job` entries only.** The first cut of §5 did, on the reading that a
project's location is the loose one. It fires on `orbit-analytics — Remote` in the fixture bank,
which is a job, and correctly written. The type is not what distinguishes an address from a
not-an-address; the comma is.

**Charging the Static profile, or letting Education compete.** `0013` §7 settled that Education never
competes and the profile is not a Bank entry. §7 prints a price; it does not levy one. Making the
Grade-12 row compete would be a different ADR against a different decision, and the read that
produced this one did not argue for it.

**Putting the month pattern in `config.py` so both files could import it.** The only place both
`bank.py` and `pack.py` may read from — and the file whose entire discipline is that everything in
it was measured off a compiled page. See §3.

## Consequences

- **The page can no longer carry two date formats**, because it carries none: the two dates it
  displays are composed from validated fields by one function. The format is `Mon YYYY -- Mon YYYY`
  and this ADR is where it is written down.
- **An Entry's end date exists in two files and they are checked against each other.** The bank is
  the owner; `scores.md` holds a copy; `render.py` refuses a run where they differ.
- **The bank gains a migration.** Four entries, `dates:` out and `started:`/`ended:` in, committed in
  the private `bank` repo under `0019`'s boundary and never in a PR here.
- **`bankcheck.py` grows a voice.** It was a pure pass/fail parse check; it now prints two advisories
  — the static profile's price and the location shapes — while keeping `bank parses` on stdout as
  the go-ahead the three skills read.
- **The Skills heading is `Skills`.** `0020`'s per-JD labels sit under a heading that cannot
  contradict them.
- **`0004` §3 and `0005`'s example are corrected** on the frontmatter's date keys. `0013` §7 and
  `0006` are surfaced and left standing.
- **No recalibration.** The template's blob hash in `config.py`'s docstring is updated, the five
  constants are not re-measured, and §8 says why.
