# The page opens on a summary, and the posting may lend it words there

**Status:** accepted

## Context

`runs/auxo-ai` renders sixteen Bullets, four leads and four Skills rows across four entries, and a
reader arriving at the top of it meets `Product Development Intern` — `American Express` and then
five achievements. Nothing on the page says what the person **is**. The entry headers say where he
was; the Bullets say what he did there; the Skills rows say what he can name. The claim a résumé
normally opens with — *this is the kind of engineer you are looking at* — is the one thing sixteen
true sentences cannot make, because a Bullet is scoped to one Claim by construction
(`0027` §6) and no Claim is about the candidate.

There is a second reader, and it does not read sentences at all. `jd.md` for `auxo-ai` carries
**thirty-four Must-have terms** and `terms.md` lifts every one of them; the page as composed can
only echo the ones a placed Claim's own Evidence happens to carry. `deep learning frameworks`,
`TensorFlow`, `PyTorch`, `R`, `feature engineering`, `Business Requirement Documents` reach neither
a Bullet nor a Skills row, and `gaps.md` classifies them honestly as things the bank does not hold.
That is the right answer for a Bullet and the wrong shape for the top of the page: **the terms the
candidate genuinely works in are also mostly absent from the first inch of the document**, which is
the only part a keyword scan and a thirty-second human read both reliably reach.

### The rule this decision is a stated exception to

`0027` §3 and §4, which are the two sharpest sentences in the composition rubric:

> *"The posting may tell you which of your own words to reach for; it may never supply one."*
>
> *"The JD decides which claims get a line. It does not decide what goes in the sentence."*

They were earned. §3's worked example is `xlscout/c1` bent into *"Ran user acceptance testing
across product teams and handled post-go-live fixes"* — every word defensible, the whole sentence a
job description, and fourteen characters longer than the truth it replaced. §4's is the JD filter
applied twice, once to select the Claim and again to the inside of its sentence, leaving only the
part the posting already knew.

**The maker has relaxed that rule for this element and no other.** Not because the reasoning was
wrong, but because it was reasoning about a **Bullet**, and both of its mechanisms are about a
Bullet's interior. §3 protects a sentence *that is making a specific claim about a specific piece of
work* from being rebuilt out of the posting's phrase for it. §4 protects the *detail inside such a
sentence* from being filtered a second time by the posting. A Summary makes no specific claim about
a specific piece of work — it says what the candidate is and what they work in — so there is no
interior for the posting to hollow out, and there is no `4-5 Excel files` for it to cut. What the
posting supplies here is **vocabulary for a claim the maker is already making**, which is what §3
licenses everywhere else and refused only because a Bullet's words were doing a second job.

## Decision

### 1. The Summary is one unbulleted paragraph, at the top, two typeset lines, no heading

It sits between the Static profile header and `\section{Experience}` — the first prose on the page.
It is composed per run, like a Bullet and a lead, out of `bullets.md`'s new `## Summary` section.

**Two typeset lines, `SUMMARY_LINES = 2`, fixed by decision rather than derived** — the same
standing `LEAD_LINES = 1` has (`0032` §4), and for the same reason: nothing measures how long a
summary *should* be. Two lines is about thirty-five words, which is the length at which a summary
is still read; it is also **two Bullets**, and *The cost* below states that rather than waving
past it.

**No `\section{Summary}` heading.** A heading costs `SECTION_LINES = 2` on top of the prose — a
third of a whole page's evidence spent on the word *Summary* — and buys nothing either reader
needs. A keyword scan matches text, not sections; a human meeting a paragraph directly under a name
and a contact line does not need to be told it is a summary. Headings on this page earn their
height by separating things that would otherwise run together, and nothing precedes this one.

> **Reversed on 2026-08-11 — see the Addendum below.** The Summary carries a `\section{Summary}`
> heading, charged `SECTION_LINES` like any other. This paragraph stands as the record of what the
> heading was refused for and what it was known to cost; the Addendum is the maker paying it.

