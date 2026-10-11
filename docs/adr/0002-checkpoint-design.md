# Checkpoint design: what the pre-render checkpoint contains, and what earns a question

**Status:** accepted

## Context

Tailoring needs one batched round where it surfaces its uncertainty to the human
*before* writing any LaTeX — the **checkpoint**. The feature dies in both directions: ask
about everything and it becomes a second interview ("just pick"); ask about nothing and the
human is left arguing with a finished PDF. This ADR fixes what the checkpoint contains and,
critically, the **gate** — what earns a question versus what is decided-and-logged silently.

It is designed backwards from the selection model (`docs/adr/0001-selection-model.md`, #4),
which already hands over the raw material: three contested-slot kinds that escalate (coverage
gap, JD ambiguity, confidence flag) and two that resolve silently (boundary ties,
recency-vs-relevance). Resolved in issue #7.

## Decision

- **Form.** The checkpoint's spine is an **angle statement** plus a bounded set of either/or
  **forks**. The angle statement is one short frame — how the JD was read and the argument the
  resume will make — and it *names which entries lead*, so the shortlist is shown as
  overridable context, **not** a separate tick-box approval gate. A bare shortlist is the most
  bikeshed-prone form and carries the least reasoning, so it is never its own step.

- **Two item classes.** The checkpoint holds **notifications** (FYI — nothing to decide; the
  human may react but need not) and **forks** (actionable — the system will not proceed on that
  point until the human chooses). Either class is enough to make an otherwise-silent run
  surface.

- **Conditional presence (silent path).** When the selector and the JD align fully and nothing
  needs the human, the run renders straight through — no checkpoint, no rubber-stamp. A gate
  whose only possible response is "allow" is theatre and trains reflexive approval. The output
  PDF (regenerable) is the backstop for the rare confidently-wrong read.

- **The gate.** A contest becomes a **fork** only when it is **load-bearing** (touches
  coverage, interpretation, or truth — the resume's core) **and unadjudicable** from the JD
  text, the bank, and fixed tiebreaks. Load-bearing but *adjudicable* → **decided by rule and
  logged** in the run's readable decisions record, never asked. Not load-bearing (boundary
  ties, recency-vs-relevance) → **decided silently**, not even logged as a question. A contest
  is **never** resolved by inventing.

- **Item catalogue** (the five contested kinds from #4, sorted through the gate):
  - **Coverage gap** → **notification** with an escape hatch: point the system at evidence /
    add it and **re-analyse**, or accept it as a Gap-report line. Never a fork, never
    fabricated — there is nothing to *choose*, only a fact to be told.
  - **JD framing ambiguity** → a strictly **binary fork** (A / B), offered *only* when the JD
    genuinely splits two ways (e.g. frontend vs backend). A third response, **"research the
    company,"** lets external context break the tie instead of a blind pick. **More than two
    directions** is a JD-quality signal, not a real fork → **default-and-notify**: pick the
    highest-fit angle by fixed rule, log the reasoning, and show an FYI notification.
  - **Confidence flag** → **fork**: feature / soften / drop a high-fit claim resting on shaky
    recollection.
  - **Boundary ties, recency-vs-relevance** → silent, by fixed rule (per #4).

- **No hard cap on forks.** The gate *is* the budget: every fork shown has already passed
  load-bearing-and-unadjudicable, so a numeric cap could only force a forbidden outcome
  (fabricate an answer, or silently make a risky choice). Forks are ordered
  most-load-bearing-first; an unusual *volume* of forks is a signal handled upstream — many
  confidence flags mean a thin, recollection-heavy bank (#15); many directions mean a diffuse
  JD (handled above), not a checkpoint that muzzles genuine questions.

- **Recording.** The angle, the silent calls and their reasons, the checkpoint items, and the
  **human's answers** are all captured in the **per-run diffable artifact** mandated by #4 —
  human-readable, so material determinism is auditable by diffing runs. Recorded answers are
  **first-class replayable inputs**: a resolved fork replays on a similar JD; the coin-flip
  happens once. Company research only *informs* the human's recorded choice, so live web
  content never enters the selector as a persisted input and never breaks determinism.

- **Control flow.** Some answers **loop back** into selection (add-evidence → re-analyse)
  rather than proceed to render; the re-run is a fresh (possibly silent) checkpoint.

## Considered options (rejected)

- **Shortlist approval as its own gate** — rejected: most granular and most bikeshed-prone,
  and it presents entries without the *why*. Folded into the angle statement as context
  instead.
- **Always show the checkpoint** (one-glance confirm on clean runs) — rejected: a gate whose
  only response is "allow" trains rubber-stamping and adds friction with no value; the silent
  path with a PDF backstop is the better trade for a single-user tool.
- **A numeric cap on forks** — rejected: would force fabrication or a silent risky choice,
  both forbidden. Volume is controlled upstream (bank sufficiency, JD quality), not by muzzling
  earned questions.
- **Multi-way framing menu for a diffuse JD** — rejected: a >2-way multiple-choice is itself
  the second-interview failure; default-and-notify keeps forks binary while still telling the
  human the pick was a judgment call.
- **Company research as a silent selector input** — rejected: live web content is
  non-reproducible; it must feed a recorded *human* answer to preserve material determinism.

## Consequences

- **Boundary with neighbouring tickets.** #7 asserts only *that* the reasoning, angle, items,
  and answers are captured in the per-run artifact and are human-readable. The artifact's
  **storage format** is deferred to #10; propagating a checkpoint **answer back into the bank**
  is deferred to #13.
- **New capability graduated.** The "research the company" action is in scope for v1, but it is
  a **cross-cutting company-research capability**, not a checkpoint sub-detail — its mechanism
  (trusted sources, company-identity confirmation, how much to pull, whether anything lands in
  the bank, how a result feeds a fork) is its own grilling ticket. The framing fork is its
  first consumer; it may also serve the ingestion branch where a source is silent.
- **Feeds the qual/quant ticket (#8).** Confidence-flag feature/soften/drop mechanics detail
  the no-silent-upgrade boundary under this claim-level rule.
