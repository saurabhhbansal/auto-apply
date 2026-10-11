"""The Packer's own numbers the tests have to know, read out of pack.py's source.

`EDUCATION_ROWS` is what pack.py charges for Education when there is no
`bank/profile.md` beside the run, which is the case for every fixture run folder
here; with a profile, pack.py counts its rows instead.

The Skills reservation's two numbers are here for a related reason: a test that
sizes a fixture against the page has to know what the Skills section was charged,
and a literal 5 would silently stop meaning anything the day a row's cost is
re-measured.

Read as text, never imported: the suite's seam is the CLI.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def packer_constant(name: str, repo_root: Path | None = None) -> int:
    """One `NAME = <int>` assignment from tools/pack.py, as text."""
    source = (repo_root or REPO_ROOT) / "tools" / "pack.py"
    match = re.search(rf"^{name} = (\d+)$", source.read_text(encoding="utf-8"), re.M)
    assert match, f"no {name} assignment in {source}"
    return int(match.group(1))


def skills_charge(config, skills_rows: list[int] | None = None) -> int:
    """Lines the Skills section costs, its own `\\section` heading included.

    docs/calibration.md's arithmetic, restated here rather than imported, the same
    way the rest of the budget formula is: these tests state what the page *should*
    charge, so that a Packer which computes something else fails them.

    `None` is pass one — the reservation, four rows at one typeset line each.
    """
    if skills_rows is None:
        skills_rows = [1] * packer_constant("RESERVED_SKILLS_ROWS")
    if len(skills_rows) < packer_constant("MIN_SKILLS_ROWS"):
        return 0
    points = sum(
        Fraction(config.SKILLS_ROW_PT) + Fraction(config.SKILLS_ROW_WRAP_PT) * (lines - 1)
        for lines in skills_rows
    )
    return math.ceil(points / Fraction(config.BULLET_LINE_PT)) + config.SECTION_LINES


def education_rows_charged(repo_root: Path | None = None) -> int:
    """The Education rows `tools/pack.py` charges the fixed page overhead for."""
    return packer_constant("EDUCATION_ROWS", repo_root)
