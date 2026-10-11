# The page carries three jobs and two projects

**Status:** accepted

## Context

`0049` guarantees that an Entry reaching the page tells its whole story. It says
nothing about **which** Entries reach it, and on a growing bank that is now the
binding question: the maker asked for whole Entries to be scored and the top ones
fitted, with Experience preferred over Projects.

Two things he asked for already existed and were not rebuilt. **Entries are already
scored as wholes** — `Entry.score`, the mean of the top three qualifying claims
(`0024`). **The last two jobs are already guaranteed** — `reservation_queue` is
literally *"the two most recent jobs, then Entry-score descending"* (`0026` §3).

Two things he asked for were flawed as stated, were put back to him with the
arithmetic, and were settled:

- **"Experience always takes priority over projects"** contradicted his own next
  sentence, *"if the 3rd one is equivalent to another project, put the experience
  first"*. Absolute priority means a `0.50` job displaces a `0.85` project; on his own
  bank that drops `auto-apply` — his strongest project — for a weaker job. He chose
  the tie-break reading.
- **Defaults of 3 and 3.** Six Entries want 42 lines against the page's 31 even with
  every claim merged three to a line. They fit only at one merged Bullet each, which
  is the opposite of what `0049` is for. He chose 3 and 2.

## Decision

### 1. Three jobs, two projects, and a job wins only a tie

`MAX_EXPERIENCE = 3` and `MAX_PROJECTS = 2` cut the competing set after ordering and
before anything is reserved, so a capped Entry never takes a block another could have
used.

**A job outranks a project inside a tie group and nowhere else.** The existing
`EPSILON = 0.05` band already means *equivalent*, so this is one clause added to the
sort inside a group that the Packer was already forming. Outside the band, score
decides, and a `0.50` job never displaces a `0.85` project.

**The two-most-recent-jobs guarantee outranks the cap.** The floor's jobs are seated
first and the rest of `MAX_EXPERIENCE` is filled by score, so a recent job that
happens to score fourth is not quietly cut. The cap is never exceeded and the
guarantee is never lost to it.

**Both are command-line flags with these defaults, and `allocation.md` records what it
packed under.** That is the shape `--skills-rows` already has: a flag that materially
changes the allocation, derived from committed files and written into the artifact, so
a replay reproduces it. What would break material determinism is a value nothing
records.

### 2. A capped Entry is reported apart from one the page had no room for

Three reasons an Entry is absent now, not two, and the cap is the new one:

```
- job-4 — entry score 0.80 — did not compete — the page carries 3 experience
  entries and 3 scored above it — best claim job-4/c1 (0.80) — a reason
```

It is named apart because **it is not about this page being full**: the Entry never
competed, and a page with lines to spare would have cut it just the same. Reporting it
as *no room* would send the maker to look at a budget that was never the constraint.

### 3. A section lends the slots the other cannot use

A cap binds **against competition from the other kind**, not for its own sake. What the
caps exist to prevent is a page of nothing but Experience while real Projects wait —
not an Experience section held to three when there is nothing to hold it for. The
maker put it plainly:

> *"we can keep the cap only when we have both projects and experience — if it's say
> only 1 project and 4 experience we can have that. What I didn't want is that even if
> we have projects then also we resort to filling only experience."*

So each section's room is its cap plus whatever the other section cannot use:

```
room[job]     = MAX_EXPERIENCE + max(0, MAX_PROJECTS  - qualifying projects)
room[project] = MAX_PROJECTS   + max(0, MAX_EXPERIENCE - qualifying jobs)
```

**Only unused capacity moves, and that is the whole guard.** A section can never take a
slot the other could have filled, so a bank with four projects still seats two of them
however strong the jobs are — which is exactly the failure the maker named. Four jobs
against one project seats four jobs, because the second project slot had nothing to put
in it. The total never exceeds `MAX_EXPERIENCE + MAX_PROJECTS`, and neither section is
ever starved by the transfer.

The Omission view names the room a cut was made against, and says when part of it was
borrowed, so a maker reading *"the page carries 4 experience entries (3 by default,
plus 1 the other section could not use)"* can see why the number is not the default.

## Consequences

- **`0026` §1's *crossing the floor buys presence* is bounded.** Every qualifying Entry
  used to be reserved a block; now every qualifying Entry **within the caps** is. That
  ADR gains an Addendum.
- **`0026` §1's ten-Entry ceiling is unreachable.** Five is the most that can compete,
  so the cut-lowest-score-first rule above ten entries is dead code kept for its
  reasoning.
- **A cap no longer wastes room.** Four strong jobs and one project seats four jobs —
  §3, added after the maker read this ADR's original consequence saying the opposite.
  The page's shape now depends on what the bank holds of each kind, which is why the
  Omission view prints the room rather than the default.
- **The test suite lifts the caps unless a test is about them.** Most fixtures build
  five to eleven entries to exercise the Entry floor, the sharing rule and the tie
  band; left at their defaults every one of those would be testing the cap instead.
