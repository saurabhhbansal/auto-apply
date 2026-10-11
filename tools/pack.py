#!/usr/bin/env python3
"""The Packer — Score table in, Allocation out.

    python tools/pack.py runs/<jd-slug>                      pass one
    python tools/pack.py runs/<jd-slug> --skills-rows 1,2,1,1   pass two

Reads `runs/<jd-slug>/scores.md` and writes `runs/<jd-slug>/allocation.md`.

IT RUNS TWICE, and the Skills rows are composed in between. Pass one reserves four
single-line rows, because the page budget has to exist before anyone can compose
against it. Pass two is handed the rows' real typeset line counts and settles up —
in whichever direction the composition landed, which is why the second pass is a
*reconcile* rather than the hand-back it was charted as
(`docs/adr/0021-skills-row-cost.md` §4). Only the second pass's output may be
rendered; `render.py` refuses a reservation.

`--skills-rows` is one integer per composed row, its typeset line count, and an
empty value means the section was dropped. It is an argument rather than a second
file on purpose: the Packer still reads exactly one file, which is what keeps it
bank-blind and on the arithmetic side of the seam. What it receives is Opus's
judgement — which skills went into which row — already reduced to arithmetic.

All the arithmetic of tailoring lives here, and only arithmetic: the skill judges what
is relevant and writes the scores; this owns what fits. It never reads the bank —
everything it needs travels in the Score table — which is enforced by importing
nothing but the standard library and `config.py`.

What it writes, since `render.py` parses it and the `tailor` skill reads it aloud:

    # Allocation: <run folder>
    ... the budget, and how much of it went out ...
    Skills: ...              <- what the Skills section was charged, and whether
                                this is the reservation or the composed section

    ## Placed                 <- in page order: Experience, then Projects
    ### <entry> — <type> — ended <ended> — entry score <s> — N bullets
    - <entry>/c<n> — <score> — <1 line|2 lines> — <the reason Opus wrote>

    ## Silent calls           <- every call made by rule rather than by score:
    - tie: ... / shrink: ... / page full: ...
    - Opener: ...             <- which unit opens each placed entry, and where it
                                 sat by score before it was moved
    - Share: ...              <- how the lines were shared out, every run
    - Room: ...               <- what the seating left, which slots were granted a
                                 second line out of it, and what stayed unspent —
                                 every run

    ## Did not place          <- the Omission view, cut by structure not by score
    ### Entries
    - <entry> — entry score <s> — <how it lost> — best claim <entry>/c<n> (<score>) — <reason>
    ### Claims
    - <entry>/c<n> — <score> — <how it lost> — <reason>
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402  (tools/ is not a package; this is the page-budget block)


COLUMNS = ["entry", "claim", "type", "ended", "score", "width", "reason"]
LEADS_COLUMNS = ["entry", "lead"]
MERGES_COLUMNS = ["entry", "claims", "width", "reason"]
OPENERS_COLUMNS = ["entry", "unit"]
SECTIONS_COLUMNS = ["section", "entry", "ended", "signal", "reason"]

#: The supporting sections, in the order the page prints them and the order the
#: residue fill offers them in — one order, because there is no reason for two
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §5, §7).
#:
#: RESTATED HERE, NOT IMPORTED. `bank.SECTION_OF_TYPE` maps an Entry type to one of
#: these names, and the Packer may import nothing but the stdlib and `config` — the
#: same seam that makes it restate the month pattern. `tests/test_pack.py` holds the
#: two copies equal.
SUPPORTING_SECTIONS = ("certifications", "responsibilities", "extracurriculars")

#: What each section is called on the page and in the allocation's prose. The one
#: name here that is not the section's own is `responsibilities`: a résumé section
#: headed *Responsibilities* reads as a job description of the role being applied to,
#: which is the opposite of what the section says.
SECTION_HEADINGS = {
    "certifications": "Certifications",
    "responsibilities": "Positions of Responsibility",
    "extracurriculars": "Extracurriculars",
}

#: `c1+c3+c4` — 2 or 3 `+`-joined claim ids, the same grammar `bank.py` and
#: `render.py` use for a merged citation (docs/adr/0034-a-merged-bullet-coordinates.md).
#: Restated here rather than imported: the Packer may import nothing but the
#: stdlib and `config`.
MERGE_IDS = re.compile(r"^c[1-9][0-9]*(?:\+c[1-9][0-9]*){1,2}$")

# --------------------------------------------------------------------------
# The selection knobs
#
# These three decide which evidence reaches the page, so changing any of them is a
# selection event and belongs in a commit of its own. They are not in config.py
# because that holds only numbers measured against the template; these are
# decisions, and no measurement can check them.
# --------------------------------------------------------------------------

#: The absolute cut-off below which a Claim never takes a Bullet slot, even when
#: slots are free. What makes "a soft cap of ~6, never padded to a quota"
#: mechanical rather than a request the model is trusted to honour. It stayed at
#: 0.50 when the cap rose to six: the floor asks *is this worth showing at all* and
#: the page budget asks *is there room*, and making one number answer both is the
#: overloading that came off MAX_BULLETS (docs/adr/0024-ranking-window.md §4).
BULLET_FLOOR = Fraction(50, 100)

#: The tie band. Any Entry score gap below this is a tie, not an ordering — an
#: LLM float is stable in its first decimal and noisy in its second, and without
#: the band that noise silently reorders the résumé between runs.
EPSILON = Fraction(5, 100)

#: The soft cap on an Entry's Bullets — how many slots one block may hold, and
#: nothing else. It does NOT set the Entry score's ranking window, which stays at
#: three qualifying claims and is a literal in `Entry.score`
#: (docs/adr/0024-ranking-window.md §1, §3).
#:
#: SINCE `0048` IT IS THE CANDIDATE WINDOW AND NOT THE CAP THAT BINDS. What limits
#: an Entry's depth is MAX_BULLET_LINES below. This number can no longer bind on its
#: own: every unit costs at least one line, so an Entry that has run out of lines has
#: already run out of units. It stays because `Entry.slots` is the window the
#: distribution pass ranks inside, and because the Omission view names it.
MAX_BULLETS = 6

#: The soft cap on an Entry's Bullets, IN LINES — the number `0026` was actually
#: computing with, given a name (docs/adr/0048-the-depth-cap-is-a-line-budget.md).
#:
#: `0026` §1 sized the page as *"32 − 2n lines for Bullets, and a cap of 6 wants
#: 6n"*. That `6n` is 6 UNITS costing 6 LINES — an identity that held because a
#: Bullet was one line and a second was bought later out of the residue. `0047` §3
#: made the width a charge, so six units want up to twelve lines, the crossing point
#: `0026` put at four entries moved to two, and greedy top-first — which that ADR
#: chose on a page with five spare lines — began starving every Entry below the
#: first.
#:
#: IT IS DELIBERATELY THE SAME NUMBER AS MAX_BULLETS, and that is the whole claim to
#: being a repair rather than a new policy: on a page of `width: 1` Bullets the two
#: caps bind identically and the allocation is byte-identical to `0026`'s. What it
#: changes is only the page `0047` created, where an Entry of dense two-line claims
#: now shows three Bullets rather than eating twelve lines of a one-page résumé.
MAX_BULLET_LINES = 6

#: How many Entries of each kind the page may carry. THE TWO KNOBS THE MAKER TURNS —
#: everything else in this block is calibration or a decided rule
#: (docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md).
#:
#: DEFAULTS HERE, OVERRIDABLE ON THE COMMAND LINE, and `allocation.md` records what
#: it packed under. That is the same shape `--skills-rows` already has: a flag that
#: materially changes the allocation, whose value is derived from committed files and
#: written into the artifact, so a replay reproduces it and material determinism
#: survives. What would break determinism is a value nothing records.
#:
#: 3 AND 2 RATHER THAN 3 AND 3. Six Entries at a full block each want far more lines
#: than the page has, so a sixth would place as a header and one Bullet — a stub that
#: says less than it costs. Five ceilings on a page that seats about four means the
#: caps bind rarely and the page budget stays the thing that decides.
MAX_EXPERIENCE = 3
MAX_PROJECTS = 2

#: The claim-ref grammar, restated here rather than imported: `bank.py` owns the
#: definition, but the Packer may import nothing but the stdlib and `config`.
#: Widening the alphabet is therefore a two-file edit.
CLAIM_ID = re.compile(r"^c[1-9][0-9]*$")
ENTRY_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

#: The end date, restated from `bank.ENDED_PATTERN` for the same reason as the two
#: above. The bank owns the shape now — the column here is a COPY of the Entry's own
#: `ended` field rather than a judgement, and `render.py` fails a run where the two
#: disagree (docs/adr/0031-the-entry-header-is-built.md §3, §4). Changing it is a
#: two-file edit, and `tests/test_bank.py` fails if only one of the two moves.
ENDED = re.compile(r"^(?:present|[0-9]{4}-(?:0[1-9]|1[0-2]))$")
SCORE = re.compile(r"^[0-9]\.[0-9]{2}$")

#: A Bullet's declared width, in typeset lines. THE SCHEMA IS THE CAP: a `3` is
#: refused at parse rather than clamped, which is where `MAX_ROW_LINES` puts the
#: equivalent line for Skills rows (docs/adr/0025-bullet-wrap-cost.md §3). It is a
#: charge, not a want, since `0047` §3 — `pack_page` seats the unit at exactly this
#: many lines or leapfrogs it. It was a want `grant_widths` paid for out of the
#: residue until then.
WIDTH = re.compile(r"^[12]$")

#: What `ended: present` counts as when entries are ordered by recency: a date
#: above every real one, so "still there" always reads as the most recent.
PRESENT_KEY = "9999-99"


class ScoreTableError(Exception):
    """A malformed Score table. Always names the offending row."""


# --------------------------------------------------------------------------
# The Score table
# --------------------------------------------------------------------------


class Claim:
    """One row of the Score table: Opus's judgement about one Claim, and why.

    The score is an exact rational rather than a float, because the tie band has
    to treat a gap of exactly 0.05 as *outside* it and in binary 0.85 - 0.80 lands
    a hair under. Nothing else here would notice, and that one case is the band's
    boundary — the place it is most likely to be wrong and least likely to be seen.
    """

    def __init__(
        self,
        entry: str,
        claim_id: str,
        type_: str,
        ended: str,
        score: Fraction,
        width: int,
        reason: str,
        row: int,
    ):
        self.entry = entry
        self.id = claim_id
        self.type = type_
        self.ended = ended
        self.score = score
        #: The width Opus WANTS, judged on the claim's substance at scoring time.
        #: What the slot is actually charged is the Packer's grant, which lives on
        #: the Placement — a declared want is not a granted line.
        self.width = width
        self.reason = reason
        self.row = row

    @property
    def ref(self) -> str:
        return f"{self.entry}/{self.id}"

    @property
    def order_key(self) -> tuple:
        """Best first: score descending, then claim id ascending."""
        return (-self.score, int(self.id[1:]))


@dataclass
class MergeGroup:
    """One row of `## Merges` — a declared want, judged before any word is composed.

    `width` is what the group is charged at the reservation phase — `0034` §3's
    *reserved, not wanted*. Since `0047` §3 that is true of every unit, merged or
    not, so this is no longer the exceptional case it was written as.
    """

    entry: str
    claim_ids: tuple[str, ...]
    width: int
    reason: str
    row: int


@dataclass
class Unit:
    """One thing that can occupy a Bullet slot — a single Claim, or a merge group.

    The cap counts these, not Claims (`docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md`
    §6): `Entry.slots` is `min(MAX_BULLETS, len(units))`. `score` orders it — a
    Claim's own, or a merge group's maximum member (`0034` §2) — and `width` is
    what it is charged, for a Claim exactly as for a merge group since `0047` §3; a
    merge group's is committed at the reservation phase and never renegotiated.
    """

    entry: str
    claim_ids: tuple[str, ...]
    score: Fraction
    width: int
    reason: str
    merge: bool

    @property
    def ref(self) -> str:
        return f"{self.entry}/{'+'.join(self.claim_ids)}"

    @property
    def order_key(self) -> tuple:
        return (-self.score, int(self.claim_ids[0][1:]))


class Entry:
    """One Bank entry as the Score table describes it — the block that competes."""

    def __init__(self, slug: str, type_: str, ended: str):
        self.slug = slug
        self.type = type_
        self.ended = ended
        self.claims: list[Claim] = []
        #: Set from the `## Leads` table after every row is parsed (`0035` §2).
        self.lead: bool = False
        self.merge_groups: list[MergeGroup] = []
        #: The unit declared to open this Entry's block, as a tuple of claim ids —
        #: `("c1", "c3", "c4")` for a merge group, `("c3",)` for a single Claim.
        #: `None` where `scores.md` carries no `## Openers` table at all, and only
        #: then: `check_openers` refuses a table that skips a placed Entry
        #: (docs/adr/0040-fit-orders-the-page-force-orders-the-block.md §3).
        self.opener: tuple[str, ...] | None = None

    def claim_by_id(self, claim_id: str) -> Claim:
        return next(claim for claim in self.claims if claim.id == claim_id)

    @property
    def header_lines(self) -> int:
        """What this Entry's header costs before its first Bullet, lead included.

        A job's header is two rows — title and dates, then employer and location. A
        project's is ONE: name, stack and link beside the dates, because a personal
        project has no employer or office to fill a second row with
        (docs/adr/0057-the-page-reads-like-a-resume.md §3).
        """
        header = (
            config.PROJECT_HEADER_LINES if self.type == "project" else config.ENTRY_HEADER_LINES
        )
        return header + (config.LEAD_LINES if self.lead else 0)

    @property
    def ordered_claims(self) -> list[Claim]:
        return sorted(self.claims, key=lambda claim: claim.order_key)

    @property
    def qualifying_claims(self) -> list[Claim]:
        """Best first, and only the claims that could actually take a Bullet slot."""
        return [claim for claim in self.ordered_claims if claim.score >= BULLET_FLOOR]

    @property
    def units(self) -> list[Unit]:
        """Best first: every qualifying unmerged Claim, plus every merge group.

        A merge group's members do not individually have to clear the Bullet
        floor — the group's worth is a judgement made at scoring time
        (`docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md` §2), not a
        threshold — but an unmerged Claim below the floor still never takes a
        slot on its own.
        """
        merged_ids = {claim_id for group in self.merge_groups for claim_id in group.claim_ids}
        individual = [
            Unit(self.slug, (claim.id,), claim.score, claim.width, claim.reason, merge=False)
            for claim in self.ordered_claims
            if claim.id not in merged_ids and claim.score >= BULLET_FLOOR
        ]
        merges = [
            Unit(
                self.slug,
                group.claim_ids,
                max(self.claim_by_id(claim_id).score for claim_id in group.claim_ids),
                group.width,
                group.reason,
                merge=True,
            )
            for group in self.merge_groups
        ]
        return sorted(individual + merges, key=lambda unit: unit.order_key)

    @property
    def ordered_units(self) -> list[Unit]:
        """PRINT ORDER: the declared opener first, everything else in score order.

        `units` above is score order and is the **selection** surface — `slots`
        counts it, `pack_page` reserves and distributes out of it, and the Omission
        view reads positions off it. This is the same list read for a different
        question, and the two are separate because **fit and force are different
        quantities and one ordering was serving both**
        (docs/adr/0040-fit-orders-the-page-force-orders-the-block.md §2).

        The pre-pass is stable: exactly one unit moves, to index 0, and every other
        unit holds the score order it already had. Nothing here can change WHICH
        units place — this list is applied to the set `pack_page` already chose,
        after it has chosen it, which is what makes *selection stays exactly as it
        is* a property of the code rather than an intention. Applying it earlier
        would seat the units in a different order, and on a page whose last line
        runs out mid-entry a different order drops a different unit.
        """
        units = self.units
        if self.opener is None:
            return units
        declared = [unit for unit in units if unit.claim_ids == self.opener]
        return declared + [unit for unit in units if unit.claim_ids != self.opener]

    @property
    def score(self) -> Fraction:
        """The mean of the top 3 claim scores AT OR ABOVE THE BULLET FLOOR.

        The 3 IS NOT `MAX_BULLETS` and does not follow it to six. An entry is
        **ranked on its best evidence and gets its width from its depth**: peak
        quality decides the queue, `slots` decides how wide the block gets, and the
        two are separate questions. A mean over six would be the entry's *average*
        quality instead, and on a bank where most entries have fewer than six
        qualifying claims that flips an incentive — adding an honest mid-scoring
        claim would DEMOTE the entry that owns it, on a system whose other half
        exists to add claims.

        It stays a literal here rather than joining the selection knobs above: this
        method is the only reader, and the 3 is what *Entry score* MEANS. Turning it
        redefines the metric rather than tuning it, and parking it beside the floor
        and the tie band would advertise a dial that is not one
        (docs/adr/0024-ranking-window.md §1-§3).

        An entry with fewer than 3 qualifying claims averages what it has: padding
        with phantom zeros would rank an entry on claims it never wrote, and reading
        down past the floor would rank it on claims that can never render.

        AN ENTRY WITH NO QUALIFYING CLAIM falls back to the top 3 of what it has.
        Such an entry can never place, so this number is only ever printed — in the
        Omission view's Entry line — and it still orders correctly, since a mean of
        sub-floor claims is always below a mean of qualifying ones. The ADRs do not
        settle this case; the alternative was leaving the score undefined for an
        entry the Omission view has to print a score for.
        """
        window = self.qualifying_claims[:3] or self.ordered_claims[:3]
        top = [claim.score for claim in window]
        return sum(top) / len(top)

    @property
    def slots(self) -> int:
        """`min(6, units)` — the cap counts units, not claims
        (`docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md` §6). Free page
        space never promotes a below-floor claim to a unit of its own."""
        return min(MAX_BULLETS, len(self.units))

    @property
    def tie_break(self) -> tuple[int, str]:
        """The fixed rule for a tie: recency descending, then entry id ascending.

        `ended` becomes a negated YYYYMM so that "most recent" sorts first, and
        `present` outranks every real date.
        """
        ended = PRESENT_KEY if self.ended == "present" else self.ended
        return (-int(ended.replace("-", "")), self.slug)


@dataclass
class Placement:
    """An Entry that made the page, and the units that got its Bullet slots.

    `widths` runs parallel to `units` and holds what each slot was CHARGED — which
    since `0047` §3 is simply the unit's own declared width, merged or not. It used
    to be what a slot was GRANTED: a non-merge unit started at one line and
    `grant_widths` raised it out of whatever the evidence left over, deliberately
    NOT read off `Claim.width`, which was a want (docs/adr/0025-bullet-wrap-cost.md
    §6, now inverted by that ADR's Addendum). A merge unit's width was already
    committed at the reservation phase and is unchanged
    (docs/adr/0034-a-merged-bullet-coordinates.md §3) — the two cases have simply
    converged.
    """

    entry: Entry
    units: list[Unit]
    widths: list[int] = field(default_factory=list)
    #: Units inside the candidate window that the ENTRY's own line budget refused,
    #: as distinct from the ones the PAGE could not afford. Carried so the Omission
    #: view can tell a maker which of the two happened, because the repairs differ:
    #: a page that ran out means the bank has outgrown it, and an Entry at its depth
    #: cap means this one block is deeper than a one-page résumé will show
    #: (docs/adr/0048-the-depth-cap-is-a-line-budget.md §3).
    depth_capped: list[Unit] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.widths:
            self.widths = [unit.width for unit in self.units]

    @property
    def lines(self) -> int:
        return self.entry.header_lines + sum(self.widths)


def unescape(cell: str) -> str:
    return cell.replace(r"\|", "|")


def split_row(line: str) -> list[str]:
    """Cells of a markdown table row, honouring `\\|` as an escaped pipe."""
    body = line.strip()
    cells = re.split(r"(?<!\\)\|", body)
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def is_delimiter(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def parse_scores(text: str) -> list[Claim]:
    """Every row of the Score table, in file order. Raises on anything malformed.

    Every failure here names the offending row and stops the run. The alternative
    — skipping what does not parse — would silently drop a Claim from both the
    page and the Omission view, which is the one outcome the Omission view exists
    to make impossible.
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == COLUMNS:
            header_index = index
            break
    if header_index is None:
        raise ScoreTableError(
            "scores.md has no Score table: expected a row of "
            f"`{' | '.join(COLUMNS)}` and found none"
        )

    body = lines[header_index + 1 :]
    if not body or not is_delimiter(split_row(body[0])):
        raise ScoreTableError(
            f"row {header_index + 2}: the Score table's header is not followed by a "
            "`|---|` delimiter row"
        )

    claims: list[Claim] = []
    seen: dict[tuple[str, str], int] = {}
    entries: dict[str, tuple[str, str, int]] = {}
    table_ends_at = len(lines)
    for offset, line in enumerate(body[1:]):
        row = header_index + 3 + offset
        if not line.lstrip().startswith("|"):
            table_ends_at = row
            break
        cells = split_row(line)
        if len(cells) != len(COLUMNS):
            raise ScoreTableError(
                f"row {row}: expected {len(COLUMNS)} columns "
                f"({' | '.join(COLUMNS)}), found {len(cells)}: {line.strip()}"
            )
        slug, claim_id, type_, ended, score, width, reason = cells
        if not ENTRY_SLUG.fullmatch(slug):
            raise ScoreTableError(f"row {row}: {slug!r} is not an entry slug: {line.strip()}")
        if not CLAIM_ID.fullmatch(claim_id):
            raise ScoreTableError(
                f"row {row}: claim id {claim_id!r} is not `c<n>`: {line.strip()}"
            )
        if type_ not in ("job", "project"):
            raise ScoreTableError(
                f"row {row}: type {type_!r} is neither `job` nor `project`: {line.strip()}"
            )
        if not ENDED.fullmatch(ended):
            raise ScoreTableError(
                f"row {row}: ended {ended!r} is neither `YYYY-MM` nor `present`: {line.strip()}"
            )
        if not SCORE.fullmatch(score):
            raise ScoreTableError(
                f"row {row}: score {score!r} is not two decimals in 0.00-1.00: {line.strip()}"
            )
        value = Fraction(int(score.replace(".", "")), 100)
        if value > 1:
            raise ScoreTableError(
                f"row {row}: score {score} is above 1.00: {line.strip()}"
            )
        if not WIDTH.fullmatch(width):
            raise ScoreTableError(
                f"row {row}: width {width!r} is neither `1` nor `2` — a Bullet takes "
                f"one typeset line or two, and a claim that will not fit in two is a "
                f"claim to re-read rather than a wider slot: {line.strip()}"
            )
        reason = unescape(reason)
        if not reason:
            raise ScoreTableError(f"row {row}: the reason is empty: {line.strip()}")

        key = (slug, claim_id)
        if key in seen:
            raise ScoreTableError(
                f"row {row}: {slug}/{claim_id} is already scored on row {seen[key]}: "
                f"{line.strip()}"
            )
        seen[key] = row
        if slug in entries:
            first_type, first_ended, first_row = entries[slug]
            if (type_, ended) != (first_type, first_ended):
                raise ScoreTableError(
                    f"row {row}: {slug} is `{type_} / {ended}` here and "
                    f"`{first_type} / {first_ended}` on row {first_row}: {line.strip()}"
                )
        else:
            entries[slug] = (type_, ended, row)
        claims.append(
            Claim(slug, claim_id, type_, ended, value, int(width), reason, row)
        )

    for offset, line in enumerate(lines[table_ends_at:]):
        # A `## ` heading opens a new section — `## Leads` or `## Merges`, each
        # validated by its own parser — so a stray row is only a stray row before
        # the first one of those.
        if line.lstrip().startswith("## "):
            break
        if line.lstrip().startswith("|"):
            raise ScoreTableError(
                f"row {table_ends_at + offset + 1}: a table row sits below the end of "
                f"the Score table, where nothing would have read it: {line.strip()}"
            )

    if not claims:
        raise ScoreTableError("the Score table has a header but no rows")
    return claims


def collect_entries(claims: list[Claim]) -> list[Entry]:
    """Claims grouped into Entries, in the order the entries first appear."""
    by_slug: dict[str, Entry] = {}
    for claim in claims:
        entry = by_slug.get(claim.entry)
        if entry is None:
            entry = by_slug[claim.entry] = Entry(claim.entry, claim.type, claim.ended)
        entry.claims.append(claim)
    return list(by_slug.values())


def parse_leads(text: str, claim_entries: set[str]) -> dict[str, bool]:
    """The `## Leads` table: one row per scored Entry, `y` or `n`, no reason
    (docs/adr/0035-the-lead-crosses-the-seam.md §2). Absent entirely when the bank
    holds no lead yet — every Entry then reads `n`, honestly.
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == LEADS_COLUMNS:
            header_index = index
            break
    if header_index is None:
        return {entry: False for entry in claim_entries}

    body = lines[header_index + 1 :]
    if not body or not is_delimiter(split_row(body[0])):
        raise ScoreTableError(
            f"row {header_index + 2}: the Leads table's header is not followed by a "
            "`|---|` delimiter row"
        )
    leads: dict[str, bool] = {}
    for offset, line in enumerate(body[1:]):
        row = header_index + 3 + offset
        if not line.lstrip().startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(LEADS_COLUMNS):
            raise ScoreTableError(
                f"row {row}: expected {len(LEADS_COLUMNS)} columns (entry | lead), found "
                f"{len(cells)}: {line.strip()}"
            )
        slug, value = cells
        if slug in leads:
            raise ScoreTableError(f"row {row}: {slug} already has a Leads row: {line.strip()}")
        if value not in ("y", "n"):
            raise ScoreTableError(
                f"row {row}: lead {value!r} is neither `y` nor `n`: {line.strip()}"
            )
        leads[slug] = value == "y"

    missing = claim_entries - leads.keys()
    if missing:
        raise ScoreTableError(
            f"the Leads table has no row for {sorted(missing)[0]}, which the claims table "
            "scores — every Entry needs a `y` or `n` row"
        )
    unknown = leads.keys() - claim_entries
    if unknown:
        raise ScoreTableError(
            f"the Leads table has a row for {sorted(unknown)[0]}, which the claims table "
            "never scores"
        )
    return leads


def parse_merges(text: str, claims_by_entry: dict[str, dict[str, Claim]]) -> list[MergeGroup]:
    """The `## Merges` table: a group of 2 or 3 claims declared as one argument
    (docs/adr/0034-a-merged-bullet-coordinates.md §2). Absent entirely when nothing
    merges on this run.
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == MERGES_COLUMNS:
            header_index = index
            break
    if header_index is None:
        return []

    body = lines[header_index + 1 :]
    if not body or not is_delimiter(split_row(body[0])):
        raise ScoreTableError(
            f"row {header_index + 2}: the Merges table's header is not followed by a "
            "`|---|` delimiter row"
        )
    groups: list[MergeGroup] = []
    seen: dict[tuple[str, str], int] = {}
    for offset, line in enumerate(body[1:]):
        row = header_index + 3 + offset
        if not line.lstrip().startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(MERGES_COLUMNS):
            raise ScoreTableError(
                f"row {row}: expected {len(MERGES_COLUMNS)} columns "
                f"(entry | claims | width | reason), found {len(cells)}: {line.strip()}"
            )
        slug, ids_cell, width, reason = cells
        if slug not in claims_by_entry:
            raise ScoreTableError(f"row {row}: {slug!r} is not a scored entry: {line.strip()}")
        if not MERGE_IDS.fullmatch(ids_cell):
            raise ScoreTableError(
                f"row {row}: claims {ids_cell!r} is not 2 or 3 `+`-joined claim ids: "
                f"{line.strip()}"
            )
        ids = tuple(ids_cell.split("+"))
        if len(set(ids)) != len(ids):
            raise ScoreTableError(f"row {row}: {ids_cell} repeats a claim id: {line.strip()}")
        claims = claims_by_entry[slug]
        for claim_id in ids:
            if claim_id not in claims:
                raise ScoreTableError(
                    f"row {row}: {slug}/{claim_id} is not scored in the claims table: "
                    f"{line.strip()}"
                )
            key = (slug, claim_id)
            if key in seen:
                raise ScoreTableError(
                    f"row {row}: {slug}/{claim_id} is already in a merge on row {seen[key]}: "
                    f"{line.strip()}"
                )
            seen[key] = row
            if claims[claim_id].width != 1:
                raise ScoreTableError(
                    f"row {row}: {slug}/{claim_id} is in a merge group and its own claims-"
                    f"table width reads `{claims[claim_id].width}`, not `1` — a merged "
                    f"claim's width column is ambiguous unless it reads 1: {line.strip()}"
                )
        if not WIDTH.fullmatch(width):
            raise ScoreTableError(f"row {row}: width {width!r} is neither `1` nor `2`: {line.strip()}")
        reason = unescape(reason)
        if not reason:
            raise ScoreTableError(f"row {row}: the reason is empty: {line.strip()}")
        groups.append(MergeGroup(slug, ids, int(width), reason, row))
    return groups


def apply_leads_and_merges(
    entries: list[Entry], leads: dict[str, bool], merges: list[MergeGroup]
) -> None:
    """Wire the two extra tables onto the Entries the claims table produced."""
    by_slug = {entry.slug: entry for entry in entries}
    for slug, has_lead in leads.items():
        by_slug[slug].lead = has_lead
    for group in merges:
        by_slug[group.entry].merge_groups.append(group)


#: An `## Openers` row's unit name: one claim id, or a `+`-joined group of 2 or 3,
#: exactly as `## Merges` writes one and exactly as `bullets.md` will cite it. It is
#: `CLAIM_ID` and `MERGE_IDS` in one pattern rather than an alternation of the two,
#: because the column holds either for one reason — **a Bullet slot holds either**,
#: and this names the thing in the slot (docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md §6).
#: A fourth id is refused here rather than deferred to `MERGE_IDS`, so the message
#: names the column the maker actually wrote in.
OPENER_UNIT = re.compile(r"^c[1-9][0-9]*(?:\+c[1-9][0-9]*){0,2}$")


def parse_openers(text: str, entries: list[Entry]) -> dict[str, tuple[str, ...]] | None:
    """The `## Openers` table: which unit opens each Entry's block, on force.

    One row per Entry, one unit named — a claim id or a `+`-joined merge group.
    Score decides which units reach the page; this decides which of them a reader
    meets first, and it is a **different question**: *which of this entry's lines
    would make a stranger reading only one of them want to read the rest?*
    (docs/adr/0040-fit-orders-the-page-force-orders-the-block.md §1.)

    RETURNS `None` WHERE THE TABLE IS ABSENT ENTIRELY, which is not the same as a
    table with a row missing. This mirrors `parse_leads`, and for the same reason:
    a run folder scored before the table existed still packs, and its `## Silent
    calls` says out loud that every entry opened on the unit the score handed it.
    A table that is *present* is held to `check_openers` — a placed Entry with no
    row is a refusal, because the whole point of the table is that the common
    answer is **made rather than inherited** (§3).

    What is checked here is everything the table can be wrong about on its own:
    the entry is scored, the row is not a duplicate, and the name is a **unit** —
    a claim that sits inside a merge group is not one, and neither is a claim
    below the Bullet floor. Whether the named unit actually placed is a fact about
    the packing and is checked after it.
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == OPENERS_COLUMNS:
            header_index = index
            break
    if header_index is None:
        return None

    body = lines[header_index + 1 :]
    if not body or not is_delimiter(split_row(body[0])):
        raise ScoreTableError(
            f"row {header_index + 2}: the Openers table's header is not followed by a "
            "`|---|` delimiter row"
        )
    by_slug = {entry.slug: entry for entry in entries}
    openers: dict[str, tuple[str, ...]] = {}
    for offset, line in enumerate(body[1:]):
        row = header_index + 3 + offset
        if not line.lstrip().startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(OPENERS_COLUMNS):
            raise ScoreTableError(
                f"row {row}: expected {len(OPENERS_COLUMNS)} columns (entry | unit), "
                f"found {len(cells)}: {line.strip()}"
            )
        slug, name = cells
        if slug not in by_slug:
            raise ScoreTableError(
                f"row {row}: {slug!r} is not a scored entry: {line.strip()}"
            )
        if slug in openers:
            raise ScoreTableError(
                f"row {row}: {slug} already has an Openers row — one entry opens on "
                f"one unit: {line.strip()}"
            )
        if not OPENER_UNIT.fullmatch(name):
            raise ScoreTableError(
                f"row {row}: unit {name!r} is neither a claim id nor a `+`-joined "
                f"merge group: {line.strip()}"
            )
        claim_ids = tuple(name.split("+"))
        entry = by_slug[slug]
        if not any(unit.claim_ids == claim_ids for unit in entry.units):
            raise ScoreTableError(
                f"row {row}: {slug}/{name} is not a unit of {slug} — {why_not_a_unit(entry, claim_ids)}"
                f": {line.strip()}"
            )
        openers[slug] = claim_ids
    return openers


#: How a supporting row reached the page, written on its allocation line and read
#: back by nothing — it is for the maker, who otherwise cannot tell a page that
#: argues credentials from a page that had three lines spare
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md,
#: "The cost, stated rather than waved past").
BY_THE_POSTING = "the posting's call"
BY_THE_ROOM = "the room left over"


@dataclass
class SupportingEntry:
    """One row of `scores.md`'s `## Sections` table — a supporting entry, and whether
    the posting called for it.

    It is NOT an `Entry`. It has no claims here, no score, no units and no slots: the
    Packer learns of it through this table and nothing else, and it never enters the
    reservation queue or the score ordering
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §2).

    `placed_by` is filled in by `place_supporting` — `BY_THE_POSTING`, `BY_THE_ROOM`,
    or `None` for one that did not place, which is what the Omission view lists.
    """

    section: str
    slug: str
    #: The Packer's copy of the bank's `ended`, carried across the seam exactly as
    #: the claims table carries one. It orders the residue fill by recency, and
    #: `render.py` refuses a run where the copy and the bank disagree.
    ended: str
    signal: bool
    reason: str
    placed_by: str | None = None

    @property
    def order_key(self) -> tuple[str, str]:
        """Recency descending, then slug ascending — the fixed order of the fill.

        `ended` sorts as text because `YYYY-MM` does, and `present` is mapped to
        `PRESENT_KEY` for the same reason an Entry's is. Reversed on the caller's
        side, so the slug tiebreak has to be inverted here to come out ascending.
        """
        ended = PRESENT_KEY if self.ended == "present" else self.ended
        return (ended, invert(self.slug))


def invert(slug: str) -> str:
    """A key that sorts backwards under `reverse=True`, so one sort does both
    directions. Cheaper than two passes and it keeps the ordering in one expression."""
    return "".join(chr(0x10FFFF - ord(character)) for character in slug)


def parse_sections(text: str, claim_entries: set[str]) -> list[SupportingEntry]:
    """The `## Sections` table: one row per supporting entry the bank holds.

    Absent entirely when the bank holds none — which is the state of every bank
    before the first `ingest` session writes one, so an absent table is a normal run
    and not a refusal. What is refused is a table that is *present* and wrong.

    Every supporting entry gets a row **every run, including the unsignalled ones**,
    for the reason the claims table takes every claim including the zeros: an entry
    left out of the table cannot lose visibly, and the Omission view is built from
    what lost (§4).
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == SECTIONS_COLUMNS:
            header_index = index
            break
    if header_index is None:
        return []

    body = lines[header_index + 1 :]
    if not body or not is_delimiter(split_row(body[0])):
        raise ScoreTableError(
            f"row {header_index + 2}: the Sections table's header is not followed by a "
            "`|---|` delimiter row"
        )
    found: list[SupportingEntry] = []
    seen: set[str] = set()
    for offset, line in enumerate(body[1:]):
        row = header_index + 3 + offset
        if not line.lstrip().startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(SECTIONS_COLUMNS):
            raise ScoreTableError(
                f"row {row}: expected {len(SECTIONS_COLUMNS)} columns "
                f"(section | entry | ended | signal | reason), found {len(cells)}: "
                f"{line.strip()}"
            )
        section, slug, ended, signal, reason = cells
        if section not in SUPPORTING_SECTIONS:
            raise ScoreTableError(
                f"row {row}: {section!r} is not a supporting section — the three are "
                + ", ".join(SUPPORTING_SECTIONS)
                + f": {line.strip()}"
            )
        if not ENTRY_SLUG.fullmatch(slug):
            raise ScoreTableError(f"row {row}: entry {slug!r} is not a slug: {line.strip()}")
        if slug in seen:
            raise ScoreTableError(
                f"row {row}: {slug} already has a Sections row — one entry, one row: "
                f"{line.strip()}"
            )
        # A supporting entry never competes, so it can never also be scored. The two
        # tables naming one slug would mean an entry that both took Bullet slots and
        # rendered as a row, which is two places on one page for one thing (§2).
        if slug in claim_entries:
            raise ScoreTableError(
                f"row {row}: {slug} is also scored in the claims table — a supporting "
                f"entry never competes for a Bullet slot, so it is in one table or the "
                f"other: {line.strip()}"
            )
        if not ENDED.fullmatch(ended):
            raise ScoreTableError(
                f"row {row}: ended {ended!r} is not `YYYY-MM` or `present`: {line.strip()}"
            )
        if signal not in ("y", "n"):
            raise ScoreTableError(
                f"row {row}: signal {signal!r} is neither `y` nor `n`: {line.strip()}"
            )
        if not reason:
            raise ScoreTableError(
                f"row {row}: the reason is empty — a signal that cannot be traced to "
                f"words in the posting is a section invented to fill a page: {line.strip()}"
            )
        found.append(SupportingEntry(section, slug, ended, signal == "y", reason))
        seen.add(slug)
    return found


