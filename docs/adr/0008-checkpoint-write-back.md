# Checkpoint write-back: in-flow answers reach the bank marked, framing answers never do

**Status:** accepted

## Context

The checkpoint (`docs/adr/0002-checkpoint-design.md`, #7) asks the maker questions mid-run and
records the answers. Some of those answers are *new facts about the maker's own history* —
volunteered at a coverage gap, in the middle of tailoring. The bank they would land in is
otherwise built through a careful ingestion interview that excavates evidence and refuses mush.

So checkpoint write-back is a **back door into a rigorous store**, and the tension is real: let
everything through and the bank degrades into a pile of one-liners; let nothing through and the
same coverage gap re-fires on every similar JD, which is precisely the recurrence the feature
exists to kill.

This ADR fixes which answers reach the bank, what marks them, and where the ones that never
reach it live instead. Resolved in issue #13.

## Decision

### Three kinds of checkpoint answer, not two

The ticket assumed a binary — JD-specific framing vs. bank gaps. Walking the item catalogue in
`0002` turns up a third shape, and it is the dangerous one:

| kind | example | destination | recurs? |
| --- | --- | --- | --- |
| **framing** | "lead backend for this JD" | `runs/<jd-slug>/checkpoint.md` only | yes, and correctly so |
| **add** | "I did run Kafka at Acme" | a new **Claim** in the bank, immediately | no — that is the point |
| **revise** | "that 40% isn't real" | run-local, plus an offer to fix the bank | until settled |

**Revise** is the confidence fork (feature / soften / drop). Its answer is not a statement about
the company — it is a statement about the claim's truth — but it is also not a gap being filled.
Collapsing it into either neighbour breaks something: treat it as pure framing and the same doubt
is re-litigated on every JD forever; treat it as a bank edit and a per-JD judgment call silently
destroys stored content.

### The rigour gap is thinness, not falsehood

A checkpoint answer must be good enough to render a bullet from and defend in an interview —
that is why it was asked. It is **not less true** than an interviewed claim. What it lacks is
*excavation*: it is volunteered rather than dug out, narrow rather than complete, and it arrives
with a sound `assertion` and a nearly-empty `evidence` body. The "so what?" test was never
applied to any number in it.

This reframe is load-bearing. The risk is not a **false** bank; it is a bank holding claims that
cannot be re-framed for a future JD, because render has no evidence to draw a different angle
from.

### Adds land in the bank immediately, marked `needs-interview: yes`

The new Claim is written into `bank/jobs/<slug>.md` (or `projects/`) at the moment it is given,
and the run then re-analyses per `0002`'s add-evidence loop-back. It competes on the next JD like
any other claim.

The mark is a loose `key: value` line in the Claim section, following `0005`'s convention for
`confidence: uncertain` — **written only when set, omitted otherwise**.

### The mark does nothing mechanically

Selection, packing, render, and the checkpoint all ignore `needs-interview`. It changes no score,
gates no slot, fires no fork.

This is deliberate, and it is not laziness: **thinness already enforces itself.** Downgrade-only
bounds render to what a claim's evidence *entails*, and a claim with one line of evidence entails
almost nothing beyond its own assertion — so render can restate it but cannot re-angle it. The
constraint is already present in a rule the project has locked; adding a second one would be
redundant.

The mark's single consumer is a later ingestion session. There is **no queue file**: `0005` bans
derived indexes because they rot on hand-edit, so the mark in the entry file *is* the queue,
found by grep over `bank/`.

Explicitly rejected: making the mark auto-fire the **Confidence flag**. That would escalate every
thin claim to a fork on every JD — resurrecting the recurrence this ADR exists to kill — and
`0003` already ruled that provenance never auto-fires escalation and the flag is hand-set only.

### Adds are claims-only; a missing Entry is a Gap-report line

A coverage gap answered with evidence from a job or project **not already in the bank** does not
create an Entry mid-flow. It becomes a **Gap report** line for this run and a to-do for a real
ingestion session.

An Entry carries the spine of the résumé — dates, org, seniority context — and admitting one
through the back door, with a single thin claim, is a larger act than adding a claim to an entry
whose shape is already established.

### The confidence fork is answered run-local, with an inline offer

The fork's answer always applies to **this run only**. Answering it then offers one follow-up:
*settle it in the bank while you're here?*

- **Take it** → the maker states the correction explicitly; the bank is edited; the flag resolves;
  it never recurs.
- **Decline** → the claim gains `needs-interview: yes`, **keeping** its `confidence: uncertain`,
  which still marks real doubt and still governs escalation.

A bank edit can never be *inferred* from a fork answer, because **the answer carries no content**:
"soften" tells render how to phrase a line, but not that the number is really 25% rather than 40%.
The correction has to be said out loud, which is why it costs a beat that the **add** case does
not — an add arrives with its content attached. That asymmetry is intrinsic to the case.

Asking then rather than deferring is the right trade because the maker has the context loaded;
an ingestion session three weeks later starts from "which claim was this?"

### Framing answers never touch the bank, and there is no cross-run store

A framing answer lives in `runs/<jd-slug>/checkpoint.md` and nowhere else. There is no keyed
store of "how I position myself" outside `bank/` — that would be a second bank, and its key
("this JD splits frontend/backend") is itself a judgment call, so it could not be matched
deterministically anyway.

**Cross-run consistency is served by a glance, not a store.** When a framing fork is about to be
shown, Opus reads past `checkpoint.md` files and surfaces what the maker chose before ("you led
backend on `acme-backend` and `stripe-platform`"). The glance is:

- **Lazy** — it happens only when a fork actually fires, which the conditional checkpoint already
  makes rare. It reads every past `checkpoint.md`; there is no last-N cut-off.
- **Informative, never decisive** — the fork is still asked, and the maker's answer is what is
  recorded. This is the same shape `0002` already fixed for **Company research**: non-reproducible
  context may inform a recorded human answer, but never enters the selector as a persisted input.
- **Recorded** — `checkpoint.md` captures what was shown alongside what was answered, because the
  glance is the fork's one non-reproducible input and `0002` requires the record to carry the
  reasoning, not just the verdict.

**Material determinism is untouched.** Re-running a slug replays that run's own `checkpoint.md`
and does not re-glance.

### Write-back survives an abandoned run

The bank edit happens when the answer is given, not when the run ships. Abandoning the run
afterwards leaves the new claim in place — it is true whether or not that application is
finished.

## Considered options (rejected)

- **A holding pen outside the bank** (an inbox drained by a later ingestion interview) — rejected.
  Zero pollution by construction, and genuinely attractive until you notice it does not solve the
  stated problem: until the inbox is drained, the next similar JD hits the *same* coverage gap.
  The recurrence was the whole point.
- **Writing adds in unmarked** — rejected: simplest possible design, but it destroys any way to
  ask "what in my bank has never been interviewed?"
- **A mark that caps what the claim can win** (barred from a bullet slot while an interviewed
  claim is available) — rejected: it half-wastes the write-back, handicapping the very claim that
  was added because the JD needed it.
- **The confidence-fork answer rewriting the bank directly** — rejected on two counts: it destroys
  stored content as a side-effect of a per-JD judgment, and it cannot express corrections that
  need new content ("soften" carries none).
- **Never offering an inline fix, always deferring to the queue** — rejected: strictest separation
  and zero extra questions, but it defers the correction to the moment the maker has least
  context.
- **Admitting new Entries mid-flow, thin-marked** — rejected (see above); an Entry is the résumé's
  spine, not an increment on an established shape.
- **No cross-run visibility at all** (replay strictly same-slug) — considered and *not* taken: it
  is the cleanest determinism story, but it discards a consistency signal the maker wants, and the
  informs-only glance keeps determinism intact anyway.
- **A cross-run decisions file built for replay** — rejected: a second bank by another name, with
  an unsolvable keying problem.
- **Silent cross-run replay** (a confident match skips the fork) — rejected: output would depend
  on which other run folders happen to exist, so two identical JDs could render differently.
- **One mark per condition** (`origin: checkpoint` for adds, reusing `confidence: uncertain` for
  declined forks) — considered; the single `needs-interview: yes` was chosen instead, as one
  concept and one grep covering both populations.

## Consequences

- **Refines `0002`.** "A resolved fork replays on a similar JD; the coin-flip happens once"
  becomes: a past answer **informs** a fork that is still asked. There is no silent cross-run
  replay. Same-slug re-run behaviour is unchanged.
- **Extends the Claim schema** (`0004`, `0005`) with `needs-interview`, written only when set,
  alongside `number` / `provenance` / `confidence` / `skills`.
- **Fixes what `0002` deferred**: the checkpoint's record is `runs/<jd-slug>/checkpoint.md`
  (already fixed by `0007`), and it now also carries the glance.
- **Gives the ingestion branch a defined inbound edge.** Ingestion must handle two populations of
  marked claim — never-interviewed adds needing excavation, and declined forks needing a number
  settled — and clear the mark when done. This lands in the ingestion tickets, still fog.
- **Noted, not fixed:** a one-claim Entry's **Entry score** is the mean of a one-element set, so a
  dead-on claim sorts it to the top of Experience on a single line, above a richer entry scoring
  0.8 across three claims. The **Packer** handles the *size* correctly (slots = `min(3, claims ≥
  0.50)` = 1), so it cannot over-consume the page; only the ordering is odd. This is a
  pre-existing property of the ranking in `0006`, not something write-back introduces — recorded
  here because refusing mid-flow Entries removes the most likely way to *create* one.
