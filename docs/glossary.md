# Glossary

The words the skills and tools use, in one place. Each term is defined the way the code uses it;
the decision behind it is in `docs/adr/`.

## The bank

**Bank** — `bank/`: everything the user has told the system about their work, as Markdown files.
The only source of facts for any page. Private, ignored by this repo, with its own local git.

**Entry** — one file in the bank: one job, project, position of responsibility, extracurricular or
certification. Its filename is its slug (`helios-payments`), which never changes. Its frontmatter
(`title`, `org`, `location`, `started`, `ended`, and on a project `stack` and `link`) builds the
entry's header on the page.

**Supporting entry** — a `responsibility`, `extracurricular` or `certification`. It never competes
for Bullets and renders as at most one row in a supporting section.

**Claim** — one `## c<n>` section of an Entry: one accomplishment. Ids are sequential, never
renumbered and never reused. A Claim holds an Assertion, Evidence, and optional fields: `number`,
`provenance`, `confidence`, `needs-interview`, `skills`.

**Assertion** — the Claim's neutral one-sentence core fact, not angled at any posting.

**Evidence** — the surrounding detail the user gave in the interview: what was there before, who
asked, what changed, how they know. Never printed as written; every fact on a page must be in or
entailed by it.

**Provenance** — how solid a stored `number` is: `measured` (a dashboard, benchmark, query) or
`estimated` (anything else, including a remembered figure). An estimate always renders softened
(`~30%`, `30%+`).

**Downgrade-only** — a page may state a Claim's facts more cautiously than the bank does, never
more confidently: it can soften or (on stated grounds) drop a figure, never invent, harden or grow one.

**Confidence flag** — `confidence: uncertain`, set only when the user doubts a specific fact. It
raises a Fork on every run that places the Claim.

**Lead** — an Entry's optional `## lead` block: a **Situation** (what things looked like before)
and/or an **Aggregate** (a total across several Claims, with its own `number` and `provenance`).
It can print as one unbulleted line under the entry header; off by default.

**Merge** — 2–3 Claims of one Entry printed as one Bullet, for two halves of one accomplishment.
Declared in `scores.md`; a `## merge <ids>` bank block stores the group's summed figure.

**Static profile** — `bank/profile.md`: name, contact details, Education and the optional
`## Standing` block (the user's own description of themselves, used for the Summary). Written by
hand; never competes for space.

**Deepening queue** — every Claim marked `needs-interview: yes`. Not a file — a grep over `bank/`.

## Sessions

**Ingestion** — `/ingest`: one sitting reads one source, interviews the user and writes one Entry.

**Return door** — an `/ingest` session on an Entry that already exists: to add new work, deepen a
marked Claim, or merge two Claims that describe the same work.

**Parking** — ending a Claim the interview could not dig further: it is still written, marked
`needs-interview: yes`.

**Shallowness checks** — the four tests `bank-audit` applies: a **Shallow claim** never says what
changed, or its Evidence adds nothing a different posting could use; a **Shallow entry** has fewer
than three Claims, or no Claim says how big the work was.

**Hole** — work that was never ingested at all. Only meaningful against the postings actually run
(`runs/*/gaps.md`).

**Recurrence** — how many past runs' Gap reports raised the same territory. The only standard
`bank-audit` judges the bank by.

## A tailoring run

**Run folder** — `runs/<slug>/`: one application. `jd.md` (the posting) goes in; every working file
and the PDF are written beside it.

**Fit rubric** — the fixed scale each Claim is scored on against the posting: 1.0 direct must-have,
0.7 adjacent or nice-to-have, 0.5 transferable, 0.2 same field, 0.0 unrelated.

**Bullet floor** — 0.50. A Claim scored below it never takes a line.

**Entry score** — the mean of an Entry's top three Claim scores at or above the Bullet floor. It
decides who shrinks first when the page runs out of lines.

**Packer** — `tools/pack.py`. Pure arithmetic over `scores.md`: which Entries place, how many
Bullets each gets and at what width. It never reads the bank.

**Slot** — one Bullet position the Packer grants an Entry.

**Width** — the typeset lines a Bullet is granted: `1` (the default, ~95 characters) or `2`.

**Depth cap** — the most lines one Entry's Bullets may take on a page.

**Allocation** — `allocation.md`, the Packer's output. Its **Silent calls** section logs every
decision a rule made; its **Did not place** section is the **Omission view**: every Entry and Claim
that lost, with its score and reason.

**Checkpoint** — the moment before writing where the run shows the user its **angle** (how it read
the posting) and the Omission view, and asks any **Forks**: questions only the user can answer. A
**Notification** is said and not asked. Recorded in `checkpoint.md`; its `## Decided by rule`
section logs what the run decided itself, including any stored figure left off a Bullet.

**Write-back** — a Checkpoint answer that changes the bank: an **add** (a new Claim, marked
`needs-interview: yes`) or a **revise** the user states explicitly.

**Summary** — the two-line opening of the page: who the person is, by name and evidence. No figures.

**Category row** — one labelled row of the Skills section (`Languages: Go, Python`). Each skill
cites a Claim whose `skills:` line names it.

**Opener table** — `scores.md`'s optional `## Openers` table: which Claim or merge group opens each
placed Entry's block. Not to be confused with the **opening word** rule: one first word at most
twice per page and never twice in one Entry.

**Gap report** — `gaps.md`, the run's second deliverable: what the posting asked for that the page
doesn't claim, in three **Gap classes** — *nothing in the bank*, *too shallow to claim it* (names
the Claim), *you have it, the page did not*.
