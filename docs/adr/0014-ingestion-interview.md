# The ingestion interview: what it asks, how it pushes, and when it stops

**Status:** accepted

## Context

`0013` fixed the **shape** ingestion sits inside — one session/one entry, facts-then-claims, **lift
never manufacture**, one **Checkable source** binary, the résumé as a checklist only — and
deliberately left the interview itself undecided. This ADR decides it: what a session asks, in what
order, how hard it pushes, how it knows a claim is finished, and when the session ends.

Grilling this ticket did something the other ingestion questions did not: it **corrected `0013`'s
threat model**. The shape ADR assumed the danger at ingestion was inflation — the maker's claim
drifting upward with no lint to catch it — and built the **Checkable source** binary as the
counter-pressure. The maker rejected that framing outright: *"my word can be taken as source of
truth, I am not going to lie on my own resume."* Single-user, single-reader, and the person who
would pay for an inflated claim is the person sitting in the interview room defending it. The
pressure the maker actually wants is **memory-jogging, not verification** — *"to have be questioned
around those points so it helps me jog my memory and give you the detail."*

That correction, plus the observation that git authorship is worthless here (sole committer on
personal projects; work repos live behind a company account the agent will never see), demoted most
of what the binary was carrying. The decisions below are built on the corrected model.

## Decision

### Wide first, and the merge is the point

A session runs **wide, then deep**. After the read, the agent establishes the *list* of pieces of
work worth claiming before digging into any of them; then each item is excavated in turn.

The wide pass draws from **two lists merged** — what the maker volunteers, and what the read
surfaced that they did not mention. The merge is the load-bearing half, not the maker's list.
`0013` warned that a self-written summary is a floor because it hands back the maker's own words;
**a summary spoken aloud in the first two minutes of a session is the same floor**. Digging only
the volunteered list caps the entry at what the maker happened to recall, which is the résumé-seeding
failure at a slower pace.

Wide-first also gives the session a knowable size before any excavation starts, which is what makes
the stopping condition below work without a budget.

Deep-as-you-go (grab the best thread, dig, then ask "what else?") is rejected: it never knows how
much is left, and it makes the write-out and the stopping condition both undecidable.

### The read names work; it never extracts impact

A fact earns its place in the read if it can **name a piece of work**, so a question can point at
something specific. Reading for comprehension is not the job.

**Authorship and timelines are dropped from the read.** They ground nothing here: a personal project
has one committer by definition, so *"you shipped this in six weeks"* claims nothing, and a
shared work repo is inaccessible. What the read pulls instead is **substance** — what the thing
does, what it talks to, what is actually in it, and any place the source's own prose *states* an
outcome (README, design doc, CHANGELOG, a committed benchmark), which `0013` admits as liftable
**Evidence**.

**The read cannot extract impact.** A repo shows what was built; *"cut p99 40%"* is not derivable
from the existence of a cache package — that is the manufacture case, in the one place with no lint
behind it. What the read can do is pin down what was built precisely enough that the impact question
has something to bite on. Impact comes out of the maker's mouth, always.

### Pushback is excavation, not verification

Where nothing can check an answer — which is nearly everywhere, and covers the entire job half of
the bank — the pressure is **demanding the surrounding detail**: who asked for it, what was in place
before, what broke, who pushed back, how you knew it worked, what you would have done with another
month.

The register is **jogging, not interrogating**. *"Are you sure?"* is unanswerable and is not asked.
The questions are specific and grounded because vague ones jog nothing. A thin memory runs out of
texture fast and a real one keeps producing specifics — so the same mechanism that surfaces detail
also, incidentally, marks the claims that could not hold it up. That side effect is not the design
goal and is never reported as one.

The case with no external check needs **more** excavation, not less. Treating it as degraded and
asking fewer questions inverts the whole thing.

### The Checkable source binary is recut

`0013`'s binary — *can this source check me?* — is **corrected to: can this source tell me something
the maker has not?**

The useful half survives intact. A repo can hold work the maker forgot and specifics they would
never recall unprompted; a summary they wrote cannot, by construction — which is precisely why
`0013` called it a floor. That half is what makes the merge worth doing and what the near-empty
source smell actually measures. The trust half is gone with the threat model that motivated it.

**A mismatch is a question, never a verdict.** The claim says retry logic; the repo has no retry
path. Under the old frame that was the source arguing back. Under the corrected one it is simply
worth asking — *"I don't see a retry path in here, different repo or did it get ripped out?"* — asked
because it is usually informative. The maker's answer settles it. The agent never overrides them and
**the discrepancy is never recorded**.