### 2. The relaxation is exactly one thing wide: the posting may supply WORDS, never FACTS

The Summary may echo `jd.md`'s vocabulary and role-adjacent phrasing — `generative AI`, `AI
application development`, `decision-making systems`, `NLP` — including terms no placed Claim's
Evidence spells. That is the whole licence, and it exists because a term the candidate genuinely
works in should reach a scanner even when the Bullet that proves it says `copilot` instead.

**Everything the sentence ASSERTS still comes from the bank.** No invented metric, no title the
maker does not hold, no employer he did not work for, no experience he does not have, no seniority,
no years. The test is unchanged from rule 2 of the skill and §6 of `0027`: **the maker has to defend
it in the interview.** A posting asking for `5+ years` licenses the word *years* in no sentence on
this page.

The line between the two is sharper than it looks, and it is this: **a keyword is a name for
something; a fact is a claim about the candidate.** Writing `NLP` where the bank says *translation
pipeline over model APIs* is renaming work he did. Writing `deep learning frameworks` when the bank
holds no model he trained is claiming work he did not do, and the fact that it is a keyword does not
change that. **The relaxation licenses re-naming, never re-scoping.** A term the bank cannot support
belongs in `gaps.md`, exactly where it goes today.

### 3. The facts come from the profile's `## Standing` block and from the Claims

Two sources, and no third:

- **`bank/profile.md`'s new optional `## Standing` block** — free prose lines the maker writes about
  himself, the durable self-description no Claim holds and no Entry header states. It exists because
  the alternative was the composer inventing one: this bank's two job titles are `Data Scientist
  Intern` and `Product Development Intern`, and a Summary that opens `AI Engineer` has awarded the
  candidate a title. What he is — a final-year CS undergraduate specialising in data science, who
  builds AI applications end to end — is true, is his to state, and was nowhere in the bank.
- **the Claims**, whose Assertions and Evidence are what the summary generalises over. The
  generalisation may be wider than any one Claim — that is what a summary is — but every kind of work
  it names must be work some Claim carries.

`## Standing` is **optional and never a hard failure**. A bank without one still renders; the
Summary is composed from the entry headers and the Claims, and `tools/bankcheck.py` says the block
is missing on the advisory line it already prints for the Static profile's cost
(`0031` §5, §7 — the parts of the page that never compete are the maker's call, and this check
prices them rather than refusing them).

### 4. No figure ever appears in the Summary, and that is checked

`check_summary_figures` fails the run on any number in it.

**Not a style rule — a consequence of having nothing to trace to.** Every other figure on this page
is resolved against a cited Claim's stored `number:` at equal-or-softer provenance
(`check_number_trace`), or against the Entry's `## lead` block (`check_lead_trace`). The Summary
cites nothing: it is one sentence about a whole career, and there is no Claim to resolve it against.
Resolving it against *any* Claim in the bank instead would be a check that passes on
`~95%` borrowed from a translation benchmark and reported as though it described the candidate.

This is `0043`'s own reasoning applied one element over. It refused a composer-marked emphasis span
because *"nothing could check it"*, and took a real loss to keep the record auditable. A Summary
figure is that hole with a number in it, on the most-read line of the page. **The figures live in
the Bullets, where they trace.**

The check is a mechanical one — `numbers()` over the composed text — so it fires or it does not, and
it cannot report that a sentence looks fine. `0010`'s refusal of a second judgement of prose stands.

### 5. It is a fixed part of the page: always charged, always composed

`bullet_budget` subtracts `SUMMARY_LINES` unconditionally, the way it subtracts `HEADER_LINES`, and
`bullets.md` with no `## Summary` section is a hard failure naming the file. This is the Skills
section's precedent exactly (`render.py`: *"the Skills breadth list is a fixed part of the page and
the budget charges for it"*), and the alternative is worse than it sounds: an optional Summary means
the Packer either charges for one that may not arrive — leaving evidence off the page for room
nobody used — or charges nothing and discovers the overflow at the page-count assert, where the
message blames the constants. The Packer is bank-blind and runs before a word is composed; a
conditional element it cannot see is a budget that is wrong in one direction or the other.

