---
name: ingest
description: Fill the bank. One sitting takes one job, project, position of responsibility, extracurricular or certification, reads the source, interviews the user, and writes one Entry file — read, wide pass, depth pass, write as you go.
---

# ingest

One sitting, **one source, one Entry file**. Five folders, five types:

| folder | `type` | what it holds |
|---|---|---|
| `bank/jobs/` | `job` | employment |
| `bank/projects/` | `project` | something built |
| `bank/responsibilities/` | `responsibility` | a position of responsibility — a post held, people or a programme owned |
| `bank/extracurriculars/` | `extracurricular` | a sport, a society, a volunteering commitment, a community |
| `bank/certifications/` | `certification` | a credential earned from an issuer on a date |

A folder holding five things is five sessions. Never survey a pile and split it, and never open a
second entry because the source mentioned one — splitting is the user's act.

**The last three are supporting entries, and the spine below runs over them unchanged** — the read,
the wide pass, the depth pass, the four rules, write as you go. What differs is §9, which is short,
and one thing worth knowing before you start: **a supporting entry renders as at most one line**,
and most of that line is built from the frontmatter. Say so if the user is about to spend a full
sitting on one (§9).

Terms are defined in `docs/glossary.md`. Read it if one below is unfamiliar.

**Two ways in, one spine.** No Entry file yet → cold session: run §1–§7 straight through. The file
already exists → the **Return door**: read §8 first; it says which of §1–§7 this session runs.
Decide by checking whether the file exists, never by a flag.

## The four rules

Ingestion is the one door with no lint behind it: whatever lands in the Entry file is the ground
truth every later trace resolves against. These hold without exception.

1. **Lift, never manufacture.** What the source *states* may be lifted as Evidence. The *shape* of
   the code entails nothing: a cache package does not license "improved performance", and a `perf:`
   commit message is not an outcome.
2. **No fact enters the file that was not spoken.** "Tight deadline" goes in because the user said
   the deadline was tight — never because migrations usually are.
3. **Never arrive with a drafted Entry.** Do not write claims and ask the user to correct them. A
   plausible draft gets nodded through and is then true forever.
4. **The fix for mush is another question, never a better sentence.** Tightening a rambling answer
   is transcription and is fine. Repairing *"led the migration"* into something that reads well is
   manufacturing facts — and the result reads better than the honest version, so nothing will ever
   flag it.

## 1. The read

**Read the source before asking anything.** The read produces facts; the interview produces claims.
The facts make the questions grounded — *"you have a whole invalidation package in here, what were
you fixing?"* beats *"what was the impact?"*

Extract only what the source **literally shows**, and only enough to **name each piece of work**:

- what the thing does, what it talks to, what is in it;
- any sentence where the source's own prose *states* an outcome (README, design doc, CHANGELOG, a
  committed benchmark) — that sentence is liftable as Evidence.

Do **not** read authorship or timelines — neither grounds anything here. And **the read cannot
extract impact**: a repo shows what was built, never what changed for anyone. Impact comes out of
the user's mouth, always. Stop reading when you can name the pieces of work.

**The user's existing résumé is a checklist of what exists, never a source of claims.** It says
there was a job at Acme and a project called Harbour; every claim still comes from this session. Do
not seed claims from it, even marked `needs-interview` — its bullets are already compressed by the
exact process this system replaces.

## 2. The wide pass

Establish the **list of pieces of work worth claiming** before digging into any of them. It is two
lists merged — what the user volunteers, plus what the read surfaced that they did not mention —
and the merge is the load-bearing half. (A return session adds a third list: §8.3.)

- **Ask the user first, then add.** Leading with your list turns theirs into agreement with yours
  (rule 3 in another form).
- **Report what they did not mention, by name**: *"you didn't mention the rate limiter or the
  migration tooling — is either worth a claim?"* Something left off on purpose stays off; what
  matters is that it was offered, not silently dropped.
- **Anything the user raises is admissible** even where the source is silent on it. *"I ran the
  on-call rotation"* belongs in the entry with no backing at all.

At the end of the wide pass, **write the Entry frontmatter** (§5).

### Angles — the fallback opening for a thin source

