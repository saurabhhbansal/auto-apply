# Output quality evaluation: lints guarantee truth, the maker reviews what lost

**Status:** accepted

## Context

There is no ground truth for a tailored résumé. Nothing can be diffed against a correct answer,
and the only real-world signal — an interview invitation — arrives weeks later, once, against a
sample size of one, confounded by everything else in the application. The ticket (#14) asked what
stands in for quality when nothing can score it.

The ticket predates `0006`, `0007` and `0008`, and most of what it listed as open is now closed
by machinery already decided:

- **Traceability** — every Bullet is composed from exactly one Claim and cites its id (`0007`);
  the **Number-trace check** verifies every rendered number against that claim with
  equal-or-softer provenance (`0003`). A bullet that "cannot cite an entry" is not a defect the
  system can produce.
- **One-page fit** — the bullet-length lint runs pre-compile, the page-count assert post-compile
  (`0007`); both hard-fail.
- **No silent qual→quant upgrade** — **downgrade-only**, enforced by the same trace check
  (`0003`).
- **The gap report** — `runs/<jd-slug>/gaps.md` already exists (`0001`), and `0009` has since
  classified every line in it.

The ticket also asked what a **red flag** is and what happens when one is found. For all of the
above the answer was already fixed: the run **hard-fails and names the offender**.

So what this ADR is actually left with is the one thing no lint can reach: **was the selection
right, and is the prose any good.** A run can pass every check and still be a bad résumé.

## Decision

### The target is selection, not prose

Of the two ways output can be bad, only one is worth building for:

| | how it fails | visible? |
| --- | --- | --- |
| **selection** | the wrong evidence won the page | **no** |
| **prose** | the right evidence, weakly written | yes — it is on the page |

The asymmetry decides it. A weak line can be rewritten; **a claim that was never selected never
gets the chance.** And a weak line is caught for free — the maker reads the PDF every run, and is
the only user — whereas a mis-scored claim is buried in a score table nobody reads line by line
and looks identical to a correct one from the rendered page.

Prose quality gets **no mechanism in v1** (see the last section).

### The invisible failure is the *confident* run

`0002` made the **Checkpoint** conditional: a fully-aligned run renders straight through, with no
rubber-stamp. The gate is *load-bearing **and** unadjudicable*.

That leaves a hole precisely where it hurts. A run in which Opus scored everything confidently has
no contested slots, so no Checkpoint fires, so **nothing about the selection is ever put in front
of the maker.** Confidence is not correctness — a wrong score does not feel contested, *because*
Opus was sure. The runs that sail through silently are exactly the runs in which a wrong pick is
most invisible.

With no ground truth, nothing can *tell* the maker the selection is wrong. Only the maker can. So
the question is not what algorithm evaluates this, but **what gets put in front of them, and
when.**

### No automated reviewer

Rejected: a second Opus pass reading `scores.md` against the JD and flagging scores it disagrees
with.

It is the same model, reading the same JD, carrying the same blind spots, asked to disagree with
itself. It will largely ratify its own work and hand back **false confidence**, which is worse
than no check at all — a check that reliably says "looks fine" actively suppresses the suspicion
that would otherwise make the maker look. Genuine independence is not available here, and
simulating it is a liability.

**Refined by `0034` §6, for one case.** A model may check another model's output here under four
conditions, all of which this rejection's target failed: the question is **adjudicable** (entailment
against a fixed passage, not a judgement about relevance), the **context is stripped** (no JD, no
`scores.md` — so the blind spots cannot travel), there is **no pass verdict** (its only output is a
suspicion; a clean run prints nothing, so there is nothing to be reassured by), and its findings are
**put in front of the maker** rather than gating silently. The *selection* question this section was
written about is untouched and remains unadjudicable.

### The omission view: what lost, with the reason it lost

Every run prints, and `allocation.md` records, the things that **did not make the page**:

- every **Bank entry** that did not place — its **Entry score** and its best claim's reason
- every **Claim** that lost a slot inside an entry that *did* place — shrunk away under
  **elastic blocks**, or below the **0.50 bullet floor** — with its score and reason

