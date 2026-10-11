# The page is read back against the posting, and the read changes nothing

**Status:** accepted

## Context

`srbhr/Resume-Matcher` (28.1k★) computes this on every run, in its normal test suite, deterministic
and LLM-free:

```python
def jd_keywords_present(tailored: dict, keywords: list[str]) -> float:
    """Fraction (0.0–1.0) of ``keywords`` that appear in the tailored resume."""
    haystack = flatten_resume_text(tailored)
    hits = sum(1 for kw in keywords if kw and kw.lower() in haystack)
    return hits / len(keywords)
```

We compute nothing of the kind. §7's Gap report answers *"what did the posting ask for that the
**bank** could not answer"* — and answers it well; `runs/auxo-ai/gaps.md` is the better half of that
run's output. It does not answer *"what did the posting ask for that the bank **can** answer and the
**page** did not say"*, except through the *you have it, the page did not* class, which today is fed
by hand, from memory.

**And by hand, from memory, it mostly does not fire.** Across the three committed runs:

```
runs/auxo-ai/gaps.md        Nothing in the bank · Too shallow to claim it
runs/mckinsey-shape/gaps.md Nothing in the bank · Too shallow to claim it
runs/zs-btsa/gaps.md        Nothing in the bank · Too shallow to claim it · You have it, the page did not
```

Two of three have no lines in that class at all. The one that does has three, and every one of them
is a Claim that **lost the page to a cap** — *"covers it cleanly at 0.85 and lost to the three-bullet
cap behind three 1.00s"*. Not one is the other shape: a Claim that **placed**, whose composed
sentence simply did not carry the thing the posting asked about. That shape is invisible from
`allocation.md`, which knows nothing about the sentence, and it is invisible from memory, because by
the time §7 is written the sentence has been read a dozen times and reads fine.

### What a count finds on the page that already exists

Extracting `runs/auxo-ai/jd.md`'s terms by hand — 19 of them, verbatim — and counting them against
that run's own `bullets.md`, `scores.md` and `allocation.md`:

```
Answered by the bank, absent from the page (4/19)
  data analysis         placed: american-express/c7
  data pre-processing   placed: american-express/c1, american-express/c4
  predictive modelling  placed: sweatpact/c4
  cross-cloud           placed: american-express/c4
```

Three of those four are real and were not in `gaps.md`. `american-express/c7` scored 0.70 on
*"Multi-source data analysis and automation at real scope, adjacent to the data-analysis
must-have"*, took a Bullet slot, and composed as *"Owned ~60 of a new diagnostics scorecard's KPIs,
automating the heaviest to halve its refresh"* — a good line that never says *analysis*.
`predictive modelling` points at `sweatpact/c4`, which is exactly the claim §7 wrote its *too
shallow* line about, arrived at independently.

The fourth is the counter-example and it is worth more than the three. `cross-cloud` comes back
*answered* because `american-express/c4`'s reason reads *"close to the cross-cloud essential but
**one warehouse rather than cross-cloud** solution work"* — the reason names the requirement while
denying it, and a substring count cannot tell those apart. `gaps.md` classifies cross-cloud as
*nothing in the bank*, and `gaps.md` is right. **The count produces leads, not findings**, and any
design that forgets this turns a diagnostic into a page edit.

## Decision

### 1. The posting's terms are lifted verbatim into `runs/<slug>/terms.md`, at §2

Written at scoring time, before any composition:

```markdown
# Terms: auxo-ai

## Must-have
- TensorFlow
- PyTorch
- feature engineering
- model training

## Nice-to-have
- Streamlit
- BigQuery
```

**An extraction, never a paraphrase** — `0009`'s *lift, never manufacture*, applied to the posting
instead of to the source. If it had to be rewritten it is not a term.

**Nothing scores against it.** §2's *"Score against the full JD text, never a theme list you
distilled first"* is untouched and this file is not that list: nothing reads it until §6.5, after
`bullets.md` is final.

**It is written before composing for one reason.** Extracted afterwards, it would be a list of what
the page happens to say, and the read would be the page marking its own homework. Written first, it
is also the first artifact in the run folder that makes the Fit scoring's *input* reviewable, which
is a thing `0010` would have liked to have.

The Must-have / Nice-to-have split is for the person: it says what they do about a gap, which is
§7's judgement. `coverage.py` does not read the headings.

### 2. The read runs after the page is final, and cannot reach a sentence

`0027` §3 forbids **the posting supplying a word to a sentence**; `0027` §4 forbids **the posting
filtering a sentence's interior**. Neither forbids counting, after the fact, which of the posting's
terms the page happens to answer — and telling the maker, who is not a lint and does not have to
obey it.

