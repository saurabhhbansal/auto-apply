#!/usr/bin/env python3
"""The Renderer — composed Bullets in, a one-page PDF out.

    python tools/render.py runs/<jd-slug>

Reads `bullets.md` and `allocation.md` from the run folder, plus the bank and
`bank/profile.md`; writes `resume.tex` and `resume.pdf` beside them.

The lints live here because this is the only path that produces a résumé: calling
`pdflatex` by hand yields an unlinted `.tex` and no PDF worth sending.

Order of operations. Every failure is hard, names the offender, and exits non-zero:

     1. Profile validation   bank/profile.md by field name — the one seam
     2. Structural check     every cited claim resolves; the Bullets and the Skills
                             rows are exactly what the allocation charged for; the
                             allocation's copy of each Entry's `ended` is the bank's
     3. Length lint          pre-compile, plain text: a Bullet against the width its
                             slot was granted (`width x CHARS_PER_BULLET`), a Skills
                             row against the two-line cap
     4. Set checks           pre-compile, the whole file at once: the spread rule,
                             no opening word twice, one spelling convention
     5. Number-trace check   pre-compile; equal-or-softer provenance, skills too
     6. Escape and fill      the Template filled WHOLE into resume.tex
     7. Compile              pdflatex, SOURCE_DATE_EPOCH pinned
     8. Header-fit check     post-compile, from the log — did a header line wrap?
     9. Overflow check       post-compile, from the log — did anything run past the
                             right margin? The loud twin of 8
    10. Page-count assert    post-compile, on the PDF

3 to 5 run before a compile is spent, on the plain text as written: extracting text
back out of a PDF is fragile under ligatures and hyphenation.

3 reads one Bullet at a time and 4 reads the page. That is the whole difference between
them, and it is why 4 exists: a spread, a repeated opener and a mixture of spellings are
faults of the composed set, invisible in any single line however carefully it is read
(docs/adr/0030-the-composed-set.md).

The Template ships with the tools and is found relative to this script. The bank is
data and sits beside `runs/`, so it is found relative to the run folder,
`<run>/../../bank` — the real layout, which is why the tests can drive this as a
command with no `--bank` flag and no test-only code path.

This is the only component permitted a third-party dependency (Jinja2, pinned), so the
Template stays one hand-editable file. `pack.py` stays stdlib-only, and `bank.py` is
imported here and nowhere else.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank  # noqa: E402  (tools/ is not a package; the Entry file reader)
import config  # noqa: E402  (the page-budget block)
import pack  # noqa: E402  (EDUCATION_ROWS and the Skills-row rules the budget spends)

REPO = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO / "templates"
TEMPLATE_NAME = "resume.tex.j2"
PROFILE_EXAMPLE = TEMPLATE_DIR / "profile.example.md"


class RenderError(Exception):
    """A run that must not produce a PDF. Always names the offender."""


# --------------------------------------------------------------------------
# What Opus wrote: bullets.md
# --------------------------------------------------------------------------

#: A cited claim ref inside a longer line. Built from `bank.py`'s grammar rather
#: than respelled, so the slug and claim-id alphabets have one definition on this
#: side of the bank-blind seam (see `bank.ENTRY_SLUG_PATTERN`).
CITED_REF = rf"(?P<entry>{bank.ENTRY_SLUG_PATTERN})/(?P<claim>{bank.CLAIM_ID_PATTERN})"

#: A Bullet's citation, singular or merged — `helios/c1` or `helios/c1+c3+c4`
#: (docs/adr/0034-a-merged-bullet-coordinates.md Consequences). `claims` is the raw
#: `+`-joined string; callers split it themselves, since a Skill's citation (below)
#: never merges and has no business knowing the grammar exists.
CITED_REF_GROUP = (
    rf"(?P<entry>{bank.ENTRY_SLUG_PATTERN})/"
    rf"(?P<claims>{bank.CLAIM_ID_PATTERN}(?:\+{bank.CLAIM_ID_PATTERN})*)"
)

BULLET_LINE = re.compile(rf"^-\s+{CITED_REF_GROUP}:\s*(?P<text>.+?)\s*$")
SKILL_LINE = re.compile(rf"^-\s+(?P<skill>.+?)\s*\({CITED_REF}\)\s*$")
HEADING = re.compile(r"^##\s+(?P<name>.+?)\s*$")
SKILLS_HEADING = "skills"

#: The Summary's own section heading — the page's opening claim about the candidate
#: (docs/adr/0044-the-page-opens-on-a-summary.md). Matched the same case-insensitive
#: way `## Skills` is, and carrying the same collision with a Bank entry slugged
#: `summary`: the precedent is `0020`'s and this does not widen it.
SUMMARY_HEADING = "summary"

#: An entry section's lead line — the composed sentence over the bank's `## lead`
#: facts, written before the Bullets (docs/adr/0032-the-entry-arc.md). Optional,
#: and legal only as the first line under a `## <entry-slug>` heading.
LEAD_LINE = re.compile(r"^Lead:\s*(?P<text>.+?)\s*$")

#: The supporting sections' one section in `bullets.md` — the LAST, below `## Skills`,
#: because that is where the sections sit on the page
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §7).
#: One section for all three, routed to Certifications, Positions of Responsibility or
#: Extracurriculars by the Entry's own `type` — the routing the Template already does
#: for `job` and `project`.
SUPPORTING_HEADING = "supporting"

#: A supporting row, in its two legal shapes:
#:
#:     - aws-saa/c1: Renewed after rebuilding the billing pipeline on Lambda.
#:     - aws-saa
#:
#: The tail is optional and its citation rides with it — a row is a built label plus
#: at most one composed clause, and a certification the bank holds no claim for
#: renders as the bare label, which is what a certification line usually is (§3). The
#: two halves are optional TOGETHER: a ref with no tail cites a Claim that reaches no
#: word on the page, and a tail with no ref is prose that traces to nothing.
SUPPORTING_LINE = re.compile(
    rf"^-\s+(?P<entry>{bank.ENTRY_SLUG_PATTERN})"
    rf"(?:/(?P<claim>{bank.CLAIM_ID_PATTERN}))?"
    rf"(?::\s*(?P<text>.+?))?\s*$"
)

#: A Skills category row's heading. It cannot collide with `HEADING`, which requires
#: whitespace after the second `#` — `### AI` has a third `#` there instead. That is
#: what let the row heading be added without touching `SKILL_LINE`, which is
#: byte-identical to what it was (docs/adr/0020-skills-section.md §5).
SKILL_ROW_HEADING = re.compile(r"^###\s+(?P<label>.+?)\s*$")


@dataclass(frozen=True)
class Bullet:
    """One rendered line, and the Claim(s) it was composed from.

    `claim_ids` holds one id for an ordinary Bullet and two or three for a merged
    one — the `+`-joined citation `bullets.md` writes
    (docs/adr/0034-a-merged-bullet-coordinates.md). Order is the citation's own,
    which is also the bank's `## merge` heading order once `bank.Entry.merge`
    looks it up by set.
    """

    entry: str
    claim_ids: tuple[str, ...]
    text: str
    line: int

    @property
    def ref(self) -> str:
        return f"{self.entry}/{'+'.join(self.claim_ids)}"

    @property
    def merged(self) -> bool:
        return len(self.claim_ids) > 1


@dataclass(frozen=True)
class Skill:
    """One skill in a Skills category row, and the Claim that backs it."""

    name: str
    entry: str
    claim_id: str
    line: int

    @property
    def ref(self) -> str:
        return f"{self.entry}/{self.claim_id}"


@dataclass
class SkillRow:
    """One category row: a label named from the JD, and the skills under it.

    The label is the run's own wording rather than anything the bank holds, and
    the row's order on the page is the order the rows were written in.
    """

    label: str
    line: int
    skills: list[Skill] = field(default_factory=list)

    @property
    def text(self) -> str:
        """The row's skills as the one comma list the Template typesets."""
        return ", ".join(skill.name for skill in self.skills)


@dataclass(frozen=True)
class SupportingRow:
    """One row of a supporting section: the Entry it is built from, and its tail.

    `claim_id` and `tail` are both `None` on a bare row. Where they are set the tail
    is composed from that one Claim and is bound by everything a Bullet's prose is
    bound by — Downgrade-only, the Claim-level trace, the Number-trace check and the
    spelling check
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §8).

    It is not a Bullet: never scored, never a candidate for a slot, and outside the
    spread and opener checks — the same standing a lead has, and for the same reason.
    """

    slug: str
    claim_id: str | None
    tail: str | None
    line: int

    @property
    def ref(self) -> str:
        """What the failures name. A bare row has no citation, so it names the slug."""
        return f"{self.slug}/{self.claim_id}" if self.claim_id else self.slug

    def as_bullet(self) -> Bullet:
        """The tail, shaped as a `Bullet` so the trace checks can read it unchanged.

        The Number-trace check is arithmetic over *prose against the Claim it cites*,
        and that is exactly what a tail is. Reusing it is what keeps a supporting row
        from becoming a second, thinner rule about figures — which is the shape a
        résumé lies in most easily, since a credential line reads as fact.
        """
        return Bullet(self.slug, (self.claim_id,), self.tail, self.line)


def parse_bullets(
    path: Path,
) -> tuple[list[Bullet], list[SkillRow], dict[str, str], str, list[SupportingRow]]:
    """`bullets.md` — `## Summary`, a section per placed Entry, then `## Skills`.

        ## Summary
        Final-year CS undergraduate building generative AI applications end to end.

        ## helios-payments
        Lead: The whole reporting cycle was hand-run; automating it gave back ~5 hours.
        - helios-payments/c1: Cut checkout p99 latency 40% by batching commits
        - helios-payments/c1+c3: Cut checkout p99 latency and rebuilt the retry path

        ## Skills

        ### Languages
        - Go (helios-payments/c1)
        - Python (orbit-analytics/c2)

        ### Data & Analytics
        - ClickHouse (orbit-analytics/c1)

    Anything that does not parse is a hard failure naming the line. Skipping an
    unparseable line would drop a Bullet the Packer earned a slot for, and the
    résumé would come out a line short with nothing said about it — so the only
    tolerated extras are blank lines and a `# ` document title.

    A `Lead:` line, when present, is the section's first line — the composed
    sentence over the bank's `## lead` facts (docs/adr/0032-the-entry-arc.md §2).
    Returned as a third dict, entry slug -> composed sentence, since it is not a
    Bullet: not scored, not cited, never a candidate for a slot.

    `## Summary` is the FIRST section, mirroring `## Skills` being the last, and for
    the same reason: this file is written in page order and the Summary is the first
    thing on the page. It is plain prose rather than a list — its lines are joined
    with a single space, so the paragraph may be wrapped in the file however the
    composer likes — and it is returned as a fourth value, a bare string, because
    like a lead it is not a Bullet and unlike a lead it belongs to no Entry
    (docs/adr/0044-the-page-opens-on-a-summary.md).

    `## Supporting` is the one section that may sit BELOW `## Skills`, and it is last
    for the reason the Summary is first: the file is written in page order, and the
    supporting sections are the last thing above Education. It is absent on most
    runs, which is not a failure — a page with no supporting section on it is the
    normal page
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §7).
    """
    bullets: list[Bullet] = []
    rows: list[SkillRow] = []
    leads: dict[str, str] = {}
    summary_lines: list[str] = []
    supporting: list[SupportingRow] = []
    section: str | None = None
    section_started = False
    in_skills = False
    in_summary = False
    in_supporting = False
    #: `in_skills` says where the reader IS; this says the section was seen at all.
    #: They came apart when `## Supporting` was allowed to follow `## Skills`, and the
    #: refusal at the end is about the second question.
    saw_skills = False

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.rstrip()
        if not line.strip() or line.startswith("# "):
            continue

        heading = HEADING.match(line)
        if heading:
            name = heading.group("name")
            heading_name = name.strip().lower()
            if in_supporting:
                raise RenderError(
                    f"{path}:{number}: `## {name}` sits below `## Supporting`, which is "
                    f"the last section — this file is written in page order"
                )
            if in_skills and heading_name != SUPPORTING_HEADING:
                raise RenderError(
                    f"{path}:{number}: `## {name}` sits below `## Skills`, and the only "
                    f"section that may is `## Supporting` — every Bullet section comes "
                    f"first, in page order"
                )
            if heading_name == SUPPORTING_HEADING:
                if not in_skills:
                    raise RenderError(
                        f"{path}:{number}: `## Supporting` sits above `## Skills`, and the "
                        f"supporting sections are below Skills on the page — this file is "
                        f"written in page order"
                    )
                in_supporting, in_skills, in_summary, section = True, False, False, None
                continue
            if heading_name == SUMMARY_HEADING:
                if bullets or leads or section is not None:
                    raise RenderError(
                        f"{path}:{number}: `## Summary` sits below a Bullet section, and it "
                        f"is the FIRST section — this file is written in page order and the "
                        f"Summary is the first thing on the page"
                    )
                if summary_lines:
                    raise RenderError(
                        f"{path}:{number}: a second `## Summary` section. The page carries "
                        f"exactly one, charged {config.SUMMARY_LINES} line(s) once"
                    )
                in_summary, section = True, None
                continue
            in_summary = False
            if heading_name == SKILLS_HEADING:
                in_skills, saw_skills, section = True, True, None
            else:
                section = name.strip()
                section_started = False
            continue

        if in_summary:
            if line.lstrip().startswith("- "):
                raise RenderError(
                    f"{path}:{number}: the Summary is one paragraph of plain prose, not a "
                    f"list — it cites nothing, so there is no Claim for a `- ` line to "
                    f"name: {line.strip()}"
                )
            summary_lines.append(line.strip())
            continue

        if in_supporting:
            match = SUPPORTING_LINE.match(line)
            if not match:
                raise RenderError(
                    f"{path}:{number}: a supporting row is `- <entry-slug>/c<n>: <tail>` "
                    f"or a bare `- <entry-slug>`, and this is neither: {line.strip()}"
                )
            claim_id, tail = match.group("claim"), match.group("text")
            if bool(claim_id) != bool(tail):
                raise RenderError(
                    f"{path}:{number}: a supporting row cites a Claim and composes a tail, "
                    + (
                        "or does neither — this cites `"
                        f"{match.group('entry')}/{claim_id}` and composes nothing, so the "
                        f"Claim reaches no word on the page"
                        if claim_id
                        else "or does neither — this composes a tail and cites no Claim, so "
                        "the prose traces to nothing"
                    )
                    + f": {line.strip()}"
                )
            supporting.append(
                SupportingRow(match.group("entry"), claim_id, tail, number)
            )
            continue

        if in_skills:
            row_heading = SKILL_ROW_HEADING.match(line)
            if row_heading:
                rows.append(SkillRow(row_heading.group("label").strip(), number))
                continue
            match = SKILL_LINE.match(line)
            if not match:
                raise RenderError(
                    f"{path}:{number}: a Skills line is `- <skill> (<entry-slug>/c<n>)` "
                    f"and this is not one: {line.strip()}"
                )
            if not rows:
                raise RenderError(
                    f"{path}:{number}: this skill sits above the first `### <category>` "
                    f"row heading, so there is no row to put it on: {line.strip()}"
                )
            rows[-1].skills.append(
                Skill(match.group("skill"), match.group("entry"), match.group("claim"), number)
            )
            continue

        if section is None:
            raise RenderError(
                f"{path}:{number}: this line sits above the first `## <entry-slug>` "
                f"heading: {line.strip()}"
            )

        if not section_started:
            section_started = True
            lead_match = LEAD_LINE.match(line)
            if lead_match:
                leads[section] = lead_match.group("text")
                continue

        match = BULLET_LINE.match(line)
        if not match:
            raise RenderError(
                f"{path}:{number}: a Bullet line is `- <entry-slug>/c<n>: <prose>` "
                f"(or `<entry-slug>/c<n>+c<n>` for a merge) and this is not one: "
                f"{line.strip()}"
            )
        if match.group("entry") != section:
            raise RenderError(
                f"{path}:{number}: this Bullet cites {match.group('entry')} but sits under "
                f"`## {section}` — a Bullet belongs to the Entry it is filed under"
            )
        claim_ids = tuple(match.group("claims").split("+"))
        bullets.append(Bullet(match.group("entry"), claim_ids, match.group("text"), number))

    summary = " ".join(part for part in summary_lines if part)
    if not summary:
        raise RenderError(
            f"{path}: no `## Summary` section. The Summary is a fixed part of the page "
            f"and the budget charged {config.SUMMARY_LINES} line(s) for it before a word "
            f"was composed, so there is no version of this page without one — the Packer "
            f"runs first and cannot see whether you wrote it "
            f"(docs/adr/0044-the-page-opens-on-a-summary.md §5)"
        )
    if not bullets:
        raise RenderError(f"{path}: no Bullets — there is nothing to render")
    if not saw_skills:
        raise RenderError(
            f"{path}: no `## Skills` section. The Skills breadth list is a fixed part of "
            f"the page and the budget charges for it; write the heading with no rows "
            f"under it if the JD really asks for nothing the bank carries"
        )
    for row in rows:
        if not row.skills:
            raise RenderError(
                f"{path}:{row.line}: the `### {row.label}` row has no skills under it — "
                f"a row with nothing on it is a bold label and a colon"
            )
    if 0 < len(rows) < pack.MIN_SKILLS_ROWS:
        raise RenderError(
            f"{path}: the Skills section has {len(rows)} row(s), and a section is "
            f"{pack.MIN_SKILLS_ROWS} rows or it is not a section — its heading costs "
            f"{config.SECTION_LINES} lines, so one row spends three lines of page to "
            f"show one. Either find a second category the JD asks for, or drop the rows "
            f"and leave `## Skills` empty; the Packer hands the whole reservation back "
            f"either way"
        )
    return bullets, rows, leads, summary, supporting


# --------------------------------------------------------------------------
# What the Packer decided: allocation.md
# --------------------------------------------------------------------------