**Only omissions.** What placed is deliberately excluded: the maker is about to read the PDF, and
that *is* the report on what placed, rendered better than any summary. Restating it would be the
one part of the view that is pure duplication, and it would train the eye to skim the block —
taking the omissions with it. Inclusions are self-revealing; omissions are not, and the view
exists for what the page cannot show.

> **Refined by `0037` §4, in this clause only.** *Inclusions are self-revealing* fails for a
> **merged** Bullet: a line fusing three claims reads exactly as well as one that wrongly fused the
> entry's two strongest, and nothing on the page distinguishes them. So the view shows omissions
> **plus the one class of inclusion that is not self-revealing** — every merge, with the reason it
> was made, carried across verbatim like every other reason here. The rest of this section stands:
> what placed is still excluded, and the structural cut still never consults the score.

**The reason is the reviewable part, not the score.** `0.42` cannot be judged by eye — there is no
calibration for whether 0.42 was right. `0.42 — "Kafka here was ops-only; the JD wants
stream-processing design"` can be judged in about a second, because it turns the question into a
claim about the maker's own history, which they are the world expert on. This is why `0006`
required every score to carry a one-line reason; this decision puts those reasons where they will
actually be read.

### The cut is structural, never score-based

The full omission set is most of the bank, so it needs a cut. It is **one line per non-placing
Entry, and one line per lost Claim inside a placed Entry** — no threshold, no top-N, no band
around the cut line.

A score band or a top-N would be **circular**. The object of the search is a claim whose *score is
wrong*; both of those cut the list *using that score*. The more badly something was mis-scored, the
more certainly it is filtered out of the view built to catch it — a claim that deserved 0.9 and got
0.15 sits nowhere near the cut line and nowhere near the top five. It is the worst failure in the
run and the only one guaranteed invisible. The structural cut never consults the suspect number:
an entry appears because it exists and lost.

The cost is length, and it is accepted. The view scales with the **bank**, not the JD, so it is
roughly the same size every run — the maker learns its shape and the eye goes to the anomaly. And
a whole *job* wrongly scored off the page is the worst form of the failure this ADR targets; the
structural cut is the only option under which that can never be hidden. If it proves unreadable
against a real bank, it is trimmed then, on evidence — starting complete and trimming beats
starting trimmed and never learning what the cut concealed.

### It prints and proceeds; it never blocks

The view appears on every run and **stops nothing**. Only a **Fork** ever blocks.

A gate approved every time stops being a gate. If nine runs in ten are fine, the tenth is waved
through with the same reflex keystroke as the other nine — the check decays into exactly the
rubber-stamp `0002` refused to build, and it decays *silently* while still looking like a
safeguard.

Blocking also buys nothing, because being late costs nothing. `0002`'s own backstop applies: the
PDF is regenerable, the run folder overwrites in place, and `git diff` shows what changed. Reading
the view while pdfLaTeX runs and thinking *"why did the consulting gig beat the platform work?"*
costs a re-run, not a lost application.

**This refines `0002`.** The Checkpoint becomes **always present, conditionally blocking**: its
spine — the **Angle statement** plus this view — surfaces on every run, while **Forks** remain
conditional and remain the only thing that halts. What `0002` made conditional was never really
*seeing*; it was *being asked*. Notifications inform, Forks gate, and "no rubber-stamp" is
preserved because nothing ever waits on an approval.

### The bank is the only repair surface

When the maker disagrees with an omission, the fix is **a bank edit and a re-run**. `scores.md` is
**never hand-edited**.

The tempting escape hatch — override the score, re-run the **Packer** — was rejected. Both causes
of a disagreement route to the bank anyway:

- the reason **misreads a well-written claim** → making that claim read more clearly is a bank
  edit, and it helps every future JD rather than this one run;
- the reason **fairly describes what is written**, and the claim only looks weak because its
  `evidence` is thin → this is `0009`'s **shallow claim**, and deepening it is the fix.

