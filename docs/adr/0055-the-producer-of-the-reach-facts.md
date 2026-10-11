# The interview collects what the page reaches for

**Status:** accepted

## Context

Reading the `runs/auxo-ai` page, the maker objected to a line describing him as having
gone to other teams **"unasked"**:

> *"me saying something like I went to the other team to get something done is just me
> conversing in a normal tone, you started to write that as went to other teams unasked
> … a better version could be took initiative to go push the product."*

He read this as the bank storing his conversational phrasing and the page repeating it,
and asked for it to be fixed at ingestion.

**The word is not in the bank.** `grep -rn unasked bank/` returns nothing. `xlscout/c1`
says *"by going to Xlscout's other product teams himself"*, and its Evidence says
*"Going wider was his own move, not an assignment."* Both are good raw material for
exactly the framing he wanted.

**The word is in the tailor skill.** `0039` §5 and `tailor` §5 list five sizing facts a
Bullet should reach for, each with worked examples. Four of those examples are lifted
verbatim from the maker's Amex entry. One — *"went unasked"* — is a coined paraphrase of
`xlscout/c1` that appears in no bank file. A run reached into that list and wrote the
system's own invented phrase onto a résumé as if it were the maker's.

So the leak is real and it runs the other way: **the system's illustrations were being
read as vocabulary.**

### The second finding, which is the one worth building on

`0039` says the tailor reaches into Evidence for five facts, and that *"a claim whose
Evidence carries none of them composes without one, and that absence is a `bank-audit`
finding, never an invention."* `bank-audit` duly checks for them (Check 4). So the
**consumer** and the **auditor** were both written. Against them, what `ingest`'s depth
pass actually asks:

| reach fact | asked at ingestion? |
|---|---|
| the denominator | **yes**, explicitly |
| how far it spread | **yes** — *"who ended up using it, and are they still?"* |
| what it would have cost to get wrong | **yes** — *"what happened if it did not get done"* |
| who consumed it, and how senior | **partly** — asks *who*, never *how senior* |
| whether it was a first, or self-started | **no** |

The missing one is precisely what `xlscout/c1` needed, and it is missing for a reason
worth naming: the list asks *"who asked for it"*, which invites a name and presumes
there was one. **A self-started piece of work answers that question sounding assigned.**

## Decision

### 1. The depth pass asks all five, in forms that can come back empty

Three questions are added or sharpened:

- **who saw the output, and how senior** — *"who did that end up in front of?"*. A name
  is not the answer; where it landed is. *"my manager"* and *"senior leadership"* size
  the same artefact differently.
- **whose call it was** — *"was that asked of you, or your own move?"*, asked **whenever
  the maker describes going somewhere or doing something outside the brief**, and
  phrased so that *nobody* is an available answer.
- **whether it was a first** — *"had anyone done this before, here?"*

**The producer now matches the consumer.** A fact nobody asks for is a fact no page can
ever use, and `bank-audit` was reporting the absence of facts nothing was collecting.

### 2. The answer is recorded as the maker's account, never as résumé phrasing

*"Going wider was his own move, not an assignment"* is Evidence. *"Self-initiated
cross-team product adoption"* is a Bullet written at ingestion time, and it is refused
here for two reasons:

- **it fixes one framing into a bank that has to answer many postings.** The same claim
  is *"took the initiative to push it across the product teams"* against a role that
  wants drive, and *"debugged the layout failures ten users reported"* against one that
  wants QA. Storing the first destroys the second.
- **a stored phrase gets reused verbatim.** That is not a hypothetical: it is the exact
  failure this ADR opens on, and adding polished phrasing to the bank would make it
  systematic rather than incidental.

**The bank holds what happened; the page decides what to call it.** Since `0053` the
composer is free to frame, so the bank does not need to pre-frame — and must not.

### 3. The tailor's examples are labelled as illustrations

The five-fact list keeps its examples and gains a paragraph saying they are lifted from
one bank to show what each category looks like, that reusing their wording is how the
system's phrasing ends up impersonating the maker's, and naming *"went unasked"* as the
instance that reached a rendered page. The coined example itself is removed; §5 now
describes the category and tells the composer to read the Evidence and name it.

## Consequences

- **Existing entries are not re-interviewed.** The gap is a `bank-audit` Check 4 finding
  where it matters, and the Return door (`ingest` §8) is where a maker fills one in.
  Nothing regenerates a bank file.
- **Sittings get slightly longer**, on items where the maker describes stepping outside
  the brief. That is the trade: three questions against a fact the page cannot invent.
- **`0039` is unchanged in substance** — it already named all five. What changes is that
  something now collects them, and that its examples stop reading as approved wording.
- **This does not fix the phrasing the maker objected to by itself.** `0053` licensed
  the reframing; §3 removes the word that pre-empted it; §1 makes sure the fact behind
  it is on file for entries written from here.