#: THE THIRD FIELD OF THIS LINE IS CONTRACT TOO, and for a different reason from the
#: claim line's width below: `ended` here is the Packer's copy of a field the bank
#: owns. `pack.py` reads `scores.md` and only `scores.md` (`0006`), so the copy cannot
#: be removed — but it can be checked, and `check_structure` does
#: (docs/adr/0031-the-entry-header-is-built.md §4).
PLACED_ENTRY = re.compile(
    r"^###\s+(?P<slug>\S+)\s+—\s+(?P<type>job|project)\s+—\s+ended\s+(?P<ended>\S+)\s+—\s+"
    r"entry score\s+[0-9.]+\s+—\s+(?:(?P<lead>lead)\s+—\s+)?"
)

#: A placed claim line, whose THIRD FIELD IS CONTRACT: it carries the width the
#: Packer granted the slot, in typeset lines. The width is read from here rather
#: than from `scores.md` because a *declared* want is not a *granted* line, and only
#: the allocation knows which wants survived. This is the second place
#: `allocation.md`'s wording is load-bearing, after the `Skills:` line, and the cost
#: is recorded rather than discovered (`docs/adr/0025-bullet-wrap-cost.md` §6). The
#: `claims` group is one id or a `+`-joined merge group — one row, one unit
#: (docs/adr/0034-a-merged-bullet-coordinates.md).
PLACED_CLAIM = re.compile(
    rf"^-\s+{CITED_REF_GROUP}\s+—\s+[0-9]\.[0-9]{{2}}\s+—\s+(?P<width>[12])\s+lines?\s+—"
)


@dataclass
class PlacedEntry:
    """One Entry the Packer placed, and the units it allocated Bullet slots to.

    A unit is one Claim id or a merge group's `+`-joined ids. `widths` runs
    parallel to `units`: what each slot was charged, in typeset lines. It is what
    the length lint measures the composed prose against.
    """

    slug: str
    type: str
    #: The Packer's copy of the Entry's `ended`, carried through `scores.md`. Checked
    #: against the bank's own field, never used to render anything.
    ended: str
    #: The Packer's copy of whether this Entry carries a lead, read off the `##
    #: Leads` table. Checked against the bank's own `## lead` block
    #: (docs/adr/0035-the-lead-crosses-the-seam.md §2).
    lead: bool
    units: list[tuple[str, ...]]
    widths: list[int] = field(default_factory=list)

    @property
    def claim_ids(self) -> list[str]:
        """Every individual Claim id across every unit, flattened — Skills-line
        resolution and similar checks want the flat set, not the grouping."""
        return [claim_id for unit in self.units for claim_id in unit]


def parse_allocation(path: Path) -> list[PlacedEntry]:
    """The `## Placed` section of `allocation.md`, in page order.

    Only the two machine-written shapes are read — the `###` entry heading and the
    `-` claim lines beneath it. The prose the Packer writes around them is ignored
    on purpose: `allocation.md` is a document for a person that a script also reads,
    and tightening this to reject prose would make every wording change a breakage.

    That property is NARROWER than it was by exactly two fields: the claim line's
    granted width, and the entry line's `ended` — a copy of a bank field, checked
    below rather than trusted. Changing `pack.py`'s wording in either place means
    changing a pattern here and the fixture in `tests/test_render.py`. A claim line
    the pattern cannot read is a claim line with no slot, which the caller catches;
    an entry heading it cannot read is an entry that never placed, which
    `check_structure` catches as an unfilled slot.
    """
    placements: list[PlacedEntry] = []
    in_placed = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_placed = line.strip() == "## Placed"
            continue
        if not in_placed:
            continue
        entry = PLACED_ENTRY.match(line)
        if entry:
            placements.append(
                PlacedEntry(
                    entry.group("slug"),
                    entry.group("type"),
                    entry.group("ended"),
                    entry.group("lead") is not None,
                    [],
                    [],
                )
            )
            continue
        claim = PLACED_CLAIM.match(line)
        if claim and placements:
            placements[-1].units.append(tuple(claim.group("claims").split("+")))
            placements[-1].widths.append(int(claim.group("width")))

    if not placements:
        raise RenderError(
            f"{path}: no placed Entries under a `## Placed` heading — this is not an "
            f"allocation.md written by tools/pack.py"
        )
    for placement in placements:
        if not placement.units:
            raise RenderError(
                f"{path}: {placement.slug} placed with no Bullet slots, which the Packer "
                f"never writes — the minimum block is a header and one Bullet"
            )
    return placements


#: `allocation.md`'s `## Supporting` section, in its two machine-written shapes. This
#: is the third place the Packer's wording is contract, after the `Skills:` line and
#: the placed-claim line's width, and it is recorded here rather than left to be
#: discovered (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §5).
#:
#: The `ended` on the row line is the Packer's copy of a bank field, carried across
#: the seam exactly as a placed Entry's is, and checked against the bank below rather
#: than trusted — the copy is what ordered the residue fill, and the page prints a
#: date built from the field.
PLACED_SUPPORTING_SECTION = re.compile(r"^###\s+(?P<section>\S+)\s+—\s+")
PLACED_SUPPORTING_ROW = re.compile(
    rf"^-\s+(?P<slug>{bank.ENTRY_SLUG_PATTERN})\s+—\s+ended\s+(?P<ended>\S+)\s+—\s+"
    r"(?P<how>[^—]+?)\s+—\s+"
)


@dataclass
class PlacedSupporting:
    """One supporting row the Packer seated, with the section it prints in."""

    section: str
    slug: str
    #: The Packer's copy of the bank's `ended`. Checked, never used to render.
    ended: str
    #: `the posting's call` or `the room left over` — carried so the Renderer can
    #: say why a section is on the page it just built, and read by nothing else.
    how: str


def parse_supporting(path: Path) -> list[PlacedSupporting]:
    """The `## Supporting` section of `allocation.md`, in page order.

    Empty on most runs, and an empty result is not an error: `## Supporting` says
    *No supporting section placed.* on every page that carries none, which is the
    normal page. An allocation written before this section existed also yields an
    empty list, and that is right — it charged for no supporting section, so the page
    it describes has none.
    """
    placed: list[PlacedSupporting] = []
    section: str | None = None
    in_supporting = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_supporting = line.strip() == "## Supporting"
            continue
        if not in_supporting:
            continue
        heading = PLACED_SUPPORTING_SECTION.match(line)
        if heading:
            section = heading.group("section")
            continue
        row = PLACED_SUPPORTING_ROW.match(line)
        if row and section:
            placed.append(
                PlacedSupporting(section, row.group("slug"), row.group("ended"), row.group("how"))
            )
    return placed


#: The Packer's `Skills:` line, in its two final-pass forms. The reservation's own
#: wording matches neither, which is the point: a reservation must not render.
#:
#: THIS IS THE ONE LINE OF allocation.md WHOSE WORDING IS CONTRACT. Everywhere else
#: the Packer's prose is ignored on purpose (see `parse_allocation`), and the cost of
#: narrowing that here is recorded in `docs/adr/0023-skills-allocation-check.md`.
#: Changing the wording in pack.py means changing these two patterns and the fixture
#: in tests/test_render.py — the suite fails on the way past if you do not.
ALLOCATED_ROWS = re.compile(r"^Skills: \d+ row\(s\), (?P<lines>[0-9,]+) typeset line")
ALLOCATED_NO_SECTION = re.compile(r"^Skills: no section")


ALLOCATION_EDUCATION = re.compile(r"^Education: (?P<rows>\d+) row", re.M)


def parse_allocation_education(path: Path) -> int:
    """The Education rows the Packer charged, from its `Education:` line.

    An allocation written before the line existed was charged `pack.EDUCATION_ROWS`.
    """
    match = ALLOCATION_EDUCATION.search(path.read_text(encoding="utf-8"))
    return int(match.group("rows")) if match else pack.EDUCATION_ROWS


def parse_allocation_skills(path: Path) -> list[int]:
    """What the Packer charged the Skills section for, one line count per row.

    Read for the same reason the placed Claims are: the budget is only true if the
    page holds what it was charged for. The Packer is handed the row shape as an
    argument (`--skills-rows`), so nothing else connects the number it spent to the
    rows that are about to typeset — and a wrong one is a two-page PDF the
    page-count assert would blame on the constants.
    """
    for line in path.read_text(encoding="utf-8").splitlines():
        if ALLOCATED_NO_SECTION.match(line):
            return []
        allocated = ALLOCATED_ROWS.match(line)
        if allocated:
            return [int(cell) for cell in allocated.group("lines").split(",")]
        if line.startswith("Skills: "):
            raise RenderError(
                f"{path} is a RESERVATION, not a finished allocation: it reads\n"
                f"  {line.strip()}\n"
                f"The Packer runs twice, and the Skills rows are composed in between — "
                f"re-run `python tools/pack.py <run> --skills-rows <counts>` and render "
                f"from that. Rendering the reservation would put a page on paper that "
                f"was budgeted for four rows nobody composed"
            )
    raise RenderError(
        f"{path}: no `Skills:` line — this is not an allocation.md written by "
        f"tools/pack.py, or it predates the two-pass Packer"
    )


# --------------------------------------------------------------------------
# What the maker settled: checkpoint.md
# --------------------------------------------------------------------------

#: The one section of `checkpoint.md` a script reads. It holds the run's
#: compose-time calls — the judgements too small to halt for and too load-bearing to
#: leave unwritten — and a dropped figure is one of them
#: (`docs/adr/0029-when-a-number-may-leave.md` §3).
DECIDED_BY_RULE = "decided by rule"

#: A cited ref anywhere inside that section's prose. Deliberately loose about what
#: surrounds it: the section is written for a person, in sentences, and the ref is
#: the only part of a line this reads. Same grammar as a Bullet's citation, from the
#: same source, so `checkpoint.md` and `bullets.md` cannot disagree about what a ref
#: looks like. Merged refs too — `helios/c1+c3` — since a merged Bullet's figure is
#: its group's stored sum and dropping it is recorded under the merged ref.
DECIDED_REF = re.compile(CITED_REF_GROUP)


def parse_decided_by_rule(path: Path) -> set[str]:
    """Every Claim ref named under `## Decided by rule`, or an empty set.

    A missing `checkpoint.md` reads as *nothing recorded*, not as a failure. The file
    is written on every run, but a check that died on its absence would fail the run
    for the wrong reason and name the wrong file — and the failure that matters here
    already names the Claim and says what to write.
    """
    if not path.is_file():
        return set()
    refs: set[str] = set()
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line[3:].strip().lower() == DECIDED_BY_RULE
            continue
        if in_section:
            for match in DECIDED_REF.finditer(line):
                refs.add(match.group(0))
                refs.update(
                    f"{match.group('entry')}/{claim}" for claim in match.group("claims").split("+")
                )
    return refs


# --------------------------------------------------------------------------
# Step 1 — Profile validation: the one seam
# --------------------------------------------------------------------------

#: The three fields that land inside a LaTeX `\href` target as well as in the visible
#: text. Escaping is right for the copy and wrong for the target — an escaped `\_`
#: inside `\href` breaks the link instead of the compile — so the Template gets each
#: twice: escaped for the text, raw as `<field>_url` for the target. `_` and `~` are
#: fine raw; what a raw target cannot carry is refused here.
URL_FIELDS = ("email", "linkedin", "github")
URL_UNSAFE = re.compile(r"[\s&%$#{}^\\]")

EDUCATION_ROW = re.compile(r"^###\s+(?P<id>\S+)\s*$")

#: The Static profile's two `## ` blocks. Education is the rows; Standing is free
#: prose the Summary is composed from and nothing typesets
#: (docs/adr/0044-the-page-opens-on-a-summary.md §3).
EDUCATION_BLOCK = "education"
STANDING_BLOCK = "standing"

#: The Static profile's two header lines, in page order, and the fields the Template
#: builds each from. The Header-fit check reports against these, which is what turns
#: "it wrapped" into "shorten the contact line by about four characters".
#:
#: The grouping — which field lands on which line — lives here because
#: `templates/profile.example.md` publishes a flat contract with nowhere to say it.
#: `Profile.load` checks the two against each other, so a field added to the contract
#: cannot go unaccounted for here.
HEADER_LINE_FIELDS = {
    "name": ("name",),
    "contact": ("location", "phone", "email", "linkedin", "github"),
}
#: Profile keys a profile MAY carry and the example does not publish, because each has
#: a sensible default and a required key nobody needs is a hard failure waiting for
#: every new user (docs/adr/0057-the-page-reads-like-a-resume.md §2):
#:
#: - `education_first: yes|no` — where Education sits. Left out, it is decided from
#:   the dates: still studying or finished within a year puts it at the top.
OPTIONAL_PROFILE_FIELDS = ("education_first",)

#: Contact fields the example publishes and a profile may leave out or blank — not
#: everyone has a GitHub, and not everyone puts a phone number on a résumé. The
#: Template drops each with its separator. `name`, `location` and `email` stay
#: required: a header without them is not a header.
OPTIONAL_CONTACT_FIELDS = ("phone", "linkedin", "github")

#: - `gpa:` on an Education row — written as it should read, `CGPA 8.4/10` or
#:   `GPA 3.8/4.0`, and set after the degree on the row's second line.
OPTIONAL_EDUCATION_KEYS = ("gpa",)

#: How recently a degree may have finished and still lead the page. A year: a new
#: graduate's degree is still their strongest credential; after that, the work is.
RECENT_GRADUATE_YEARS = 1

YEAR = re.compile(r"\b(19|20)\d{2}\b")

#: What the Template puts between the contact fields — `$|$`, which is one glyph
#: with a space either side. Plain text here, because the count this feeds is
#: advice to a human editing `bank/profile.md`, not a measurement.
HEADER_SEPARATOR = " | "


