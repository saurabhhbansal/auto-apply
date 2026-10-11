#!/usr/bin/env python3
"""The coverage read — the composed page, counted back against the posting's terms.

    python tools/coverage.py runs/<jd-slug>

Reads `terms.md`, `bullets.md`, `scores.md` and `allocation.md` from the run folder,
prints three lists, and changes nothing. It runs at `tailor` §6.5 — after the page is
final — and it is **advisory, not a gate**: it prints, it never raises, and it exits 0
whatever it finds. `render.py` neither calls it nor reads its output, which is the
mechanical form of the promise below.

WHAT IT IS NOT. `0027` §3 forbids the posting **supplying a word** to a sentence and
§4 forbids the posting **filtering a sentence's interior**. Neither forbids counting,
after the fact, which of the posting's terms the page happens to answer, and telling
the maker — who is not a lint and does not have to obey it. Nothing here can reach a
sentence: by the time this runs, `bullets.md` is written, the cold read has been done
and the merge verifier has halted or not (docs/adr/0041-the-page-is-read-back-against-the-posting.md §2).

IT IS A COUNT, NEVER A JUDGEMENT, which is what keeps it on the right side of `0010`'s
refusal of a second reading of the prose. Matching is **case-insensitive substring**,
the naive version on purpose: anything cleverer starts making claims about synonymy,
and synonymy is a judgement. It cannot say *looks fine* — it fires a list or an empty
one (docs/adr/0030-the-composed-set.md §2's species).

THE MIDDLE LIST DOES NOT READ THE BANK. *Answered by the bank, absent from the page*
is sourced from `scores.md`'s **reason** column — the one line per Claim that the Fit
scoring already wrote in the JD's own terms — and never from `bank/`. That keeps this
inside the run folder, where a replay finds every input it had (**Material
determinism**), and it is why the list is honest about being a *lead* rather than a
proof: a claim whose reason names the requirement under a different word is missed.

The three lists partition `terms.md`, in that order: a term covered on the page is
never also counted as absent from it, and a term no reason names is *Answered
nowhere*.

The parse of `bullets.md` and of `allocation.md` comes from `render.py`, and the parse
of `scores.md` from `pack.py`, for the reason `lengths.py` borrows `row_lines`: a
second copy that drifted would report on a page the run does not have. The prose
surface read here is `render.page_prose`'s three sources — Bullets, leads and Skills
rows — carrying the citation each line came from, which `page_prose` itself drops
because the checks that use it want line numbers instead.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank as bankreader  # noqa: E402  (a supporting row's label is the bank's)
import pack  # noqa: E402  (tools/ is not a package; parse_scores, for the reasons)
import render  # noqa: E402  (parse_bullets and parse_allocation, so nothing drifts)


#: Below this many characters, a substring count is not a measurement of anything.
#: `R` — a real Qualification on a real posting, *"Python, R etc."* — is
#: inside `Replaced`, `Rewrote`, `Streamlit` and every other line on that page, so it
#: came back covered 30 times over. `Go` is inside `Google`. The guard is arithmetic
#: rather than a judgement about what the term means, and it does not drop the term:
#: a term too short to count is printed under its own heading and counted nowhere, so
#: the four lists still add up to `terms.md` and the maker can see the one this tool
#: refuses to answer (docs/adr/0041-the-page-is-read-back-against-the-posting.md §5).
MIN_TERM_CHARS = 3


@dataclass(frozen=True)
class Prose:
    """One piece of text on the page, and where a reader would find it.

    `where` is written the way `gaps.md` names things — a claim ref plus what kind
    of line it is — because the whole output of this tool is material for §7, and a
    finding a person has to re-address by hand is a finding they will not use.
    """

    text: str
    where: str


def terms(text: str) -> list[str]:
    """Every term in `terms.md`, in file order, duplicates collapsed to the first.

    A term is a `- ` item, wherever it sits. The `## Must-have` / `## Nice-to-have`
    headings are read by the person and not by this: they say what the maker does
    about a gap, which is §7's judgement and not a count. Matched loosely for the
    same reason `lengths.py` matches loosely — this is a measuring tape over a file
    a person wrote, not a lint that may refuse it.

    The parse itself is `render.listed_items`, not a copy of it, for the reason every
    other borrowing in this file exists: `render.py` reads the same file for its
    keyword pass, and two readings that disagreed about what a term
    is would have this tool reporting on a page it does not have
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §4).
    """
    return render.listed_items(text)


def page_surface(
    bullets, rows, leads, summary=None, supporting=None, labels=None
) -> list[Prose]:
    """Every line of prose on the page, each carrying the citation behind it.

    Exactly `render.page_prose`'s sources. The Skills rows are in it because
    they are prose the reader reads, and a Nice-to-have surviving on a Skills row
    rather than in a sentence is precisely the thing the middle list must not
    mistake for a gap. A row's **label** is in it too and carries no citation: it is
    the run's own wording, named from the posting under `0020`, so a term that only
    matches there is reported as matching a label rather than a claim.

    The Summary is in it for a sharper version of the same reason, and it is the one
    line here that is **licensed** to carry the posting's own words
    (docs/adr/0044-the-page-opens-on-a-summary.md §2). Leaving it out would report a
    term as missing from a page that says it in its first sentence. Like a row label
    it carries no citation — it cites nothing by design — so a term matching only
    here is reported as matching the Summary, which is exactly the reading the maker
    wants: the page has the word, and no Claim was found to put it on a line.
    """
    surface = [Prose(bullet.text, f"{bullet.ref} (bullet)") for bullet in bullets]
    if summary:
        surface.append(Prose(summary, "the Summary (no citation)"))
    for slug, text in (leads or {}).items():
        surface.append(Prose(text, f"{slug} (lead)"))
    for row in rows:
        surface.append(Prose(row.label, f"the {row.label} row (skills label)"))
        surface.extend(
            Prose(skill.name, f"{skill.ref} (skills row)") for skill in row.skills
        )
    # A supporting row lands as two pieces of prose, because its two halves have
    # different citations. The BUILT label — the entry's `title` and `org` — is
    # exactly where a posting's own term most often appears verbatim (`AWS Certified
    # Solutions Architect` is a term and a title at once), so leaving it out would
    # report a term missing from a page that prints it; but no Claim supplied a word
    # of it, so it is credited to the ENTRY rather than to a claim ref. The composed
    # tail cites a Claim and is credited to it, like a Bullet
    # (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §3).
    #
    # `labels` is empty when the bank could not be read, and the label is then simply
    # absent from the surface: this tool never fails a run, and a missing lead is a
    # better outcome than a stack trace over an advisory.
    for row in supporting or []:
        label = (labels or {}).get(row.slug)
        if label:
            surface.append(Prose(label, f"{row.slug} (supporting label)"))
        if row.tail:
            surface.append(Prose(row.tail, f"{row.ref} (supporting row)"))
    return surface


def bank_surface(scores_text: str) -> list[Prose]:
    """One piece of prose per scored Claim: the reason the Fit scoring wrote.

    Not the Claim's Evidence, and not the bank at all. What the reason is *for* is
    what makes it the right surface here — `tailor` §2 requires it written **in the
    JD's own terms**, naming the requirement the claim hits or misses, which is the
    only place in the run folder where a term of the posting is already attached to
    a claim id (docs/adr/0041-the-page-is-read-back-against-the-posting.md §3).
    """
    return [Prose(claim.reason, claim.ref) for claim in pack.parse_scores(scores_text)]


def matches(term: str, surface: list[Prose]) -> list[str]:
    """Where `term` appears, case-insensitively, in file order and de-duplicated."""
    needle = term.casefold()
    where: list[str] = []
    for prose in surface:
        if needle in prose.text.casefold() and prose.where not in where:
            where.append(prose.where)
    return where


def placed_refs(run_dir: Path) -> set[str] | None:
    """Every Claim ref that took a Bullet slot, or `None` if that is unreadable.

    `None` rather than an empty set, so the report can leave the annotation off
    instead of saying *lost the page* about a page it could not read. Missing or
    malformed is not an error here for `lengths.py`'s reason: this is advisory, and
    an old run folder must still get an answer.
    """
    allocation = run_dir / "allocation.md"
    if not allocation.is_file():
        return None
    try:
        placed = render.parse_allocation(allocation)
    except render.RenderError:
        return None
    return {
        f"{place.slug}/{claim_id}" for place in placed for claim_id in place.claim_ids
    }


def annotate(refs: list[str], placed: set[str] | None) -> str:
    """`placed: a/c5, a/c6` · `lost the page: x/c3` — which half of §7 this is.

    The distinction is the actionable part and it is arithmetic, not judgement: a
    claim that **placed** and whose term did not reach its sentence is a composition
    call the maker may want back; a claim that **lost the page** is `0009`'s *you
    have it, the page did not* with nothing to fix in the bank.
    """
    if placed is None:
        return ", ".join(refs)
    took = [ref for ref in refs if ref in placed]
    lost = [ref for ref in refs if ref not in placed]
    parts = []
    if took:
        parts.append("placed: " + ", ".join(took))
    if lost:
        parts.append("lost the page: " + ", ".join(lost))
    return "; ".join(parts)


def report(
    slug: str,
    term_list: list[str],
    page: list[Prose],
    bank: list[Prose],
    placed: set[str] | None,
) -> list[str]:
    """The three lists, in the order a reader wants them, as lines to print.

    Every heading carries its count, including the zeros — `0025` §7's rule again:
    a signal is only readable if its absence never has to be interpreted. The count
    is the size of one part of a partition of `terms.md`, which is why it is not the
    coverage ratio `0010` and §7 refuse: it grades no one, it compares to nothing,
    and the denominator is this run's own extraction rather than the job market. It
    stays out of `gaps.md` all the same
    (docs/adr/0041-the-page-is-read-back-against-the-posting.md §4).
    """
    covered: list[tuple[str, str]] = []
    in_bank: list[tuple[str, str]] = []
    nowhere: list[str] = []
    short: list[str] = []
    for term in term_list:
        if len(term) < MIN_TERM_CHARS:
            short.append(term)
            continue
        on_page = matches(term, page)
        if on_page:
            covered.append((term, ", ".join(on_page)))
            continue
        in_scores = matches(term, bank)
        if in_scores:
            in_bank.append((term, annotate(in_scores, placed)))
        else:
            nowhere.append(term)

    total = len(term_list)
    width = max((len(term) for term, _ in covered + in_bank), default=0)
    out = [
        f"Coverage: {slug} — {total} term(s) from terms.md, read back against the "
        f"composed page.",
        "Reported, never applied: nothing here may supply a word to a sentence.",
        "",
        f"Covered on the page ({len(covered)}/{total})",
    ]
    out += [f"  {term.ljust(width)}  {where}" for term, where in covered] or [
        "  nothing"
    ]
    out += ["", f"Answered by the bank, absent from the page ({len(in_bank)}/{total})"]
    out += [f"  {term.ljust(width)}  {where}" for term, where in in_bank] or [
        "  nothing"
    ]
    out += ["", f"Answered nowhere ({len(nowhere)}/{total})"]
    out += ["  " + " · ".join(nowhere)] if nowhere else ["  nothing"]
    out += ["", f"Too short to count ({len(short)}/{total})"]
    out += (
        [
            "  " + " · ".join(short),
            f"  under {MIN_TERM_CHARS} characters a substring is inside half the page — "
            f"read these off the page yourself",
        ]
        if short
        else ["  nothing"]
    )
    return out


def main(argv: list[str]) -> int:
    """Always 0. A coverage read that could fail a run would be a gate.

    Every way this can go wrong prints one line saying what it could not read and
    stops there. The one that is not a fault at all is a run folder with no
    `terms.md` — one scored before §6.5 existed, or one where the maker chose not to
    extract — and it says so and leaves.
    """
    if len(argv) != 2:
        print("usage: python tools/coverage.py runs/<jd-slug>")
        return 0
    run_dir = Path(argv[1])
    terms_path = run_dir / "terms.md"
    if not terms_path.is_file():
        print(
            f"coverage.py: no {terms_path} — nothing to read the page back against. "
            f"The posting's terms are lifted verbatim into it at §2, before scoring."
        )
        return 0
    bullets_path = run_dir / "bullets.md"
    if not bullets_path.is_file():
        print(f"coverage.py: no composed page at {bullets_path}")
        return 0

    term_list = terms(terms_path.read_text(encoding="utf-8"))
    if not term_list:
        print(f"coverage.py: {terms_path} lists no terms — a term is a `- ` item")
        return 0
    try:
        bullets, rows, leads, summary, supporting = render.parse_bullets(bullets_path)
    except render.RenderError as error:
        print(f"coverage.py: {error}")
        return 0

    # The bank, for the supporting rows' built labels and for nothing else — so a
    # bank that will not parse costs this read one label, never the report.
    labels: dict[str, str] = {}
    if supporting:
        try:
            held = bankreader.load_bank(run_dir.parent.parent / "bank")
            labels = {
                row.slug: f"{held[row.slug].title}, {held[row.slug].org}"
                for row in supporting
                if row.slug in held
            }
        except bankreader.BankError as error:
            print(f"coverage.py: {error}")

    scores_path = run_dir / "scores.md"
    bank: list[Prose] = []
    if scores_path.is_file():
        try:
            bank = bank_surface(scores_path.read_text(encoding="utf-8"))
        except pack.ScoreTableError as error:
            print(f"coverage.py: {scores_path}: {error}")
            return 0

    for line in report(
        run_dir.name,
        term_list,
        page_surface(bullets, rows, leads, summary, supporting, labels),
        bank,
        placed_refs(run_dir),
    ):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
