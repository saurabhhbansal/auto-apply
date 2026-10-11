"""tools/config.py holds the Page-budget numbers in one block, no logic and no I/O.

"No logic and no I/O" is asserted rather than merely stated: a constant computed at
import time would be a function of the environment instead of a measurement of the
template, and two machines could then select different evidence for the same
résumé.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from pack_constants import skills_charge

#: The counts, in whole Bullet lines or whole characters.
PAGE_BUDGET_COUNTS = [
    "PAGE_LINES",
    "HEADER_LINES",
    "SECTION_LINES",
    "ENTRY_HEADER_LINES",
    "PROJECT_HEADER_LINES",
    "CHARS_PER_BULLET",
    "BOLD_CHARS_PER_BULLET",
    #: The entry arc's lead line (docs/adr/0032-the-entry-arc.md §4). LEAD_LINES
    #: is fixed at 1 by decision, not derived — but it is still an int constant in
    #: this same block, so it belongs in the count list rather than a third one.
    "LEAD_LINES",
    "LEAD_CHARS",
    #: LEAD_CHARS's bold twin, measured at the lead's own \linewidth rather than
    #: derived from a Bullet's ratio, because the lead now carries emphasis
    #: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).
    "BOLD_LEAD_CHARS",
    #: The Summary (docs/adr/0044-the-page-opens-on-a-summary.md). SUMMARY_LINES is
    #: fixed at 2 by decision, the same standing LEAD_LINES has; SUMMARY_CHARS is
    #: measured, though not from a rate — it bounds two typeset lines rather than
    #: one, so the probe measures the fit itself.
    "SUMMARY_LINES",
    "SUMMARY_CHARS",
]

#: The three in points. `BULLET_LINE_PT` is the unit the counts are expressed in;
#: the two Skills-row costs are the stated exception to rounding each element up,
#: because a row is never charged alone (docs/adr/0021-skills-row-cost.md §1).
PAGE_BUDGET_POINTS = [
    "BULLET_LINE_PT",
    "SKILLS_ROW_PT",
    "SKILLS_ROW_WRAP_PT",
]

PAGE_BUDGET_CONSTANTS = PAGE_BUDGET_COUNTS + PAGE_BUDGET_POINTS


@pytest.fixture(scope="module")
def config_source(repo_root: Path) -> str:
    return (repo_root / "tools" / "config.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def config_ast(config_source: str) -> ast.Module:
    return ast.parse(config_source)


def test_all_the_constants_are_present(config_module):
    for name in PAGE_BUDGET_CONSTANTS:
        assert hasattr(config_module, name), f"config.py is missing {name}"


def test_every_count_is_a_positive_int(config_module):
    for name in PAGE_BUDGET_COUNTS:
        value = getattr(config_module, name)
        assert isinstance(value, int), f"{name} is {type(value).__name__}, not int"
        assert not isinstance(value, bool), f"{name} is a bool"
        assert value > 0, f"{name} is {value}"


def test_every_point_measurement_is_a_positive_float(config_module):
    for name in PAGE_BUDGET_POINTS:
        value = getattr(config_module, name)
        assert isinstance(value, float), f"{name} is {type(value).__name__}, not float"
        assert value > 0, f"{name} is {value}"


def test_the_module_defines_nothing_but_those_constants(config_ast):
    """No stray names, so the block is the whole file's content."""
    assigned = [
        target.id
        for node in config_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    ]
    assert sorted(assigned) == sorted(PAGE_BUDGET_CONSTANTS)


def test_no_logic(config_ast):
    """Only a docstring and plain assignments of literals — nothing executable."""
    for node in config_ast.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # the module docstring
        assert isinstance(node, ast.Assign), (
            f"line {node.lineno}: config.py may only hold assignments, "
            f"found {type(node).__name__}"
        )
        assert isinstance(node.value, ast.Constant), (
            f"line {node.lineno}: a constant must be a literal, not a computed value"
        )


def test_no_io_and_no_imports(config_ast):
    """An import is how I/O would arrive, so the check is for either."""
    for node in ast.walk(config_ast):
        assert not isinstance(node, (ast.Import, ast.ImportFrom)), (
            f"line {node.lineno}: config.py must not import anything"
        )
        assert not isinstance(node, ast.Call), (
            f"line {node.lineno}: config.py must not call anything"
        )
        assert not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)), (
            f"line {node.lineno}: config.py must not define functions or classes"
        )