class Profile:
    """`bank/profile.md` — the Static profile, and everything render.py asks of it.

    The one seam every path that produces a PDF goes through. The Header-fit check
    validates the same file but can only run after the compile, so it lives here as
    `check_header_fit`, called between the compile and the page-count assert — before
    it, because a wrapped header can tip the page to two and the assert would then
    blame the constants.

    The keys are the contract `templates/profile.example.md` publishes, read out of
    that file rather than restated here. `HEADER_LINE_FIELDS` is not an exception: it
    says which field lands on which header line, which the example has nowhere to
    state, and `load` checks it names the same set.
    """

    def __init__(
        self,
        path: Path,
        fields: dict[str, str],
        education: list[dict[str, str]],
        standing: list[str] | None = None,
    ):
        self.path = path
        self.fields = fields
        self.education = education
        #: The maker's own durable self-description, in their words — what the Summary
        #: is composed from where no Claim carries the fact
        #: (docs/adr/0044-the-page-opens-on-a-summary.md §3). Nothing typesets it and
        #: nothing validates its content; it is read by whoever composes the Summary
        #: and priced by tools/bankcheck.py. Empty is legal and common.
        self.standing = standing or []

    @classmethod
    def load(cls, path: Path) -> Profile:
        example = PROFILE_EXAMPLE
        if not path.is_file():
            raise RenderError(
                f"no Static profile at {path} — write one by hand from {example}"
            )
        expected_fields, expected_rows, _ = cls._parse(example)
        if not expected_rows:
            raise RenderError(
                f"{example} publishes no `### e<n>` Education row to validate against"
            )
        expected_row = expected_rows[0]
        grouped = {field for line in HEADER_LINE_FIELDS.values() for field in line}
        if grouped != set(expected_fields):
            raise RenderError(
                f"{example} publishes {sorted(expected_fields)} and HEADER_LINE_FIELDS in "
                f"tools/render.py groups {sorted(grouped)} onto the header's two lines. "
                f"They have to be the same set: the Header-fit check reports how much of a "
                f"wrapped line to cut, and a field missing from the grouping would make "
                f"that advice quietly wrong"
            )
        fields, education, standing = cls._parse(path)

        for key in expected_fields:
            if key in OPTIONAL_CONTACT_FIELDS:
                fields.setdefault(key, "")
                continue
            if key not in fields:
                raise RenderError(f"{path}: missing `{key}` (see {example})")
            if not fields[key]:
                raise RenderError(f"{path}: `{key}` is blank, and no value may be blank")
        for key in fields:
            if key not in expected_fields and key not in OPTIONAL_PROFILE_FIELDS:
                raise RenderError(
                    f"{path}: unknown key `{key}` — {example} publishes the contract, and "
                    f"a key it does not name is a typo that would render an empty header"
                )
        for field in URL_FIELDS:
            if URL_UNSAFE.search(fields.get(field, "")):
                raise RenderError(
                    f"{path}: `{field}` contains a character that is not URL-safe (spaces, "
                    f"% # & $ ^ \\ {{ }}). It goes inside a LaTeX \\href target, where such a "
                    f"character breaks the link silently instead of failing the compile"
                )

        flag = fields.get("education_first", "").strip().lower()
        if flag and flag not in ("yes", "no"):
            raise RenderError(
                f"{path}: `education_first: {fields['education_first']}` — write `yes` or "
                f"`no`, or leave the key out and the dates decide"
            )
        if not education:
            raise RenderError(
                f"{path}: no Education rows — {example} defines at least one `### e1` "
                f"section under `## Education`"
            )
        for index, row in enumerate(education, start=1):
            for key in expected_row:
                if not row.get(key):
                    raise RenderError(
                        f"{path}: Education row {index} is missing `{key}` (see {example})"
                    )
            for key in row:
                if key not in expected_row and key not in OPTIONAL_EDUCATION_KEYS:
                    raise RenderError(
                        f"{path}: Education row {index} has unknown key `{key}` (see {example})"
                    )
        return cls(path, fields, education, standing)

    def check_education_charge(self, charged: int) -> None:
        """The Education rows `allocation.md` was packed for, against the profile now.

        pack.py counts them when it runs, so the two disagree only when the profile
        was edited after the pack. More rows than charged is a page promising lines it
        does not have; fewer is lines left unspent, worth a note and no more.
        """
        rows = len(self.education)
        if rows > charged:
            raise RenderError(
                f"{self.path}: {rows} Education rows, but allocation.md was packed for "
                f"{charged}. Re-run pack.py — left as it is, the page promises "
                f"{(rows - charged) * config.ENTRY_HEADER_LINES} line(s) it does not have"
            )
        if rows < charged:
            note(
                f"{self.path}: {rows} Education row(s), and allocation.md was packed for "
                f"{charged} — re-run pack.py to give the difference to the Bullets"
            )

    @staticmethod
    def _parse(path: Path) -> tuple[dict[str, str], list[dict[str, str]], list[str]]:
        """The `---` scalars, `### e<n>` rows under `## Education`, `## Standing` prose.

        The scalars are read by the bank's own frontmatter parser, so the two
        hand-written file kinds cannot drift into two dialects of one shape. What is
        local is the Education block, which no Entry file has.

        `## Standing` is optional, holds free prose rather than `key: value` lines,
        and is **named here rather than skipped**. Everything else in this file is
        validated to the letter — an unknown frontmatter key is a hard failure — so a
        block that parsed by being ignored would be the one place a typo in the
        maker's own file went quietly nowhere
        (docs/adr/0044-the-page-opens-on-a-summary.md §3).
        """
        lines = bank.strip_comments(path.read_text(encoding="utf-8")).splitlines()
        fields, body = bank.parse_frontmatter(lines, path)
        education: list[dict[str, str]] = []
        standing: list[str] = []
        row: dict[str, str] | None = None
        block = EDUCATION_BLOCK

        for number, line in enumerate(lines[body:], start=body + 1):
            if line.startswith("## "):
                name = line[3:].strip().lower()
                if name not in (EDUCATION_BLOCK, STANDING_BLOCK):
                    raise RenderError(
                        f"{path}:{number}: unknown block `{line.strip()}` — the Static "
                        f"profile holds `## Education` and, optionally, `## Standing`"
                    )
                block = name
                continue
            if not line.strip():
                continue
            if block == STANDING_BLOCK:
                standing.append(line.strip())
                continue
            match = EDUCATION_ROW.match(line)
            if match:
                row = {}
                education.append(row)
                continue
            pairs = bank.split_fields(line)
            if not pairs:
                raise RenderError(
                    f"{path}:{number}: expected a `key: value` line and found: {line.strip()}"
                )
            if row is None:
                raise RenderError(
                    f"{path}:{number}: `{pairs[0][0]}` sits below the frontmatter and above "
                    f"any `### e<n>` Education row, where nothing reads it"
                )
            for key, value in pairs:
                if key in row:
                    raise RenderError(f"{path}:{number}: `{key}` is set twice")
                row[key] = value

        return fields, education, standing

    def education_first(self, today: date | None = None) -> bool:
        """Whether Education leads the page — a student's or a new graduate's does.

        The profile's `education_first:` decides when it is there. Otherwise the
        latest year any Education row's `dates` mentions decides: a degree finishing
        this year or later, or within `RECENT_GRADUATE_YEARS` of it, is still the
        strongest thing on the page (docs/adr/0057-the-page-reads-like-a-resume.md §2).
        """
        flag = self.fields.get("education_first", "").strip().lower()
        if flag:
            return flag == "yes"
        years = [
            int(match.group())
            for row in self.education
            for match in YEAR.finditer(row.get("dates", ""))
        ]
        if not years:
            return False
        this_year = (today or date.today()).year
        return max(years) >= this_year - RECENT_GRADUATE_YEARS

    def context(self) -> dict:
        """The `profile` hole the Template takes, escaped.

        Every field is escaped for the visible text, and each of `URL_FIELDS` also
        rides raw as `<field>_url` for its `\\href` target — validated above to hold
        nothing a raw target cannot carry.
        """
        return {
            **{key: escape_latex(value) for key, value in self.fields.items()},
            **{f"{key}_url": self.fields.get(key, "") for key in URL_FIELDS},
            "education": [
                {key: escape_latex(value) for key, value in row.items()}
                for row in self.education
            ],
        }

    def header_text(self) -> dict[str, str]:
        """The two header lines as a reader sees them — for counting, not measuring.

        The typeset width comes from the Template; this is only what the failure
        message quotes back and divides by, so the maker can see the line that is
        too long and be told roughly how much of it to lose.
        """
        return {
            line: HEADER_SEPARATOR.join(
                self.fields[field] for field in fields if self.fields.get(field)
            )
            for line, fields in HEADER_LINE_FIELDS.items()
        }

    def check_header_fit(self, log: str) -> None:
        """Neither header line wrapped, per TeX — the Header-fit check.

        Detect by height, report by width (`docs/adr/0017-header-fit-check.md`).
        The Template measures each line twice from the macro it typesets it from,
        once unbreakable and once line-broken for real; taller means it broke. This
        reads that verdict, and touches the widths only to say how much to cut.

        Nothing here models where TeX breaks. It cannot be modelled from a width:
        how far a line's interword glue will shrink is a property of its content,
        and a strict width comparison fails a 119-character contact line that
        measures 1.75pt over the line and does not wrap.
        """
        measured = read_header_fit(log)
        missing = [
            line
            for line in HEADER_LINE_FIELDS
            if not HEADER_FIT_VALUES <= measured.get(line, {}).keys()
        ]
        if missing:
            raise RenderError(
                f"the compile log carries no Header-fit measurement for the "
                f"{', '.join(missing)} line. templates/resume.tex.j2 emits one per "
                f"header line, and a résumé whose header could not be checked does "
                f"not ship — a wrapped header is invisible in the PDF itself"
            )

        text = self.header_text()
        wrapped = [
            report_header_wrap(line, measured[line], text[line])
            for line in HEADER_LINE_FIELDS
            if measured[line]["broken"] > measured[line]["flat"] + WRAP_NOISE_PT
        ]
        if not wrapped:
            return
        raise RenderError(
            f"{self.path}: the Static profile header does not fit.\n"
            + "\n".join(wrapped)
            + f"\n\nHEADER_LINES charges the header {config.HEADER_LINES} lines for a "
            f"one-line name above a one-line contact line, so a wrapped header spends "
            f"a line the budget never granted. Nothing else catches this: a centred "
            f"line breaks legally, so LaTeX issues no warning and the résumé comes "
            f"out a line short of what the allocation was packed for"
        )


#: A wrap costs a whole line — 12.00pt on the contact line, 23.11pt on the name —
#: while an unwrapped line measures the same to the scaled point in both boxes. A
#: floating-point floor, not a tolerance: any value in (0, 12) picks the same cases.
WRAP_NOISE_PT = 1.0

HEADER_FIT = re.compile(
    r"AUTOAPPLY:headerfit:(?P<line>[a-z]+):(?P<what>[a-z]+):(?P<points>[0-9.]+)pt"
)
#: What the Template promises per header line. Checked rather than assumed, so a
#: truncated log fails the run instead of raising a KeyError two frames down.
HEADER_FIT_VALUES = frozenset({"flat", "broken", "width", "avail"})


def read_header_fit(log: str) -> dict[str, dict[str, float]]:
    """The Template's four measurements per header line, out of the compile log.

    One value per marker, because pdfTeX wraps the `.log` at 79 columns and a
    single line carrying all four would be split down the middle of a number.
    `pdflatex` truncates the log on each pass, so this reads the last pass's — the
    passes measure the same header and agree.
    """
    found: dict[str, dict[str, float]] = {}
    for match in HEADER_FIT.finditer(log):
        found.setdefault(match.group("line"), {})[match.group("what")] = float(
            match.group("points")
        )
    return found


#: The Template's Summary-fit measurement — the composed paragraph boxed at the
#: width it typesets at. One `\typeout` per value, same reason as the header's: the
#: `.log` wraps at 79 columns.
SUMMARY_FIT = re.compile(r"AUTOAPPLY:summaryfit:(?P<what>[a-z]+):(?P<points>[0-9.]+)pt")


def check_summary_fit(path: Path, log: str, summary: str) -> None:
    r"""The Summary fits in the lines the budget charged it — per TeX, not per model.

    The Header-fit check's sibling, and the second half of what `SUMMARY_CHARS`
    starts. A Summary that runs to three typeset lines is **silent**: a paragraph
    breaks legally, so LaTeX warns about nothing, the overfull-box check sees
    nothing, and the page comes out a line short of what the allocation was packed
    for. Exactly the failure `0017` built the Header-fit check for
    (docs/adr/0044-the-page-opens-on-a-summary.md §6).

    The character budget cannot close it. `SUMMARY_CHARS` bounds two lines, and a
    paragraph breaks at word boundaries — so where the break lands is a property of
    the words, not of their count. So this does not judge a width either: it reads
    the height TeX measured for the very paragraph the page typeset, and compares it
    to `SUMMARY_LINES x BULLET_LINE_PT`, which is what the budget spent.

    The calibration probe is what makes that ceiling a gate rather than a number
    that always passes: it measures a two-line Summary at 20.89pt and a three-line
    one at 32.89pt against a 28.00pt ceiling, and fails if the two ever land on the
    same side of it.
    """
    measured = {
        match.group("what"): float(match.group("points"))
        for match in SUMMARY_FIT.finditer(log)
    }
    if "height" not in measured:
        raise RenderError(
            f"the compile log carries no Summary-fit measurement. "
            f"templates/resume.tex.j2 emits one, and a résumé whose Summary could not be "
            f"checked does not ship — a Summary that ran to a third line is invisible in "
            f"the PDF itself"
        )
    ceiling = config.SUMMARY_LINES * config.BULLET_LINE_PT
    if measured["height"] <= ceiling:
        return
    lines = math.ceil(measured["height"] / (ceiling / config.SUMMARY_LINES))
    raise RenderError(
        f"{path}: the Summary does not fit. It typesets {measured['height']:.0f}pt tall "
        f"against the {ceiling:.0f}pt the budget charged for it "
        f"({config.SUMMARY_LINES} x {config.BULLET_LINE_PT:.0f}pt), so it is running to "
        f"about {lines} typeset lines instead of {config.SUMMARY_LINES}.\n"
        f"    {summary}\n\n"
        f"It is inside SUMMARY_CHARS ({len(summary)} of {config.SUMMARY_CHARS}), which "
        f"means the line breaks landed badly rather than that it is too long — cut a "
        f"few words and it will come back. Nothing else catches this: a paragraph breaks "
        f"legally, so LaTeX issues no warning and the page comes out a line short of what "
        f"the allocation was packed for"
    )


def report_header_wrap(line: str, measured: dict[str, float], text: str) -> str:
    """One wrapped header line, named, with roughly how many characters to lose.

    The character count is the point of reporting a width at all — nobody can act on
    "7.30pt too wide". It comes from the offending line's own average character
    width, since the name and contact lines are different fonts at different sizes.

    "About" is load-bearing in both directions: the target is generous, because TeX
    broke past the shrink its glue allowed rather than at the exact fit, and the
    conversion is an average, so cutting that many narrow characters may not get
    there. The check runs again on the next compile and says so.
    """
    over = measured["width"] - measured["avail"]
    characters = max(1, math.ceil(over / (measured["width"] / len(text))))
    plural = "" if characters == 1 else "s"
    return (
        f"  the {line} line wraps: it typesets {measured['width']:.0f}pt wide against "
        f"the {measured['avail']:.0f}pt the page gives it, so shorten it by about "
        f"{characters} character{plural} —\n    {text}"
    )


# --------------------------------------------------------------------------
# Step 2 — Structural check
# --------------------------------------------------------------------------


def resolve_claim(
    entries: dict[str, bank.Entry], entry: str, claim_id: str, where: str
) -> bank.Claim:
    """The cited Claim, or a hard failure naming the citation that did not resolve."""
    found = entries.get(entry)
    if found is None:
        raise RenderError(f"{where} cites {entry}/{claim_id}, and no bank entry is `{entry}`")
    claim = found.claim(claim_id)
    if claim is None:
        raise RenderError(
            f"{where} cites {entry}/{claim_id}, and {found.path} has no claim `{claim_id}`"
        )
    return claim


@dataclass(frozen=True)
class PageContents:
    """Everything one run puts on the page, assembled once and read by every step.

    The five travelled together anyway — the Static profile, the Packer's page order,
    the Bullets, the bank behind them and the Skills rows. Naming them puts the two
    joins every step had to redo in one place: `skills`, and `blocks`, the pairing of
    a placed Entry with the Bank entry it was placed from.

    `entries` is the whole bank, not the placed subset: the Bullets and the Skills
    rows cite Claims from Entries that never placed.

    `blocks` assumes every placed slug resolves, which is `check_structure`'s job;
    every step that calls it runs after. `bullets_path` rides along because it is what
    the failures name.
    """

    profile: Profile
    placed: list[PlacedEntry]
    allocated_skill_rows: list[int]
    bullets: list[Bullet]
    skill_rows: list[SkillRow]
    leads: dict[str, str]
    summary: str
    entries: dict[str, bank.Entry]
    bullets_path: Path
    #: The supporting rows the Packer seated, and the ones composed against them.
    #: Both empty on most runs
    #: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md).
    placed_supporting: list[PlacedSupporting] = field(default_factory=list)
    supporting: list[SupportingRow] = field(default_factory=list)
    #: Every term the keyword pass recognises — the bank's skills, `bank/vocabulary.md`
    #: and this run's `terms.md`, unioned by `keyword_vocabulary`. With every
    #: `MAX_*_KEYWORDS` at 0 none of them is bolded (0057 §4); the pass still tells a
    #: version like `Python 3.11` from a figure. It travels with the
    #: page contents because the length lint and the fill both need the same one, and
    #: two calls that read the files separately could disagree about what the page
    #: costs (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §4).
    vocabulary: tuple[str, ...] = ()

    @property
    def supporting_blocks(self) -> list[tuple[PlacedSupporting, SupportingRow, bank.Entry]]:
        """Each seated supporting row with the composed row and the Bank entry behind it.

        Safe for the same reason `blocks` is: `check_structure` has already refused a
        page whose composed rows are not exactly the seated ones, in order.
        """
        return [
            (place, row, self.entries[place.slug])
            for place, row in zip(self.placed_supporting, self.supporting)
        ]

    @property
    def supporting_tails(self) -> list[Bullet]:
        """The composed tails, shaped as Bullets, for the trace checks to read."""
        return [row.as_bullet() for row in self.supporting if row.tail]

    @property
    def skills(self) -> list[Skill]:
        """Every skill on the page, in row order then line order.

        The rows are what typesets; this is the flat view the citation checks want,
        since a skill's backing Claim has nothing to do with which row it landed in.
        """
        return [skill for row in self.skill_rows for skill in row.skills]

    @property
    def blocks(self) -> list[tuple[PlacedEntry, bank.Entry]]:
        """Each placed Entry with the Bank entry behind it, in the Packer's page order."""
        return [(place, self.entries[place.slug]) for place in self.placed]

    @property
    def granted_widths(self) -> dict[str, int]:
        """Bullet ref -> the typeset lines the Packer charged that slot for.

        What the length lint measures against. A ref that is not here has no slot,
        which `check_structure` refuses before the lint ever runs. Keyed by the
        same `+`-joined ref a merged Bullet's own `.ref` produces.
        """
        return {
            f"{place.slug}/{'+'.join(unit)}": width
            for place in self.placed
            for unit, width in zip(place.units, place.widths)
        }


def check_structure(contents: PageContents) -> None:
    """Every citation resolves, and the page is exactly what the allocation charged.

    Exactly: no extra Bullet, no unfilled slot, in the Packer's page order, and a
    Skills section shaped like the one the second pass was told about. The
    allocation is what makes block height true by construction — an extra Bullet
    spends a line the budget never granted, and a missing one silently changes what
    the résumé argues while still compiling to a tidy page.

    This is also what makes `PageContents.blocks` safe for everything downstream:
    the slug-resolves check below is the one that has to use `.get`.
    """
    path = contents.bullets_path
    bullets, entries = contents.bullets, contents.entries

    for bullet in bullets:
        for claim_id in bullet.claim_ids:
            resolve_claim(entries, bullet.entry, claim_id, f"{path}:{bullet.line}")
    for skill in contents.skills:
        resolve_claim(entries, skill.entry, skill.claim_id, f"{path}:{skill.line}")

    check_skills_allocation(contents)
    check_supporting_allocation(contents)

    for place in contents.placed:
        entry = entries.get(place.slug)
        if entry is None:
            raise RenderError(
                f"allocation.md places `{place.slug}` and no bank entry is `{place.slug}` — "
                f"the allocation was packed from a Score table that has moved on from the bank"
            )
        if entry.type != place.type:
            raise RenderError(
                f"allocation.md places {place.slug} as a `{place.type}` and {entry.path} says "
                f"`type: {entry.type}` — the two route the Entry to different sections"
            )
        # The Packer is bank-blind by `0006`, so `scores.md` carries a COPY of the
        # Entry's `ended` and the Packer orders the page on that copy. Nothing else
        # ties the copy to the field it was copied from, and the page prints a date
        # built from the field — so the two can drift into a résumé whose recency
        # ordering and whose printed dates disagree, with nothing said. This is the
        # one comparison that closes it (docs/adr/0031-the-entry-header-is-built.md §4).
        if entry.ended != place.ended:
            raise RenderError(
                f"allocation.md says {place.slug} ended `{place.ended}` and {entry.path} "
                f"says `ended: {entry.ended}`. The bank owns that field and scores.md "
                f"carries a copy of it — fix the copy in scores.md and re-run "
                f"`python tools/pack.py <run>`, because the Packer ordered this page on "
                f"the copy and the page prints a date built from the bank"
            )
        # The lead, tied back to the bank fact it was charged for. A lead is the run's
        # CHOICE now, not the bank's to impose: a page carries one only where the
        # scorer marked it `y` (docs/adr/0057-the-page-reads-like-a-resume.md §5,
        # reversing 0035 §1's "the model may not withhold it"). What is still a fault
        # is a lead charged that the bank cannot supply, a lead charged and not
        # written, and a lead written that nothing charged.
        bank_has_lead = entry.lead is not None
        composed_lead = contents.leads.get(place.slug)
        if place.lead and not bank_has_lead:
            raise RenderError(
                f"allocation.md charges {place.slug} a lead and {entry.path} has no "
                f"`## lead` block to compose it from — mark it `n` in scores.md's "
                f"`## Leads` table and re-run pack.py"
            )
        if place.lead and composed_lead is None:
            raise RenderError(
                f"allocation.md charges {place.slug} a lead line and "
                f"{contents.bullets_path} composes none — write the `Lead:` line, or mark "
                f"it `n` in `## Leads` and re-run pack.py"
            )
        if not place.lead and composed_lead is not None:
            raise RenderError(
                f"{contents.bullets_path} composes a `Lead:` line for {place.slug} and "
                f"allocation.md charged it none — mark it `y` in `## Leads` and re-run "
                f"pack.py, or drop the line"
            )

    seen_claims: dict[str, int] = {}
    for bullet in bullets:
        for claim_id in bullet.claim_ids:
            key = f"{bullet.entry}/{claim_id}"
            if key in seen_claims:
                raise RenderError(
                    f"{path}:{bullet.line}: {key} already has a Bullet on line "
                    f"{seen_claims[key]}. Every Claim appears in exactly one place on the "
                    f"page — as its own Bullet or in exactly one merge group, never both"
                )
            seen_claims[key] = bullet.line

    allocated = [
        f"{place.slug}/{'+'.join(unit)}" for place in contents.placed for unit in place.units
    ]
    written = [bullet.ref for bullet in bullets]
    if written == allocated:
        return

    extra = [ref for ref in written if ref not in allocated]
    missing = [ref for ref in allocated if ref not in written]
    if extra:
        raise RenderError(
            f"{path}: {extra[0]} has a Bullet but no slot in allocation.md — the Packer "
            f"decides how many lines the page has, so an extra Bullet is a line nobody "
            f"budgeted for" + also_naming(extra[1:])
        )
    if missing:
        raise RenderError(
            f"{path}: {missing[0]} was allocated a Bullet slot and none was written — an "
            f"unfilled slot leaves the page arguing something the allocation did not"
            + also_naming(missing[1:])
        )
    raise RenderError(
        f"{path}: the Bullets are the allocated ones but not in page order. "
        f"allocation.md reads {', '.join(allocated)}"
    )


