# Ingestion shape: the session, the source, and the way back in

**Status:** accepted

## Context

The map held the whole ingestion branch as fog on purpose, with one stated gate: *chart ingestion
after the schema exists, because the schema is what ingestion must produce.* `0004` fixed the
**Claim** and the **Entry**; `0005` fixed the files they live in. The gate is open.

Nine fog patches were parked. Charting them breadth-first collapsed most of them: they were not
nine questions but one real question — *what does the interview do* — surrounded by eight framings
that either dissolve against a decision already made elsewhere, or fall out of one structural choice
made here.

This ADR records what was fixed while charting, so that the remaining tickets inherit it rather than
re-litigate it. It decides the **shape** of ingestion. It deliberately does **not** decide the
interview itself.

## Decision

### One session, one entry

An ingestion session takes one job or one project and produces one **Entry file**. It never surveys
a pile and splits it.

Splitting is the maker's act, not machinery. `0011` established **Hand-delivered input** — every v1
input arrives because the maker put it there — and "this repo, write it up as one project" is
another instance of it. A folder holding five things is five sessions, and the maker may stop after
two.

This also protects the only budget ingestion has. Whatever the interview's stopping condition turns
out to be, it is **per entry**; a session that produced five entries would multiply it by five and
would need a survey-and-split phase up front whose posture (skim broadly, classify) is the opposite
of the digging that follows.

**Accepted cost:** nothing ever tells the maker about a fourth project buried in a folder they
forgot. It surfaces the slow way — a **Hole** recurring across `runs/*/gaps.md`, which `0009` already
made the sufficiency standard.

### The read produces facts; the interview produces claims

The session reads the source **first**, and what it extracts is what the source literally shows —
languages, structure, dates, which files the maker actually touched, what the thing talks to. Those
facts exist to make the questions **grounded**: *"you were the only committer on the invalidation
package for eight months — what were you fixing in there?"* rather than *"what was the impact?"*.

The agent does **not** arrive with a draft Entry for the maker to correct.

This is the north star's edge case and it is worth stating plainly. Everywhere else in the system,
fabrication happens at render time and a lint catches it: `0003`'s **Number-trace check**, `0007`'s
length and page lints. At ingestion there is **no lint at all** — whatever is written becomes the
bank, and the bank is the ground truth every later trace resolves against. A drafted claim invites
the one failure nothing downstream can catch: the agent reads a commit saying `perf: cut p99`,
writes *"reduced p99 latency ~40%"*, and the maker skims it and thinks *yeah, that's about right*.
Nothing is wrong with the trace. The claim is simply something the maker never said, and it is now
true forever.

The line is **lift, never manufacture**. A design doc in the repo that states an outcome is the
maker's own words and may be lifted as **Evidence**. The *shape* of the code entails nothing: a
cache package does not license "improved performance."

The division that makes this workable is that a source is structurally incapable of holding half of
every claim. A repo can say **what was built**. It can almost never say **what it was for, who it
was for, or what changed as a result** — which is exactly what `0009`'s **Shallowness checks**
demand ("never says what changed"). So the interview is not padding out a draft; it supplies the
half no source holds.

**The interview is ingestion's spine, and that is correct.** An ingestion interview is a one-time
cost per project with nothing to interrupt. It must not be confused with the **Checkpoint**, whose
budget is tight precisely because it interrupts a run the maker wants finished.

### Sources: one binary, not a taxonomy

The fog proposed three tiers by how much a source volunteers — repo, artifacts folder, self-written
summary. That does not need designing: how much a source volunteers is just how many facts fall
out, and the interview covers whatever is missing either way.

What the tiers were actually pointing at is a property that **does** change what the agent can do:

> **Can this source check me?**

A repo can. *"You say you built the retry logic; git says you never touched that package"* is a
source arguing back — the only genuinely adversarial pressure available at ingestion. An artifacts
folder half-can: it proves a thing shipped, never that the maker drove it. A summary the maker wrote
is their own words handed back, and any pushback against it is theatre.

