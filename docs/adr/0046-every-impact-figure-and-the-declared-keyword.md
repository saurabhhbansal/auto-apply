# Every impact figure carries the emphasis, and a declared keyword may join it

**Status:** accepted

**Extends** `0043-the-number-carries-the-emphasis.md`, which stands except where §1, §2 and §5 are
named below.

## Context

`0043` put the first real emphasis on this page eleven days ago and deliberately spent one lever:
**one bolded span per Bullet, always the figure, never a keyword.** Both limits were argued from the
same worry — that nothing downstream could check a wider rule — and the ADR ended by naming its own
cost and asking that *"the next output review should look at it again"*.

This is that review, and the page it read back is `runs/auxo-ai/resume.tex` as `0043` left it:

```
\resumeItem{Owned $\sim$\resumeEmph{60} of a new diagnostics scorecard's $\sim$150 KPIs, …}
\resumeItem{Automated the merchant-account mapping, newly matching $\sim$41 accounts, plus the
            monthly leadership email and the review deck's data cuts, cutting $\sim$8 hours a month}
```

Two problems, and neither is the one `0043` was worried about.

**The first is that half a claim is emphasised.** `american-express/c7` bolds `~60` and leaves
`~150 KPIs` plain, and `~150` is what makes `~60` mean anything: `0039` put the denominator on that
page precisely to size the work. `american-express/c1+c3+c4` bolds `~41 accounts` and leaves
`~8 hours a month` plain — the outcome, the thing a reader is scanning for, set in body text under a
bolded input. `0043` had a rule for which figure wins (the Claim's stored `number:`, leftmost
otherwise) and the rule is defensible; what it cannot do is stop being a rule about **one** figure
on a line that is making a claim with **two**.

**The second is that the page's technical names are invisible.** `GPT`, `Gemini`, `Qwen`,
`Streamlit`, `Claude Code`, `LLM`, `Apple Health` all appear in Bullets on that page, in body
roman, and a thirty-second read finds none of them. `0043` §2 refused keyword bolding on three
grounds and the three are re-read in *Rejected* below; the short version is that the argument it
actually rests on — *the posting must not choose where the reader's eye lands* — is an argument
about the **posting**, and it does not reach a name the maker's own bank declares.

### What has changed since `0043`, and why the checkability argument is now answerable

`0043`'s *Rejected* refused a composer-marked span with the sentence that governs this whole area:

> *"A marked span can be validated for shape … but not for **judgement**, and whether this phrase is
> the impact is exactly a judgement. … A marker the composer places and no check can assess is a
> lint-shaped hole."*

That still stands, and this ADR does not reopen it — **nothing here is marked in `bullets.md`**.
What it observes is that `0043` drew the boundary in the wrong place. It concluded *"only a figure
can be checked"* from *"only a figure is already mechanically identified"*, and by 2026-08-11 that
second clause is no longer the whole truth. Two other things on this page are mechanically
identified:

- **every figure, not one of them.** `check_number_trace` resolves *each* number in *each* Bullet
  against the cited Claim's stored value at equal-or-softer provenance before the page is filled. It
  never proved one figure; it proved all of them, and `0043` used one.
- **the terms the maker and the posting have written down.** A Claim's `skills:` field is validated
  by `bankcheck.py` and gated onto the page by `check_skills_trace`; `terms.md` is lifted verbatim
  from `jd.md` at `tailor` §2 and is already read back against the page by `coverage.py`. Neither is
  a judgement made at render time. Both are lists a person typed.

And the property that makes all of this safe was already the load-bearing one in `0043` §1, stated
one level more generally: **emphasis cannot introduce content, because it does not choose content.**
It re-typesets a substring that is already on the page. A rule that bolds a word the page does not
say bolds nothing.

## Decision

### 1. Emphasis is still decided at render time, mechanically, from the prose

`bullets.md` does not change. The composer writes plain sentences, the cold read (§5.05) reads plain
sentences, the number trace, the opener, spelling, spread and marker checks all read the same plain
prose they read yesterday. `tools/render.py` derives the spans and `templates/resume.tex.j2` owns
what emphasis looks like. That is `0043` §3 unchanged and `0007`'s rule kept rather than bent.

