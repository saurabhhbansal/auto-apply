---
name: tailor
description: One tailoring run. A job posting in a run folder goes in; a one-page PDF résumé and a classified Gap report come out — score every Claim, pack, show the angle and what lost, halt only on a real fork, write the bullets, render, report the gaps.
---

# tailor

One run, **one run folder** — `runs/<jd-slug>/`, holding the posting in `jd.md`. A re-run
overwrites in place, which is what makes `git diff` mean something. Terms are defined in
`docs/glossary.md`.

**Before anything:**

1. **Find the run.** `/tailor <slug>` means `runs/<slug>/`. With no argument, list `runs/*/jd.md`
   and ask which one. If the user pasted the posting into the chat instead, ask them for a short
   slug (`acme-backend`), then write their text verbatim to `runs/<slug>/jd.md`. Never pick the
   slug yourself.
2. **Check the bank.** Run `python tools/bankcheck.py`. If it fails, or prints `Static profile: no
   …profile.md`, stop: the user copies `templates/profile.example.md` to `bank/profile.md` and fills
   it in. If `bank/jobs/` and `bank/projects/` hold no `.md` files, stop and point them at `/ingest`
   — there is nothing to tailor from.
3. **Check the history.** If `runs/.git` or `bank/.git` is missing, ask the user to run
   `git -C bank init && git -C runs init` (§9 commits into `runs/`).

**What this run is for.** A recruiter gives a résumé about seven seconds on the first pass, and a
hiring manager perhaps a minute on the second. The page has to survive both: scannable at a
glance (clear section headings, the right titles and employers, numbers that pop), and specific
enough on a close read that the reader believes it (real technologies, real scale, real results).
Everything below serves one of those two reads — or keeps the page honest, which is the third
thing it owes: **every line is something the user can defend in the interview.**

The spine, in fixed order:

```
jd.md ──► scorable? ──► terms.md (the posting's own words)
      ──► score every Claim, call the sections  ──► scores.md
      ──► pack.py                               ──► allocation.md  (reservation)
      ──► compose the Skills rows               ──► bullets.md, `## Skills` only
      ──► lengths.py, pack.py --skills-rows      ──► allocation.md  (final)
      ──► xray.py                               ──► xray.md        (advisory)
      ──► the Checkpoint: angle + what lost (always), notifications, forks (only when earned)
                                                ──► checkpoint.md, write-back
      ──► compose the Summary and every Bullet  ──► bullets.md, whole
      ──► the cold read, plainish.py, the evidence check, the merge verifier
      ──► lengths.py, render.py                 ──► resume.tex, resume.pdf
      ──► coverage.py                           (advisory)
      ──► gaps.md, commit