def check_skills_allocation(contents: PageContents) -> None:
    """The rows about to typeset are the rows the Packer's second pass charged for.

    `--skills-rows` is an argument rather than a file, which is what keeps the
    Packer bank-blind — and it is also the one number in the budget that nothing
    else ties to the page. Charge too little and the run dies at the page-count
    assert with a message blaming the constants; charge too much and evidence is
    left off the page for room nobody used. Both are silent without this.
    """
    composed = [row_lines(row.label, row.text) for row in contents.skill_rows]
    if composed == contents.allocated_skill_rows:
        return
    if any(lines > pack.MAX_ROW_LINES for lines in composed):
        # A row past the cap has no legal allocation — the Packer refuses to be
        # told about one. Saying "re-run with --skills-rows 3,1" would send the
        # maker to a command that rejects the argument, so the length lint's
        # message is the one worth having, and it is two steps away.
        return
    shape = ",".join(str(lines) for lines in composed) or "no section"
    charged = ",".join(str(lines) for lines in contents.allocated_skill_rows) or "no section"
    raise RenderError(
        f"{contents.bullets_path} composes a Skills section of {shape} typeset "
        f"line(s), and allocation.md was charged for {charged}. The page would be "
        f"budgeted for a section it does not hold — re-run `python tools/pack.py "
        f"<run> --skills-rows {shape if composed else repr('')}` and compose the Bullets "
        f"against the allocation it writes"
    )


def check_supporting_allocation(contents: PageContents) -> None:
    """The supporting rows about to typeset are exactly the ones the Packer seated.

    Same standing as `check_skills_allocation` and the same failure behind it: the
    budget charged `SECTION_LINES` plus a row count, and a page holding a row nobody
    charged for is a line the budget never granted. The order matters too — the
    Packer's order is the page's, and it is what the section headings are grouped by
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §5).

    The `ended` copy is checked here rather than in the loop over placed Entries
    below, because a supporting entry never reaches that loop: it was never in the
    Score table, so `scores.md`'s `## Sections` is where its copy travelled and this
    is the only thing tying that copy to the field it was copied from.
    """
    path, entries = contents.bullets_path, contents.entries
    seated = [place.slug for place in contents.placed_supporting]
    written = [row.slug for row in contents.supporting]
    if written != seated:
        extra = [slug for slug in written if slug not in seated]
        missing = [slug for slug in seated if slug not in written]
        if extra:
            raise RenderError(
                f"{path}: `{extra[0]}` has a supporting row and no seat in allocation.md — "
                f"a supporting section is charged by its row count, so an extra row is a "
                f"line nobody budgeted for" + also_naming(extra[1:])
            )
        if missing:
            raise RenderError(
                f"{path}: allocation.md seats a supporting row for `{missing[0]}` and none "
                f"was written — the budget paid for it" + also_naming(missing[1:])
            )
        raise RenderError(
            f"{path}: the supporting rows are the seated ones but not in the Packer's "
            f"order. allocation.md reads {', '.join(seated)}"
        )

    for place, row, entry in contents.supporting_blocks:
        if not entry.supporting:
            raise RenderError(
                f"allocation.md seats `{place.slug}` as a supporting row and {entry.path} "
                f"says `type: {entry.type}`, which competes for a Bullet slot — the two "
                f"put the same Entry in two places on one page"
            )
        if bank.SECTION_OF_TYPE[entry.type] != place.section:
            raise RenderError(
                f"allocation.md prints `{place.slug}` under `{place.section}` and "
                f"{entry.path} says `type: {entry.type}`, which routes to "
                f"`{bank.SECTION_OF_TYPE[entry.type]}` — scores.md's `## Sections` table "
                f"names the section and the bank owns the type, so fix the table and "
                f"re-run `python tools/pack.py <run>`"
            )
        if entry.ended != place.ended:
            raise RenderError(
                f"allocation.md says {place.slug} ended `{place.ended}` and {entry.path} "
                f"says `ended: {entry.ended}`. The bank owns that field and scores.md's "
                f"`## Sections` carries a copy — fix the copy and re-run "
                f"`python tools/pack.py <run>`, because the Packer ordered the room it "
                f"spent on the copy and the row prints a date built from the bank"
            )
        if row.claim_id is not None:
            resolve_claim(entries, row.slug, row.claim_id, f"{path}:{row.line}")


def supporting_row_text(row: SupportingRow, entry: bank.Entry) -> str:
    """Everything after the bold title: the org, the dates, and the tail if there is one.

    BUILT, not composed — `org` and the dates are the bank's own fields, and the
    dates come through `row_dates`, which collapses `started == ended` to one month
    so a credential with no expiry does not print a range to itself
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §3).

    The composed tail is a **complete sentence** and follows a full stop, which is
    what keeps the row readable as one line rather than a run of clauses. Everything
    up to it is the maker's own frontmatter; only the tail was written this run.
    """
    built = f"--- {entry.org}, {entry.row_dates}"
    return f"{built}. {row.tail}" if row.tail else built


def check_supporting_lengths(contents: PageContents) -> None:
    """A supporting row is one typeset line, and this is what makes that true.

    The cap is not a style preference: `supporting_charge` is a function of a row
    COUNT rather than of composed text, and it can only be one because a row never
    wraps. A Skills section needs a second Packer pass precisely because its rows may
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §6).

    Measured with `row_lines`, unchanged, because a supporting row IS a Skills row —
    a bold label and plain text in the same geometry. Its `len(label) + 2` charges
    two bold characters this row does not have, since the separator here is a space
    rather than a colon; that over-counts by about two characters' worth of budget,
    which is the direction the whole formula is built to err in.
    """
    for place, row, entry in contents.supporting_blocks:
        text = supporting_row_text(row, entry)
        lines = row_lines(entry.title, text)
        if lines <= 1:
            continue
        # What the line has left for the plain half once the BOLD title is charged
        # at its own rate, in characters. Said out loud because the label is most of
        # the row and the composer cannot see the exchange rate — a 33-character
        # credential name spends about 41 of the 103, and what is left over is
        # frequently no tail at all.
        room = int(
            (1 - Fraction(len(entry.title) + 2, config.BOLD_CHARS_PER_BULLET))
            * config.CHARS_PER_BULLET
        )
        raise RenderError(
            f"{contents.bullets_path}:{row.line}: the supporting row for {row.slug} "
            f"predicts {lines} typeset lines and a supporting row is one — it is charged "
            f"as one row, so a second line is a line the budget never granted. The bold "
            f"title spends {len(entry.title)} characters at the bold rate, leaving about "
            f"{room} for `{entry.org}` plus the dates plus any tail, and this row uses "
            f"{len(text)}. "
            + (
                f"Cut about {len(text) - room} character(s) from the tail, or drop it and "
                f"write the bare `- {row.slug}` — most rows carry no tail, and that is the "
                f"normal case rather than a loss"
                if row.tail
                else f"There is no tail to cut: shorten `title` or `org` in {entry.path}"
            )
        )


def also_naming(rest: list[str]) -> str:
    """The other offenders, so one run reports all of them rather than one per run."""
    return f" (also: {', '.join(rest)})" if rest else ""


# --------------------------------------------------------------------------
# Step 3 — the Bullet-length lint
# --------------------------------------------------------------------------


def row_lines(label: str, text: str) -> int:
    """Typeset lines one Skills row will take, from character counts alone.

    The bold label and the plain comma list are charged at their own measured
    rates, because bold is wider and charging it at the plain rate would
    over-promise — the one direction `config.py` forbids.

    THE DIRECTION OF ERROR IS THE POINT. Both rates come from the widest realistic
    sample rather than an average, so the predicted width is never under the real
    one and the predicted line count is never under the real one. It over-counts
    sometimes: the prototype's 286-character row predicts 4 lines and typesets 3.
    That costs a skill that would have fitted, and it is the right way round — a
    formula that under-counted would hand the Packer a budget promising a line the
    page does not have, and nothing downstream would catch it before the page-count
    assert (`docs/adr/0021-skills-row-cost.md` §3).

    Exact rationals, not floats: the interesting inputs are the ones that land on a
    whole number, and that is precisely where binary division would decide it by a
    rounding error.
    """
    return max(1, math.ceil(
        Fraction(len(label) + 2, config.BOLD_CHARS_PER_BULLET)
        + Fraction(len(text), config.CHARS_PER_BULLET)
    ))


#: What one bold character costs in plain-character-equivalents — 99/80 = 1.2375 at
#: today's constants. A RATIO OF TWO MEASURED NUMBERS AND THEREFORE A PROPERTY OF THE
#: FONT, not of the column: both constants are the same Bullet text width divided by a
#: pt-per-character rate, so the width cancels and what is left is bold's 6.056pt
#: against plain's 4.915pt (`docs/calibration.md`). That is the whole reason the
#: Summary can be charged for bold against `SUMMARY_CHARS` — a budget measured at a
#: different and wider `\linewidth` — without a second measurement and without a
#: `BOLD_SUMMARY_CHARS` nobody took
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §6).
BOLD_PENALTY = Fraction(config.CHARS_PER_BULLET, config.BOLD_CHARS_PER_BULLET)

#: THE LEAD'S OWN PENALTY, AND THE ONE PLACE THE PARAGRAPH ABOVE DOES NOT REACH. Both
#: of these counts are the LEAD's 514.40pt over a pt/char rate, so the width cancels
#: here too — what does not cancel is the sample family, and that is why this is 1.425
#: where a Bullet's is 1.2375. `LEAD_CHARS` is the worst realistic lead SENTENCE, which
#: is narrow prose; `BOLD_LEAD_CHARS` is the worst realistic bold SPAN, which is a
#: figure or a technical name and runs wide. Charging a lead's bold at the Bullet's
#: ratio would have been derivable and cheaper and is not what was measured
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).
LEAD_BOLD_PENALTY = Fraction(config.LEAD_CHARS, config.BOLD_LEAD_CHARS)


def bold_equivalent_chars(
    text: str, spans: Sequence[tuple[int, int]], penalty: Fraction = BOLD_PENALTY
) -> float:
    """`text`'s length with its bold runs charged at the bold rate.

    Bold is genuinely wider, which is why `BOLD_CHARS_PER_BULLET` exists beside
    `CHARS_PER_BULLET` for a Skills row's label. A line that sets its figures and a
    declared keyword in bold has exactly the same problem and is charged the same
    way — every bold character counts `BOLD_PENALTY` plain ones:

        equivalent = plain characters + bold characters x BOLD_PENALTY

    which is `calibration.md`'s row-lines formula with the label swapped for the
    emphasis spans. No new constant, because no new element — the page already
    measured this bold (docs/adr/0043-the-number-carries-the-emphasis.md §4).

    A 15-character span therefore drops a one-line Bullet's real ceiling from 99 to
    about 95. That is the honest price and it lands on the prose: lines get shorter.
    Charging bold at the plain rate would under-count, which is the one direction
    `calibration.md` forbids — it ends in a Bullet past the right margin, or a
    two-page PDF blaming the constants.

    `penalty` is the element's own ratio and defaults to a Bullet's. The Summary uses
    the default deliberately — `0046` §6's width-independence claim is exactly what
    lets it — while a lead passes `LEAD_BOLD_PENALTY`, which was measured rather than
    derived and comes out dearer.
    """
    bold_chars = sum(end - start for start, end in spans)
    return float(len(text) - bold_chars + bold_chars * penalty)


def bullet_line_cost(text: str, spans: Sequence[tuple[int, int]] = ()) -> float:
    """What a Bullet costs in typeset lines, its bold runs charged at the bold rate."""
    return bold_equivalent_chars(text, spans) / config.CHARS_PER_BULLET


def check_lengths(
    path: Path,
    bullets: list[Bullet],
    rows: list[SkillRow],
    widths: dict[str, int],
    vocabulary: Sequence[str] = (),
) -> None:
    """A Bullet against the width its slot was charged — `width x CHARS_PER_BULLET`.

    An over-budget Bullet **fails and is named**, and Opus rephrases that one Bullet
    shorter. It is never truncated (a cut sentence can assert something the Claim
    does not) and never dropped (a slot the Packer earned would vanish because a
    sentence ran four characters long).

    Composing UNDER the granted width does not fail. It wastes whitespace and cannot
    over-promise, and failing a run because a sentence came out crisp would be
    absurd; `tools/lengths.py` reports it as a finding instead
    (docs/adr/0025-bullet-wrap-cost.md §6).

    A Skills row is measured differently, because a row is *allowed* to wrap: what
    is capped is how far. A row that would run past two lines sheds its least
    prominent skills instead, and the cap is the maker's call rather than a
    measurement — past two lines the section stops reading as a breadth list.
    """
    for bullet in bullets:
        width = widths.get(bullet.ref, 1)
        spans = emphasis_spans(bullet.text, vocabulary)
        cost = bullet_line_cost(bullet.text, spans)
        if cost > width:
            # Say it in characters, because characters are what the maker rephrases
            # in. `over` is how many plain characters have to go for the weighted
            # cost to come back under the granted width.
            over = math.ceil((cost - width) * config.CHARS_PER_BULLET)
            emphasis = (
                f", of which {sum(end - start for start, end in spans)} are set in "
                f"bold at {config.BOLD_CHARS_PER_BULLET} to the line "
                f"({', '.join(f'`{bullet.text[start:end]}`' for start, end in spans)})"
                if spans
                else ""
            )
            raise RenderError(
                f"{path}:{bullet.line}: the Bullet for {bullet.ref} is "
                f"{len(bullet.text)} characters{emphasis} and its slot holds "
                f"{width * config.CHARS_PER_BULLET} "
                f"({width} x {config.CHARS_PER_BULLET}) — "
                f"rephrase this one {over} character(s) shorter: {bullet.text}"
            )
    for row in rows:
        lines = row_lines(row.label, row.text)
        if lines > pack.MAX_ROW_LINES:
            raise RenderError(
                f"{path}:{row.line}: the `{row.label}` skills row runs to {lines} "
                f"typeset lines and a row holds {pack.MAX_ROW_LINES} — drop the skills "
                f"this JD leans on least, from the end: {row.text}"
            )


# --------------------------------------------------------------------------
# Step 4 — the set checks
# --------------------------------------------------------------------------

#: THESE THREE ARE JUDGEMENTS, NOT MEASUREMENTS, and that is why they are here rather
#: than in config.py. Nothing measured them and nothing can: they are a reading of what
#: a page looks like to a person, in the same family as the Template's `\hfuzz=2pt` (*a
#: judgement about what a reader can see, not a measurement*) and `pack.MAX_ROW_LINES`.
#: config.py's docstring is a contract — MEASURED, NEVER ESTIMATED, off a compiled page
#: — and a second kind of number living in it weakens that however well it is labelled,
#: so they sit beside the check that spends them (docs/adr/0030-the-composed-set.md §6).
#:
#: They are deliberately WEAK. `0027` said *"a line that finishes in 66 characters has
#: not failed for being short"*; 88 is a far softer demand than 66, and one in three is
#: a far softer demand than most. The check counts characters and cannot tell a sentence
#: that finished early from one that was cut short — only a reader can — so it asks for
#: the least that still says something.
SPREAD_MIN_BULLETS = 6
SHORT_BY = 15
SHORT_ONE_IN = 3


@dataclass(frozen=True)
class Spread:
    """How a page's one-line Bullets sit against the cap, and whether that is a fault.

    Two-line Bullets are not in it at all. A second line was granted because
    compressing the claim would cost the thing worth saying (`0027` §5), so filling
    it is the point rather than evidence of writing to the cap.
    """

    one_line: int
    short: int
    threshold: int
    shortest: int | None

    @property
    def needed(self) -> int:
        """How many of them have to finish early. One in three, rounded up."""
        return math.ceil(self.one_line / SHORT_ONE_IN)

    @property
    def fires(self) -> bool:
        """Under `SPREAD_MIN_BULLETS` there is no rule: no distribution to speak of."""
        return self.one_line >= SPREAD_MIN_BULLETS and self.short < self.needed

    @property
    def finding(self) -> str:
        """The one line both `render.py` and `lengths.py` say it in.

        One wording, because the maker meets this in `lengths.py` while composing and
        again in `render.py` if they did not, and two phrasings of one rule read as
        two rules.
        """
        return (
            f"spread {self.short}/{self.needed} of {self.one_line} one-line bullets "
            f"at or under {self.threshold} (shortest is {self.shortest})"
        )


def measure_spread(bullets: list[Bullet], widths: dict[str, int]) -> Spread:
    """The one-line Bullets, counted against `CHARS_PER_BULLET - SHORT_BY`."""
    lengths = [
        len(bullet.text) for bullet in bullets if widths.get(bullet.ref, 1) == 1
    ]
    threshold = config.CHARS_PER_BULLET - SHORT_BY
    return Spread(
        one_line=len(lengths),
        short=sum(1 for length in lengths if length <= threshold),
        threshold=threshold,
        shortest=min(lengths, default=None),
    )


