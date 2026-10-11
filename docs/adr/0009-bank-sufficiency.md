# Bank sufficiency: a shallow claim and a hole are different defects, told apart in the gap report

**Status:** accepted

## Context

The bank is the whole system's substrate: if an entry is thin on outcomes, tailoring produces
weak bullets from good machinery and the maker has no way to see why. The ticket (#15) asked
what "the bank is good enough" means, how thinness is detected, how the maker is prompted to
fix it, and how a thin-entry gap is distinguished from a real one.

The ticket predates `0003`, `0004`, `0005` and `0008`, and several of its premises moved:

- It proposed "a per-entry completeness signal over the schema fields". `0005` bans derived
  indexes (they rot on hand-edit) and `0006` fixes that Opus judges while a script only does
  arithmetic — so a computed completeness signal has neither a place to live nor a component
  entitled to produce it.
- It listed "no provenance" and "no quantitative *or* strong qualitative dimension" as thinness
  symptoms. `0003` made numbers optional and killed qualitative tags: a claim with no number is
  frequently a claim whose number failed the **"so what?" test**, which is the interview
  working, not failing.
- It listed "unanswered why/who/what-it-replaced fields from the interview". `0004`'s Claim has
  no such fields; checking for them would invent structure the bank does not have.
- `0008` already named one specific thinness — the un-excavated checkpoint **add** — and gave it
  the `needs-interview` mark. This ADR generalises that notion and reuses the mark rather than
  inventing a parallel one.

## Decision

### Two failure modes, both owned here

"My bank isn't good enough" means one of two different things:

| | what it is | how it is found | the fix |
| --- | --- | --- | --- |
| **shallow claim** | the work is in the bank; the claim cannot say enough about it | judgeable **cold**, claim against itself | deepen it — an ingestion interview |
| **hole** | the work was never ingested at all | only **against a target** | ingest something new, or accept it |

They are kept separate because they need different machinery — but they are owned by one
decision, because at the moment the maker feels the pain they are **indistinguishable**:
`gaps.md` says "no evidence for event-driven systems" and nothing tells them whether they never
did it or did it at Acme and the entry is too shallow to say so. Telling them apart is this
ADR's concrete deliverable.

### The target for holes is the run history, not a target-roles file

A hole is not a defect in the abstract — "no evidence of leading a team" is only a problem if
the maker applies to lead roles. The target is therefore **the JDs actually run**, read from
`runs/*/gaps.md`.

Rejected: a hand-maintained target-roles file audited against cold. It is a second artifact to
keep current, it goes stale silently, and it licenses the agent to invent gaps the maker does
not care about.

### Three shallowness checks, and only three

**At the Claim level:**

1. **It never says what changed.** The claim describes what was built and how, and never what
   was different afterwards. This is the ticket's headline worry and the defect that actually
   sinks a claim: it will score badly against every JD forever, because no job ad asks for
   activity.
2. **There is no room to re-angle it.** The `evidence` body entails nothing the `assertion` does
   not already state. Under **downgrade-only**, render can restate such a claim and nothing
   more — it works for the one JD it was written for and is dead weight on every other. This is
   `0008`'s thinness, now detectable outside a checkpoint.

**At the Entry level:**

3. **Too few claims to fill a block.** An entry with one or two claims can never take three
   bullet lines, so a three-year job renders as a one-liner beside a side project. Worth
   flagging even when every individual claim is sound. *(This is also the ordering oddity
   `0008` recorded: a one-claim entry's **Entry score** is the mean of a one-element set.)*

**Explicitly not checks:** a missing number, a missing provenance, or any "why / who / what it
replaced" field — see Context.

### The gap report sorts every line into three classes

`runs/<jd-slug>/gaps.md` stops being a flat list of uncovered must-haves. Each line is
classified:

| class | meaning | action |
| --- | --- | --- |
| **nothing in the bank** | no work in this territory at all | ingest something new, or apply anyway |
| **too shallow to claim it** | something is in the territory but cannot carry the claim — **names the claim id** | deepen that claim |
| **you have it, the page did not** | a claim covers it cleanly, but its entry lost the page or the claim lost a slot | nothing to fix in the bank |

The third class earns its place by preventing a false alarm: without it the maker reads a gap
report and goes off to deepen an entry that was already good enough, because the report failed
to say the problem was the page budget.

Classification is **Opus's judgement, not a threshold.** The **Score table** scores each Claim
against the JD as a whole, not against each requirement individually, so no number can be read
off to mean "close on Kafka". What makes the judgement checkable is that the middle class must
**name the claim id** it suspects — an unnamed suspicion is not reportable.

### Ingestion: a finish line, not a gate

The three checks are the ingestion interview's **definition of done** — it keeps digging until
each claim says what changed and carries evidence with more in it than the assertion. This is
what the ingestion branch has otherwise lacked: without it the interview simply stops when it
runs out of questions.

They are **not** a lock on the door. When the interview genuinely cannot get there — the number
is unrecoverable, the work predates anything checkable — the claim **lands anyway, marked
`needs-interview: yes`**. A shallow claim beats no claim: downgrade-only already stops it from
over-claiming, and it can still win a bullet on a JD it fits head-on.

This is a **third population** wearing `0008`'s mark, alongside checkpoint adds and declined
confidence forks. Same meaning ("owed more interview"), same grep. It does not dilute the queue,
because it is set by something that happened in a session, not by an opinion.

*How the interview digs is not decided here — that stays with the ingestion tickets. This ADR
fixes only the standard they aim at.*

### Tailoring: a notification, and answers land as new claims

A "too shallow to claim it" gap line is a **Notification, never a Fork.** It fails `0002`'s
gate on both counts: the run knows exactly what to do without the maker (claim only what is
covered, report the rest), so it is adjudicable; and stalling a résumé the maker is sending
tonight on a bank-maintenance chore is the wrong trade. It rides the coverage-gap Notification
`0002` already defines, with a sharper line — naming the claim rather than saying "nothing
covers this".

If the maker answers it anyway ("I owned that on-call for two years, two incidents"), the answer
lands as a **new Claim** marked `needs-interview: yes` — `0008`'s existing **add** path — not as
an append to the existing claim's `evidence`.

Rejected: appending to the existing claim. It reads more naturally, but it mixes volunteered
material into a claim that was properly interviewed, after which the two are inseparable — and
it edits stored content mid-run, which `0008` refused for the confidence fork for the same
reason. The cost of the chosen path is an entry holding two claims circling the same work until
an interview merges them; merging is exactly what draining the mark is for.

### The audit is standalone, read-only, and leaves nothing behind

A deliberate "how is my bank doing?" pass, invoked outside a tailoring run. It is **bank
maintenance**, not a third capability alongside ingestion and tailoring. Two halves:

- **the cold sweep** — reads the bank and lists claims failing the shallowness checks
- **the recurrence view** — reads every `runs/*/gaps.md` and orders findings by how often each
  has actually cost the maker something ("event-driven came up in four of nine runs; three said
  Acme is too shallow, one said nothing's there"), carrying the three classes through

**It marks nothing.** `needs-interview` means *something happened to this claim*; an audit's
opinion is not an event. If an audit could stamp it, the first run would stamp a large fraction
of the bank and the grep would stop being a queue.

**It writes no file.** A committed `bank-health.md` is precisely the derived index `0005` banned:
stale the moment an entry is hand-edited, and then actively misleading. The audit is cheap to
re-run and always current, so it prints and the maker acts or does not. The accepted cost is
that nothing persists between audits — "starting over" here means re-reading the bank, which is
what keeps it honest.

**Repeat offenders are re-checked for freshness.** A gap recorded in an old run may already be
fixed, so anything recurring is re-checked against the bank as it stands before being reported.
Only the recurring items are re-checked, so the pass stays cheap and never nags about something
already dealt with.

### There is no completeness score and no "done"

No percentage, no per-entry score, no bank-level grade. Such a number would be arithmetic over a
schema with almost no required fields, and `0006` already put the line in the right place:
judgement is stated in words, arithmetic is reserved for what is genuinely countable.

**Recurrence replaces "done".** The bank is good enough for the kind of job the maker actually
applies to when nothing keeps repeating in the gap reports. The bank grows and evolves; there is
no terminal state.

## Considered options (rejected)

- **A computed per-entry completeness signal over the schema fields** (the ticket's proposal) —
  rejected: `0004`'s schema has too few required fields for the arithmetic to mean anything, and
  `0005`/`0006` leave it nowhere to live and no component entitled to compute it.
- **A hand-maintained target-roles file** as the standard holes are judged against — rejected:
  a second artifact that goes stale silently, and an invitation to invent gaps.
- **An ingestion gate that refuses to land a claim failing the checks** — rejected: a shallow
  claim beats no claim, and downgrade-only already bounds what it can do.
- **The audit writing `needs-interview` on what it finds** — rejected: it would stamp a large
  fraction of the bank on first run and destroy the queue's meaning.
- **A committed bank-health report** — rejected as a derived index (`0005`), stale on the first
  hand-edit.
- **A thin-entry gap as a Checkpoint Fork** — rejected: adjudicable, so it fails `0002`'s gate,
  and it stalls the run on maintenance.
- **Appending a checkpoint answer to the existing claim's evidence** — rejected: it fuses
  volunteered material into interviewed material irreversibly.
- **Folding "you have it, the page did not" into "not a gap, do not report"** — considered and
  not taken: silence there is what sends the maker off to fix a bank that is fine.

## Consequences

- **Extends `0001`/`0007`'s Gap report** with three classes; the "too shallow" class must name a
  claim id.
- **Sharpens `0002`'s coverage-gap Notification**: it now says which of the three classes fired,
  and names the suspect claim where there is one.
- **Extends `0008`'s `needs-interview` mark with a third population** — claims the ingestion
  interview could not excavate — without changing its (nil) mechanical effect.
- **Gives the ingestion branch its definition of done.** The three checks are the interview's
  finish line; the ingestion tickets design how it digs toward them.
- **Adds a bank-maintenance pass** to the system's surface: read-only, print-only, invoked
  deliberately. Not a third capability — `CLAUDE.md`'s "two capabilities" stands.
- **The merge duty lands on ingestion.** Answering a shallow-gap notification creates a second
  claim circling the same work; draining `needs-interview` must merge as well as excavate.