#: Rows one supporting section may print. A fifth credential is real and is not worth
#: a fifth line of a one-page résumé; what is past the cap lands in the Omission view
#: like any other loss
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §7).
MAX_SUPPORTING_ROWS = 4


def supporting_charge(rows: int) -> int:
    """Lines a supporting section of `rows` rows costs, its `\\section` heading included.

    The same arithmetic as `skills_charge` and deliberately so: a supporting row IS a
    Skills row — `\\resumeItem` with a bold label, in the same list geometry with the
    same zeroed glue — so it is charged `SKILLS_ROW_PT` and `config.py` gains no
    constant. `SKILLS_ROW_WRAP_PT` never appears because a supporting row never wraps:
    it is capped at one typeset line, which `render.py` enforces, and that cap is what
    lets this be a function of a row COUNT rather than of composed text
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §6).

    1 row costs 3 lines, 2 costs 4, 3 costs 5, 4 costs 5.

    THERE IS NO MINIMUM-ROWS FLOOR, unlike the Skills section's two. Skills' rows are
    interchangeable breadth, so one surviving row spends three lines to show a
    category label nobody asked for; a single certification the posting named by name
    is not interchangeable with anything (§7).
    """
    if rows <= 0:
        return 0
    points = Fraction(config.SKILLS_ROW_PT) * rows
    return math.ceil(points / Fraction(config.BULLET_LINE_PT)) + config.SECTION_LINES