#: How many Bullets on one page may open on the same word. Two, and never two in one
#: entry. It was one, and on a page of fifteen Bullets that pushed composition off
#: the plain verbs — `Built`, `Cut`, `Automated` — into openings no person writes:
#: *"Got the other product teams running…"*, *"Two custom GPTs moved analysts…"*.
#: A recruiter notices the same verb three times down a column; they do not notice
#: `Built` once under each of two jobs (docs/adr/0057-the-page-reads-like-a-resume.md §6).
MAX_OPENER_USES = 2


def opener(text: str) -> str:
    """A Bullet's opening word, as a reader meets it.

    Case-insensitive, because `Built` and `built` open a line the same way. Hyphens
    are kept — `Hand-mapping` and `Hand-rolling` are different openings, and splitting
    them would make the check fire on a distinction nobody can see. Trailing
    punctuation is dropped so `Replaced,` and `Replaced` are one word.
    """
    return text.split()[0].rstrip(",;:.").casefold()


#: A word carrying one of the alternating suffixes, with the stem long enough to be a
#: stem. The `{3,}?` is what keeps `rise`, `wise`, `noise`, `size`, `prize` and `seize`
#: out structurally: there is no three-letter stem in front of the suffix, so they never
#: match and never need a list entry.
SPELLING_VARIANT = re.compile(
    r"\b(?P<stem>[A-Za-z]{3,}?)(?P<mark>is|iz|ys|yz)"
    r"(?P<tail>e|es|ed|er|ers|ing|ation|ations|ational)\b",
    re.IGNORECASE,
)

#: Stems where those letters are not the suffix. THE ONE SOFT EDGE IN THIS FILE:
#: everything else here is closed arithmetic, and this is a list that can be short. A
#: résumé says `supervised`, `revised`, `comprises` and `promising` constantly, and a
#: check that failed a page for writing one of them beside `standardization` would be
#: worse than no check at all. It fails loudly and names both words when it is wrong,
#: and the fix is one entry here (docs/adr/0030-the-composed-set.md §4).
#:
#: Each entry is what the regex above actually captures as `stem`, which is the
#: SHORTEST split that works — `advise` is `adv`, `supervise` is `superv`.
NOT_A_SUFFIX = frozenset(
    {
        "adv", "advert", "appr", "bru", "chast", "circumc", "compr", "comprom",
        "conc", "cru", "dem", "desp", "dev", "disgu", "enterpr", "exc", "exerc",
        "expert", "franch", "improv", "inc", "merchand", "parad", "pra", "prec",
        "prem", "prom", "rev", "superv", "surm", "surpr", "telev", "treat",
        # The `-ize` side, which is much shorter: an `-ize` word is nearly always
        # the suffix.
        "caps", "downs", "overs", "res", "ups",
    }
)

#: `-yses` is the one form both conventions spell identically — it is also the plural
#: of `-ysis`, so `analyses` is a noun as often as a verb and says nothing about which
#: convention the page uses. `analyzes` is not ambiguous and is left in.
AMBIGUOUS_YSES = ("ys", "es")


def spelling_variants(text: str) -> list[tuple[str, str]]:
    """Every alternating spelling in one line, as `(convention, the word as written)`.

    The convention is `-is-` or `-iz-`; which of them is *correct* is not this check's
    business, so nothing here knows about dialects. What is refused is the mixture.
    """
    found: list[tuple[str, str]] = []
    for match in SPELLING_VARIANT.finditer(text):
        stem, mark = match["stem"].lower(), match["mark"].lower()
        if stem in NOT_A_SUFFIX or match.group().lower().endswith("wise"):
            continue
        if (mark, match["tail"].lower()) == AMBIGUOUS_YSES:
            continue
        found.append(("-is-" if mark in ("is", "ys") else "-iz-", match.group()))
    return found


def check_lead_lengths(
    path: Path, leads: dict[str, str], vocabulary: Sequence[str] = ()
) -> None:
    """A lead against `LEAD_CHARS` — the length lint's twin for the entry arc's frame.

    A different budget from a Bullet's: the lead sits one list level shallower
    (docs/adr/0032-the-entry-arc.md §4).

    Its bold spans are charged at `LEAD_BOLD_PENALTY`, which is the second thing that
    makes this budget the lead's own rather than a borrowed one. A Bullet's ratio
    would have been derivable from `0046` §6 and is not what was measured; the lead's
    was taken at the lead's `\\linewidth`, off the widest bold span a lead carries
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).

    Charged, not counted — the same shape `check_summary_length` uses, and for the
    same reason: `len(text)` is what a person rewrites in, and the number they have to
    get under is the weighted one.
    """
    for slug, text in leads.items():
        spans = emphasis_spans(text, vocabulary, MAX_LEAD_KEYWORDS)
        charged = math.ceil(bold_equivalent_chars(text, spans, LEAD_BOLD_PENALTY))
        if charged > config.LEAD_CHARS:
            emphasis = (
                f", of which {sum(end - start for start, end in spans)} are set in "
                f"bold at {config.BOLD_LEAD_CHARS} to the line "
                f"({', '.join(f'`{text[start:end]}`' for start, end in spans)})"
                if spans
                else ""
            )
            raise RenderError(
                f"{path}: the lead for {slug} is {len(text)} characters{emphasis} and "
                f"its budget holds {config.LEAD_CHARS} — rephrase it "
                f"{charged - config.LEAD_CHARS} character(s) shorter: {text}"
            )


def check_summary_length(path: Path, summary: str, vocabulary: Sequence[str] = ()) -> None:
    """The Summary against `SUMMARY_CHARS` — the length lint's third twin.

    A third budget, because the Summary sits at TOP LEVEL, outside every itemize,
    and is therefore the widest prose on the page — wider than a lead, which is
    itself wider than a Bullet (docs/adr/0044-the-page-opens-on-a-summary.md §6).

    Its keyword spans are charged at `BOLD_PENALTY` like a Bullet's, and that needs
    no `BOLD_SUMMARY_CHARS` because the penalty is a ratio of two counts taken at the
    same width: what survives the division is the font's, not the column's
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §6).

    This one is a tape and not the gate. `SUMMARY_CHARS` bounds two typeset lines
    and a paragraph breaks at word boundaries, so it is measured conservatively and
    the real verdict comes from `check_summary_fit` after the compile — which reads
    the height TeX measured off the composed block, bold and all. Failing here first
    is a kindness: it names the number to write to, before pdflatex runs.
    """
    spans = emphasis_spans(summary, vocabulary, MAX_SUMMARY_KEYWORDS)
    charged = math.ceil(bold_equivalent_chars(summary, spans))
    if charged > config.SUMMARY_CHARS:
        bold = sum(end - start for start, end in spans)
        emphasis = (
            f" ({len(summary) - bold} of them plain, and "
            f"{bold} set in bold at "
            f"{config.BOLD_CHARS_PER_BULLET} to the line)"
            if spans
            else ""
        )
        raise RenderError(
            f"{path}: the Summary is {charged} characters{emphasis} and its budget holds "
            f"{config.SUMMARY_CHARS} — rephrase it "
            f"{charged - config.SUMMARY_CHARS} character(s) shorter. The page charges "
            f"{config.SUMMARY_LINES} line(s) for it and a third typeset line is a line of "
            f"evidence nobody granted: {summary}"
        )


def check_summary_figures(path: Path, summary: str) -> None:
    """No number appears in the Summary — the one place a figure has nothing to cite.

    NOT A STYLE RULE. Every other figure on this page is resolved against something:
    a Bullet's against the Claim it cites (`check_number_trace`), a lead's against
    its Entry's `## lead` block (`check_lead_trace`). The Summary cites nothing — it
    is one sentence about a whole career — so there is no stored value to trace a
    figure to and no provenance tier to render it at.

    Resolving one against *any* Claim in the bank instead would be a check that
    passes on `~95%` lifted off a translation benchmark and set at the top of the
    page as though it described the candidate. That is worse than no check, so the
    figures stay in the Bullets, where they trace
    (docs/adr/0044-the-page-opens-on-a-summary.md §4).
    """
    found = numbers(summary)
    if not found:
        return
    raise RenderError(
        f"{path}: the Summary renders `{found[0].raw}`, and the Summary carries no "
        f"figures. It cites no Claim, so there is nothing for a number here to trace "
        f"to and no provenance to render it at — every other figure on this page is "
        f"resolved against what its line cites. Say it without the number, or put it "
        f"on the Bullet or the lead that can back it"
        + (
            f" (also: {', '.join(number.raw for number in found[1:])})"
            if len(found) > 1
            else ""
        )
        + f": {summary}"
    )


def check_lead_trace(path: Path, leads: dict[str, str], entries: dict[str, bank.Entry]) -> None:
    """Every number in a lead traces to its `## lead` block, equal-or-softer.

    The lead is exempt from `0030`'s set checks (spread, opener) but bound by
    render.py's arithmetic exactly as a Bullet is — a figure that does not trace
    to `lead.number` fails the run, and an estimated aggregate may only render
    softened (docs/adr/0032-the-entry-arc.md §7).
    """
    for slug, text in leads.items():
        lead = entries[slug].lead
        sources = (stored_values(lead.number) if lead.number else []) + stored_values(
            lead.evidence
        )
        for rendered in numbers(text):
            matched = next((source for source in sources if traces_to(source, rendered)), None)
            if matched is None:
                raise RenderError(
                    f"{path}: the lead for {slug} renders `{rendered.raw}`, which is "
                    f"nowhere in {entries[slug].path}'s `## lead` block ({entries[slug].path}"
                    f":{lead.line}) — every number on the page traces to what it cites"
                )
            check_tier(path, f"the lead for {slug}", None, lead.provenance, matched, rendered)


def check_set(
    path: Path,
    bullets: list[Bullet],
    rows: list[SkillRow],
    widths: dict[str, int],
    leads: dict[str, str] | None = None,
    summary: str | None = None,
    supporting: list[SupportingRow] | None = None,
) -> None:
    """`bullets.md` read as one page's prose rather than as a column of lines.

    Three faults live only at this scale (docs/adr/0030-the-composed-set.md):

    - **the spread** — every line jammed against `CHARS_PER_BULLET`, which is a rubric
      being followed rather than these sentences needing that much room;
    - **a repeated opener** — the two on the run that motivated this were in *different*
      entries, which is why the rule is the page and not the block;
    - **two spellings of one convention.**

    None of them is a reading of the prose: a character count, a first-word comparison
    and a suffix match. Each either fires or it does not, and none can report that a
    line looks fine — which is what keeps `0010`'s refusal of a second judgement intact.
    """
    spread = measure_spread(bullets, widths)
    if spread.fires:
        raise RenderError(
            f"{path}: {spread.finding} — the page is written to the cap rather than "
            f"to what these sentences need. Say the thing and let some lines finish "
            f"early; a line that ends in 66 characters has not failed for being short"
        )

    seen: dict[str, list[Bullet]] = {}
    for bullet in bullets:
        word = opener(bullet.text)
        earlier = seen.setdefault(word, [])
        same_entry = next((b for b in earlier if b.entry == bullet.entry), None)
        if same_entry is not None:
            raise RenderError(
                f"{path}:{bullet.line}: {bullet.ref} opens on `{word}` and so does "
                f"{same_entry.ref} on line {same_entry.line}, in the same entry — a "
                f"reader meets them one under the other. Pick another verb for one"
            )
        if len(earlier) >= MAX_OPENER_USES:
            refs = ", ".join(b.ref for b in earlier)
            raise RenderError(
                f"{path}:{bullet.line}: {bullet.ref} would be Bullet number "
                f"{len(earlier) + 1} on the page to open on `{word}` (after "
                f"{refs}) — at most {MAX_OPENER_USES} to a page. Pick another verb"
            )
        earlier.append(bullet)
    conventions: dict[str, tuple[int, str]] = {}
    for line, text in page_prose(bullets, rows, leads, summary, supporting):
        for convention, word in spelling_variants(text):
            conventions.setdefault(convention, (line, word))
        if len(conventions) == 2:
            (one_line, one), (two_line, two) = conventions.values()
            raise RenderError(
                f"{path}: the page spells `{one}` (line {one_line}) and `{two}` "
                f"(line {two_line}) two different ways — one convention to a page. "
                f"Which one is yours; the mixture is the fault"
            )


def page_prose(
    bullets: list[Bullet],
    rows: list[SkillRow],
    leads: dict[str, str] | None = None,
    summary: str | None = None,
    supporting: list[SupportingRow] | None = None,
) -> list[tuple[int, str]]:
    """Every line of prose on the page, in file order, with its line number.

    The Skills rows are in it because they are prose the reader reads — `Data
    standardization` sat under a Bullet saying `generalised` on the run this comes
    from. They are NOT in the opener check: a row label is a noun lifted from the
    posting's own vocabulary under `0020` and has no opener problem. Leads are in
    it for the same reason as Skills rows — the spelling check was never
    Bullets-only, its scope is already *anywhere in bullets.md* — and are excluded
    from the spread and opener checks the same way, by never reaching `bullets`
    (docs/adr/0032-the-entry-arc.md §7).

    The Summary joins them on the same terms, and it is the line where a mixed
    convention would show worst: it is licensed to echo the posting's vocabulary
    (docs/adr/0044-the-page-opens-on-a-summary.md §2), and the posting is where a
    `-ize` spelling arrives from on a page that otherwise writes `-ise`. It is
    outside the spread and opener checks for the lead's reason — it is not a Bullet
    — and outside them harder: it is one line, so a spread over it is not a
    quantity, and it has no neighbours to repeat an opener with.
    """
    prose = [(bullet.line, bullet.text) for bullet in bullets]
    for row in rows:
        prose.append((row.line, row.label))
        prose.extend((skill.line, skill.name) for skill in row.skills)
    for text in (leads or {}).values():
        prose.append((0, text))
    if summary:
        prose.append((0, summary))
    # A supporting row's tail on the same terms as a lead: it is prose the reader
    # reads, so the spelling check reaches it, and it is not a Bullet, so the spread
    # and opener checks never see it. A bare row contributes nothing here — its every
    # word is the bank's frontmatter, which no run composed
    # (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §8).
    for row in supporting or []:
        if row.tail:
            prose.append((row.line, row.tail))
    return sorted(prose)


# --------------------------------------------------------------------------
# Step 5 — the Number-trace check, and its mirror
# --------------------------------------------------------------------------

#: A number as it appears in prose: an optional softening tilde, digits, and an
#: optional unit glued to them. The lookbehind keeps `p99`, `gp3`, `OAuth2` and `EC2`
#: out — a digit run welded to letters is an identifier, not a claim about magnitude.
#: A deliberate blind spot: the alternative fails a run for writing `p99`.
NUMBER = re.compile(
    r"(?<![A-Za-z0-9.])"
    r"(?P<soft>~\s*|[Oo]ver\s+|[Mm]ore than\s+|[Aa]t least\s+)?"
    r"(?P<value>\d+(?:,\d{3})*(?:\.\d+)?)"
    r"(?P<unit>%|[xX×]|[kKmMbB](?![A-Za-z]))?"
    r"(?P<plus>\+)?"
)

#: THE LOWER-BOUND FORMS ARE SOFTENING, and that is what `soft` and `plus` are doing
#: above. `~150` says *about* 150; `150+` and `over 150` say *at least* 150. Both are
#: claims no more precise than the estimate behind them, so both satisfy `check_tier`
#: — an `estimated` source may be written either way.
#:
#: IT WAS ADDED BECAUSE THE TILDE ALONE LOST A FACT. A real Claim's Evidence
#: says "over 150 KPIs"; the tilde was the only softened form, `~150` would have
#: misstated it, and a flat `150` is refused — so the denominator came off the page
#: entirely, on a run whose own rubric (`0039`) calls the denominator the FIRST thing
#: a Bullet should reach for. A softening vocabulary with no form for "more than"
#: makes some true facts unwritable.


@dataclass(frozen=True)
class Number:
    """One figure, as written — or, for a range's midpoint, as computed.

    `is_midpoint` marks a value this module derived from a stored `low--high`
    range rather than one the maker wrote: it renders softened always, whatever
    the Claim's tier (docs/adr/0033-a-range-collapses-to-its-midpoint.md §4).
    """

    raw: str
    value: Decimal
    unit: str
    softened: bool
    is_midpoint: bool = False


def numbers(text: str) -> list[Number]:
    """Every figure in a piece of prose, normalised enough to compare.

    Thousands separators go, `×` folds to `x`, and a unit is lower-cased — so `2X`
    and `2x` are one number while `40%` and `40` stay two, since a unit carries as
    much of the claim as the digits do.
    """
    found = []
    for match in NUMBER.finditer(text or ""):
        #: A BARE YEAR IS A DATE, NOT A FIGURE, and it is skipped here for exactly the
        #: reason `0046` §3 skips it when deriving emphasis. Until this line the two
        #: halves of this module disagreed about what a year is: `figure_spans` called
        #: `2026` a date and declined to bold it, while this call site called it an
        #: impact figure and demanded it render softened against an `estimated`
        #: source. `~2026` is not a thing anyone can write, so a year inside an
        #: estimated Claim could not be stated at all — it cost a real Claim
        #: its reporting year on a real run. One definition, one call site each.
        if is_year(match):
            continue
        unit = (match.group("unit") or "").lower().replace("×", "x")
        found.append(
            Number(
                raw=match.group(0).strip(),
                value=Decimal(match.group("value").replace(",", "")),
                unit=unit,
                softened=bool(match.group("soft") or match.group("plus")),
            )
        )
    return found


#: `digit--digit`, no surrounding whitespace — the bank's one syntactic test for a
#: range, measured off the bank rather than assumed (docs/adr/0033-a-range-collapses-to-its-midpoint.md
#: §2). A leading `~` binds to the WHOLE range, never to the first endpoint alone.
RANGE = re.compile(
    r"(?<![A-Za-z0-9.])(?P<soft>~\s*)?(?P<low>\d+(?:,\d{3})*(?:\.\d+)?)"
    r"--(?P<high>\d+(?:,\d{3})*(?:\.\d+)?)"
    r"(?P<unit>%|[xX×]|[kKmMbB](?![A-Za-z]))?"
)