Where the source cannot populate the list (typically a job, whose source is a paragraph the user
wrote), open on these instead. They exist because people forget, not because they inflate.

- What did you own end to end — yours if it broke?
- What were you brought in to fix?
- What was in place before you that is not there now?
- What broke, or nearly broke?
- What did you argue for and lose?
- What does someone else depend on now that you built?
- What would you redo?

Guardrails: an angle **populates the list, never asks the claim** — once work is on the table, dig
that work and the angle is spent. They are a fallback, not a fixed opening — a session with a real
repo opens on what the repo showed. An angle that surfaces nothing is dropped in a sentence; never
work the list in order like a form.

## 3. The depth pass

Take the list one item at a time. Each item ends as a written claim — clearing the Shallowness
checks or parked (§4).

**Pressure means demanding surrounding detail, not verifying.** The danger is not inflation — the
user defends every claim in the room — it is compression and forgetting. Ask:

- who asked for it, and what happened if it did not get done;
- what was in place before;
- what broke, or what you were bracing for;
- who pushed back, and what they wanted instead;
- **how you knew it worked**;
- **the denominator** — *"~12 services — out of how many?"*, *"how much of the deliverable was
  that?"*;
- **the reach** — *"who ended up using it, and are they still?"*;
- **who saw the output, and how senior** — *"who did that end up in front of?"*. A name is not the
  answer; where it landed is. *"my manager"* and *"the CFO"* size the same report differently, and
  only the user knows which it was;
- **whose call it was** — *"was that asked of you, or your own move?"*. Ask it **whenever the
  user describes going somewhere or doing something outside the brief**, and ask it in a form
  that can be answered *nobody*. *"Who asked for it?"* invites a name and quietly assumes there
  was one, so a self-started piece of work comes back sounding assigned;
- **whether it was a first** — *"had anyone done this before, here?"*, *"was this a new thing or
  an existing one taken over?"*

**These five size the work**, and a page cannot weigh *what changed* without them: the tailor
reaches into Evidence for the denominator, the audience and its seniority, how far it spread, what
it would have cost to get wrong, and whether it was a first or self-started (`tailor` §5). **It may
only reach for what is there** — the consumer is written and the producer is this list, so a fact
nobody asked for is a fact no page can ever use.

**Record the answer in the user's own account, never as résumé phrasing.** *"Going wider was their
own move, not an assignment"* is Evidence. *"Self-initiated cross-team product adoption"* is a
Bullet somebody wrote at ingestion time, and it is wrong here for two reasons: it fixes one framing
into a bank that has to answer many postings, and a stored phrase gets reused verbatim on every run
that touches the claim. The bank holds what happened; the page decides what to call it.

These are questions about the shape of the work — see **Numbers** below for why they are not
questions about a number.

