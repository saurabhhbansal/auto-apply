#!/usr/bin/env python3
"""The plain-English read — every Claudish marker on the page, found in one go.

    python tools/plainish.py runs/<jd-slug>
    python tools/plainish.py runs/<jd-slug> --paw

A reading aid, not a lint. It runs at `tailor` §5.06, after `bullets.md` is whole,
and it is **advisory**: it prints, it never rewrites, and it exits 0 whatever it
finds (docs/adr/0056-the-bullet-is-written-in-plain-english.md §3). The standing is
`xray.py`'s and `coverage.py`'s, and for the same reason — what it matches is a fixed
vocabulary, and a fixed vocabulary cannot tell `row-level security` from `the security
surface`. Its findings are read, not obeyed.

WHAT IT READS FOR. `.claude/skills/tailor/plain-english.md` is the voice every composed
line is written in, adapted from `claudish-to-english` in
`github.com/programasweights/claudish`. Seven families of marker come out of that spec
and are matched here:

    contrast    a rejected alternative the sentence did not need
    aphorism    a verdict, a slogan, or emphasis announcing itself
    metaphor    a figurative verb or noun standing where the actual action belongs
    compound    an X-gated / X-backed / X-driven abstraction to decompress
    list        a colon, a semicolon or an em dash holding claims in a row
    category    `the <something> arithmetic` — the class of the thing, not the thing
    abstraction three or more nominalisations in one line — clauses turned into nouns

    <line> <family> <matched> — <the prose>

CITATIONS ARE CHECKED TOO, and that half is not about voice. Composing for voice means
rewriting a line, and a rewrite is where a citation gets lost or a claim quietly stops
being represented. Every Bullet's ref is read back against `allocation.md`'s units, in
page order, so the file can be checked on its own before a compile is spent. `render.py`
fails the run on the same mismatch; this names all of them at once and names nothing
`render.py` would let through.

    citation <finding>

WHAT IT WILL NEVER DO IS REWRITE A LINE. `--paw` runs `claudish`'s own ProgramAsWeights
translator (`to_english`, e469f61ccab2699fbd51) over each composed line and reports how
much shorter the translation came back and which of the line's figures and names it
dropped. **Its output is never printed as a replacement and never written anywhere**,
because the spec that program implements prefers semantic compression and a Bullet has no
redundancy to compress — run over final text it takes facts, and among the first it takes
is the reach fact (`0056` §"The trap").

    paw <line> <ref> -<pct>% kept <n>/<m>
    paw <line> dropped <the figures and names the translation did not carry>

READ THE DROP LIST, NOT THE PERCENTAGE. The percentage was measured over 40 composed lines
and it does NOT separate register from density: the interpreter is a 0.6B model, and on a
line written to the full 198-character budget it stops paraphrasing and starts summarising,
so it takes a third off a plain line as readily as off a Claudish one — a line about
choosing a translation model per language tripped no marker in this file and still came
back 73% shorter, as *"For Spanish, use Gemini; for Japanese, use Qwen."* (`0056` §4). What survives the
measurement is the negative result, which is the one this pipeline needed: **a compressing
translator cannot be let near a finished Bullet.** The drop list is the useful half — it
names which of a line's facts a paraphrase reaches for first, and those are the facts worth
re-reading in the Evidence.

The dependency is optional and unvendored — `programasweights` builds `llama-cpp-python`
and downloads a model, which no run may require. Point `PAW_LIB` (or `--paw-lib`) at an
install directory if it is not on the default path; without it the flag prints one line
saying so and the rest of the pass runs.

The parse of `bullets.md` and `allocation.md` comes from `render.py`, for the reason
`lengths.py` borrows `row_lines`: a second copy that drifted would report on a page the
run does not have.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render  # noqa: E402  (parse_bullets, parse_allocation — one parse, not two)

#: The public `to_english` program from github.com/programasweights/claudish.
PAW_TO_ENGLISH = "e469f61ccab2699fbd51"

#: Compounds that are the standard name for the thing rather than an abstraction to
#: decompress. `plain-english.md` §1.2 names the first two; the rest are ordinary
#: English or this bank's own vocabulary.
STANDARD_COMPOUNDS = frozenset(
    {
        "server-side",
        "client-side",
        "row-level",
        "self-serve",
        "end-to-end",
        "open-source",
        "real-time",
        "line-by-line",
        "head-to-head",
        "cross-team",
        "one-click",
        "lock-screen",
        "home-screen",
        "native-speaker",
        "per-user",
        "per-job",
        "per-cycle",
        "multi-source",
        "single-page",
        "full-stack",
        "constant-time",
        "read-only",
        "double-entry",
        "high-level",
        "top-level",
        "entry-level",
        "first-year",
        "final-year",
    }
)

#: `(family, pattern)`, in the order they are reported. Every one of them is a marker
#: `plain-english.md` names; nothing here is a guess about style.
MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "contrast",
        re.compile(
            r"\brather than\b"
            r"|\binstead of\b"
            r"|\bnot (?:a|an|the|just|merely|only)\b[^,;]{0,40}\bbut\b"
            r"|,\s+not\b(?=\s+\w)"
            r"|\bless\b[^,;]{0,30}\bthan\b"
            r"|\bpast (?:its|his|their|the) (?:team|own|first)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "aphorism",
        re.compile(
            r"\bthat (?:distinction|boundary|difference) matters\b"
            r"|\bthe (?:key|whole|real|actual|deeper|honest) (?:point|distinction|question|constraint|shape|answer|take)\b"
            r"|\bcannot (?:bluff|lie|pretend)\b"
            r"|\bin other words\b"
            r"|\bput differently\b"
            r"|\bwhat (?:actually|really) (?:matters|changed)\b"
            r"|\bthe load-bearing\b"
            r"|\bthe smoking gun\b",
            re.IGNORECASE,
        ),
    ),
    (
        "metaphor",
        re.compile(
            r"\bload-bearing\b"
            r"|\bgated\b"
            r"|\bthe spine\b"
            r"|\bthe \w+ surface\b"
            r"|\bsurfaced\b"
            r"|\blanded\b"
            r"|\bheld (?:the|its|his|their) \w+ (?:on|to|at)\b"
            r"|\bhonest to\b"
            r"|\bkept? (?:the|it|its) \w+ honest\b"
            r"|\bkeeps? (?:the|it|its) \w+ honest\b"
            r"|\bprov(?:ed|ing) (?:the|it|that|his|its)\b"
            r"|\bdrove\b|\bdriving\b"
            r"|\bbounded what\b"
            r"|\bthe frontier\b|\bthe regime\b|\bthe trajectory\b|\bthe floor\b"
            r"|\bhandoff\b"
            r"|\bown(?:ed|ing|s)? the \w+ (?:arithmetic|surface|layer|path|story)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "compound",
        re.compile(
            r"\b[a-z]{3,}-(?:gated|backed|side|level|first|safe|matched|layer|surface|path|boundary|driven|shaped|aware)\b",
            re.IGNORECASE,
        ),
    ),
    ("list", re.compile(r"[:;]\s|\s—\s|\s--\s")),
    (
        "category",
        re.compile(
            r"\bthe \w+ (?:arithmetic|handling|posture|stance|framing|cadence|calculus)\b",
            re.IGNORECASE,
        ),
    ),
)

#: A nominalisation — a verb or an adjective wearing a noun suffix. One is ordinary
#: English; `plain-english.md` §1.2 is about the pile-up, so this is counted rather
#: than matched, and only a line carrying NOMINALISATION_DENSITY of them is reported.
NOMINALISATION = re.compile(r"\b\w{4,}?(?:tion|sion|ment|ance|ence|ility|ism)s?\b")

#: How many it takes. Three is the point at which the clause the sentence should have
#: been written as has gone: *enforced provenance constraints and prevented model
#: hallucinations by pairing a pre-render verification pass with…* carries exactly
#: three and says two things.
NOMINALISATION_DENSITY = 3

#: A figure, in the shapes `render.py`'s own number rules allow on the page — the
#: softened forms of `0054` included, since the PAW comparison is about whether a
#: figure survived at all.
FIGURE = re.compile(
    r"(?:~|over |more than |at least |about )?\d[\d,]*(?:\.\d+)?\+?\s?%?", re.IGNORECASE
)

#: A technical or proper-noun token — the second half of what the PAW comparison counts
#: as a fact. Mid-sentence capitals and the dotted/plus stack spellings catch the tech;
#: the match at position 0 is discarded by `facts()`, being the Bullet's own opener.
TOKEN = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:[.+#-][A-Za-z0-9]+)*\b")

#: Openers are capitalised because they open, not because they are names.
STOPWORDS = frozenset({"A", "An", "The", "It", "Its", "He", "His", "They", "I"})


@dataclass(frozen=True)
class Line:
    """One composed line of the page, with where it is and what cites it."""

    number: int
    ref: str
    text: str


def composed_lines(run_dir: Path) -> list[Line]:
    """Every line on the page a person wrote — Summary, leads, Bullets, tails.

    Skills rows are left out: a row is a comma list of names, so no register rule in
    `plain-english.md` can apply to one and every marker it matched would be noise.
    """
    bullets, _rows, leads, summary, supporting = render.parse_bullets(
        run_dir / "bullets.md"
    )
    text = (run_dir / "bullets.md").read_text(encoding="utf-8").splitlines()

    lines: list[Line] = []
    if summary:
        number = next(
            (n for n, raw in enumerate(text, 1) if raw.strip().lower() == "## summary"),
            0,
        )
        lines.append(Line(number + 1, "summary", summary))
    for slug, lead in leads.items():
        number = next(
            (n for n, raw in enumerate(text, 1) if raw.strip() == f"Lead: {lead}"), 0
        )
        lines.append(Line(number, f"{slug}/lead", lead))
    lines.extend(Line(b.line, b.ref, b.text) for b in bullets)
    lines.extend(
        Line(row.line, row.ref, row.tail) for row in supporting if row.tail is not None
    )
    return sorted(lines, key=lambda line: line.number)


def markers(text: str) -> list[tuple[str, str]]:
    """`(family, the matched words)` for every marker in one line, in report order."""
    found: list[tuple[str, str]] = []
    for family, pattern in MARKERS:
        for match in pattern.finditer(text):
            matched = match.group(0).strip()
            if family == "compound" and matched.lower() in STANDARD_COMPOUNDS:
                continue
            found.append((family, matched))
    piled = [match.group(0) for match in NOMINALISATION.finditer(text)]
    if len(piled) >= NOMINALISATION_DENSITY:
        found.append(("abstraction", ", ".join(piled)))
    return found


def citation_findings(run_dir: Path) -> list[str]:
    """Every Bullet ref read back against the units `allocation.md` granted.

    A voice rewrite is a rewrite, and this is what says the rewrite kept its provenance:
    same refs, same order, one Bullet per unit. Silent when there is no allocation to
    read — §3.2 runs this file before pass two has written one.
    """
    allocation = run_dir / "allocation.md"
    if not allocation.is_file():
        return []
    try:
        placed = render.parse_allocation(allocation)
    except render.RenderError as error:
        return [f"citation allocation.md unreadable — {error}"]

    granted = [f"{place.slug}/{'+'.join(unit)}" for place in placed for unit in place.units]
    try:
        bullets, *_ = render.parse_bullets(run_dir / "bullets.md")
    except render.RenderError as error:
        return [f"citation bullets.md unreadable — {error}"]
    written = [bullet.ref for bullet in bullets]

    if written == granted:
        return []
    findings = [
        f"citation {ref} — allocated, and no Bullet cites it"
        for ref in granted
        if ref not in written
    ]
    findings += [
        f"citation {ref} — cited on the page, and the allocation granted no such unit"
        for ref in written
        if ref not in granted
    ]
    if not findings:
        findings.append(
            "citation page order differs from the allocation's — "
            f"written {', '.join(written)}; granted {', '.join(granted)}"
        )
    return findings


def facts(text: str) -> set[str]:
    """The checkable tokens in a line — its figures and its names.

    Deliberately crude. This is not the Number-trace check, which is arithmetic against
    the bank and lives in `render.py`; it is the set the PAW comparison diffs to say
    whether a translation kept what the line asserts.
    """
    found = {match.group(0).strip() for match in FIGURE.finditer(text)}
    found |= {
        match.group(0)
        for match in TOKEN.finditer(text)
        #: THE OPENER IS NOT A FACT. Every Bullet begins with a capitalised verb, so
        #: counting the first token would report `Owned`, `Picked` and `Wrote` as facts
        #: the translation dropped every time it reordered a sentence — noise on every
        #: line, and it would bury the drops that are real.
        if match.start() > 0 and match.group(0) not in STOPWORDS
    }
    return {token for token in found if token}


def load_paw(lib: str | None):
    """`to_english`, or `None` with the reason printed. The dependency is optional."""
    if lib:
        sys.path.insert(0, lib)
    try:
        import programasweights as paw
    except ImportError:
        where = f" on {lib}" if lib else ""
        print(
            f"paw programasweights not importable{where} — "
            "pip install programasweights --extra-index-url "
            "https://pypi.programasweights.com/simple/ , or set PAW_LIB"
        )
        return None
    return paw.function(PAW_TO_ENGLISH)


def paw_findings(lines: list[Line], translate) -> list[str]:
    """One line per composed line: how much the translator took, and what it dropped.

    The translation itself is not printed. It is a compressing paraphrase of a sentence
    that has no room to be compressed, so showing it beside the original invites exactly
    the edit `0056` forbids — and on a dense line it is frequently wrong as well as short.

    No verdict is attached to the percentage. It confounds register with density (see the
    module docstring), so the reader gets the two numbers and the drop list and draws their
    own conclusion, which is the same standing every other finding in this file has.
    """
    findings: list[str] = [
        "paw the translation is never the fix — a drop on a dense line is the translator "
        "summarising, not a verdict on the prose"
    ]
    for line in lines:
        try:
            english = str(translate(line.text)).strip()
        except Exception as error:  # noqa: BLE001 — an optional backstop never halts a run
            findings.append(f"paw {line.number} {line.ref} — translation failed: {error}")
            continue
        before, after = facts(line.text), facts(english)
        kept = before & after
        shorter = 1 - (len(english) / len(line.text)) if line.text else 0.0
        findings.append(
            f"paw {line.number} {line.ref} {-shorter:+.0%} kept {len(kept)}/{len(before)}"
        )
        dropped = sorted(before - after)
        if dropped:
            findings.append(f"paw {line.number} dropped {', '.join(dropped)}")
    return findings


def report(lines: list[Line]) -> list[str]:
    """The marker report — one line per marker, in page order."""
    return [
        f"{line.number} {family} {matched!r} — {line.text}"
        for line in lines
        for family, matched in markers(line.text)
    ]


def main(argv: list[str]) -> int:
    args = [arg for arg in argv[1:] if not arg.startswith("-")]
    flags = [arg for arg in argv[1:] if arg.startswith("-")]
    lib = os.environ.get("PAW_LIB")
    for flag in flags:
        if flag.startswith("--paw-lib="):
            lib = flag.split("=", 1)[1]
        elif flag != "--paw":
            print(f"plainish.py: unknown flag {flag}", file=sys.stderr)
            return 2
    if len(args) != 1:
        print(
            "usage: python tools/plainish.py runs/<jd-slug> [--paw] [--paw-lib=DIR]",
            file=sys.stderr,
        )
        return 2

    run_dir = Path(args[0])
    if not (run_dir / "bullets.md").is_file():
        print(f"plainish.py: no bullets.md in {run_dir}", file=sys.stderr)
        return 2
    try:
        lines = composed_lines(run_dir)
    except render.RenderError as error:
        print(f"plainish.py: {run_dir / 'bullets.md'}: {error}", file=sys.stderr)
        return 2

    for finding in citation_findings(run_dir):
        print(finding)
    for finding in report(lines):
        print(finding)
    if "--paw" in flags:
        translate = load_paw(lib)
        if translate is not None:
            for finding in paw_findings(lines, translate):
                print(finding)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
