# Nothing qualifying is left out; the merge is how it fits

**Status:** accepted

## Context

The maker read the page `0047` and `0048` produced and rejected the premise under it:

> *"The goal is to rewrite everything of that particular experience or project
> according to how the JD requires, it does not mean we are leaving out points."*

That is a different job from the one this system has been doing. Since `0001` the
Packer has been a **selector**: claims compete, the best fit, the Omission view
reports the losers, and the maker reads what lost as a signal about the bank. The
maker is asking for a **compressor**: an entry that reaches the page tells its whole
story, re-angled toward the posting, and what varies with the JD is *how the work is
said*, not *which of it is said*.

### The arithmetic, because it decides what is possible

The bank holds 24 claims across 4 entries; 16 are at or above the Bullet floor. The
page gives **31 lines** to Entry headers and Bullets.

| | lines | vs 31 |
|---|---|---|
| 16 qualifying units, each its own two-line XYZ Bullet | 44 | **+13** |
| the same 16 claims folded into ~7 merge groups | 26 | **fits, with 5 spare** |

**One page and nothing-left-out are compatible only through the merge.** They are not
compatible through the cap, through the Bullet floor, or through anything the Packer
can do with the allocation, because none of those add lines. This is why the decision
below is about compression and not about the cap.

Two candidates were rejected on the maker's own call and are recorded here so the
choice is legible: **two pages** (56 lines fits comfortably; rejected), and **fewer
entries told fully** (two entries in 30 of 31 lines; rejected).

## Decision

### 1. Every qualifying claim of a placed Entry reaches the page

**Qualifying** is the existing Bullet floor and nothing new: score at or above `0.50`.
A claim below the floor still does not place, and that is not an omission — a 0.20
claim on the page argues against the maker, and forcing it there would make the page
worse in the name of completeness.

An Entry that does not place at all is unaffected; the Entry floor already decides
that, and `0026` is untouched.

**Reaching the page means being cited by a placed unit** — its own Bullet, or a merge
group it belongs to. It does **not** mean having its own line. Compression is the
mechanism; presence of the *substance* is what is guaranteed.

### 2. The Packer enforces coverage; the scorer supplies it

`pack.py` gains a check: **a placed Entry with a qualifying claim that no placed unit
cites fails the run**, naming the claims and how many lines the Entry has. It does not
merge anything itself — declaring a merge is a judgement about whether beats land
alone (`0037`), and the Packer owns arithmetic, not judgement (rule 1).

So the loop is: score, pack, and where the page cannot seat the entry's claims
separately, the failure says so and the scorer declares merges in `## Merges` and
re-packs. **The Packer states the constraint; the scorer writes the sentence that
satisfies it.**

This is deliberately a *failure* rather than a silent drop. Under the old contract a
dropped claim was reported in the Omission view and the run continued, because losing
was a normal outcome worth reading. Losing is no longer a normal outcome for a
qualifying claim, so it stops the run.

### 3. `0037`'s trigger is unchanged, and its default now bites

`0037` already says the default is together and separateness is what must be earned:

> *"A claim earns its own line when standing alone makes it land harder than it would
> inside a merge."*

Nothing about that test changes. What changes is that the page can no longer absorb a
generous reading of it: an Entry that declares five lone claims where three groups
would have told the same story now fails §2 rather than quietly dropping its weakest
two. **`0037` was already the rule; this ADR is what makes it binding.**

### 4. The cap is soft, and the softness is earned by compressing

`0048`'s `MAX_BULLET_LINES = 6` stays as the Entry's share. It becomes a **soft cap**:
an Entry may take lines past it out of the page's residue, in Entry-score order.

**But it may borrow only when every one of its placed units is a merge group.**

That condition is the maker's own caveat made mechanical:

> *"we need to make sure that the model does not take it as lenience to not merge the
> bullets together to tell a story."*

Without it the soft cap is strictly easier than merging, and a scorer that wants six
separate lines simply borrows them — the cap bends, the story never gets compressed,
and §1 is satisfied by spending page rather than by writing better. With it, extra
lines are available **only to an Entry that has already paid the compression cost
everywhere**, so borrowing is the reward for merging and never the alternative to it.

The bill, stated plainly: **an Entry holding one claim that genuinely lands alone
lives inside six lines.** That is a real cost and it is the right one — a lone claim
strong enough to refuse a merge is strong enough to be worth the entry's whole share.

### 5. The Omission view keeps its job, and its content changes

It stops being mostly *claims that lost* and becomes mostly *claims below the floor*
and *entries that did not place*. The `depth cap` reason from `0048` §3 survives for
the Entries that cannot borrow. Nothing is removed — what shrinks is the population,
which is the point.

## Consequences

- **The merge stops being an occasional declaration and becomes the normal unit.**
  Expect most Bullets on most pages to cite two or three claims. `0034`'s rules on
  what a merged Bullet may assert are load-bearing on every line now rather than on
  one, and the merge verifier (`tailor` §5.1) runs on nearly the whole page.
- **A run can now fail for a reason the maker must fix by composing differently**,
  which is new. Every previous packing failure was a malformed table.
- **The Gap report's *you have it, the page did not* class nearly empties** for placed
  entries. It survives for skills shed from a row and for entries that did not place.
- **This reverses the selection premise of `0001`** for claims inside a placed Entry.
  Selection still decides which *Entries* reach the page and in what order; it no
  longer decides which of a placed Entry's qualifying claims do.
- **`0048`'s hard cap becomes soft**, and that ADR gains an Addendum. Its arithmetic —
  the cap is a line budget — is untouched and is what the soft cap bends.

## Addendum, 2026-08-13 — the floor stops filtering inside a placed Entry

`docs/adr/0053-the-bank-is-the-source-of-facts-not-of-words.md` §3 widens §1 above.
The guarantee ran to every claim **at or above the Bullet floor**; it now runs to
**every claim** of a placed Entry.

§1's reasoning was that a 0.20 claim on the page argues against the maker. What
`runs/auxo-ai` showed is the other half of that trade: `sweatpact` holds five claims,
four of them scored 0.20 against an AI posting, and it rendered **one line under its
own heading** — a project introduced to the reader and then not described. An Entry is
ranked as a whole, and if it earned the page it tells its whole story.

**The floor keeps its other job.** `Entry.slots` and the reservation queue still read
qualifying claims, so an Entry with nothing above the floor still never places. What
stops is the floor filtering inside a block that already won.

The mechanism needed no invention: a merge group's members never had to clear the floor
individually (`0037` §2). What changed is that the Packer now insists it be used.