### 6. The fit is asked of TeX, not modelled — and the character budget is the composer's tape

Two numbers, doing two different jobs.

**`SUMMARY_CHARS` is a pre-compile budget**, measured the same way as `CHARS_PER_BULLET` and
`LEAD_CHARS` — widest realistic sample wins, against the Summary's own `\linewidth`, which is the
full text width because the paragraph sits at top level rather than inside any list. `check_summary_length`
enforces it before the compile so the composer meets a number while writing, and
`tools/lengths.py` reports it on the same tape.

**But characters are not the gate here, and they cannot be.** `CHARS_PER_BULLET` bounds a *one-line*
element, where a character count and a line count are the same question. A two-line paragraph breaks
at word boundaries, so a text inside `2 x` the per-line count can still spill to a third line —
and a three-line Summary is **silent**: it breaks legally, LaTeX warns about nothing, and the budget
over-promises by a whole line. That is precisely the Static profile header's problem, and it gets
the Static profile header's answer.

So the Template measures the composed paragraph in a `\parbox` at its real `\linewidth` and
`\typeout`s the height; `render.py` fails the run when it exceeds `SUMMARY_LINES x BULLET_LINE_PT`.
**Ask TeX, do not model TeX** — the Template's own words for `\hfuzz`, and `0017`'s for the header.
The invariant the check states is the one that actually matters: *the Summary fits inside the lines
the budget charged for it.*

### 7. The Overflow check gains a `summary` element

`%% AUTOAPPLY:element:summary:page` above the block, `page_elements` names it, and
`check_markers_account_for` holds the two sets together as it does for every other element. The id
is `page` rather than a slug because there is exactly one and it belongs to no Entry.

### 8. The probe ran, and one constant moved for a reason that is not a measurement

`docs/calibration.md`: *"Re-run it whenever `templates/resume.tex.j2` changes its geometry, fonts,
margins or macros."* This adds a macro and a block above every section on the page, so it ran.

**Measured, 2026-08-10. `RESULT: constants hold`.** Every element constant came back unmoved —
`HEADER_LINES 3` (36.91pt, to the scaled point), `SECTION_LINES 2`, `ENTRY_HEADER_LINES 2`,
`CHARS_PER_BULLET 103`, `BOLD_CHARS_PER_BULLET 83`, both Skills row figures, `LEAD_CHARS 117` — and
`SUMMARY_CHARS = 220` is newly measured, at the Summary's own 542.03pt `\linewidth` (`+34.93pt`
against a Bullet's, `+10.84pt` against a lead's).

**`HEADER_LINES` surviving is a property of how the block is priced, not luck.** The cheap
measurement — a `\pagetotal` reading at the first token of the Summary's text — reports 46.78pt
where the header is 36.91pt. That 9.87pt is glue `\end{center}` contributes when the next paragraph
starts, and charging it here would have pushed `HEADER_LINES` to 4 under a typography ticket. The
probe prices the Summary as a **differential** instead: the same page built from the template with
the `\resumeSummary` call site removed, differenced at the first Bullet's marker. Glue the two share
is charged to neither.

**And the macro's trailing `\vspace` was set by that measurement.** At `-6pt` the block measured
**28.70pt against the 28.00pt** two Bullet lines charge — an over-promise, and the one direction
`calibration.md` forbids. `-8pt` brings it to **26.70pt** and clears by 1.30pt. Two probe checks
hold it: *a two-line Summary costs no more than two Bullet lines*, and *the Summary-fit ceiling
separates a two-line Summary from a three-line one* (20.89pt ≤ 28.00pt < 32.89pt) — the second is
what makes §6's runtime gate a gate rather than a number that always passes.