**The one simplification worth naming: no Claim is read to choose a span.** `0043` needed the
Claim's stored `number:` to decide *which* figure argued the claim. This bolds all of them, so
`emphasis_spans(text, vocabulary, cap)` is a pure function of the prose and two files. A test pins
the signature, because a later change quietly reading the bank back in would be re-introducing a
choice that no longer needs making.

### 2. Every impact figure is bolded, with the noun that gives it meaning

Replaces `0043` §1. `~60` **and** `~150 KPIs`; `~41 accounts` **and** `~8 hours a month`.

The unit extension is `0043`'s, unchanged and still worth its rules: one following alphabetic word,
never a stopword, never across punctuation, plus the `a month` / `per cycle` rate tail. `~150` alone
is a quantity of nothing.

There is **no cap on figures**, and the reason is the shape of the thing being counted: a Bullet is
one Claim (`0027` §6), and a Claim carries two or three figures at the outside. The runaway case
does not exist. Keywords are a different animal and §5 caps them.

### 3. A figure is impact unless it is a date or a version, and both are decided mechanically

The default is bold, and the exclusion list is short, because the alternative — enumerating what
counts as impact — is a judgement wearing a regex. Two exclusions:

- **A year.** A bare four-digit integer in 1900–2099 with **no softening tilde, no unit and no
  thousands separator**. All four conditions have to hold at once, which is what keeps
  `~2,100 lines`, `~2100 lines` and `2100 rows` figures: each of those carries something a date
  never does. What is refused is `2024` standing alone in prose, which on a résumé is a date.
- **A version.** A figure sitting immediately after a declared term — the `3.11` of `Python 3.11`.
  It names a release of the thing in front of it and asserts nothing about magnitude. This needs no
  second list: a version follows a technical name, and a technical name is exactly what §4's
  vocabulary pass has already found on the line.

`NUMBER`'s existing lookbehind already keeps `p99`, `EC2`, `OAuth2` and `Jinja2` out — a digit run
welded to letters is an identifier — so nothing here has to re-decide those.

**A number spelled as a word is not a figure and is not bolded.** `auto-apply/c7` reads *"three
agent skills, ~2,100 lines of prose"* and the page bolds `~2,100 lines` and leaves *three* plain.
That is a real inconsistency on the page and it is taken rather than fixed: the alternative is a
number-word list, which is a second vocabulary with none of the properties that make the first one
safe.

### 4. A keyword span is a verbatim match against a vocabulary the maker declared

Replaces `0043` §2. Three sources, unioned, **all of them literal lists a person wrote**, and no
fourth:

| source | what it is | who checks it |
|---|---|---|
| every Claim's `skills:` | the names the maker can claim | `bankcheck.py`, `check_skills_trace` |
| `bank/vocabulary.md` | the technical names his prose uses | the maker, and `bankcheck.py` counts it |
| the run's `terms.md` | the posting's own terms, verbatim | lifted at `tailor` §2, read back by `coverage.py` |

`bank/vocabulary.md` is new and it exists for a reason worth stating plainly: **a skill is named for
a capability and a sentence names a thing.** The bank calls the skill `Custom GPT configuration`;
the Bullet says *a custom GPT*. Without a second file the only way to bold `GPT` is to reword the
skills field — that is, to let a typography need press on the field that decides what the maker may
*claim*, which is the wrong direction on a system whose whole spine is evidence. It is optional, its
absence is an advisory line in `bankcheck.py` and never a failure, and a bank without one still
renders on the skills names alone.

The file is safe to keep generous for the reason this ADR keeps returning to: **it can only
emphasise text already on the page.** A term listed there that no sentence says is a term nothing
bolds. It is not evidence, it claims nothing, and it must never be read as a skills list.

**Matching is verbatim, whole-term, case-insensitive, longest first.** No stemming, no synonymy, no
plural folding — every one of those is a judgement, and `0010` refused a second judgement of prose
on the record. So `automation` does not match *Automated*, and the fix for that, if the maker wants
it, is another line in a file rather than cleverness in the renderer.

Three details the boundary rule owes, all of them found on real text:

- **Under three characters, a term is not matched at all.** `R` is a genuine Qualification on
  `auxo-ai`'s posting and is inside `Rewrote`. Same number and same reasoning as
  `coverage.MIN_TERM_CHARS` (`0041` §5), which is also why the two tools now read `terms.md` through
  one parser instead of two.
- **A hyphen and an underscore are boundaries**, so `automation` cannot bold half of
  *automation-first*. Bolding a fragment of a compound is the one way this rule makes the page look
  broken rather than merely over-emphasised.
- **A dot, a slash or an `@` running into a term rejects it.** A URL is not prose. `grafana` is a
  declared skill in the test bank and `https://grafana.internal.example.com/d/A7F3C9B2` is a link a
  Bullet may legally carry; `\b` alone bolds four characters out of the middle of it. A trailing dot
  is admitted when no word character follows, because `Next.js` is a term that can end a sentence.

**The JD-match half is emphasis of the maker's existing words, never the posting's supply of one.**
`0027` §3 and §4 forbid the posting *putting a word in a sentence* and *filtering a sentence's
interior*; by the time this runs the sentence is written, the cold read is done, and every word it
touches is one the maker composed. That is the same line `0044` §2 drew for the Summary, one element
over: the posting may lend vocabulary, never facts — and here it lends not even vocabulary, only
attention.

### 5. What carries emphasis, what caps it, and what is never bolded

**Two elements carry it.** Bullets, and the Summary.

| element | figures | keywords |
|---|---|---|
| a Bullet | all of them | at most `MAX_BULLET_KEYWORDS = 2`, leftmost first |
| the Summary | none exist (`0044` §4) | at most `MAX_SUMMARY_KEYWORDS = 3` |

The caps are **judgements, not measurements**, and they live beside the check that spends them for
the reason `SPREAD_MIN_BULLETS` does — `config.py`'s docstring is a contract that its numbers are
measured off a compiled page, and a second kind of number in it weakens that however well labelled.
Two is the number at which a line still has a body font. The Summary gets one more because it is two
typeset lines rather than one and because `0044` §4 leaves it carrying no figures at all, so three
spans are its entire bold budget.

**Leftmost wins when the cap bites**, because reading order is the only order this module can defend
without making a judgement about which of the maker's own words matters more.

**Spans never nest and never overlap.** The passes run keywords-uncapped, then figures, then
keywords again with anything a figure swallowed dropped. `3 Python services` is one span, because
`extend_over_unit` already took `Python` as the unit noun and two macros around one word is a bug
waiting to be read as a heavier weight.

**Never bolded**, and every one of these is `0043` §5 retained:

- **a lead line.** `0032` made it the entry's frame and a frame in bold competes with what it
  frames. It is also where the honest cost of this decision sits — see below. **Superseded by the
  Addendum**, which measured the constant this ADR named as the price of reopening it; the frame
  argument survives as `MAX_LEAD_KEYWORDS`, not as a refusal.
- **a Skills row's skills.** The row is the page's breadth list and its label is already its
  emphasis; a term bolded in a Bullet *and* set bold on a row is one word twice at one weight.
- **a supporting row**, an Entry header, an Education row, the profile header — fixed furniture,
  already carrying the `\textbf` the Template wanted.
- **a figure that is a date or a version** (§3), and **a term shorter than three characters** (§4).

### 6. Bold costs characters, and one ratio charges it at every width

`0043` §4's arithmetic, generalised from one span to a set:

```
equivalent characters = plain characters + bold characters x BOLD_PENALTY
```

`BOLD_PENALTY` is `CHARS_PER_BULLET / BOLD_CHARS_PER_BULLET` — 99/80 = 1.2375 today. For a Bullet
this is exactly `0043`'s formula rewritten, and `check_lengths` charges it as before.

**The new claim, and it is the one that had to be checked rather than reasoned about: that ratio is
a property of the font, not of the column.** Both constants are the same Bullet text width divided
by a pt-per-character rate, so the width cancels and what survives is bold's 6.056pt against plain's
4.915pt. That is what lets `check_summary_length` charge the Summary's keyword spans against
`SUMMARY_CHARS` — a budget measured at a different and wider `\linewidth` — **with no new constant
and no `BOLD_SUMMARY_CHARS` nobody took.** `docs/calibration.md` forbids a constant that was
estimated, and this way none is.