```

`python` below means the repo's `.venv/bin/python` where it exists.

## The four rules

1. **You judge relevance; the scripts own the arithmetic.** You decide what a Claim is worth
   against this posting; `pack.py` decides what fits. Never re-derive a score, a slot count or a
   page budget, and never hand-edit `allocation.md`. If the allocation looks wrong, the input is
   wrong — fix `scores.md` (your judgement) or the bank (the user's facts) and re-run.
2. **The bank is the source of facts, not of words.** Every fact in a line — metric, scope,
   technology, audience, outcome — must be present in or entailed by the cited Claims' Evidence.
   The wording is yours: verb, sentence shape, what to lead with, and the posting's name for work
   the bank describes in other words.
   *Forbidden:* a number no cited Claim carries, or one stated more precisely than its provenance;
   a technology, scope, audience or outcome no cited Claim carries; a title, seniority, headcount
   or duration the bank does not hold; promoting scope — *contributed to* never becomes *led*.
   **The test is the interview:** could the user defend this exact sentence to someone who asks
   "tell me more about that"? No script can check meaning, so this one is on you.
3. **`scores.md` is your judgement and nothing else.** When the user disagrees with a score, the
   bank is the repair surface — they change the claim, you re-run. A Fork answer is an input
   recorded in the run folder, never a pen taken to the table.
4. **Nothing reaches the page except through a file in the run folder.** No facts from memory,
   from other postings, or from what "this kind of role usually wants".

## 0. Company research — only when asked

The only part of a run that touches the web, and **it never fires on its own**: only when the user
asks for it (at the thin-JD question in §1, or at any halt). An unattended lookup risks the worst
failure there is — true facts about the wrong company.

1. **Does `jd.md` name a company at all?** If not, there is nothing to look up. Say so and stop.
2. **Identify.** Launch one general-purpose subagent and wait for its result before continuing:
   ```
   Agent(subagent_type: "general-purpose", prompt:
     "Read .claude/skills/tailor/company-research.md and follow it exactly.
      Pass: identify.
      The JD names: Acme.")
   ```
   Put a single candidate to the user as a question (*"I think this is acme.dev, the Berlin
   data-infrastructure company, ~80 people — right?"*). Two plausible candidates, or nothing, is
   the finding: stop there. Never pick the bigger one.
3. **Read** — only after a yes, same launch with `Pass: read.`, the confirmed name and URL, and
   the question being asked. Pass only those; the brief is the subagent's.
4. **Write `runs/<jd-slug>/context.md` the moment the finding returns** — a `## Company` block
   (name, URL, confirmed by the user, date) and one dated `## <date>, at <where>` block per pass
   with **Asked**, **Finding** (each sentence citing its URL; drop any that cite none) and the lean.
   Later passes append. A dead end still writes its block.

**Standing: below `jd.md`, always.** A finding may change how you *read* the posting; it may never
add a requirement, and no score's reason and no `gaps.md` line may rest on it. It is not a Claim
and nothing on the page cites it. Research informs a Fork; the user still answers it. On a re-run,
if `context.md` exists, read it and launch nothing unless the user asks a new question.

## 1. Is the posting scorable?

Read `jd.md` whole. Ignore the company blurb, benefits and EEO text, and look for two things:

- **the work** — what this team builds, runs or owns;
- **the ask** — what they want from a person: technologies, experience, scope, seniority, and the
  must-have / nice-to-have split if there is one.

**Either one missing, or both present in under ~80 words → stop and ask.** The usual cause is a
half-paste, and it is usually visible (text ends mid-sentence, a heading with nothing under it):

> *"`jd.md` has what the team does but nothing about what they want from you — it stops right
> after 'What you'll do'. Can you paste the rest?"*

Three ways forward: they paste the rest; they ask for company research (§0 — which can sharpen
your reading but can never supply the missing requirements); or they say score it as it stands,
and you note once that scores will be thin and go. Never fill the gap yourself.

## 2. Score every Claim

Read every Entry under `bank/jobs/` and `bank/projects/`. **Every Claim gets a row, including the
zeros** — the Omission view is built from what lost.

### 2.1 `terms.md` — the posting's own words, first

Before scoring, write `runs/<jd-slug>/terms.md`: the posting's skills, tools, methods and
qualifications **lifted verbatim**, under exactly two headings, `## Must-have` and
`## Nice-to-have` — the tools read only headings containing *must* or *nice*, and anything under
another heading counts for nothing. If the posting doesn't split its asks, everything goes under
Must-have.

```markdown
# Terms: acme-backend

## Must-have
- Go
- Kafka
- PostgreSQL
- distributed systems

## Nice-to-have
- Kubernetes
- Terraform
```

An extraction, never a paraphrase — if you had to reword it, it isn't a term. Nothing scores
against this file; `xray.py` and `coverage.py` read it, and writing it before composing keeps the
coverage read from marking the page's own homework. A one- or two-character term (`R`, `Go`, `C`)
cannot be counted by the tools — lift it anyway and check it by eye.

### 2.2 The Fit rubric

Score the Claim as it stands — Assertion, Evidence, `skills:` line — against the **full posting
text**, never against a theme list you distilled.

| | |
|---|---|
| **1.0** | directly evidences a **must-have** — same technology, same kind of work |
| **0.7** | adjacent to a must-have, or a **nice-to-have** head-on |
| **0.5** | transferable — one inferential hop |
| **0.2** | same field, nothing the posting asks for |
| **0.0** | unrelated |

**Score what the claim achieved, not how it works.** A claim whose Evidence is mostly mechanism
scores on the outcome and the skill it shows; the mechanism is never itself a match for anything a
posting asks.

**Below 0.50 a Claim never takes a line**, even with room to spare (the Bullet floor), and an entry
with no Claim at 0.50 or above doesn't place — so the two most recent jobs are only guaranteed a
place when each has one.

Absolute, never on a curve: nine 1.0s on one posting and none on the next is the scale working. A
score may sit between anchors when the claim genuinely does (`0.85` = just under a direct
must-have). **Neither bank mark is a scoring input**: `needs-interview: yes` does nothing, and
`confidence: uncertain` is doubt about truth, spent at the Checkpoint — a flagged claim that hits a
must-have still scores 1.0.

**Every score carries a one-line reason in the posting's terms** — name what it hits, and below
the top anchor what held it back:

> `1.00` Kafka consumer work in Go on a hot production path — the streaming must-have, same tech
> `0.85` A 34-service Postgres split with a cutover runbook — close to the data-store must-have, but a migration
> `0.20` A tutorial for a personal tool — same field only

### 2.3 Width — one line unless it truly needs two

Each row carries a **`width`**: the number of typeset lines its Bullet will take, `1` or `2`. The
Packer seats the Bullet at exactly that width, or not at all.

**The default is `1`.** One line is about 95 characters, and that is the length of a strong
résumé bullet: an action verb, what was built or changed, the technology, and the result.

> *Cut checkout p99 latency 40% by batching offset commits in the Go Kafka consumer* — 80 chars
> *Designed the versioned event schema that 3 analytics teams' jobs still read* — 76 chars

**Declare `2` only for an entry's one or two most important Claims**, and only when the result, the
method *and* the scale that makes it impressive cannot be said in one line. A page of two-line
bullets is a wall of text; recruiters skim the first line of each bullet and skip the rest. Every
`2` you declare costs another Claim its line.

### 2.4 Merges — rare, and only for two halves of one thing

A merge fuses 2–3 Claims of one Entry into one Bullet. **Most pages need none.** A résumé is a
selection: the strongest Claims of each Entry, each on its own line, and the rest reported in the
Omission view. That is not lost work — the Gap report and the interview are where the rest goes.

Merge only when two Claims are **two halves of one accomplishment** and neither reads as a complete
bullet alone — the build and its measured result recorded separately, say. Never merge to squeeze
more Claims onto the page; a bullet carrying three accomplishments gets none of them read.

```markdown
## Merges

| entry | claims | width | reason |
|---|---|---|---|
| helios-payments | c1+c3 | 2 | c1 is the batching change and c3 is its measured latency result; apart, neither is a whole bullet |
```

Mechanics `pack.py` enforces: 2–3 claim ids, `+`-joined, one entry; every member's own row shows
`width: 1` (the group declares the width); no claim in two merges. If the bank holds a
`## merge <ids>` block for the exact set, its stored figure is the group's number. The block sits
in the Entry file after the Claims; `number`, `provenance` and `**Evidence:**` are all required, and
it is not a Claim — it takes no id and no `needs-interview`:

```markdown
## merge c1+c3
number: ~8 hours a month
provenance: estimated

**Evidence:** c1 ~3h + c3 ~5h; the user confirmed they are separate stages, checkpoint of 2026-07-31.
```

### 2.5 Leads — off by default

The bank may hold a `## lead` block per Entry (a situation, an aggregate figure). A lead line is
an unbulleted sentence between the entry header and its bullets. **Normal résumés don't have
them**, and a page of four reads like a story, not a résumé. Write the `## Leads` table only when
you use one, marking `y` only where an entry's employer or product would mean nothing to this
reader and the lead says in one line what it is. If you write it, **every entry in the claims table
needs a row**, even ones that won't place — every other entry is `n`. With no `y`, leave the table
out:

```markdown
## Leads

| entry | lead |
|---|---|
| helios-payments | n |
| orbit-analytics | n |
```

A lead's aggregate figure can only reach the page on a `Lead:` line — a Bullet's figure traces to
its own Claims or a `## merge` block, never to `## lead`.

### 2.6 The first bullet under each entry

The first bullet under a job is the one a skimming recruiter actually reads. It should be the
entry's strongest accomplishment for *this* posting — usually the top score, sometimes not (the
1.0 is a tool name; the 0.85 is the result that makes them call). Declare it per entry:

```markdown
## Openers

| entry | unit |
|---|---|
| helios-payments | c1+c3 |
| orbit-analytics | c2 |
```

Optional — leave the table out and score order decides. **Leave it out of the first pack**: you
can't know what places until you've read `allocation.md`. Add it afterwards, naming one placed
claim or merge group per placed entry, and re-pack — `pack.py` fails a placed entry with no row and
a row naming a unit that didn't place.

### 2.7 Supporting sections — certifications, responsibilities, extracurriculars

`bank/certifications/`, `bank/responsibilities/` and `bank/extracurriculars/` never compete for
Bullets and get **no row in the claims table**. Each entry gets a row in `## Sections`, every run,
`y` or `n`:

```markdown
## Sections

| section | entry | ended | signal | reason |
|---|---|---|---|---|
| certifications | aws-saa | 2025-03 | y | Qualifications: "AWS Certified Solutions Architect or equivalent" |
| responsibilities | placement-coordinator | 2025-05 | n | the only leadership words are "collaborate with cross-functional teams" |
```

`signal: y` needs all three: the posting **asks** for this kind of thing (a named or generic
credential; responsibility for people or a programme; activity outside work), you **quote** the
asking phrase from `jd.md` in `reason`, and **this entry answers it**. "Team player",
"cross-functional", "industry-leading" and a degree requirement are not asks. Borderline is `n` —
an `n` section can still place if the page has room left, and `pack.py` decides that, not you.
`ended` is copied character for character from the entry's frontmatter.

### 2.8 Writing `scores.md`

Prose above the table is welcome — a short paragraph on how you read the posting. The table is
fixed:

```markdown
| entry | claim | type | ended | score | width | reason |
|---|---|---|---|---|---|---|
| helios-payments | c1 | job | present | 1.00 | 1 | Kafka consumer work in Go on a hot production path — the streaming must-have |
| ledger-cli | c3 | project | 2024-06 | 0.20 | 1 | A tutorial for a personal tool — same field only |
```

- `entry` is the filename slug; `claim` the id as the file writes it; `type` and `ended` copied
  from the frontmatter character for character, and identical on every row of one entry.
- `score` is two decimals; `reason` is one line, never empty; a literal `|` is `\|`.
- Then `## Merges`, `## Leads`, `## Openers`, `## Sections` as needed, in any order. Nothing that
  looks like a table row below them.

On a re-run, rewrite the file whole from the current bank and posting.

## 3. Pack, compose the Skills rows, pack again

```bash
python tools/pack.py runs/<jd-slug>
```

