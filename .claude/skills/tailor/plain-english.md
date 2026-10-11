# Plain English — the voice every composed line is written in

The register the page is written in. It binds **every line you compose**: the Summary, the leads,
the Bullets and the supporting tails. Read it before writing (`SKILL.md` §5) and keep it open while composing.

It is adapted from `claudish-to-english` in `github.com/programasweights/claudish`, which
characterises the register this page has to avoid better than this repo could:

> **Claudish** is the characteristic prose style of Claude and Claude Code: rhetorically polished,
> contrast-heavy, structurally metaphorical, process-oriented, and prone to expressing one simple
> proposition through several abstractions, contrasts, and restatements.

It is the default output of an LLM asked to compress an argument into one sentence, so **not
writing it is an instruction you have to be given** — which is what this file is
(`docs/adr/0056-the-bullet-is-written-in-plain-english.md`).

## 0. The one rule that outranks this whole file

**Plainer is never a ground for dropping a fact.** This file governs **words**. Every fact on the
page still traces to the cited Claims' Evidence, and plainer never drops the figure, the sizing fact
or the scope — though not every fact in the Evidence belongs on the page (`SKILL.md` §5.1).

In particular, and this is the failure mode this file creates:

- **the number is still the last thing a Bullet gives up** (`SKILL.md` §5.3). *"It reads better
  without the figure"* is not one of the grounds and never becomes one.
- **the sizing fact is worth keeping** (§5.1). The denominator, the audience and how far it spread
  are the first things a compression instinct deletes, and they are what makes a task read as an
  accomplishment.
- **the scope is exactly the Evidence's.** Plain English is shorter, and shorter is where
  *"a payout API that ~12 internal services call"* quietly becomes *"a payout API"*. That is not a
  plainer sentence, it is a smaller claim.
- **a genuine technical term is the plainest word there is.** *Row-level security*, *fuzzy
  matching*, *ClickHouse*, *full-text search*, *gRPC* — keep them. What this file removes is the
  abstraction wearing a technical coat, never the technical word. A technical term stays; a setting
  or an implementation detail doesn't (§5.1).

**The transform is meant to be fact-monotone.** Stripping the frame off a clause hands you
characters back inside the same budget — spend them on the fact that sizes the work, or let the
line finish early. A rewrite for voice that comes back with **fewer**
facts than it started with has been done backwards — go back to the Evidence, not to the sentence.

## 1. What to write instead — six moves

### 1.1 Name the action with the verb for the action

The metaphor verb is the single loudest marker. Replace it with what was actually done.

| written | what it was | plain |
|---|---|---|
| *Became the single door every payout walks through* | three callers moved onto one service | **Unified three payout callers behind one gRPC API** |
| *Kept the system honest to its evidence* | the build fails on an untraceable figure | **Fails the build when a figure is not in the recorded evidence** |
| *Proved the schema generalised past its first consumer* | two more teams adopted it | **Adopted by two more analytics teams** |
| *Bounded what the server hands out* | the endpoint caps its history window | **Capped the history the widget endpoint returns** |
| *Drove ~60% leaner dashboards* | the dashboard database shrank ~60% | **Cut dashboard query cost ~60%** |
| *Engineered the reruns out of nightly settlement* | the overruns stopped | **Brought nightly settlement back inside its window** |

Ordinary verbs do this job: **built, wrote, ran, cut, replaced, automated, measured, checked,
shipped, fixed, added, moved, split, tightened, took over**. A verb is not too plain for a résumé;
a verb nobody uses is too loud for one.

### 1.2 Turn the nominalisation back into a clause

A noun ending in *-ion*, *-ment*, *-ance*, *-ility*, *-ism* where a verb belongs, and the noun
stacks around it, are the second marker.

> *Enforced provenance constraints and prevented model hallucinations by pairing a pre-render
> verification pass with a decoupled architecture that keeps page packing deterministic*

Nothing in that sentence is a lie and nobody can read it. What it says:

> *Fails the résumé build when a figure in a line is not in the recorded evidence, with the page
> arithmetic in a script the model cannot reach*

Same two claims, same two facts, a clause each.

