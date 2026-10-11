# The Bullet is written in plain English

**Status:** accepted

## Context

`runs/zs-btsa` was composed three times against the same JD, the same bank and the same
`scores.md`, by three different models — `zs-btsa-claude` (Claude), `zs-btsa-hermes`
(deepseek) and `zs-btsa-agy` (Gemini). Every rule in this skill held in all three runs. Every
figure traced. Every citation resolved. The merge verifier came back `clean`.

And all three pages are written in the same voice, which is not a human one:

> *Kept the system honest to its evidence by owning the page arithmetic outside the model*
> — `zs-btsa-hermes`, `auto-apply/c2+c4+c5`

> *Proved the translation tool generalised past its team by taking it to the other product
> teams* — `zs-btsa-hermes`, `xlscout/c1+c5`

> *Held the pact's rules on the server: a Haversine check against each gym's radius, a
> constant-time secret on the iOS Shortcut posting check-ins, and row-level security on
> invites* — `zs-btsa-claude`, `sweatpact/c1+c2+c3`

> *Enforced provenance constraints and prevented model hallucinations by pairing a pre-render
> verification pass with a decoupled architecture that keeps page packing deterministic*
> — `zs-btsa-agy`, `auto-apply/c1+c2`

**Three different models, one register.** That rules out a prompt accident in any one of
them and rules in the register itself: it is what an LLM writes when it is asked to compress
an argument into a sentence and given no instruction about voice. The `claudish` project
(`github.com/programasweights/claudish`) names it and characterises it exactly —
*rhetorically polished, contrast-heavy, structurally metaphorical, process-oriented, and
prone to expressing one simple proposition through several abstractions, contrasts and
restatements.*

Read the four lines above against that description and every clause of it lands. *Kept
honest*, *owning*, *held the rules*, *proved… past its team* are metaphors standing where a
verb for the actual action belongs. *Provenance constraints*, *a decoupled architecture that
keeps page packing deterministic* are nominalisations standing where a clause belongs.
*Generalised past its team*, *rather than a script he ran on their behalf* are contrasts the
sentence did not need.

**This is a résumé.** The reader is a screener with thirty seconds and a stack, and the
register costs on both axes a screener reads for: it is harder to parse than the fact it
carries, and it reads as generated. Neither is caught by anything downstream — `render.py`
reads numbers, citations, lengths, openers and spelling, and none of those read English.

## The trap: the obvious fix loses facts

The `claudish` project ships a translation both ways, as a spec (`specs/claudish-to-english.md`)
and as a ProgramAsWeights function (`to_english`, `e469f61ccab2699fbd51`). The obvious
integration is a post-pass: compose as today, then translate `bullets.md` before rendering.

**That post-pass is forbidden here, and the reason is in the spec's own text.** Its central
rule is *prefer semantic compression*:

> If deleting a clause changes no fact, condition, permission, uncertainty, or implication,
> prefer deleting it. […] It is acceptable, and often preferable, for the output to be
> substantially shorter than the input.

The rule is correct for the prose it was written for, where a Claudish passage restates one
proposition four ways. **A Bullet has no restatements to collapse.** It is written at maximum
density into 99 or 198 characters, and §5's cut-for-length table is four worked examples of
what a Bullet gives up when it is over — *"not one lost a fact."* Every clause in a finished
Bullet carries a distinct fact that traces to a cited Claim's Evidence. So a compression pass
over final text has nothing to take but facts, and the first thing it takes is the reach fact
(`0055`) — the denominator, the audience, the spread — because that is the clause whose
deletion looks most like deleting rhetoric.

**This was measured, not assumed.** `to_english` was run over all 31 Bullets of the three
`zs-btsa` runs. Three of the results, verbatim:

| ref | in → out | what came back |
|---|---|---|
| `zs-btsa-claude` `american-express/c1+c3+c4` | 170 → 82 chars (−52%) | *"Move the hand-run reporting to Python, and drop the BigQuery tables from the deck."* |
| `zs-btsa-claude` `auto-apply/c4+c7` | 189 → 109 (−42%) | *"The bank stores raw evidence, not pre-written bullets, because the ingestion one was forbidden from drafting."* |
| `zs-btsa-hermes` `auto-apply/c7+c1` | 121 → 72 (−40%) | *"The system passed the build because the recorded claim was not rejected."* |

The first lost the whole figure — *~8 hours a month*, the group's stored `## merge` sum — and
inverted the BigQuery clause into its opposite. The second lost *Claude Code agent skills*,
which is the entirety of what `c7` is about, so a claim the allocation granted a line stopped
being represented on it. The third lost both cited claims and came back a sentence about
nothing.

**A page that reads beautifully and has quietly lost the denominator has failed worse than a
page that reads like a machine**, because the second failure is visible.

### The tempting second conclusion, and why it did not survive its own measurement

The lines that came back **unchanged** looked at first like a detector:

| ref | in → out |
|---|---|
| `zs-btsa-hermes` `american-express/c5` | 76 → 76 chars (+0%), word for word |
| `zs-btsa-hermes` `american-express/c6` | 88 → 88 (+0%) |
| `zs-btsa-agy` `american-express/c1+c3+c4` | 163 → 159 (−2%), every fact kept |
| `zs-btsa-claude` `xlscout/c3` | 170 → 167 (−2%), every fact kept |

Those four are among the plainest lines in the three runs, the six the translator cut hardest
are among the worst, and the obvious inference is that shrinkage measures residual rhetoric.

