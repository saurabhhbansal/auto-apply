# A supporting section is earned by the posting, or paid for out of the room left over

**Status:** accepted

## Context

The bank holds two Entry types, `job` and `project`, and they are the two that
**compete** — the Packer seats them, the Entry floor reserves them, the Bullet column
argues them. Three kinds of evidence the maker actually holds have had nowhere to go:

- **positions of responsibility** — placement coordinator, club secretary, chapter
  lead, teaching assistant;
- **extracurricular activities** — a sport played at some level, a society run, a
  volunteering commitment, a community organised;
- **certifications** — a credential earned from an issuer on a date.

They are not jobs and not projects, and filing them as either is wrong in a way that
does damage rather than being merely untidy. A certification filed as a `job` would be
reserved a minimum block by the **Entry floor** the moment one of its claims cleared
the **Bullet floor** — header, lead and a Bullet, five lines, on every posting,
unconditionally. A placement coordinator role filed under `bank/jobs/` would rank in
the same pool as American Express and could take Bullet lines off it.

Both failures have the same root: **the competition is the wrong instrument for this
material.** What a certification is worth to a page is not *how well does it argue
against this posting compared to a Kafka consumer*; it is *does this posting care that
you hold credentials, and is there room*. That is two questions, and neither of them
is a Fit score.

There is also a second, quieter problem this material is the natural answer to. The
page budget is `PAGE_LINES` and the **Room** line reports what the width pass left
**unspent**. On a thin bank that number is not zero, and unspent lines are white space
at the bottom of a one-page résumé — the one defect the system could see coming and
had nothing to spend on.

Resolved alongside the ingestion side, which needed the same three types to have a
folder to be written into.

## Decision

### 1. Three new Entry types, three new folders, the same Entry file

`bank/responsibilities/<slug>.md`, `bank/extracurriculars/<slug>.md` and
`bank/certifications/<slug>.md`, carrying `type: responsibility`,
`type: extracurricular` and `type: certification`. Everything `0005` fixed holds
unchanged: the filename slug is the Entry id, the folder and the `type` must agree,
frontmatter is the same required set (`type`, `title`, `org`, `location`, `started`,
`ended`), claims are `## c1`, `## c2` with the same fields and the same
`**Assertion:**` / `**Evidence:**` body.

**A claim-type extension was rejected** (see below). A new *folder* per type is what
the storage format already spends to say *this is a different kind of thing*, and it is
what makes `ls bank/certifications/` the answer to *what credentials do I hold* without
a query.

Collectively these three are **supporting entries**, and the sections they render into
are **supporting sections**. The two that compete keep their own name — a supporting
entry is not an Entry that lost, it is an Entry that never entered.

### 2. A supporting entry never enters the Score table, and so never competes

It is **not scored**. It gets no row in `scores.md`'s claims table, no **Claim score**,
no **Entry score**, no place in the reservation queue, no Bullet slot, and it cannot
shrink or be shrunk. `pack.py` learns of it through one new table and nothing else.

This is the load-bearing half of the decision and it is what keeps every existing
guarantee intact. The **Entry floor**, the **Epsilon tie band**, **Sharing the lines**,
the **Omission view**'s two halves, **Evidence outranks room** — none of them gains a
case. A page with three supporting sections on it packs its Bullets **byte-identically**
to the same page without them, minus whatever lines the sections were charged.

### 3. The row: a built label, an optional composed tail, one typeset line

A supporting entry renders as **at most one row**, never a block:

```
Certifications
  • AWS Certified Solutions Architect – Associate — Amazon Web Services, Mar 2025
Positions of Responsibility
  • Placement Coordinator — Training & Placement Cell, Aug 2024 – May 2025. Ran the
    drive for six branches and 40+ visiting companies.
```

- **The label is built, never typed** — `title` in bold, then `org` and the dates,
  composed by the **Renderer** from the entry's own `started`/`ended` exactly as an
  Entry header is (`docs/adr/0031-the-entry-header-is-built.md`). One departure, and it
  is general rather than a type special-case: **where `started` and `ended` are the same
  month the row prints that one month** rather than a range to itself, which is what a
  credential with no expiry looks like.