The compound forms go the same way — **X-gated, X-backed, X-side, X-level, X-first, X-safe,
X-layer, X-surface, X-driven** — by recovering the relationship they compress. *approval-gated
release path* is *release needs approval*. The exception is where the compound is the standard
name for the thing: **server-side** and **row-level security** are what these are called.

### 1.3 Drop the contrast unless the contrast is the fact

*not X but Y*, *X, not Y*, *rather than Y*, *less X than Y*, *past its team*, *instead of a Y* —
delete them where the sentence still says the same thing without Y.

> *Shipped it as a pipeline anyone on the team can run, rather than a script on one engineer's
> laptop* → *Moved the deploy to a pipeline anyone on the team can run*

**Where the choice between X and Y is itself the claim, the contrast stays**, because now it is a
fact and the Evidence carries it: *"moved the aggregates to ClickHouse, keeping Postgres for
transactions"* is the design decision the claim is about. The test is whether deleting *Y* deletes
information.

### 1.4 No aphorism, no verdict, no staged emphasis

The tail that sums up what the sentence just said, and the frame that announces it is important:
*that is the boundary*, *the key distinction*, *the whole point*, *a system that cannot bluff*, *the
honest shape*. On a Bullet these are always cuttable, because a Bullet has one sentence and no room
for a sentence about it.

The heading-style flourish is the same failure in a different position: **a Bullet does not open on
a slogan.** *"Built a résumé generator that cannot bluff: …"* spends its opener on an epigram and
then has to say the real thing after the colon.

### 1.5 One sentence, not a colon and a list

> *Rebuilt the feed fetcher end to end: a bounded worker pool, a per-host limiter, and
> conditional requests on every fetch*

The colon promises a definition and delivers three parts of a build. A comma-list or an em-dash
appositive does the same; **the colon is the same list with a better suit**, and so is the
semicolon. One bullet is one accomplishment — pick the part that matters for this posting and give
the others their own lines, or let them go:

> *Cut feed refresh from most of a minute to under 5 seconds with a bounded worker pool*

### 1.6 Say the thing, not the category of the thing

*the page arithmetic*, *the layout handling*, *provenance constraints*, *the ingestion surface*,
*the delivery cycle* — abstractions the reader has to unpack into an object. Name the object: *how
many lines fit on the page*, *text overflowing its box*, *a figure with no recorded evidence*, *the
monthly release*.

This is `SKILL.md` §5.1's *self-contained* rule seen from the other side: *the page arithmetic* has
no missing antecedent — it is simply a level of abstraction above the fact, and the reader pays for
the climb.

## 2. What plain English is not

**Not vaguer.** A plain line still has to finish its argument and keep its facts (§0). Shorter is
usually a side effect, and a good one: most strong bullets fit on one line.

**Not flatter.** Nothing here softens a claim. *"Own the payments ledger end to end"* is plain
English already — the claim is large because the work was.

**Not the bullet shape being relaxed.** *Verb, what, how, result* (`SKILL.md` §5.1) is a
**shape**; this is a **register**. They compose: that shape in plain verbs is the ordinary strong
résumé line, and the same shape in Claudish is what the early runs produced.

**Not chatty, and not first-person.** The register is résumé grammar: the subject is dropped, the
verb leads, no *I*, no *we*, no *my*. Plain does not mean conversational — *"Went round the other
teams and got them to try it out, which was pretty successful"* fails for a different reason.

**Not a licence to reach for the posting's words.** The posting supplies **names** for the work,
never facts about it (`SKILL.md` §5.2), and this file supplies no new names at all.

## 3. Read it back

The last move in composing a line is reading it aloud as one sentence and asking:

1. **Would a person say this?** Not *is it correct* — the other rules already decided that.
2. **Is every noun a thing, or is one of them a category?** (§1.6)
3. **If I delete the frame, is a fact still missing?** If yes, the frame was hiding a hole and the
   fix is in the Evidence, not the wording.

`tools/plainish.py` prints the markers this file names, over the whole of `bullets.md` at once. It
is a pattern lint over a fixed vocabulary and it cannot read meaning: it flags *row-level security*
as readily as *the security surface*, so **its findings are read, not obeyed** (`SKILL.md` §6.2). A finding
you can defend is left alone.
