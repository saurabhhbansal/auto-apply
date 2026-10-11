# The return door: what it opens on, and what a merge is

**Status:** accepted

## Context

`0013` fixed that there is **one Return door** into an existing Entry and that it may **amend, never
regenerate** — new claims append with new ids, existing claims are edited in place, nothing is
renumbered. It deliberately did not decide how the door behaves once opened.

Three things were left owed to this ticket. `0008` created the `needs-interview` mark and said its
single consumer is "a later ingestion session", without deciding what that session does or what
clears the mark. `0009` handed ingestion a **merge duty** in one line — answering a shallow-gap
notification mid-run writes a **new claim**, never an append, so the bank ends up holding two claims
circling the same work — and called merging "exactly what draining the mark is for" without saying
what a merge is. `0014` fixed the interview's spine and noted only that the return door inherits it.

The merge is the sharp part, because **Claim ids are frozen and cited by every past run**. If two
claims must become one and no id may be renumbered, it is not obvious that a merge is expressible at
all.

## Decision

### The door opens on a readout of what it can see

The maker invokes `ingest` against an Entry that exists. The agent opens the **Entry file**, greps
its `needs-interview` marks, and **shows what is sitting there** — *"Acme has 6 claims; c2 and c5 are
marked. What are we here for?"* The maker answers, and that answer is the opening.

The split is that the agent shows what it can see and the maker supplies what it cannot. Of `0013`'s
three triggers only one is visible in the file: **new work** is known to nobody but the maker, and a
**Gap report** line naming a claim is something they arrive already holding. So the agent cannot work
out why the session was opened — but it can lay out the marks, which is the only reason the queue is
drainable at all. Nobody remembers which claims were left owed three weeks ago.

The agent does **not** re-run `0009`'s recurrence view over `runs/*/gaps.md` to find its own reasons.
That is `bank-audit`'s pass, deliberately standalone and read-only, and duplicating it inside the one
skill whose job is writing claims is the erosion-by-proximity `0013` separated them to avoid.

### One mode, and what differs is whether the wide pass runs

`0013` fixed the three triggers as one mode. This is the whole of what differs between them:

- **New work at the same job** → the full spine of `0014`. The read, the **wide pass**, then digging
  each item. The source is whatever the maker points at *now*.
- **Deepening a marked claim, or one a Gap report keeps flagging** → no read, no wide pass. Straight
  into the depth pass on the named claims.

Skipping the read when deepening is not a saving, it is a correction. The read's job is to **name a
piece of work** so a question has something to bite on; that job is already done — the claim is
sitting there naming it. What a marked claim lacks is **what changed for anyone**, and `0014` was
explicit that no source holds that and that inferring it is the manufacture case in the one place
with no lint behind it. Re-reading the repo to deepen `c2` spends the session's opening stretch on
the one thing the source structurally cannot give.

Running the full spine for new work is equally forced. `0014` made the wide pass **two lists merged**
because a summary spoken aloud in the first two minutes is the same floor as a written one; new work
ingested off unaided recall is that failure at a slower pace.

Two source states fall out. A source that has **moved on** — more commits since the last session —
*is* new work, and takes the new-work opening. A source that has **vanished** gets said out loud once
and the session runs on memory, which is `0014`'s spoken cue and already the normal case for a job
entry.

### A merge: the elder id survives, the loser is deleted, nothing is renumbered

The concrete case: `gaps.md` classified *event-driven — too shallow, see `c3`*, the maker answered it
mid-run, and `0009` landed that answer as a **new** claim `c7` rather than an append. Acme now holds
two claims circling the same work.

This is not untidiness. `0006` scores an Entry as the **mean of its top 3 claims** and grants it
`min(3, claims ≥ 0.50)` slots, so two near-duplicates that both score well take two of three bullet
slots on the same content *and* inflate the entry's score by counting it twice. Merging is load-bearing.

- **The agent proposes, the maker calls it.** Whether two claims circle the same work is judgement,
  and this is the shape the project already uses at **Parking**, at the **hedge trigger**, and at
  identity confirmation in `0012`. Proposing is cheap: both claims are in the file just opened.
- **Merge first, then dig once.** Otherwise the session excavates the same piece of work twice in one
  sitting.
- **The elder id survives** — the interviewed `c3`, not the volunteered `c7`. It carries the
  excavation, and being older it holds the most past citations, so killing it would break the most.
