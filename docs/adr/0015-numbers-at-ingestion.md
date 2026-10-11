# Numbers and provenance at the ingestion interview

**Status:** accepted

## Context

`0003` fixed the **model**: two **Provenance** tiers (**measured** / **estimated**), a separate
hand-set **Confidence flag**, the **"So what?" test**, no qualitative tags and strong prose instead.
`0004` and `0005` gave the Claim the fields (`number`, `provenance`, `confidence`) and their on-disk
form. `0014` fixed the **shape** of the session those fields get filled in — wide-then-deep, no
question cap, incremental write, review by diff.

What was never designed is the **mechanism**: how the interview actually gets a number, its tier, and
the maker's doubt out of the maker, without turning every claim into an interrogation. Resolved in
issue #19.

The stakes are asymmetric and worth stating once. The **Number-trace check** enforces
*equal-or-softer* only, so an estimate wrongly recorded as measured renders flat and hard forever and
**nothing downstream can catch it** — ingestion has no lint. Everything below leans on that asymmetry.

The organising finding: **none of the five sub-questions needed new machinery.** Each resolved into a
placement or a register decision inside `0014`'s depth pass, and three resolved the *same* way — by
pointing a question the interview already asks at the number, rather than adding a question about it.

## Decision

### The tier is a by-product, not a question

**Provenance is not asked. It falls out of a question the interview is already asking.**

`0014`'s **Excavating pressure** already includes *"how did you know it worked?"* Its answer very
nearly *is* the provenance: *"we had a Grafana panel on it"* is measured, *"everyone stopped
complaining"* is estimated. In the common case the tier is recorded without a provenance question ever
being asked.

Where the answer genuinely leaves it open, the agent asks **one** plain follow-up in the maker's
register — *"did you clock that, or is that your read of it?"* — and **takes the answer**. `0014`
already fixed that the maker's word on a tier is taken, not adjudicated.

Asking per number was rejected as the interrogation register `0014` banned, repeated eight times a
session. Inferring the tier from the source and asking for confirmation was rejected because it only
works where a source exists, which is essentially never on the job half of the bank.

**The fallback is `estimated`.** Where the tier is still unresolved — the maker shrugs, the session
ends mid-claim, the number arrived sideways — the recorded tier is estimated. This is not a coin
flip; the two errors are not the same size. A wrongly-estimated number costs a `~` and some
competitive strength. A wrongly-measured one is a hard, fabricated-in-effect claim that renders flat,
passes every lint, and is never revisited.

### The "So what?" test is a redirect, not a gate

`0003` framed the test as a **refusal**: an empty number "survives only if it connects to a genuine
consequence, else it is cut to qualitative prose or dropped." That framing came from the threat model
`0014` corrected. **It is re-framed here as a redirect.**

*"10,000 lines of code"* is almost never padding. It is the maker reaching for the nearest number
because the one that mattered is not in reach yet — which is **compression**, the exact thing the
interview exists to fight. So a number failing the test is not a verdict to deliver. It is the
loudest available signal that the excavation is not finished, and it is the most grounded question in
the session: *"10k lines — what did all that code let people do?"*

Three landings, by what the dig produces:

- **A consequence-bearing figure** — that becomes the `number`, and the empty one is simply never
  written.
- **Prose about what changed, but no figure** — the claim lands qualitative. This is the normal
  healthy case: `0009` already fixed that a missing number is **not** a shallowness defect.
- **Nothing** — the claim is at the **Parking** boundary already, because *"never says what changed"*
  is the shallowness check an empty number fails by definition. It lands marked `needs-interview`.

If the maker still wants the figure in after the dig comes up empty, the agent says so plainly once —
the move `0014` already licensed at Parking, naming the gap rather than quietly overruling — and then
takes their answer. The figure stays out of the `number` field regardless, because it would render
flat, trace clean, pass every lint and make the page worse; it is admissible as scale texture inside
the prose where it genuinely conveys size.

**The number is what fails the test, never the claim.** Cutting a figure never cuts the work it was
attached to.

### Doubt is raised by a hedge, never by a schedule