The probe now holds the claim as a check, in the direction that matters: *a bold character is
charged at least what it measures, at any width* — `1.2375 >= 6.056/4.915 = 1.2323`. The two
`floor`s that produced the constants push it the safe way. If a template change ever inverts it, a
bold character is being charged less than it costs, and under-counting is the one direction
`calibration.md` forbids.

**The Summary's real gate is unchanged and is not this.** `check_summary_fit` reads the height TeX
measured off the composed block, bold and all, through the `\parbox` the Template already sets
(`0044` §6). The character budget is the composer's tape; TeX is the verdict.

### 7. The probe ran, and nothing moved

`docs/calibration.md`: *"Re-run it whenever `templates/resume.tex.j2` changes its geometry, fonts,
margins or macros."* This adds no macro — `\resumeEmph` is `0043`'s and is unchanged; what changed
is how many times per line `render.py` calls it, which is not a property of the template. The probe
ran anyway, because the file's own rule is that a reader who finds a mismatched hash cannot tell
from the hash what kind of edit they are looking at.

**Measured, 2026-08-11: `RESULT: constants hold`.** `PAGE_LINES 53`, `CHARS_PER_BULLET 99`,
`BOLD_CHARS_PER_BULLET 80`, `SUMMARY_CHARS 220`, `LEAD_CHARS 114`, both Skills row figures, every
element height identical to the scaled point. `tools/config.py` is not touched by this ADR.

## Rejected

**`0043` §2's three reasons for never bolding a keyword, re-read one at a time.** They are the
strongest thing standing against this decision and each is answered on its own terms:

1. *"Bolding a term because this posting names it lets the posting choose where the reader's eye
   lands."* **This is the real argument and it is why the vocabulary has three sources rather than
   one.** A term is bolded because the **bank** declares it or because the **maker** listed it, and
   `terms.md` adds to that set rather than being it. The posting cannot introduce a word (§4), and
   on `auxo-ai` every JD-matched span sits in the Summary — the one element `0044` already licensed
   it to lend vocabulary to. What is left of the objection is real: on a run where a term appears in
   `terms.md` and nowhere else, the posting did choose which of the maker's existing words got the
   weight. That is a smaller thing than §4 forbids and it is taken knowingly.
2. *"Keywords already have their own real estate, and it is already bold."* True of the Skills rows'
   **labels**, which are category names — `Generative AI`, `Languages & Data`. It was never true of
   the technologies themselves, which sit in body roman inside the row, and the rows are the last
   thing on the page a reader reaches. A name in the sentence where the work is described and a name
   in a list at the bottom are not one word twice.
3. *"It is the surveyed tools' failure mode."* The failure `resume-optimization-crew` shipped was
   *inventing a line* to echo the posting — *"Collaboration with cross-functional stakeholders"*
   beside *"Cross-functional collaboration and team leadership"*. That is a **composition** failure,
   and it is refused by `0027` §3, the cold read, and the fact that nothing here can write a word.
   Emphasis of a sentence that would have been written identically without the posting is a
   different act.

**A composer-marked `**…**` span in `bullets.md`.** Refused again, on `0043`'s own reasoning and
without amendment. It remains the only way to bold an outcome phrase with no figure and no declared
term in it — *"in a deck senior leadership reads"* is still the most persuasive reach fact on the
`auxo-ai` page and is still plain — and it remains a marker no check can assess.

**Bolding the lead's figure.** `american-express`'s lead carries `~17.5 hours a month`, which is the
best number this bank holds, and it stays plain. Two reasons and the second is the binding one:
`0032` made the lead the entry's frame, and charging bold there needs a bold character count at the
lead's own `\linewidth` that nobody has measured. §6's ratio would make that derivable, but
`config.py` is explicit that a constant change is *"a selection event, not a layout tweak"*, and one
is not smuggled in under a typography ticket. **If this is reopened it is reopened as a
calibration**, with `LEAD_CHARS`'s bold twin measured off a compiled page.