- **The loser is deleted outright, and its id is never reused.**

Deletion looks like it violates `0013` and does not, and the reason is the whole answer:

> **Deletion is loud. Renumbering is silent.**

What `0013` forbade is `c3` quietly coming to denote a different claim than the one last month's
résumé traced to — wrong, undetectable, and no lint able to notice. A deleted `c7` denotes nothing.
If anything ever resolves it, it fails in the open.

Nothing does resolve it, which is why the cost is nil. `0007` needed the citation for the
**Number-trace check**, which ran during that run and passed; `bullets.md` holds the rendered prose
itself. **A run folder is a complete record of itself** — the claim id beside a bullet is a note of
where the line came from at the time, not a live link into a mutable bank. And the deleted claim is
still in git.

**No tombstone.** A `c7 → merged into c3` line left in the Entry file would keep every old citation
resolvable to something, but nothing reads it and it is bookkeeping in a file the maker hand-edits.

`0009` explicitly **refused** to append the volunteered answer to `c3` mid-run, on the ground that it
fuses volunteered material into a properly interviewed claim and afterwards the two are inseparable.
This merge is that same move, made later, and it is permitted here for the reason the refusal named:
**the material is excavated first.** By the time it lands in `c3` it is no longer volunteered. That is
what `0009` meant in saying merging is what draining the mark is for.

### Two openings for the mark's three populations

The mark's populations (`0008`'s adds and declined forks, `0009`'s un-excavatable claims) do not need
three treatments. They need two, and the split is legible in the file:

- **A checkpoint add and a parked claim get the same pass.** Both mean *this claim is thin, dig it*.
- **A declined confidence fork is the claim carrying `confidence: uncertain` alongside the mark.** It
  is not thin and does not want excavation — it wants the correction the maker declined to state
  mid-run. `0008` fixed that the fork's answer carries no content, so the only thing that settles it
  is the maker saying the number out loud. The opening is *"you flagged the 40% on c4 — what should it
  say?"*, not *"tell me more about c4"*.

A parked claim is therefore **indistinguishable in the file** from a never-interviewed one, and the
session may re-ask angles that already came up empty. That is accepted rather than fixed.

**Parking writes nothing down.** Recording which shallowness check it could not clear is rejected on
three counts: `0009` made the checks judgeable **cold, claim against itself**, so re-deriving costs
one read of a file already open and saves nothing; written down it is a stale opinion the moment the
claim is hand-edited, which is `0005`'s derived-index ban in miniature; and it **reads like doubt** —
`0014` deleted the "rests on memory alone" marker precisely because a field that reads like doubt gets
treated as doubt by a later session and can only ever lose the claim slots.

What recovers the wasted questions is the maker, in the moment — *"we went at that one, there is
nothing there"* — after which `0014`'s rule already applies: the agent gets exactly one more try, then
accepts it. Same division as the readout: the agent shows what it can see, the maker supplies what it
cannot.

### Two events clear the mark, and clearing it does not mean the claim is good

`0009` fixed that the mark is set by something that **happened**, never by an audit's opinion. Two
events count:

1. **The claim reaches the Shallowness checks.**
2. **The maker says that is as deep as it goes.**

The second is what makes the queue drainable. Without it a claim dug at twice and still thin sits
there forever, surfacing in every readout, and a queue that never drains is one the maker stops
reading. It can be cleared at the door, inside the readout, with no session at all — agent proposes,
maker calls, as everywhere else.

**Clearing the mark does not assert the claim is good.** It stays shallow, `bank-audit`'s cold sweep
will still list it, and `gaps.md` will still classify it *too shallow to claim it* when a JD reaches
for it. That is `0009`'s own split doing its work: those are **observations**, recomputed fresh every
time, while the mark is an **event queue**. All clearing it says is *nobody owes this another
interview*.

For a declined confidence fork, which wears two marks, they part company:

- The maker states the correction → **both clear** (`0008` already fixed this).
- The maker still does not know the real number → **`needs-interview` clears, `confidence: uncertain`
  stays.**

The flag is **self-announcing and the mark is not**. `confidence: uncertain` fires a **Fork** on every
JD that reaches the claim, so the doubt keeps surfacing on its own; a second queue holding a copy of
it adds nothing. Real doubt should persist as long as it is real — but the *to-do* is discharged once
the maker has decided against it.