The **Confidence flag** is hand-set (`0003`) and is the only thing that escalates a claim to the
**Checkpoint**. So the maker must set it — but the maker will never reach for a field they cannot
see, and the obvious prompt, *"are you sure?"*, is banned **by name** in `0014` as unanswerable.

**The trigger is a hedge the agent hears, not a question it schedules.** *"I think it was 40%, could
have been 30."* · *"Don't quote me."* · *"That's the number we gave the VP, anyway."* The maker has
already raised the doubt; the agent's only job is to stop it evaporating. It then asks one question
that *is* answerable, because it is grounded in something actually said: *"you sounded unsure on the
40% — want me to mark it, so it gets a second look before it goes on a page?"*

**The agent proposes, the maker calls it** — the same shape as Parking (`0014`) and identity
confirmation (`0012`). Hand-set survives intact.

This also *explains* the orthogonality `0003` asserted rather than restating it: a confidently
remembered estimate produces no hedge and is never flagged, while a hesitantly recalled dashboard
reading produces one and is. Provenance never enters into it.

Two boundaries hold this in place:

- **The flag is not only for numbers.** `0004` hung `confidence` on the Claim, not the number, so
  *"I'm fairly sure I was the one who pushed for that, but it might have been Raj"* is flaggable with
  no figure anywhere near it. Same trigger.
- **A parked claim is never automatically flagged.** The two marks look adjacent and are not:
  `needs-interview` means *thin, not yet excavated* — agent-set, a session event, and at tailoring
  only a notification (`0009`). `confidence: uncertain` means *the maker doubts the substance* —
  maker-set, and it fires a **Fork** that interrupts a run. Parking is the agent admitting it could
  not dig; that is not the maker expressing doubt. Conflating them would hang a checkpoint fork off
  every thin claim in the bank and destroy the conditional path `0003` protected.

### Mush is thinness; the fix is another question

`0003` put the whole weight of the no-qualitative-tags decision on "the interview refusing mush",
with the example *"led the migration"* → *"sole owner of the 6-service migration, no team, tight
deadline."* **That needs no separate mechanism**, and the reason changes what the answer is: every
word the fix added — *sole owner*, *6 services*, *no team*, *tight deadline* — is a **fact that got
dug out**. None of it is better writing.

So **mush is not a defect alongside thinness; it is what thinness looks like before anyone has
asked**, and `0014` already decided the cure — Excavating pressure, ending at `0009`'s checks or at
Parking. An empty phrase and an empty number are the same object: *"improved code quality"* is
*"10,000 lines of code"* without the digits, and it gets the redirect above.

One rule here **is** new, because **Write as you go** put the agent in charge of the wording:

> **The fix for mush is another question, never a better sentence.**

The agent hears *"led the migration"* and the cheapest repair is to write it up nicely. That produces
a claim the maker never made, in the one place with no lint, and it reads *better* than the honest
version, so nothing will ever flag it. `0014` licensed transcription, so tightening a rambling answer
into a clean sentence is fine. **No fact may appear in the entry file that was not spoken.** "Tight
deadline" goes in because the maker said it was tight — never because migrations usually are.

Where the maker genuinely has only mush, there is no new path: that is Parking.

### A lifted figure is a lead, not a record

`0013` permits **lifting**: a design doc or README that *states* an outcome is the maker's own words
and is admissible as **Evidence**. But nothing in the doc says whether *"reduced p99 latency by 40%"*
came off a dashboard or was a ballpark typed while writing the doc. **Lifting under-determines the
tier**, because the tier is not a thing the source's words contain.

**The agent raises every lifted figure rather than absorbing it, and what gets written is the maker's
answer, not the doc's sentence.** *"Your README says you cut p99 40% — was that off the dashboard, or
a ballpark at the time?"*

The argument is `0013`'s own no-drafting argument one level down. Silently absorbing the figure is
exactly *"the agent reads a commit saying `perf: cut p99`, writes it up, and the maker skims it and
thinks yeah, that's about right"* — except it slips through more easily, because the number is real
and the trace resolves clean.

