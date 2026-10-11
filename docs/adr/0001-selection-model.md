# Selection model: fit-ranked entry blocks under a one-page budget

**Status:** accepted

## Context

Tailoring must decide which bank evidence goes on a one-page resume for a given JD —
deterministically and with zero fabrication. This is the **anchor** decision the bank
schema (#9), checkpoint (#7), qual/quant (#8), and selection locus (#11) are all designed
backwards from. Resolved in issue #4.

## Decision

- **Unit.** The **Bullet** is the atomic unit of fit and truth, but the **Entry** (a job or
  project) is the *block* that competes for page space. The page holds a bounded number of
  entry slots; more candidates exist than fit, and they compete on Fit. Sections are the
  fixed skeleton (forked "Jake's Resume" `.tex`), not competitors. Bullets per entry are a
  **soft** cap of ~3 — fewer when the evidence doesn't justify more, never padded to a quota.

- **Fit** is judged against the **full JD text** — not a distilled theme-checklist, which
  loses hidden themes only visible when the whole JD meets the whole bank — blending skill
  coverage, semantic relevance, seniority/scope, recency, and domain. Must-haves outweigh
  Nice-to-haves in the competition for expensive Bullet slots, but Nice-to-haves survive on
  cheap real estate (the Skills breadth list): **real estate is tiered**.

- **Budget.** The one-page limit is enforced as **budget-aware pick-best-N over
  predictable-height entry blocks**, not threshold-include-everything. Fixed-size blocks make
  selection largely the page-fit authority (no render-trim loop needed as the primary mechanism).

- **Determinism** is **material**: the same — or a similar-sounding — JD yields the same
  Entries, the same skills, and a similar set of impact claims; wording may drift. Delivered
  by full-JD semantic matching (paraphrase-robust), fixed deterministic tiebreaks, pinned
  relative-time, minimal sampling variance, and treating recorded checkpoint answers as
  first-class inputs.

- **Contested slots** — Coverage gaps, JD ambiguity, Confidence flags — escalate to the
  human checkpoint (they act on the resume's core). Interchangeable close calls (boundary
  ties, recency-vs-relevance) resolve silently by fixed rule.

- **Zero fabrication** is drawn at the **claim level**: every claim traces to bank evidence;
  rewording aligns vocabulary (true synonyms only) and emphasis, but never adds or inflates
  scope, metrics, or tech. The selector never *fakes coverage* — an uncovered Must-have
  becomes a Gap-report entry, not a stretched Bullet. The test: every claim must be
  **defensible in the interview**.

## Considered options (rejected)

- **Bullet-level over-select + render-trim loop** — rejected in favour of packing
  predictable-height entry blocks, which is more deterministic and more predictable to fit.
- **Distil the JD into a theme-checklist before matching** — rejected: lossy, misses hidden
  themes.
- **Byte-identical determinism** — rejected: would force caching rewritten text; material
  determinism is the right, achievable bar.

## Consequences

- Schema (#9), storage (#10), and locus (#11) inherit three requirements: match against the
  full JD *in context* (not a lossy extract); persist each tailoring run as a **diffable
  artifact** (also serves version-control/diff and entry-evolution re-run-and-diff); and
  represent **claim-level provenance** so Confidence flags can be raised.
- Checkpoint design (#7) is built from the three contested-slot kinds.
- Qual/quant (#8) details the Confidence-flag / no-silent-upgrade mechanics under this
  claim-level boundary.