Two properties follow, and they are the reason for the strictness. `scores.md` stays a clean record
of what Opus judged, so a diff between runs always means *the bank or the JD changed* — never
*someone patched it*. And **every disagreement compounds**: with no per-run patch available, the
system can only improve across runs, through the bank. An override would have let the same claim
lose on every future JD while each individual run looked fine.

The repair is not slow. `0008`'s **add** path and `0009`'s shallow-gap answer already provide the
mid-flow bank edit, and it lands marked `needs-interview: yes`.

**What this evaluates is the bank, not the run.** A run's own correctness is covered by hard-fail
lints; the omission view exists to show where the bank is under-excavated.

### Diff within a slug, never against a golden résumé

The ticket's third shape — "a diff against a prior good resume" — splits, and only half survives.

**Rejected: a golden reference.** Keeping the maker's best hand-made résumé and scoring runs by
their distance from it is the most tempting idea in the ticket, because it is the closest thing to
ground truth available. It is a trap for a specific reason: **that résumé was tailored to a
different JD.** Its selections encode that posting's priorities. Rewarding proximity to it rewards
reproducing old framing and punishes the per-JD re-angling this system exists to perform — a
machine built to regress toward the last résumé.

**Kept: the same-slug re-run diff.** Runs are committed to git and `0007` had the maker choose the
slug *specifically* so a re-run overwrites in place and `git diff` works. This is not an eval
criterion; it is the **verification half of the repair loop** — fix the bank, re-run, and the diff
answers "did that change the selection, and only where I expected?" Without it a bank fix is a shot
in the dark. A diff across *different* JDs carries no signal at all: two postings should produce
different résumés.

### No external ATS scoring

Rejected: sending the rendered PDF to a third-party ATS scorer (the thread `0007` left open when it
ruled Rezi out of scope).

`0007` fixed **fully offline, no network in a run**, and chose TinyTeX partly to hold it; an ATS
scorer is a network call plus an account, mid-pipeline, on every run. More decisively, it does not
measure the target: an ATS score measures **parseability**, and would happily rate a
perfectly-parseable résumé built from the wrong three jobs. It is also optimisable in the worst
direction — chasing it drifts toward keyword stuffing, colliding head-on with zero fabrication.

The genuine ATS risk was already handled structurally: `0007` chose LaTeX in the Jake's Resume
lineage **on ATS-safety grounds** and locked single-column for the same reason. That is a property
of the **Template**, established once — re-measuring a fixed template every run pays a recurring
cost for a constant. If it is ever wanted, its honest form is a one-off check when the template
changes, the same shape as `0007`'s calibration procedure.

### Nothing is scored

No quality number is emitted. A run's only verdicts are the hard-fail lints; `gaps.md` is a
classified list; the omission view is a list. Nothing gets a grade, because nothing grounds a
grade, and an ungrounded grade is worse than none.

Specifically rejected: a **coverage ratio** ("7 of 11 must-haves evidenced"), which is nearly free
since `gaps.md` already knows both numbers.

It measures the wrong thing — not résumé quality but **fit between the maker and the job**. A run
covering 4 of 11 can be an excellent résumé; the bank simply does not hold what that posting wants,
and no selection could fix it. Reporting that as a quality signal attributes a mismatch to the
system.

And the list already contains everything the ratio would, plus what the ratio destroys. Missing
*Kubernetes* and missing *ten years of experience* are entirely different situations — one is
coverable from a project, the other is immovable — and a ratio flattens them into one digit, which
is then read *instead of* the list that actually drives the decision. This is the **"so what?"
test** (`0003`) applied to the system's own reporting: a number that reads as rigour, drives no
decision the list does not drive better, and invites being optimised. `0009` reached the same
conclusion independently for the bank ("no completeness score, no done") — arithmetic is reserved
for what is genuinely countable.

### Prose quality: no mechanism in v1

