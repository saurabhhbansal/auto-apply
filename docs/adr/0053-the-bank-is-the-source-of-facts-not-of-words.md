# The bank is the source of facts, not of words

**Status:** accepted

## Context

`runs/auxo-ai` was re-run end to end under `0047`–`0052`. It rendered one page, eleven
Bullets, five of them merges, and every qualifying claim on the page. The maker read
it and made two complaints, which turn out to be one problem seen from both ends:

> *"the bullets have started to read as disjoint statements merged together by commas"*

> *"sweatpact project is still just a single line even after directions to cover the
> whole story and not just 1 point"*

The offending line, verbatim from that run:

> *Took the pipeline unasked to other teams, ~95% of manuals came out usable; pinned
> translated tables to their source box as images; shipped it as a Streamlit app the
> manual writers ran themselves*

Three verbs, three subjects, no single X. It is **true**, it **traces**, and it passed
the merge verifier. It is also not a sentence anyone would write.

### Why the lines came out as lists, exactly

Not because merging is wrong. Because **rule 2 bound every word to the Evidence.**
Downgrade-only composition means each cited claim's substance has to survive into the
line more or less as the bank states it, so fusing three claims necessarily produces
three clauses. The comma-list is not a failure of composition; it is the only shape
rule 2 permits for a three-claim merge.

`0034` §4 made this explicit and load-bearing: *asserting anything about their
relationship that no cited Evidence states is forbidden — the merge does the
compression, the entry's lead does the synthesis.* A sentence with **one** X over
three claims is exactly such an assertion. The rule that keeps the page honest is the
same rule that makes the page read badly.

### The arithmetic says compression is not optional

The maker asked whether ranking entries as wholes — best three jobs, best two projects,
each explained fully — solves it. It does not, and the numbers say why:

```
24 claims · 4 entries · 31 lines for headers and Bullets
  entry headers 8 + leads 4     = 12
  left for Bullets              = 19  →  9 Bullets at two lines each
  24 claims ÷ 9 Bullets         = ~2.7 claims per line
```

**About three claims per line is forced by the page**, whatever the entry caps say.
Which entries place changes nothing about it. The only free variable is whether that
line is a **list** or a **sentence** — and that is a question about wording, not about
selection.

### What the maker released

> *"you have full permission to rewrite those wording, you don't have to stick to the
> same wording as the bank. Bank is the source of truth not a lift and shift — it's
> something like me telling you these are the details of my work but you frame it
> better than what I had told."*

That is the constraint whose removal makes a three-claim merge writable as one
sentence. It is also the strictest guard this system had.

## Decision

### 1. Rule 2 binds facts, not words

The rule was: *every claim in a Bullet — metric, scope, technology, outcome — must be
present in or entailed by the cited Claim's Evidence*, and rewording spends a claim's
truth **down**, never up.

It becomes:

> **Every FACT in a Bullet must be present in or entailed by the cited Claims'
> Evidence. The words are the composer's.**

| | |
|---|---|
| **free** | word choice, sentence shape, clause order, voice |
| **free** | naming the theme two or three claims share |
| **free** | **synthesis** — saying what the cited claims add up to |
| **forbidden** | a **number** no cited claim carries, or one rendered flatter than its provenance |
| **forbidden** | a **technology**, **scope**, **audience** or **outcome** no cited claim carries |
| **forbidden** | **seniority, headcount, duration or title** the bank does not hold |
| **forbidden** | promoting scope — *contributed to* never becomes *owned* |

**The interview test is now the whole of the guard, and it is unchanged:** the maker
has to defend this line in the room. What changes is that he defends the *claim the
sentence makes*, not the *provenance of each word in it*.

### 2. `0034` §4's ban on synthesis is lifted; its ban on invention is not

*The merge does the compression, the entry's lead does the synthesis* is reversed for
the Bullet. A merged Bullet may now assert the thing its cited claims have in common
and lead on it.

**What survives, and it is the part that matters:** the merged sentence may still not
carry a fact none of its claims holds. Naming three pieces of work *"the pipeline's
adoption"* is framing; saying it reached *"eleven teams"* when no Evidence counts them
is invention, and it is exactly as forbidden as it was yesterday.

### 3. A placed Entry shows all of its claims, not only the qualifying ones

`0049` §1 guaranteed the page to every claim at or above the `0.50` Bullet floor. That
is why `sweatpact` rendered one line: four of its five claims scored `0.20` against an
AI posting, so the guarantee never reached them.

The maker's answer is that an Entry is now ranked **as a whole** — if it earned the
page, it tells its whole story:

> **Every claim of a placed Entry reaches the page.** The Bullet floor no longer
> filters inside a block; it survives only where it always mattered, in deciding which
> Entries compete at all.

The floor keeps its other job: `Entry.slots` and the reservation queue still read
qualifying claims, so an Entry with nothing above the floor still does not place.

### 4. The merge verifier polices facts, not framing

It was asked two questions: does the line assert anything about these claims **or their
relationship** that the Evidence does not carry, and is every cited claim represented.

The relationship half is now legal, so it must stop being asked — left as written it
would flag every well-written merged line on the page, and a check that fires on
correct output trains its reader to ignore it. It is re-scoped to:

> **Does the line state a fact — a number, a technology, a scope, an audience, an
> outcome — that none of the cited Evidence carries?**

Coverage is unchanged: every cited claim must still be represented in the line, not
merely named in the ref.

## Consequences

- **This is the largest reduction in guarantees this system has made.** Until now every
  word on the page could be traced to something the maker said at ingestion. From here
  only every *fact* can. A line that is factually clean and rhetorically inflated is
  now possible, and no script can catch it — `render.py` checks numbers, citations,
  lengths, openers and spelling, and none of those read meaning.
- **The cold read (§5.05) and the interview test carry the weight the trace used to.**
  They were belt-and-braces; they are now the braces.
- **`sweatpact` will grow from one line to two or three**, and its claims are unrelated
  to each other and to this posting. It is the hardest test of §1 on the current bank:
  if any block is going to read as an inflated list, it is that one.
- **`0027` §1's completeness standard becomes the operative test of a Bullet**, since
  the vocabulary rule that used to do most of the work is gone.
- **`0034` §4 and `0049` §1 are amended**, and both gain Addenda.
- **The Gap report is unaffected.** A term the bank cannot support is still a gap line;
  framing freedom is not evidence.