def stored_values(text: str) -> list[Number]:
    """Every traceable value in STORED bank prose — a Claim's `number:` or Evidence,
    a lead's `number:` or Evidence, a merge's `number:` or Evidence.

    A range contributes exactly three traceable values — its two endpoints and
    their midpoint — never the interval (docs/adr/0033-a-range-collapses-to-its-midpoint.md
    §3). Ordinary figures outside any range are read the same way `numbers()` reads
    a rendered Bullet; this is the bank-side counterpart, and the two never see the
    same text — `numbers()` reads what was rendered, this reads what was stored.
    """
    text = text or ""
    values: list[Number] = []
    consumed: list[tuple[int, int]] = []
    for match in RANGE.finditer(text):
        consumed.append((match.start(), match.end()))
        soft = bool(match.group("soft"))
        unit = (match.group("unit") or "").lower().replace("×", "x")
        low = Decimal(match.group("low").replace(",", ""))
        high = Decimal(match.group("high").replace(",", ""))
        midpoint = (low + high) / 2
        values.append(Number(raw=str(low), value=low, unit=unit, softened=soft))
        values.append(Number(raw=str(high), value=high, unit=unit, softened=soft))
        values.append(
            Number(raw=f"~{midpoint}", value=midpoint, unit=unit, softened=True, is_midpoint=True)
        )
    for match in NUMBER.finditer(text):
        if any(start <= match.start() < end for start, end in consumed):
            continue
        unit = (match.group("unit") or "").lower().replace("×", "x")
        values.append(
            Number(
                raw=match.group(0).strip(),
                value=Decimal(match.group("value").replace(",", "")),
                unit=unit,
                softened=bool(match.group("soft")),
            )
        )
    return values


def check_no_range_on_page(path: Path, lines: list[tuple[int, str, str]]) -> None:
    """The page never carries a range — it collapses to one figure at compose time.

    `lines` is `(line number, ref-or-label, text)` for every Bullet and lead on
    the page. This is the rule `0033` §3 makes explicit: today a range fails only
    as an accidental side effect of the tier check, and a `measured` range would
    have sailed straight through.
    """
    for number, ref, text in lines:
        match = RANGE.search(text)
        if match:
            raise RenderError(
                f"{path}:{number}: {ref} renders `{match.group(0)}`, a range — a range "
                f"never reaches the page (docs/adr/0033-a-range-collapses-to-its-midpoint.md "
                f"§3). Collapse it to one figure; the midpoint is the rubric's default"
            )


def traces_to(stored: Number, rendered: Number) -> bool:
    """Does `rendered` say the same thing as `stored`, or a rounder version of it?

    A flat number must be exact. A softened one may round — "~" is the rounding
    convention on both tiers, and a Measured 39.98% legitimately shows as ~40% — so
    the stored value is rounded to the precision the Bullet actually wrote and
    compared there. `~45%` against 39.98% still fails: rounding to whole percent
    gives 40, not 45.
    """
    if stored.unit != rendered.unit:
        return False
    if not rendered.softened:
        return stored.value == rendered.value
    exponent = rendered.value.as_tuple().exponent
    places = -exponent if isinstance(exponent, int) and exponent < 0 else 0
    quantum = Decimal(1).scaleb(-places)
    return stored.value.quantize(quantum, rounding=ROUND_HALF_UP) == rendered.value


def check_tier(
    path: Path, where: str, line: int | None, claim_provenance: str | None,
    stored: Number | None, rendered: Number,
) -> None:
    """A figure that traces to an `estimated` source, or a range's midpoint, renders
    only softened.

    The tier governs the source, not one token inside it — see the original
    reasoning below. A midpoint is a further case `0033` §4 adds: a figure nobody
    measured, softened whatever the tier of the range it came from, because
    rounding two stated endpoints into one is arithmetic nobody vouched for.

    A `number:` line is prose and often carries more than one figure — `40% (2.5s
    to 1.5s)` is one estimate written three ways — and an estimated Claim's
    evidence normally restates and elaborates its own number, because that is
    where the estimate came from. Every one of those figures is the same estimate,
    so every one of them costs a `~`; governing only the first would leave the
    rest as a way round the tier.
    """
    if rendered.softened:
        return
    location = f"{path}:{line}" if line is not None else str(path)
    if stored is not None and stored.is_midpoint:
        raise RenderError(
            f"{location}: {where} renders `{rendered.raw}` flat, and it is a range's "
            f"midpoint — a midpoint is a figure nobody measured and may only render "
            f"softened (`~{rendered.raw}`), whatever the tier of the range it came from "
            f"(docs/adr/0033-a-range-collapses-to-its-midpoint.md §4)"
        )
    if claim_provenance != "estimated":
        return
    raise RenderError(
        f"{location}: {where} renders `{rendered.raw}` flat, but its source is "
        f"estimated — every figure that traces to an estimated source may only render "
        f"softened (`~{rendered.raw}`). Render may spend a source's truth down, never up"
    )


def check_number_trace(path: Path, bullets: list[Bullet], entries: dict[str, bank.Entry]) -> None:
    """Every number on the page traces to what it cites, equal-or-softer.

    Three ways a Bullet fails, which are the three ways a résumé lies about a figure:
    the number is not in its source at all; the source is `estimated` (or the figure
    is a range's midpoint) and the Bullet renders it flat — a silent upgrade,
    undetectable once shipped; or the source is qualitative and the Bullet grew a
    number.

    A single-claim Bullet's source is that Claim's stored `number:` and its prose —
    a figure written only in Evidence still traces, since it is a fact the maker
    stated at ingestion. A merged Bullet's source widens to ANY cited Claim, or the
    group's stored `## merge` sum (docs/adr/0034-a-merged-bullet-coordinates.md §8)
    — the sum discharges arithmetic no check can verify, so it is a traceable value
    in its own right, not a claim to re-derive.
    """
    for bullet in bullets:
        claims = [
            resolve_claim(entries, bullet.entry, claim_id, f"{path}:{bullet.line}")
            for claim_id in bullet.claim_ids
        ]
        sources: list[Number] = []
        for claim in claims:
            sources += stored_values(claim.number) if claim.number else []
            sources += stored_values(claim.prose)
        provenance_by_value: dict[tuple, str | None] = {}
        for claim in claims:
            for value in (stored_values(claim.number) if claim.number else []) + stored_values(
                claim.prose
            ):
                provenance_by_value.setdefault((value.value, value.unit), claim.provenance)
        merge = None
        if bullet.merged:
            merge = entries[bullet.entry].merge(bullet.claim_ids)
            if merge is not None:
                merge_values = stored_values(merge.number)
                sources += merge_values
                for value in merge_values:
                    provenance_by_value.setdefault((value.value, value.unit), merge.provenance)

        for rendered in numbers(bullet.text):
            matched = next((stored for stored in sources if traces_to(stored, rendered)), None)
            if matched is not None:
                provenance = provenance_by_value.get((matched.value, matched.unit))
                check_tier(path, bullet.ref, bullet.line, provenance, matched, rendered)
                continue
            raise RenderError(
                f"{path}:{bullet.line}: {bullet.ref} renders `{rendered.raw}`, which is "
                f"nowhere in {'the claims it cites' if len(claims) > 1 else 'the Claim'} "
                f"({entries[bullet.entry].path})"
                + (f" or their stored merge sum" if merge is not None else "")
                + ". Every number on the page traces to what it cites; rephrase the "
                f"Bullet without it, or dig the figure out first"
            )


def check_number_kept(
    path: Path,
    bullets: list[Bullet],
    entries: dict[str, bank.Entry],
    recorded: set[str],
) -> None:
    """A source's stored figure is the last thing its Bullet gives up, not the first.

    The mirror of `check_number_trace`, and the same arithmetic run the other way:
    that one fails a figure that traces to nothing, this one fails a figure that
    traced to something and then vanished. A stored `number:` is the most defensible
    fact a Claim owns — the only one with a `provenance:` tier behind it — and it was
    the one fact composition could drop for free
    (`docs/adr/0029-when-a-number-may-leave.md`).

    **A merge group's stored sum discharges its constituents**
    (`docs/adr/0034-a-merged-bullet-coordinates.md` §8): a Bullet citing a group with
    a stored `## merge` sum owes the page that ONE figure, not every member's own —
    `~8 hours a month` *is* the receipt for `c1`'s, `c4`'s and `c3`'s numbers, and
    demanding all three back would be undeliverable. A merge group with **no** stored
    sum falls back to the ordinary rule, per cited Claim.

    The escape is `checkpoint.md`'s **Decided by rule** section naming the ref: a drop
    is a compose-time judgement, so it costs a sentence in an existing file rather
    than a Fork and a halt.

    Two things this does not do, both of them consequences of it being arithmetic.
    It cannot see *which* figure stayed, so a Bullet that dropped its outcome number
    and kept a scope one passes — what governs that is the rubric. And a `number:`
    carrying no figure at all ("half the fleet") does not arm it, since there is
    nothing for the Bullet to keep; the same blind spot `check_number_trace` names.
    """
    for bullet in bullets:
        rendered = numbers(bullet.text)
        if rendered or bullet.ref in recorded:
            continue
        if bullet.merged:
            merge = entries[bullet.entry].merge(bullet.claim_ids)
            if merge is not None:
                raise RenderError(
                    f"{path}:{bullet.line}: {bullet.ref} renders no figure, and its group's "
                    f"stored `## merge {merge.ref}` sum is `number: {merge.number}` "
                    f"({entries[bullet.entry].path}:{merge.line}). The sum discharges its "
                    f"constituents' own figures — it is the last thing a merged Bullet "
                    f"gives up, not the first"
                )
            owed = [
                claim_id
                for claim_id in bullet.claim_ids
                if (claim := resolve_claim(entries, bullet.entry, claim_id, f"{path}:{bullet.line}"))
                and claim.number
                and stored_values(claim.number)
            ]
            if owed:
                raise RenderError(
                    f"{path}:{bullet.line}: {bullet.ref} renders no figure, and "
                    f"{', '.join(f'{bullet.entry}/{claim_id}' for claim_id in owed)} store "
                    f"a `number:` with no group sum to discharge it — write at least one "
                    f"back in, or record the drop as a `Decided by rule` line in "
                    f"checkpoint.md"
                )
            continue
        claim = resolve_claim(entries, bullet.entry, bullet.claim_ids[0], f"{path}:{bullet.line}")
        if not claim.number or not stored_values(claim.number):
            continue
        raise RenderError(
            f"{path}:{bullet.line}: {bullet.ref} renders no figure, and its Claim stores "
            f"`number: {claim.number}` ({entries[bullet.entry].path}:{claim.line}). The "
            f"number is the last thing a Bullet gives up, not the first — write it back "
            f"into the line and cut something else, or record the drop as a `Decided by "
            f"rule` line in checkpoint.md naming {bullet.ref} and which ground it stood "
            f"on: a Checkpoint `soften` answer, or Evidence that undercuts the figure for "
            f"this JD"
        )


def check_skills_trace(path: Path, skills: list[Skill], entries: dict[str, bank.Entry]) -> None:
    """Every listed skill appears in the `skills:` line of the Claim it cites.

    The Skills rows draw from any Claim in the bank, including ones whose Entry
    lost the page — which is exactly why they need the same lint as a Bullet. It is
    the cheapest route to claiming a skill nothing backs.

    Case is already outside what this constrains, on both sides, which is what lets
    a run normalise a skill's case without touching its identity: the bank owns
    whether `Google BigQuery` and `BigQuery` are the same skill, and compose time
    may not answer that question (`docs/adr/0020-skills-section.md` §3).
    """
    for skill in skills:
        claim = resolve_claim(entries, skill.entry, skill.claim_id, f"{path}:{skill.line}")
        carried = {name.strip().lower() for name in claim.skills}
        if skill.name.strip().lower() not in carried:
            raise RenderError(
                f"{path}:{skill.line}: the Skills line claims `{skill.name}` against "
                f"{skill.ref}, whose `skills:` line reads "
                f"`{', '.join(claim.skills) or '(none)'}` — cite a Claim that carries it"
            )


# --------------------------------------------------------------------------
# Step 6 — emphasis, escape, and fill
# --------------------------------------------------------------------------


#: Words that never begin a unit, so a figure's span stops before them. Without
#: this, `~60 of a new diagnostics scorecard's ~150 KPIs` would bold `~60 of a new`:
#: the extension is looking for the noun that makes a bare figure mean something
#: (`~8 hours`, `~150 KPIs`, `~2,100 lines`), and a preposition or an article says
#: there is no such noun here (docs/adr/0043-the-number-carries-the-emphasis.md §1).
UNIT_STOPWORDS = frozenset(
    {
        "a", "an", "the", "of", "in", "on", "to", "for", "and", "or", "with",
        "from", "by", "at", "into", "across", "over", "per", "that", "which",
        # Words that end in `s` and are not plural nouns, so PLURAL_UNIT's shape
        # alone would take them: `from 4 as the lead`, `to 3 this quarter`.
        "as", "is", "was", "has", "does", "this", "its", "his", "thus", "plus",
        "less", "unless", "us", "yes", "whereas", "always", "perhaps",
    }
)

#: One plain alphabetic word. No digits and no punctuation: a unit is a word, and
#: anything else ends the span.
UNIT_WORD = re.compile(r"[A-Za-z]+")

#: A word shaped like a plural count noun — three letters or more ending in `s`, not
#: `ss` (`process`, `class`). Crude on purpose: it only decides how far a bold span
#: reaches, never what is claimed.
PLURAL_UNIT = re.compile(r"[A-Za-z]+[A-Za-rt-z]s|[A-Z]{2,}s")

#: The cadence `~8 hours a month` / `~5 hours per cycle` — the one place a stopword
#: may sit INSIDE the span, because the rate is the unit. Matched only after a unit
#: noun has already been taken, never on its own.
RATE_TAIL = re.compile(r"\s+(?:a|per)\s+[A-Za-z]+")

#: The window a bare four-digit integer is read as a YEAR in rather than as a
#: quantity, and therefore never bolded. Deliberately narrow: `2,100 lines` carries a
#: separator, `~2100` carries the softening tilde, `2100 accounts` carries a unit
#: noun — all three stay figures. What is left is a bare `2024` sitting in prose,
#: which on a résumé is a date and not an outcome
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §3).
YEAR_WINDOW = range(1900, 2100)

#: Below this many characters, a keyword match is not a match of anything. `R` is a
#: real Qualification on a real posting and is inside `Rewrote`; `AI` is
#: inside half the page's nouns and all of its own compounds. The guard is arithmetic
#: rather than a judgement about what the term means, and it is the same number
#: `coverage.py` refuses to count under, for the same reason
#: (docs/adr/0041-the-page-is-read-back-against-the-posting.md §5).
MIN_KEYWORD_CHARS = 3

#: How many keyword spans one Bullet may carry, and how many the Summary may. Figures
#: are uncapped and these are not, because the two run away differently: a Bullet is
#: one Claim and carries two or three figures at the outside, while a posting brings
#: thirty-four terms and would bold a sentence into a second body font. THESE ARE
#: JUDGEMENTS, NOT MEASUREMENTS, in the family of `SPREAD_MIN_BULLETS` and the
#: Template's `\hfuzz` — a reading of what a page looks like to a person. The Summary
#: gets one more because it is two typeset lines rather than one, and because
#: `0044` §4 leaves it carrying no figures at all, so three is its whole bold budget
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §5).
#:
#: ALL THREE ARE ZERO NOW, and the machinery stays because a version still needs the
#: keyword pass to be recognised as a version. Bolding a posting's terms inside prose
#: read, on a real page, as random words in a heavier weight — `reporting`,
#: `computer science`, `prompt design` — which is the opposite of what a recruiter's
#: six-second scan needs. The figures are the one thing worth finding at a glance, and
#: they stay bold (docs/adr/0057-the-page-reads-like-a-resume.md §4).
MAX_BULLET_KEYWORDS = 0
MAX_SUMMARY_KEYWORDS = 0

#: And the lead's, which is a Bullet's. One typeset line carrying one or two facts is
#: the same shape a Bullet is, so the number that keeps a body font on a Bullet keeps
#: one on a lead. It is a NAME OF ITS OWN rather than a reuse of `MAX_BULLET_KEYWORDS`
#: because `0046` §5's table is per element, and because the lead is the one element
#: with an argument for spending less than a Bullet: `0032` made it the entry's frame,
#: and a frame that competes with what it frames is the failure mode to watch. Moving
#: it to 1 is a one-line change here and no change anywhere else
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).
MAX_LEAD_KEYWORDS = 0

#: One `- ` item, wherever it sits in the file. The shape `terms.md` and
#: `bank/vocabulary.md` share, and `coverage.py` reads `terms.md` through this same
#: function so the two tools can never disagree about what a term is.
LIST_ITEM = re.compile(r"^\s*-\s+(?P<item>.+?)\s*$")


def read_if_present(path: Path) -> str:
    """A file's text, or `""` where there is no file. Never an error.

    The two vocabulary sources this reads are both optional, and the failure mode of
    treating a missing one as fatal is a run refused over typography — which is the
    opposite of what emphasis is worth.
    """
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def listed_items(text: str) -> list[str]:
    """Every `- ` item in a Markdown file, in file order, duplicates dropped.

    Matched loosely, and headings are ignored: these are files a person writes by
    hand, and the `## Must-have` / `## Nice-to-have` split in `terms.md` says what
    the maker does about a gap, which is never a question about typography.
    """
    found: list[str] = []
    for line in text.splitlines():
        match = LIST_ITEM.match(line)
        if match and match["item"] and match["item"] not in found:
            found.append(match["item"])
    return found