> **Reopened and settled on 2026-08-11 — see the Addendum below.** The measurement was taken, the
> constant is `BOLD_LEAD_CHARS = 80`, and the lead now carries emphasis. This paragraph stands as
> the record of the terms that were set for reopening it; the Addendum is those terms being met.

**A curated technical-term list living in `render.py`.** It is data about the world, not about the
template, and it would need editing for every bank. `UNIT_STOPWORDS` is in `render.py` because a
preposition is a fact about English; `Streamlit` is a fact about this maker.

**Deriving the technical terms by shape instead of by list** — an internal capital, an all-caps
token, a word a dictionary does not hold. Tried against this bank and it fails in both directions:
the `skills:` fields are sentence-cased inconsistently (`Debugging`, `User acceptance testing`,
`prompt engineering`), so case cannot separate `Python` from `Business`, and a dictionary is an
environment dependency that would make the page a function of the machine that rendered it.

**Stemming, or matching a term's individual words.** Word-splitting the vocabulary is what would
catch `GPT` inside `Custom GPT configuration` without a second file, and it also bolds `data`,
`business`, `layout` and `model` all over the page. Every filter that fixes that is a list of
generic English words — which is the dictionary again, or a judgement.

**Raising `CHARS_PER_BULLET` to absorb the wider bold charge.** `0025` refused raising it on the
record, `0043` refused it again, and nothing here reopens it. Bold costs characters; the lines get
shorter.

**Italics, colour, a second weight, or a bolded lead-in phrase.** One emphasis to a page. `0007` put
the Template in charge of appearance and this still spends exactly one of its levers.

## The cost, stated rather than waved past

**Three lines had to be rewritten shorter on the `auxo-ai` re-run, and that is the design working.**
`0043` predicted it — *"on a tighter page the lint will start refusing lines that read well"* — and
the prediction came due immediately:

| line | was | now | what was cut |
|---|---|---|---|
| `american-express/c7` | 98 ch | 94 ch | *new* — the scorecard was newly built and the page no longer says so |
| `xlscout/c3` | 97 ch | 85 ch | *translation* — the entry's lead still frames it, the Bullet no longer does |
| the Summary | 211 ch | 207 ch | *data work* |

None of those is a good trade in isolation. The trade is that `~150 KPIs`, `~8 hours a month`,
`Gemini`, `Qwen` and eleven other spans are now findable in a thirty-second read, and `0027`'s
cut-for-length is the mechanism the system already uses to pay for room.

**Nineteen bolded spans on one page is close to the ceiling of what "emphasis" can mean.** Seven
figures and twelve keywords across sixteen Bullets and a Summary. `0043` warned that *"a page where
every line carries a bold run has no emphasis — it has a second body font"*, and that warning is not
retracted: it is now held by two caps and a vocabulary the maker controls rather than by a rule that
allowed one span. **The next output review should read the compiled page and count, and if it reads
busy, the lever is `MAX_BULLET_KEYWORDS`, not the figures.**

**The Summary is where the weight concentrates, and it is the least-checked element on the page.**
Three of its ~35 words are bold, chosen leftmost, and on `auxo-ai` all three are JD terms. `0044`
already called the Summary *"the largest unchecked surface this system has"*; this ADR puts the
page's densest emphasis on it. The mitigation is that emphasis cannot change what the sentence says
— but a false claim set in bold is read harder than a false claim set plain, and that is a real
increase in what the cold read is carrying.

**`MIN_KEYWORD_CHARS = 3` silently drops terms that matter.** `AI` is the single most load-bearing
term on this posting and is never bolded anywhere. There is no fix that is not a list of exceptions,
and a two-character substring is inside `said`, `again`, `maintain` and `AI-driven` itself.

**Leftmost-wins is arbitrary where the cap bites.** On the `auxo-ai` Summary it spends all three
spans on `generative AI`, `AI-driven business copilots` and `NLP`, leaving `Python`, `model
evaluation` and `BigQuery` — the most concretely technical names in the sentence — plain, purely
because they were written last. Any other rule is a judgement about which word matters more.

## Consequences

