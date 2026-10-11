# Qual/quant position: numbers, provenance, and the no-silent-upgrade ratchet

**Status:** accepted

## Context

A tailored resume lives and dies on its claims, and the sharpest claims are numeric.
The design has to fix, as a first-class matter rather than a formatting afterthought:
how a claim's numeric truth (or its absence) is captured, how solid that number is, how
it is *spent* at render for a given JD, and — critically — how tailoring is stopped from
quietly inflating a claim. This is the through-line of the whole project: **zero
fabrication**. It resolves before the entry schema (#9) because it dictates several of
its fields. Resolved in issue #8.

It builds on the selection model (`docs/adr/0001-selection-model.md`, #4) — which
established the **Claim-level trace** ("every claim must be present in or entailed by its
Bank entry") and the **Confidence flag** — and on the checkpoint (`0002`, #7), which
already fixed the feature/soften/drop **Fork** for a flagged claim.

The organising principle: **the ingestion interview is where truth gets fixed; render only
ever spends that truth down, never up — and a mechanical check enforces it.**

## Decision

- **Split locus: facts at ingestion, framing per-JD at render, downgrade-only.** The bank
  stores a claim's raw truth — the number (if any), its provenance, and the qualitative
  substance around it — decided once at ingestion. *How* a given JD frames that truth
  (lead with the number vs. lead with the qualitative angle; a quant-heavy JD and an
  infra JD may frame the same entry differently) is chosen per-JD at render. Render may
  only ever move in the **downgrade** direction — drop a number, present it qualitatively,
  soften it — never invent or harden. Both "when is qual/quant decided" answers are true,
  but for different things.

- **Two provenance tiers, set at ingestion: measured vs. estimated.**
  - **Measured** — the number came from a real measurement (dashboard, benchmark, query,
    A/B test).
  - **Estimated** — everything else the maker believes but did not measure, *including a
    number simply remembered*. There is deliberately **no third "recalled" tier**: in a
    single-user system the maker's own interview-defense discipline ("I'll have to defend
    this number in the interview") is the guarantee against junk numbers, so a bare
    recollection is absorbed into *estimated* rather than machine-refused.
  The tier is set at ingestion, where the maker knows best, and serves mainly truth-tracking
  and interview prep.

- **Provenance drives wording, not escalation.** A **measured** number renders flat
  ("cut p99 latency 40%"); an **estimated** number renders softened ("~40%", "roughly").
  A "~" is also just **tidy rounding** and reads on either tier — a measured 39.98% still
  shows as "~40%" — so it is *not* a doubt signal. Being an estimate never, by itself,
  sends a claim to the checkpoint.

- **Doubt is a separate, hand-set Confidence flag, orthogonal to provenance.** The
  Confidence flag is raised deliberately at ingestion when the maker is genuinely unsure of
  a specific claim ("not sure, it's so-so"). *That* — and only that — escalates the claim to
  the checkpoint as a feature/soften/drop Fork (per `0002`). It is **never auto-fired by
  "estimated."** Auto-flagging every estimate was rejected: it would flood the checkpoint and
  destroy its conditional/silent path.

- **No qualitative tags — strong prose, enforced by the interview.** When there is no number,
  strength comes from concrete, dug-out prose (scope, ownership, complexity, constraint,
  novelty, judgment shown), **not** a taxonomy of structured "qualitative strength" tags. The
  selector already matches on full JD text, so a well-written qualitative bullet competes on
  its own; the fix for weak prose is the **ingestion interview refusing mush** and forcing
  specifics ("led the migration" → "sole owner of the 6-service migration, no team, tight
  deadline").

- **Meaningless numbers are refused in the interview.** A technically-true-but-empty number
  ("10,000 lines of code", "5 API endpoints", "managed 3 repos") faces a **"so what?"** test
  in the ingestion interview: it survives only if it connects to a genuine consequence, else
  it is cut to qualitative prose or dropped. There is **no automated vanity-metric detector** —
  a single-user system does not need one when the interview interrogates every claim.

- **A mechanical post-render trace check is the ratchet.** Because numbers are stored
  structured, the "no silent upgrade" guarantee is enforced by machine, not by hope. After
  render, a check extracts every number from the generated bullets and confirms each traces
  to the source entry with **equal-or-softer provenance**: no invented number, no "~40%"
  hardened to "40%", no estimate presented as measured, no bullet that was qualitative in the
  bank that grew a number. Any orphan or hardening **fails the run**. Construction-time
  discipline ("the render step is told only to use claims in the entry") is retained as the
  first line, but is not sufficient on its own — a guarantee cannot rest on the model policing
  itself.

## Considered options (rejected)

- **A third "recalled" provenance tier** (instrumented / estimated / recalled) — rejected:
  render only ever forks two ways (state vs. soften-and-flag), and in a single-user system the
  maker's interview-defense discipline already keeps junk numbers out, so a bare recollection
  folds into *estimated*. The distinction the third tier drew is carried instead by the
  separate, hand-set Confidence flag.
- **"Estimated" auto-fires the Confidence flag** — rejected: most numbers are estimates, so
  this would drag nearly everything to the checkpoint and train reflexive approval, gutting the
  conditional/silent checkpoint from `0002`.
- **Structured qualitative-strength tags** (`ownership: sole`, `scope: org-wide`, …) — rejected:
  the taxonomy would rot against the next entry, and the selector already matches full text; the
  real remedy for weak prose is an interview requirement, not a schema field.
- **An automated vanity-metric detector** at ingestion or render — rejected: unnecessary when
  the interview is already the gate; the machine's only job is to not *resurrect* a cut number.
- **Baking the qual/quant framing at ingestion** (render cannot reframe) — rejected: it throws
  away per-JD framing, where the same entry should lead with a metric for one JD and a
  qualitative angle for another.
- **Construction-time discipline alone for no-silent-upgrade** — rejected: "the model was told
  not to" is an intention, not a guarantee; the structured numbers make a mechanical trace check
  cheap and real, so the guarantee is enforced, not hoped for.

## Consequences

- **Drives the entry schema (#9).** Fixes three fields designed backwards from this decision:
  a **number** (magnitude + unit, optional), its **provenance** (measured / estimated), and a
  per-claim **Confidence flag**. The schema stores facts, not framing.
- **Adds a stage to the render pipeline (#12).** The **post-render number-trace check** is a
  mandatory lint between LaTeX generation and shipping; a failure blocks the run rather than
  emitting a fabricated PDF.
- **Loads the ingestion interview.** The interview carries the qual/quant weight — sorting
  measured vs. estimated, prompting the Confidence flag, applying the "so what?" test, refusing
  mush. The interview *mechanism* is ingestion-branch fog (map #3, "Not yet specified"); this
  ADR fixes only the *model* it must implement.
- **Confidence-flag mechanics already fixed.** The feature/soften/drop Fork for a flagged claim
  lives in `0002` (#7); this ADR only settles what raises the flag (a deliberate hand-set doubt,
  not provenance).