`PAGE_LINES` stays 50. It is read off the compiled page, and the sweep now compiles a page carrying
a Summary — so what moved is not the constant but **the budget**, by `SUMMARY_LINES` at
`bullet_budget`, which is where a new element's cost belongs. `calibration.md` is explicit that a
constant change is *"a selection event, not a layout tweak"*; this is a selection event that arrives
as an overhead line rather than as a moved constant, and the auxo-ai re-run in §"The cost" is what
it looks like on a real page.

## Rejected

**A `\section{Summary}` heading.** §1. Two lines for a word, on a page where two lines is two pieces
of evidence. **Reversed on 2026-08-11 — see the Addendum.**

**Three typeset lines.** More keywords, and the honest trade is a third Bullet. Two lines already
holds every Must-have term this bank can support; the third would be spent on terms it cannot, which
is §2's forbidden direction wearing a length argument.

**Letting the Summary carry a figure — `~17.5 hours a month` at the top of the page.** The most
persuasive number this bank holds, and it is refused for §4's reason. Note what the design does
instead: the figure is not lost, it is on `american-express`'s lead where it traces. If this ever
becomes intolerable the reopening is a **cited** Summary — `## Summary` carrying a claim ref, run
through `check_number_trace` like anything else — never an uncited figure.

**Letting the Skills rows do this job by widening their labels.** Considered because the rows are
already the page's keyword real estate (`0020`) and already carry the posting's vocabulary in their
labels. Refused: a row is a **breadth list**, every skill on it is backed by a cited Claim
(`check_skills_trace`), and the terms this decision is about are exactly the ones with no Claim to
cite. Loosening that would put unbacked skills in the one place on the page where every item is
currently traceable — a far larger hole than the one being opened, and in the wrong element.

**Making the Summary optional, or letting the model withhold it.** §5. The Packer cannot see it.

**A per-run objective naming the company** — *"seeking an AI Engineer role at AuxoAI"*. It is what
the relaxation's slippery slope ends at, and it is `0027` §4's failure with the whole page's most
valuable line in it: a sentence that tells the reader nothing about the candidate and exists only to
be matched. The Summary says what the candidate is. It never says what the candidate wants, and it
never names the employer being applied to.

**A trace check over the Summary's prose.** There is no seam to check it at: it cites nothing by
design (§4), and a check that resolved its phrases against the whole bank would pass anything the
bank happens to mention anywhere. The Summary's truth is defended where the rest of the page's prose
truth is defended — the skill's rule 2, the cold read at §5.05, and the maker in the interview. What
is mechanically checked is what can be: no figures, the length, the fit, the spelling convention,
and its presence.

## The cost, stated rather than waved past

**Two lines of evidence, every run, on every page.** `runs/auxo-ai` had `Spent 32, 0 left` — the
budget was exactly full. At 30 the Packer's `grant_widths` pass is where the two lines come from: it
had `3 line(s) left after the Bullets were seated` and granted second lines to
`american-express/c6`, `xlscout/c1` and `auto-apply/c1`. On the re-run it has 1, and the allocation
says so: *"2 claim(s) asked and were written to one line: `xlscout/c1`, `auto-apply/c1`"*.

**No Bullet leaves the page and no entry loses its slot** — which is luck, not design. What the two
lines actually cost is detail inside two sentences: `xlscout/c1` keeps *unasked* and its `~95%` and
loses the layout fixes; `auto-apply/c1` keeps the check and loses the one-way provenance clause.
On a tighter bank the same two lines come out of Bullets instead, and `0025`'s rule decides which:
evidence outranks room. The re-run's page also had to find a fifth short Bullet to keep `0030`'s
spread — fourteen one-line Bullets need five at or under 88 where twelve needed four — which is the
second-order cost nobody would predict from *two lines*.

