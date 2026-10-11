# The composed set is a checked object

**Status:** accepted

## Context

`runs/auxo-ai` at `242dc01` is the second composition of that page — the re-run under `0029`, on a
bank and a JD that did not move, so `scores.md` stood and `allocation.md` re-packed byte-for-byte
identical. Every fault the last three tickets went after is gone from it. Read back as a **page**
rather than as a column of lines, it carries three more, and each of them is invisible in any single
Bullet (#54, #60).

### Fault A — every Bullet is still jammed against the cap

Measured against the width each slot was granted:

```
american-express/c5   99/103   96.1%      xlscout/c4          98/103   95.1%
american-express/c6  197/206   95.6%      auto-apply/c1      192/206   93.2%
american-express/c1  102/103   99.0%      auto-apply/c2       95/103   92.2%
american-express/c4  103/103  100.0%      auto-apply/c7       98/103   95.1%
american-express/c7  102/103   99.0%      auto-apply/c4      100/103   97.1%
american-express/c3   98/103   95.1%      auto-apply/c5      100/103   97.1%
xlscout/c3           102/103   99.0%      sweatpact/c4        99/103   96.1%
xlscout/c1           204/206   99.0%
xlscout/c2            97/103   94.2%      TOTAL  1987/2060 = 96.5%
xlscout/c5           101/103   98.1%
```

**Fourteen one-line Bullets, and the shortest is 95.** Not one lands below 88.

This is `0027`'s fault 2 verbatim — *"all twelve composed Bullets landed at 98–103. Not some of them:
all of them, jammed against the cap"* — and the timing is the finding. The build carrying `0027`
landed at `1925238`; the first page composed under the rewritten rubric was committed 23 minutes
later at `9c1e988` and measured 95.9%. The re-compose under `0029` measured **96.5%**. Two
compositions under the rule that was written to stop this, and the number went the other way.

### Fault B — the openers repeat

Every Bullet's first word, across the page:

```
Automated  Barred  Benchmarked  Built  Built  Drawn  Hand-mapping  Made  Made
Owned  Replaced  Shipped  Split  Turned  Unified  Went  Wrote
```

`Built` twice and `Made` twice in seventeen lines. The `auto-apply` column reads *Built / Split /
Wrote / Barred / Made* — five past-tense verbs stacked, which is the *"reads like a form"* shape
`0027` §2 was written to prevent.

`0027` §2 says to *"look at its neighbours before you settle"*, and both repeats are in **different
entries** — different `## <entry-slug>` sections, composed pages apart. A composer obeying that rule
to the letter still ships them.

### Fault C — two spellings on one page

```
xlscout/c1   …to prove the tool generalised past the manuals…     en-GB
skills row   Data standardization                                 en-US
```

Nothing anywhere states which convention the page uses, so nothing was disobeyed.

### The read: the only rule with teeth is the ceiling

`0027` diagnosed fault A correctly and even named the tell, in `.claude/skills/tailor/SKILL.md`:

> **Write to say the thing, then check the budget. Not the reverse.** If every line in `bullets.md`
> lands within five characters of the cap, that is evidence of a rubric being followed rather than of
> these particular sentences needing that much room.

**Nothing measures it.** `check_lengths` fails only when a Bullet goes **over** `CHARS_PER_BULLET`,
and its own docstring says composing under budget *"does not fail"*. So compose gets a hard failure
in one direction, silence in the other, and prose that reads as advice — and it optimises to the only
number with consequences. Two runs of evidence say the paragraph is not enough on its own.

Faults B and C are the same story with no paragraph at all behind them. And all three are
**properties of the set**: a spread, a repetition, a mixture. No amount of care taken over one Bullet
can catch any of them, because none of them exists in one Bullet.

> **The `0010` conflict, surfaced rather than routed around.** `0010` decided that *"Prose quality
> gets no mechanism in v1"* and rejected an automated reviewer because *"it is the same model,
> reading the same JD, carrying the same blind spots"*.
>
> **That rejection is correct and this does not reopen it.** What `0010` refused was a **second
> judgement** — Opus re-reading the JD and disagreeing with itself, handing back false confidence.
> Every check below is **arithmetic on the composed file**: a character count, a first-word
> comparison, a suffix match. None of them reads the JD, none forms an opinion about whether a line
> is good, and none can say *"looks fine"* — they either fire or they do not.
>
> `0010`'s asymmetry argument — selection is invisible, prose is visible — also holds only for faults
> a reader *sees* in one line. A length distribution is exactly the kind of prose fault that is
> invisible on the page and visible in the file, which is why two people read this page and neither
> counted the characters.

## Decision

### 1. `bullets.md` is one page's prose, and it is checked as one object

Stated first because it is what the three rules have in common and what makes this one ADR rather
than three. **A composed set is not a bag of independently-valid lines.** Some of its faults exist
only at the scale of the page, and a pipeline that only ever looks at one Bullet at a time cannot
see them however carefully it looks.

The three checks below are **the set checks**. They run together, after the length lint, on the same
plain text, before a compile is spent.

### 2. The spread rule — fail a page whose Bullets are indistinguishable in length

On a run of **six or more one-line Bullets**, at least **one in three** must land at or below
`CHARS_PER_BULLET − 15` — 88 at the current calibration. Under six one-line Bullets there is no rule:
a short run has no distribution to speak of.

Against `runs/auxo-ai`: 14 one-line Bullets, so 5 must be at or under 88. Zero are. It fires,
correctly.

**Two-line Bullets do not count**, neither toward the six nor toward the one in three. A two-line
slot was granted because compressing the claim would cost the thing worth saying (`0027` §5), so
filling it is the point rather than the fault. Only one-line Bullets are evidence of writing to the
cap.

**Why a floor on short lines rather than a cap on the mean.** A mean is hit by writing half the page
at 60 and half at 103, which is not what is being asked for. The thing wanted is *some of these
sentences finished early*, and that is a count of sentences, not an average of them.

**Both constants are the maker's judgement, not a measurement**, and are labelled that way wherever
they are written down — the same label `\hfuzz=2pt` carries in the Template (*"a judgement about what
a reader can see, not a measurement"*) and `MAX_ROW_LINES` carries in `pack.py`. Nothing measured
this. `0027` said *"a line that finishes in 66 characters has not failed for being short"*; 88 is a
far weaker demand than 66, and one in three is a far weaker demand than most.

### 3. No opening word twice on one page

Case-insensitive, the first whitespace-delimited token of the Bullet's prose, across **all** Bullets
in `bullets.md` — not per entry, which is the gap fault B fell through. Both repeats on that page are
in different `## <entry-slug>` sections.

A hyphenated opener is **one token, matched whole**. *Hand-mapping* and *Hand-rolling* are different
openings to a reader, and splitting them would make the check fire on a distinction it cannot see.

**Skills row labels are not openers.** A row label is a noun lifted from the posting's own vocabulary
under `0020`, chosen from a different set of rules, and has no opener problem.

The failure names both refs. The fix is one rephrase — and `0027` §2 already forbids the lazy way
out: *"charging every sentence into a house verb is the same error in the other direction"*.

### 4. One spelling convention per page

`-ise/-ize`, `-isation/-ization`, `-yse/-yze`. If both spellings appear anywhere in `bullets.md` —
Bullets or Skills rows — the run fails and names the two words.

**Which variant is correct is not the check's business.** It fails on the mixture, not on the choice,
so nothing here encodes a house dialect into the renderer. If the maker wants one pinned, that is
`bank/profile.md`'s job and a separate decision.

The check carries **a list of words where those letters are not the suffix** — *comprise*,
*supervised*, *revised*, *exercise*, *capsize* and their kind — because résumé prose is full of them
and a check that failed a page for writing *"supervised"* beside *"standardization"* would be worse
than no check. The list is the one soft edge in this ADR, and it is stated as such under the cost
below.

### 5. `render.py` fails the run; `lengths.py` reports the distribution

The repo already has a two-tier convention and these slot into it rather than inventing a third
place:

| | |
|---|---|
| `tools/render.py` | **fails the run**, on the first offender, naming it. All three checks live here |
| `tools/lengths.py` | **reports a finding and exits 0.** §2 goes here *as well* |

The spread is the one that also belongs in `lengths.py`, because it is the one you need to see
*while composing*. `lengths.py`'s docstring is explicit that it *"names all of them at once"* where
`render.py` fails on the first, and a spread finding is a page to rewrite rather than a line: the
maker wants the distribution in front of them before the file is finished, not a refusal afterwards.
§3 and §4 need no second home — each is a one-line fix, and `render.py` names it before a compile is
spent, so nothing is wasted by hearing it there.

### 6. The constants live with the check that spends them

`tools/config.py`'s docstring is a contract — **MEASURED, NEVER ESTIMATED**, from the procedure in
`docs/calibration.md` — and these three numbers are neither measured nor measurable. They do not go
in it, not even below the block under their own heading: a file whose whole discipline is *everything
here came off a compiled page* is weakened by a second kind of number living in it, however well
labelled.

They go in `render.py`, beside the checks that spend them, which is where `pack.py` already keeps
`MAX_ROW_LINES` (*"the maker's judgement, which no measurement can check"*) and `EDUCATION_ROWS`.
`lengths.py` imports `render` already, for exactly the reason that applies here: a second copy that
drifted would measure against a rule the run does not enforce.

## The cost, stated rather than waved past

**The spread rule can be satisfied by writing badly.** Nothing in it distinguishes a sentence that
finished early from one that was cut short, and `0027` §1 is emphatic that the second is the failure
this whole rubric exists to prevent. The check counts characters; only a reader can tell which kind
of short line it got. So the rule is written to be **weak on purpose** — one in three, and 15
characters, when `0027`'s own illustration was 66 — and the re-render is read by eye before this is
called done. If the page comes back worse, the answer is `0027` §1 restated harder in the rubric,
**not a looser threshold**.

**The spelling check has a word list in it, and a word list can be short.** Every other check in
`render.py` is closed arithmetic; this one is a suffix match minus a list of exceptions, and a word
that belongs on the list and is not yet on it fails a legitimate page. Two things make that
affordable: the failure is **loud and immediate** rather than silent, it names the two words, and the
fix is one line in `render.py`; and the list only has to cover the words a résumé actually uses,
which is a much smaller set than the language. It is still the one place in this ADR where the check
can be *wrong* rather than merely *unhelpful*, and it is recorded here rather than discovered later.

**A run can legitimately fail §2 and have nothing to fix.** Six claims that all genuinely need 100
characters is a page this rule refuses. That is the rule working rather than a false positive, and
the fix is the sentences. If it recurs across three real runs, reopen it **with those runs as
evidence** rather than widening the threshold on the strength of one.

## Rejected

**A cap on the mean, or on the total.** Both are hit by writing half the page at 60 and half at 103 —
a shape nobody wants and the rule would have to accept. See §2.

**A minimum spread, or a standard deviation.** Same objection, plus a number no one can read off the
page. *At least a third of these finished early* is a sentence the maker can check by eye against
`lengths.py`; *σ ≥ 8.5* is not.

**Counting two-line Bullets in the spread.** It would make a granted width count against the page
that granted it, and `0025` already has a check for a width nobody used — `lengths.py`'s advisory
`wide slot` line, which is a width-declaration error at scoring time rather than a prose error.

**Per-entry opener uniqueness.** It is what `0027` §2 already asks for in prose and it is exactly
what shipped both repeats: *Built* is in `auto-apply` and `american-express`, *Made* in `auto-apply`
and `sweatpact`. The page is what a reader reads.

**Pinning a dialect.** Tempting, because then the check is a single lookup and there is no mixture
rule at all. Refused: the bank is the maker's own prose and `bank/profile.md` is the maker's file, so
a dialect is theirs to pin, not the renderer's to impose. The mixture is the defect; the choice is
not.

**A raised `CHARS_PER_BULLET`, or shortening the cap to force the spread.** `0025` refused raising it
on the record and `0027` restated the refusal. Lowering it is the same error inverted — it is a
measurement of the Template, and moving it to buy a distribution would make the page budget a lie.

**Making the spread advisory in `render.py` too.** Considered, since it is the one check here that
could be satisfied badly. Refused on the evidence: an advisory paragraph is exactly what `0027`
already wrote at `SKILL.md`, and two composed pages later the number had gone up.

## Consequences

- **`render.py` gains `check_set`** beside `check_lengths`, running the three rules of §2–§4, and the
  Renderer's order of operations gains a step. The three judgement constants live at the top of that
  section, labelled as judgements.
- **`lengths.py` gains a `spread` finding line** in its existing `<kind> <detail>` grammar, printed
  when the rule would fire and silent otherwise, still exiting 0.
- **`SKILL.md`'s *Write to say the thing, then check the budget* paragraph gains the rule that now
  backs it**, and the composition rubric gains §3 and §4 as rubric lines.
- **`tools/config.py` is untouched.** §6 — its contract is what the Header-fit check and
  `docs/calibration.md` both reason from.
- **`CONTEXT.md` gains **Composed set** as a term**, and **Bullet**, **Composed bullets** and
  **Renderer** say the set is checked.
- **The bar on the re-render:** at least 5 of the one-line Bullets at or below 88, no repeated
  opener, one spelling — and then **read the page**. A page that reads worse means the spread rule is
  buying whitespace instead of completeness, and that is a finding for #60 rather than a threshold to
  tune.
- **`0010` stands.** Nothing here evaluates prose. The three things added are a character count, a
  first-word comparison and a suffix match.