- **The tail is composed per run from exactly one Claim**, cited like a Bullet, bound by
  **Downgrade-only** and the **Claim-level trace** like a Bullet, and traced by the
  **Number-trace check** like a Bullet. It is **optional**: a supporting entry the bank
  holds no claim for, or whose claim will not fit the line, renders as a bare label —
  which is what a certification line on a résumé usually is, and is not a defect.
- **One typeset line, hard.** A row that measures over sheds its tail or shortens it;
  it never wraps. This is what lets the charge in §6 be arithmetic over a row count
  rather than a third Packer pass — the Skills section needs one because its rows are
  *allowed* to wrap and a supporting row is not.

The row is written in `bullets.md` under a single `## Supporting` section, in the
allocation's order, and the **Renderer routes it to a section by the entry's `type`** —
the same routing the Template already does for `job` and `project`.

### 4. The first trigger: the posting's call, declared in `scores.md`'s `## Sections`

Judgement, so it sits **above the seam** and is written down where a git diff can read
it. Every supporting entry in the bank gets a row, every run, including the ones that
are not called — the **Omission view**'s reason for the claims table applies here word
for word: an entry left out of the table cannot lose visibly.

```markdown
## Sections

| section | entry | ended | signal | reason |
|---|---|---|---|---|
| certifications | aws-saa | 2025-03 | y | the ask names "AWS Certified Solutions Architect" |
| responsibilities | tnp-coordinator | 2025-05 | n | the posting's only leadership word is "team-oriented environment" |
```

`ended` is a **copy of a bank field**, carried for the same reason the claims table
carries one — the Packer reads `scores.md` and only `scores.md`, and it orders the
residue fill by recency. The **Renderer** checks the copy against the bank and refuses a
run where they disagree, exactly as it does for a placed Entry.

**A section is called when at least one of its entries is signalled `y`.** The tests
the signal is judged against, and the exclusions that stop it firing on every posting,
are `tailor`'s and are stated there precisely. What this ADR fixes is that the reason
column must **quote the posting's own phrase** — the same discipline a **Category row**'s
label is held to, and for the same reason: a signal that cannot be traced to words in
`jd.md` is a section invented to fill a page.

### 5. The second trigger: the room the width pass left unspent

Arithmetic, so it sits **below the seam** and is the Packer's alone. The number is one
that already exists and is already printed: the **Room** line's `N line(s) unspent` —
what is left after every Entry is seated, every lead charged, every granted second line
paid for and every *called* supporting section reserved.

**That number is the white space.** It is not a heuristic about how the page looks; it
is the page budget's own residue, and a résumé that ends two inches above the bottom
margin ends there because that residue was positive.

So: after `grant_widths`, the unsignalled supporting entries are offered the unspent
lines in a **fixed order** — certifications, then positions of responsibility, then
extracurriculars; within a section by `ended` descending, then slug ascending. An entry
is taken **only if the whole of it fits**: its own row, plus `SECTION_LINES` for the
heading when it is the first row of a section nothing has placed yet. One that does not
fit is **skipped and the next is offered** — leapfrogging inside the supporting fill,
which is `pack_page`'s own rule for units inside one entry and is safe here for the
same reason: nothing is competing on merit, so passing over a section that will not fit
costs no one their place.

**Order of payment is Bullets, then widths, then supporting rows.** *Evidence outranks
room* already says a second line is paid out of what the evidence did not want; this
says a supporting row is paid out of what the second lines did not want. On a full page
nothing supporting places at all, which is correct — a full page has no white space to
answer.

### 6. What a section costs, and why it adds no constant to `config.py`

A supporting row is **the same element as a Skills row**: `\resumeItem` carrying a bold
label and plain text, inside the same list geometry with the same zeroed glue. It is
charged the same way, which means `SKILLS_ROW_PT` now charges two call sites:

```
section points = SKILLS_ROW_PT x rows        (a supporting row never wraps, so
charge         = ceil(points / BULLET_LINE_PT) + SECTION_LINES     never SKILLS_ROW_WRAP_PT)
```

1 row costs 3 lines, 2 costs 4, 3 costs 5, 4 costs 5.