- **`docs/adr/0043`** stands; §1, §2 and §5's one-span and no-keyword clauses are superseded here.
  Its §3 (the Template owns the bolding), §4 (bold is charged) and its refusal of a composer-marked
  span are unchanged and are load-bearing for this ADR.
- **`bank/vocabulary.md`** is new, optional, and read by `render.py`, `lengths.py` and
  `bankcheck.py`.
- **`tools/render.py`**: `read_if_present`, `listed_items`, `keyword_vocabulary`, `keyword_pattern`,
  `keyword_spans`, `is_year`, `figure_spans`, `emphasis_spans`, `BOLD_PENALTY`,
  `bold_equivalent_chars`; `emphasis_span` and the old single-span `emphasised_latex` are gone;
  `bullet_line_cost` and `emphasised_latex` take a span list; `check_lengths` takes the vocabulary
  instead of the bank and names every span when it refuses; `check_summary_length` charges bold;
  `PageContents.vocabulary`; `fill_template` emphasises the Summary as well as the Bullets.
- **`tools/lengths.py`** builds the same vocabulary from the same three files and charges the same
  way. It no longer needs the bank to charge a Bullet's figures — only its keywords.
- **`tools/coverage.py`**: `terms` is now `render.listed_items`, so the tool that counts terms and
  the tool that bolds them cannot disagree about what a term is.
- **`tools/bankcheck.py`** gains `vocabulary_advisory` — counted, never judged, never a failure.
- **`templates/resume.tex.j2`**: the `\resumeEmph` comment says what now calls it. The macro is
  unchanged.
- **`tests/calibration/probe.py`** gains *a bold character is charged at least what it measures, at
  any width*, which is the only thing holding §6's width-independence claim.
- **`docs/calibration.md`** gains a dated line; **`tools/config.py`** gains a note and **no constant
  change**.
- **`tests/test_render.py`**: the emphasis block is rewritten — every figure bolded not just one, no
  Claim read, the year and version exclusions, the four-digit quantity that is not a year, the
  vocabulary's three sources and its longest-first order, the compound and URL boundaries, the cap
  and the uncapped figures, the double-bold that does not happen, bolding introduces no new text,
  the spans never cover the line, the bold penalty is a font ratio, and the Summary is charged for
  its keywords. `FILLER` lost the phrase `on-call`, which is a fixture skill and would have pushed
  every spread-test Bullet over its cap — the length tests are about length and nothing else.

---

# Addendum, 2026-08-11 — the lead is reopened, measured, and bolded

**Status:** accepted. Supersedes §5's *"never bolded: a lead line"* and the *Rejected* entry
*"Bolding the lead's figure"*. Everything else above stands unamended, including §6, which this
addendum tests rather than replaces.

Written as an addendum rather than folded into the body on purpose. The body records a decision
taken with a measurement missing and the cost of that absence named; rewriting it to read as though
the lead were always in scope would erase the one thing worth keeping — that the constant was
refused first, on a rule, and taken later, on a measurement.

## A1. The terms this ADR set for reopening, met

The *Rejected* entry above named exactly one thing standing between the lead and its figure:

> *"charging bold there needs a bold character count at the lead's own `\linewidth` that nobody has
> measured. §6's ratio would make that derivable, but `config.py` is explicit that a constant change
> is 'a selection event, not a layout tweak' … **If this is reopened it is reopened as a
> calibration**, with `LEAD_CHARS`'s bold twin measured off a compiled page."*

The maker reopened it. This is the calibration, taken on its own, with nothing else in the change.

## A2. What was measured

`tests/calibration/probe.py` gains `LEAD_BOLD_SAMPLES`, `measure_lead_bold_widths` and
`measure_bold_lead_chars` — `measure_lead_chars`'s method with `\textbf` around the `\sbox`, run
inside `\resumeEntryLead`'s own `\item`, so both counts come off **one width** and anything that
moved between them would have moved the ratio for a reason that is not the font.

The samples are the two shapes emphasis actually produces and no third: a figure grown over its unit
noun (§2), and a declared vocabulary term (§4). Widest wins, as everywhere else here.