**It does not, and running it over the finished plain-English page is what showed that.**
`runs/zs-btsa-english` trips one marker in `plainish.py` across the whole page, and its lines
still came back 21%, 31%, 52%, 64% and 73% shorter. The 73% is `xlscout/c3`:

> *in* — Picked a translation model per language by scoring four backends against text a
> native-speaker translator had already verified, settling on Gemini for Spanish and Qwen for
> Japanese.
> *out* — For Spanish, use Gemini; for Japanese, use Qwen.

Nothing in that input is Claudish. What separates it from the four lines above is **length**:
they run 76–170 characters and it runs 181. The PAW interpreter is Qwen3 0.6B, and past roughly
170 characters of dense, low-redundancy prose it stops paraphrasing and starts summarising —
`auto-apply/c1+c2+c5` came back as *"Do not use the figures or claims in the script"*, which is
not a compression of the input, it is a misreading of it.

**So the percentage confounds register with density, and this ADR does not claim otherwise.**
What the 40-line measurement does establish is the negative result, which is the one the design
turned on: on a résumé Bullet a compressing translator loses facts whether or not the sentence
deserved compressing. **The program is a catastrophic editor, and only a weak detector** —
§"Decision" 4 keeps it for the first fact and declines to lean on the second.

## Decision

**The voice is a composition input, not a post-pass.** Bullets, leads, the Summary and
supporting tails are written in plain, direct, idiomatic English *at §5*, under a voice guide
adapted from `claudish-to-english`: `.claude/skills/tailor/plain-english.md`.

Four things follow from putting it there rather than after.

### 1. Compression spends what it frees on facts, never on nothing

The spec's register rules — strip the metaphor, drop the contrast, lower the abstraction,
turn the nominalisation back into a verb — return characters. At §5 those characters are
still inside the line's budget, so they are spent the way §5 already says to spend spare
characters: on the strongest reach fact the sentence can afford (`0055`). **The transform is
fact-monotone.** *Held the pact's rules on the server: a Haversine check against each gym's
radius* is 20 characters of frame around one fact; *Verified gym check-ins server-side
against each gym's own 50m radius* says more in less.

Run after composition, the same rules return characters to nobody and delete a clause to
collect them. Run before, they buy room. That is the whole of the difference, and it is why
the integration point is the only design question this ADR had to answer.

### 2. Rule 2 is untouched, and it outranks the voice everywhere they meet

The voice guide governs **words**. `0053` governs **facts**. Nothing in the voice guide
licenses a fact, and where plain English would be easier with a fact the Evidence does not
carry, the sentence goes without it exactly as it does today. The clause is written into the
guide in the guide's own terms: *plainer is never a ground for dropping a figure, a
denominator, an audience or a scope, and the number is still the last thing a Bullet gives
up (`0029`).*

### 3. It is checked by a human-readable pass, not by a lint that reads meaning

`tools/plainish.py` is added, and it is deliberately shallow: a pattern lint over the
register markers the spec enumerates (contrastive framing, aphoristic tails, staged emphasis,
the metaphor vocabulary, colon-drama, nominalisation suffixes), plus an assertion that every
Bullet still carries the citation `allocation.md` granted it. **It prints and never gates**,
the standing `xray.py` and `coverage.py` already hold. A pattern lint cannot tell *row-level
security* from *the security surface*, and the spec says so itself — *keep terms like
provenance, boundary, gate when they are genuinely the clearest technical description.* A
lint that failed the run on those would be corrected by making the page worse.

What decides is §5.05's cold read and §5.06's per-Bullet evidence check, both of which read
meaning because a model is doing the reading.

### 4. The PAW program is a detector, never a writer

`plainish.py --paw` runs `to_english` over each composed line and compares the **facts** in
the two texts — figures, and the capitalised or technical tokens the line carries. It reports
how much shorter the translation came back and which facts it dropped, attaches **no verdict**
to either number, and writes nothing.

The drop list is the half worth reading: it names which of a line's facts a paraphrase reaches
for first, and those are the facts worth checking against the Evidence one more time. The
percentage is reported because it is the evidence for the rule above — that this transform
cannot be applied to final text — and not because it scores the prose; the section above is why.

The output is never copied to the page and the tool never edits `bullets.md`. That
containment is what makes it safe to run a compressing translator at all inside a pipeline
whose first rule is that facts do not go missing.

The dependency is optional and unvendored: `programasweights` builds `llama-cpp-python` and
downloads a model, which no run may require. Without it the flag prints one line saying so
and the rest of the pass runs.

## Consequences

- §5's composition rubric gains a voice section; `plain-english.md` is its long form, sitting
  beside `company-research.md` as the skill's second side file.
- §5.05's cold read gains a third question. The stranger already had to parse the line and
  carry it away; now they are also asked whether a person wrote it.
- §5.06 is new: `plainish.py`, then the per-Bullet evidence check. That check is §5.1's merge
  verifier generalised — the same subagent, the same two questions, now run on **every**
  Bullet rather than merged ones only. Rewriting a line for voice is exactly when a fact goes
  missing quietly, so the verifier that existed for the one composition step that invented
  facts now covers the second one.
- `runs/zs-btsa-english` is the demonstration: the same JD, the same bank, and `scores.md`
  copied byte-for-byte from `runs/zs-btsa-claude` so the only variable between the two pages
  is the voice.
- The three `zs-btsa-{claude,hermes,agy}` runs are kept as the before. They are not re-run.
