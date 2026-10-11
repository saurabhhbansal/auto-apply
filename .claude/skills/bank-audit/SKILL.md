---
name: bank-audit
description: How is the bank doing? A read-only, print-only maintenance pass over the whole bank — a cold sweep for the four Shallowness checks and the trivia check, then a recurrence view over past Gap reports ordered by what keeps costing the user something. Marks nothing, writes nothing, scores nothing.
---

# bank-audit

One pass over the whole bank. It is **bank maintenance, not a third capability** — the system has
two, ingestion and tailoring, and this is neither. It is the deliberate *"how is my bank doing?"*,
invoked outside a tailoring run.

Terms are defined in `docs/glossary.md`. Read it if one below is unfamiliar.

**Two halves, in order.** The **cold sweep** (§2) reads the bank and lists what fails the
**Shallowness checks**. The **recurrence view** (§3) reads `runs/*/gaps.md` and orders findings by
how often each has actually cost the user something. Run the sweep first, and run it cold — see
§2's opening for why the order is load-bearing rather than cosmetic.

You take **no argument** and sweep the whole bank. There is no single-entry mode and no flag.

## The four rules

These hold without exception.

1. **You mark nothing.** Never write `needs-interview: yes`, and never clear one — the mark records
   that something happened in a session, and your opinion is not an event.
2. **You write no file.** No health report, summary, scratch note or issue. This pass **prints**;
   the user acts or does not.
3. **You edit nothing.** No Entry file, no `bank/profile.md`, no `runs/`, however obvious the fix.
   If the user asks for one, that is an `ingest` session.
4. **There is no score.** No percentage, grade, "8 of 14 entries healthy" or traffic light.
   Judgement is in words. The one thing you count is **recurrence** (§3) — a count of runs.

No network. Nothing here is answerable by fetching anything, and a claim's shallowness is a fact
about the claim.

## 1. Read the bank

**Check it parses, then read it.** The parse comes first because a file the reader refuses cannot be
swept, and calling its claims shallow would be a verdict on prose you have not correctly read. It is
the same read-only parse `ingest` runs after writing an entry — it reads every Entry file through
`tools/bank.py` and writes nothing, which is the whole of what rule 3 allows.

```bash
python tools/bankcheck.py
```

A failure names the offending file. **Say which one, leave it out of the sweep, and read the rest** —
it is not a shallowness finding, it enters neither list, and repairing it is a hand edit you do not
make (rule 3). The commonest shape is a `number` with no `provenance`, refused because it would
otherwise render flat and trace clean forever.

Then read every Entry file — all five folders — and read them **fully**. The sweep is judgement over
the prose; a `## c3` heading tells you nothing on its own.

Use the Glob tool: `bank/jobs/*.md`, `bank/projects/*.md`, `bank/responsibilities/*.md`,
`bank/extracurriculars/*.md`, `bank/certifications/*.md`.

The last three are **supporting entries** and the sweep reaches them **with two checks lifted** —
see the note under check 4.

`bank/profile.md` is the **Static profile**, not an Entry. It holds no Claims, the checks do not
reach it, and `render.py` already validates it by field name. Skip it.

An empty bank is not an error. Say there is nothing to sweep and go to §3.

## 2. The cold sweep

**Cold means claim against itself.** No JD, no `runs/`, no gap report — those belong to §3, and
letting them in here corrupts the one property that makes the sweep worth running. A claim is not
shallow *because a posting wanted something it does not say*; that is a **Hole** or a coverage
problem, and it is judged against a target, not against the claim. Do the sweep before you read a
single gap report, and **do not go back and revise its list** once §3 has told you which JDs the
user has been running.

There are exactly **five checks**, and only five — four for shallowness, one for clutter.

**A Shallow claim**, two ways:

1. **It never says what changed.** The claim describes what was built and how, and never what was
   different afterwards. This is the defect that actually sinks a claim: no job ad asks for
   activity, so it will score badly against every JD forever. *"Built a Kafka consumer that batches
   offset commits"* — what happened once it did?