Pass one reserves room for four one-line Skills rows and writes `allocation.md`: which entries
placed, how many bullets each at what width, every rule-made decision under **Silent calls**, and
**Did not place** — the Omission view. The page carries at most three jobs and two projects
(`--max-experience` / `--max-projects` change that; pass the same flags on both passes); the two
most recent jobs always place. A malformed table exits non-zero naming the row.

Then write `bullets.md` with its `## Skills` section only (§5.4), measure it, and pack again:

```bash
python tools/lengths.py runs/<jd-slug>            # prints `skills rows 1,1,2,1`
python tools/pack.py runs/<jd-slug> --skills-rows 1,1,2,1
```

Never work out the row counts yourself. With fewer than two rows, keep the `## Skills` heading
with nothing under it and pack with `--skills-rows ''` — `render.py` refuses a `bullets.md` with no
`## Skills` heading at all. Only pass two's `allocation.md` may be rendered.

### 3.1 The X-ray

```bash
python tools/xray.py runs/<jd-slug>
```

Advisory, never gates. It reads the **evidence** of what placed (not prose — there is none yet)
against `terms.md` and prints a coverage score, **Invisible without** (must-have terms no placed
Claim's Evidence carries), and red flags such as an employment gap. Use it two ways: a term it
calls *answered* is one you may name in a Bullet in the posting's own words, where the Evidence
supports it; a term it calls *missing* is never a licence to write it — that is a `gaps.md` line.
It matches substrings, not meaning, so check the claim before acting on any line.

## 4. The Checkpoint — show the angle, ask only what you can't decide

The one moment the run surfaces its judgement to the user, before any prose is written. Most runs
ask nothing.

**Always, and blocking nothing:**

1. **The angle** — three or four sentences: how you read the posting, what the page argues, which
   entries lead, and what it deliberately doesn't argue because the bank can't. Not a question.
2. **What lost** — print `allocation.md`'s **Did not place** section as it stands, plus its
   `## Merges` and `## Supporting` sections when they're not empty. Don't re-summarise or filter.

**Then sort every open question through one gate.** It becomes a **Fork** (you stop and ask) only
if it is **load-bearing** — it changes which requirement the page evidences, how the posting is
read, or whether a claim can be stated as written — **and** you **cannot name the rule** that
decides it from the posting or the bank. Everything else you decide, and log one line about it
under `## Decided by rule` in `checkpoint.md`. Never resolve anything by inventing.

| situation | what it becomes |
|---|---|
| A must-have nothing on the page evidences | a **Notification**: say it, offer to add evidence, keep going |
| The posting genuinely splits two ways and the bank answers each differently | a **framing Fork**: A / B, or C — research the company first (§0) |
| More than two ways | decide by rule (the reading the bank answers best), notify |
| A placed Claim marked `confidence: uncertain` | a **Fork**: feature / soften / drop |
| A merge group with summable figures and no stored `## merge` block, first time ever | a **Fork**: what do they add up to? |
| Ties, recency vs relevance, phrasing | silent — `pack.py`'s rules or yours |

How each Fork goes:

- **Notification** — *"Nothing in the bank covers their Kubernetes must-have. If that's wrong, tell
  me and I'll add it; otherwise it goes in the Gap report."* Or, where a claim carries the skill
  name but its Evidence never shows the work: *"too shallow to claim it"*, naming the claim.
- **Framing** — name both readings, say which you scored and why (the default is the reading the
  bank answers best), and ask. Before asking, glance at past runs'
  `## Forks` (Glob `runs/*/checkpoint.md`) for answered framing Forks and show any as dated history,
  never as a default. A past `context.md` for what may be the same company is offered as a
  question (*"same Acme as March?"*), shown only after a yes.
- **Confidence** — quote the claim's own hedge: *"`helios-payments/c4` says ~12 services and the
  file says it could have been ten. Feature it, soften it, or drop it?"* **feature**: compose as
  normal. **soften**: compose without the figure (or qualitatively). **drop**: set that row's score
  to `0.00` with the answer as its reason and re-run `pack.py`. Every `0.00` is a Fork answer.
- **Merge sum** — print each member's figure, name any overlap you suspect, and ask what the total
  is. The answer is written back as a `## merge <ids>` block (an *add*, below) and reused forever.

**Ask every Fork in one round**, most load-bearing first, and wait — a run is a conversation and
cannot be batched. Apply the answers: a confidence answer is at most a re-pack; a framing answer
against your default is a full re-score (rewrite `scores.md` whole). Anything that surfaces after
the round is decided by rule and notified, never asked. A re-run reads its own `checkpoint.md`
and **applies** recorded answers instead of re-asking (a recorded drop re-zeroes the row).

### 4.1 `checkpoint.md`

Written every run, after the answers and before composing:

```markdown
# Checkpoint: helios-platform
Run date: 2026-07-31

## Angle
<the angle, as printed>

## Decided by rule
- `helios-payments/c2`: figure left off — the Evidence says the 30% was one week's reading (ground 2).

## Notifications
- **Kubernetes — nothing in the bank.** Not answered.

## Forks
### Confidence: `helios-payments/c4`
**Asked:** feature / soften / drop. **Answered:** soften — "leave the number off". **Applied:** at composition.

## Write-back
- `bank/jobs/helios-payments.md` — new claim `c7`, `needs-interview: yes`, from the Airflow answer.
```

Omit empty sections. Record the question as asked and the answer as given.
**`## Decided by rule` is read by `render.py`**: every Bullet that leaves out a figure its Claim
stores needs a line here naming the claim and the ground (§5.3), or the render fails.

### 4.2 Write-back — which answers reach the bank

| kind | example | lands |
|---|---|---|
| **framing** | *"platform, not data modelling"* | `checkpoint.md` only — it's about this posting |
| **add** | *"I did run Kafka at Helios"* | a new Claim in that **existing** Entry, immediately |
| **revise** | *"that 40% isn't real"* | this run only, then offer once to fix the bank |

An **add** goes only into an Entry the bank already has (a job it doesn't hold is a `gaps.md` to-do
for a real `/ingest` session), takes the next unused claim id (`ingest` §8.4), is marked
`needs-interview: yes`, and is written in `ingest`'s conventions — neutral Assertion, the answer as
Evidence, a figure only with a `provenance` (one plain question: *"did you measure that, or is it
your estimate?"*). One clarifying question at most. Check it with `python tools/bankcheck.py`,
score it, re-pack. A **revise** edits the bank only when the user states the correction
explicitly; a Fork answer like *soften* never implies one. Bank edits are not committed by this
run — tell the user they're there to review (`git -C bank diff`).

## 5. Write the page

`bullets.md`, in page order: `## Summary`, then one `## <entry-slug>` section per placed entry in
the allocation's order, then `## Skills` (from §3), then `## Supporting` if the allocation seats
any rows.

```markdown
## Summary
Backend engineer with four years on payments and analytics platforms in Go and Python, owning
Kafka pipelines and the Postgres stores behind them from design through on-call.

## helios-payments
- helios-payments/c1+c3: Cut checkout p99 latency 40% by batching offset commits in the Go Kafka order-ingest consumer
- helios-payments/c4: Built the payout API that ~12 internal services integrate against, with idempotent retries
- helios-payments/c2: Rewrote nightly settlement as a partitioned concurrent job, cutting the run from 6 hours to 4

## Skills

### Languages
- Go (helios-payments/c1)
- Python (orbit-analytics/c2)
```

**One Bullet per allocated slot, citing exactly the unit the allocation names, in its order.**
Plain text only — no markdown, no LaTeX; `render.py` typesets and escapes.
Read `.claude/skills/tailor/plain-english.md` before writing, and write in that register.

### 5.1 What a strong bullet is

> **[Action verb] [what you built or changed] [with what / how], [result — a number when the
> Claim stores one]**

That is the shape every good résumé guide converges on — Google's *accomplished X as measured by Y
by doing Z*, the STAR result line — and it is the shape here. In practice:

- **Start with a strong past-tense verb** (present tense for a role still held): *Built, Cut,
  Automated, Designed, Shipped, Replaced, Reduced, Launched, Migrated, Benchmarked, Led, Owned*.
  Never *Worked on*, *Helped*, *Responsible for*, *Was involved in*, *Assisted with*. Never a
  sentence whose subject is a thing (*"The new schema let three teams…"*) — the reader is
  scanning for what **this person** did.
- **One accomplishment per bullet.** If you need *and* twice or a comma list, it is two bullets,
  or one of them doesn't make the page.
- **Concrete nouns.** Name the system, the technology, the people who used it: *a gRPC payout
  service every payout goes through*, not *a unified payments solution*. A real technical term
  (*Kafka*, *row-level security*, *full-text search*, *ClickHouse*) is the plainest word there is.
- **The result, with its number.** A Claim that stores a `number:` puts it on the line (§5.3).
  A Claim with none writes the change itself — *"replaced a fully manual workflow"* — and never
  grows a figure.
- **Size the work when you can afford it** — the denominator (*~12 of 40 services*), who used it
  (*for the finance team*), how far it spread (*across 3 analytics teams*), or that it was the
  user's own initiative. One such fact per bullet, taken from the Evidence. It's what turns a task
  into an accomplishment.
- **Only what a recruiter would care about, even when the Evidence carries more.** The Evidence
  is there so you can be accurate, not so you can be thorough. Name the technology and the
  approach (*by batching offset commits in the Kafka consumer*); never the settings or the wiring
  (*to a 50ms window*, *moving the lock release ahead of the commit*, *via a `should_stop`
  callback*). The test: if the hiring manager for this posting read the detail, would it change
  their opinion of the person? If not, it's spending their seven seconds.
- **No adjectives about the person**, no *successfully*, *effectively*, *passionate*,
  *cutting-edge*, *robust*, *seamless*, *leveraged*, *spearheaded*, *utilized*. Show it instead.
- **Self-contained.** Each bullet meets its reader cold, below the entry header and nothing else.
  No *the pipeline* or *the tool* the page never introduced, and none of this system's own
  vocabulary (Claim, bank, Bullet, posting).

Before → after, in the shape early runs of this system produced:

| before | after |
|---|---|
| *Got the three consuming teams onto one versioned event schema, enforced at the ingest edge, so that new event types stopped being a negotiation and parsers stopped breaking* | *Designed a versioned event schema, enforced at ingest, that 3 analytics teams' jobs still read* |
| *Kept unsupported claims off the page, failing the build on any figure no recorded claim carries, leaving what fits to a script no model can reach, and reporting the gaps it cannot fill* | *Built a pre-render check that fails the build when a figure isn't backed by recorded evidence* |
| *A unified gRPC door moved every payout off three request shapes, one per caller, and onto one service the callers were migrated to…* | *Unified three payout request shapes into one gRPC API that ~12 internal services call* |

### 5.2 Using the posting's words

**The posting supplies names for the user's work; it supplies no facts about them.** Where the
Evidence describes work in other words, use the posting's name for it — that is how a human
screener and an applicant-tracking system both recognise the match.

| | |
|---|---|
| **yes — renaming** | Evidence: *scored three candidate models against a hand-labelled test set* → **model evaluation** |
| **yes — renaming** | Evidence: *the internal metrics store, essentially ClickHouse* → **ClickHouse** |
| **no — re-scoping** | posting asks for `TensorFlow`; the bank holds no model the user trained → it doesn't go in |
| **no — a fact** | `led a team of four`, `3 years' experience` → no headcount, seniority or duration the bank lacks |

A name the user couldn't defend in the room is a re-scoping wearing a synonym. And the posting
decides **which Claims get a line**, not what goes inside the sentence — keep the specific detail
that makes a claim real even when the posting never asked about it.

### 5.3 Numbers

- **A number on the page measures impact or scale** — time or money saved, users, teams, volume,
  speed, share of a whole. **Never a setting** (a radius, a timeout, a batch size, a refresh
  rate): `render.py` bolds every figure, so a configuration value in a bullet is the first thing
  the reader sees, and it says nothing about the person.
- **Write digits**, attach the unit (*40%*, *~8 hours a month*, *3 teams*, *200+ sources*). `render.py`
  bolds every figure with its unit, so they pop on the scan — that's the only bold on the page.
- **Provenance moves one way.** `measured` renders as stored or softened; `estimated` renders
  **softened, always**: `~30%`, `30%+`, `over 30%`, `more than 30%`, `at least 30%` — pick the form
  that matches the Evidence (*"over 200 sources"* is `200+ sources`, never `~200`). A bare year is a
  date, not a figure.
- **A range never reaches the page.** Collapse a stored `4--5 hours` to its midpoint (`~4.5
  hours`) or an endpoint where that reads better.
- **The number is the last thing a bullet gives up.** A Claim with a stored `number:` renders it.
  Exactly three grounds allow leaving it off: the Checkpoint answered *soften*; the Claim's own
  Evidence undercuts the figure for this posting; or the stored figure is a setting, not impact or
  scale (then also offer the user a *revise* to the bank, §4.2). "The line is tight" is not a
  ground. Whichever it is, write a line under `## Decided by rule` naming the claim and the ground
  — `render.py` fails the run otherwise.

### 5.4 The Skills section

Two to four rows, one category per row, label in bold — the cheap real estate where a nice-to-have
survives its entry losing the page, and the section an applicant-tracking system parses hardest.

- **Hard skills only.** Languages, frameworks, libraries, tools, platforms, databases, cloud,
  methods with a name (*A/B testing*, *ETL*, *REST APIs*, *prompt engineering*). **Never soft
  skills** — *communication*, *cross-team coordination*, *ownership*, *problem-solving* are claims
  anyone can type; the bullets prove them or nothing does.
- **Conventional categories**, adapted to the posting: *Languages*, *Frameworks & Libraries*,
  *Data & Cloud*, *AI/ML*, *Tools*. A label may use the posting's own word for a category of hard
  skills (*Big Data*, *BI & Reporting*); it never names a disposition.
- **Draw from any Claim in the bank**, placed or not, filtered to what the posting asks for, most
  important first. Each skill cites a Claim whose `skills:` line carries that exact name (any
  case) — `render.py` checks it. Where the posting's general term is honestly the user's (they
  wrote `PostgreSQL` queries; the posting says `SQL`), that is a one-word bank edit to the claim's
  `skills:` line, offered to the user as a *revise* (§4.2) — never written here first. A sibling
  (`pandas` → `NumPy`), a specialisation (`Python` → `Django`) or a substitute (`PostgreSQL` →
  `MySQL`) is not the user's at all.
- **Case only**: capitalise the first letter unless the name's own form starts lowercase
  (`pytest`, `iOS`). Never Title Case, never respell.
- A row needs at least two skills; a skill appears in one row; a row may wrap to two lines, never
  three (`lengths.py` flags it — shed from the least important end). Below two rows, keep the
  `## Skills` heading with nothing under it and pack with `--skills-rows ''`.

```markdown
## Skills

### Languages
- Go (orbit-analytics/c1)
- Python (orbit-analytics/c2)

### Data
- ClickHouse (orbit-analytics/c1)
- PostgreSQL (northwind-retail/c1)
- ETL (orbit-analytics/c2)
```

A skill the posting asks for that fell off the section is a Gap report line (*you have it, the
page did not*).

### 5.5 The Summary

Every page opens with one: **two typeset lines at most** (`SUMMARY_CHARS`, ~220 characters), a
sentence or two saying who this person is for this reader. Composed from `bank/profile.md`'s
`## Standing` block (what they study or are, what they build, what they want) and the Claims (what
they've done). It's the one element that may generalise across Claims and borrow the posting's
names for the work.

- **Lead with the identity the reader is hiring for**: *"Backend engineer with four years on
  payments and analytics platforms in Go and Python"* — a title or degree the bank holds, never one
  it doesn't.
- **Then the strongest proof by name** — employers, products, technologies: *"…owning the Kafka
  pipelines and Postgres ledger behind Helios Pay's checkout."*
- **No figures at all** (it cites no Claim, so nothing could trace one; `render.py` refuses it).
  **No adjectives** (*results-driven*, *passionate*, *detail-oriented*). **No "seeking"**, and never
  the name of the company being applied to — the Summary describes the candidate.
- A term the bank cannot support stays out — that's a `gaps.md` line.

### 5.6 Leads, merged Bullets, supporting rows

- **A lead** (only where `## Leads` says `y`): one `Lead:` line first in the entry's section, one
  typeset line (`LEAD_CHARS`), composed from the bank's `## lead` block and its stored number only.
  Say what the employer or product *is* — *"Payments platform for small online merchants"* — not a
  scene. That fact must be in the block's **Situation** or the entry's Evidence; if neither says
  it, the entry is `n`.
- **A merged Bullet** cites its group (`- helios-payments/c1+c3: …`) and reads as **one
  accomplishment**: one verb, one result. If it reads as a list of its claims, the merge was wrong
  — go back to `scores.md`.
- **Supporting rows** (only if the allocation seats them), last, under `## Supporting`:
  `- <slug>` alone (the normal case — the page prints the title, issuer and date from the bank) or
  `- <slug>/c<n>: <short tail>` where the room is real. One typeset line, hard; the tail is bound by
  rule 2 like a Bullet and says what it was *for*, never that it happened.

### 5.7 Fitting the line

Run the tape before rendering, and again after every round of edits:

```bash
python tools/lengths.py runs/<jd-slug>
```

It prints each line that is over its width (`<line> <length> <prose>`; bold figures count extra),
an over-long Summary or Skills row, and the spread line. **An over-length bullet is rephrased
shorter — cut the tail, never the head, never the number, never a fact:** drop a repeated noun, a
decoration, an article. A rephrase that has to lose a fact is a different bullet; re-read the
Claim. Also from `render.py`'s set checks: on a page of six or more one-line bullets, **at least
one in three ends at or under `CHARS_PER_BULLET − 15`** — let finished sentences be finished; one
opening word **at most twice on the page and never twice in one entry**; one spelling convention
(`-ise` or `-ize`) across the whole page.

## 6. Read it back before you render

### 6.1 The cold read

Read `bullets.md` top to bottom as a recruiter who has never seen the bank, this system or the
posting, holding the page for thirty seconds. For every line:

1. **Does it parse on first read?** Ungrammatical is an automatic fail.
2. **Could they say what this person did and why it mattered?**
3. **Did a person write it?** — against `plain-english.md`: a metaphor where a verb belongs, a noun
   pile where a clause belongs, a contrast nobody needed, a colon holding a list, an epigram.
4. **Would they care about every detail in it?** A setting, a file, an internal name or a
   plumbing step is cut, even when it's true and traced (§5.1).

Then the page as a whole: **does the top third make the case?** The Summary and the first bullet
of each entry should be enough to get the call. Recompose a failed line from its Claim, not by
patching the sentence.

### 6.2 The plain-English lint

```bash
python tools/plainish.py runs/<jd-slug>
```

Prints marker hits (`contrast`, `aphorism`, `metaphor`, `compound`, `list`, `category`,
`abstraction`) and any `citation` drift. Advisory, never gates; it matches words, not meaning. Read
every finding and fix the real ones.

### 6.3 The evidence check — every traced line, by a reader who didn't write it

Rewriting for voice is where a fact quietly changes size. Put every Bullet and lead (not the
Summary) in front of one general-purpose subagent that has **not** seen the posting, and wait for
its result before continuing:

```
Agent(subagent_type: "general-purpose", prompt:
  "You are checking résumé lines against the evidence behind them. You have NOT seen the job
   posting, and you must not guess at it.

   <ref>: '<the line>'
   Evidence for <ref>:
   <each cited Claim's Evidence, verbatim — or the lead block's prose>

   … one block per line …

   For each line, answered only from its own Evidence:
   1. Facts — does it state a CHECKABLE fact the Evidence does not carry? A number, technology,
      scope, audience, outcome, seniority, headcount or duration. Wording is not a fault; the line
      is meant to be phrased differently from the Evidence, and to name what claims share.
   2. Scope — is anything stated LARGER than the Evidence, or a figure flatter? 'contributed to' as
      'led', an estimate as a flat number, '~12 internal services' as 'every service'.
   3. For a merged line (ref with '+'): is every cited claim actually represented?

   Report findings only, one or two sentences each. Say 'clean' if there are none.")
```

**A clean check is silence** — never report that the page passed. For a finding, rewrite the line
once and **halt with numbered options**, never a silent edit:

```
helios-payments/c1+c3
  as written   Cut checkout latency 40% across the payments platform by batching commits
  proposed     Cut checkout p99 latency 40% by batching offset commits in the order-ingest consumer
  flagged:     "across the payments platform" — c1 and c3 describe one consumer

  1. Take the proposal
  2. Keep it as written — the Evidence carries it        -> recorded in checkpoint.md
  3. It's true and missing from the bank — add it        -> write-back, keep as written
```

The proposal may not drop a cited claim or a stored figure to make a finding go away. Record each
finding and the option taken under `## Decided by rule`.

## 7. Render

```bash
python tools/lengths.py runs/<jd-slug>
python tools/render.py runs/<jd-slug>
```

`render.py` validates `bank/profile.md`, checks every citation against the bank and the allocation,
runs the length, set and number-trace checks, fills the template, compiles with pdfLaTeX, and then
checks the header and Summary didn't wrap, nothing ran past the margin, and the page is one page.
Every failure is hard and names the offender. It is the only way to produce the PDF.

What a failure is asking for:

| failure | fix |
|---|---|
| a line over its width | rephrase shorter (§5.7) |
| the spread rule | the bullets are written to the cap — let some finish early |
| an opening word repeated | another verb for one of the two |
| two spelling conventions | pick one |
| a citation that doesn't resolve / slot mismatch / wrong order | make `bullets.md` match `allocation.md` exactly; never invent an id |
| a number not in the Claim, or an estimate rendered flat | rephrase without it, or soften it; never edit the bank to make a line legal |
| a Claim's stored figure missing from its bullet | put it back, or log the ground under `## Decided by rule` |
| a skill its cited Claim doesn't carry | cite the Claim that does, or drop the skill |
| a figure in the Summary | say it without the number |
| Skills section not what the allocation charged / RESERVATION | re-run `lengths.py` and pack pass two |
| header-fit / Overflow on an entry header or Education | `bank/profile.md` or the bank's frontmatter is too long — the user's call; tell them what to cut |
| Summary-fit | the Summary broke onto a third line; cut a few words |
| the page-count assert | every line passed and the page still ran over: the calibration is off (`docs/calibration.md`) — never fix it by dropping a bullet |

Then **look at the PDF** — open `runs/<jd-slug>/resume.pdf` with the Read tool and read it the way
a recruiter would.
Mechanically valid is not the same as good.

### 7.1 The coverage read

```bash
python tools/coverage.py runs/<jd-slug>
```

Reads `terms.md` back against the rendered page and prints four lists: covered, **answered by the
bank but absent from the page** (with the claim ids), answered by nothing, and too short to count.
Advisory. The middle list is where §8's *you have it, the page did not* lines start; it is never a
reason to go back and stuff a term into a sentence.

## 8. The Gap report — `gaps.md`

The second deliverable, and the honest half: what the posting asked for that the page doesn't
claim, each line in one of three classes:

- **Nothing in the bank** — no work in this territory. Fix: an `/ingest` session, or accept it.
- **Too shallow to claim it** — the work is there and the Claim can't carry it. **Name the claim.**
  Fix: a deepening interview on that claim.
- **You have it, the page did not** — a Claim covers it and lost the page, the slot or the Skills
  row. Nothing to fix in the bank; say so.

```markdown
## Too shallow to claim it

- **Airflow, as orchestration.** `helios-payments/c2` lists Airflow under `skills:`, but its
  Evidence never mentions a DAG, a schedule or a backfill — so it made the Skills row and couldn't
  carry a bullet.

## You have it, the page did not

- **AWS.** `orbit-analytics/c3` carries it, but its bullet is about Terraform and AWS fell off the
  Skills row. Nothing to fix in the bank.
```

A requirement the page claims is not a gap. Every line must name something `jd.md` asks for —
never something only company research turned up. A credential the posting names is a gap like any
other (and `bank/certifications/` is the cheapest `/ingest` session there is). **No score, no
ratio** — *"7 of 11 must-haves"* says less than the list does.

## 9. Commit the run folder

```bash
git -C runs add <jd-slug> && git -C runs commit -m "Tailor: <jd-slug>"
```

Everything is committed — `jd.md`, `terms.md`, `scores.md`, `allocation.md`, `xray.md`,
`checkpoint.md`, `bullets.md`, `resume.tex`, `resume.pdf`, `gaps.md`, and `context.md` where
research happened — so the run folder is a complete record of how the page was made. Bank
write-backs are not part of this commit; say they're waiting in `git -C bank diff`.

Then hand the user the PDF and the Gap report, and say in two lines what the page argues and what
it couldn't.