def called_sections(supporting: list[SupportingEntry]) -> dict[str, list[SupportingEntry]]:
    """The rows reserved before anything competes: the signalled ones, by section.

    A section is called when at least one of its entries is signalled `y` — the
    judgement is per entry, because a posting naming *AWS Certified Solutions
    Architect* has called for that credential and not for every credential the maker
    holds (§4). The cap applies here too: the signalled rows past
    `MAX_SUPPORTING_ROWS` do not place, and lose visibly in the Omission view.
    """
    by_section: dict[str, list[SupportingEntry]] = {}
    for section in SUPPORTING_SECTIONS:
        rows = sorted(
            (row for row in supporting if row.section == section and row.signal),
            key=lambda row: row.order_key,
            reverse=True,
        )
        if rows:
            by_section[section] = rows[:MAX_SUPPORTING_ROWS]
    return by_section


def reserved_supporting_charge(supporting: list[SupportingEntry]) -> int:
    """What the called sections take off the budget before a single Bullet is seated."""
    return sum(supporting_charge(len(rows)) for rows in called_sections(supporting).values())


def place_supporting(
    supporting: list[SupportingEntry], unspent: int
) -> tuple[dict[str, list[SupportingEntry]], list[str]]:
    """Seat the called sections, then spend the room left over on the rest.

    Runs AFTER `grant_widths`, and the order of payment is the whole decision:
    **Bullets at their charged widths, then supporting rows.** It used to be three
    steps — Bullets, then widths, then rows — because a second line was bought out
    of the residue; `0047` §3 folded the width into what a Bullet costs to place, so
    the two front steps are one and a supporting row is paid out of what the Bullets
    did not need. On a full page nothing supporting places at all, which is correct —
    a full page has no white space to answer (§5).

    `unspent` is the **Room** line's own tail, handed in rather than recomputed, for
    the reason `room_log` takes `seated` rather than re-deriving it: two numbers
    describing the same moment must not be computed twice.

    The fill is a fixed order — `SUPPORTING_SECTIONS`, then recency, then slug — and
    an entry is taken only if the WHOLE of it fits: its own row, plus the heading when
    it is the first row of a section nothing has placed yet. That heading is not a
    special case in the code, because `supporting_charge(n + 1) - supporting_charge(n)`
    already carries it: the first row of a section costs 3, the second 1, the third 1,
    the fourth 0.

    One that does not fit is **skipped and the next is offered** — leapfrogging inside
    the supporting fill, which is `pack_page`'s own rule for units inside one entry
    and is safe here for the same reason: nothing is competing on merit, so passing
    over a section that will not fit costs no one their place.
    """
    placed = called_sections(supporting)
    for rows in placed.values():
        for row in rows:
            row.placed_by = BY_THE_POSTING

    log: list[str] = []
    if not supporting:
        return placed, log

    left = unspent
    taken: list[str] = []
    for section in SUPPORTING_SECTIONS:
        rows = sorted(
            (
                row
                for row in supporting
                if row.section == section and row.placed_by is None
            ),
            key=lambda row: row.order_key,
            reverse=True,
        )
        for row in rows:
            seated = placed.get(section, [])
            if len(seated) >= MAX_SUPPORTING_ROWS:
                break
            cost = supporting_charge(len(seated) + 1) - supporting_charge(len(seated))
            if cost > left:
                continue
            left -= cost
            row.placed_by = BY_THE_ROOM
            placed.setdefault(section, []).append(row)
            taken.append(f"{row.slug} ({cost} line(s))")

    reserved = reserved_supporting_charge(supporting)
    opening = (
        f"Supporting: {reserved} line(s) reserved before packing for "
        f"{len(called_sections(supporting))} section(s) the posting called for; "
        f"{unspent} line(s) unspent after the width pass."
    )
    if taken:
        log.append(
            f"{opening} The room went to {', '.join(taken)}; {left} line(s) still unspent"
        )
    elif unspent:
        log.append(f"{opening} No supporting row fitted in it; {left} line(s) still unspent")
    else:
        log.append(f"{opening} The page had no room left over to offer")
    return placed, log


