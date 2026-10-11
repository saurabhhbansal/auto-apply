# Tool surface: filesystem, bash and the conversation — no MCP server

**Status:** accepted

## Context

The ticket (#16) asked whether anything in auto-apply warrants an MCP server, or whether
filesystem + bash covers the whole system, with the burden of proof explicitly on adding one.

Enumerating what the resolved decisions actually require:

| capability | served by |
| --- | --- |
| read `runs/<jd-slug>/jd.md` | file read |
| read the whole bank to score it (`0005`, `0006`) | file read / glob |
| write `scores.md`, `bullets.md`, `checkpoint.md`, `gaps.md` | file write |
| run `tools/pack.py` (stdlib-only) | bash |
| run `tools/render.py` — Jinja2, lints, pdfLaTeX, page assert (`0007`) | bash |
| bank write-back — new Claim, `needs-interview` mark (`0008`) | file edit |
| the **Deepening queue** (`0008`) | grep over `bank/` |
| the **Past-run glance** (`0008`) | grep / file read over `runs/` |
| the **Bank audit** (`0009`) | file read |
| commit the run folder (`0007`) | bash (`git`) |
| **Company research** (#17) | the network |

Exactly one row reaches outside the filesystem, and Claude Code serves it with built-in
WebSearch/WebFetch — which are not MCP either. The repo has no `.mcp.json` and no
project-scoped server.

The enumeration therefore answers the literal question almost immediately. What made the ticket
worth its session was the question underneath it — **what is this system allowed to touch, and
where is the line** — which owns two things nothing else on the map owned: the enforcement
argument that is the only real case for MCP, and a live contradiction between `0007`'s "no
network in a run" and #17's existence.

## Decision

### No MCP server in v1, and the reason is not the enumeration

The enumeration is a symptom. The cause is that **every input to v1 is hand-delivered**: the
maker pastes the JD into `runs/<jd-slug>/jd.md` and puts ingestion sources in reach. The system
has **no automated inbound edge at all**, so there is nothing for a server to broker.

No trigger condition is pre-named for adopting one later. The general rule covers it: **the day
an input stops arriving by hand is the day to re-ask.** Naming a candidate service now (a
hosted document store with an official server, say) would be guessing at a v2 that does not
exist yet, and the guess would age worse than the rule.

### Enforcement comes from the scripts, not from the caller

The strongest case for MCP is that a typed tool can refuse what a shell cannot. Once Opus has
bash in order to run `pack.py` and `render.py`, it can equally hand-edit `scores.md`, call
`pdflatex` directly and skip the lints, or re-pack with a nudged number until a favoured Entry
places. `0010` leans hard on "`scores.md` is never hand-edited", and nothing mechanical enforces
it.

**Rejected, on three grounds:**

1. **A narrow tool would sit beside the wide one, not in front of it.** A headless Claude Code
   session has bash regardless; an MCP wrapper adds an alias, it does not remove a capability.
   Enforcement by tool surface is only real when the wide tool is absent, and here it cannot be.
2. **The lints live inside `render.py`.** Any path that produces a PDF ran the **Number-trace
   check**, the length lint and the page assert. Calling `pdfLaTeX` by hand does not yield a
   shortcut — it yields an unlinted `.tex` and no résumé.
3. **The run folder is in git.** Anything hand-touched shows in the diff.

**The hole this leaves, named rather than papered over:** a `scores.md` nudged *before* the
packer runs passes every downstream check. The Bullet still traces to a real Claim — the wrong
Claim simply won. `git diff` is the only detector, and it is the maker reading it, not a
machine; and because `0006` lets a framing flip legitimately re-score mid-run, "the file
changed" is not by itself a signal. **Accepted for v1** on the git audit trail: if it is ever
seen in practice, it gets fixed then (the obvious fix being that the packer only reads a
`scores.md` committed first).

### The network boundary, restated

`0007` says a run is "fully offline; no network in a run". **That is corrected here.** When a JD
is flimsy, company research genuinely solidifies it, so network-derived material genuinely
reaches the selector, and no wording makes that untrue.

The invariant that actually holds, and the one worth defending:

> **Nothing reaches the selector except through a file in the run folder.**

The network is touched, the result lands as a committed artifact, and *that* is what scoring
reads — never a live fetch feeding a judgement. This is `0007`'s JD seam ("the JD enters as a
file") extended to fetched context, and it is what keeps **material determinism** intact without
pretending the run is offline: replaying a slug reads the file and never re-fetches.

Web access is a real capability the system has. It is **built-in (WebSearch/WebFetch), not MCP**.

### Researched context lands beside the JD, never inside it

**`runs/<jd-slug>/context.md`** — committed like every other run artifact, and held at **lower
standing than `jd.md`**.

`jd.md` is what the employer said they want; a company's engineering blog is what the company
likes to talk about. Folding the second into the first makes everything downstream treat it as
requirements, and `0009`'s **Gap report** starts emitting lines like "you do not cover event
sourcing" because someone published a post about it — a **fabricated Must-have**, which is the
one failure the whole map is built to prevent.

So, precisely:

- `context.md` may change **how the JD is read** — telling the maker that a "full-stack" posting
  is really a backend role, so the JD gets read correctly.
- It may **never add a requirement**, and **no Gap-report line may trace to it.**

*These are constraints #17 inherits, not #17's answer. Which sources are trusted, how the
company's identity is confirmed, how deep the pull goes, whether anything persists, and how a
result feeds back into a Fork all remain that ticket's to decide.*

### The Checkpoint is the Claude Code conversation, and nothing else

The last place a running process could be argued for. A **Fork** halts by Opus asking in the
session and waiting for the reply — **no file to poll, no watcher, no notification, nothing
running in the background.** `runs/<jd-slug>/checkpoint.md` is the *record* written after the
answer, not the channel the answer arrives through.

**Consequence, stated rather than discovered later: a tailoring run is not batchable and not
schedulable.** It cannot be fired at ten JDs overnight for reading in the morning — it stops and
waits for a person. This follows from `0002`'s design; it becomes concrete here.

### What "bash covers it" actually costs

Bash covers the system because the machine is provisioned, not because nothing is needed. The
install-time prerequisites are: **Python 3** (stdlib only, for `pack.py`), **Jinja2** pinned (for
`render.py`, per `0007` the project's only third-party dependency), a **TinyTeX or TeX Live**
install providing **pdfLaTeX**, and **git**. These are things installed once, not a service to
keep running — which is the distinction that matters to this decision.

The `gh` CLI and the GitHub issue tracker are **the design process, not the product.** The
running system uses `git` for the run folder and never talks to GitHub.

## Considered options (rejected)

- **An MCP server wrapping `pack.py` / `render.py` as typed tools**, to make `0010`'s
  "never hand-edit `scores.md`" mechanical — rejected: bash remains in the session, so the
  narrow tool sits beside the wide one rather than in front of it; enforcement belongs in the
  scripts, where it already is.
- **An MCP server for company research** — rejected: WebSearch/WebFetch are built in, and a
  server would add a process to maintain for a capability already present.
- **A pre-named trigger condition for adopting MCP later** (a hosted source with an official
  server, alternative to hand-writing a client) — considered and dropped: v1 has no automated
  inbound edge at all, so the general rule ("an input stops arriving by hand") covers the case
  without guessing at services.
- **Folding researched context into `jd.md`** — rejected: it turns company marketing into
  requirements and lets the Gap report fabricate Must-haves.
- **Requiring the packer to read only a committed `scores.md`** — considered, not taken for v1;
  the git audit trail is accepted instead.
- **Writing the tool surface down as a configured permission allowlist** — deferred: that is a
  build-time artifact, and this map is a design spec with zero code. `SPEC.md` states the
  surface; configuring it is a build concern.

## Consequences

- **Corrects `0007`.** "Fully offline; no network in a run" is replaced by *nothing reaches the
  selector except through a file in the run folder*. The rendering pipeline itself — score,
  pack, render, compile — remains network-free.
- **Adds `context.md` to the run folder**, extending `0007`'s fixed file list, present only on
  runs where research actually happened.
- **Gives `0010`'s rejection of external ATS scoring a cleaner reason**: not "it breaks offline"
  but that it feeds a judgement from the network without landing as a reviewable file, and
  measures parseability rather than selection.
- **Constrains #17** on two points — a separate file, and no requirement may originate there —
  without resolving it.
- **Names a limit**: tailoring is interactive by construction and cannot be batched or scheduled.
- **Adds no dependency.** The dependency list stays Jinja2 alone.
- **Accepts one unenforced rule** (a pre-packer `scores.md` nudge), detectable only by the maker
  reading a diff.