2. **There is no room to re-angle it.** The **Evidence** entails nothing the **Assertion** does not
   already state. Under **Downgrade-only**, render can restate such a claim and nothing more, so it
   works for the one JD it was written for and is dead weight on every other. **The test is
   entailment, not length**: a long Evidence that paraphrases the Assertion fails it, and a
   two-clause one that names who was waiting and what they did instead passes. A near-empty Evidence
   body — a **Checkpoint** add has one by construction — is the commonest instance rather than the
   definition, so read it and ask what a *different* JD could draw out of it.

**A Shallow entry**, two ways:

3. **Too few claims to fill a block** — fewer than three. The entry can never take three **Bullet**
   lines, so a three-year job renders as a one-liner beside a side project. It is worth reporting
   **even when every individual claim is sound**, and it is also the source of the odd ordering:
   a one-claim **Entry score** is the mean of a one-element set.
4. **No claim in it carries a sizing fact.** Not one Claim's Evidence says what the work was a part
   of, who consumed it and how senior they were, how far it spread, or whether it was a first or
   self-started — the sizing facts `tailor` §5.1 reaches for. Each claim may say what changed
   perfectly well; the entry still renders as a column of true sentences a reader cannot weigh,
   because *~12 services* means nothing without the 40. **Entry-level, like check 3**: one claim
   without a denominator is normal, and a whole job without one is a depth pass that never asked.
   The fix is a deepening interview on the entry, and the questions are `ingest` §3's last five.

**A cluttered claim**, one way:

5. **Its Evidence carries detail that fails `ingest` §3.1's résumé test** — a configuration value
   (*a 50m radius*), a file, function or field name, plumbing, an unused side feature, an anecdote,
   commentary about the user. True and harmless-looking, and the tailor may still reach for it:
   every sentence in the bank is a candidate for a page. Quote the offending phrase. The fix is a
   hand edit — delete the sentence — never an interview, so say that it is a two-minute trim.
   **Never report a sentence that a `number:`'s provenance rests on** (*"the 3x is what it felt
   like; nobody timed it"*): that one is load-bearing even though it reads like an aside.

**Checks 3 and 4 do not reach a supporting entry.** Both are about an Entry's ability to fill a
**block**, and a `responsibility`, `extracurricular` or `certification` has no block — it renders as
one row. A certification with a single claim is not thin; it is a certification. Reporting either
against one would send the user off to deepen an entry that is already everything it can be
(`docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md` §9).

Check 1 is lifted on a `certification` alone, and only there: the claim a credential makes is that
it was **earned**, which is a fact about the user rather than a difference afterwards. **Check 2
binds it hardest** — a certification whose Evidence says only *"passed the exam"* can never answer a
posting that names the skill rather than the credential, and that is the finding worth reporting.
Checks 1 and 2 both bind a `responsibility` and an `extracurricular` unchanged: a post held has a
before and an after like any job.

### What is not a check

- **A missing `number`.** Numbers are optional, and a figure cut by the **"So what?" test** is the
  interview working, not failing. Do not report it, do not mention it, do not soften it into "could
  be stronger with a number". **Check 4 is not this check wearing a coat**: a sizing fact is prose
  in the Evidence — *"one of about 40 services"*, *"read by the CFO every month"* — so an entry
  whose every claim carries a `number:` can still fail it, and an entry with no figure anywhere can
  pass.
