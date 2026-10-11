# Selection locus: Opus judges, a script packs

**Status:** accepted

## Context

The ticket (#11) framed this as a binary: a **skill reasoning directly over the bank files**
versus a **script that does retrieval/scoring and hands the LLM a shortlist**. Which fails
better?

`0005` had already leaned on one half of that answer — it named "there is no mechanical
selector; Opus reads the whole bank and drafts" as the governing fact that collapsed the
storage choice, and explicitly left #11 to decide the question on its own terms. Taking that
prior at face value would have banked skill-over-files and closed the ticket. Grilling it
instead exposed the thing the binary hides: **the real question is not *who selects* but
*where the seam sits between judgment and arithmetic*.**

Two facts force a seam to exist at all:

- `0001` promised **Material determinism** delivered by "fixed deterministic tiebreaks, pinned
  relative-time, minimal sampling variance." If Opus ranks in its head, a tiebreak is a
  sentence in a `SKILL.md` that the model mostly follows — there is nowhere to *bolt* it.
- `0003` already commits to real code: the **Number-trace check**, a mechanical post-render
  lint that fails the run. Code was never actually banned; it was banned from *judging*.

## Decision

### The seam: code never decides relevance, only what fits

Opus reads the whole bank against the full JD and **scores** it. A small deterministic script
owns everything downstream of the scores: rollup, ordering, tiebreaks, slot allocation, and
page-budget packing. Opus then composes bullets **within the allocation the script handed
back**. Lints close the run.

```
JD ──► [Opus: score every Claim against the full JD, per rubric]
         │ writes runs/<jd-slug>/scores.md
         ▼
       [pack.py: roll up, order, allocate slots, shrink to fit]
         │ writes runs/<jd-slug>/allocation.md
         ▼
       [CHECKPOINT — angle statement + forks]  ──framing flip?──► re-score ──┐
         │                                                                   │
         ▼ ◄─────────────────────────────────────────────────────────────────┘
       [Opus: compose bullets within the allocation]
         ▼
       [lints: page-count assert, Number-trace check] ──► PDF + Gap report
```

### Scoring is Opus's, against a fixed rubric — not against the other claims

Every **Claim** (not Entry) gets a 0–1 float, because `0001` puts Fit on the Bullet/Claim while
the Entry is only the *block* that competes. One scoring pass therefore drives both ordering
and bullet counts.

Scores are assigned against a **fixed written rubric with named anchors**, never relatively
against whatever else is in the run:

| score | meaning |
|-------|---------|
| 1.0 | directly evidences a stated Must-have — same tech, same scope |
| 0.7 | evidences a Must-have adjacently, or a stated Nice-to-have head-on |
| 0.5 | transferable — a reader must make one inferential hop |
| 0.2 | same broad field; nothing the JD asks for |
| 0.0 | unrelated |

Anchoring is load-bearing: an epsilon band and an absolute bullet floor are meaningless if
0.5 means something different on Monday's JD than on Friday's. **Per-run normalization is
rejected** for exactly this reason — it makes a weak-bank run look identical to a strong one
and reduces the floor to noise.

Each score carries a one-line reason, written in the same row.

### Rollup: entry score = mean of its top 3 claim scores

An entry block spends three bullet lines, so it should be ranked on what it can actually put
in them. **Max-claim is rejected**: a one-claim wonder would outrank a broadly-relevant job and
then be allocated three slots it cannot fill well. **Scoring entries and claims separately** is
also rejected — two judgments that can contradict, with no rule for which governs.

### Ordering: strict score order, with an epsilon tie band

Entries are ordered by descending entry score. **Any gap smaller than ε = 0.05 is a tie**,
broken by the fixed rule: **recency descending, then entry-id ascending**.

This is what keeps float scores honest. An LLM float is stable in its first decimal and noisy
in its second; without a band, 0.81 vs 0.79 silently reorders the résumé between runs and the
"fixed deterministic tiebreak" of `0001` is dead code that never fires. With the band, the
float still supplies the *distance* that contested-slot detection needs — which coarse named
tiers could not — while the ordering re-coarsens exactly where it matters, at the cut line.
A gap under ε at the page boundary is precisely `0001`'s "boundary tie, resolved silently by
fixed rule."

### Allocation: an absolute bullet floor, and elastic blocks

- **Slots = `min(3, claims scoring ≥ 0.50)`.** The **0.50 floor** is what makes `0001`'s
  "soft cap of ~3, never padded to a quota" *mechanical* rather than a request the model is
  trusted to honour. A claim below the floor never takes a bullet slot even when slots are free.
- **Blocks are elastic**, not fixed-height: header + 1..3 bullets.
- **The packer walks strict score order and shrinks rather than skips.** When the next entry
  does not fit the remaining lines, it drops that entry's *own* lowest-scoring bullet until it
  does. A higher-scoring entry is never passed over so a weaker one can fit.
- **Shrinking never reaches backwards.** A placed entry never gives up a line to admit a
  weaker entry below it. Depth beats breadth; nothing above pays for something below.

Because the minimum viable block is uniform (header + 1 bullet), *if the next entry cannot fit
at minimum, no entry can* — the page is simply full. **Leapfrogging and backfill therefore stop
existing as concepts**, and with them the whole class of "a .40 entry displaced a .85 entry for
arithmetic reasons" unfairness.

### Sections: one pool, with a floor on Experience

Jobs and projects compete in a **single score-ordered pool**, so the best evidence wins
regardless of type — but the **two most recent jobs always place at ≥ 1 bullet** before the
pool competes for the remainder. A pure single pool is rejected: a projects-heavy JD would
mechanically produce a résumé with an empty Experience section. Hard per-section budgets are
also rejected: they force the split to be guessed in advance, so a weak job consumes space a
strong project earned.

### Phrasing: height is true by construction, not estimated

The packer allocates *before* any bullet text exists, so the height model only holds if
phrasing is **constrained to the allocation** — each bullet must fit one line (≤ N chars).
Opus phrases within that or returns fewer bullets. A post-compile **page-count assert** then
fails the run if it ever overflows.

This preserves `0001`'s rejection of a render-trim loop as the primary mechanism: overflow is
a **lint that fails**, not a loop that retries. *(Phrasing bullets first and packing on measured
text is rejected — it throws away most of a run's phrasing. A compile-measure-repack loop is
rejected as the mechanism `0001` already ruled out.)*

### Artifacts: the score table *is* the Decisions record

Opus writes a **fixed-column markdown table** into `runs/<jd-slug>/`; `pack.py` parses it and
writes its allocation back into the same folder.

```markdown
## Claim scores

| claim     | score | why                             |
|-----------|-------|---------------------------------|
| acme/c1   | 0.91  | payments latency = must-have #1 |
| acme/c2   | 0.84  | postgres depth, named in JD     |
| globex/c1 | 0.93  | k8s oncall, must-have #3        |
| globex/c2 | 0.40  | tangential                      |
```

One artifact, one copy, git-diffable — the interchange format and the audit trail are the same
file. This answers the ticket's "which fails better" question directly: **a bad selection is
debugged by reading a diff.** A script that silently mis-scores and an LLM that silently
hallucinates relevance are equally opaque *until* the reasoning is written down; writing it
down is what makes either recoverable. Every silent call the packer makes — a shrink, a tie
broken by rule — is logged there with its reason, per `0002`'s decided-by-rule-and-logged class.

A separate `scores.json` for the script plus a generated markdown view is **rejected**: it is
two representations of one fact, the derived-copy shape `0005` already rejected for the bank.
An ephemeral temp file is **rejected**: the numbers that drove the cut would not be in git.

### Checkpoint placement: re-score on a framing flip, decide-by-rule after

`0002` fixed the Checkpoint as **one** pre-render round whose Angle statement names the leading
entries — so it sits *after* scoring and packing. The two fork kinds cost differently:

- A **Confidence fork** (feature / soften / drop) frees a line; applying it is a cheap re-pack.
- A **JD framing fork** invalidates every score, since the bank was scored against one reading.

So: score under the default framing → pack → one Checkpoint round. If the framing answer flips,
**re-score and re-pack**. Anything newly surfaced by the re-score — a flagged claim that only
now ranks high enough to matter — is **decided by fixed rule and logged**, never a second round.
The 2× scoring cost is paid only when the human actually flips.

Scoring both framings up front is **rejected**: it always pays 2× on a split, and `0002`
already gave the human a way not to answer blind (Company research offered as a third
response). Resolving framing before scoring is **rejected**: it is two human touch points,
which is what `0002`'s single batched round exists to prevent.

### Form: `tools/pack.py`, stdlib-only, invoked via Bash

One small dependency-free Python file in the repo. Reads the run folder's score table, writes
the allocation back into it. Inspectable, unit-testable, runs offline, and its determinism is
verifiable by reading it. Doing the arithmetic inline in the skill is **rejected** — it hands
the deterministic half back to the same thing that produced the scores, which is exactly what
the split was chosen to avoid.

This gives #16 (does anything warrant an MCP server?) a concrete candidate to judge rather than
a hypothetical.

## Reconciliation with `0005`

This does **not** overturn `0005`'s "there is no mechanical selector." The packer never reads
the bank — it reads a structured table that *Opus* wrote. The bank stays pure prose markdown,
read only by Opus, exactly as `0005` specified. Machine-readable structure appears at the **run
artifact** layer and never at the **storage** layer, so none of `0005`'s reasoning (no derived
index, nothing to rot on hand-edit) is disturbed.

