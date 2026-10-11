#!/usr/bin/env python3
"""The ATS X-ray — what the page is about to be able to say, scored before it is written.

    python tools/xray.py runs/<jd-slug>

Reads `terms.md`, `scores.md` and `allocation.md` from the run folder plus the Claims
the allocation placed, writes `xray.md`, and prints. It runs at `tailor` §3.4 — after
the Packer's second pass, **before a Bullet is composed** — and it exits 0 whatever it
finds (docs/adr/0052-the-x-ray-runs-before-the-page-is-written.md).

WHY BEFORE AND NOT AFTER. `0041` reads the composed page back against the posting and
changes nothing, on the ground that a report which can reach a sentence turns into the
page marking its own homework. That stands for `coverage.py` and is untouched. This is
the other question, and it is one only answerable early: **of the evidence that just
won the page, how much of the posting can it be made to carry?** After `render.py` the
answer arrives too late to act on, and acting on it would mean rewriting a rendered
page to chase a number — the exact failure `0041` refused.

WHAT IT SCORES IS THE EVIDENCE, NOT THE PROSE, and that is the whole of why it is safe
to consult while composing. It reads each placed unit's cited Claims — Assertion,
Evidence, `skills:` — and asks which of the posting's terms that material *could*
support. It never reads `bullets.md`, which does not exist yet. So a term it calls
answered is a term the bank can back, and surfacing it is `0050` §1's renaming, not an
invention. **A term it calls missing is never a licence to write it anyway.**

IT IS A COUNT WITH A JUDGEMENT-FREE MATCHER. Case-insensitive substring, minimum term
length borrowed from `coverage.py`, for that module's reason: anything cleverer starts
making claims about synonymy, and synonymy is a judgement. Every line is a lead to
check, never a finding to copy.

THE SCORE IS OURS AND SAYS SO. No ATS vendor publishes a scoring algorithm — Workday
and Greenhouse both document parse tolerance only, and nothing about keyword weighting
(`docs/research/bullet-frameworks.md`). Five per-platform numbers would be one
computation wearing five hats. So there is one number, the arithmetic is printed under
it, and `0052` §2 holds the weights rather than this docstring, because they are a
judgement about what matters and not a measurement.

NONE OF THIS REACHES `gaps.md`. §7's *no score, no grade, no coverage ratio* is
untouched: a ratio there measures the maker against the job market, and this measures
one run's own extraction against one posting.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank as bankreader  # noqa: E402
import coverage  # noqa: E402  (Prose, matches, MIN_TERM_CHARS — one matcher, not two)
import render  # noqa: E402  (parse_allocation and listed_items, so nothing drifts)

#: What the three parts of the score are worth. IN THE ADR, NOT HERE — `0052` §2 owns
#: these and this is the transcription. They are a judgement about what matters on a
#: résumé, so they are argued somewhere a person reads rather than tuned in a module.
MUST_HAVE_POINTS = 70
NICE_TO_HAVE_POINTS = 20
STRUCTURE_POINTS = 10

#: What one red flag costs against `STRUCTURE_POINTS`. Two flags spend the structural
#: budget and a third cannot take the score below what the terms earned: a page with
#: bad seams and every must-have answered is still a better page than the reverse.
FLAG_COST = 5

#: Months between two jobs before the gap is worth a recruiter's ten seconds. Placed,
#: not measured — short enough to catch a real break, long enough that ordinary
#: notice periods and a rounded `YYYY-MM` never fire it.
GAP_MONTHS = 6

#: How many missing must-haves the headline names. The rest are in `xray.md`; this is
#: the number a person can hold while rewriting, and the external skill's own figure.
INVISIBLE_SHOWN = 5


@dataclass
class Reading:
    """One run's X-ray: the term verdicts, the flags, and the arithmetic behind them."""

    slug: str
    must_have: list[tuple[str, list[str]]] = field(default_factory=list)
    nice_to_have: list[tuple[str, list[str]]] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    short_terms: list[str] = field(default_factory=list)

    @staticmethod
    def _hit_rate(verdicts: list[tuple[str, list[str]]]) -> tuple[int, int]:
        return sum(1 for _, where in verdicts if where), len(verdicts)

    @property
    def must_have_score(self) -> float:
        answered, total = self._hit_rate(self.must_have)
        #: A posting with no Must-haves scores the section full rather than zero. The
        #: alternative caps every such run at 30 and says nothing about the page; the
        #: thinness is the flimsy-JD check's business (`tailor` §1), not the score's.
        return MUST_HAVE_POINTS if not total else MUST_HAVE_POINTS * answered / total

    @property
    def nice_to_have_score(self) -> float:
        answered, total = self._hit_rate(self.nice_to_have)
        return NICE_TO_HAVE_POINTS if not total else NICE_TO_HAVE_POINTS * answered / total

    @property
    def structure_score(self) -> int:
        return max(0, STRUCTURE_POINTS - FLAG_COST * len(self.flags))

    @property
    def score(self) -> int:
        total = self.must_have_score + self.nice_to_have_score + self.structure_score
        return int(total + 0.5)

    @property
    def invisible_without(self) -> list[str]:
        return [term for term, where in self.must_have if not where]


