# Rendering approach: a hand-owned Jinja2 → `.tex` template, compiled by pdfLaTeX

**Status:** accepted — §"Constants" amended 2026-08-01, recorded in that section

## Context

The ticket (#12) framed this as **RenderCV vs a hand-owned `.tex` template + templating
layer**, to be decided against the hard constraints: owned hand-editable LaTeX, local compile,
one page hard, deterministic re-runs, and no schema pushed back onto the bank.

The research (#6) collapsed the titular comparison before grilling started: **RenderCV dropped
LaTeX in v2.0 (2025-01-07) and renders through Typst.** The current release emits `.typ` and
there is no flag that produces `.tex` — that code path was removed. RenderCV cannot satisfy an
owned-**LaTeX** constraint at any price.

That left the constraint itself as the only live question, and grilling reframed the ticket
accordingly: *is LaTeX the requirement, or merely "a source file I own"?* — because a
format-agnostic reading puts RenderCV back in play via `.typ`.

**LaTeX is the requirement, and the recorded reason is ATS-safety:** `.tex` via the
sb2nov/"Jake's Resume" lineage is the known-good, battle-tested one-page format against résumé
parsers. Typst output is not. This reason is load-bearing well beyond the file extension — it
constrains the engine, the template, and the escape hatches available when the page runs tight.

A second candidate surfaced mid-grilling: the **Rezi MCP server** (`list_resumes`,
`read_resume`, `write_resume`; OAuth 2.1; Rezi Pro). It is dealt with under "Considered
options" — briefly, it exposes no render tool at all, so it cannot produce the PDF, and its
export formats are PDF/DOCX/Drive with no `.tex` anywhere.

## Decision

### The template is a Jinja2 file that generates the whole `.tex`

`templates/resume.tex.j2` — a fork of sb2nov "Jake's Resume" (MIT) — is the hand-owned
skeleton: preamble, `\resumeItem` macros, section scaffolding, with holes for the static
profile, the entry blocks, the bullets, and the skills line. Each run renders it **whole** into
`runs/<jd-slug>/resume.tex`.

Jinja2 is instantiated with LaTeX-safe delimiters (`\VAR{...}`, `\BLOCK{...}`, `\#{...}`) and
`autoescape=False`, since the defaults collide with LaTeX's own `{}`, `%` and `#`.

The survey's (#5) "borrow section-only regeneration" idea — keep a master `.tex` as source of
truth and rewrite only named `\section{}` bodies — is **rejected**. That technique exists to
preserve a human's *prose* in untouched sections; here the prose comes from the bank and is
composed fresh per JD, so what actually needs protecting is the preamble and macros, which
templating protects for free. Splicing would additionally require a `.tex` parser and would
make the master document a **second store of content competing with the bank**, which `0005`
established as single source of truth.

You hand-edit the template for looks, or a run's `resume.tex` for a one-off fix. Both are
yours; neither is generated from the other.

### Opus never writes LaTeX — it phrases, the script typesets

This extends `0006`'s seam by one step. Opus emits **plain prose with no markup**;
`tools/render.py` escapes `& % $ # _ { } ~ ^ \` mechanically on every hole via an explicit
Jinja filter. Nothing Opus writes can break a compile or smuggle formatting in.

Inline markup — even a one-rule `**bold**` allowlist — is **rejected**: emphasis would become a
per-run model judgment for no traceable gain. Emphasis lives in the template (bold section
labels), never in the data.

This also gives the trace check a clean plain-text target *before* anything compiles.

### Every bullet cites its source claim id

`runs/<jd-slug>/bullets.md` is what Opus writes and `render.py` reads:

```markdown
## stripe-payments-eng   (3 slots)
- [c2] Cut checkout p99 latency ~40% by introducing a read-through cache ...
- [c5] Owned ledger reconciliation across three payment processors ...
- [c1] Led a 4-engineer team through the migration off the legacy gateway ...

## Skills
Languages: Go [stripe-payments-eng/c2], Python [etl-tool/c1]
Infra: Kubernetes [stripe-payments-eng/c4], Terraform [homelab/c2]
```

The citation is what makes the **Number-trace check** of `0003` a *lookup* rather than a
search. Grepping the whole bank for a matching `40%` would find *a* claim, not *the* claim, and
a number that happens to match a different entry would pass falsely — a check that can pass
falsely is not a backstop.

**Bullet ↔ Claim is 1:1** (see Consequences — this corrects `0004`).

### Lints: trace pre-compile, page-count post-compile

```
bullets.md
   ├─► [length lint]  bullet > CHARS_PER_BULLET → FAIL, name bullet + claim id
   ├─► [Number-trace check]  every number & skill → cited claim, equal-or-softer → FAIL
   ▼
resume.tex ──► pdflatex ──► resume.pdf
                              └─► [page-count assert]  pages > 1 → FAIL
```

- **Trace runs pre-compile**, on plain text. It is cheap, it fails before a compile is spent,
  and it avoids extracting text from a PDF — fragile under ligatures, hyphenation and line
  breaks. Since render is a mechanical escape-and-substitute, `bullets.md` → PDF is a faithful
  transform; linting the PDF would only catch template bugs, which the page-count assert
  already covers.
- **Trace covers the skills line too**, not just bullets: a listed skill must appear in the
  `skills:` line of the claim it cites. There is no path to a skill on the résumé that no claim
  supports.
- **An over-length bullet fails and is named**; Opus rephrases that one bullet shorter and
  re-renders. `0006`'s literal wording allowed "or be dropped" — **dropping is rejected**: a
  slot the packer *earned* for a claim would vanish because a sentence ran four characters
  long, silently changing what the résumé argues. Truncation is rejected outright, since a cut
  sentence can change what a claim asserts and break the trace guarantee.
- **The page-count assert is post-compile and hard-fails**, per `0006` — a lint, never a
  render-trim loop. Because every bullet already passed the length lint, reaching page 2 means
  the **constants are miscalibrated**, which is a template-level recalibration event, not a
  per-run one.

### Engine: pdfLaTeX, via TinyTeX

The engine is fixed at **pdfLaTeX** — the one "Jake's Resume" is proven on. **tectonic is
rejected** despite being the smaller, tidier, single-binary option: it is XeTeX underneath, and
since ATS-safety is the entire reason for choosing LaTeX, quietly changing engines would put
font embedding and glyph packages back in play and make ATS-safety something to re-prove rather
than inherit. Tectonic's first compile of a package set also needs the network.

**TinyTeX** provides it: a few hundred MB, fully offline once installed, package set curated
via `tlmgr`. No network anywhere in a run. A full TeX Live satisfies the same contract.

Determinism comes from pinning the package set, setting `SOURCE_DATE_EPOCH`, and never using
`\today` or any other time-varying construct.

### Constants: this decision fixes the procedure, not the numbers

`0006` deferred the page-budget constants here. They are **measurements, not decisions** — you
cannot know where a bullet wraps without compiling the template and looking. The map forbids
prototypes and spikes and the destination is zero code, so producing real numbers is out of
bounds this session, and inventing plausible ones is unacceptable in a project whose north star
is zero fabrication.

So the ADR fixes **one named constants block** in `tools/config.py`, read by both `pack.py` and
`render.py`:

```python
PAGE_LINES         = <calibrate>   # usable body lines on one page
HEADER_LINES       = <calibrate>   # static profile block
SECTION_LINES      = <calibrate>   # per \section{} heading
ENTRY_HEADER_LINES = <calibrate>   # per entry title/org/dates line
CHARS_PER_BULLET   = <calibrate>   # one-line bullet budget
```

**Calibration procedure** (run once at build, re-run whenever the template changes):

1. Fill the template with filler bullets of known character lengths.
2. Compile; find the length at which a bullet wraps to a second line → `CHARS_PER_BULLET`.
3. Add entries until page 2 appears → `PAGE_LINES`, and the per-block overheads.
4. Record the values in `tools/config.py` with the date and template commit they were measured
   against.

A constants change alters selection output, so it is a recorded event, not a silent edit — the
same discipline `0006` set for ε and the bullet floor.

#### Amended 2026-08-01: "one block" was one *home*, and the build found two

Building the packer and the renderer (#22, #23, #24) put two more numbers on the page budget, and
neither is in `config.py`. This section said "one named constants block" because at the time there
was only one *kind* of number to hold. The line the build actually drew is sharper than a count,
and it is the reason the five names stayed five.

**`config.py` holds what was measured against the template** — exactly the five above, and nothing
else. Its docstring pins a calibration date and the template's blob hash and instructs a re-run of
`docs/calibration.md` whenever either moves. That is a promise about the *whole file*, so every
number living under it has to be a fact about `templates/resume.tex.j2` and about nothing else.

**`pack.py` holds the overhead the packer spends**, next to `bullet_budget()`, the only function
that reads it:

```python
EDUCATION_ROWS = 1   # rows the fixed overhead is charged for
SKILLS_LINES   = 1   # the Skills breadth list
```

`EDUCATION_ROWS` is not a measurement of the template at all — it is the count of `### ` rows in
`bank/profile.md`, which is to say how many schools the maker has. Filed under `config.py`'s
docstring it would make that docstring false: a bank edit no calibration re-run can see would
silently invalidate a file whose central claim is that it is re-measured whenever the template
changes. It is held in step by other means instead — `tests/test_pack.py` reads the real profile,
so a second school fails a test rather than a résumé.

`SKILLS_LINES` is genuinely measured, and the calibration probe re-derives it on every run. But
`docs/calibration.md` writes it into the overhead formula as an unconditional `+ 1`: it is a
readable name for a term the budget always pays, not a knob calibration turns. The probe's job is
to confirm the template still deserves the `+ 1`, and if it ever does not, the fix is to tighten
the template rather than to grow the number.

**`render.py` imports `pack.py` on purpose, for one value.** `import pack  # for EDUCATION_ROWS`
sits beside `import config` at the top of the renderer, and it is there so the renderer can check
the Education rows it is about to typeset against **what the budget was charged for**. The packer
is bank-blind by design (`0006`) and cannot count schools; the renderer parses `bank/profile.md`
and can. So the component that reads the bank audits the component that spends the budget, and a
second school fails at parse time naming the line to edit — instead of surfacing as a two-page PDF
that the page-count assert blames on the constants. The dependency runs one way only:
`render.py → pack.py → config.py`, and `pack.py` stays stdlib-only per "Form" below.

**What the split protects is the count, and the criterion behind it.** The rule is not "the repo
contains five page-budget numbers"; it is **`config.py` holds exactly the numbers the calibration
procedure measures against the template, and there are five of them.** A number that moves when the
template moves is a calibration constant and has to live there — which is why `0017` can still
reject a header character-count constant on the ground that "the block would go from five names to
seven", and why `docs/calibration.md` can still tell the maker that a failing probe check is fixed
by tightening the template rather than by adding a sixth constant. Both passages hold as written.
What `pack.py` may hold is the complement: a number the calibration does not measure. Anything
else earns its place in `config.py` or does not exist.

### The run folder, and the JD-input seam

```
runs/<jd-slug>/
  jd.md           you paste the JD here            (the seam)
  scores.md       Opus — claim scores + reasons    (0006)
  allocation.md   pack.py — slots + silent-call log (0006)
  checkpoint.md   Opus's angle + forks + your answers (0002)
  bullets.md      Opus — composed bullets + skills, with claim ids
  resume.tex      render.py
  resume.pdf      pdflatex
  gaps.md         the Gap report                   (0001)
```

Committed to git, in full. `0005` deferred the run-artifact layout to this decision; `0006`
pinned two of the files; this pins the rest, including where `0002`'s Checkpoint record lives.

**The JD-input seam is simply that the JD is a file.** Nothing downstream knows or cares where
`jd.md` came from. Today you paste into it; a scraper later writes the same file. That keeps
auto-scraping (explicitly out of scope) a **swap, not a rewrite** — which is what the ticket
asked this decision to record.

**You create the folder and choose the slug.** Slug derivation by Opus is **rejected**: it puts
a model judgment at the very first step of the pipeline, and a re-run could land on a different
path — which would destroy `0006`'s core debugging story, since "debug a bad selection by
reading a diff" requires the re-run to overwrite the *same* files.

### Form: `tools/render.py`, Jinja2-pinned

One Python file: reads `bullets.md` + the bank + `allocation.md`, runs the length and trace
lints, renders the template, shells out to `pdflatex`, asserts the page count.

**Jinja2 is a dependency** — the project's first, and pinned. It breaks `pack.py`'s
stdlib-only rule knowingly. A stdlib `string.Template` approach would push the loops over
entries and bullets into Python, splitting the template between the `.tex.j2` file and the
code that drives it — which directly undercuts the thing this decision exists to protect: **one
hand-editable template file the maker owns.** `pack.py` stays stdlib-only; the dependency is
confined to rendering.

## Consequences

- **Bullet ↔ Claim is 1:1. This corrects `0004`.** `0004` allows "a Bullet that combines
  claims, traceable claim-by-claim", and `CONTEXT.md` defines a Bullet as "composed per-JD from
  one or more Claims." `0006` had already made that untrue in practice — slots are
  `min(3, claims ≥ 0.50)`, one slot per qualifying claim — and single-id citation confirms it.
  `CONTEXT.md` is updated. This is a correction, not a gap, in the same way `0006` corrected
  `0001` on sampling variance.
- **The trace checker is a second mechanical reader of the bank.** `0005` justified pure prose
  markdown on "there is no mechanical selector"; this is a mechanical *linter*. It survives only
  because `0005` fixed `number: 40%` and `skills:` as loose `key: value` lines that a regex can
  read. **Those two lines are now load-bearing structure** — a future tidy-up that folds them
  into prose would break the trace check. `0006`'s reconciliation still holds: machine-readable
  structure lives at the run-artifact layer, and the only thing read mechanically from the bank
  is a value `0005` already specified as a `key: value` line.
- **Two-column density is no longer an escape hatch.** `0005`'s survey kept Deedy-style
  two-column layout as a fallback for a tight page. Single-column is now load-bearing for
  ATS-safety, so a tight page is solved by cutting content — never by layout tricks.
- **The structured export seam is `bullets.md` + the bank, not the `.tex`.** Any future export
  (a Rezi sync, a JSON Resume export view) reads the structured intermediates that already
  exist one step before rendering. **Parsing `resume.tex` back into structure is the wrong
  direction** — it reconstructs information the pipeline already had. Recorded here so the door
  is not nailed shut; the work itself is out of scope for v1.
- **#16 gains a second concrete candidate.** Alongside `pack.py`, the render + compile step is
  now a real thing to judge "does this warrant an MCP server?" against.
- **#14 gains a candidate external signal.** Rezi's ATS scoring could serve as an independent
  quality check on a finished PDF, sitting *outside* the pipeline where it cannot touch
  traceability or determinism.
- **Build-time residual:** the constants block is unfilled by design. First build runs the
  calibration procedure above before the packer produces meaningful allocations.

## Considered options (rejected)

- **RenderCV** — rejected on the research's dominant fact: since v2.0 it emits Typst, not
  LaTeX, and no flag recovers a `.tex`. Under a format-agnostic reading it was viable (`.typ`
  is genuinely owned, editable and offline-compilable, MIT, well maintained) — but the LaTeX
  constraint held on ATS grounds. It would additionally have imposed its closed set of 8 typed
  entry shapes as the render contract, and enforces no one-page limit.
- **Rezi MCP server** — rejected on four independent grounds, none of them price. It exposes
  **no render tool**, so it cannot produce the PDF at all: adopting it adds a dependency without
  removing any pipeline stage. It offers no `.tex` (PDF/DOCX/Drive only). It requires network
  and OAuth per run, defeating local compile and pinned determinism. Its fixed section taxonomy
  (contact/summary/experience/education/skills/projects/certification/coursework/involvement/
  awards) is the same schema trap as RenderCV and JSON Resume, which the map's standing
  preference rules out. Its docs also do not state whether `write_resume` passes bullet text
  through verbatim or lets Rezi's AI rewrite it — undocumented rewriting cannot sit inside a
  pipeline whose guarantee is that every rendered word traces to a claim. Kept as a **v2
  export target** (out of scope) and a **#14 evaluation candidate**.
- **Master `.tex` + section splicing** — rejected under "The template" above.
- **Opus writing `.tex` freehand** — rejected: escaping correctness and compile-validity move to
  the model, and determinism drops.
- **tectonic** — rejected under "Engine" above: wrong engine for an ATS-proven pdfLaTeX
  template.
- **Ballparking the constants now** — rejected: they would be reasoned-at rather than measured,
  in a project whose north star is zero fabrication.
- **Dropping or truncating an over-length bullet** — rejected under "Lints" above.
- **Skills drawn only from placed entries** — rejected: it would kill a Nice-to-have whose entry
  lost the page competition, defeating `0001`'s tiered-real-estate design in which the Skills
  breadth list is the cheap space where Nice-to-haves survive.
- **Opus writing the skills line freehand from the JD** — rejected on zero-fabrication grounds:
  the direct route to claiming a skill no claim backs.
- **`runs/` gitignored** — rejected: it would discard the diffable audit trail `0006` made the
  Decisions record.