What `0005` got slightly wrong is only its phrasing: there is no mechanical *judge*. There is
very much a mechanical *packer*.

## Consequences

- **`0001`'s "minimal sampling variance" is not achievable.** Headless Claude Code exposes no
  temperature control. The determinism load is carried instead by the fixed rubric (a stable
  scale), the epsilon tie band (noise cannot reorder), the 0.50 floor (bullet counts are not
  discretionary), and the recorded score table (any run is replayable and diffable). This is a
  correction to `0001`, not a gap.
- **Render (#12) owes this decision its constants.** The line budget (page height in lines),
  the header height, and the chars-per-bullet limit cannot be fixed until the forked "Jake's
  Resume" template lands. The *rules* here are complete; the *numbers* are calibrated in #12.
  #12 also owns where the page-count assert runs in the pipeline.
- **ε = 0.05 and floor = 0.50 are the starting values**, chosen to be readable and roughly
  right. They are single-constant knobs in `pack.py`, tuned against real runs; changing them
  changes selection, so a change is a recorded event, not a silent edit.
- **`runs/<jd-slug>/` now has named contents** — `scores.md` (Opus's claim scores + reasons)
  and `allocation.md` (the packer's slots + skip/shrink log). `0005` deferred the run-artifact
  layout to render/checkpoint; this pins the two files selection owns.
- **Ingestion is unaffected.** Nothing here asks the bank to be machine-parseable.

## Considered options (rejected)

- **Pure skill-over-files (the ticket's first horn)** — rejected: leaves `0001`'s fixed
  tiebreaks and page arithmetic as prose the model may drift from, with no artifact to diff.
- **A scoring script feeding a shortlist (the ticket's second horn)** — rejected: it would need
  a machine-parseable bank, reopening the derived-index pressure `0005` closed, and it puts
  semantic relevance — the one thing genuinely unmechanisable here — in code.
- **Coarse named tiers instead of floats** — rejected: tiers cannot express *distance*, which
  contested-slot and boundary-tie detection require.
- **Raw floats with no epsilon band** — rejected: second-decimal drift silently reorders the
  résumé, and the fixed tiebreak never fires.
- **Per-run score normalization** — rejected: destroys the absolute floor and makes a weak run
  indistinguishable from a strong one.
- **Max-claim rollup** and **separate entry-level scoring** — rejected under "Rollup" above.
- **Backfill / leapfrogging at the page boundary** — rejected: elastic blocks make it
  unnecessary, and it would let a weak entry displace a strong one for arithmetic reasons.
- **Shrinking a placed entry to admit a weaker one** — rejected on the same fairness principle.