def split_terms(text: str) -> tuple[list[str], list[str]]:
    """`terms.md`'s two halves, kept apart — which `coverage.py` deliberately merges.

    That module collapses them because what a maker DOES about a gap is §7's
    judgement and not a count. Here the split is the count: a Must-have and a
    Nice-to-have are not worth the same, and a score that weighed them equally would
    rate a page answering every nicety and no essential above the reverse.

    The parse of each half is `render.listed_items`, the same one `coverage.py` and
    `render.py`'s bold check use, so three readers cannot disagree about what a term
    is (docs/adr/0046-… §4).
    """
    sections: dict[str, list[str]] = {"must": [], "nice": []}
    current: str | None = None
    for line in text.splitlines():
        heading = line.strip().lower()
        if heading.startswith("#"):
            if "must" in heading:
                current = "must"
            elif "nice" in heading:
                current = "nice"
            else:
                current = None
            continue
        if current:
            sections[current].append(line)
    must = render.listed_items("\n".join(sections["must"]))
    nice = [
        term for term in render.listed_items("\n".join(sections["nice"])) if term not in must
    ]
    return must, nice


def evidence_surface(run_dir: Path, bank_dir: Path) -> list[coverage.Prose]:
    """What every placed unit's Claims could be made to say, one Prose per claim.

    THE ASSERTION, THE EVIDENCE AND THE `skills:` LINE, concatenated — the whole of
    what `0050` lets a Bullet be written from. Not `scores.md`'s reason, which is what
    `coverage.py` reads: a reason is the scorer's sentence about a claim, written in
    the JD's own terms, so counting terms against it would be counting the run's own
    paraphrase and would report a term answered because somebody typed it while
    explaining why the claim did not answer it.

    Only PLACED units. A claim that lost the page cannot put a term on it, and
    crediting one would make the score describe the bank rather than the page — which
    is `gaps.md`'s job and a different question.
    """
    allocation = run_dir / "allocation.md"
    if not allocation.is_file():
        return []
    try:
        placed = render.parse_allocation(allocation)
    except render.RenderError:
        return []
    try:
        entries = bankreader.load_bank(bank_dir)
    except bankreader.BankError:
        return []
    surface: list[coverage.Prose] = []
    for place in placed:
        entry = entries.get(place.slug)
        if entry is None:
            continue
        for claim_id in place.claim_ids:
            claim = next((one for one in entry.claims if one.id == claim_id), None)
            if claim is None:
                continue
            skills = claim.fields.get("skills", "")
            surface.append(
                coverage.Prose(
                    f"{claim.assertion} {claim.evidence} {skills}", f"{place.slug}/{claim_id}"
                )
            )
    return surface


def red_flags(run_dir: Path, bank_dir: Path) -> list[str]:
    """What a recruiter would see in ten seconds, computed rather than judged.

    Only things readable off the bank and the allocation. Nothing here reads prose,
    because the prose does not exist yet — and nothing here is a matter of taste: each
    flag is a fact about dates or structure that the maker can check in one look.
    """
    allocation = run_dir / "allocation.md"
    if not allocation.is_file():
        return []
    try:
        placed = render.parse_allocation(allocation)
    except render.RenderError:
        return []
    try:
        entries = bankreader.load_bank(bank_dir)
    except bankreader.BankError as error:
        return [f"the bank does not parse, so nothing here was checked: {error}"]
    flags: list[str] = []

    #: A gap between consecutive placed JOBS. Projects are not employment and a break
    #: between two of them is not a hole in a history, so they are not read here.
    jobs = []
    for place in placed:
        entry = entries.get(place.slug)
        if entry is None or entry.frontmatter.get("type") != "job":
            continue
        jobs.append((entry.frontmatter.get("started", ""), entry.frontmatter.get("ended", ""), place.slug))
    jobs.sort(key=lambda job: job[0], reverse=True)
    for newer, older in zip(jobs, jobs[1:]):
        gap = months_between(older[1], newer[0])
        if gap is not None and gap >= GAP_MONTHS:
            flags.append(
                f"a {gap}-month gap between {older[2]} ending {older[1]} and "
                f"{newer[2]} starting {newer[0]}"
            )

    #: A missing lead line is no longer a flag. A job's header already names the
    #: employer and the title, and a project's names its stack — a bare heading is the
    #: normal résumé shape, not a hole (docs/adr/0057-the-page-reads-like-a-resume.md §5).
    return flags


