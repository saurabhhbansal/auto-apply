# The bad Bullets were made at compose time

**Status:** accepted

## Context

`CONTEXT.md` defines a Bullet as **the Claim's Assertion, re-angled toward the JD — not a new
sentence about the same work**. So when the maker read `runs/zs-btsa` back and found the prose bad,
the **Assertion** was a live suspect, and he raised it himself by asking that Fable be cleared to
write `ingest` as well as `tailor` (#47, #52).

The evidence was genuinely mixed, which is why this was a ticket and not an assumption.
`american-express/c4`'s Assertion reads well —

> *Automated the monthly business-review deck data cuts off scorecard data and internal data platform tables, replacing about 4–5
> hours of hand-built Excel pivoting per cycle.*

— and the Bullet composed from it is worse, which points at compression rather than at the source.
But `xlscout/c1`'s Bullet is ungrammatical, and nobody had looked at whether its Assertion was the
reason.

**The method was a read, not an argument.** All twelve Bullets of `runs/zs-btsa` were put beside the
Assertions they came from, and each fault was traced to the field it entered at.

## The read

Six of the twelve are clean: `american-express/c5` and `/c6`, `xlscout/c2` and `/c3`,
`auto-apply/c2`, `sweatpact/c3`. The other six:

| Claim | The fault | Entered at | Already covered by `0027`? |
|---|---|---|---|
| `xlscout/c1` | *"…then fixed the failures **that exposed**"* — a relative clause with no object. | **the Assertion** — the clause is in the bank verbatim: *"…then fixing the layout failures that exposed."* | **no** |
| `auto-apply/c1` | *"**Fail** the build when…"* — a bare infinitive that reads as a spec line, not as something someone did. The Assertion is past-tense and sound: *"Built a pre-render verification pass that fails…"*. Compose dropped the main clause and promoted a subordinate verb. | compose | yes — the tripwire |
| `auto-apply/c7` | *"…**which** produced **its** written design record"* — both float. The Assertion pinned the subject: *"…and **that method** is what produced a written design record…"*. Compose traded a named subject for a dangling relative to save characters. | compose | yes — quoted in the ADR by name |
| `american-express/c4` | Good Assertion, worse Bullet, and what went is *4–5 Excel files* — the only thing that says what the work actually was, and nowhere in the ZS ask. | compose | yes — §4, by name |
| `sweatpact/c1` | The Assertion's point is *"it changed his own behaviour — he went to the gym when he would otherwise have skipped."* The Bullet spends the room on `Next.js and Supabase` and ends *"used by friends"*. | compose | yes — §1 and §4 |
| `sweatpact/c2` | Drops *"a one-time setup that removed the need to remember the app at all"* — the reason the Shortcut exists. | compose | yes — §1 |

**Five of the six faults were manufactured at compose time, and `0027` names every one of them** —
two of them by quoting the exact broken string.

### The sixth

`xlscout/c1` is the only Bullet whose fault came out of the bank. Compose did not invent
*"the failures that exposed"*; it carried the phrase word for word from the Assertion, and shortening
the sentence around it is what made it audible. `0027` quotes that string as its worked example of a
**compression stump** — and the string is an Entry file's.

This exposed a real asymmetry. `0027` made *"read the line back as English"* the standard for a
Bullet; `ingest` §4's Shallowness checks are both about content — *says what changed*, *room to
re-angle* — and neither would blink at a sentence missing a word. Nothing gates an Assertion on
being a sentence.

**Put to the maker, he read the Assertion as sound at its own length.** The clause survives inside a
long sentence that supplies what it needs, and breaks only once the sentence around it is cut down —
which makes it a compression failure like the other five, not a defect in the bank.

## Decision

**1. The fault entered at compose time. `ingest` is unchanged.** No grammar check joins the
Shallowness checks, no instruction on writing an Assertion is rewritten, and Fable is not needed at
`ingest` for this. The suspect is ruled out on the record so it is not re-opened.

**2. The composition rubric gains nothing either.** The obvious addition was a line telling Opus that
the Assertion's own wording is not protected — if a clause will not survive being shortened, rewrite
it rather than carry the fragment. Rejected as already covered: *"Read the line back as English
before you keep it. Ungrammatical is not a style fault here, it is the tripwire"* fires whatever the
phrase's provenance, and `0027` puts this exact string in front of the composer as an example.

**3. This ADR changes no file but itself.** The prose fault was diagnosed and fixed by `0027`. What
`0028` adds is the confirmation that it was fixed at the right layer.

## Rejected

**Rewriting how `ingest` writes an Assertion.** The map's Out of scope already blocked re-editing the
four Entry files on disk — **Amend, never regenerate** and the **Return door** govern those — so this
was only ever a change to how the *next* Assertion gets written. The read gives it nothing to fix.

**A grammar tripwire on the Assertion at ingestion.** Live for as long as `xlscout/c1` looked like a
bank defect. It dies with the maker's reading: one Assertion in the bank contains a clause that does
not survive compression, and that is a fact about compression.

**"The Assertion is fine but the wrong shape to re-angle from."** The ticket floated this as the
interesting outcome — a sentence can be well written and still resist turning. The read does not
support it. `xlscout/c1` buries its point (*"Proved the tool generalised past the one product team it
was built against"*) behind the mechanics, and the Bullet duly kept the mechanics and dropped the
point — but that is a Bullet that failed `0027` §1, not an Assertion that could not be turned.

**"The Evidence is where the good sentence was all along."** Also floated, also not supported. The
sharpest material *is* routinely one field over — *4–5 Excel files* for `american-express/c4`,
*"Going wider was his own move, not an assignment"* for `xlscout/c1` — but the rubric already permits
the reach (*"Start from it, and reach into the Evidence for detail that is already there"*), and
`0027` §4 already names the `american-express/c4` case. The run not reaching is the compose-time
fault, not a missing permission.

## Consequences

- **`ingest` leaves this map untouched.** The only bank-side question `#47` still carries is the fog
  entry on the shallowness bar, which is about how many claims an entry owes the page — not how they
  are written.
- **`0027` is the fix.** If the prose is still bad after `#53` re-renders `runs/zs-btsa`, the next
  suspect is the rubric again, not the bank.
- **The asymmetry is recorded but not acted on.** An Assertion is not gated on being a sentence, and
  now it is written down that this was seen and left alone. If a future Assertion lands broken badly
  enough that the tripwire cannot rescue the Bullet, this is the paragraph to re-open.