Two postures follow. Where the source **can** check, the agent verifies answers against it and shows
the receipt. Where it **cannot**, the agent **says so**, so the maker knows that entry rests
entirely on memory.

The dangerous case is the self-written summary, because it reads like a source: the agent treats it
as one, stops digging, and stops at the maker's starting position instead of excavating past it.
**A self-written summary is a floor, not a source.**

### Coming back to an entry: one door, amend never regenerate

There are three reasons to return to an Entry that exists — new work at the same job, a Claim marked
`needs-interview` (`0008`'s three populations), and a Claim a **Gap report** keeps classifying *too
shallow to claim it* (`0009`). These are **one mode**, not three. All that differs is which claims it
opens on. Three near-identical interview flows would drift apart and would make the maker remember
which to invoke.

What the door is permitted to do is fixed here: **amend, never regenerate.**

Re-running ingestion and rewriting the Entry file is the obvious-looking option and it is a trap.
`0005` froze **Claim ids** at ingestion, and every `bullets.md`, `scores.md`, `allocation.md` and
`gaps.md` in every past run cites them. Regenerating makes `c3` silently denote a different claim
than the one last month's résumé traced to — it breaks the **Claim-level trace** retroactively,
invisibly, and with no lint able to notice. Independently, `0005` made the bank a **hand-edited**
file; a regenerate clobbers hand corrections and the maker stops trusting it.

So: new claims append with new ids; existing claims are edited **in place, keeping their id**;
nothing is ever renumbered.

**Accepted cost:** the bank accumulates claims the maker has outgrown. The cure is deleting them by
hand, which is acceptable because it is a markdown file.

### The cold start has no fast path

The bank is useless until it holds real content, and one-session-one-entry means roughly fifteen
sessions before tailoring earns its keep. The obvious shortcut is to seed entries from the maker's
existing résumé.

**The résumé is admitted as a checklist of what exists, never as a source of claims.** It tells the
agent there was a job at Acme from 2021–2023 and a project called Harbour, so the bank knows what is
missing. Every claim still comes from a real session against real material.

Seeding claims from it — even marked `needs-interview` to be repaired later — is rejected. It is the
worst source by this ADR's own binary (the maker's own words, handed back), and worse, it is those
words **already compressed for a résumé**: every bullet on it is the lossy output of the exact
process this system exists to do better. Seeding from it builds a machine whose ceiling is the
résumé the maker already had. It also fails quietly: the bank looks full, the gap reports go quiet
because everything is nominally covered, and the hollowness is discovered only when a real JD needs
a claim re-angled and it cannot be.

### Confidential material is not a design problem

`0005` wrote *"confidential scrubbed at ingestion (no marker)"*. **That is overruled: there is
nothing to scrub.**

Confidential material never becomes a source. The maker decides what goes in reach, so the guarantee
sits upstream of the system — `0011`'s **Hand-delivered input** again. Ingestion needs no scrubbing
step, no generalisation rule, no marker, and no lint.

This is strictly better than scrubbing, which was irreversible and unrecorded: once *"Client X"*
became *"a large US retailer"* the specific was gone from the second brain, with no marker to say it
had ever been there — so a client who later became a public reference could never be recovered.

### `bank/profile.md` is hand-written

The **Static profile** — name, contact, links, education — is explicitly not an Entry (`0004`), so
one-session-one-entry does not reach it, and it had no owner.

The maker writes it by hand from a committed `templates/profile.example.md`. There is nothing to
excavate, nothing to push back on, and it changes twice a decade; an interview mode for it is
machinery for a five-minute typing job.

Because `0007`'s **Renderer** splices it into the template, a typo'd field name becomes a LaTeX
failure — or, worse, a silently missing phone number on a PDF already sent. So **`render.py`
validates it and fails by field name** on a missing or unknown key. That is `0011`'s **Enforcement
locus**: the rule lives in the script, not in something the maker must remember.

