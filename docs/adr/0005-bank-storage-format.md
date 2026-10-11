# Bank storage format: one markdown file per entry, read directly by the agent

**Status:** accepted

## Context

The schema (`0004`, #9) fixed the *shape* of the bank — Entries owning pools of Claims,
stable Entry and Claim ids, prose `assertion`/`evidence` alongside structured
`number`/`provenance`/`confidence`/`skills` — and explicitly deferred *how it lands on disk*
to this decision (#10): id encoding and on-disk layout. This is hard to reverse once the bank
holds entries, hence an ADR.

The bank must be **version-controlled and diffable**, **survive hand-editing** (entry-evolution
is still fog on map #3), hold the **confidential-source shareable form** cleanly, and feed
whatever the selection-locus decision (#11) needs.

The governing fact that collapses the choice: **there is no mechanical selector.** This runs
headless in Claude Code; **Opus reads the whole bank and drafts.** The "embedding + keyword
scoring" of the selection model (`0001`) is a *technique the agent applies*, not a standalone
service deserializing structs. So nothing downstream needs machine-parseable structure — the
reader parses prose natively.

## Decision

### Pure markdown, one file per Entry — single source of truth, no derived index

The bank is **markdown**, **one file per Entry**, hand-edited, **read directly by Opus**. No
generated structured mirror. The "both, with a derived index" option is **rejected**: its only
job was to feed a mechanical selector, which does not exist; a derived index is a second copy
that silently rots on every hand-edit — the exact opposite of the survive-hand-editing
requirement. One representation, no sync.

One file **per Entry** (not one big `bank.md`): a change to one job is a one-file diff, git
blame is per-Entry, the on-disk unit matches the schema's "Entry is the competing block," and
Opus can read entries selectively if the bank ever outgrows a single context window.

### Layout: `bank/` split by Entry type; the filename slug *is* the Entry id

```
bank/
  jobs/<slug>.md        # type: job
  projects/<slug>.md    # type: project
  profile.md            # static profile — never competes
```

- **The filename slug is the Entry `id`.** `bank/jobs/acme-backend-api.md` → id
  `acme-backend-api`. The path *is* the identity; there is no separate `id:` field to keep in
  sync. Human-readable, greppable, stable. (Renaming a file changes its id and thus its key in
  the run artifact / determinism machinery — rare, deliberate, accepted.)
- **Subfolders mirror `type` only** — `jobs/` and `projects/`, the schema's two Entry types and
  the resume's two competing sections. No other filing axis (employer, domain, year): those are
  ranking signals the selector reads *inside* the file, not directory structure.
- **`bank/profile.md`** holds the **static profile** — name, contact, links, **education**. It
  lives *outside* the jobs/projects competition so the selector's world stays "jobs and
  projects only." (Split into `bank/profile/` files if contact/links/education grow; the point
  is only that it is marked static and never competes.)

### Skills are not stored entities — no `skills/` folder

Skills stay a **free-form `skills:` list inside each Claim**, per the schema and `0003`'s
no-tags rule. There is deliberately **no `skills/` folder or master list**: the resume's Skills
section is a **breadth list composed at render time** by gathering the skills off the selected
Claims. A standalone skills store would reintroduce the curated taxonomy `0003`/`0004` rejected
and would immediately drift from what the Claims actually say.

### Inside a file: YAML frontmatter for the Entry, a markdown section per Claim

Entry metadata (all short scalars) → **YAML frontmatter**. Each Claim → a **markdown section**:
an opaque id heading, a few loose `key: value` lines for the structured bits, then prose.

```markdown
---
type: job
title: Backend Engineer
org: Acme Corp
location: Remote
dates: 2023-01 – 2024-06
domain: fintech / payments
---

## c1
number: 40%  ·  provenance: measured
skills: [postgres, query-optimization, caching]

**Assertion:** Cut checkout API p95 latency by 40%.

**Evidence:** Traced the hot path to an unindexed join on the orders table
under load; added a composite index plus a read-through cache. (Interview-defense
context — never rendered verbatim.)
```

- **Claim `id` is opaque and content-independent** — sequential **`c1`, `c2`** per Entry,
  globally addressed as `<entry-slug>/c1`. Frozen at ingestion. It is *not* a slug of the
  assertion: the schema requires the id to survive rewording, so it must not derive from the
  wording. An opaque id is never tempting to "rename to match the new phrasing," and the
  assertion sitting directly beneath supplies all the human readability needed.
- **Structured bits are loose `key: value` lines**, not a nested YAML block — less punctuation
  to hand-edit; `number`/`provenance`/`confidence`/`skills` are the only structured fields.
- **Prose fields (`assertion`, `evidence`) are markdown body**, never quoted YAML strings —
  this is the whole reason markdown beats structured formats here; `evidence` is often a
  paragraph.

### Representation conventions

- **Confidence flag is present-or-absent, not a value.** Omit the line when the Claim is fine;
  write `confidence: uncertain` *only* when flagged. Absence is the common case; presence is the
  signal that escalates to the checkpoint (`0002`).
- **Number stays human-readable text** — `number: 40%` with `provenance: measured`, *not* split
  into `magnitude`/`unit` sub-keys. Opus reads the text and the Number-trace check (`0003`)
  compares against it; nothing mechanical needs the split. The `number`/`provenance` pair is
  **omitted** for a purely-qualitative Claim.
- **Absent optional fields are omitted** — no `domain: null`, no `skills: []`. Not there means
  not there. Keeps hand-edits clean and diffs quiet.
- **Confidential sources need nothing on disk.** Confidential material is scrubbed to its
  shareable form *at ingestion* (`0004`), so the bank only ever holds an already-safe Claim,
  indistinguishable from any other. No marker, no quarantine folder — the format satisfies the
  requirement by having nothing to do.

### Run artifacts are not bank content

The per-run diffable artifact (`0002`, determinism) is a **tailoring output, not the bank**. It
is markdown-in-git and diffable like everything else, but lives **outside `bank/`** (e.g.
`runs/<jd-slug>/`) so per-JD churn never pollutes Entry history. Its exact location and contents
are the render/checkpoint decisions' call (#12 and what #7 opened), not this ticket's.

## Considered options (rejected)

- **Structured throughout (YAML/JSON per entry)** — rejected: the prose `assertion`/`evidence`
  fields read terribly as quoted strings, and the structure buys nothing when the reader is an
  agent that parses prose natively.
- **A derived structured index alongside markdown ("both")** — rejected: its consumer (a
  mechanical selector) does not exist, and a second derived copy rots on every hand-edit.
- **One big `bank.md`** — rejected: noisy diffs, all-or-nothing context load, and the on-disk
  unit stops matching the competing block.
- **A `skills/` folder / curated skills store** — rejected: reopens the no-tags decision
  (`0003`/`0004`); skills live inside Claims, the Skills section is derived at render.
- **Content-derived (slug) Claim ids** — rejected: they break on rewording, which the schema
  forbids.
- **Splitting `number` into `magnitude`/`unit` sub-keys** — rejected by the field test: nothing
  mechanical reads the split.

## Consequences

- **Selection locus (#11)** now inherits a strong prior: since Opus reads the bank files
  directly, the "skill reading files" shape is favoured over a standalone scoring script. #11
  still decides this on its own terms; this ADR only removes the mechanical-parser pressure.
- **Render (#12)** reads Entries from `bank/{jobs,projects}/*.md` + `bank/profile.md`, composes
  Bullets from Claim prose, and writes its run artifact *outside* `bank/`.
- **The ingestion branch** (map #3 fog) must *write* this layout: create/update one markdown
  file per Entry under the right type folder, assign the filename slug (Entry id) and sequential
  Claim ids, and emit already-scrubbed Claims. Entry-evolution (re-run-and-diff vs append over
  hand-edited files) remains fog; this format's per-file, per-Claim-id diffability is what makes
  that decision tractable later.
