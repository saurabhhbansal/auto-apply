#!/usr/bin/env python3
"""The length pass — every over-budget line in `bullets.md`, found in one go.

    python tools/lengths.py runs/<jd-slug>

A measuring tape, not a lint. `render.py` fails the run on the *first* over-budget
Bullet; this names all of them at once, plus every Skills row, which is measured by
the typeset lines it will take rather than by a character count.

    <line> <length> <the prose>       one over-budget Bullet, by line number
    summary <length> <the prose>      the Summary, over SUMMARY_CHARS
    wide slot <line> <length> <ref>   a Bullet granted two lines that fits in one
    spread <short>/<needed> …         the page is written to the cap
    skills row <n> <label> <lines>    one Skills row that runs past the two-line cap
    skills rows <1,2,1,1>             what `pack.py --skills-rows` takes
    supporting row <line> <slug> <lines>   a supporting row that runs past one line

A Bullet is measured against **the width its slot was granted**, read out of
`allocation.md` beside it — `width x CHARS_PER_BULLET`. Where there is no allocation
to read yet, every Bullet is measured at one line, which is what the Packer would
have charged.

The `wide slot` line is **advisory, not a defect**. A short sentence is not a
failure — the composition rubric's standard is completeness, not length
(`docs/adr/0027-composition-rubric.md` §1). What it points at is a *granted width
nobody used*, which is an error in the `width` column of `scores.md` rather than in
the prose: the room came off the page and bought nothing.

The `spread` line is the one finding here that IS a defect — `render.py` fails the
same rule. It is repeated here because it is the only one of the three **set checks**
you need while the file is still being written: a repeated opener and a mixed spelling
are each one rephrase, named before a compile is spent, but a spread is the whole page
and the maker wants the distribution in front of them rather than a refusal afterwards
(`docs/adr/0030-the-composed-set.md` §5). The rule and its wording come from
`render.py`, so the two can never say it differently.

The `skills rows` line is printed **whenever there are rows**, over budget or not,
because it is not a finding — it is the argument the Packer's second pass needs, and
the run cannot proceed without it. Everything else obeys the old rule: nothing over
budget means no output. The exit code is 0 either way; a finding here is work to do
before spending a compile, and whether the run may proceed stays render.py's call.

The line grammar is matched loosely on purpose. A strict parse would mean rejecting
the file the way `render.py` does, and this exists precisely to measure a file
render.py would refuse on its first bad line. What it does NOT re-derive is the
row-lines arithmetic: that comes from `render.py`, because a second copy that drifted
would hand the Packer a budget for a section the page does not hold. Importing the
Renderer costs nothing — its Jinja2 import is lazy, inside the one function that
needs it.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402  (tools/ is not a package; the page-budget block)
import pack  # noqa: E402  (MAX_ROW_LINES — the cap a row is measured against)
import render  # noqa: E402  (row_lines, so the two never disagree)

#: `- <entry-slug>/c<n>: <prose>` — or `<entry-slug>/c<n>+c<n>` for a merge — `-
#: <skill> (<entry-slug>/c<n>)`, and a Skills category row's `### <label>` heading,
#: all matched loosely.
BULLET_LINE = re.compile(r"- (?P<ref>\S+/c\d+(?:\+c\d+)*): (?P<text>.+)")
SKILL_LINE = re.compile(r"- (.+) \(\S+/c\d+\)$")
SKILL_ROW_HEADING = re.compile(r"### (.+)")

#: A `## <name>` section heading. It cannot collide with SKILL_ROW_HEADING above:
#: this demands whitespace after the second `#`, and `### Languages` has a third `#`
#: there instead — the same split render.py's own two patterns rely on.
SECTION_HEADING = re.compile(r"##\s+(.+)")

#: The Summary's section, matched the case-insensitive way render.py matches it.
SUMMARY_HEADING = "summary"

#: The supporting sections' one section, matched the same way. Tracked here rather
#: than ignored because BULLET_LINE above would otherwise MATCH a supporting row that
#: carries a tail — `- aws-saa/c1: Renewed after…` is a bullet-shaped line — and the
#: row would be measured against a Bullet's budget instead of its own one-line cap
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §6).
SUPPORTING_HEADING = "supporting"


def granted_widths(run_dir: Path) -> dict[str, int]:
    """Claim ref -> typeset lines granted, out of `allocation.md` if there is one.

    Missing or unreadable is not an error here: this runs at §3.2 as well, where the
    Bullet sections do not exist yet, and it is a measuring tape rather than a lint.
    The parse comes from `render.py` for the same reason `row_lines` does — a second
    copy that drifted would measure against a width the page was not charged.
    """
    allocation = run_dir / "allocation.md"
    if not allocation.is_file():
        return {}
    try:
        placed = render.parse_allocation(allocation)
    except render.RenderError:
        return {}
    return {
        f"{place.slug}/{'+'.join(unit)}": width
        for place in placed
        for unit, width in zip(place.units, place.widths)
    }


def supporting_finding(line: str, number: int, entries: dict | None) -> list[str]:
    """One supporting row, measured against the one typeset line it is charged.

    Returns nothing without the bank, and that is the honest answer rather than a
    guess: a row is a BUILT label plus a tail, and the label — the entry's `title`,
    `org` and dates — is most of it. Measuring the tail alone would report a row
    inside budget that `render.py` then refuses, which is the one thing a measuring
    tape must not do (§3).
    """
    match = render.SUPPORTING_LINE.match(line.strip())
    if not match or entries is None:
        return []
    entry = entries.get(match.group("entry"))
    if entry is None:
        return []
    row = render.SupportingRow(
        match.group("entry"), match.group("claim"), match.group("text"), number
    )
    taken = render.row_lines(entry.title, render.supporting_row_text(row, entry))
    if taken > 1:
        return [f"supporting row {number} {row.slug} {taken}"]
    return []


def report(
    text: str,
    widths: dict[str, int] | None = None,
    entries: dict | None = None,
    vocabulary: tuple[str, ...] = (),
) -> list[str]:
    """The lines to print for one `bullets.md`, in the order they were measured.

    `entries` is the bank, needed only for the supporting rows' built labels, and
    `vocabulary` is render.py's keyword vocabulary. Both are optional: this is a
    measuring tape and it has to work on a run folder alone. A Bullet is charged the
    way `render.py` will charge it — every emphasis span at the bold rate
    (`docs/adr/0046-every-impact-figure-and-the-declared-keyword.md` §6). Since 0057
    §4 only figures are bold, and they need no vocabulary. The arithmetic itself is
    imported, never re-derived.
    """
    widths = widths or {}
    findings: list[str] = []
    rows: list[tuple[str, list[str]]] = []
    bullets: list[render.Bullet] = []
    summary_lines: list[str] = []
    in_summary = False
    in_supporting = False

    for number, line in enumerate(text.splitlines(), 1):
        section = SECTION_HEADING.match(line)
        if section:
            name = section[1].strip().lower()
            in_summary = name == SUMMARY_HEADING
            in_supporting = name == SUPPORTING_HEADING
            continue
        if in_supporting:
            findings += supporting_finding(line, number, entries)
            continue
        if in_summary:
            if line.strip():
                summary_lines.append(line.strip())
            continue
        bullet = BULLET_LINE.match(line)
        if bullet:
            ref, prose = bullet["ref"], bullet["text"]
            slug, claims = ref.split("/", 1)
            bullets.append(render.Bullet(slug, tuple(claims.split("+")), prose, number))
            width = widths.get(ref, 1)
            if render.bullet_line_cost(prose, render.emphasis_spans(prose, vocabulary)) > width:
                findings.append(f"{number} {len(prose)} {prose}")
            elif width > 1 and len(prose) <= config.CHARS_PER_BULLET:
                findings.append(f"wide slot {number} {len(prose)} {ref}")
            continue
        heading = SKILL_ROW_HEADING.match(line)
        if heading:
            rows.append((heading[1].strip(), []))
            continue
        skill = SKILL_LINE.match(line)
        if skill and rows:
            rows[-1][1].append(skill[1])

    # The Summary against its own budget — the widest prose on the page, so neither
    # of the other two counts applies to it. Reported here rather than only at the
    # compile for the reason everything else here is: it is a number to write to
    # (docs/adr/0044-the-page-opens-on-a-summary.md §6). The tape stops at the
    # character count; whether the paragraph actually broke in two lines is
    # render.py's post-compile call and nothing this side of pdflatex can answer it.
    summary = " ".join(summary_lines)
    summary_chars = render.bold_equivalent_chars(
        summary,
        render.emphasis_spans(summary, vocabulary, render.MAX_SUMMARY_KEYWORDS),
    )
    if math.ceil(summary_chars) > config.SUMMARY_CHARS:
        findings.append(f"summary {math.ceil(summary_chars)} {summary}")

    spread = render.measure_spread(bullets, widths)
    if spread.fires:
        findings.append(spread.finding)

    lines = [render.row_lines(label, ", ".join(skills)) for label, skills in rows]
    for index, ((label, _skills), taken) in enumerate(zip(rows, lines), 1):
        if taken > pack.MAX_ROW_LINES:
            findings.append(f"skills row {index} {label} {taken}")
    if rows:
        findings.append("skills rows " + ",".join(str(taken) for taken in lines))
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/lengths.py runs/<jd-slug>", file=sys.stderr)
        return 2
    run_dir = Path(argv[1])
    bullets_path = run_dir / "bullets.md"
    if not bullets_path.is_file():
        print(f"lengths.py: no composed bullets at {bullets_path}", file=sys.stderr)
        return 1
    text = bullets_path.read_text(encoding="utf-8")
    # The bank is found RELATIVE TO THE RUN FOLDER — `<run>/../../bank` — which is
    # how render.py finds it and is the layout a run folder actually sits in.
    # Resolving it beside this script instead would measure one bank while the run
    # renders against another. Missing or unreadable is not an error here: the tape
    # still measures, one notch generous on figures (see `report`), and a supporting
    # row simply goes unmeasured.
    entries = None
    bank_dir = run_dir.resolve().parent.parent / "bank"
    try:
        entries = render.bank.load_bank(bank_dir)
    except Exception:
        pass
    # The same three sources render.py unions, read the same way. A bank that would
    # not load costs the keywords and nothing else — the figures need no vocabulary.
    vocabulary = render.keyword_vocabulary(
        entries or {},
        render.read_if_present(bank_dir / "vocabulary.md"),
        render.read_if_present(run_dir / "terms.md"),
    )
    for line in report(text, granted_widths(run_dir), entries, vocabulary):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