**The relaxation is not checkable, and that is a real hole.** Every other constraint on this page's
prose is either mechanical or scoped to a citation. §2's line between re-naming and re-scoping is a
judgement, made by the same model that benefits from blurring it, defended only by the cold read and
the maker. It is the largest unchecked surface this system has, and it is on the most-read line of
the page. The mitigation is that it is **bounded to one element** and that the element carries no
figures, so the worst case is an overclaimed *kind* of work rather than an invented number — but the
next output review should read this line first and hardest.

**A summary is the easiest thing on a résumé to write badly.** *"Results-driven AI professional with
a passion for leveraging cutting-edge technologies"* satisfies every rule in this ADR and says
nothing. `0027` §2 refused a fixed shape for Bullets because six in a column read as a form; there
is only one Summary, so that argument does not apply, and what replaces it is the rubric in
`tailor/SKILL.md` §5 and the cold read.

## Consequences

- **`tools/config.py`** gains `SUMMARY_LINES = 2` (fixed by decision) and `SUMMARY_CHARS = 236`
  (measured, 220). `docs/calibration.md` gains both, its measurement procedure, and a dated line.
- **`templates/resume.tex.j2`** gains `\resumeSummary`, the `summary` hole, the
  `%% AUTOAPPLY:element:summary:page` marker, and the Summary-fit instrumentation beside the
  Header-fit block it is modelled on.
- **`tools/pack.py`**: `bullet_budget` subtracts `SUMMARY_LINES`; `render_allocation` says so on the
  budget line, because a line the page spends and nobody can see spent is how a budget stops being
  auditable.
- **`tools/render.py`**: `parse_bullets` reads `## Summary`; `PageContents.summary`;
  `check_summary_length`, `check_summary_figures`, `check_summary_fit`; `page_elements` gains
  `summary:page`; `page_prose` includes it, so the spelling check covers it; `fill_template` passes
  it.
- **`tools/lengths.py`** reports the Summary against `SUMMARY_CHARS` on the same tape as the Bullets
  and the leads.
- **`tools/coverage.py`**: the Summary joins `page_surface`, named as itself rather than as a claim
  because it cites nothing. Leaving it out would report a term as missing from a page that says it
  in its first sentence — and on `auxo-ai` it is the only thing on the page carrying `AI-driven
  business copilots` and `decision-making systems` in the posting's own words. The read stays
  advisory and stays out of the sentence: a term it calls missing is never a reason to add it to
  the Summary, since whether the bank supports the term was decided when the Summary was written.
- **`bank/profile.md` and `templates/profile.example.md`** gain the optional `## Standing` block;
  `Profile` parses it; `tools/bankcheck.py` advises when it is absent and **never fails on it**.
- **`.claude/skills/tailor/SKILL.md`**: the spine gains the Summary, §5 gains its composition rules
  and the bounded relaxation, and §5.05's cold read reads it first.
- **The number trace, the spread check and the markers accounting are unchanged in what they
  demand.** The Summary is outside the spread check (it is not a Bullet, exactly as a lead is not),
  inside the spelling check, and carries no figures for the trace to have an opinion about.

---

# Addendum, 2026-08-11 — the Summary gets its heading, and the page pays for it

**Status:** accepted. Supersedes §1's *"no heading"* and the *Rejected* entry *"A `\section{Summary}`
heading"*. Everything else above stands unamended — §2's relaxation, §3's sources, §4's refusal of a
figure, §5's unconditional charge and §6's fit gate are untouched. **This changes what surrounds the
element, never what may go inside it.**

Written as an addendum rather than folded into the body, for the reason `0046`'s is: the body
records a refusal reasoned from a price, and the price was right. Rewriting §1 to read as though the
heading were always intended would erase the only thing worth keeping — that two lines of evidence
were counted first, and spent on purpose.

## A1. What §1 got right, and what it left out

§1's arithmetic was never in doubt and is unchanged: **a heading costs `SECTION_LINES = 2`, and two
lines on this page is two pieces of evidence.** What §1 argued from that price was that the heading
buys nothing — *"a human meeting a paragraph directly under a name and a contact line does not need
to be told it is a summary"*.