**On a project, ask about the technical approach — at the level a hiring manager would.** A project
has no employer to vouch for it, so its Evidence needs the technologies used and the shape of the
solution: what it was built with, what the hard problem was, and the main design decision with its
reason (*"a bounded worker pool with a per-host limit, so fetching 200 feeds stays fast without
getting rate-limited"*). Stop there. How the solution is tuned and wired — the values, the file it lives in, the
schema behind it — is not something a page or an interviewer will ask for (§3.1).

### 3.1 The résumé test — what earns a place in the file

**Every fact you write must pass one test: would a recruiter or hiring manager use it to decide
whether to call, or would the user need it to answer *"tell me more about that"* in the
interview?** True is not enough. The bank is not a design document; anything it holds is a
candidate for a page, and a page has no room for a fact that fails this test.

**Write down:**

- **the work** — what was built, owned or changed, described the way a hiring manager would;
- **the technologies and methods** — the names a job posting could list;
- **the size** — who used it, how many, what it was part of, how senior the audience;
- **the result** — what was different afterwards, and **how the user knows** (this sentence stays
  whenever a claim carries a `number:`: it is what the provenance rests on);
- **whose call it was**, and whether it was a first;
- **at most one design decision per claim, with its reason, in one sentence** — the choice a
  reasonable engineer could have made differently, at architecture level;
- **a caveat that bounds a claim** (*"designed for groups; in practice used in pairs"*), in one
  clause.

**Leave out, even when the user says it and it is true:**

| leave out | example |
|---|---|
| configuration and tuning values | *a 50ms batch window*, *a 30-second timeout*, *48 refreshes a day* |
| file paths, function, table and field names | *`internal/consumer/commit.go`*, *a `should_stop` callback*, *a nullable `merchant_id`* |
| plumbing and edge-case handling | *one row per user per day, upgraded in place*, *UUID file ids* |
| side features that went unused | *a CSV export nobody used* |
| anecdote and motivation | *"my flatmate kept forgetting the rent"* |
| commentary about the user | *"they are candid about…"*, *"they raise this deliberately"*, *"they saw this coming"* |
| counts of the user's own artefacts | *10,000 lines of code*, *a 600-line parser*, *eighteen design docs* |

**The test is the fact, not the topic.** *"Batched the consumer's offset commits"* passes; *"the
batch window went from 20ms to 50ms because the broker flushes every 40ms"* is the same topic and
fails. When a user's answer is mostly detail of this kind, ask the question one level up — *"and
what did that make possible?"* — and write the answer to that.

Rules of register:

- **Jogging, not interrogating.** Questions are specific and grounded; vague ones jog nothing.
- ***"Are you sure?"* is never asked** — in those words or any other.
- **A claim with no external check needs more excavation, not less.**
- **A mismatch is a question, never a verdict.** The claim says retry logic, the repo has none:
  *"different repo, or did it get ripped out?"* The user's answer settles it, and **the discrepancy
  is never recorded**.
- **Where the source could have answered and cannot, say so once, out loud** — *"the repo won't tell
  me who asked for this, so it's on you."* A spoken cue to dig, never written down (§5).
- **One claim, one assertion, at most one number.** *"Cut latency 40% and cost 30%"* is two claims:
  split and dig each.

### Numbers

**Never ask for a number.** Numbers arrive inside answers about what changed.

**The denominator and the reach are not exceptions to that** — they are questions about the shape
of the work whose answers happen to carry figures. **A denominator that arrives this way is
Evidence prose, never the claim's `number:`**, which stays the outcome figure: *~40 services* is
hollow as a `number:` and worth its place in the Evidence.

**A hollow number gets the "So what?" test — a redirect, not a refusal.** *"10,000 lines of code"*
is the user reaching for the nearest figure; the redirect is the most grounded question in the
session: *"10k lines — what did all that code let people do?"* Three landings:

1. **a consequence-bearing figure** — that becomes the `number`; the hollow one is never written;
2. **prose about what changed, no figure** — the claim lands qualitative. The healthy common case;
   a missing number is not a defect;
3. **nothing** — the claim is at the Parking boundary (§4): *never says what changed* is the check
   an empty number fails by definition.

**The number fails the test, never the claim.** If the user still wants a failed figure in, say
once why it stays out of the `number` field, then take their answer: it may live inside the prose
as scale texture, never as the claim's number. An empty phrase (*"improved code quality"*) gets the
same redirect.

### Provenance — a by-product, never a question

**Never ask "measured or estimated?"** *"How did you know it worked?"* nearly is the tier: *"we had
a Grafana panel on it"* → `measured`; *"everyone stopped complaining"* → `estimated`. Where the
answer genuinely leaves it open, ask **one** plain follow-up — *"did you clock that, or is that
your read of it?"* — and take the answer. You never adjudicate a tier.

**The fallback is `estimated`.** A wrongly-estimated number costs a `~`; a wrongly-measured one
renders flat, passes every lint, and is undetectable forever.

**A lifted number is a lead, not a record.** The README says *"cut p99 40%"* — nothing in it says
whether that came off a dashboard or was a ballpark. Raise every lifted figure before it becomes a
claim's `number` — *"was that off the dashboard, or a ballpark at the time?"* — and write **the
user's answer, never the doc's sentence**. The source's sentence still lands as Evidence unchanged;
what routes through the user is the figure becoming claimable.

### Doubt — the hedge trigger

`confidence: uncertain` is user-set and fires a Fork on every future run that reaches the claim.
The trigger is **a hedge you hear**: *"I think it was 40%, could've been 30"* · *"don't quote me"* ·
*"I'm fairly sure it was me, but it might have been Raj"*. Then **you propose, the user calls it**:
*"you sounded unsure on the 40% — want me to mark it for a second look before it goes on a page?"*
Never set the flag unasked.

**Hedge vs verbal tic:** a hedge attaches to **one identifiable fact** and offers an alternative —
another value, a range, someone else. A tic (*"I guess"*, *"kind of"*, *"roughly"* on an
already-rounded number) attaches to nothing in particular and would survive if the fact were
different. Test: can you point at the fact and say what the alternative was? Twice-hedged is real;
genuinely unclear costs one question. The flag is not only for numbers — an attribution wobble is
flaggable on the same trigger.

## 4. Ending a claim

A claim ends by clearing the **Shallowness checks** or by being **parked**. Two checks, only:

1. **it says what changed** — a difference afterwards, not activity and method;
2. **there is room to re-angle it** — the Evidence entails more than the Assertion states, so a
   future JD can draw a different angle from it.

A missing number, a missing provenance, and any "why / who / what it replaced" detail are **not**
checks.

**Parking is an explicit interaction, never a silent decision.** After a couple of follow-ups
return nothing new, name the check you cannot clear and offer to park:

> *"I have that you built the ingest pipeline and roughly how, but nothing about what changed for
> anyone — so it will lose to every JD. Park it, or try a different angle?"*

The claim is **still written**, with whatever was gathered, marked `needs-interview: yes` — a
shallow claim beats no claim, and the offer makes the mark an event the next session can pick up.
**A parked claim never gets `confidence: uncertain`** — that flag is user-set doubt; parking is you
admitting you could not dig.

**The user may end a claim at any time.** You get exactly one more try, then you accept it.

## 5. Write as you go

**Each claim lands in the file the moment it settles or is parked.** Frontmatter is written once at
the end of the wide pass. A half-finished session is a normal state — an entry with fewer claims.
Never batch the writing to the end: the user can stop at any claim boundary, and there is no
resume machinery. Write markdown by hand; nothing generates Entry files.

```markdown
---
type: job
title: Senior Software Engineer
org: Helios Pay
location: Bengaluru, India
started: 2023-01
ended: present
domain: payments
---

## c1
number: 40%
provenance: measured
skills: Go, Kafka, PostgreSQL

**Assertion:** Cut checkout p99 latency 40% by batching consumer commits.

**Evidence:** The consumer committed offsets per message, so ...
```

- **Frontmatter:** `type` (one of the five in the table at the top), `title`, `org`, `location`,
  `started`, `ended` required; `domain` optional — a few words for the user's own reference, which
  nothing on the page reads. **Folder and `type` must agree** — a `job` under `bank/projects/` is a
  hard failure. What the six mean on a supporting entry is §9.
- **The filename slug is the Entry id, and it never changes** — every run cites it. Propose a
  lowercase-hyphenated one (`helios-payments`) at the end of the wide pass and confirm it with the
  user. Never `summary`, `skills` or `supporting`: those collide with `bullets.md`'s own headings.
- **A project** may leave out `org` and `location` — its header on the page is one row: the name,
  then **`stack:`** (the four or five technologies a reader should see, comma-separated, as the
  project's own README would list them — `stack: Next.js, TypeScript, Supabase, PostgreSQL`), then
  **`link:`** if it has a public home, written as the page should show it (`github.com/you/thing`,
  no `https://`, no `_ # % &`). Ask for both at the end of a project session; a private repo gets no
  link. Every technology in `stack:` must also appear on some claim's `skills:` line.
- **`started`/`ended` are `YYYY-MM`**; `ended` also takes `present`. Never write a display date —
  `render.py` composes `Jan 2023 -- Present` from these (`docs/adr/0031-the-entry-header-is-built.md`).
- **`location`** is `City, Region, Country` for a real place, `Remote` otherwise. A project omits
  `org` and `location`; the page doesn't print them. `bankcheck.py` advises when the bank mixes
  location depths; it never refuses one.
- **Claim ids** `c1`, `c2`, … are **sequential, frozen, never renumbered**. A merged-away id is
  never reused (§8.4).
- **Fields** (one `key: value` per line): `number`, `provenance`, `confidence`, `needs-interview`,
  `skills`. Absent fields are **omitted, never nulled**. `number` and `provenance` ride together —
  one without the other fails the parse. `skills` is a free-form comma-separated list.
- **`**Assertion:**`** is the neutral, canonical core fact — never framed toward any JD.
- **`**Evidence:**`** is the dug-out surrounding detail — who asked, what was before, what changed,
  how they knew. Never rendered verbatim; it is what a future JD re-angles from. **Every sentence in
  it passes §3.1's résumé test** — a short, dense Evidence beats a long one with trivia in it.

**What never goes in the file:**

- any marker that a claim rests on memory alone — it would fire on nearly every entry and reads as
  doubt to a later session;
- which shallowness check a parked claim failed;
- a mismatch between what the user said and what the source shows;
- **a null lead** — any marker that this entry has no aggregate. The claims grow; a null written
  today goes stale silently. The closing move (§6.5) can simply be offered again next session;
- any note that a claim was merged away — no tombstone, no comment.

When the entry is written, **check it parses**:

```bash
python tools/bankcheck.py
```

`bank parses` on the last line and exit 0, or the offending file and line, non-zero. Lines above
are advisories — read them and decide. A failure naming a *different* entry was already there: say
so and leave it.

## 6. The stretch check

**There is no question cap** — the session ends when every listed item has landed or been parked.
What replaces a cap is the stretch check, offered **at claim boundaries, never mid-claim**:

> *"Four down, three left on the list — keep going, or park the rest?"*

## 6.5 The closing move: an optional lead

After the last claim lands or parks, before §7. A lead is one unbulleted line under the entry
header, and most pages carry none — `tailor` prints one only where an employer or product needs a
line of introduction. So this is an **offer, not a step**, and both halves are optional.

- **Situation — asked, never proposed.** Offer it on a job whose employer or product would mean
  nothing to a stranger: *"In one line, what does Helios Pay do, and what did things look like when
  you got there?"* On a project, the situation is what people did before it existed: *"what were
  you doing instead, before you built this?"* Never draft one and ask the user to confirm it
  (rule 3): a plausible sentence gets nodded through. Skip it for a well-known employer, or when the
  user declines.
- **Aggregate — computed and proposed**, only when **two or more claims carry comparable figures**.
  Read the figures off the claims, name any pair you suspect overlaps, and let the total arrive as
  the consequence, in one exchange:

  > *"Reading your file: `c2` saves about 3 hours a week and `c4` about 5. `c3` has no figure. That
  > comes to about 8 hours a week — unless the reconciliation rewrite and the report job overlap. Do
  > they? And is it every week?"*

  One `yes` covers the readings, the cadence and the overlap together. With nothing to sum, write
  no aggregate; the trigger is recomputed fresh every session.

Write what you got as a `## lead` block after the claims — an amend under §8.4's rule even on a
cold session:

```markdown
## lead
number: ~8 hours a week
provenance: estimated

**Situation:** Payments platform for small online merchants; settlement ran by hand from spreadsheets.

**Aggregate:** Two of the automations together gave back about 8 hours a week.

**Evidence:** c2 ~3h, c4 ~5h a week; the user confirmed they are separate jobs, weekly. c3 has no figure.
```

- `**Situation:**` and `**Aggregate:**` are body labels like `**Evidence:**`, not `key:` lines.
  Either may be left out, never both.
- `number:` and `provenance:` belong to the Aggregate: an Aggregate needs a number, and a number
  needs an Aggregate. `provenance` is **`estimated` by construction** — a sum over remembered
  savings and an overlap judgement is never `measured`.
- **The Aggregate states its scope** — *"two of the automations"*, not *"the automations"*, when
  another contributed nothing.
- **`**Evidence:**` carries the per-claim readings and the overlap and cadence answers.**

## 7. Ending the session

**Point the user at the file.** A new entry: open `bank/<folder>/<slug>.md`. An edit to an
existing one: `git -C bank diff`. They read it and **edit** it where it is off, and when it reads
right they commit it — `git -C bank add -A && git -C bank commit -m "<slug>"` — because §8.4's next
claim id is read from that history. Do not read the entry back in chat — a wall of text earns a *"yeah, that's about right"*, the exact
nod that made drafting dangerous.

**Report the smell where it applies** — an observation, not a score:

- *this entry has two claims, which is thin by the Shallow entry check* — fewer than three claims
  can never fill a block;
- *the source gave up nothing you had not already told me* — the sign the source was their own
  summary wearing a repo's clothes.

Say nothing about which claims held up under questioning and which ran out of texture.

## 8. The return door

The Entry file already exists. This is a **branch**, not a second skill: it says which of §1–§7 the
session runs. The four rules bind unchanged.

**No mode flag.** Three things bring a user back — **new work**, a `needs-interview` **mark**, a
Gap-report line *too shallow to claim it* — and they are one mode. Only the wide pass differs (§8.2).

### 8.1 The readout

Open the file, count claims, grep marks, and show what is sitting there:

> *"Acme has 6 claims; c2 (the nightly ingest pipeline) and c5 (the on-call rotation) are marked.
> What are we here for?"*

Where the file holds no `## lead` block, say so and offer the closing move as independently
runnable:

> *"Acme has 7 claims, 5 with figures, and no lead — want to do that now?"*

On a project entry with no `stack:` line, offer that too — it is what the page shows beside the
project's name:

> *"ledger-cli has 5 claims, no lead and no stack line — want to add the stack now?"*

Give each marked id **a few words off its own Assertion** — a bare id means nothing three weeks
later. Note which marked claims also carry `confidence: uncertain`; those open differently (§8.5).

**You show what you can see; the user supplies what you cannot.** Do not work out why the session
was opened, and do not go looking — no reading `runs/*/gaps.md`, no recurrence view; that is the
bank audit's pass. If a gap report is why they came, they will name the claim.

Two things happen at the door and nowhere else: **a mark can be cleared with no session at all**
(§8.5), and **a Claim merge is proposed here** (§8.6) — look for two claims circling the same work
before the session picks a direction. **Merge first, then dig once.**

### 8.2 Whether the wide pass runs

- **New work** → the full spine: §1 over whatever source the user points at now, §2 with a third
  list (§8.3), §3.
- **Deepening** a marked or gap-flagged claim → **no read, no wide pass** — straight into §3 on the
  named claims. The read's job is naming a piece of work, and the claim already names it; what it
  lacks is *what changed for anyone*, which no source holds.

Source states on a return: **moved on** (new commits, the doc grew) is new work and takes the
new-work path; **vanished** (repo gone) — say it once, out loud, and run on memory. One session may
do both — the wide pass runs for the new-work half only.

### 8.3 New work: the third list

The third list is **what the Entry already claims**. Diff the read against it and say so, by name:

> *"the invalidation work is already c3 — skipping it, unless c3 is narrower than what I'm looking
> at?"*

Never drop silently. Either the existing claim covers it (off the list), or `c3` is **narrower**
than what the read found — dig the wider version and **edit `c3` in place**. The same work never
gets a second id.

**Frontmatter is edited freely in place** — a promotion changes `title`, leaving changes `ended`.
*Amend, never regenerate* is a rule about claim ids; frontmatter carries none.

### 8.4 Amend, never regenerate

- New claims **append with a new id**. Existing claims are **edited in place, keeping their id** —
  change the lines that change.
- **Nothing is renumbered and the file is never regenerated**, even where a rewrite would be
  tidier: every past run cites these ids, so regeneration silently changes what `c3` denotes —
  wrong retroactively, invisible, unlintable. It also clobbers the user's hand edits.

**The next id is one past the highest the file has *ever* held** — not the highest in it now, since
a merge deletes an id that is never reused and leaves no tombstone. The record is git:

```bash
git -C bank log -p --follow -- jobs/<slug>.md | grep -oE '^\+## c[0-9]+'
grep -oE '^## c[0-9]+' bank/jobs/<slug>.md
```

(`projects/` for a project.) Take the highest number across both outputs; the next id is one past
it. This only works if the bank's changes have been committed (§7). Gaps in the sequence are normal
and never closed up.

### 8.5 Draining the mark

Marks arrive from a **checkpoint add**, a **parked claim**, or a **declined confidence fork** — two
openings, legible in the file:

- **the mark alone** → *this claim is thin, dig it*. Depth pass, opened on the claim's material:
  *"c2 has you building the ingest pipeline off a nightly cron — who was waiting on that data?"*,
  never *"tell me more about c2"*;
- **the mark alongside `confidence: uncertain`** → a declined fork. Not thin — it wants the
  correction the user declined to state mid-run: *"you flagged the 40% on c4 — what should it
  say?"*

Parking writes nothing down, so a parked claim is indistinguishable from a never-interviewed one
and a session may re-ask an angle that came up empty. Accepted, not fixed — the user says *"we
went at that one, there's nothing there"*, and §4's one-more-try rule applies.

**Two events clear the mark**, and only events:

1. the claim reaches the Shallowness checks (§4);
2. **the user says that is as deep as it goes** — you propose, they call it: *"want me to take the
   mark off c5 and leave it as it stands?"* This one can happen inside the readout, no session at
   all. Without it the queue never drains and the user stops reading it.

**Never clear a mark on your own judgement**, and **clearing it does not assert the claim is
good** — the audit will still list it, `gaps.md` will still classify it. All clearing says is
*nobody owes this another interview*. Clearing = deleting the `needs-interview: yes` line.

On a declined fork the two marks part company: the user **states the correction** → write it,
clear both lines; the user **still does not know** → clear `needs-interview: yes`, keep
`confidence: uncertain` — the flag re-fires on every future run by itself, so a queue copy of it
adds nothing.

### 8.6 A claim merge

Two claims circling the same work — most often a checkpoint add landing beside the claim it
duplicates. It is load-bearing, not tidiness: an **Entry score** is the mean of the top 3 claims
and the entry gets `min(3, claims ≥ 0.50)` slots, so two near-duplicates spend two slots on one
piece of work and count it twice.

**Same work means the same change to the same thing** — one before, one after, described twice. The
same *area* is not the same work: batching the consumer's commits and giving it a dead-letter queue
are two claims about one consumer, and stay two. Test: could a future JD draw a **different angle**
from each? If both would render on one page and a reader would ask why it is there twice, it is one
claim.

**You propose, the user calls it**:

> *"c3 and c7 both look like the consumer commit change — c3 has the excavation, c7 came in off a
> checkpoint. Same piece of work, or two?"*

Then:

- **Merge first, then dig once** — on the survivor.
- **The elder id survives** (the lower number): it carries the excavation and the most citations.
- **Fold the loser's material into the survivor**, then delete the loser's whole section.
- **A figure on the loser does not ride across on its own** — it goes into the dig like any other
  number; the tier comes from the user's answer (§3).
- **No tombstone; the dead id is never reused** (§8.4).

Deletion doesn't break *amend, never regenerate*: a deleted id denotes nothing and is never
reused, while renumbering would silently change what an old id means. The deleted claim is still in
git.

### 8.7 Splitting the Entry is out

A session that concludes the entry should have been two **says so, once, and stops there**. A split
means new Entry ids and rehomed claims — the user's act, done by hand in git.

### 8.8 Ending a return session

§7 applies unchanged — the review is `git -C bank diff`, and you do not narrate the session back. Re-run
§5's parse check before you finish.

## 9. The three supporting types

`responsibility`, `extracurricular`, `certification`. **Everything above runs unchanged** — the four
rules, the read, the wide pass, the depth pass, the Shallowness checks, Parking, write as you go,
the return door. This section is only what is different, and there are four things
(`docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md`).

### 9.1 Say what the row is, before the sitting

**A supporting entry renders as at most one line, and most of that line is built rather than
composed.** The page shows:

> **Placement Coordinator** — Training & Placement Cell, Aug 2024 – May 2025. Ran the drive for six
> branches and 40+ visiting companies.

Everything up to the full stop is the frontmatter. Only the last clause is composed per posting, out
of one Claim. And the section is on the page **only** when the posting asks for that kind of thing
or the page has lines left over.

So say it, once, before digging:

> *"Heads up on what this buys: a position of responsibility is one line on the page, and it only
> shows up when a posting asks about leadership or the page has room. Still worth doing — the line
> has to come from somewhere and the material re-angles — but it is not an Experience block."*

Not a discouragement and not a gate — the user decides how to spend the time, knowing the ratio.

### 9.2 The frontmatter, which reads differently on each type

| | `responsibility` | `extracurricular` | `certification` |
|---|---|---|---|
| `title` | the post held — *Placement Coordinator* | what was done — *Varsity Football*, *Teaching Volunteer* | the credential's **exact official name** |
| `org` | who it was held in | the club, team, school or charity | **the issuer** — *Amazon Web Services*, *DeepLearning.AI* |
| `location` | as anywhere else; `Online` and `Remote` are answers | | |
| `started` | when the post began | when the commitment began | **the month it was issued** |
| `ended` | when it ended, or `present` | or `present` | **the expiry month; where there is none, the issue month again** |

**`started` and `ended` equal is how a credential with no expiry is written**, and it is not a
workaround — the row prints the one month rather than a range to itself. Never write `present` on a
certification that does not expire: *present* says *still going*, and an exam that was passed is
not going.

**`title` on a certification is the issuer's own string, character for character** — *AWS Certified
Solutions Architect – Associate*, not *AWS Solutions Architect cert*. It is the one field on the
page most likely to be the posting's own term verbatim, and a posting asking for *AWS Certified
Solutions Architect* against a bank that wrote something else has a gap that is not real. Lift it
off the certificate; if the user does not have it in front of them, ask them to check rather than
writing what they remember.

### 9.3 The depth pass, per type

**Do not skip it. One claim is what the row's tail is composed from, and a supporting entry with no
Claim can only ever render its bare label** — fine for a certification, poor for the other two.

- **A position of responsibility digs exactly like a job.** It has a before and an after, people who
  wanted something, something that broke. §3 unchanged, §3's Angles unchanged. *"What was the
  placement cell doing before you took it?"* · *"What did you inherit?"* · *"Who was waiting on
  you?"* · *"What went wrong on your watch?"* The denominator and the reach are the two that matter
  most here and they are usually right there — *six branches*, *forty companies*, *three hundred
  students* — and they are Evidence prose, not the claim's `number:`, exactly as §3's Numbers says.

- **An extracurricular digs for the commitment and what came of it**, and the trap is composing a
  hobby. *"How long, and how often?"* · *"What level was it at?"* · *"What did you end up
  organising or running?"* · *"Who else was involved?"* A season played is a fact; *taught me
  teamwork* is not a claim and never goes in the file — that is mush, and §3's rule holds: the fix
  is another question.

- **A certification digs for what it was for.** The exam is not the claim. Ask *"what made you take
  it?"* · *"what did it let you do that you could not before?"* · *"what did it cover that you
  actually use?"* · *"did anything at work or in a project change after it?"* What that produces is
  the room to re-angle — which is the whole point, since a posting naming the credential can use
  the bare label, and a posting naming the *skill* needs a tail that says the user can do the
  thing.

  **Never write a score or a percentile.** It fails the "So what?" test by construction — an
  exam score is a number about the exam, not about anything that changed — and it invites a
  comparison nobody asked for. Where the user wants it in, §3's rule applies: say once why it stays
  out of the `number:` field, then take their answer; it may live in the Evidence as texture.

### 9.4 The Shallowness checks, adjusted in exactly two places

Both **Shallow entry** checks — *fewer than three claims* and *no claim carries a sizing fact* —
**do not apply.** They are checks about filling a block, and a supporting entry has no block. A
certification with one claim is not thin; it is a certification. So **§7's smell report says nothing
about claim count on these three**.

The two **Shallow claim** checks apply unchanged to `responsibility` and `extracurricular`. On a
`certification`, **the first one — *it says what changed* — is lifted**: the claim a credential
makes is that it was *earned*, which is a fact about the user rather than a difference afterwards.
**The second — *there is room to re-angle it* — binds hard, and is what §9.3's questions are for.**
A certification whose Evidence says only *"passed the exam"* is parked (§4) like anything else, and
the offer is worth making plainly: *"I have the credential and nothing about what it was for — park
it? The row still renders, it just can't say anything beyond the name."*

### 9.5 The closing move does not run

No `## lead` block on a supporting entry, and do not offer one. The lead is the frame around a
**Bullet column**, and there is no column here — one row has nothing to frame. §6.5 is skipped
whole, on a cold session and at the return door both, and §8.1's *"and no lead — want to do that
now?"* is not said on these three.