That is enforced by where it sits rather than by intention: a new **§6.5**, after §5.05's cold read,
after §5.1's merge verifier, after §6's render. By the time it runs there is no composition left to
influence. **`render.py` neither calls it nor reads its output**, and `tools/coverage.py` writes no
file, so there is no path by which a term reaches a Bullet. A proposal to feed it back is out of
scope by construction.

The posture is `liangdabiao/resume-matcher-agent-cn`'s HR critic — a read of the page from the
screener's side, run *after* composition, that reports and never edits. §7 already does that for the
bank; nothing did it for the page.

### 3. It is a count, and the middle list is sourced from `scores.md`, never from the bank

**Matching is case-insensitive substring**, the naive version deliberately: anything cleverer starts
making claims about synonymy, and synonymy is a judgement. This is what keeps the read on the right
side of `0010`'s refusal of a second reading of the prose — it cannot say *looks fine*, it fires a
list or an empty one, which is `0030` §2's species exactly.

Three lists, partitioning `terms.md` in order:

- **Covered on the page** — matched anywhere in `render.page_prose`'s surface: Bullets, lead lines
  and Skills rows, each carrying the citation it came from. The Skills rows are in it because a
  Nice-to-have surviving on a cheap row rather than in a sentence is `0020`'s whole design and must
  not be reported as a gap.
- **Answered by the bank, absent from the page** — matched in **`scores.md`'s `reason` column**,
  annotated `placed:` or `lost the page:` off `allocation.md`.
- **Answered nowhere.**

The middle list's source is the decision, and it is not the bank. `coverage.py` **does not read
`bank/`** — everything it reads is in the run folder, which is what keeps a replay reproducible
(**Material determinism**) and keeps the tool on the arithmetic side of the seam. What it reads
instead is the one line per Claim that §2 already requires to be written *"in the JD's own terms —
name the requirement it hits or misses"*. That is the only place in the run folder where a term of
the posting is already attached to a claim id, and it exists because `0006` made every score carry a
reviewable reason.

The `placed:` / `lost the page:` split is the actionable part and it is arithmetic: a claim that
**placed** with the term absent from its sentence is a composition call the maker may want back; a
claim that **lost the page** is `0009`'s *you have it, the page did not* with nothing to fix in the
bank.

### 4. It prints, never gates, and no ratio reaches `gaps.md`

`tools/coverage.py` **exits 0 whatever it finds**, including on a run folder with no `terms.md` — an
old run must still get an answer — and on a `bullets.md` it cannot parse. Every failure prints one
line saying what it could not read. `lengths.py` set this precedent: *"It is a measuring tape, exits
0 regardless."*

Each heading carries its count — `Covered on the page (3/19)` — and **`0025` §7's rule applies**: a
signal is only readable if its absence never has to be interpreted, so the zero lists print too.

Those counts are **not** the coverage ratio §7 and `0010` refuse. *"7 of 11 must-haves"* is refused
because it *"measures the maker against the job market and flattens a list that says strictly
more"*; these are the sizes of the parts of a partition of one run's own extraction, they grade
nobody, and the denominator changes with every posting so there is nothing to compare across runs.
The refusal survives where it was aimed: **no count reaches `gaps.md`**, which stays a list.

### 5. A term under three characters is refused as a measurement rather than answered wrongly

`R` is a real Qualification on `runs/auxo-ai`'s posting — *"Python, R etc."* — and a substring count
reports it covered thirty times over, once for every line of the page. `Go` is inside `Google`.

So there is a fourth heading, `Too short to count`, and the terms under it are counted in no other
list. It is arithmetic and not a judgement about what the term means, it does not drop the term, and
the four lists still add up to `terms.md`. The maker reads that one off the page themselves.

This is the one place the *naive version is the right one* rule is qualified, and the qualification
is not about synonymy: it is about a substring being inside half the page.

## Rejected

**`injectable_keywords`.** Resume-Matcher's ATS card renders the JD terms the résumé is missing as
chips for the user to insert. That is `0027` §3 with a UI, and it is the exact move this ADR spends
its §2 fencing off. The same information lands here as a **gap in the bank**, not as a hole to fill
in the page.

**Feeding the read back into composition** — re-composing a Bullet because a term did not land, or
scoring the page against `terms.md`. `0027` §4's argument is unchanged: filtering the sentence's
interior by the JD a second time leaves only the part the posting already knew. §2's placement is
what makes this refusal structural rather than a promise.