def supporting_omissions(supporting: list[SupportingEntry], unspent: int) -> list[str]:
    """The third subsection of the Omission view: supporting entries that did not place.

    Cut by structure like the other two — one line per entry the bank holds and the
    page does not show, never a filter on the signal, since the thing being hunted is
    a signal that was judged **wrong** and filtering on it hides exactly those.
    """
    lines: list[str] = []
    for section in SUPPORTING_SECTIONS:
        for row in sorted(
            (row for row in supporting if row.section == section and row.placed_by is None),
            key=lambda row: row.order_key,
            reverse=True,
        ):
            how = (
                f"past the {MAX_SUPPORTING_ROWS}-row cap for {section}"
                if row.signal
                else f"not called by the posting, and the page left {unspent} line(s) unspent"
            )
            lines.append(f"{row.slug} — {section} — {how} — {row.reason}")
    return lines


def supporting_section(placed: dict[str, list[SupportingEntry]]) -> list[str]:
    """`## Supporting` in `allocation.md` — the rows the page is charged for, in order.

    TWO SHAPES HERE ARE CONTRACT, like the `Skills:` line and the placed-claim line's
    width before them: the `###` section heading and the `-` row lines beneath it.
    `render.py` reads them to know which supporting rows to expect, in which sections,
    in which order, and it checks each row's `ended` against the bank. Changing the
    wording means changing a pattern in `render.py` and a fixture in the tests — the
    suite fails on the way past if you do not.
    """
    out = [
        "",
        "## Supporting",
        "",
        "The supporting sections, in page order, and how each row got there — the",
        "posting called for it, or the width pass left room. Never a competitor: none",
        "of these was scored, and the page above packs its Bullets identically without",
        "them (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md).",
        "",
    ]
    if not placed:
        out.append("No supporting section placed.")
        return out
    for section in SUPPORTING_SECTIONS:
        rows = placed.get(section)
        if not rows:
            continue
        out.append(
            f"### {section} — {SECTION_HEADINGS[section]} — {len(rows)} row(s), "
            f"{supporting_charge(len(rows))} line(s) including the heading"
        )
        for row in rows:
            out.append(f"- {row.slug} — ended {row.ended} — {row.placed_by} — {row.reason}")
        out.append("")
    return out[:-1]


def why_not_a_unit(entry: Entry, claim_ids: tuple[str, ...]) -> str:
    """Why a named opener is not something the Packer can give a slot to.

    Four ways to get this wrong and they want different fixes, so the refusal
    names which one it is rather than repeating the grammar back. The commonest by
    far is the merge one: `c1` reads like a unit everywhere else in the run, and
    inside a merge group it is a *part* of one.
    """
    known = {claim.id for claim in entry.claims}
    unknown = [claim_id for claim_id in claim_ids if claim_id not in known]
    if unknown:
        return f"{unknown[0]} is not scored in the claims table"
    merged = {
        claim_id: group for group in entry.merge_groups for claim_id in group.claim_ids
    }
    inside = [claim_id for claim_id in claim_ids if claim_id in merged]
    if inside and len(claim_ids) == 1:
        group = merged[inside[0]]
        return (
            f"it sits inside the merge group {'+'.join(group.claim_ids)}, which is the "
            f"unit that takes the slot — name the group"
        )
    if len(claim_ids) > 1:
        return "no row in `## Merges` declares that group"
    claim = entry.claim_by_id(claim_ids[0])
    return (
        f"it scores {two_decimals(claim.score)}, below the "
        f"{two_decimals(BULLET_FLOOR)} bullet floor, so it never takes a slot to open"
    )


def apply_openers(entries: list[Entry], openers: dict[str, tuple[str, ...]]) -> None:
    """Wire the `## Openers` table onto the Entries, after the merges are on."""
    by_slug = {entry.slug: entry for entry in entries}
    for slug, claim_ids in openers.items():
        by_slug[slug].opener = claim_ids


# --------------------------------------------------------------------------
# Ordering
# --------------------------------------------------------------------------