That is true of the paragraph and false of the page. The rendered `runs/auxo-ai` reads, top to
bottom, as: a name, a contact line, **two lines of unlabelled prose**, then `Experience`,
`Projects`, `Skills`, `Education` — four ruled headings and one block that is none of them. §1 read
the Summary as *the header's tail*, and the Template's own comment said so out loud, tuning
`\resumeSummary`'s leading `\vspace` to `-6.5pt` so the paragraph sat **17.43pt** under the contact
line — the distance a heading keeps above its own first row. The block was styled to belong to the
thing above it.

**The maker does not want it to belong to the header. It is a section of the résumé, and it is the
one the reader meets first.** That is a judgement about the document rather than a defect in §1's
reasoning, and it is the maker's to make. §1's price stands; the maker has paid it.

## A2. The heading is a `\section`, not a lookalike

The same macro, the same `\titleformat`, the same `\large \scshape` and the same rule, at the same
measured **23.86pt**. Nothing in the Template is special-cased for it, and `SECTION_LINES` gains a
fifth call site rather than a twin — which is the rule `config.py` states for
`ENTRY_HEADER_LINES` and applied here without argument, since the heading *is* the element already
charged.

It is charged **unconditionally**, which is the one way it differs from the four headings the budget
already counted. Experience, Projects and Education are charged when the page holds that kind of
content, and Skills charges its own heading inside `skills_charge` because whether it has one is a
fact about what was composed. `\section{Summary}` is on every page that renders, for §5's reason
exactly — so `bullet_budget` adds it flat, beside `HEADER_LINES` and `SUMMARY_LINES`.

## A3. The spacing, and the 3pt that turned out to be the header's

The page has a spacing grammar and it was measured before anything moved. Read off the compiled
`runs/auxo-ai`, baseline to baseline:

| gap | measured |
|---|---|
| above the `Experience` heading | 24.91pt |
| above `Projects` | 24.97pt |
| above `Skills` | 23.91pt |
| above `Education` | 24.41pt |
| `Skills` heading → its first row | 17.33pt |
| `Experience` heading → its first Entry header | 17.90pt |

Dropped in with nothing tuned, the new heading landed **27.70pt** under the contact line — 3pt
looser than any other heading on the page — while the paragraph under it sat at **17.32pt**, dead on
the grammar with no tuning at all, because that distance is now set by the heading's own after-skip
rather than by a `\vspace`.

**So the tuning went the other way from §1's.** `\resumeSummary`'s leading `\vspace{-6.5pt}` is
**gone**, not re-aimed: it existed to pull a heading-less paragraph up to a heading's first-row
distance, and there is a heading now. What it was really absorbing was `\end{center}`'s own trailing
glue, and that is trimmed where it is generated — `\headerContactLine\vspace{-3pt}`, inside the
centre box. The trailing `\vspace{-1.5pt}` is unchanged and still measured: it puts the `Experience`
rule **24.91pt** under the Summary's last baseline, the same number it had before.

**The trim has to be inside the centre box, and that is a fact about `\addvspace` rather than a
preference.** `\section` contributes its space with `\addvspace`, which **merges** with the skip
already on the vertical list instead of adding to it. Anything placed between `\end{center}` and the
heading stops the merge and makes the two add: measured, a bare `\vspace{0pt}` in that gap costs
**+11.96pt**, and `\vspace{-3pt}` costs +8.96pt. Inside the box the merge is untouched and `-3pt`
means `-3pt`.

The page as it now renders:

```
name                     -> contact line          12.95pt
contact line             -> Summary rule          24.71pt   (grammar: 23.91-24.97)
Summary rule             -> Summary's first line  17.33pt   (grammar: 17.33 / 17.90)
Summary's last line      -> Experience rule       24.91pt   (unchanged)
```

## A4. The probe ran, and `PAGE_LINES` moved for the first time on anything but the paper

