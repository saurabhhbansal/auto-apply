# The X-ray runs before the page is written

**Status:** accepted

## Context

The maker brought in an external skill whose second stage parses a résumé the way ATS
platforms do and reports a match score, the keywords the candidate is invisible
without, and the red flags a recruiter catches in ten seconds. He first placed it
after `render.py` with a recompose loop, then moved it:

> *"I think the XRAY part of stage 2 could be brought earlier and directly integrated
> into this rather than being treated as a review."*

That is the right instinct and it resolves a problem the post-render placement had.
`0041` decided that reading the page back against the posting **changes nothing**,
precisely because a report that can reach a sentence turns into the page marking its
own homework. A post-render X-ray with a recompose loop is that failure by
construction: the score is computed from the prose, and the prose is then rewritten to
move the score.

**Run early, the same report is a different object.** Before composition there is no
prose to grade — only the evidence that just won the page. So the question it answers
is not *did the page say the right words* but **of the evidence that placed, how much
of the posting can it be made to carry?** That is a question about the bank, it is
answerable at exactly one moment, and acting on it is composition doing its job rather
than a page being tuned.

### Two vendor findings that decide the shape

`docs/research/bullet-frameworks.md` went looking for documented ATS behaviour and
found a negative result: **Workday and Greenhouse both document parse tolerance only** —
images, columns, tables, file size — and **neither documents anything about scoring or
keyword weighting.** So:

- **there is no per-platform score to reproduce.** Five numbers would be one
  computation wearing five hats, and each would be labelled with a vendor's name it
  had no right to.
- **the parse-simulation half has nothing to find.** This template is single-column,
  no graphics, plain headings, and already satisfies every documented requirement, so
  a parse check would pass on every run and report nothing. It is not built.

## Decision

### 1. `tools/xray.py` runs at `tailor` §3.4 and scores the evidence

After the Packer's second pass, before a Bullet is composed. It reads `terms.md`,
`allocation.md`, and — for every **placed** unit — the cited Claims' **Assertion,
Evidence and `skills:` line**. It never reads `bullets.md`, which does not exist yet.

**Scoring the evidence rather than the prose is the whole safety property.** A report
that scores prose can be satisfied by editing prose. A report that scores the bank
cannot: the only way to move it is to have different evidence, which is `ingest`'s job
and cannot be done by writing a better sentence. There is a test that pins this — a
`bullets.md` stuffed with a missing term does not move the verdict.

It reads only **placed** units. A claim that lost the page cannot put a term on it, and
crediting one would make the score describe the bank rather than the page, which is
`gaps.md`'s question and a different one.

Matching is `coverage.py`'s: case-insensitive substring, above `MIN_TERM_CHARS`. One
matcher, not two, and it is deliberately naive — anything cleverer starts making claims
about synonymy, and synonymy is a judgement.

### 2. One score, ours, with the arithmetic printed

| | |
|---|---|
| must-have terms answered | **70** points, pro rata |
| nice-to-have answered | **20** points, pro rata |
| structure | **10** points, less **5** per red flag, floored at 0 |

```
Coverage: 71/100
  must-have terms answered   8/12  (47 of 70)
  nice-to-have answered      3/6   (10 of 20)
  red flags                  2      (-10 of 10)
```

The weights live here rather than in a docstring because they are a **judgement about
what matters on a résumé**, not a measurement of anything. A must-have is worth three
and a half times a nice-to-have because a posting that names an essential and does not
get it is a screen-out and a missed nicety is not. Structure is worth a tenth because
two red flags should sting and should never outweigh answering the job.

**A section with no terms scores full rather than zero.** A posting with no Must-have
list would otherwise cap every run at 30 while saying nothing about the page; a thin
posting is the flimsy-JD check's business (`tailor` §1), not the score's.

### 3. The red flags are computed, never judged

Only facts readable off the bank and the allocation, each checkable in one look:

- **an employment gap** of `GAP_MONTHS` (6) or more between consecutively placed
  **jobs**. Projects are not employment and a break between two of them is not a hole
  in a history, so they are not read.
- **a placed entry with no lead line** — its Bullets meet the reader under a bare
  heading, which `0032` calls the largest quality hole a page can carry, surfaced while
  `ingest`'s closing move can still fix it.

Nothing here reads prose, because there is none. Nothing here is a matter of taste.

### 4. What it may and may not do to a sentence

**`0050` §1 is the licence and the limit.** A term the X-ray calls *answered* is one
some placed Claim's Evidence carries, so writing the posting's word for it is the
renaming `0050` licenses. A term it calls **missing is never a licence to write it
anyway** — that is a `gaps.md` line, and putting it on the page because a report named
it is precisely how this decision goes wrong.

**`0027` §4 is untouched.** The posting still does not decide which things a sentence
mentions. The X-ray says which of the maker's own facts are worth surfacing; it does
not filter the sentence's interior.

### 5. `0041` and `gaps.md` are untouched

`coverage.py` still runs after `render.py`, still reads the composed page, and still
changes nothing. The two are different questions asked at different moments — *what
can this evidence carry* before, *what did the page actually say* after — and the
post-render one keeps its no-feedback rule for the reason `0041` gave.

**No number from here reaches `gaps.md`.** §7's *no score, no grade, no coverage ratio*
stands: a ratio there measures the maker against the job market, and this measures one
run's own extraction against one posting.

## Consequences

- **The score under-reports by construction, and that is the honest reading of it.**
  It matches the posting's words against the maker's raw Evidence, and `0050` exists
  precisely because those differ — a bank saying *"a copilot over four data sources"*
  scores nothing against a posting saying *"AI-driven business copilots"*. On
  `runs/auxo-ai` the first reading came back **11/100** for exactly this reason.
  **The number is a floor, not a measure**, and a low one means *the bank does not
  spell the posting's words*, which is the input to renaming rather than a verdict
  that the page cannot cover the job.
- **The *Invisible without* list is the actionable output, not the score.** It is the
  list to consider renaming toward where the bank supports it, and to write as gaps
  where it does not.
- **The parse-simulation half of the external skill is not built**, and §Context says
  why: no vendor documents a constraint this template does not already satisfy.
- **`xray.py` joins the bank readers.** `pack.py` stays bank-blind and nothing it
  imports reaches the X-ray.