def order_entries(entries: list[Entry]) -> tuple[list[Entry], list[str]]:
    """Entries in competition order, plus a log line for every tie broken by rule.

    Descending entry score, with any gap below EPSILON treated as a tie and broken
    by recency descending, then entry id ascending.

    The band is transitive: a tie group closes only where two *adjacent* entries sit
    EPSILON or more apart, so any two entries within EPSILON of each other land in the
    same group. 0.90 / 0.86 / 0.83 is one group of three — 0.86 is tied with both
    neighbours, and calling it tied with one and ordered against the other would make
    the relation depend on a third entry.

    The cost is that the band chains: 1.00 / 0.96 / 0.92 / 0.88, each gap under
    EPSILON, collapses into one group spanning 0.12, and recency then leads the 0.88
    entry over the 1.00 one. Every link is a real tie; the span is the price of not
    breaking a tie in the middle of one.
    """
    by_score = sorted(entries, key=lambda entry: (-entry.score, entry.tie_break))

    groups: list[list[Entry]] = []
    for entry in by_score:
        if groups and groups[-1][-1].score - entry.score < EPSILON:
            groups[-1].append(entry)
        else:
            groups.append([entry])

    ordered: list[Entry] = []
    log: list[str] = []
    for group in groups:
        #: A JOB OUTRANKS A PROJECT INSIDE A TIE GROUP, AND ONLY THERE
        #: (docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md §1). Outside
        #: the band score decides, so a 0.50 job never displaces a 0.85 project — the
        #: priority is a tie-break, not an ordering of the two kinds of work.
        group.sort(key=lambda entry: (0 if entry.type == "job" else 1, *entry.tie_break))
        ordered.extend(group)
        if len(group) > 1:
            scored = ", ".join(
                f"{entry.slug} ({two_decimals(entry.score)}, ended {entry.ended})"
                for entry in group
            )
            log.append(
                f"tie: {scored} — each within ε = {two_decimals(EPSILON)} of the "
                "next, so all of them are one tie — ordered jobs first "
                "(docs/adr/0051 §1), then ended descending, then entry ascending: "
                + ", ".join(entry.slug for entry in group)
            )
    return ordered, log


# --------------------------------------------------------------------------
# The page budget
# --------------------------------------------------------------------------

#: Education rows the fixed overhead is charged for when there is no
#: `bank/profile.md` beside the run — the shipped example's one row.
#:
#: Otherwise the Packer counts the `### ` rows in the profile itself
#: (`education_rows`). The profile is the Static profile, not a Bank entry: it never
#: competes, so counting its schools reads nothing the scorer decides and leaves the
#: Packer blind to every Claim. The count is written into `allocation.md`, and
#: render.py refuses a profile that has grown a row since.
EDUCATION_ROWS = 1

EDUCATION_ROW = re.compile(r"^###\s+\S+\s*$", re.M)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def education_rows(run_dir: Path) -> int:
    """The `### ` rows in `<repo>/bank/profile.md`, the bank beside `runs/`."""
    profile = run_dir.resolve().parent.parent / "bank" / "profile.md"
    if not profile.is_file():
        return EDUCATION_ROWS
    text = HTML_COMMENT.sub("", profile.read_text(encoding="utf-8"))
    return len(EDUCATION_ROW.findall(text))

#: What pass one assumes about a Skills section nobody has composed yet: four rows,
#: one typeset line each. OPTIMISTIC on purpose. Reserving the worst case — four
#: rows all wrapping, 9 lines — would permanently spend four lines of evidence
#: defending against a shape that is rare: four skills plus a label runs about 90
#: characters against a 103-character budget (docs/adr/0021-skills-row-cost.md §4).
RESERVED_SKILLS_ROWS = 4

#: Below this a Skills section is not a section. Its heading costs SECTION_LINES, so
#: one surviving row spends three lines to show one — the whole thing goes instead,
#: heading included, and every reserved line comes back
#: (docs/adr/0020-skills-section.md §4).
MIN_SKILLS_ROWS = 2


def skills_charge(skills_rows: list[int] | None) -> int:
    """Lines the Skills section costs, its `\\section` heading included.

    `None` is pass one: charge the reservation. A list is pass two: one typeset
    line count per composed row, and an empty list is a section that was dropped.

    THE ROUNDING HAPPENS ONCE, AT THE SUM, which is `config.py`'s one stated exception
    (`docs/adr/0021-skills-row-cost.md` §2). A row measures `SKILLS_ROW_PT` (14.00pt
    today, one Bullet line, so the two roundings agree); the sum is kept so a template
    change that moves a row off a whole line does not start over-promising.
    """
    if skills_rows is None:
        skills_rows = [1] * RESERVED_SKILLS_ROWS
    if len(skills_rows) < MIN_SKILLS_ROWS:
        return 0
    points = sum(
        Fraction(config.SKILLS_ROW_PT)
        + Fraction(config.SKILLS_ROW_WRAP_PT) * (lines - 1)
        for lines in skills_rows
    )
    return math.ceil(points / Fraction(config.BULLET_LINE_PT)) + config.SECTION_LINES


def bullet_budget(
    entries: list[Entry],
    skills_rows: list[int] | None = None,
    supporting_lines: int = 0,
    education: int = EDUCATION_ROWS,
) -> int:
    """Lines left for Entry headers and Bullets, per docs/calibration.md.

    A section is charged whenever the Score table *contains* that type, rather
    than when one places. Charging by placement would be circular — whether a
    project places is what the budget decides — and the error is in the safe
    direction: an over-charge leaves whitespace, an under-charge is a second page.

    The Skills section is the exception, and not by choice: whether it has a heading
    at all is a fact about what was composed, so its heading is charged inside
    `skills_charge` rather than counted here.

    The Summary is charged UNCONDITIONALLY, beside HEADER_LINES, and that is the
    same argument one notch further on. Whether a Summary was composed is a fact
    about the run, and this function is what runs first — so the page always carries
    one and this always pays for it. An optional Summary would have to be charged
    either way and would be wrong either way: charge it and a run that composed none
    leaves evidence off the page for room nobody used; charge nothing and the
    overflow surfaces at render.py's page-count assert, where the message blames the
    constants (docs/adr/0044-the-page-opens-on-a-summary.md §5).

    ITS HEADING IS CHARGED THE SAME WAY, AND IT IS THE ONE SECTION NOT IN `sections`.
    `\\section{Summary}` is the same macro and the same SECTION_LINES as Experience,
    Projects and Education — what differs is the condition, and the Summary has none.
    The other three are charged when the Score table holds that type or the profile
    holds a row; the Summary heading is on every page that renders, so it is added
    flat rather than counted (docs/adr/0044-the-page-opens-on-a-summary.md, Addendum).

    `supporting_lines` is what the sections the POSTING CALLED FOR were reserved,
    headings included — `reserved_supporting_charge`, computed before this runs. It
    is charged here, ahead of the packing, because a called section is not competing
    for the room: it earned the page on the posting's own terms and the Bullets are
    seated in what is left. The sections that arrive the other way are paid for out
    of the residue, after `grant_widths`, and never reach this function
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §5).
    """
    sections = (
        any(entry.type == "job" for entry in entries)
        + any(entry.type == "project" for entry in entries)
        + (education > 0)  # Education
    )
    overhead = (
        config.HEADER_LINES
        + config.SUMMARY_LINES
        + config.SECTION_LINES  # \section{Summary}, on every page
        + sections * config.SECTION_LINES
        + education * config.ENTRY_HEADER_LINES
        + skills_charge(skills_rows)
        + supporting_lines
    )
    return config.PAGE_LINES - overhead


# --------------------------------------------------------------------------
# Allocation and packing
# --------------------------------------------------------------------------


def pack_page(
    ordered: list[Entry], budget: int
) -> tuple[list[Placement], list[str]]:
    """Reserve every qualifying Entry its minimum block, then hand out the rest.

    TWO PASSES, AND EVERY ENTRY TRAVELS THE SAME PATH THROUGH BOTH.

    **The reservation.** Every Entry with a unit is reserved its header (`header_lines`:
    one row for a project, two for a job, plus `LEAD_LINES` for an Entry with a lead)
    and its best unit at that unit's own declared width, before anything competes for
    depth — *crossing the floor buys presence* (`0047` §3).

    **The distribution.** The remainder goes top-first in Entry-score order: each
    placed Entry takes its own units best-first, each charged its declared width, up
    to `MAX_BULLET_LINES` per Entry — and **a unit that does not fit the lines the
    Entry has left is skipped
    in favour of the next one down**: leapfrogging inside one Entry, never between
    Entries (`docs/adr/0035-the-lead-crosses-the-seam.md` §4). *The floor buys
    presence; score buys depth.*

    The bill, taken deliberately: on a crowded page the bottom of the page is
    **stubs**, an Entry spending three lines — two of header — to say one thing. A
    job at 1 Bullet beside a project at 6 is the design rather than an accident
    (docs/adr/0026-sharing-the-lines.md).

    EVERY unit's width is settled here, at its declared value (`0047` §3). A unit
    that cannot afford its width is leapfrogged in favour of the next one down, so
    no Claim is ever seated and then squeezed — which is how `0025`'s *no Claim
    loses a slot to a wrap* survives the width becoming a charge.
    """
    log: list[str] = []
    free = budget
    #: `Entry.units` is a property that builds fresh `Unit` objects on every
    #: access — cached once per entry so "the reserved unit" and "a candidate in
    #: the distribution pass" can be compared by identity rather than re-deriving
    #: and silently talking past each other.
    units_by_entry = {entry.slug: entry.units for entry in ordered}

    reserved: set[str] = set()
    reserved_unit: dict[str, Unit] = {}
    for entry in reservation_queue(ordered):
        #: The reserved slot is the Entry's best unit at ITS OWN DECLARED WIDTH
        #: (docs/adr/0047-the-bullet-is-an-xyz-sentence.md §3). `0035` §3-4 used to
        #: skip a `width: 2` merge here, because the guaranteed line was one line
        #: and a two-line group could not occupy it. The guaranteed slot is now the
        #: unit's own width, so that exclusion has nothing left to do.
        first = units_by_entry[entry.slug][0]
        minimum = entry.header_lines + first.width
        if free < minimum:
            log.append(
                f"page full: no room to reserve a block for {entry.slug} — "
                f"{free} line(s) left, a block needs {minimum} (header"
                f"{' + lead' if entry.lead else ''} + {first.width} bullet line(s))"
            )
            continue
        free -= minimum
        reserved.add(entry.slug)
        reserved_unit[entry.slug] = first

    placements: list[Placement] = []
    for entry in ordered:
        if entry.slug not in reserved:
            continue
        first = reserved_unit[entry.slug]
        taken: list[Unit] = [first]
        widths: list[int] = [first.width]
        #: The Entry's own line budget, spent alongside the page's `free`. The
        #: reserved unit is charged against it like any other — a block that opens on
        #: a two-line Bullet has four of its six lines left (`0048` §2).
        depth = first.width
        depth_capped: list[Unit] = []
        candidates = [
            unit for unit in units_by_entry[entry.slug][: entry.slots] if unit is not first
        ]
        for unit in candidates:
            #: EVERY unit is charged its declared width, merged or not — `0047` §3's
            #: inversion. It used to read `unit.width if unit.merge else 1`, because a
            #: non-merge Claim's width was a want `grant_widths` paid for later out of
            #: the residue. It is a charge now, and `grant_widths` pays for nothing.
            cost = unit.width
            #: THE ENTRY'S CAP IS TESTED FIRST, so a unit refused by both is reported
            #: against the binding one. An Entry at its depth cap has not run the page
            #: out of room, and saying it did would send the maker to the wrong repair.
            #: The cap is hard. `0049` §4 let an all-merge block borrow past it; `0057`
            #: §5 made merges rare, and with them the reason for the exception.
            if depth + cost > MAX_BULLET_LINES:
                log.append(
                    f"depth cap: {entry.slug} dropped {unit.ref} "
                    f"({two_decimals(unit.score)}) — {cost} line(s) needed, "
                    f"{MAX_BULLET_LINES - depth} left of the entry's {MAX_BULLET_LINES}"
                )
                depth_capped.append(unit)
                continue
            if cost > free:
                log.append(
                    f"shrink: {entry.slug} dropped {unit.ref} ({two_decimals(unit.score)}), "
                    f"the next unit down — {cost} line(s) needed, {free} left for it"
                )
                continue
            free -= cost
            depth += cost
            taken.append(unit)
            widths.append(unit.width)
        log += unit_tie_log(entry, taken, units_by_entry[entry.slug])
        taken, widths, opener_log = open_on_the_declared_unit(entry, taken, widths)
        log += opener_log
        placements.append(Placement(entry, taken, widths, depth_capped))
    return placements, log