**`config.py` gains nothing**, and that is the rule rather than an economy: what may
never be added there is *a second name for an element already charged*. This is the
`ENTRY_HEADER_LINES` situation exactly — two macros, one constant, held together by a
calibration probe check rather than by a promise. The probe gains **"a supporting row
costs the same as a Skills row"** beside **"an Education row costs the same lines as an
Entry header"**, and if it ever fails the fix is to tighten a macro, never to split the
constant.

### 7. Where the sections sit, the cap, and the absent floor

On the page, after Skills and before Education: **Certifications**, **Positions of
Responsibility**, **Extracurriculars**. Bottom-of-page is where the white space the
second trigger spends actually is, and it is where a reader expects them.

**`MAX_SUPPORTING_ROWS = 4` per section.** A fifth credential is real and is not worth a
fifth line of a one-page résumé; the entries past the cap land in the Omission view like
any other loss, with the cap named as how they lost.

**There is no minimum-rows floor, and the departure from the Skills section's two is
deliberate.** Skills' floor exists because its rows are *interchangeable breadth* — one
surviving row spends three lines to show one thing, and the one thing is a category
label nobody asked for. A single certification the posting **named by name** is not
interchangeable with anything, and three lines is a fair price for the page carrying
the credential the ask spelled out. A single row that arrived through the **room
trigger** is paying with lines that would otherwise be white space, so its floor is the
arithmetic in §5 and needs no second rule.

### 8. What binds a supporting row, and what does not

**Binding**, all of it for the same reason it binds a Bullet — the maker defends every
word of it in the room:

- **Downgrade-only** and the **Claim-level trace**: every word of the tail is present in
  or entailed by the cited Claim's Evidence.
- **The Number-trace check**: a figure in the tail traces to its Claim at
  equal-or-softer Provenance.
- **The spelling check**: the page has one convention, and a supporting row is on the
  page.
- **The Overflow check**: a new `supporting` element kind, one marker per row.

**Not binding**, and each absence has a reason rather than being an oversight:

- **The spread rule** and **no opening word twice** — the **Composed set**'s two other
  checks are about the *Bullet column*, a run of full sentences a reader reads as one
  block. A row is a label and a clause; a bare label has no opening word to be twice,
  and a spread rule over labels would be a rule about the maker's job titles.
- **The number-kept mirror** (`check_number_kept`): a Bullet that drops its Claim's
  figure owes a **Decided by rule** line, because a Bullet's whole job is to carry the
  claim. A supporting row's job is to carry the *credential*, and its one line is mostly
  spent on the label — a tail that cannot afford the figure is the normal case, not a
  downgrade anyone decided.
- **The `## Openers` table**: a section of rows has no block to open.

### 9. The Shallowness checks do not reach a supporting entry

The two **Shallow entry** checks — *fewer than three claims* and *no claim carries a
sizing fact* — are checks about an Entry's ability to **fill a block**. A supporting
entry has no block: three claims would buy it nothing, and a certification with one
claim is not thin, it is a certification.

The two **Shallow claim** checks reach a `responsibility` and an `extracurricular`
claim **unchanged** — that work has a before and an after and the interview digs for it
like any other. A `certification` claim is exempt from *it says what changed*, and the
exemption is narrow and stated: the claim a credential makes is that it was **earned**,
which is a fact about the maker rather than a difference afterwards. *There is room to
re-angle it* still binds, and is what the interview is actually for on a certification —
a cert whose Evidence says only *"passed the exam"* can never be the row that answers a
posting, and a cert whose Evidence says what it was taken for and what it let the maker
do can.

`bankcheck.py` prints what the supporting entries cost and what they would cost the
page, on an **advisory line that never changes the exit code** — the standing
`static_profile_cost` and `standing_advisory` already have, and for the same reason:
what belongs in these sections is the maker's judgement about a life.

## Rejected

- **A claim-type extension — `kind: certification` on a claim inside an existing
  Entry.** Rejected on the field test and on the filing. A certification is not an
  assertion about a piece of work at some employer, so there is no Entry it belongs
  inside; the alternative is one synthetic Entry called `certifications` holding a claim
  per credential, which is a folder wearing an Entry's clothes and loses the frontmatter
  — issuer, date — that the row is *built* from.
- **Filing all three under one `bank/supporting/` folder with the type in the
  frontmatter.** Rejected: the folder is the type everywhere else in the bank, and one
  folder would make the type a field that can silently disagree with nothing.
