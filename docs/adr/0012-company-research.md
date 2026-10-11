# Company research: a maker-invoked lookup that informs, never decides

**Status:** accepted

## Context

A JD is often silent on the thing the résumé most needs to know. "Senior Engineer, TypeScript,
fast-paced team" splits two ways and says which is meant in neither direction. `0002` handled the
sharp case by offering **"research the company"** as a third response on a binary framing **Fork**,
and graduated the mechanism to its own ticket (#17) as a cross-cutting capability: which sources
are trusted, how the right company is confirmed, how deep the pull goes, whether anything persists,
and how a result feeds back.

Two things had already moved by the time this was grilled.

`0008` invented the **Past-run glance** and named it *"the same shape as Company research"* — lazy,
informative but never decisive, recorded beside the answer, and never re-consulted on a replay. So
the feedback and recording sub-decisions had a precedent to inherit rather than invent.

`0011` then went further and settled two things outright: the finding lives in
`runs/<jd-slug>/context.md` as **Researched context**, a committed artifact held at **lower
standing** than `jd.md`; and the **Network boundary** — *nothing reaches the selector except
through a file in the run folder* — replaced `0007`'s overreaching "no network in a run". `0011`
also **widened** the capability past `0002`'s framing Fork, to solidifying a **flimsy JD** before
scoring.

What was genuinely left: the locus of the looking, what triggers it, how identity is confirmed,
which sources count, how deep to go — and whether `0011`'s widening fires automatically.

## Decision

### Opus looks, in a subagent

The maker does not do the looking. The alternative reading of `0002`'s third response — that it
means *"hold on, let me go tab over"* — leaves nothing to design, and it makes the one moment the
system admits it does not know also the moment it hands the maker a chore. A headless Claude Code
session already has built-in web access (`0011`: **built-in web fetch**, not MCP), and it is
already stopped and waiting.

The lookup runs in a **subagent**. Fetched pages never enter the main session; only the finding
crosses back. This makes *"the finding is what is recorded"* structural rather than a matter of
good behaviour, and it keeps a long tailoring run's context clean.

### Two consumers, both maker-invoked

There are two places a JD's silence hurts, and neither fires on its own.

- **At a halt** (the `0002` consumer, widened). The maker asks; the run is already stopped. Not
  Fork-only: `0010` made the **Checkpoint** *always present*, so the maker is reading an **Angle
  statement** and an **Omission view** on every run, including silent ones. "Is that really what
  this company is?" is a fair question with no Fork attached, and the answer is a web search. The
  framing Fork merely *advertises* the action as its option C.
- **Before scoring, when the JD is too thin to score against** (the `0011` consumer). `0001` fixed
  **Fit** as judged against the **full JD text**; when the full JD text is forty words, that
  scoring is noise. The repair is only useful *before* scoring. But the run **halts and asks**
  first — it does not research on its own.

**Nothing is fetched without the maker asking for it.** The decisive argument is identity: an
automatic pre-scoring fetch happens while the run is still moving, so there is nobody to confirm
*which* company was found. That would reintroduce the exact failure the next section exists to
kill. The secondary benefit is that a JD too thin to score may simply mean half the posting was
pasted, and re-pasting is the cheaper fix — a silent research pass would hide that.

### Identity is adjudicated, never inferred

This is where the capability could violate zero fabrication without inventing anything: by
reporting **true facts about the wrong company**. That is worse than a guess, because it reads as
solid, and nothing downstream traces a framing answer back to a source.

**Propose and confirm.** Opus searches, proposes the candidate in one line — *"I think this is
acme.dev, the Berlin data-infrastructure one, ~80 people. Right?"* — and reads deeper only once
the maker says yes. One line of confirmation kills the entire namesake class.

Two rules bound it:

- **Two plausible candidates → say so and stop.** *"Could be the Dublin payments one or the Seattle
  logistics one"* is a **finding**, not a failure to be resolved by picking the larger. Ambiguity
  is reported, never resolved.
- **A JD that names no company** — a blind recruiter posting — returns **no signal** immediately,
  with no searching at all. There is nothing to confirm an identity against, and reconstructing one
  from role shape and location is fabrication wearing a hat.

The confirmed identity, including the URL, is recorded in `context.md`.

### Sources: the company's own surfaces

The question being answered is **not** *"what is this company like"* — it is *"the JD splits two
ways; which way does this company actually lean."* Those pull toward different corners of the
internet, and the second one is narrow.

Trusted, and only these — **the company's own public surfaces**:

- **Product / site** — what they build.
- **Engineering blog** — what their engineers think is worth writing about. The strongest single
  signal on frontend vs backend vs infra.
- **Their other open roles** — near the top, and easy to overlook. Four backend postings and no
  frontend one breaks a framing tie by itself: current, on-question, and the company's own words.
- **Public docs / API reference** — an API-first company reveals itself immediately.
- **GitHub org**, where one exists.

**Every line of the finding cites the URL it came from** — the **Claim-level trace** discipline,
applied to research. A sentence that cannot name its source is the model's prior talking, and it
does not ship.

### Depth: the stopping condition is the question

The stopping condition is **the decision, not a page budget**: read until the tie breaks or the
signal is clearly absent, then stop. **One pass** over the surfaces above — no crawling outward, no
following links off the domain, no second-order sources.

What comes back is deliberately small: **a handful of cited sentences ending in an explicit lean —
A, B, or no signal.** It must be readable in fifteen seconds, because it is read mid-decision.

> Their eng blog is 9 of 11 posts on stream processing and storage (URL). Docs are API-first, no UI
> surface (URL). Three of their four other open roles are backend or infra (URL). **Leans backend.**

**Absence is as cheap to report as presence.** The failure mode is an agent that reads twelve pages
rather than come back empty-handed, because empty-handed *feels* like failing the task. It is not:
*"their public surfaces say nothing either way"* is a finding, and a useful one — it says the tie is
genuinely the maker's to call. **No signal is a legitimate terminal state**, reported on reaching
it, not after exhausting the list.

### The finding informs; the human decides

At a halt, the finding is shown **inside the same Fork, and the Fork is still asked.** Research
never answers it. Research also never re-scores by itself — if the maker's *answer* flips the
framing, `0006`'s existing re-score rule fires, and nothing new is needed.

Before scoring, the finding does reach the selector — but only as `0011`'s **Researched context**:
a committed file, at lower standing than `jd.md`, which **may change how the JD is read** and may
**never add a requirement**. No **Gap report** line may trace to it. `jd.md` is what the employer
said they want; a company blog is what the company likes to talk about, and folding the second into
the first fabricates **Must-haves**.

### Persistence: nothing beyond the run folder

Company research **never touches the bank**. `0008` fixed that framing answers do not, and `0005`
banned derived stores; a `companies/` directory would be that ban in a different hat — a second
store of facts nobody maintains, stale on first read, outside `bank/` with no interview discipline
behind it.

Applying to the same company twice needs **no new machinery**. `0008`'s **Past-run glance** already
reads past run files when a Fork fires; a recorded finding is sitting there and surfaces
automatically, **labelled as past and dated**, so a six-month-old finding is never read as fresh.
Staleness is the maker's judgement, and re-invoking research is one line.

**The determinism statement** is sharper than "a replay never re-fetches" (though it does not):
**the run folder's files fully determine the final selection.** `jd.md`, `context.md` and
`checkpoint.md` are all committed, so a replay reproduces the run's *settled* state. That a replay
scores with a `context.md` the first pass did not yet have is correct, not a leak — the first pass
was superseded by the maker's answer the moment it was given.

## Considered options (rejected)

- **The maker does the looking** — rejected: nothing to design, and it makes the system's one
  admission of ignorance into a chore. Also, whatever the maker read evaporates: no `context.md`,
  nothing for the **Past-run glance** to surface later.
- **Fork-only availability** (as `0002` wrote it) — rejected: too tight once `0010` made the
  Checkpoint always present. "No Fork fired, so you may not ask" is a silly answer to a request for
  a web search from someone already sitting at a halt.
- **Automatic pre-scoring research** — rejected: the run has not stopped, so **no one can confirm
  the company's identity**, and the namesake risk returns in the one place nothing downstream would
  catch it. It also hides the cheaper diagnosis (the posting was half-pasted).
- **A live fetch feeding scoring directly** — rejected by `0011`'s **Network boundary**, and
  independently here: it would make a cross-run `scores.md` diff mean *someone else's website
  changed*, destroying the property `0010` hangs its whole repair story on.
- **Glassdoor / Blind / Reddit** — rejected: they answer *"should I work here"*, not *"how should I
  frame this résumé"*. Wrong question. Also anonymous, unverifiable, and selection-biased toward the
  angry. Tempting because the content is vivid.
- **News, funding, Crunchbase** — rejected: reports stage and runway; says almost nothing about
  which engineering discipline leads.
- **LinkedIn team composition** — genuinely on-question (who they actually employ), but login-walled
  and hostile to fetching. Recorded as **wanted but unavailable**, so it is not rediscovered as a
  fresh idea later.
- **A company store** (`companies/acme.md`, accumulated across runs) — rejected: `0005`'s banned
  derived index by another name. The **Past-run glance** covers the same need with zero new
  machinery and correct staleness semantics.
- **A page or token budget as the stopping condition** — rejected: it either truncates a search that
  was about to succeed or licenses one that should have stopped. The decision is the budget.

## Consequences

- **Refines `0002`.** Company research is not a Fork sub-option: it is an action available at **any
  halt**, which the framing Fork advertises. `0002`'s "third response" survives as the place it is
  most obviously useful, not as its only door.
- **Sharpens `0011`.** `0011` established `context.md` and widened the capability to the flimsy-JD
  case; this ADR fixes that the widened case **halts and asks** rather than firing automatically,
  and supplies the identity, source and depth rules `0011` explicitly left to #17.
- **Inherits `0008` wholesale.** The **Past-run glance** is the repeat-company mechanism; a
  surfaced past finding is dated and labelled as past.
- **`0007`'s offline claim stays superseded.** `0011`'s **Network boundary** is the live wording;
  nothing here reopens **tectonic** (rejected as XeTeX, not for its network use) or **external ATS
  scoring** (rejected, in `0010`'s own words *"more decisively"*, for measuring parseability rather
  than selection).
- **The ingestion consumer stays fog.** #17 framed this as cross-cutting and possibly serving a
  silent ingestion source. The ingestion interview does not exist yet, and a capability shaped
  around two consumers when only one is real fits neither. The map keeps it in **Not yet
  specified**.
- **Build-time residual:** what counts as *"too thin to score"* is deliberately not a threshold
  here. Like `0007`'s **page-budget constants** it is a measurement, to be calibrated against real
  JDs — and unlike them it fires a question rather than a rule, so a wrong call costs one dismissed
  prompt.