def open_on_the_declared_unit(
    entry: Entry, taken: list[Unit], widths: list[int]
) -> tuple[list[Unit], list[int], list[str]]:
    """Move the declared opener to the top of a placed block. PRINT ORDER ONLY.

    Runs at the end of the entry's turn through `pack_page`, on the set of units
    that turn already chose, and permutes `taken` and `widths` together so a slot
    keeps the width it was granted. What comes out is `Entry.ordered_units` order —
    the opener, then score order — restricted to what placed.

    It cannot move a Bullet on or off the page, and that is the whole reason it
    runs here rather than inside `Entry.units`: the reservation, the `[: slots]`
    window and the leapfrogging all read score order, untouched
    (docs/adr/0040-fit-orders-the-page-force-orders-the-block.md §2).

    `grant_widths` runs after this and is unaffected — since `0047` §3 it hands out
    nothing at all, and the widths it once permuted alongside `taken` were already
    final by the time this ran.

    The log line is written on every placed Entry, including the entries where the
    declared unit was top by score anyway: `0026` §5's rule for `Share:` and `0025`
    §7's for `Room:`, applied again — a signal is only readable if its absence never
    has to be interpreted. An Entry with no declared opener says so in the same
    place, since that is the state this table exists to make visible.
    """
    if entry.opener is None:
        inherited = (
            f"Opener: {entry.slug} has no `## Openers` row, so it opens on "
            f"{taken[0].ref}, its best unit by score — inherited, not chosen"
        )
        return taken, widths, [inherited]
    refs = [unit.ref for unit in taken]
    declared = f"{entry.slug}/{'+'.join(entry.opener)}"
    if declared not in refs:
        # It did not place. `check_openers` refuses the run over it; nothing is
        # reordered and nothing is logged, because there is no page to log about.
        return taken, widths, []
    was = refs.index(declared) + 1
    if was == 1:
        agreed = (
            f"Opener: {declared} declared to open {entry.slug}, and already first by "
            f"score — nothing moved"
        )
        return taken, widths, [agreed]
    order = {unit.ref: position for position, unit in enumerate(entry.ordered_units)}
    seated = sorted(zip(taken, widths), key=lambda pair: order[pair[0].ref])
    return (
        [unit for unit, _width in seated],
        [width for _unit, width in seated],
        [
            f"Opener: {declared} moved to the top of {entry.slug}, from position "
            f"{was} by score"
        ],
    )


def check_openers(placements: list[Placement]) -> None:
    """The two refusals that can only be judged once the packing is done.

    Both are about a table that exists and does not describe the page it was
    written for. The Packer refuses rather than falling back on the score, for the
    reason the table exists at all: an opener silently inherited is exactly what
    `0040` was written to stop, and a fallback that fires when the maker's row is
    wrong is that inheritance with a warning printed over it.
    """
    for place in placements:
        entry = place.entry
        if entry.opener is None:
            raise ScoreTableError(
                f"the Openers table has no row for {entry.slug}, which placed "
                f"{bullets_phrase(len(place.units))} — every placed entry names the "
                f"unit that opens its block, and `{place.units[0].ref}` is what the "
                f"score would hand it"
            )
        declared = f"{entry.slug}/{'+'.join(entry.opener)}"
        if declared not in {unit.ref for unit in place.units}:
            placed = ", ".join(unit.ref for unit in place.units)
            raise ScoreTableError(
                f"the Openers table names {declared}, which did not place — "
                f"{entry.slug} took {placed}. An opener is chosen from the units that "
                f"reach the page, and which those are is the allocation's call"
            )


def apply_entry_caps(
    ordered: list[Entry], caps: dict[str, int]
) -> tuple[list[Entry], set[str], dict[str, int], list[str]]:
    """Cut the page to MAX_EXPERIENCE jobs and MAX_PROJECTS projects.

    Returns the survivors, the slugs cut, THE ROOM EACH KIND ACTUALLY HAD after any
    lending, and a Silent call per cut. The room is handed back rather than recomputed
    downstream because the Omission view has to name the same number this cut on.

    Runs after `order_entries` and before anything is reserved, so a capped Entry
    never takes a block another Entry could have used. Returns the survivors in
    competition order, the slugs that were cut, and a Silent call for each.

    THE TWO-MOST-RECENT-JOBS GUARANTEE OUTRANKS THE CAP, and that is the one piece of
    ordering here that is not score. The Experience floor has always held that the
    page shows the last two jobs; a cap applied on score alone would drop a recent
    job that happened to score fourth and quietly break it. So the floor's jobs are
    seated first and the rest of MAX_EXPERIENCE is filled by score. The cap is never
    exceeded: a cap below two seats only the most recent job, or none.

    A capped Entry is not a failure and not an omission the maker can repair by
    editing the bank: it is the page saying it carries three jobs and two projects.
    The Omission view gives it its own reason for exactly that reason.
    """
    #: A CAP BINDS ONLY AGAINST COMPETITION FROM THE OTHER KIND. What the caps exist
    #: to prevent is a page of nothing but Experience while real Projects wait — not
    #: an Experience section held to three when there is nothing to hold it for. So a
    #: section lends what it cannot use: one qualifying project against a cap of two
    #: leaves a slot, and Experience may take it
    #: (docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md §3).
    #:
    #: ONLY UNUSED CAPACITY MOVES, which is the whole guard. A section can never take
    #: a slot the other could have filled, so a bank with four projects still seats
    #: two of them however strong the jobs are. The total stays MAX_EXPERIENCE +
    #: MAX_PROJECTS, and neither section is ever starved by the transfer.
    available = {
        kind: sum(1 for entry in ordered if entry.type == kind and entry.slots)
        for kind in ("job", "project")
    }
    room = {
        "job": caps["job"] + max(0, caps["project"] - available["project"]),
        "project": caps["project"] + max(0, caps["job"] - available["job"]),
    }

    #: ONLY AN ENTRY WITH A QUALIFYING CLAIM TAKES A CAP SLOT. One with nothing at the
    #: floor places nothing, so seating it would cut an entry that could have; it
    #: passes through uncapped, and the Omission view gives it its own reason.
    qualifying = [entry for entry in ordered if entry.slots]
    floor_jobs = sorted(
        (entry for entry in qualifying if entry.type == "job"),
        key=lambda entry: entry.tie_break,
    )[: min(2, room["job"])]
    keep_jobs: list[Entry] = list(floor_jobs)
    for entry in qualifying:
        if len(keep_jobs) >= room["job"]:
            break
        if entry.type == "job" and entry not in keep_jobs:
            keep_jobs.append(entry)
    keep_projects = [entry for entry in qualifying if entry.type == "project"][
        : room["project"]
    ]

    keep = {entry.slug for entry in keep_jobs} | {entry.slug for entry in keep_projects}
    keep |= {entry.slug for entry in ordered if not entry.slots}
    kept = [entry for entry in ordered if entry.slug in keep]
    capped = {entry.slug for entry in ordered if entry.slug not in keep}

    log: list[str] = []
    for entry in ordered:
        if entry.slug not in capped:
            continue
        cap = room[entry.type]
        kind = "experience" if entry.type == "job" else "project"
        lent = "" if cap == caps[entry.type] else (
            f" ({caps[entry.type]} by default, plus "
            f"{cap - caps[entry.type]} the other section could not use)"
        )
        log.append(
            f"entry cap: {entry.slug} ({two_decimals(entry.score)}) did not compete — "
            f"the page carries {cap} {kind} entries{lent}, {cap_rule(entry.type)}"
        )
    return kept, capped, room, log


def cap_rule(kind: str) -> str:
    """How a section's capped room was filled, for the line that names who lost it.

    Not "N scored above it": the two most recent jobs are seated whatever they score,
    so a capped job can outscore one that was kept.
    """
    if kind == "job":
        return "the two most recent jobs first and the rest by score"
    return "taken by score"


def reservation_queue(ordered: list[Entry]) -> list[Entry]:
    """Who is reserved a minimum block, in the order the reservations are made.

    *The two most recent jobs, then Entry-score descending.* The head is the
    **Experience floor**, which stopped being a rule of its own when the Entry floor
    generalised it to everything that qualifies: below ten Entries every qualifying
    Entry is reserved anyway and the order changes nothing, and above ten it does
    its one original job — stopping a projects-heavy pool from shipping an empty
    Experience section — while everything below it is cut lowest-score-first, the
    principle governing every other cut on the page.

    A job with no claim above the Bullet floor is not in the queue at all: the floor
    exists to stop an *empty* Experience section, and padding a job with a 0.40
    claim would trade the emptiness for something worse.
    """
    qualifying = [entry for entry in ordered if entry.slots]
    jobs = sorted(
        (entry for entry in qualifying if entry.type == "job"),
        key=lambda entry: entry.tie_break,
    )[:2]
    head = {entry.slug for entry in jobs}
    return jobs + [entry for entry in qualifying if entry.slug not in head]


def unit_tie_log(entry: Entry, taken: list[Unit], all_units: list[Unit]) -> list[str]:
    """The unit refs that decided the last slot, when two units scored the same.

    The Fit rubric's anchors are coarse enough that equal scores inside one entry
    are common, so the cut often lands between two identical numbers. That is a
    tie broken by rule, and it belongs in the log with the entry-level ones.
    `all_units` is unbounded by the cap or the budget — the runner-up may have
    lost to either, and both are still a tie worth logging.
    """
    taken_refs = {unit.ref for unit in taken}
    lost = [unit for unit in all_units if unit.ref not in taken_refs]
    if not taken or not lost:
        return []
    last, first_out = taken[-1], lost[0]
    if last.score != first_out.score:
        return []
    also_tied = [unit.ref for unit in lost if unit.score == last.score]
    return [
        f"tie: {last.ref} took the last slot in {entry.slug} over "
        f"{' and '.join(also_tied)}, all at {two_decimals(last.score)} — "
        "broken by claim id ascending"
    ]


def share_log(placements: list[Placement], budget: int) -> list[str]:
    """One aggregate line saying how the page was shared out. EVERY RUN.

    The counterpart of `room_log`'s line, and always printed for the same reason:
    on a crowded page *"placed at their reserved line only"* is the signal that the
    bank has outgrown the page, and a signal is only readable if its absence never
    has to be interpreted.

    It is also the only evidence the Entry floor will ever get. Every candidate
    sharing rule — greedy, round-robin, a soft cap at three — produced the identical
    page on the bank the rule was chosen against, so it was decided on principle
    alone, and this line is what turns the next crowded page into evidence about
    whether top-first was right (docs/adr/0026-sharing-the-lines.md §5).
    """
    if not placements:
        return []
    headers = sum(place.entry.header_lines for place in placements)
    available = budget - headers
    reserved = sum(place.widths[0] for place in placements)
    remainder = available - reserved
    extra = [
        (place.entry.slug, sum(place.widths[1:]))
        for place in placements
        if len(place.units) > 1
    ]
    spent = sum(lines for _slug, lines in extra)
    stubs = [place.entry.slug for place in placements if len(place.units) == 1]

    where = (
        ", ".join(f"{slug} +{lines}" for slug, lines in extra)
        if extra
        else "nothing — no placed entry earned a second bullet"
    )
    reserved_only = (
        f"{len(stubs)} entry(s) placed at their reserved line only: "
        + ", ".join(stubs)
        if stubs
        else "no entry placed at its reserved line only"
    )
    leads = sum(1 for place in placements if place.entry.lead)
    lead_note = (
        f", {leads} of them carrying a lead ({leads * config.LEAD_LINES} line(s))"
        if leads
        else ""
    )
    return [
        f"Share: {available} line(s) for Bullets after "
        f"{len(placements)} header(s){lead_note}. Every qualifying entry reserved 1 "
        f"unit ({reserved} line(s) in all); {spent} of the remaining {remainder} "
        f"line(s) went in score order — {where}. {reserved_only}"
    ]