Raising it is also strictly better *ignoring* safety, because a stated outcome is the most grounded
question available in a session, and the answers it produces are the ones ingestion exists for:
*"yeah, and it held for six months"* · *"that was before the second pass, it ended up closer to 60"* ·
*"honestly that number was optimistic, we never re-ran it."* The last is the interview working — a
number that would have gone on a résumé and had to be defended in a room, dying at the only gate that
could have killed it.

The source's **sentence** still lands as Evidence under `0013`, unchanged. What routes through the
maker is the **figure becoming claimable**, because that is what render spends and what the
**Number-trace check** adjudicates, and its tier can come from nowhere else.

## Considered options (rejected)

- **Asking the tier per number** ("measured or estimated?") — rejected: it is the interrogating
  register `0014` banned, eight times a session, and it trains the reflexive answer.
- **Inferring the tier from the source and asking for confirmation** — rejected: it only works where
  a source exists, which excludes the entire job half of the bank.
- **Refusing to store a number whose tier is unresolved** — rejected: it deletes real material to
  avoid a mislabel, when `estimated` already caps the damage at a `~`.
- **Defaulting an unresolved tier to `measured`** — rejected on the asymmetry: it is the one error
  with no downstream detector and no recovery.
- **The "So what?" test as `0003`'s gate** (judge the number, cut it, move on) — rejected: it throws
  away the session's most grounded remaining question and puts the agent back in the adjudicator's
  chair the corrected threat model removed it from.
- **Asking "how solid is that?" on every number** — rejected for the reason `0003` rejected
  auto-firing the flag on *estimated*: it floods the checkpoint's upstream, trains reflexive
  approval, and destroys the conditional path.
- **Never prompting the Confidence flag at all** (purely volunteered) — rejected: faithful to
  "hand-set" and useless, since nothing in the session surfaces the field's existence.
- **Parking auto-setting the Confidence flag** — rejected: it conflates the agent's failure to
  excavate with the maker's doubt, and would hang a run-interrupting Fork off every thin claim.
- **A fourth shallowness check for mush** — rejected: `0009` said *only three* deliberately, it would
  overlap the re-angle check almost entirely, and unlike the other three it has no statable form —
  "is this vague?" is not a check.
- **The agent improving mushy prose at write-out** — rejected: it manufactures facts in the one place
  with no lint, and the result reads better than the honest version, so nothing flags it.
- **Lifted numbers default to `estimated` with no question** — rejected: it systematically softens
  the strongest numbers in the bank, since a committed benchmark is as measured as anything gets.
- **Inferring a lifted number's tier from the kind of source** (benchmark → measured, README →
  estimated) — rejected: `0013`'s source taxonomy climbing back in through the numbers, and wrong in
  both directions — a README often quotes a real benchmark, a checked-in benchmark is often a toy.

## Consequences

- **Re-frames `0003`'s "So what?" test** from a refusal into a redirect. The test still has no
  automated detector and the interview is still the only gate; what changes is that a failing number
  becomes the next question rather than a verdict, with three defined landings.
- **Completes `0003`'s Confidence flag** with the one thing it lacked — a trigger. Hand-set is
  preserved: the agent proposes on a heard hedge, the maker calls it.
- **Separates `confidence: uncertain` from `needs-interview` explicitly.** Agent-set thinness never
  becomes maker-set doubt, so `0009`'s notification never silently becomes `0002`'s Fork.
- **Extends `0013`'s lift rule to numbers.** A source's sentence may be lifted as Evidence; a figure
  becomes claimable only through the maker, because its tier exists nowhere in the source.
- **Adds no field, no marker and no lint.** Every sub-question resolved into placement and register
  inside `0014`'s depth pass. `0004`'s three fields are unchanged and the **Number-trace check** is
  untouched.
- **Confirms that a missing number is not a defect** (`0009`) from the other side: the redirect's
  most common landing is a qualitative claim.
- **Build-time residuals:** telling a real hedge from a verbal tic (*"I guess"*, *"kind of"*); the
  wording of the provenance follow-up and the flag offer. Calibration, same bucket as `0014`'s angle
  list.
