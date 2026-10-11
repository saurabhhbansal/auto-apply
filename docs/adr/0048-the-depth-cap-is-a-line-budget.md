# The depth cap is a line budget, and always was

**Status:** accepted

## Context

`0047` made a Bullet's declared width a charge at reservation. Re-packing
`runs/auxo-ai` with every claim declared at two lines produced a page nobody
designed:

```
                    before 0047      after 0047
american-express         5                5
xlscout                  5                2
auto-apply               5                1
sweatpact                1                1
```

Nine Bullets instead of sixteen was the expected cost and was accepted knowingly.
**The distribution was not.** The most recent job kept all five of its Bullets while
the maker's main project fell to one line under a bare heading — the exact stub
`0026` called the bill of the Entry floor, except it is now being paid by the middle
of the page rather than the bottom.

### The identity that broke, in `0026`'s own words

`0026` §1 sized the crossing point:

> *"The page gives **32 lines** to Entry headers and Bullets. A header is
> `ENTRY_HEADER_LINES = 2`. So at *n* entries the page has `32 − 2n` lines for
> Bullets and a cap of 6 wants `6n`. They cross at **exactly four**."*

**`6n` is six units costing six lines.** That identity held because a Bullet was one
line and a second was bought afterwards out of the residue, so a cap counted in units
and a cap counted in lines were the same number. `MAX_BULLETS = 6` was a line budget
wearing a unit's name, and nothing in the code said so because nothing had to.

`0047` §3 separated them. Six units now want up to **twelve** lines, so:

- the crossing point `0026` computed at **four entries moved to two**;
- from three entries up the page is permanently oversubscribed;
- **greedy top-first**, which `0026` §2 chose deliberately on a page with *five spare
  lines*, became a rule for dividing a page that has none.

`0026` chose greedy over round-robin and over a soft cap, and recorded that it was
choosing **blind**: *"Nothing re-renders differently, and no page tells the maker
whether he chose right."* All three candidates produced an identical page. Under
`0047` they diverge sharply, and the evidence `0026` did not have now exists.

## Decision

### 1. The per-Entry cap is expressed in lines: `MAX_BULLET_LINES = 6`

An Entry may take at most six **Bullet lines**, not six units. `MAX_BULLETS` survives
as the **candidate window** the distribution pass ranks inside; it can no longer bind
on its own, because every unit costs at least one line and an Entry out of lines has
already run out of units.

**It is the same number on purpose, and that is the claim to being a repair rather
than a new policy.** On a page of `width: 1` Bullets the two caps bind identically and
the allocation is byte-identical to `0026`'s — including every worked model in that
ADR's §2, which was computed at one line per Bullet throughout. What changes is only
the page `0047` created.

Measured on `runs/auxo-ai`, every claim at width 2:

```
                    0047 alone       with this ADR
american-express         5                3
xlscout                  2                3
auto-apply               1                2
sweatpact                1                1
                    ─────────        ─────────
                         9                9
```

**The same nine Bullets, shared.** The page did not get bigger; the top entry stopped
taking twelve lines of it.

### 2. The reserved unit is charged against the Entry's budget like any other

A block opening on a two-line Bullet has four of its six lines left. There is no
exemption for the reserved unit — it is a Bullet on the page and costs what it costs.

### 3. *The page ran out* and *this Entry is at its cap* are reported apart

They look identical on the résumé — a claim that is not there — and point at opposite
repairs:

- **the page ran out** — the bank has outgrown one page. It is about the rest of the
  page, and what changes it is a different bank or a different posting.
- **this Entry is at its depth cap** — this one block is deeper than a one-page
  résumé will show. **Nothing about the rest of the page**: a bank half this size
  would lose the same unit.

So `pack_page` writes a `depth cap:` Silent call where it wrote `shrink:`, the Entry's
own cap is tested **before** the page's remaining room so a unit refused by both is
reported against the binding one, and the Omission view carries the distinction
through to the line the maker actually reads:

```
- american-express/c7 — 0.70 — dropped at american-express's own 6-line depth cap,
  not for want of room on the page — Multi-source data analysis and automation…
```

`0026` §5 exists because that ADR was decided blind and wanted the sharing rule made
visible. This is that requirement applied to the rule that replaced it.

### 4. Greedy top-first is kept; round-robin is not adopted

`0026` §2's governing sentence — **the floor buys presence; score buys depth** —
stands. With the cap corrected, greedy no longer produces the starvation that
prompted this ADR, so there is no longer a defect for round-robin to fix, and
adopting it would reverse a decided principle to solve a problem that has gone.

**What remains true, and is the honest limit of this decision:** the guarantee is
still paid from the bottom of the placed set upward. `sweatpact` still shows one
Bullet. That is `0026` §2's stated bill and it is unchanged — presence is owed, depth
is earned.

## Consequences

- **An Entry can no longer monopolise the page.** A consequence worth naming because
  it changed a test: filling the page is now a matter of how many entries the bank
  holds, not how deep one of them is. Three entries of six two-line claims used to
  exhaust the budget and now leave room the supporting fill takes.
- **A deep Entry of two-line claims shows three Bullets.** That is the intended
  reading, not a loss: six two-line Bullets is twelve lines of one employer on a
  one-page résumé, which is not a page anyone would choose.
- **The Omission view gets longer again**, and more of it is now `depth cap` lines,
  which are the benign kind.
- **`0026` gains an Addendum**; its decision is amended, not superseded.

## Addendum, 2026-08-13 — the cap is soft

`docs/adr/0049-nothing-qualifying-is-left-out.md` §4 makes `MAX_BULLET_LINES` a **soft**
cap. An Entry may take lines past its six out of the page's residue, in Entry-score
order — **but only when every one of its placed units is a merge group.**

**The arithmetic above is untouched, and it is what bends.** The cap is still a line
budget and still the same number as `MAX_BULLETS`; a page of `width: 1` Bullets still
packs byte-identically to `0026`. What changes is that six lines is now an Entry's
*share* rather than its ceiling.

The condition is the load-bearing half. Without it, borrowing is strictly easier than
merging: a block that wanted six separate lines would buy them, the cap would bend on
every run, and `0049` §1's guarantee would be met by spending page rather than by
writing better. With it, extra lines are the reward for having compressed everywhere.

§3's two reported causes become three, and the third is the new one: a unit may now be
refused because **the block holds a lone claim and so may not borrow** — a different
line from the depth cap proper, because the remedy is different. Merge the lone claim
and the room appears.