The maker reads the PDF; a limp bullet is caught by eye. Composition is already heavily constrained
— one Claim per Bullet, downgrade-only, entailment-bounded, plain prose, a hard character budget —
so little room remains in which prose can go wrong, and what remains is taste, applied for free by
looking at the page. An evaluator here would hit the same wall as the automated reviewer above.

Noted and deliberately not decided: there is no **composition rubric** — the phrasing counterpart
to `0006`'s **Fit rubric**. If bullets come out generic across many runs, that absence is the
likely cause rather than a missing evaluator. It is not charted, because such a rubric is written
by looking at twenty real bullets one dislikes, which needs a working system and a real bank.
Deciding it on paper now would be guessing. It is a build-time residual, like `0007`'s constants.

## Considered options (rejected)

- **An automated reviewer** — a second Opus pass disagreeing with `scores.md`: rejected as
  self-critique with no independence, whose false confidence is worse than no check.
- **A score band or top-N cut** on the omission view — rejected as circular: it filters using the
  number under suspicion, hiding the worst mis-scores most reliably.
- **Showing what placed** alongside what lost — rejected as duplication of the PDF that dilutes the
  part only the view can supply.
- **Blocking on the view** — rejected: a gate approved every time decays into a rubber-stamp, and
  being late costs one re-run.
- **Hand-editing `scores.md` as a stopgap** (with a marked override) — rejected: it adulterates the
  audit trail and, worse, lets a disagreement resolve without compounding, so the same claim loses
  on every future JD while each run looks fine.
- **A golden reference résumé** — rejected: it encodes a different JD's priorities and would reward
  regression toward past framing.
- **External ATS scoring** — rejected: breaks `0007`'s offline property, measures parseability
  rather than selection, and is optimisable toward keyword stuffing.
- **A coverage ratio in `gaps.md`** — rejected: measures maker-to-job fit rather than quality, and
  flattens a list that is strictly more informative.
- **A separate `runs/<jd-slug>/review.md`** — rejected as a derived mirror of `scores.md` +
  `allocation.md`, the thing `0005` and `0006` both ban.
- **Outcome tracking** (recording which applications got interviews) — not taken: the only true
  ground truth available, but delayed by weeks, sample size one per application, and confounded by
  everything else in the application. It cannot close a loop at the granularity of a claim score.

## Consequences

- **Refines `0002`.** The Checkpoint is **always present, conditionally blocking**: the **Angle
  statement** and the omission view surface on every run; **Forks** remain conditional and remain
  the only thing that halts. "Conditional" applied to being *asked*, not to being *shown*.
- **Extends `0006`'s `allocation.md`** with a **"Did not place"** section. The **Packer** computes
  it — deciding who placed, who did not, and what fell under the floor is arithmetic over the
  **Score table**, which is the script's side of **the seam**. It carries each loser's reason
  across verbatim and never writes a reason of its own; Opus only prints it.
- **`scores.md` becomes immutable to the maker.** It is Opus's output and nothing else, which is
  what makes a cross-run diff interpretable.
- **Cross-checks `0009`'s gap classification.** `0009`'s third class ("you have it, the page did
  not") is *requirement-driven* and **trusts the scoring** — it fires only where Opus recognised
  the coverage. The omission view is *bank-driven* and trusts nothing: it lists everything that
  lost, whether or not it was matched to a must-have. This matters because a bad enough mis-score
  makes `0009` **misclassify** — a claim that really does cover Kafka, scored 0.15 for the wrong
  reason, is reported as "nothing in the bank" or "too shallow", sending the maker off to deepen an
  entry that was already fine. The omission view is where that mis-score becomes visible, with the
  reason attached.
- **Feeds the bank, not the run.** A claim the maker knows is strong that keeps losing is not bad
  luck; it is `0009`'s **shallow claim** surfacing through selection. The repair channel is the
  **deepening queue**.
- **`gaps.md` is unaffected.** Uncovered must-haves stay `0009`'s business; the omission view never
  reports them. "The bank has nothing" and "the bank had something and it lost" are different
  questions with different fixes.
- **Build-time residual:** the **composition rubric** is deliberately not charted, to be written
  against real output.