**Anything cleverer than substring** — stemming, synonym sets, embeddings, an LLM read. `0010`
refused a second judgement of prose on the record and gave prose *"no mechanism in v1"*; §5.05's
cold read is the mechanism it has. A count is not a judgement; the moment matching decides that
*model selection* answers *model training*, it is one, and it is one made by the same model that
composed the line.

**Reading the bank for the middle list.** It would catch the terms a Claim's Evidence carries and
its reason never names, which is a real class this misses. Refused: it puts the bank inside a
per-run diagnostic, and it would need the full 32-claim Evidence corpus scanned by substring, where
the false-positive rate the `cross-cloud` case demonstrates gets much worse over prose that was
never written to name requirements.

**Failing the run on a term nothing answers.** That is a gate on the posting's vocabulary, i.e.
`0027` §3 arriving through the build. And it would fail every honest run: `runs/auxo-ai` answers
nothing at all on eleven of nineteen terms, and `gaps.md` says so at length. **The gap is the
output, not the error.**

**A coverage number in `gaps.md`, or a trend across runs.** §7's *no score, no grade* and `0010`'s
argument for it, unchanged. A number in a committed file is compared to last time's, and what that
produces is the completeness score `0009` refused, arrived at sideways.

## The cost, stated rather than waved past

**Substring matching is wrong in both directions, and the ADR is arguing from a case where it was.**
`cross-cloud` came back *answered by the bank* off a reason that says the bank does **not** answer
it, on the very run this is written from. The other direction is worse because it is silent: a term
the page answers in the maker's own words — *model selection* against *model training* — lands in
*Answered nowhere* and looks like a hole. **The claim ref beside every line is the mitigation, and
it is a mitigation and not a fix**: every line is a lead to check, and a maker who copies the middle
list into `gaps.md` unchecked has written a worse gap report than the one they wrote from memory.

**`terms.md` is a hand extraction with nothing checking it.** Whatever is left out is invisible to
this read forever, and the failure mode is the quiet one — a thin `terms.md` produces a clean-looking
report. Nothing measures the extraction, and nothing can: the only available check would be a second
model reading `jd.md`, which is `0010`'s reviewer. The file is committed with the run, so at least
the omission is on the record.

**One more artifact in the run folder, and one more thing to keep in step.** `terms.md` joins
`jd.md`, `scores.md`, `allocation.md`, `checkpoint.md`, `bullets.md`, `gaps.md`, `resume.tex`,
`resume.pdf` and sometimes `context.md`. It is the first one written for a tool that runs at the very
end, so it is also the easiest to forget: §6.5 says so and skips cleanly rather than failing, which
is right for an advisory pass and does mean a forgotten `terms.md` costs nothing and is noticed by
nobody.

**Three characters is a placed number, not a measured one.** It excludes `Go`, `R`, `C` and `ML` —
real must-haves on real postings — from the count entirely. The alternative was a word-boundary
match, which is a small step onto the road §3 refuses to walk, and the honest version of a threshold
is to say out loud which terms it declined to answer. It does.

**§6.5 lands between the render and the Gap report, and both of those are the maker's attention.**
`0010` cut the Checkpoint tight on purpose — *"it would train the eye to skim the block"* — and this
adds a second block of lists to a run that already ends with two. It is one command with four short
lists and it exists to make §7 shorter and better sourced, but the interaction is real.

## Consequences

- **`tools/coverage.py`** is new: deterministic, stdlib plus the Renderer's own parse, no LLM, no
  network, no bank access, exits 0 always. It borrows `render.parse_bullets`,
  `render.parse_allocation` and `pack.parse_scores` rather than re-deriving them, for the reason
  `lengths.py` borrows `row_lines`.
- **`tests/test_coverage.py`** covers the four-way split, each of the three prose surfaces, the
  page-before-reasons precedence, the counts adding up, the short-term guard, and that every failure
  path still exits 0.
- **`.claude/skills/tailor/SKILL.md`**: §2 gains *The posting's terms*; a new §6.5 sits between
  `## 6. Render` and `## 7. The Gap report`; §7's *you have it, the page did not* class names §6.5 as
  where it starts; §7's *no score, no grade* gains the sentence keeping the counts out of `gaps.md`;
  §8's commit list gains `terms.md`; the spine diagram gains both.
- **`tools/render.py` is untouched**, and that is the load-bearing part of §2.
- **`CONTEXT.md`**: **Coverage / Coverage gap** gains the read, and **Gap classes**' third class
  gains its source.
- **No page line is spent and no constant moves.**
- **Old run folders keep working.** No `terms.md` is not an error, and `render.py` never knew about
  any of this.