### Nothing records that a claim rests on memory alone

`0013` imposed a duty: where a source cannot check the agent, the agent **says so**. That duty now
fires on nearly every entry, so as a written marker it is deleted.

The decisive reason is not noise, it is **suppression**. `0003` deliberately separated **Provenance**
(how solid a number is) from the **Confidence flag** (hand-set doubt). A field that is neither but
*reads* like doubt gets treated as doubt by the session that finds it later, and a future agent
weighing a claim marked *unbacked* will quietly skip it. It is a field that can only ever lose the
maker slots and can never win one — with no consumer in `0004`'s schema, no test in `0009`'s
shallowness checks, and no possible lint.

What survives is the **live** version, spoken and not written: when the agent asks something the
source could have answered and cannot, it says so once in the session — a cue to dig, aimed at the
maker, in the moment.

Recording it as a Claim field so a later session knows which claims were unbacked is rejected on the
same ground, plus `0008`'s: a mark with no mechanical effect earns its place only when a later
session drains it, which `needs-interview` does and this would not.

### Angles open the wide pass when the source is thin

For a job entry the source is often two paragraphs the maker wrote, and a strictly source-grounded
wide pass degenerates into *"so what did you do there?"* — unaided recall, in the case that matters
most.

The agent therefore carries a small set of **angles** to open the wide pass with when the source
cannot populate it: what you owned end to end · what you were brought in to fix · what was in place
before you · what broke or nearly broke · what you argued for and lost · what someone else now
depends on · what you would redo. Their justification is the maker's own: not that the source cannot
check them, but that they will forget things and a prompt surfaces them.

Two guardrails keep this from rotting into a form — `CONTEXT.md` avoids "questionnaire" and "intake
form" deliberately:

- **Angles populate the list; they never ask the claim.** Once a piece of work is on the table, the
  digging is grounded in *that work*. The angle has done its job and is not asked again. Angles that
  surface nothing are dropped in a sentence.
- **They are a fallback for thin sources, not a fixed opening.** A session with a real repo opens on
  what the repo showed; reaching for a generic list there wastes the only thing that grounds it.

**Anything the maker raises is admissible even where the source is silent.** *"I ran the on-call
rotation"* belongs in the entry with no backing at all. `0013` bans manufacturing a claim *from* a
source; it never required a source to license one.

### A claim ends when the agent names the gap and the maker calls it

Each claim ends either by clearing `0009`'s **Shallowness checks** or by being **parked**.

Parking is an explicit interaction, not a silent agent decision. After a couple of unproductive
follow-ups the agent **names the specific check it cannot clear** and offers to park: *"I have that
you built the ingest pipeline and roughly how, but nothing about what changed for anyone — so it
will lose to every JD. Park it, or try a different angle?"*

Three reasons the gap is named out loud:

- Naming the missing thing is often what unlocks the memory — a last, sharper question wearing an
  admission's clothes.
- The claim is still **written**, with whatever was gathered, marked `needs-interview`. `0009` fixed
  that a shallow claim beats no claim; parking never discards material.
- It makes the mark an **event in the session**, which `0008` requires and which #20's return door
  needs in order to know what it is reopening.

The maker may end a claim at any time by saying that is all they have. **The agent gets exactly one
more try, then accepts it.** Fatigue and genuine emptiness are indistinguishable from the outside,
and a tool that re-asks after the maker has said they are done is one they stop opening.

*Accepted cost:* claims get parked that a more stubborn agent might have cracked on the fourth try.
The **Return door** exists for exactly those.

### No question cap

The map's original instinct was a hard cap — roughly a dozen questions per entry, never forty. It is
dropped, and wide-first is what makes it unnecessary: the session ends when **every item on the
merged list has landed as a claim or been parked**. Question count is a result, not a budget.

A cap misfires in both directions. On a rich project it truncates mid-excavation — hardest exactly
where the material is best, which is where the résumé needs it most. On an empty one it never binds,
because the session already ran out of things to ask. And a fixed number invites rationing: three
claims left and four questions in the tank means the shallow version of each.

Two things take its place:

- **A stretch check at claim boundaries, never mid-claim** — *"four down, three left on the list;
  keep going or park the rest?"* This handles fatigue, which is what the cap was actually protecting
  against, without truncating anything by arithmetic.
- **The count becomes a smell reported at the end, not a limit.** Two are worth saying: *this entry
  has two claims, thin by `0009`'s own check*, and *the source gave up nothing you had not already
  told me* — the second being the sign that what the maker pointed at was a summary of theirs
  wearing a repo's clothes.