`RESULT: constants hold`. Every element height is identical to the scaled point — one Bullet line
14.00pt, an Entry header 27.84pt, a section heading 23.86pt, an Education row 27.28pt, both Skills
figures — and every width is unchanged, so `CHARS_PER_BULLET 99`, `BOLD_CHARS_PER_BULLET 80`,
`LEAD_CHARS 114`, `BOLD_LEAD_CHARS 80` and `SUMMARY_CHARS 220` all hold. Three things moved:

**`HEADER_LINES` is unmoved at 3 and its measurement is 33.91pt where it was 36.91pt.** The 3pt trim
is inside the header, so the differential charges it there — which is also where it belongs. The
header was the loose thing; the first heading under it is only what revealed it.

**`PAGE_LINES` is 54 where it was 53, and the page did not grow.** The sweep's rule is unchanged:
the smallest implied value wins. Four of the seven shapes already implied 54 and the three crowded
ones — `(4,3)`, `(5,2)`, `(6,1)` — implied 53; the 3pt the header gave back is what carried those
three over. All seven agree now, and slack is 0 on every shape rather than +1 on four of them.

**The Summary's own height is now priced with its heading, and cannot honestly be priced without
it.** `\addvspace` merges the glue between the two, so neither half stands alone: cut only the
paragraph and `\section{Summary}` welds to `\section{Experience}`, where the two headings' skips
merge and the differential reads **38.00pt** for a block nowhere near that; cut only the heading and
the paragraph lands on the header's glue instead. So `SUMMARY_BLOCK` removes the pair and the check
is against the pair — **54.39pt against `(SUMMARY_LINES + SECTION_LINES) x 14.00 = 56.00pt`**,
replacing *a two-line Summary costs no more than two Bullet lines*. The Summary-fit gate is
untouched, because it reads a `\parbox` height and no glue: 20.89pt ≤ 28.00pt < 32.89pt, as before.

## A5. The cost, stated rather than waved past

**One line of evidence, every run, on every page.** The heading costs 2 and the page gained 1.
Re-packed against today's other constants, `runs/auxo-ai` goes from `Spent 32, 0 left` to
`Spent 31`, and the allocation says where it went: the **Room** line had 3 and now has 2, so
`american-express/c6` and `xlscout/c1` keep their second lines and **`auto-apply/c1` asks for two
and is written to one**. That is `0025`'s rule doing what it does — the line comes out of
`grant_widths`, so what is lost is detail inside a sentence rather than a Bullet, until the bank is
tight enough that it is a Bullet.

**This is a selection event under `config.py`'s own rule**, and it is committed on its own with
nothing bundled into it. `docs/calibration.md`'s entry for this date holds the sweep and the two
checks that changed.

## Consequences

- **`templates/resume.tex.j2`**: `\section{Summary}` above the block; the
  `%% AUTOAPPLY:element:summary:page` marker moves under the heading, since the heading is a fixed
  string that cannot overflow; `\resumeSummary` loses its leading `\vspace` and keeps the trailing
  one; `\headerContactLine` gains `\vspace{-3pt}` inside the centre box.
- **`tools/config.py`**: `PAGE_LINES` 53 → 54; `HEADER_LINES`, `SECTION_LINES` and `SUMMARY_LINES`
  keep their values and gain the reasoning above. **No new constant** — the heading is a `\section`.
- **`tools/pack.py`**: `bullet_budget` subtracts a flat `SECTION_LINES` for the Summary heading, and
  the allocation's `Summary:` line says so, because a line the page spends that nobody can see spent
  is how a budget stops being auditable.
- **`tools/bankcheck.py`**: the static-profile price line reads `Summary 4` — the prose plus its
  heading — because that is what the Packer takes off.
- **`tests/calibration/probe.py`**: `SUMMARY_CALL` becomes `SUMMARY_BLOCK` and cuts the heading with
  the prose; the Summary check is against `SECTION_LINES + SUMMARY_LINES`; `predict_bullet_capacity`
  charges the heading flat.