def bullets_phrase(count: int) -> str:
    """`1 bullet`, `2 bullets` — the log is read by a person."""
    return f"{count} bullet" if count == 1 else f"{count} bullets"


def lines_phrase(count: int) -> str:
    """`1 line`, `2 lines` — the granted width, as `allocation.md` writes it."""
    return f"{count} line" if count == 1 else f"{count} lines"


# --------------------------------------------------------------------------
# The width pass
# --------------------------------------------------------------------------


def grant_widths(
    placements: list[Placement], budget: int
) -> list[str]:
    """Report the residue. GRANTS NOTHING — every width was charged at reservation.

    THIS PASS USED TO BE THE WHOLE WIDTH ECONOMY and is now only its accountant.
    Under `0025` §6 a non-merge Claim's `width: 2` was a WANT: `pack_page` charged
    it one line, and this pass raised the ones the page could afford out of what the
    evidence left over, in claim-score order, refusing the rest. `0047` §3 inverted
    that — a Bullet is charged its declared width at reservation, because an XYZ
    sentence needs the room to say all three of its parts and a second line handed
    out of the leftovers cannot be relied on while composing.

    So there is nothing left to grant here, and the function survives for two
    reasons rather than out of sentiment. It computes the residue, which
    `place_supporting` spends and the `Room:` line prints — the page's real white
    space, still the number the supporting sections are paid for out of
    (docs/adr/0045-…). And keeping the pass in the spine keeps the `Room:` Silent
    call on every run, which `0025` §7 asked for so that "no room to give" said run
    after run stays readable as a signal.

    What survives of `0025` intact: **no Claim ever loses a slot to a wrap.** It
    used to be true because widths were granted after placement; it is true now
    because a width is part of what a unit costs to place at all, so a unit that
    cannot afford its width is skipped in favour of the next one down by
    `pack_page`'s own leapfrogging rather than being seated and then squeezed.
    """
    seated = budget - sum(place.lines for place in placements)
    return room_log(seated)


def room_log(seated: int) -> list[str]:
    """The width pass's one aggregate Silent call. EVERY RUN, including the empty ones.

    A width granted or surrendered is a call made by rule rather than by score, so
    it belongs beside the shrink lines and the Skills reconcile. Printing it only
    when something moved would lose the signal that matters most: on a full page
    every declared want is refused, and *"no room to give"* said on every run is
    exactly the complaint this map was opened about, surfacing as a line the maker
    can read (docs/adr/0025-bullet-wrap-cost.md §7).

    IT NO LONGER REPORTS GRANTS, BECAUSE `0047` §3 LEFT NONE TO REPORT. Until then
    this line named which Claims got a second line and which asked and were written
    to one, because the width was a want and who won it was a call made by rule
    rather than by score. A width is charged at reservation now, so the answer is
    already in `## Placed` — every unit prints its own line count there — and a
    second account of it here is the derived copy this repo keeps refusing to write.

    What is left is the number that was always the load-bearing half: **the white
    space**. It is what `place_supporting` spends, so a reader tracing why a
    Certifications section did or did not place ends up on this line
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md).
    It is written even when it is zero, for `0025` §7's own reason: a signal is only
    readable if its absence never has to be interpreted, and *"0 line(s) unspent"*
    run after run is the page too full to write well in — which under `0047` is the
    normal state of a page and not a complaint.
    """
    return [
        f"Room: {seated} line(s) left after the Bullets were seated, "
        f"every one of them charged its declared width; {seated} line(s) unspent "
        f"and available to the supporting sections."
    ]


# --------------------------------------------------------------------------
# The Skills reconcile
# --------------------------------------------------------------------------


def reconcile_log(skills_rows: list[int]) -> list[str]:
    """The Silent call for the second pass — a call made by rule, not by score.

    It is written on every second pass, including the ones where nothing moved,
    which is where this departs from `floor_log`'s "a rule that fired without
    changing anything is not a silent call". The Experience floor is a rule inside
    one pass; this is a whole second pass, and a reader has to be able to confirm
    it ran. That composing one row fewer than reserved hands back *nothing* — the
    rounding absorbs it — is also exactly the kind of surprise worth stating.
    """
    reserved = skills_charge(None)
    spent = skills_charge(skills_rows)
    opening = (
        f"Skills reconcile: reserved {reserved} line(s) for "
        f"{RESERVED_SKILLS_ROWS} rows at one line each; "
    )
    if len(skills_rows) < MIN_SKILLS_ROWS:
        return [
            opening
            + f"the composed section came to {len(skills_rows)} row(s), under the "
            f"{MIN_SKILLS_ROWS}-row floor, so it goes heading and all and all "
            f"{reserved} line(s) came back to the page"
        ]
    wrapping = sum(1 for lines in skills_rows if lines > 1)
    shape = f"{len(skills_rows)} rows, " + (
        "none wrapping" if not wrapping else f"{wrapping} wrapping"
    )
    if spent < reserved:
        moved = f"so {reserved - spent} line(s) came back to the page"
    elif spent > reserved:
        moved = f"so {spent - reserved} line(s) came off the page"
    else:
        moved = "so the budget is unchanged — the rounding absorbed it"
    return [opening + f"the composed section cost {spent} ({shape}), {moved}"]


def skills_paragraph(skills_rows: list[int] | None) -> str:
    """What `allocation.md` says the Skills section was charged.

    `render.py` reads this line back, which is what stops a reservation being
    rendered and what catches a `--skills-rows` that does not describe the rows
    actually composed. Both are the same failure as an extra Bullet: a page
    charged for something other than what it holds.

    ITS WORDING IS CONTRACT, and it is the only line here that is. Rewording it
    means changing `ALLOCATED_ROWS` and `ALLOCATED_NO_SECTION` in `render.py` and
    the fixture in `tests/test_render.py` (`docs/adr/0023-skills-allocation-check.md`).
    """
    charged = skills_charge(skills_rows)
    if skills_rows is None:
        return (
            f"Skills: {RESERVED_SKILLS_ROWS} row(s) reserved at one typeset line each, "
            f"charged {charged} line(s) including the heading. This is a RESERVATION, "
            f"not the composed section — re-run with `--skills-rows` once the rows "
            f"exist, and render from that."
        )
    if len(skills_rows) < MIN_SKILLS_ROWS:
        return (
            f"Skills: no section — {len(skills_rows)} composed row(s) is under the "
            f"{MIN_SKILLS_ROWS}-row floor, so the section goes heading and all and "
            f"nothing is charged."
        )
    return (
        f"Skills: {len(skills_rows)} row(s), "
        f"{','.join(str(lines) for lines in skills_rows)} typeset line(s) each, "
        f"charged {charged} line(s) including the heading."
    )


# --------------------------------------------------------------------------
# Writing allocation.md
# --------------------------------------------------------------------------


def omission_view(
    ordered: list[Entry],
    placements: list[Placement],
    capped: set[str] | None = None,
    room: dict[str, int] | None = None,
) -> tuple[list[str], list[str]]:
    """What lost: one line per non-placing Entry, one per Claim that lost a slot.

    The cut is structural — no band around the cut line, no top-N — because the
    object of the search is a claim whose *score* is wrong, and a score-based cut
    hides exactly those most reliably. Every reason is the one Opus wrote, carried
    across verbatim; the Packer never writes one of its own.

    BOTH HALVES CARRY A STRUCTURAL REASON IN THE SAME POSITION, between the score
    and the prose. The Entry line could not state one until the **Entry floor** left
    it a countable set of causes — before that, an Entry could lose for any of the
    reasons the walk stopped, and the line said only how it scored
    (docs/adr/0026-sharing-the-lines.md §5).

    A WIDTH IS NOW AMONG THE REASONS, AND THAT SENTENCE HAS BEEN REVERSED. It used
    to read that a wrap could never be one, because the width pass ran after packing
    and spent only lines the evidence did not want, so the placed set was fixed
    before a second line was granted (docs/adr/0025-bullet-wrap-cost.md §7). `0047`
    §3 made the width a charge at reservation, so a unit's declared width is part of
    why it did or did not place, and two of the structural reasons below now turn on
    it.

    THE TWO ARE KEPT APART ON PURPOSE. *Dropped when the page ran out* and *dropped
    at the entry's own depth cap* look identical on the page — a claim that is not
    there — and point at opposite repairs: the first says the bank has outgrown one
    page, the second says this one block is deeper than a one-page résumé will show
    and nothing about the rest of the bank (docs/adr/0048-the-depth-cap-is-a-line-budget.md §3).
    """
    allocated_by_slug = {place.entry.slug: place.units for place in placements}
    capped_by_slug = {
        place.entry.slug: {unit.claim_ids for unit in place.depth_capped}
        for place in placements
    }
    seated = len(placements)
    entry_lines: list[str] = []
    claim_lines: list[str] = []

    for entry in ordered:
        allocated = allocated_by_slug.get(entry.slug)
        if allocated is None:
            best = entry.ordered_claims[0]
            #: THREE REASONS AN ENTRY IS ABSENT, AND THE CAP IS THE NEW ONE. It is
            #: named apart from *no room* because it is not about this page being
            #: full: the entry never competed, and a page with lines to spare would
            #: have cut it just the same
            #: (docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md §2).
            if capped and entry.slug in capped:
                cap = (room or {"job": MAX_EXPERIENCE, "project": MAX_PROJECTS})[entry.type]
                kind = "experience" if entry.type == "job" else "project"
                why = (
                    f"did not compete — the page carries {cap} {kind} entries, "
                    f"{cap_rule(entry.type)}"
                )
            else:
                why = (
                    f"no room to reserve a block; the page seated {seated} entries"
                    if entry.slots
                    else f"no claim at or above the {two_decimals(BULLET_FLOOR)} "
                    f"bullet floor, so it earned no slot to reserve"
                )
            entry_lines.append(
                f"{entry.slug} — entry score {two_decimals(entry.score)} — {why} — "
                f"best claim {best.ref} ({two_decimals(best.score)}) — {best.reason}"
            )
            continue

        allocated_claim_ids = {claim_id for unit in allocated for claim_id in unit.claim_ids}
        merged_ids = {
            claim_id for group in entry.merge_groups for claim_id in group.claim_ids
        }
        units_by_ids = {unit.claim_ids: (position, unit) for position, unit in enumerate(entry.units)}
        #: NAMED `capped_units` AND NOT `capped`, because the parameter of that name
        #: is `0051`'s set of entry slugs the caps cut, and this is `0048`'s set of
        #: unit ids one block's depth cap refused. They shadowed each other here
        #: once, which silently reported every capped entry as one the page had no
        #: room for.
        capped_units = capped_by_slug.get(entry.slug, set())

        for claim in entry.ordered_claims:
            if claim.id in allocated_claim_ids:
                continue
            if claim.id in merged_ids:
                group = next(g for g in entry.merge_groups if claim.id in g.claim_ids)
                position, _unit = units_by_ids[group.claim_ids]
                why = why_it_lost(entry, position, group.claim_ids, capped_units)
            elif claim.score < BULLET_FLOOR:
                why = f"below the {two_decimals(BULLET_FLOOR)} bullet floor"
            else:
                position, _unit = units_by_ids[(claim.id,)]
                why = why_it_lost(entry, position, (claim.id,), capped_units)
            claim_lines.append(
                f"{claim.ref} — {two_decimals(claim.score)} — {why} — {claim.reason}"
            )
    return entry_lines, claim_lines


