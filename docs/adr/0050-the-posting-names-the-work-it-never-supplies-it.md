# The posting names the work; it never supplies it

**Status:** accepted

## Context

`0044` gave the Summary one relaxation: the posting may lend it **vocabulary**, so
work the bank describes as *"benchmarked four translation model backends"* may be
written as *"model evaluation and optimization"*. `0027` §3 kept every Bullet under
the older, stricter rule — *the posting may never supply a word* — with the Evidence
as the test.

The maker asked for that relaxation to reach the Bullets, and for the Skills rows to
carry terms the posting names that sit close to what the bank holds:

> *"The correct method would be to rename work the bank holds and then stuff that has
> no evidence into the skills section, but we need to only pick the similar ones not
> say i have a python resume and we put web dev stuff, so basically have an expanded
> radius of what my skills have."*

Both halves are in that sentence, and so is the boundary: **an expanded radius, not a
different subject.**

## Decision

### 1. The Summary's relaxation extends to every Bullet

`0027` §3 is reversed for the Bullet, on `0044`'s exact terms and no wider:

> **A keyword is a name for something; a fact is a claim about the candidate. The
> posting supplies names. It supplies no facts.**

| | |
|---|---|
| **licensed** — renaming | Evidence: *benchmarked four translation model backends* → **`model evaluation`** |
| **licensed** — renaming | Evidence: *the internal metrics platform* → **`ClickHouse`**, where the Evidence says so |
| **forbidden** — re-scoping | the JD asks `TensorFlow`; the bank holds no model he trained → **it does not go in** |
| **forbidden** — a fact | `led a team of four`, `3 years' experience` → **no headcount, seniority or duration the bank does not hold** |

**Everything else in `0027` is untouched and still outranks this.** A Bullet is still
a complete sentence that says what changed; the number still traces; the JD still does
not decide what goes in the sentence's interior (§4); the detail that makes a claim
specific is still kept even where the posting never asked for it. This licenses a
**substitution of names**, never an addition of content.

**The interview test binds exactly as before**, and it is the only test that matters:
the maker has to defend this line in the room. A renaming he cannot defend as a name
for his own work is a re-scoping wearing a synonym.

### 2. The Skills rows may carry a term the bank generalises to

Today a skill must appear verbatim in its cited Claim's own `skills:` line. That
widens by one rule, and the rule has a direction:

> **Generalisation is licensed. Specialisation is not. Substitution is not.**

| bank holds | posting asks | verdict |
|---|---|---|
| `PostgreSQL` | `SQL` | **yes** — the general category of the specific thing he used |
| `Kafka` | `event streaming` | **yes** — same |
| `BigQuery` | `data warehousing` | **yes** — same |
| `Python`, `pandas` | `NumPy` | **no** — a sibling tool, not a generalisation |
| `Python` | `Django` | **no** — specialisation; the radius does not reach a domain he has not worked in |
| `PostgreSQL` | `MySQL` | **no** — substitution; a different product |

**The test, stated so it can be applied rather than felt:** *is the posting's term a
name for a class the bank's skill is a member of?* If yes, someone who did the work
the Claim describes did the thing the posting names. If it is a sibling, a
specialisation, or a different subject, they did not, and the term is a `gaps.md`
line exactly as it is today.

**The maker's own worked example is the boundary condition and is quoted in the skill:
a Python bank does not license web-development rows.** `Python → Django` fails on
direction, and `Python → React` fails on subject as well.

### 3. What survives unchanged, because it is what keeps this honest

- **The row still cites a Claim** — the one whose specific skill the term generalises.
  A generalised term with no cited instance is a skill from nowhere.
- **A row label must still be traceable to words in the JD**, a row still needs two
  skills, and a skill still appears in exactly one row (`0020`).
- **They must read as skills.** A generalisation that is really a job description
  (*"cross-functional delivery"*) is not a skill row's business.
- **A term outside the radius is a Gap line**, and the Gap report is where this
  decision's honesty lives. Widening the radius to empty the Gap report is the way
  this goes wrong.

### 4. Why the radius sits in the Skills rows and not in the Bullets

A Skills row asserts *"I can do this"*, and generalising from a specific instance to
its class keeps that assertion true. A Bullet asserts *"I did this, here, and it
changed that"* — a claim about an event, which no generalisation preserves. So §1
gives the Bullets **renaming** and §2 gives the Skills rows **generalisation**, and
those are different licences on purpose.

## Consequences

- **`0027` §3 is reversed for Bullets** and gains an Addendum saying so. §4 — *the JD
  does not decide what goes in the sentence* — is explicitly **not** reversed, and the
  two are easy to confuse: the posting may now supply the *word* for a thing the
  Evidence carries, and still may not decide *which* things the sentence mentions.
- **`0020` §3's *no expanding, contracting or respelling*** now has one exception,
  bounded by §2's direction rule.
- **The coverage read (`0041`) will report more terms answered**, and its warning that
  it produces leads rather than findings matters more, not less.
- **This is the decision most likely to put an indefensible line on the page**, and it
  is recorded plainly: the guard is the interview test and the direction rule, both of
  which are judgement, and neither of which `render.py` can check.