- **Making them compete — scored Entries the Packer seats like any other.** Rejected in
  §2. It would put a certification on every page at any score above the Bullet floor,
  and it would let a club secretaryship take a line from a job.
- **A per-section `y`/`n` signal instead of per-entry.** Rejected: a posting that names
  *AWS Certified Solutions Architect* has called for **that credential**, not for the
  maker's food-safety certificate; the per-entry signal rolls up to a section for free
  and the section-level one cannot be recovered.
- **Charging supporting rows a `SUPPORTING_ROW_PT` of their own.** Rejected by
  `config.py`'s own stated rule: it is the same element, and a second name for it is
  exactly what would let the two drift apart silently.
- **Letting a supporting row wrap to two lines, like a Skills row.** Rejected: it buys a
  longer tail and costs a third Packer pass, because a wrapping row's height is a fact
  about composed text and the budget is set before composition. The tail is a clause, and
  a clause that will not fit is a clause to cut.
- **A "the page looks empty" heuristic** — measuring the compiled PDF's content extent
  and re-running composition when it ends high. Rejected: it puts a second composition
  pass after the compile, it makes selection a function of the PDF, and it re-derives
  badly a number the budget already holds exactly. The **Room** line is the same fact,
  computed before a word is composed.
- **Filling white space with more Bullets instead.** Not rejected, already true — the
  Packer spends every line it can on evidence *first*, and the residue the supporting
  fill sees is what nothing else wanted. A bank with more qualifying claims produces
  fewer supporting rows, by construction.

## The cost, stated rather than waved past

**Two triggers means two reasons a section can be on the page, and only one of them is
about the posting.** A maker reading a résumé that carries a Certifications section may
be reading a page that argues credentials, or a page that had three lines spare. The
allocation says which, on the row, every run — but the PDF does not, and cannot.

**The room trigger makes the page a function of how full it is.** Add one claim to the
bank, and a supporting section that placed last week does not place today, with nothing
wrong. That is not a determinism break — the same bank and the same JD give the same
page, which is what **Material determinism** claims — but it is a new way for a small
bank edit to move something visible, and it lands on the section that had the weakest
claim to be there.

**A supporting entry's material is dug out by an interview and mostly does not
render — and "mostly" is generous.** The row is one typeset line and the bold title is charged at
`BOLD_CHARS_PER_BULLET`, so a 33-character credential name spends about 41 of the line's 103 before
the issuer and the dates are on it. On a long label there is **no room for a tail at all**, and the
honest reading is that a supporting row is usually a built label and nothing else. That is the right
shape for a résumé's Certifications section and a real loss on a position of responsibility, where a
clause about what was actually done is worth more than the title. The tail is kept anyway, because
where the label *is* short the clause is the difference between a name and a claim — and because the
alternative, letting the row wrap, costs a third Packer pass to buy a second line for the page's
least important section. A maker who spends a full session on a certification should be told the row
it buys is a name; `ingest` §9.1 says so before the digging starts.

## Consequences

- **`tools/bank.py`** gains three Entry types and three folders, and one derived date
  string for the row (§3).
- **`tools/pack.py`** gains the `## Sections` table, the reservation for a called
  section, the residue fill, a `Supporting:` line, a `## Supporting` section in the
  allocation, and a third subsection of the Omission view. Nothing else in it moves.
- **`tools/render.py`** gains the `## Supporting` section of `bullets.md`, the row's
  built label, the one-line length check, the `supporting` marker kind, and the
  `ended`-copy check for supporting entries.
- **`templates/resume.tex.j2`** gains one macro and three conditional sections, each
  with its `%% AUTOAPPLY:element:supporting:<slug>` markers. The blob moves, so
  `docs/calibration.md` is re-run — and the probe gains the check in §6.
- **`tools/config.py`** gains no constant and one paragraph saying why.
- **`ingest`** gains the three types: what a supporting entry's wide pass and depth pass
  look like, and what its frontmatter means.
- **`tailor`** gains §2's `## Sections` table with the precise detection rules, §3's
  third pack argument, §5's supporting-row composition rules, and the placement
  reporting.
- **`bank-audit`** inherits §9: the Shallow entry checks skip supporting entries, and a
  certification claim is exempt from *it says what changed*.