def why_it_lost(
    entry: Entry, position: int, claim_ids: tuple[str, ...], capped: set[tuple[str, ...]]
) -> str:
    """The structural reason one unit inside a placed Entry did not reach the page.

    Three causes, and they are kept apart because they send the maker to three
    different places (docs/adr/0048-the-depth-cap-is-a-line-budget.md §3):

    - **outside the candidate window** — the Entry has more qualifying units than
      `MAX_BULLETS`, and this one never competed. The repair is nothing; the block is
      deep and the window is doing its job.
    - **the Entry's own depth cap** — it competed, and this block had spent its
      `MAX_BULLET_LINES`. Nothing about the rest of the page: a bank half this size
      would lose the same unit.
    - **the page ran out** — it competed, the block had room, and the budget did not.
      This one IS about the rest of the page, and it is the line that means the bank
      has outgrown one page.
    """
    if position >= entry.slots:
        return f"beyond the {MAX_BULLETS}-unit cap on an entry"
    if claim_ids in capped:
        return (
            f"dropped at {entry.slug}'s own {MAX_BULLET_LINES}-line depth cap, "
            f"not for want of room on the page"
        )
    return f"dropped when {entry.slug} was shrunk to fit the page"


def two_decimals(value: Fraction) -> str:
    """Round half up to two decimals — a display concern only; the arithmetic is exact."""
    hundredths = (value * 100 * 2 + 1) // 2
    return f"{int(hundredths) // 100}.{int(hundredths) % 100:02d}"


def page_order(placements: list[Placement]) -> list[Placement]:
    """Placements as the page will read: Experience, then Projects.

    Jobs and projects compete in one score-ordered pool, but the template routes
    them into separate sections, so competition order and page order are different
    things whenever the two types interleave. `allocation.md` records page order —
    it is the document a person checks the PDF against. The competition that
    produced it is in the entry scores and the silent-call log.
    """
    jobs = [place for place in placements if place.entry.type == "job"]
    projects = [place for place in placements if place.entry.type == "project"]
    return jobs + projects


def merges_section(placements: list[Placement]) -> list[str]:
    """`## Merges` — every Bullet that fuses more than one Claim, Opus's reason
    carried verbatim, plus the one arithmetic check available
    (docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md §5, §7).

    Beside the Omission view rather than inside it: nothing here was omitted, and
    a merge is Opus's call rather than a Silent one the Packer made by rule.
    """
    lines = [
        "## Merges",
        "",
        "Every Bullet on this page that fuses more than one Claim, with what made",
        "them one line. Shown, not asked — a disagreement is a bank edit and a",
        "re-run, never an override.",
        "",
    ]
    rows: list[str] = []
    for place in page_order(placements):
        for unit, width in zip(place.units, place.widths):
            if unit.merge:
                rows.append(
                    f"- {unit.ref} — {lines_phrase(width)} — "
                    f"{unit.reason}"
                )
    lines += rows or ["No Bullet on this page fuses more than one Claim."]
    return lines


def render_allocation(
    run_dir: Path,
    placements: list[Placement],
    log: list[str],
    omission: tuple[list[str], list[str]],
    budget: int,
    skills_rows: list[int] | None,
    supporting: dict[str, list[SupportingEntry]] | None = None,
    supporting_omitted: list[str] | None = None,
    education: int = EDUCATION_ROWS,
) -> str:
    spent = sum(place.lines for place in placements)
    supporting = supporting or {}
    supporting_rows = sum(len(rows) for rows in supporting.values())
    supporting_lines = sum(supporting_charge(len(rows)) for rows in supporting.values())
    out = [
        f"# Allocation: {run_dir.name}",
        "",
        "Written by `tools/pack.py` from `scores.md` and the Education row count of",
        "`bank/profile.md`. Never hand-edited — the bank is the only repair surface, so a",
        "disagreement with anything below is fixed by editing the bank and re-running.",
        "",
        f"Budget: {budget} lines for Entry headers and Bullets, of "
        f"{config.PAGE_LINES} on the page. Spent {spent}, {budget - spent} left.",
        "",
        # The Summary never competes and never varies, so nothing below would ever
        # mention it — and a line the page spends that the allocation cannot show
        # spent is how a budget stops being auditable. Said here, once.
        f"Summary: {config.SUMMARY_LINES} line(s) of prose plus "
        f"{config.SECTION_LINES} for its heading, charged before anything competed. "
        f"Every page carries one (docs/adr/0044-the-page-opens-on-a-summary.md).",
        "",
        # render.py reads this line back and refuses a profile with more rows than
        # it names.
        f"Education: {education} row(s), charged "
        f"{(config.SECTION_LINES if education else 0) + education * config.ENTRY_HEADER_LINES}"
        f" line(s) including the heading.",
        "",
        skills_paragraph(skills_rows),
        "",
        # Said here for the same reason the Summary line above is: a line the page
        # spends that the allocation cannot show spent is how a budget stops being
        # auditable. Unlike the `Skills:` line this is prose and nothing parses it —
        # `## Supporting` below is what render.py reads, and the charge is arithmetic
        # over the rows it lists.
        f"Supporting: {len(supporting)} section(s), {supporting_rows} row(s), charged "
        f"{supporting_lines} line(s) including the headings."
        if supporting
        else "Supporting: no section.",
        "",
        "## Placed",
        "",
        "In page order — every `job` under Experience, then every `project` under",
        "Projects. They competed in one score-ordered pool to get here. Units, not",
        "claims — a merge group is one row (docs/adr/0037-a-beat-earns-its-line-by-landing-alone.md §6).",
        "",
    ]
    for place in page_order(placements):
        entry = place.entry
        lead_field = " — lead" if entry.lead else ""
        out.append(
            f"### {entry.slug} — {entry.type} — ended {entry.ended} — "
            f"entry score {two_decimals(entry.score)}{lead_field} — "
            f"{bullets_phrase(len(place.units))}"
        )
        for unit, width in zip(place.units, place.widths):
            out.append(
                f"- {unit.ref} — {two_decimals(unit.score)} — "
                f"{lines_phrase(width)} — {unit.reason}"
            )
        out.append("")

    out += [
        "## Silent calls",
        "",
        "Every call the Packer made by rule rather than by score, with its reason.",
        "",
    ]
    out += [f"- {line}" for line in log] or ["Nothing was decided by rule on this run."]
    out.append("")
    out += merges_section(placements)
    out += supporting_section(supporting)

    entry_lines, claim_lines = omission
    out += [
        "",
        "## Did not place",
        "",
        "The Omission view — only what lost, cut by structure rather than by score.",
        "What placed is not restated here: the PDF is that report.",
        "",
        "### Entries",
        "",
    ]
    out += [f"- {line}" for line in entry_lines] or ["Every scored Entry placed."]
    out += ["", "### Claims", ""]
    out += [f"- {line}" for line in claim_lines] or [
        "Every Claim of every placed Entry took a slot."
    ]
    if supporting_omitted is not None:
        out += ["", "### Supporting", ""]
        out += [f"- {line}" for line in supporting_omitted] or [
            "Every supporting entry the bank holds is on the page."
            if supporting
            else "The bank holds no supporting entries."
        ]
    out.append("")
    return "\n".join(out)


#: A row is capped at two typeset lines: one that would run to three sheds skills
#: instead (docs/adr/0021-skills-row-cost.md §3). A 3 here is therefore a
#: composition that should never have been written, not a page the budget can hold.
MAX_ROW_LINES = 2


def parse_skills_rows(raw: str | None) -> list[int] | None:
    """`--skills-rows 1,2,1,1` -> [1, 2, 1, 1]. `None` stays None: pass one.

    An empty value is a real answer — the section was dropped — and is not the
    same as omitting the flag, which asks for the reservation.
    """
    if raw is None:
        return None
    if not raw.strip():
        return []
    rows = []
    for cell in raw.split(","):
        cell = cell.strip()
        if not cell.isdigit() or int(cell) < 1:
            raise ScoreTableError(
                f"--skills-rows takes one typeset line count per composed row, "
                f"like `1,2,1,1`, and {cell!r} is not one"
            )
        if int(cell) > MAX_ROW_LINES:
            raise ScoreTableError(
                f"--skills-rows says a row takes {cell} typeset lines, and a row is "
                f"capped at {MAX_ROW_LINES} — a row that would run longer sheds "
                f"skills from its least prominent end instead"
            )
        rows.append(int(cell))
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="pack.py", usage="python tools/pack.py runs/<jd-slug> [--skills-rows 1,2,1,1]"
    )
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--skills-rows",
        default=None,
        help="pass two: one typeset line count per composed Skills row, comma "
        "separated; empty when the section was dropped. Omit it for pass one, "
        "which reserves four single-line rows.",
    )
    parser.add_argument(
        "--max-experience",
        type=int,
        default=MAX_EXPERIENCE,
        help=f"how many job entries the page may carry (default {MAX_EXPERIENCE})",
    )
    parser.add_argument(
        "--max-projects",
        type=int,
        default=MAX_PROJECTS,
        help=f"how many project entries the page may carry (default {MAX_PROJECTS})",
    )
    args = parser.parse_args(argv[1:])
    if args.max_experience < 0 or args.max_projects < 0:
        parser.error("--max-experience and --max-projects cannot be negative")
    run_dir = args.run_dir
    caps = {"job": args.max_experience, "project": args.max_projects}
    scores_path = run_dir / "scores.md"
    if not scores_path.is_file():
        print(f"pack.py: no Score table at {scores_path}", file=sys.stderr)
        return 1

    try:
        skills_rows = parse_skills_rows(args.skills_rows)
    except ScoreTableError as error:
        print(f"pack.py: {error}", file=sys.stderr)
        return 1

    try:
        text = scores_path.read_text(encoding="utf-8")
        claims = parse_scores(text)
        entries = collect_entries(claims)
        claims_by_entry = {
            entry.slug: {claim.id: claim for claim in entry.claims} for entry in entries
        }
        leads = parse_leads(text, set(claims_by_entry))
        supporting = parse_sections(text, set(claims_by_entry))
        merges = parse_merges(text, claims_by_entry)
        apply_leads_and_merges(entries, leads, merges)
        # After the merges, because a unit is only a unit once the groups are on.
        openers = parse_openers(text, entries)
        if openers is not None:
            apply_openers(entries, openers)
    except ScoreTableError as error:
        print(f"pack.py: {scores_path}: {error}", file=sys.stderr)
        return 1

    ordered, log = order_entries(entries)
    competing, capped, room, cap_log = apply_entry_caps(ordered, caps)
    log += cap_log
    education = education_rows(run_dir)
    budget = bullet_budget(
        entries, skills_rows, reserved_supporting_charge(supporting), education
    )
    if skills_rows is not None:
        log += reconcile_log(skills_rows)
    placements, packing_log = pack_page(competing, budget)
    if openers is not None:
        try:
            check_openers(placements)
        except ScoreTableError as error:
            print(f"pack.py: {scores_path}: {error}", file=sys.stderr)
            return 1
    log += packing_log
    log += share_log(placements, budget)
    log += grant_widths(placements, budget)

    # The Room line's own tail. `grant_widths` raises nothing since `0047` §3, so
    # this equals the number that line printed; it is recomputed rather than passed
    # through because what the supporting fill spends is a property of the seated
    # placements, and that is where it should be read from (§5).
    unspent = budget - sum(place.lines for place in placements)
    placed_supporting, supporting_log = place_supporting(supporting, unspent)
    log += supporting_log

    (run_dir / "allocation.md").write_text(
        render_allocation(
            run_dir,
            placements,
            log,
            omission_view(ordered, placements, capped, room),
            budget,
            skills_rows,
            placed_supporting,
            supporting_omissions(supporting, unspent),
            education,
        ),
        encoding="utf-8",
    )
    wide = sum(width for place in placements for width in place.widths if width == 2)
    print(
        f"pack.py: {len(placements)} entries, "
        f"{sum(len(place.units) for place in placements)} bullets "
        f"({wide // 2} of them two lines) -> {run_dir / 'allocation.md'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