| sample | pt/char | chars at the lead's 514.40pt |
|---|---|---|
| `~30% GPU spend` | 6.396 | **80** |
| `Gemini` | 6.112 | 84 |
| `Claude Code` | 5.910 | 87 |
| `~150 KPIs` | 5.845 | 88 |
| `Google BigQuery` | 5.820 | 88 |
| `Machine Learning Platform` | 5.566 | 92 |
| `~17.5 hours a month` | 5.439 | 94 |
| `~2,100 lines` | 4.864 | 105 |

**`BOLD_LEAD_CHARS = 80`.**

### What is deliberately not in that family, and why it is a judgement worth showing

**A bare all-caps acronym** — `GPT`, `LLM`, `R&D`. They are real declared terms and a lead may well
bold one. What they are not is a **rate**: `R&D` measures 8.796 pt/char and `GPT` 8.301, because a
three-character all-caps token has no lowercase letters to average against. That is the
`WWW MMM WWW` case `WIDTH_SAMPLES` already refuses one block up — *"it would win every time and
drive the budget down by 40%, and it is not English"* — and here the consequence is not
hypothetical. Taking `R&D`'s rate gives `BOLD_LEAD_CHARS = 58` and a penalty of 1.966, which
**refuses `american-express`'s lead**: 101 characters carrying one 19-character bold span, charged
119 against a budget of 114, when the thing typesets at 474.74pt inside a 514.40pt line with 40pt to
spare. A constant that refuses the sentence this ADR was reopened to set in bold is measuring the
wrong quantity.

The excess a short acronym does spend is small and bounded: three characters at 8.30 against a
charged 6.40 is 5.7pt, well inside the interword shrink a line of this length carries. And the tape
was never the gate. `check_overflow` reads pdfTeX's own overfull-hbox report and already attributes
it to the lead by its `%% AUTOAPPLY:element:lead:` marker, exactly as `check_summary_fit` is the
Summary's real verdict and `SUMMARY_CHARS` its composer's tape.

## A3. The constant is dearer than the derivation, and §6 survives that

`LEAD_CHARS / BOLD_LEAD_CHARS = 114/80 = 1.4250`, where a Bullet's `BOLD_PENALTY` is
`99/80 = 1.2375`. That looks like §6 failing and it is not.

**§6's claim holds, and this is a third width at which it was checked rather than trusted.** Measured
per string, plain against bold, at the lead's own `\linewidth`: `1.1513`, `1.1547`, `1.1567`,
`1.1566`, `1.1520`, `1.1538` across the six `LEAD_SAMPLES`. The bold penalty really is a property of
the font, and it really does not move with the column.

**What differs is the sample family, and that is a fact about the elements rather than about the
font.** `LEAD_CHARS` is measured off lead **sentences** — narrow prose at 4.510 pt/char.
`BOLD_LEAD_CHARS` is measured off bold **spans** — figures and technical names, which run wide.
Each is the worst realistic sample of what that element sets *in that weight*, which is the rule
this repository applies everywhere, and the ratio between two worst cases drawn from two families is
not the same number as the ratio between one string set two ways. The Bullet's 1.2375 has the same
shape for the same reason: `BOLD_CHARS_PER_BULLET` came off a Skills **label** and
`CHARS_PER_BULLET` off a Bullet **sentence**.

So the derivation and the measurement disagree by about 15%, in the safe direction, and the
measurement wins — which is the whole of why this ADR insisted on one.

**The probe now holds both.** *"A bold character is charged at least what it measures, at any
width"* was §6's; it gains *"a bold character in a lead is charged at least what it measures"*, the
same direction at the lead's width, plus one the ratio cannot make on its own: **a lead composed to
the bold-aware budget still fits the lead's line.** A safe ratio spent against a budget that was too
generous still puts a lead on a second line, and `LEAD_LINES` charges one. So every `LEAD_SAMPLES`
sentence is composed out to the last word the tape admits with a real bold span in it, and the width
TeX gives the result is read back — the `measure_summary_chars` idiom, one element over.

## A4. What the lead now sets in bold

**The same `emphasis_spans` a Bullet uses**, so every rule in §2, §3 and §4 comes with it and nothing
here re-decides one: every impact figure grown over its unit noun; a year and a version excluded; a
number spelled as a word left plain; verbatim, whole-term, longest-first keyword matching over the
same three declared sources, with the same compound and URL boundaries.