def months_between(ended: str, started: str) -> int | None:
    """Whole months from one `YYYY-MM` to another, or `None` if either is unreadable.

    `present` is not a date and never opens a gap: an entry still running has no end
    to measure from.
    """
    if ended == "present" or not ended or not started:
        return None
    try:
        end_year, end_month = (int(part) for part in ended.split("-"))
        start_year, start_month = (int(part) for part in started.split("-"))
    except ValueError:
        return None
    return (start_year - end_year) * 12 + (start_month - end_month)


def read(run_dir: Path, bank_dir: Path) -> Reading:
    reading = Reading(slug=run_dir.name)
    terms_path = run_dir / "terms.md"
    must, nice = (
        split_terms(terms_path.read_text(encoding="utf-8")) if terms_path.is_file() else ([], [])
    )
    surface = evidence_surface(run_dir, bank_dir)
    for term in must + nice:
        if len(term) < coverage.MIN_TERM_CHARS:
            reading.short_terms.append(term)
            continue
        verdict = (term, coverage.matches(term, surface))
        (reading.must_have if term in must else reading.nice_to_have).append(verdict)
    reading.flags = red_flags(run_dir, bank_dir)
    return reading


def report(reading: Reading) -> str:
    answered_must, total_must = Reading._hit_rate(reading.must_have)
    answered_nice, total_nice = Reading._hit_rate(reading.nice_to_have)
    out = [
        f"# X-ray: {reading.slug}",
        "",
        "Written by `tools/xray.py` before a Bullet is composed. It scores the",
        "EVIDENCE the allocation placed, not prose — there is no prose yet. A term",
        "called answered is one the bank can back, so surfacing it is a renaming",
        "(`0050` §1). A term called missing is never a licence to write it anyway.",
        "",
        "## Coverage",
        "",
        "```",
        f"Coverage: {reading.score}/100",
        f"  must-have terms answered   {answered_must}/{total_must}"
        f"  ({reading.must_have_score:.0f} of {MUST_HAVE_POINTS})",
        f"  nice-to-have answered      {answered_nice}/{total_nice}"
        f"  ({reading.nice_to_have_score:.0f} of {NICE_TO_HAVE_POINTS})",
        f"  red flags                  {len(reading.flags)}"
        f"      ({reading.structure_score - STRUCTURE_POINTS} of {STRUCTURE_POINTS})",
        "```",
        "",
        "The weights are this system's own and are argued in",
        "`docs/adr/0052-the-x-ray-runs-before-the-page-is-written.md` §2. No ATS vendor",
        "publishes a scoring algorithm, so no number here is any platform's.",
        "",
        "## Invisible without",
        "",
    ]
    missing = reading.invisible_without
    if missing:
        out += [f"- **{term}** — no placed claim's evidence carries it" for term in missing[:INVISIBLE_SHOWN]]
        if len(missing) > INVISIBLE_SHOWN:
            out.append(f"- …and {len(missing) - INVISIBLE_SHOWN} more, listed below")
    else:
        out.append("Every must-have term is carried by evidence that placed.")
    out += ["", "## Red flags", ""]
    out += [f"- {flag}" for flag in reading.flags] or [
        "Nothing a recruiter would catch in ten seconds."
    ]
    out += ["", "## Every term", ""]
    for label, verdicts in (("Must-have", reading.must_have), ("Nice-to-have", reading.nice_to_have)):
        if not verdicts:
            continue
        out += [f"### {label}", ""]
        for term, where in verdicts:
            out.append(f"- `{term}` — {', '.join(where) if where else '**nothing placed carries it**'}")
        out.append("")
    if reading.short_terms:
        out += [
            "### Too short to count",
            "",
            "Under `MIN_TERM_CHARS`, so a substring count means nothing. Read these off",
            "the page yourself.",
            "",
        ]
        out += [f"- `{term}`" for term in reading.short_terms]
        out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/xray.py runs/<jd-slug>", file=sys.stderr)
        return 2
    run_dir = Path(argv[1])
    if not run_dir.is_dir():
        print(f"xray.py: no run folder at {run_dir}", file=sys.stderr)
        return 1
    bank_dir = run_dir.parent.parent / "bank"
    reading = read(run_dir, bank_dir)
    text = report(reading)
    (run_dir / "xray.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
