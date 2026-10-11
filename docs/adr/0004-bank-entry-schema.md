# Bank entry schema: a raw claim pool, designed backwards from the selector

**Status:** accepted

## Context

The bank is the shared knowledge base both capabilities read and write. Its schema is the
last big tailoring decision, deliberately resolved **late** and **backwards** — from what the
selector (`0001`, #4), the checkpoint (`0002`, #7), and the qual/quant position (`0003`, #8)
actually consume — never forwards from what is easy to extract at ingestion. Resolved in
issue #9.

The governing test for every field: *does the selector, checkpoint, or number-logic actually
read it?* If nothing reads it, it does not belong.

Two of the ticket's original bullets were **overruled by #8** before this decision and are
recorded here as rejected: a third "recalled" provenance tier (folded into *estimated*), and
first-class structured qualitative-strength fields (scope/ownership/complexity as tags — #8
chose strong prose instead).

## Decision

### The bank is always raw — a pool of claims, not finished bullets

The bank stores **raw material**, never render-ready lines. This is a deliberate
optimise-for-best-output-not-efficiency choice: the bank is the knowledge base, and finished
prose would defeat its purpose. An **Entry** (a job or project) owns a **pool of Claims**; the
**Bullet is a render-time output unit**, composed per-JD — the bank does not store Bullets. An
entry holds *more* material than any one resume shows; render selects and phrases the ~3
Bullets that fit a given JD.

### The Claim is the atomic stored unit — one assertion each

A **Claim** is a single assertion, carrying at most one number. "Cut latency 40% and cost 30%"
is *two* claims. This makes #8's "per-claim" number/provenance/flag literal, and makes a
Bullet that combines claims traceable claim-by-claim. A Claim carries:

- **`id`** — stable identity, assigned at ingestion, persistent across edits (a reworded claim
  keeps its id). Required by the Number-trace check, Material determinism / the diffable run
  artifact, and entry-evolution re-run-and-diff. *Encoding* (uuid / slug / filename+anchor)
  is deferred to storage (#10); the schema mandates only the addressability.
- **`assertion`** — the canonical, **neutral** core fact, written *not* framed toward any JD
  (not slanted to metrics, not to scope). It is render's default/anchor phrasing and the
  **trace target**. It is deliberately *not* the matching key (see below).
- **`evidence`** (backing) — the richer dug-out context the interview excavated. **Never
  rendered verbatim.** It exists for interview-defense, for the Claim-level trace, and as the
  material render draws a *different* angle from for a different JD.
- **`number`** (optional) — `{magnitude, unit, provenance}`, at most one. Absent for a
  purely-qualitative claim.
- **`provenance`** — `measured | estimated`, riding *with* the number (absent when there is no
  number). Drives wording and the Number-trace check, per #8.
- **`confidence` flag** — the hand-set doubt marker (#8). Per-claim, applies to qualitative
  *or* quantitative claims, and is the **only** field that escalates a claim to the checkpoint.
- **`skills`** — a **free-form** list of the skills/tech this claim demonstrates. Not a curated
  taxonomy and not a distilled JD checklist — an extra bank-side signal consumed by skill
  coverage, the Gap report, and the Skills breadth section.

### The Entry is the competing block

An **Entry** carries: **`id`** (stable, as above); **`type`** = `job | project` (routes to the
Experience/Projects section, and a ranking signal); **`title`**/role; **`org`** (nullable /
personal); **`location`**; **`dates`** start/end (the recency and pinned-relative-time source);
**`domain`** (a light ranking field); and its **`claims`** pool. Everything else — scope,
seniority, impact — lives *inside* claims as prose + skills, per #8's no-tags rule. There is no
`seniority` field; that signal rides in the prose and is matched semantically.

### Matching is on the whole claim; framing is neutral in the bank

Two behaviours this schema fixes, both direct consequences of "always raw":

1. **The selector matches the *whole claim* — assertion + evidence + skills — against the full
   JD text.** The neutral assertion is *never* the match key. A claim therefore surfaces if
   *any* angle of its material fits the JD, so a fixed assertion phrasing can never lock out a
   JD that a different angle of the same backing would win. This mirrors the selection model's
   "whole JD meets the whole bank" and strengthens Material determinism.
2. **Render composes the Bullet per-JD from the full material** — downgrade-only and
   entailment-bounded (whatever lands on the page must be entailed by assertion + evidence).
   Render owns phrasing; the bank owns facts.

### Static profile is not a bank entry

Name, contact, links, and **education** are a small **static profile** render always emits into
the fixed skeleton. They never compete for slots (the maker is early-career: education is a
permanent fixture, never in the competition). Keeping them out of the entry pool keeps the
selector's world to jobs and projects only.

### Not stored (derived, not fields)

- The **"~"** tilde — a render convention derived from `provenance = estimated`, not a stored
  field.
- Any **confidential marker** — confidential sources are scrubbed to a shareable form *at
  ingestion*; the bank only ever holds the already-safe claim, and nothing downstream needs to
  know it was ever sensitive. (A private maker-only recall note earns no first-class field.)

## Considered options (rejected)

- **Storing finished/near-final Bullets** — rejected: defeats the raw-knowledge-base purpose
  and forbids per-JD reframing (a claim that should lead with a metric for one JD and a scope
  angle for another).
- **Making the assertion the matching key** — rejected: a fixed framing would lock out JDs a
  different angle of the same backing would win; matching is on the whole claim instead.
- **A third "recalled" provenance tier** — rejected upstream by #8; folded into *estimated*.
- **First-class structured qualitative-strength fields** (`scope:`, `ownership:`, …) — rejected
  upstream by #8; strength is dug-out prose the interview enforces, the selector matches full
  text.
- **A `confidential` field** — rejected by the field test: nothing downstream consumes it once
  the claim is scrubbed at ingestion.
- **A collapsed single prose blob per claim** (no assertion/evidence split) — rejected: the
  split walls "what may render" off from "context, do not lift verbatim," cheap insurance for
  zero-fabrication and a home for the interview's dug-out detail.

## Consequences

- **Storage format (#10)** inherits this shape to encode: entries owning claim pools, stable
  entry+claim ids, and the diffable-artifact requirement. It decides id encoding and on-disk
  layout.
- **Selection locus (#11)** must match the whole claim (assertion + evidence + skills) against
  the full JD, and must read the per-claim `skills` for coverage and the Gap report.
- **Render (#12)** composes Bullets from raw claim material, downgrade-only within entailment,
  and runs the Number-trace check against `number`/`provenance`.
- **The ingestion branch** (map #3 fog) now has its target: ingestion must *produce* this
  schema — neutral assertions, dug-out evidence, sorted provenance, hand-set confidence flags,
  free-form skills, scrubbed confidential material. The interview *mechanism* remains fog; this
  ADR fixes the *shape* it must fill.