def keyword_vocabulary(
    entries: dict[str, bank.Entry],
    declared: str = "",
    posting: str = "",
) -> tuple[str, ...]:
    """Every term the keyword pass recognises, longest first.

    Since `0057` §4 every `MAX_*_KEYWORDS` is 0, so none of these is set in bold; the
    pass runs so that a version (`Python 3.11`) inside a term is read as part of the
    name and not as a figure. What follows is the rule for when the caps are raised.

    Three sources, all of them **literal lists a person wrote**, and no fourth. The
    whole design rests on emphasis being unable to introduce content, so what this
    returns is only ever a filter over words already composed onto the page —
    a term nothing says is a term nothing bolds
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §4):

    - **the bank's `skills:` names**, every Claim in the bank. Free coverage and
      already curated: `bankcheck.py` validates them and `check_skills_trace` will
      not let one onto a Skills row without a Claim behind it.
    - **`bank/vocabulary.md`**, optional — the technical names the maker's prose uses
      that are not the name of a skill. `Custom GPT configuration` is a skill;
      `GPT` is what the sentence says. This file exists so that need never presses
      on the bank's evidence fields, which answer a different question.
    - **`terms.md`**, the posting's own terms, lifted verbatim at `tailor` §2. This
      is the JD-match half of the rule, and it emphasises the maker's existing words
      rather than supplying one — the distinction `0044` §2 already drew for the
      Summary.

    Longest first is not cosmetic: `Google BigQuery` and `BigQuery` are both terms,
    and matching the longer one first is what stops the page bolding `BigQuery`
    inside a span it already set.
    """
    terms: list[str] = []
    for entry in entries.values():
        for claim in entry.claims:
            terms += list(claim.skills or [])
    terms += listed_items(declared)
    terms += listed_items(posting)

    seen: set[str] = set()
    kept: list[str] = []
    for term in terms:
        term = " ".join(term.split())
        if len(term) < MIN_KEYWORD_CHARS or term.casefold() in seen:
            continue
        seen.add(term.casefold())
        kept.append(term)
    return tuple(sorted(kept, key=lambda term: (-len(term), term.casefold())))


def keyword_pattern(term: str) -> re.Pattern[str]:
    r"""`term` as a whole-word, whitespace-tolerant, case-insensitive matcher.

    `\b` is not enough here, and the two ways it is not are both real:

    - **A HYPHEN, AN UNDERSCORE.** `\b` would let `automation` bold half of
      `automation-first`. Bolding a fragment of a compound is the one way this rule
      can make the page look broken rather than merely over-emphasised.
    - **A DOT, A SLASH, AN `@`.** A URL is not prose. `grafana` is a declared term
      and `https://grafana.internal.example.com/d/A7F3C9B2` is a link a Bullet may
      legally carry, and `\b` bolds four characters out of the middle of it. So a
      term is rejected where a dot, a slash or an `@` runs into it on the left, or
      where a dot glued to a word character follows it on the right — which is what
      being *inside* a dotted name looks like from either end.

    The trailing dot is admitted where a word character does not follow it, because
    that is a full stop and `Next.js` is a term that ends a sentence.
    """
    return re.compile(
        r"(?<![A-Za-z0-9\-._/@])"
        + r"\s+".join(re.escape(word) for word in term.split())
        + r"(?![A-Za-z0-9\-_]|\.\w)",
        re.IGNORECASE,
    )


def keyword_spans(
    text: str, vocabulary: Sequence[str], cap: int | None = None
) -> list[tuple[int, int]]:
    """Where `text` says something the vocabulary declares, in reading order.

    Longest term first, and a match that overlaps one already taken is dropped — so
    `Google BigQuery` wins over `BigQuery` and the two never nest. `cap` keeps the
    leftmost N, because reading order is the only order this module can defend
    without making a judgement about which of the maker's own words matters more.
    """
    taken: list[tuple[int, int]] = []
    for term in vocabulary:
        for match in keyword_pattern(term).finditer(text):
            span = match.span()
            if not any(span[0] < end and start < span[1] for start, end in taken):
                taken.append(span)
    taken.sort()
    return taken if cap is None else taken[:cap]


def is_year(match: re.Match[str]) -> bool:
    """A bare four-digit integer inside `YEAR_WINDOW` — a date, not an outcome.

    All four conditions have to hold. A softening tilde, a unit, a thousands
    separator or a decimal point each say the maker wrote a quantity: `~2,100 lines`
    is a count of lines of prose and could be the page's biggest number
    to lose. What is refused is `2024` standing on its own
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §3).
    """
    value = match.group("value")
    return (
        not match.group("soft")
        and not match.group("unit")
        and value.isdigit()
        and len(value) == 4
        and int(value) in YEAR_WINDOW
    )


def figure_spans(text: str, keywords: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    """Every IMPACT figure in `text`, each grown over the noun that gives it meaning.

    **Every one, not one of them.** This is where `0046` parts from `0043`: a
    reader scanning for what the work was worth should find all of it, and the
    figures are the only thing on the line that is *already mechanically proved*.
    `check_number_trace` has resolved every one of them against the cited Claim's
    stored value at equal-or-softer provenance before this runs, so the set this
    returns is by construction prose the run has already checked — which is why no
    Claim is read here and none needs to be
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §2).

    Two figures are not impact and are skipped: a **year** (`is_year`), and a
    **version**, which is a figure sitting immediately after a vocabulary term —
    the `3.11` of `Python 3.11` names a release of the thing before it and makes no
    claim about magnitude. That test needs no second list: a version follows a
    technical name, and a technical name is exactly what `keywords` already found.
    """
    ends_a_keyword = {end for _, end in keywords}
    spans: list[tuple[int, int]] = []
    for match in NUMBER.finditer(text):
        start, end = match.span()
        if is_year(match):
            continue
        if start >= 1 and text[start - 1] == " " and start - 1 in ends_a_keyword:
            continue
        # A percentage or a multiplier already carries its unit, so the word after it
        # is the rest of the sentence: `~95% came out usable` bolds `~95%`, never
        # `~95% came`.
        unit = (match.group("unit") or "").lower()
        carries_unit = unit in ("%", "x", "×")
        spans.append((start, end if carries_unit else extend_over_unit(text, end)))
    return spans


def extend_over_unit(text: str, end: int) -> int:
    """Grow a figure's span rightward over the noun that gives it meaning.

    `~150` alone is a quantity of nothing; `~150 KPIs` is the claim. So the span
    takes ONE following word, and only where that word is a plain alphabetic token
    that is not a stopword — then the `a month` / `per cycle` rate tail if the
    sentence has one.

    It never crosses punctuation, because punctuation ends the quantity: in
    `~150 KPIs, automating the heaviest` the comma is where the figure stops being
    the figure. Returning `end` unchanged is the normal outcome for a figure that
    carries its own unit (`~85%`, `~2x`).
    """
    word = UNIT_WORD.match(text, end + 1) if text[end : end + 1] == " " else None
    if word is None or word.group().lower() in UNIT_STOPWORDS:
        return end
    # A count's noun is plural — `34 services`, `200 sources`, `~4.5 hours`, `150+ KPIs`.
    # The word after a figure that is NOT is nearly always an adjective standing in front
    # of the real noun, and bolding it reads as a mistake: `~12 internal services`,
    # `8 polling integrations` (docs/adr/0057-the-page-reads-like-a-resume.md §4).
    if not PLURAL_UNIT.fullmatch(word.group()):
        return end
    end = word.end()
    rate = RATE_TAIL.match(text, end)
    return rate.end() if rate else end


def emphasis_spans(
    text: str, vocabulary: Sequence[str], keyword_cap: int = MAX_BULLET_KEYWORDS
) -> list[tuple[int, int]]:
    """Every span of one line the page sets in bold, in reading order, never nesting.

    A pure function of the prose and the declared vocabulary — it reads no Claim,
    which is the simplification `0046` buys by bolding every figure instead of
    choosing one. `0043` needed the Claim only to decide **which** figure argued it.

    The order the three passes run in is the rule:

    1. the keywords, **uncapped**, so a figure can see the name in front of it;
    2. the figures, skipping years and versions;
    3. the keywords again, dropping any that a figure span swallowed, then capped.

    A keyword inside a figure's unit noun — `3 Python scripts`, where
    `extend_over_unit` already took `Python` — is dropped rather than nested: it is
    bold either way, and two macros around one word is a bug waiting to be read as a
    heavier weight.
    """
    found = keyword_spans(text, vocabulary)
    figures = figure_spans(text, found)
    keywords = [
        span
        for span in found
        if not any(span[0] < end and start < span[1] for start, end in figures)
    ][:keyword_cap]
    return sorted(figures + keywords)


def emphasised_latex(text: str, spans: Sequence[tuple[int, int]]) -> str:
    """One line's LaTeX: escaped prose with a `\\resumeEmph{...}` around each span.

    **Split first, escape the parts, then wrap.** Escaping is per-character and
    context-free, so escaping the slices and joining them is identical to escaping
    the whole string — while matching a span in the ESCAPED text would mean matching
    `$\\sim$8 hours a month` and re-deriving offsets that `escape_latex` moved. This
    way the spans are chosen in the maker's prose, where the offsets mean something,
    and `\\resumeEmph` is the only thing added after.

    The macro name is written here rather than escaped through, which is the ONE
    piece of LaTeX this module emits into a hole. It is a constant in this file, never
    anything a run composed, so `0007`'s rule holds: emphasis is the Template's, and
    nothing Opus writes can reach pdfTeX as markup.
    """
    if not spans:
        return escape_latex(text)
    if sum(end - start for start, end in spans) == len(text):
        # A fully bold line is not emphasis. Nothing composes this today — every span
        # starts at a digit or a declared term and the caps bound the rest — so it is
        # a guard against a later rule change, and it fails loudly rather than
        # typesetting the whole line bold.
        raise RenderError(
            "the emphasis spans cover the entire line, which is not emphasis — this "
            f"is a bug in emphasis_spans, not in the prose: {text}"
        )
    out: list[str] = []
    cursor = 0
    for start, end in spans:
        out.append(escape_latex(text[cursor:start]))
        out.append(r"\resumeEmph{" + escape_latex(text[start:end]) + "}")
        cursor = end
    out.append(escape_latex(text[cursor:]))
    return "".join(out)


LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    # The softening tilde of an Estimated number, and the one entry here chosen off
    # a compiled page rather than from the LaTeX manual. `\textasciitilde{}` is
    # correct and typesets, in this template's OT1 Computer Modern, as a RAISED
    # glyph up at cap height — a floating accent where the page means "about". So
    # does `[T1]{fontenc}`, measured, which is why the expensive fix was not taken.
    # `$\sim$` sits mid-x, and its Rel-atom spacing is 0.00pt here because
    # substitution is per character and a lone atom has no neighbour to be spaced
    # against (`docs/adr/0022-softening-tilde.md`).
    "~": r"$\sim$",
    "^": r"\textasciicircum{}",
}
ESCAPABLE = re.compile("|".join(re.escape(character) for character in LATEX_ESCAPES))


def escape_latex(text: str) -> str:
    """`& % $ # _ { } ~ ^ \\` made harmless, mechanically, on every hole.

    Opus writes plain prose and never LaTeX, so nothing it writes can break a
    compile or smuggle in formatting. Emphasis lives in the Template, never in the
    data (`docs/adr/0007-rendering-approach.md`).

    **One pass**, not ten `str.replace` calls in sequence. A sequential pass has to
    do the backslash first, and then every later rule chews on the escapes it just
    wrote: a lone `\\` becomes `\\textbackslash{}`, whose braces the `{` and `}`
    rules then escape into `\\textbackslash\\{\\}`. That still compiles, which is
    what makes it worth guarding — it would print the wrong characters quietly.
    """
    return ESCAPABLE.sub(lambda match: LATEX_ESCAPES[match.group()], text)


def jinja_env():
    r"""Jinja2 with LaTeX-safe delimiters — `\VAR{}`, `\BLOCK{}`, `\#{}`.

    Jinja's own `{{ }}` and `{% %}` collide with LaTeX's braces and percent, which
    is why they are all replaced. `autoescape=False` because the escaping here is
    LaTeX's, done above; `StrictUndefined` so a renamed hole fails loudly instead of
    rendering an empty header.
    """
    try:
        import jinja2
    except ImportError:
        raise RenderError(
            "Jinja2 is not installed for this Python. Run "
            "`.venv/bin/pip install -r requirements.txt` and call render.py with "
            "`.venv/bin/python`"
        ) from None

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        undefined=jinja2.StrictUndefined,
    )


def fill_template(contents: PageContents) -> str:
    """The Template, rendered **whole**. Nothing here parses or splices a `.tex`.

    Entry headers come from the bank's frontmatter and the order from the
    allocation, so the page order is the Packer's and the wording is the maker's.

    The Entry `slug` and each Bullet's `ref` ride along unescaped, because they
    reach nothing but the Overflow check's marker comments — a slug and a claim id
    are `[A-Za-z0-9._-]` by construction, and a LaTeX comment is never typeset.
    """
    by_entry: dict[str, list[dict[str, str]]] = {}
    for bullet in contents.bullets:
        by_entry.setdefault(bullet.entry, []).append(
            {
                "ref": bullet.ref,
                "text": emphasised_latex(
                    bullet.text, emphasis_spans(bullet.text, contents.vocabulary)
                ),
            }
        )

    context_entries = [
        {
            "slug": place.slug,
            "type": entry.type,
            "title": escape_latex(entry.title),
            "org": escape_latex(entry.org),
            "location": escape_latex(entry.location),
            "stack": escape_latex(entry.stack),
            "link": escape_latex(entry.link),
            # Raw for the \href target; bank.py refused anything a raw target
            # cannot carry.
            "link_url": entry.link,
            # BUILT, not copied: `display_dates` composes one house format from the
            # entry's validated `started`/`ended`, so no two Entry headers on the page
            # can be written in two shapes
            # (docs/adr/0031-the-entry-header-is-built.md §2).
            "dates": escape_latex(entry.display_dates),
            # The lead carries emphasis on the same mechanical rules a Bullet does —
            # every impact figure, and `MAX_LEAD_KEYWORDS` (now 0) declared terms — and
            # is charged for it against `config.BOLD_LEAD_CHARS`
            # (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).
            "lead": emphasised_latex(
                contents.leads[place.slug],
                emphasis_spans(
                    contents.leads[place.slug], contents.vocabulary, MAX_LEAD_KEYWORDS
                ),
            )
            if place.slug in contents.leads
            else None,
            "bullets": by_entry.get(place.slug, []),
        }
        for place, entry in contents.blocks
    ]

    # Grouped into sections here rather than in the Template, for the reason the
    # Template gives for splitting `entries` there: routing is a shape decision and
    # belongs where it can be read. The order is `pack.SUPPORTING_SECTIONS`, which is
    # the Packer's own page order, so the grouping restates nothing it decided.
    supporting_sections = []
    for section in pack.SUPPORTING_SECTIONS:
        rows = [
            {
                "slug": place.slug,
                "label": escape_latex(entry.title),
                "text": escape_latex(supporting_row_text(row, entry)),
            }
            for place, row, entry in contents.supporting_blocks
            if place.section == section
        ]
        if rows:
            supporting_sections.append(
                {
                    "name": section,
                    "heading": escape_latex(pack.SECTION_HEADINGS[section]),
                    "rows": rows,
                }
            )

    return jinja_env().get_template(TEMPLATE_NAME).render(
        profile=contents.profile.context(),
        education_first=contents.profile.education_first(),
        # The Summary is the one element outside the Bullets that carries emphasis,
        # and it carries only keywords: `0044` §4 leaves it with no figures to bold.
        # It is also the element the posting is licensed to lend words to, so it is
        # where a JD term most often has something to emphasise
        # (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §5).
        summary=emphasised_latex(
            contents.summary,
            emphasis_spans(contents.summary, contents.vocabulary, MAX_SUMMARY_KEYWORDS),
        ),
        entries=context_entries,
        skill_rows=[
            {"label": escape_latex(row.label), "text": escape_latex(row.text)}
            for row in contents.skill_rows
        ],
        supporting_sections=supporting_sections,
    )


# --------------------------------------------------------------------------
# Steps 7 to 10 — compile, then the two post-compile checks and the page count
# --------------------------------------------------------------------------

#: What a previous run left behind, deleted before compiling so the PDF is a function
#: of `resume.tex` alone. A fresh build and a rebuild over stale files are not
#: byte-identical — pdfTeX's first pass over a document with no `.out` writes bookmarks
#: it only embeds on the second — but two passes from a clean state are.
BUILD_ARTEFACTS = (".aux", ".out", ".log")
PASSES = 2

PAGE_COUNT = re.compile(r"Output written on .*?\((?P<pages>\d+) pages?")


def compile_pdf(run_dir: Path, tex_path: Path) -> str:
    """`pdflatex` in the run folder, twice, from clean. Returns the log.

    The previous `resume.pdf` goes too, so a failed compile cannot leave last run's
    page sitting beside this run's `.tex`.
    """
    for suffix in (*BUILD_ARTEFACTS, ".pdf"):
        tex_path.with_suffix(suffix).unlink(missing_ok=True)
    if shutil.which("pdflatex") is None:
        raise RenderError(
            "pdflatex is not on PATH. Install TinyTeX (https://yihui.org/tinytex/) or "
            "TeX Live, then `tlmgr install titlesec marvosym enumitem fancyhdr preprint "
            "babel-english` — see the README's Requirements"
        )

    for _ in range(PASSES):
        proc = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-output-directory={run_dir}",
                str(tex_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(run_dir),
            # SOURCE_DATE_EPOCH pinned, and the template carries no \today: between
            # them, and \pdfinfoomitdate / \pdftrailerid in the preamble, the same
            # input yields the same bytes.
            env={
                "SOURCE_DATE_EPOCH": "0",
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
            },
        )
        if proc.returncode != 0:
            raise RenderError(
                f"pdflatex failed on {tex_path}. Its own last words:\n"
                + "\n".join(proc.stdout.splitlines()[-25:])
                + f"\n\nThe full log is {tex_path.with_suffix('.log')}"
            )
    return tex_path.with_suffix(".log").read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# Step 9 — the Overflow check
# --------------------------------------------------------------------------

#: pdfTeX's own words for content that ran past the right margin. No threshold and no
#: arithmetic on the points: `\hfuzz` in the Template decides which of these are
#: printed at all, so this fails on anything TeX still reports and quotes the amount
#: back rather than comparing it. Ask TeX, do not model TeX.
#:
#: `Overfull \vbox` is deliberately not matched: a vertical overflow is a height
#: failure, which is the page-count assert's business.
OVERFULL = re.compile(r"^Overfull \\hbox \((?P<points>[0-9.]+)pt too wide\).*$", re.M)