def test_the_constants_are_recorded_as_measured(config_source):
    """The file has to say when it was last calibrated, and against what.

    Without this the numbers are indistinguishable from guesses, which is the one
    thing the calibration exists to rule out.
    """
    assert "docs/calibration.md" in config_source
    assert "Last calibrated:" in config_source


def test_a_bullet_budget_survives_the_fixed_overhead(config_module):
    """Sanity floor: a realistic page must have room for real Bullets.

    Three jobs, two projects, one Education row, three sections, the Summary with its
    own heading, and a four-row Skills section carrying its own heading. If this ever
    goes non-positive the constants are nonsense, whatever the calibration said.
    """
    c = config_module
    overhead = (
        c.HEADER_LINES
        + c.SUMMARY_LINES
        + c.SECTION_LINES  # \section{Summary}, on every page
        + 3 * c.SECTION_LINES
        + 6 * c.ENTRY_HEADER_LINES  # 5 entries + 1 education row
        + skills_charge(c, [1, 1, 1, 1])
    )
    assert c.PAGE_LINES - overhead >= 15


def test_a_skills_row_costs_no_more_than_a_bullet_line(config_module):
    """A row's first line pays the list's inter-item glue; a line inside it does not.

    The floor this holds is that neither is over `BULLET_LINE_PT`. A row that cost
    MORE than a Bullet line would be a Skills section quietly outbidding the evidence
    it sits under, which is not a thing the page budget should be able to express.

    It used to hold something narrower — `SKILLS_ROW_PT < BULLET_LINE_PT`, from when a
    row measured 10.00pt against 14.00 — and that was the headline argument for
    charging the section in points (`docs/adr/0021-skills-row-cost.md` §1). The row is
    14.00pt since the 2026-08-10 re-measure that stopped the rows setting tighter than
    `\\small`'s own leading, so a row is exactly one Bullet line and the strict
    inequality is gone. The points arithmetic stays because it is derived from a
    measurement rather than from that inequality; see `docs/calibration.md`.
    """
    c = config_module
    assert c.SKILLS_ROW_WRAP_PT <= c.SKILLS_ROW_PT <= c.BULLET_LINE_PT


def test_bold_characters_are_charged_at_a_tighter_rate(config_module):
    """Bold is wider, so fewer of them fit — charging them at the plain rate is the
    over-promise `docs/adr/0020-skills-section.md` §6 refuses."""
    assert config_module.BOLD_CHARS_PER_BULLET < config_module.CHARS_PER_BULLET


def test_the_summary_costs_less_than_the_evidence_it_displaces(config_module):
    """A sanity floor on the one element that is charged before anything competes.

    Not a calibration — the probe owns that. This is the judgement `0044` §1 made
    and could not measure: two lines is what a summary is worth against a page that
    holds tens of them. A Summary charged a fifth of the page would be a different
    decision, arriving as a number nobody argued for.
    """
    c = config_module
    assert 0 < c.SUMMARY_LINES <= 3
    assert c.SUMMARY_LINES * 10 < c.PAGE_LINES


def test_the_summary_is_the_widest_prose_on_the_page(config_module):
    """It sits at top level, outside every itemize — wider than a lead, which is
    itself wider than a Bullet. Reusing either count for it would over-promise, and
    a count that came back *narrower* would mean the block moved into a list."""
    c = config_module
    assert c.SUMMARY_CHARS > c.LEAD_CHARS > c.CHARS_PER_BULLET


def test_the_summary_budget_is_under_what_its_lines_would_naively_hold(config_module):
    """The measurement `0044` §6 insisted on, pinned as an inequality.

    `SUMMARY_CHARS` bounds TWO typeset lines, and a paragraph breaks at word
    boundaries — so it must come in under `SUMMARY_LINES x` a per-line count, which
    assumes a first line filled to the last scaled point. A value at or above that
    product is a budget derived from a rate, and it hands the composer a number the
    compile then refuses.
    """
    c = config_module
    assert c.SUMMARY_CHARS < c.SUMMARY_LINES * c.LEAD_CHARS