Education stays a static block. Making it competitive would put it back inside the selector's world,
which `0004` deliberately removed it from.

### Two skills

- **`ingest`** — cold ingestion and the return door. They share the entire spine (read the source,
  interview, write claims); the only difference is whether the file exists and which claims the
  session opens on. That is a branch inside one skill, not two skills that drift.
- **`bank-audit`** — `0009`'s standalone pass, in its **own file**.

The audit is separated on a behavioural ground, not a taxonomic one. `0009` made it **read-only and
print-only**: it marks nothing and writes no file. That property decays the moment the instructions
live in a document whose main job is writing claims to the bank — an agent mid-audit that notices a
shallow claim, surrounded by instructions on how to write claims, will help. The separate file has
no write instructions in it at all.

The fog's worry — *one skill making both postures mushy* — was about **per-source** skills, and died
with the taxonomy. Nothing distinguishes reading a repo from reading an artifacts folder at the
skill level; the difference is the one binary, which is a branch.

## Considered options (rejected)

- **One session, many entries** (point it at a folder, let it split) — rejected: it needs a
  survey-and-split phase whose posture opposes digging, and it multiplies the interview's per-entry
  budget by however many entries it finds.
- **The agent arrives with a drafted Entry to correct** — rejected: it is a better *interview* and a
  worse *bank*. It converts the maker from author to approver at the one point in the system where
  no lint exists, and a plausible drafted claim gets nodded through and becomes permanent.
- **A three-tier source taxonomy** — rejected: "how much it volunteers" is emergent, not designed.
  Replaced by the one binary that actually changes agent behaviour.
- **Regenerate the Entry file on re-ingestion** — rejected: it breaks frozen **Claim ids** and
  therefore every past run's trace, silently and unlintably, and clobbers hand edits to a file whose
  hand-editability is a decided property.
- **Three separate return flows** (new work / deepening queue / gap-report repair) — rejected: they
  differ only in which claims they open on, and would drift.
- **Seeding the bank from the existing résumé** — rejected: the worst source by the binary, already
  compressed by the process being replaced, and it fails silently by making the bank *look* full.
- **Scrubbing confidential material at ingestion** (`0005`'s line) — rejected: the material never
  arrives, so the step is unreachable; and scrubbing was irreversible with no record that it had
  happened.
- **Company research at ingestion** — ruled **out of scope**. `0012` answers *"the JD splits two
  ways, which way does this company lean"* — a question about a stranger. At ingestion there is no
  stranger: the person who knows what the project was for is in the session. The tempting case (a
  five-year-old project the maker has genuinely forgotten) is precisely where a marketing page
  confidently supplies something wrong that the maker half-recognises and agrees to.
- **An interview mode for `profile.md`** — rejected: nothing to excavate.
- **Folding the bank audit into `ingest`** — rejected: read-only is a property that erodes by
  proximity.

## Consequences

- **Overrules `0005`** on confidential scrubbing. There is no scrubbing step.
- **Closes `0012`'s open ingestion consumer.** `0012` recorded that the ingestion consumer "stays
  fog"; it is now out of scope, and the capability keeps one real consumer by design.
- **Confirms `0009`'s finish line.** The **Shallowness checks** are what the interview aims at, and
  a claim it cannot excavate to them lands marked `needs-interview` rather than blocking — which
  `0009` already fixed and this ADR does not reopen.
- **Ingestion's inbound edge from `0008` is honoured by the return door**, including the **merge
  duty** (`0009`: answering a shallow-gap notification mid-run creates a second claim circling the
  same work). How the door discharges it is the return-door ticket, not this ADR.
- **The interview itself is deliberately undecided.** What it asks, how it pushes back, when it
  stops, and how it elicits **Provenance**, numbers and the **Confidence flag** are the remaining
  ingestion tickets. This ADR fixes only the shape they sit inside.
- **Build-time residual:** `templates/profile.example.md` and the `render.py` field validation are
  build work, not design work.