### New work touches two things beyond appending claims

- **The wide pass gains a third list: what the Entry already claims.** The read will surface work that
  is already `c1`–`c6`; without a check, the session digs a claim that exists and manufactures the
  duplicate the merge above exists to clean up. The agent diffs the surfaced list against the existing
  claims and **says so** — *"the invalidation work is already c3, skipping"* — rather than dropping it
  silently, because the maker may know `c3` is narrower than what the read found.
- **Entry frontmatter is edited freely in place.** A promotion changes `title`, leaving changes
  `dates`. **Amend, never regenerate** is a rule about *claim ids*; frontmatter carries no ids, and
  nothing downstream traces to a date.

**Splitting an Entry is out.** A return session that concludes the entry should really have been two
does not attempt it. Splitting is the maker's act (`0013`), the Entry id **is** the filename slug
(`0005`), and doing it properly means new files and rehoming claims across them. It is done by hand in
git.

## Considered options (rejected)

- **A mode flag or argument on the skill** (`--deepen`, `--new-work`) — rejected: it is `0013`'s three
  flows wearing one skill's clothes, and it makes the maker pick before the agent has shown them
  anything.
- **The agent inferring why the session was opened** and proceeding silently — rejected: two of the
  three triggers are invisible to it, so it would be guessing at the door.
- **The return door running the recurrence view over `runs/*/gaps.md`** — rejected: that is
  `bank-audit`'s read-only pass, and the maker arriving from a gap report already holds the claim id.
- **Re-reading the source when deepening** — rejected: the read names work, and the work is already
  named; what a marked claim lacks is impact, which `0014` established no source holds.
- **A tombstone for the merged-away id** — rejected: nothing reads it, and it is bookkeeping in a
  hand-edited file. Past run folders are self-describing without the bank.
- **Reusing or renumbering the dead id** — rejected: this is the exact silent redenotation `0013`
  forbade, and the only failure mode in the system with no lint able to see it.
- **The younger claim's id surviving** — rejected: the elder carries the excavation and the citations.
- **Leaving both claims and merging nothing** — rejected: `0006` would grant the duplicated work two of
  three bullet slots and count it twice in the entry score.
- **Parking recording which shallowness check it failed** — rejected: cold-judgeable so nothing is
  saved, stale on the first hand-edit, and it reads like doubt.
- **The mark clearing only on reaching the checks** — rejected: a claim with nothing left to give
  never clears, and the queue stops being read.
- **Clearing `confidence: uncertain` alongside the mark** — rejected: the doubt is real until the
  maker states a correction, and the flag is the thing that keeps surfacing it.
- **An audit or the door clearing marks on its own judgement** — rejected by `0009` already: an
  opinion is not an event.
- **The door splitting an Entry into two** — rejected: new Entry ids, new files, claims rehomed; it is
  the maker's act in git.
- **Silently dropping already-claimed work from the wide pass** — rejected: the maker may know the
  existing claim is narrower than what the read surfaced.

## Consequences

- **Discharges the merge duty** that `0009` assigned to ingestion and `0013` deferred to this ticket.
  A merge is expressible under frozen ids because **deletion is loud where renumbering is silent**,
  and because a run folder is a complete record of itself.
- **Completes `0008`'s mark lifecycle.** The mark was set by an event and had no defined end; it now
  has two clearing events, both events in a session, neither an opinion.
- **Refines `0009`.** The mid-run append it refused is permitted at the door, after excavation — which
  is what it meant by "merging is what draining the mark is for."
- **Confirms and extends `0013`.** One door, amend never regenerate, ids never renumbered — plus:
  **deleting a claim is permitted**, and it is the only way one ever leaves the bank besides the
  maker's own hand.
- **Extends `0014`'s wide pass** with a third list on a return — what the Entry already claims — and
  confirms that the door inherits the spine only where the wide pass runs.
- **Frontmatter is not id-bearing** and is freely editable, which no earlier ADR had stated.
- **Closes the ingestion branch.** `0013` fixed the shape, `0014` the interview, `0015` numbers and
  provenance, and this ADR the way back in.
- **Build-time residuals:** the wording of the readout; how the agent judges that two claims circle
  the same work; how it phrases the merge proposal.