- **A missing `provenance`.** It rides with `number`; where there is no number there is nothing to
  tier. (A `number` *without* a `provenance` never reaches the sweep — §1's parse refuses it.)
- **Any "why / who / what it replaced" field.** The Claim schema has no such fields. Checking for
  them invents structure the bank does not have.

**Nor is anything else.** Inventing a check is this section's failure mode, and it arrives disguised
as helpfulness — a thin `skills` line, a terse Assertion, prose you would have written differently.
If something reads badly and does not fail one of the five, **it is not a finding**: say nothing.

### The mark is orthogonal

A claim carrying `needs-interview: yes` is not a finding, and a claim without one is not exempt.
The mark is an **event queue** — *nobody owes this another interview* is all clearing it ever said —
while shallowness is an **observation**, recomputed fresh every time you run this. So:

- a **marked** claim that clears all five checks is **not reported**;
- a claim whose mark was cleared because the user said *that is as deep as it goes* is still
  reported if it is still shallow. That is the designed behaviour, not a bug: clearing the mark
  never asserted the claim was good.

Where a finding *also* carries the mark, say so in passing — it tells the user the claim is already
in the queue and this is not new work — but never reorder or filter on it.

### What the sweep prints

One line per failure, naming the address and the check it failed. Claim addresses are
`<entry-slug>/c1`; an entry failure names the slug alone. Group under the check, because the check
is what the user would do about it.

```
Cold sweep

Never says what changed
  helios-payments/c4   builds a nightly reconciliation job; nothing about what it changed
  ledger-cli/c2        describes the parser rewrite and the test suite, no difference afterwards
  atlas-logistics/c3   "owned the deploy pipeline" — activity only  [needs-interview]

No room to re-angle it
  orbit-analytics/c3   Evidence restates the Assertion; nothing a different JD could draw on
  feedforge/c1         Evidence is one clause, added at a checkpoint  [needs-interview]

Fewer than three claims
  vantage-systems      2 claims — cannot fill a block
  pier-review          1 claim

No sizing fact anywhere in the entry
  atlas-logistics      six claims, none says what the work was a part of or who read its output

Trivia a recruiter would never use — delete the phrase
  helios-payments/c1   "batching commits to a 50ms window"; "the batch window was the third thing we tried"
  feedforge/c1         "a per-host limiter with a 250ms token bucket"
```

Give each line **a few words of its own**, off the claim's actual text. A bare id means nothing
three weeks later, and the line has to be judgeable by eye or it is just an address wearing a
verdict.

**No totals and no bank-level counts** — not *"9 findings across 14 entries"*, not a percentage
clean, not a ranking of entries. The list is the report. *(The `2 claims` beside a short entry is
check 3 saying what it saw, not a total.)*

## 3. The recurrence view

The sweep is judged cold; a **Hole** cannot be. Work that was never ingested is only a defect
*against a target*, and the target is **the JDs actually run** — `runs/*/gaps.md`, never a
hand-maintained list of roles being aimed at. Such a file would go stale silently and would license
you to invent gaps the user does not care about. So the second half reads the run history and
nothing else.

Glob `runs/*/gaps.md`; the number of files is the denominator.

If there are no runs, say so plainly and stop. A bank with no run history has no recurrence, and
that is a fact about the history, not about the bank.

### 3.1 Group by what was asked for, not by class

Read every `gaps.md`. Each line carries one of the three **Gap classes** — *nothing in the bank* ·
*too shallow to claim it* (naming a claim id) · *you have it, the page did not* — under a heading
of that name.

**A finding is a territory, across runs.** *Event-driven systems* is one finding whether four runs
classified it four different ways. Group on what the posting was asking for, then show the class
breakdown underneath. The class is what the user does next; the territory is what keeps costing
them.

**The grouping is your judgement, never a string match.** *"Event-driven systems"* in one posting
and *"async messaging at scale"* in another are the same finding; *"Kubernetes, as something you
have run"* and *"Kubernetes as a deploy target"* are two, and collapsing them would hide which one
recurs. Read the lines and decide. A grep is fine for pulling them out, never for grouping them.

### 3.2 Order by how often it has cost something

Order by **the number of distinct runs a finding appears in**, most first. Not by class, not by how
bad it looks, not by how easy it is to fix.

**Always print the denominator.** *Two of two runs* and *two of nine* are different situations, and
the ratio is the only thing separating them.

A finding that appears in **one** run is not recurrence. Print those, but keep them last, in a short
tail, and say what they are: seen once. They are exactly the material recurrence is meant to
demote — a single posting asking for something the user has never done is not evidence about the
bank.

### 3.3 Re-check the recurring ones against the current bank

**Before you report a recurring finding, check it against the bank as it stands.** A gap recorded in
March may have been ingested in April, and an audit that nags about something already fixed is one
the user stops running. Only the recurring findings are re-checked — the one-off tail is not, which
is what keeps this pass cheap.

How to re-check, per class:

- **too shallow to claim it** — the line names a claim id. Open it and apply §2's two claim-level
  checks *to that one claim*. If it now says what changed and its Evidence carries more than its
  Assertion, **the finding is retired**: say so in one line and do not carry it into the list. Where
  **the id is gone**, the claim was deleted in a **Claim merge** — a deleted id denotes nothing,
  there is no tombstone, and you cannot resolve the survivor mechanically. Re-check the territory the
  way you would for *nothing in the bank* instead, and say the id no longer resolves.
- **nothing in the bank** — look for an Entry that now covers the territory. A new Entry, or new
  claims on an existing one, retires it.
- **you have it, the page did not** — the bank was never the problem here, so the only thing to
  re-check is that the covering claim still exists. If it does, the finding stands **as a page-budget
  observation, with nothing to fix in the bank**, and you say that explicitly. Recurrence in this
  class means the user keeps having something and keeps not showing it — worth knowing, and not a
  reason to ingest anything.

Where a finding's classes disagree across runs, re-check what the most recent run said. An older run
saying *nothing in the bank* and a newer one saying *too shallow* is the bank moving in the right
direction, and it is worth one clause.

### 3.4 What the recurrence view prints

```
Recurrence — 9 runs

Event-driven systems                                    4 of 9 runs
  3× too shallow to claim it — helios-payments/c2 (re-checked: still no DAG, schedule or backfill
    anywhere in its Evidence), 1× nothing in the bank
  → a deepening interview on helios-payments/c2

Team leadership                                         3 of 9 runs
  3× nothing in the bank — no Entry claims running or growing a team
  → an ingestion session, or accept it

AWS                                                     3 of 9 runs
  3× you have it, the page did not — orbit-analytics/c3 carries it and keeps losing its Skills row
  → nothing to fix in the bank

Retired since they were recorded
  Terraform — 2 runs said nothing in the bank; northwind-retail/c4 now covers it

Seen once
  Ten years of experience (nothing in the bank) · Rust (nothing in the bank) · FedRAMP (nothing in
  the bank)
```

The `→` line is the class's action, stated plainly, and it is the whole point of carrying the
classes through: *nothing in the bank* sends the user to a cold `ingest` session, *too shallow*
sends them to the **Return door** on a named claim, and *you have it, the page did not* sends them
nowhere.

**No coverage ratio and no fit score.** *"You match 60% of the roles you apply to"* measures the
user against the job market, which is not what this pass is for and not something it can know.

## 4. The two halves are the whole report

The sweep, the recurrence view, and — where §1 hit one — the name of a file that will not parse.
**Nothing else.**

Do not comment on prose quality, on which entries are strongest, on what the user should apply to,
or on what is missing from the bank in the abstract: that last one is a **Hole** with no target,
which is exactly the invented gap the design refuses.

**Two claims circling the same work is not a finding either**, however plainly the sweep lays them
side by side. A **Claim merge** is proposed and confirmed at the **Return door**, with the user, in
a session — *"same piece of work, or two?"* is a question, and you are not in a position to ask one.
Reporting it here would be a fourth finding class arriving through the side door, and it would be
the one the user acts on first, because it looks the most concrete.

## 5. There is no "done"

Close on the standard, because it is the thing the user will otherwise ask for:

> **Recurrence is the only standard.** The bank is good enough for the kind of job the user
> actually applies to when nothing keeps repeating across the gap reports.

There is **no terminal state**. The bank grows and evolves, every new posting can open a new
territory, and a clean sweep today says nothing about next month. Never report a bank as complete,
finished, healthy, or done — and never offer a number that would let one be read that way.

The pass ends when it has printed. You do not commit, you do not offer to write any of it down, and
you do not carry it into the next thing you are asked to do.