*Accepted cost:* a genuinely rich project can run long. `0013` already made ingestion's budget
generous — one sitting per project, interrupting nothing — and the maker can stop at any boundary.

### Write as you go; review is a diff

Each claim is written into the **Entry file** the moment it settles or is parked. Entry frontmatter
(id, type, title, org, dates, domain) is written once at the end of the wide pass, when it is known.

Incremental write-out falls out of the two decisions above. The maker can stop at any claim boundary,
so a write-at-the-end would either lose the session or need resume machinery that does not exist.
Written as it goes, a half-finished session is not a broken state — it is an entry with fewer claims,
which `0009`'s **Shallow entry** check already flags and the **Return door** already knows how to
reopen. A session that dies on context also does not take the excavation with it.

This does not collide with `0013`'s no-drafting rule. What is banned is arriving with claims the
maker never said; writing down what they *did* say, as they say it, is transcription.

**The review is `git diff`, not a read-back in chat.** The maker reads the entry file and, where it
is off, **edits** it. `0013` deliberately kept the maker as author rather than approver, and a
chat read-back quietly returns them to the approver's chair: a wall of text at the end of a long
session, and *"yeah, that's about right"* is the exact nod that made drafting dangerous. Editing a
file is a different act from agreeing to one — and `0005` already made the bank hand-edited markdown
in git, so the diff is the honest surface.

*Accepted cost:* the file is briefly inconsistent mid-session and an abandoned session leaves a
partial entry in the bank. Both are cheap: it is a markdown file, and it is in git.

## Considered options (rejected)

- **Deep-as-you-go** (dig the best thread, then ask what else) — rejected: it never knows how much
  is left, which leaves both the stopping condition and the write-out undecidable.
- **A wide pass over the maker's list alone** — rejected: the spoken summary is the same floor as the
  written one, so the entry's ceiling becomes two minutes of recall.
- **Reading git authorship and timelines** — rejected as worthless *here*: sole committer on personal
  projects, inaccessible on work repos. Substance replaces it.
- **Inferring impact from what was built** — rejected: `0013`'s manufacture case, in the one place
  with no lint behind it.
- **Verification-flavoured pushback** ("git says you never touched that package" as a challenge) —
  rejected with the threat model it came from. The maker is the only reader and the one who defends
  the claim; the pressure jogs rather than audits, and a mismatch is asked, not asserted.
- **Recording that a claim rests on memory alone** — rejected: no consumer, and worse than useless,
  since a marker that reads like doubt gets treated as doubt and suppresses the claim.
- **Angles as a fixed opening for every session** — rejected: it wastes the grounding a real source
  provides and is the questionnaire the glossary avoids.
- **The agent parking a claim silently** — rejected: naming the gap is itself the sharpest remaining
  question, and the mark must be an event `0008` and #20 can see.
- **A hard question cap** — rejected: it truncates exactly where the material is richest, never binds
  where it would help, and invites rationing. Replaced by list exhaustion, a boundary stretch check,
  and a reported smell.
- **Writing the Entry file once at the end** — rejected: it makes stopping lossy and needs resume
  machinery.
- **A chat read-back for approval** — rejected: it converts the maker from author to approver at the
  one point in the system with no lint.

## Consequences

- **Corrects `0013`'s threat model.** Ingestion's pressure is memory-jogging, not inflation-catching.
  The **Checkable source** binary is recut from *can this source check me?* to *can this source tell
  me something the maker has not?*, and the "say so where it cannot check" duty becomes a spoken cue
  rather than a written marker.
- **Corrects `0013`'s reading of a repo.** Authorship and dates are not read; substance and stated
  outcomes are.
- **Confirms `0009`'s finish line** and gives it an interaction: the agent names the failing check
  and offers to park, the maker calls it, the claim lands marked.
- **Constrains #19 (numbers and provenance).** The interview's shape is fixed — wide-then-deep,
  no cap, incremental write, diff review — so eliciting a number, its **Provenance** and the
  **Confidence flag** happens inside the depth pass on a claim, and the corrected threat model applies
  there too: the maker's answer on a tier is taken, not adjudicated.
- **Constrains #20 (the return door).** Parking is a session event; a half-finished entry is a
  normal state, not a broken one; the return door inherits the same wide-then-deep spine.
- **Build-time residuals:** the exact angle list and its wording; the phrasing of the stretch check;
  what "a couple of unproductive follow-ups" means in practice. All calibration, not design.