The one thing that is the lead's own is the cap. `MAX_LEAD_KEYWORDS = 2`, a Bullet's — one typeset
line carrying one or two facts is a Bullet's shape, so the number that keeps a body font on a Bullet
keeps one on a lead. It is a name of its own rather than a reuse of `MAX_BULLET_KEYWORDS` because
§5's table is per element, and because the lead is the one element with a standing argument for
spending less: `0032` made it the entry's **frame**, and a frame competing with what it frames is the
failure mode to watch on the next output review. **The frame argument survives the reopening — as
`MAX_LEAD_KEYWORDS`, not as a refusal.** Moving it to 1 is a one-line change and no change anywhere
else.

## Rejected, this time round

**Reusing `BOLD_PENALTY` and taking no constant.** Derivable, cheaper, defensible on §6's own
reasoning, and refused — because §6's width-independence is a claim about the font and the number a
lead needs also depends on which family each of its two counts was drawn from (A3). It is also
what this ADR said it would not do.

**Taking the worst acronym's rate.** Measured, and it refuses a lead that fits with 40pt to spare
(A2). Safe is not the same as correct when the safe number makes the element unusable.

**A `BOLD_SUMMARY_CHARS` while the tools were open.** Out of scope, and still not needed: the
Summary's gate is `check_summary_fit`, which measures the composed block bold and all. Nothing here
reopens it.

**Charging `LEAD_LINES` more than 1.** Nothing about emphasis makes a line taller. `\resumeEmph` is
`\textbf` and adds no glue, no box and no list level; the probe's *"a one-line lead costs no more
than one Bullet line"* check ran and is unmoved.

**Bolding the lead's *situation* clause.** The lead carries a situation and an aggregate (`0032`
§4); only the aggregate has figures, and the situation clause has whatever declared terms it says.
No rule distinguishes the two halves, and inventing one would be a judgement about which half of the
maker's own sentence matters — the thing leftmost-wins exists to avoid.

## Consequences

- **`tools/config.py`** gains **`BOLD_LEAD_CHARS = 80`**, beside `LEAD_LINES` and `LEAD_CHARS`, and
  the docstring records it as **a selection event, not a layout tweak** — it shortens what a lead may
  say whenever a lead says something bold, which changes which evidence reaches the page. It is
  committed on its own. It is the same integer as `BOLD_CHARS_PER_BULLET` and unrelated to it; the
  file says so, because the next re-measure moves them apart.
- **`tools/render.py`**: `LEAD_BOLD_PENALTY`; `bold_equivalent_chars` takes a `penalty`;
  `check_lead_lengths` takes the vocabulary, charges bold and names every span when it refuses;
  `MAX_LEAD_KEYWORDS`; `fill_template` emphasises the lead.
- **`tests/calibration/probe.py`**: `LEAD_BOLD_SAMPLES`, `measure_lead_bold_widths`,
  `measure_bold_lead_chars`, `measure_lead_at_budget`, the two new checks, and the bold half of the
  lead's report block.
- **`templates/resume.tex.j2`**: the `\resumeEntryLead` comment says the lead carries `\resumeEmph`
  and why `BOLD_LEAD_CHARS` is its own measured constant. **No macro changed**, so no height moved —
  the probe was re-run anyway, on the rule that a reader who finds a mismatched hash cannot tell from
  the hash what kind of edit they are looking at.
- **`tools/lengths.py`** is untouched: it has never measured a lead, and giving it one is a separate
  change.
- **`tests/test_config.py`** learns the new constant; **`tests/test_render.py`** gains the lead's
  emphasis rules, its own penalty, its tape refusing a lead that fits plain, and the figure reaching
  the compiled `.tex` inside `\resumeEmph`.
- **`tests/test_template.py`** gains *no lead at the bold-aware budget wraps* — the Bullet's own
  width check at the lead's `\linewidth` and with the lead's bold charge. It matters that this one
  is in the **suite** rather than only in the hand-run probe: a wrapped lead costs two lines where
  `LEAD_LINES` charges one, and it fails silently, because a paragraph breaks legally and warns
  about nothing.