#: Where the report says it happened, indexing into `resume.tex`. Two forms:
#: `at lines 287--292` for a paragraph or an alignment, `at line 287` for a box TeX
#: built on its own. The first line of the range is what attributes the report,
#: since a paragraph runs on past the element that started it.
AT_LINE = re.compile(r"at lines (?P<first>\d+)--\d+|at line (?P<only>\d+)")

#: What the Template writes above every element that can overflow, on a line of its
#: own: `%% AUTOAPPLY:element:<kind>:<id>`.
ELEMENT_MARKER = re.compile(r"^%% AUTOAPPLY:element:(?P<key>[a-z]+:\S+)\s*$")

#: The header-fit instrumentation's own brackets. What sits between them is measured
#: and never shipped, and it reports overfull boxes of its own; the shipped header
#: keeps its marker, so ignoring this region stops the same content being reported
#: twice.
INSTRUMENTATION_BEGIN = "%% BEGIN header-fit instrumentation"
INSTRUMENTATION_END = "%% END header-fit instrumentation"


@dataclass(frozen=True)
class Element:
    """One thing on the page that can overflow, and where the maker fixes it."""

    #: How the failure names it, in the Template's own terms.
    what: str
    #: The imperative half of the message, naming the file to open.
    fix: str
    #: The content, quoted back. Newlines for an element that typesets two rows.
    text: str


def page_elements(contents: PageContents) -> dict[str, Element]:
    """Every marker the Template emits, keyed `<kind>:<id>`, with its source file.

    TeX reports a line number in `resume.tex`, which the Renderer wrote itself and
    overwrites next run, so quoting one points the maker at the wrong artifact. What
    they have to edit is a Bank entry, `bank/profile.md`, or `bullets.md`, and this is
    the table that says which. A Bullet sends them to `bullets.md`: the prose that
    overflowed is composed prose, so the fix is a rephrase.

    One table, deliberately, rather than the profile's rows hanging off `Profile` and
    an Entry's off `bank.Entry` — it has to stay true to the *Template's* set of
    markers, which is only checkable while it is written out in one place.
    `check_overflow` checks it, key for key.

    The accepted cost is a coupling: this knows the Template's structure, which
    nothing else in render.py does. The Template emits, the Renderer reads.
    """
    profile, bullets_path = contents.profile, contents.bullets_path
    found: dict[str, Element] = {
        "profile:header": Element(
            what="the Static profile header",
            fix=f"shorten a field in {profile.path}",
            text="\n".join(profile.header_text().values()),
        ),
        # `page` rather than a slug: there is exactly one Summary and it belongs to
        # no Entry. It can only reach here on one unbreakable token — the paragraph
        # wraps for everything else, which is `check_summary_fit`'s business.
        "summary:page": Element(
            what="the Summary",
            fix=f"rephrase it in {bullets_path}, under `## Summary` — it is inside "
            f"SUMMARY_CHARS, so what runs over is one token too long to break",
            text=contents.summary,
        ),
    }
    # The Template drops the whole Skills section when there are no rows, markers
    # and all — so these are the rows that are conditional, and on the same thing.
    #
    # The marker is the row NUMBER and the message is the row LABEL, which is the
    # split the Template's marker block explains: a label is run-authored text and
    # has no business inside a LaTeX comment, but it is what the maker recognises.
    for index, row in enumerate(contents.skill_rows, start=1):
        found[f"skills:{index}"] = Element(
            what=f"the {row.label} skills row",
            fix=f"drop the skills the JD leans on least, in {bullets_path}:{row.line}",
            text=f"{row.label}: {row.text}",
        )
    for place, entry in contents.blocks:
        found[f"entry:{place.slug}"] = Element(
            what=f"the Entry header for {place.slug}",
            # `dates` is not on that list: it is built from `started`/`ended` and is
            # the same width for every entry on the page, so it is never the thing to
            # shorten (docs/adr/0031-the-entry-header-is-built.md §2).
            # A project's header is one row — name, stack, link, dates (0057 §3).
            fix=(
                f"shorten `title`, `stack` or `link` in {entry.path}"
                if entry.type == "project"
                else f"shorten `title`, `org` or `location` in {entry.path}"
            ),
            text=(
                " | ".join(part for part in (entry.title, entry.stack, entry.link) if part)
                + f" … {entry.display_dates}"
                if entry.type == "project"
                else f"{entry.title} … {entry.display_dates}\n{entry.org} … {entry.location}"
            ),
        )
        if place.slug in contents.leads:
            found[f"lead:{place.slug}"] = Element(
                what=f"the lead for {place.slug}",
                fix=f"rephrase it in {bullets_path}, under `## {place.slug}` — it is inside "
                f"LEAD_CHARS, so what runs over is one token too long to break",
                text=contents.leads[place.slug],
            )
    for bullet in contents.bullets:
        found[f"bullet:{bullet.ref}"] = Element(
            what=f"the Bullet for {bullet.ref}",
            fix=f"rephrase it in {bullets_path}:{bullet.line} — it is inside "
            f"CHARS_PER_BULLET, so what runs over is one token too long to break",
            text=bullet.text,
        )
    # Keyed by SLUG rather than by row number, unlike the Skills rows above: a
    # supporting row's identity is a Bank entry slug, which is `[A-Za-z0-9._-]` by
    # construction and is exactly the file the maker has to go and edit.
    for place, row, entry in contents.supporting_blocks:
        found[f"supporting:{place.slug}"] = Element(
            what=f"the {pack.SECTION_HEADINGS[place.section]} row for {place.slug}",
            fix=(
                f"shorten the tail in {bullets_path}:{row.line}"
                if row.tail
                else f"shorten `title` or `org` in {entry.path}"
            ),
            text=f"{entry.title} {supporting_row_text(row, entry)}",
        )
    for index, row in enumerate(profile.education, start=1):
        found[f"education:{index}"] = Element(
            what=f"Education row {index}",
            fix=f"shorten `institution`, `location`, `degree` or `dates` in {profile.path}",
            text=f"{row['institution']} … {row['location']}\n{row['degree']} … {row['dates']}",
        )
    return found


def read_element_markers(tex: str) -> tuple[list[tuple[int, str]], list[tuple[int, int]]]:
    """`resume.tex` -> (its markers in page order, the line ranges to ignore).

    Both are read out of the generated file rather than predicted from the context,
    because it is the generated file the log's line numbers index into.
    """
    markers: list[tuple[int, str]] = []
    ignored: list[tuple[int, int]] = []
    begin: int | None = None
    for number, line in enumerate(tex.splitlines(), start=1):
        stripped = line.strip()
        match = ELEMENT_MARKER.match(stripped)
        if match:
            markers.append((number, match.group("key")))
        elif stripped == INSTRUMENTATION_BEGIN:
            begin = number
        elif stripped == INSTRUMENTATION_END and begin is not None:
            ignored.append((begin, number))
            begin = None
    return markers, ignored


def overfull_line(report: str) -> int | None:
    """The `resume.tex` line an overfull report points at, if it names one at all.

    It may not: a box overflowing while the output routine is active is reported
    with no line number, and there is nothing to attribute it to.
    """
    match = AT_LINE.search(report)
    if not match:
        return None
    return int(match.group("first") or match.group("only"))


def check_overflow(tex_path: Path, log: str, elements: dict[str, Element]) -> None:
    r"""Nothing on the page runs past the right margin — the Header-fit check's twin.

    Where the Header-fit check guards the one element whose over-width failure is
    silent, everything here is the opposite: `\resumeSubheading`,
    `\resumeEducationRow` and a Bullet holding one unbreakable token all overflow
    rather than wrap, so they cost the page no height and the page-count assert never
    fires — but LaTeX warns about every one, and `pdflatex` exits 0 anyway.

    So this measures nothing and judges no width. The threshold is `\hfuzz`, set once
    in the Template, and the check reduces to: did the log mention an overfull box in
    a shipped part of the document.

    A missing marker is a hard failure, checked up front rather than only when
    something overflows. It has to be: a report is attributed to the nearest marker
    *above* it, so an element that lost its marker is not unnamed — it is named as the
    element before it, and sends the maker to the wrong file.

    It runs after the Header-fit check and before the page-count assert by convention,
    not because the order is load-bearing: an overflow leaves the page height
    untouched. Failures the maker fixes in their own data come first.
    """
    markers, ignored = read_element_markers(tex_path.read_text(encoding="utf-8"))
    check_markers_account_for(tex_path, [key for _, key in markers], elements)

    offenders: dict[str, str] = {}
    unattributed: list[str] = []

    for match in OVERFULL.finditer(log):
        report = match.group(0).strip()
        line = overfull_line(report)
        if line is not None and any(first <= line <= last for first, last in ignored):
            continue
        key = attribute(line, markers)
        element = elements.get(key) if key else None
        if element is None:
            unattributed.append(report)
            continue
        offenders.setdefault(
            key,
            f"  {element.what} is {match.group('points')}pt too wide — {element.fix}:\n"
            + "\n".join(f"    {row}" for row in element.text.splitlines()),
        )

    if unattributed:
        raise RenderError(
            f"{tex_path.with_suffix('.log')} reports an overfull box that nothing on "
            f"the page accounts for:\n  " + "\n  ".join(unattributed) + "\n\n"
            f"Every element that can overflow carries an `AUTOAPPLY:element:` marker "
            f"above it, and this names the file to edit from the nearest one above the "
            f"reported line. A report that sits above the first marker, or that names "
            f"no line at all — pdfTeX writes one with no line number when the overflow "
            f"happens while the output routine is active — has nothing to be attributed "
            f"to. That is a hard failure rather than a message quoting a line number in "
            f"a generated file the next run overwrites"
        )
    if not offenders:
        return
    raise RenderError(
        f"{tex_path.with_suffix('.pdf')}: content runs past the right margin.\n"
        + "\n".join(offenders.values())
        + f"\n\nAn overfull box costs the page no height, so the PDF is still one page "
        f"and pdflatex still exits 0 — this is a purely visual defect on a document "
        f"whose whole purpose is to be read. The threshold is \\hfuzz in "
        f"templates/resume.tex.j2 and TeX applies it, so anything reported here is "
        f"wide enough to see"
    )


def check_markers_account_for(
    tex_path: Path, emitted: list[str], elements: dict[str, Element]
) -> None:
    """The Template's markers and `page_elements` name the same set of things.

    Both directions matter, and neither is the obvious one. A marker the Renderer
    cannot name would report an overflow against a `<kind>:<id>` the maker has never
    heard of; an element with no marker would hand its reports to whichever element
    is nearest above it, naming the wrong file with no sign anything went wrong.

    So it is checked once per run, on the way past, rather than on the failure path
    — the same standing the Header-fit check gives its own markers, and for the same
    reason: a résumé whose overflow could not be attributed does not ship.
    """
    unknown = sorted(set(emitted) - elements.keys())
    unmarked = sorted(elements.keys() - set(emitted))
    if not unknown and not unmarked:
        return
    raise RenderError(
        f"{tex_path} and the Overflow check disagree about what is on the page: "
        + "; ".join(
            part
            for part in (
                f"the Template marks {', '.join(unknown)}, which tools/render.py "
                f"cannot name" if unknown else "",
                f"tools/render.py expects a marker for {', '.join(unmarked)} and the "
                f"Template writes none" if unmarked else "",
            )
            if part
        )
        + ". An overflow is attributed to the nearest marker above it, so a set that "
        "has drifted does not fail to name the offender — it names the wrong one"
    )


def attribute(line: int | None, markers: list[tuple[int, str]]) -> str | None:
    """The marker key nearest above `line`, which is the element that produced it."""
    if line is None:
        return None
    key = None
    for number, found in markers:
        if number > line:
            break
        key = found
    return key


# --------------------------------------------------------------------------
# Step 10 — the page-count assert
# --------------------------------------------------------------------------


def assert_one_page(log: str, pdf_path: Path, bullets: list[Bullet]) -> None:
    """One page, or the run fails — a lint, never a render-trim loop.

    Every Bullet already passed the length lint **and the Header-fit check cleared
    the header**, so reaching page two is not a long sentence and not a wrapped
    header: it is the **Page-budget constants** promising lines the page does not
    have. That is a template-level recalibration event, and the message says so
    rather than sending the maker to shorten prose that is already inside budget.
    The ordering is what earns that message the right to be so certain.
    """
    match = PAGE_COUNT.search(log)
    if not match:
        raise RenderError(f"could not read a page count out of {pdf_path.with_suffix('.log')}")
    pages = int(match.group("pages"))
    if pages > 1:
        raise RenderError(
            f"{pdf_path} came out {pages} pages, and one page is the whole point. Every one "
            f"of the {len(bullets)} Bullets passed the length lint, so this is not prose "
            f"running long — the Page-budget constants in tools/config.py are miscalibrated "
            f"against templates/resume.tex.j2. Re-run the procedure in docs/calibration.md, "
            f"commit the new numbers on their own, and re-run pack.py: the allocation this "
            f"run was built from is over-budget too"
        )


# --------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------


def render(run_dir: Path) -> Path:
    """The ten steps, in order. Returns the path of the PDF it wrote.

    The run folder is resolved to an absolute path first and used absolute
    throughout. `pdflatex` is run with the run folder as its working directory, so a
    relative `runs/<jd-slug>` — which is exactly how the maker types it — would be
    resolved a second time against that directory and vanish.
    """
    run_dir = run_dir.resolve()
    repo = run_dir.parent.parent
    bank_dir = repo / "bank"
    bullets_path = run_dir / "bullets.md"
    allocation_path = run_dir / "allocation.md"
    for path in (bullets_path, allocation_path):
        if not path.is_file():
            raise RenderError(f"no {path.name} in {run_dir}")
    if not bank_dir.is_dir():
        raise RenderError(
            f"no bank at {bank_dir} — the bank sits beside runs/, so a run folder is "
            f"<repo>/runs/<jd-slug>/"
        )

    profile = Profile.load(bank_dir / "profile.md")            # 1
    profile.check_education_charge(parse_allocation_education(allocation_path))
    entries = bank.load_bank(bank_dir)
    for entry in entries.values():
        for key in entry.unknown_keys:
            note(f"{entry.path}: frontmatter carries `{key}`, which nothing reads")
        for claim in entry.claims:
            for key in claim.unknown_keys:
                note(f"{entry.path}: {claim.ref} carries `{key}`, which nothing reads")

    bullets, skill_rows, leads, summary, supporting = parse_bullets(bullets_path)
    # Both files are optional and neither is an error when absent: a bank with no
    # `vocabulary.md` still renders on the skills names alone, and a run scored
    # before `terms.md` existed still renders with no JD-match emphasis at all. What
    # a missing file costs is bold, never a page
    # (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §4).
    vocabulary = keyword_vocabulary(
        entries,
        read_if_present(bank_dir / "vocabulary.md"),
        read_if_present(run_dir / "terms.md"),
    )
    contents = PageContents(
        profile=profile,
        placed=parse_allocation(allocation_path),
        allocated_skill_rows=parse_allocation_skills(allocation_path),
        bullets=bullets,
        skill_rows=skill_rows,
        leads=leads,
        summary=summary,
        entries=entries,
        bullets_path=bullets_path,
        placed_supporting=parse_supporting(allocation_path),
        supporting=supporting,
        vocabulary=vocabulary,
    )
    check_structure(contents)                                             # 2

    check_lengths(bullets_path, bullets, skill_rows,                      # 3
                  contents.granted_widths, vocabulary)
    check_lead_lengths(bullets_path, leads, vocabulary)
    check_summary_length(bullets_path, summary, vocabulary)
    check_supporting_lengths(contents)
    check_set(bullets_path, bullets, skill_rows,                          # 4
              contents.granted_widths, leads, summary, supporting)
    check_no_range_on_page(
        bullets_path,
        [(bullet.line, bullet.ref, bullet.text) for bullet in bullets]
        + [(0, f"the lead for {slug}", text) for slug, text in leads.items()]
        + [(row.line, row.ref, row.tail) for row in supporting if row.tail],
    )
    check_number_trace(bullets_path, bullets, entries)                    # 5
    # The tails, on the same check and unchanged: a supporting row's prose is bound
    # by Downgrade-only exactly as a Bullet's is
    # (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §8).
    check_number_trace(bullets_path, contents.supporting_tails, entries)
    check_lead_trace(bullets_path, leads, entries)
    check_summary_figures(bullets_path, summary)
    check_number_kept(bullets_path, bullets, entries,
                      parse_decided_by_rule(run_dir / "checkpoint.md"))
    check_skills_trace(bullets_path, contents.skills, entries)

    tex_path = run_dir / "resume.tex"                                     # 6
    tex_path.write_text(fill_template(contents), encoding="utf-8")

    log = compile_pdf(run_dir, tex_path)                                  # 7
    profile.check_header_fit(log)                                         # 8
    check_summary_fit(bullets_path, log, summary)
    check_overflow(tex_path, log, page_elements(contents))                # 9
    pdf_path = run_dir / "resume.pdf"
    assert_one_page(log, pdf_path, bullets)                               # 10

    print(
        f"render.py: {len(contents.placed)} entries, {len(bullets)} bullets, "
        f"{len(contents.skills)} skills in {len(skill_rows)} rows"
        + (f", {len(supporting)} supporting row(s)" if supporting else "")
        + f" -> {pdf_path}"
    )
    return pdf_path


def note(message: str) -> None:
    """Something the maker may want to know that is not a reason to stop.

    Unknown keys reach the page this way: `bank.py` surfaces them rather than
    dropping them, and the bank is hand-edited, so a key this build has not heard of
    is the maker's business — but a silently ignored `provenence:` typo would be a
    number rendering flat forever.
    """
    print(f"render.py: note: {message}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/render.py runs/<jd-slug>", file=sys.stderr)
        return 2
    run_dir = Path(argv[1])
    if not run_dir.is_dir():
        print(f"render.py: no run folder at {run_dir}", file=sys.stderr)
        return 1
    try:
        render(run_dir)
    except (RenderError, bank.BankError) as error:
        print(f"render.py: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
