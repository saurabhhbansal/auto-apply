"""tools/lengths.py, driven as a command over a throwaway run folder.

Every test writes a hand-written `bullets.md` into `tmp_path`, runs
`python tools/lengths.py <run-dir>`, and asserts on stdout and the exit code.
Nothing imports lengths.py.

`config.py` is imported via the `config_module` fixture only to size fixtures against
the real `CHARS_PER_BULLET`, so a re-calibration changes what these tests build rather
than breaking them. What is asserted is the boundary: a line exactly at the budget is
silent, one character past it is named — the same comparison `render.py`'s lint makes.

The output format is contract: the `tailor` skill reads the fields, and the
`skills rows` line is the argument the Packer's second pass takes — which is why it
is printed whenever there are rows rather than only when something is over budget.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


# --------------------------------------------------------------------------
# Driving the tool
# --------------------------------------------------------------------------


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    """A run folder, named the way the maker would name one."""
    folder = tmp_path / "acme-backend-engineer"
    folder.mkdir()
    return folder


def lengths(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/lengths.py", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def measure(repo_root: Path, run_dir: Path) -> list[str]:
    """Run it, insist it stayed a measurement, and hand back what it printed."""
    result = lengths(repo_root, str(run_dir))
    assert result.returncode == 0, f"lengths.py is not a lint: {result.stderr}"
    assert result.stderr == ""
    return result.stdout.splitlines()


def write_bullets(run_dir: Path, *lines: str) -> None:
    """`bullets.md` in the shape Opus composes it — sections, then `## Skills`."""
    (run_dir / "bullets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prose(length: int) -> str:
    """A sentence of exactly `length` characters, in one plain unbroken run."""
    return ("Cut checkout latency by batching commits in the order-ingest consumer " * 20)[
        :length
    ]


def write_allocation(run_dir: Path, widths: dict[str, int]) -> None:
    """The `## Placed` section of an `allocation.md`, just enough to carry widths.

    `lengths.py` reads the granted width out of the run folder beside `bullets.md`,
    so a fixture that measures a wide slot has to supply one.
    """
    lines = ["# Allocation: acme-backend-engineer", "", "## Placed", ""]
    by_entry: dict[str, list[tuple[str, int]]] = {}
    for ref, width in widths.items():
        slug, claim_id = ref.split("/")
        by_entry.setdefault(slug, []).append((claim_id, width))
    for slug, claims in by_entry.items():
        lines.append(f"### {slug} — job — ended 2024-01 — entry score 0.80 — n bullets")
        lines += [
            f"- {slug}/{claim_id} — 0.80 — {width} line{'s' if width > 1 else ''} — why"
            for claim_id, width in claims
        ]
        lines.append("")
    (run_dir / "allocation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def skills_totalling(length: int) -> list[str]:
    """Skill names whose `", ".join(...)` is exactly `length` characters."""
    names = ["PostgreSQL"] * (length // 12)
    joined = ", ".join(names)
    if len(joined) < length:
        names.append("x" * (length - len(joined) - 2))
    assert len(", ".join(names)) == length
    return names


# --------------------------------------------------------------------------
# Bullets — every offender named, not the first
# --------------------------------------------------------------------------


def test_a_file_inside_the_budget_prints_nothing(repo_root, run_dir, config_module):
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(config_module.CHARS_PER_BULLET)}",
        "",
        "## Skills",
        "- Go (helios-payments/c1)",
    )

    assert measure(repo_root, run_dir) == []


def test_a_bullet_one_character_over_is_named_with_its_line_and_length(
    repo_root, run_dir, config_module
):
    over = config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
        "",
        "## Skills",
        "- Go (helios-payments/c1)",
    )

    assert measure(repo_root, run_dir) == [f"2 {over} {prose(over)}"]


def test_a_bullet_is_measured_against_its_granted_width(
    repo_root, run_dir, config_module
):
    """Two lines granted, so the same prose that was over budget is now inside it."""
    over = config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
    )
    write_allocation(run_dir, {"helios-payments/c1": 2})

    assert measure(repo_root, run_dir) == []


def test_a_bullet_past_even_its_two_lines_is_still_named(
    repo_root, run_dir, config_module
):
    over = 2 * config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
    )
    write_allocation(run_dir, {"helios-payments/c1": 2})

    assert measure(repo_root, run_dir) == [f"2 {over} {prose(over)}"]


def test_a_granted_second_line_nobody_used_is_reported_as_advisory(
    repo_root, run_dir, config_module
):
    """Not a defect. A short line is not a failure — the rubric's standard is
    completeness, not length. What this points at is a `width` declared in
    `scores.md` that the page paid for and the sentence did not need."""
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(40)}",
    )
    write_allocation(run_dir, {"helios-payments/c1": 2})

    assert measure(repo_root, run_dir) == ["wide slot 2 40 helios-payments/c1"]


def test_a_one_line_slot_written_short_is_not_reported(repo_root, run_dir):
    """The advisory is about an unused *grant*, not about a short sentence."""
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(40)}",
    )
    write_allocation(run_dir, {"helios-payments/c1": 1})

    assert measure(repo_root, run_dir) == []


def test_with_no_allocation_to_read_every_bullet_is_measured_at_one_line(
    repo_root, run_dir, config_module
):
    """§3.2 runs this before there is an allocation, and one line is what the
    Packer would have charged."""
    over = config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
    )

    assert measure(repo_root, run_dir) == [f"2 {over} {prose(over)}"]


def test_every_over_budget_bullet_is_named_in_one_pass(repo_root, run_dir, config_module):
    """The whole reason this exists: `render.py` fails on the first one, and a file
    with four of them would otherwise cost four rendering runs to discover."""
    over = config_module.CHARS_PER_BULLET + 4
    write_bullets(
        run_dir,
        "# Bullets: acme-backend-engineer",
        "",
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
        f"- helios-payments/c2: {prose(config_module.CHARS_PER_BULLET)}",
        f"- helios-payments/c3: {prose(over)}",
        "",
        "## ledger-cli",
        f"- ledger-cli/c1: {prose(over)}",
        "",
        "## Skills",
        "- Go (helios-payments/c1)",
    )

    assert [line.split()[0] for line in measure(repo_root, run_dir)] == ["4", "6", "9"]


def test_the_line_number_is_the_line_in_the_file(repo_root, run_dir, config_module):
    over = config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "# Bullets: acme-backend-engineer",
        "",
        "",
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
        "",
        "## Skills",
    )

    assert measure(repo_root, run_dir)[0].startswith("5 ")


# --------------------------------------------------------------------------
# The spread — the one finding here that render.py also fails on
# --------------------------------------------------------------------------


def near_the_cap(cap: int, count: int) -> list[int]:
    """`count` Bullet lengths jammed against the cap — the page a spread describes.

    Every one is **over** the spread threshold (`cap - 15`) and **under** the cap, so
    the only finding such a page can produce is the spread itself. Derived from the
    cap rather than written out, because a re-calibration moves both ends of that
    band at once: at `CHARS_PER_BULLET = 103` this is the literal `95..102` these
    tests used to carry, and at 99 it is `91..98`.
    """
    return [cap - 8 + (index % 8) for index in range(count)]


def a_page_of(run_dir: Path, lengths_: list[int]) -> None:
    """One Bullet per length, in one entry, with a one-row Skills section under it."""
    write_bullets(
        run_dir,
        "## helios-payments",
        *(
            f"- helios-payments/c{at}: {prose(length)}"
            for at, length in enumerate(lengths_, 1)
        ),
        "",
        *skills_section(("Languages", ["Go"])),
    )


def test_a_page_written_to_the_cap_is_reported_before_a_compile_is_spent(
    repo_root, run_dir, config_module
):
    """The one set check that also lives here, because it is the one you need while
    the file is still being written: a repeated opener is one rephrase, a spread is
    the whole page (`docs/adr/0030-the-composed-set.md` §5)."""
    cap = config_module.CHARS_PER_BULLET
    a_page_of(run_dir, near_the_cap(cap, 14))

    printed = measure(repo_root, run_dir)

    assert printed[0] == (
        f"spread 0/5 of 14 one-line bullets at or under "
        f"{cap - 15} (shortest is {cap - 8})"
    )


def test_a_page_with_a_third_of_its_lines_finishing_early_says_nothing(
    repo_root, run_dir, config_module
):
    cap = config_module.CHARS_PER_BULLET
    short = cap - 15
    a_page_of(run_dir, [short] * 5 + near_the_cap(cap, 9))

    assert measure(repo_root, run_dir) == ["skills rows 1"]


def test_five_bullets_at_the_cap_are_not_a_distribution_here_either(
    repo_root, run_dir, config_module
):
    a_page_of(run_dir, [config_module.CHARS_PER_BULLET] * 5)

    assert measure(repo_root, run_dir) == ["skills rows 1"]


def test_the_spread_is_reported_after_the_bullets_and_before_the_rows(
    repo_root, run_dir, config_module
):
    """The file order the maker reads it in: the lines to shorten, then the page,
    then the argument the Packer's second pass takes."""
    cap = config_module.CHARS_PER_BULLET
    a_page_of(run_dir, [cap + 1] + near_the_cap(cap, 13))

    printed = measure(repo_root, run_dir)

    assert printed[0].startswith("2 ")
    assert printed[1].startswith("spread ")
    assert printed[2] == "skills rows 1"


def test_reporting_a_spread_still_exits_zero(repo_root, run_dir, config_module):
    """`render.py` fails this same rule; here it stays a measurement."""
    a_page_of(run_dir, near_the_cap(config_module.CHARS_PER_BULLET, 14))

    result = lengths(repo_root, str(run_dir))

    assert result.returncode == 0
    assert result.stderr == ""
    assert any(line.startswith("spread ") for line in result.stdout.splitlines())


def test_a_granted_second_line_is_outside_the_spread(repo_root, run_dir, config_module):
    """Six one-line Bullets at the cap and two wide ones is a page of eight with no
    distribution: what the rule counts is the lines that had a choice."""
    a_page_of(run_dir, [99, 100, 101, 102, 103, 99, 200, 201])
    write_allocation(
        run_dir, {"helios-payments/c7": 2, "helios-payments/c8": 2}
    )

    printed = measure(repo_root, run_dir)

    assert [line for line in printed if line.startswith("spread ")] == [
        f"spread 0/2 of 6 one-line bullets at or under "
        f"{config_module.CHARS_PER_BULLET - 15} (shortest is 99)"
    ]


# --------------------------------------------------------------------------
# The Skills rows — measured per row, in the typeset lines each will take
# --------------------------------------------------------------------------


def skills_section(*rows: tuple[str, list[str]]) -> list[str]:
    """`## Skills` and its `### <label>` rows, as bullets.md carries them."""
    lines = ["## Skills"]
    for label, names in rows:
        lines += ["", f"### {label}", *(f"- {name} (helios-payments/c1)" for name in names)]
    return lines


def test_the_row_line_counts_are_printed_for_the_packers_second_pass(
    repo_root, run_dir
):
    """Not a finding — the argument `pack.py --skills-rows` needs, so it is printed
    whether or not anything is over budget."""
    write_bullets(
        run_dir,
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
        "",
        *skills_section(
            ("Languages", ["Go", "Rust"]),
            ("Platform", ["Kafka", "PostgreSQL"]),
        ),
    )

    assert measure(repo_root, run_dir) == ["skills rows 1,1"]


def test_a_row_that_wraps_is_counted_as_two_lines_and_is_not_a_finding(
    repo_root, run_dir, config_module
):
    """A row may wrap. It is the Packer's business, not the maker's, so it reaches
    the argument and never the findings."""
    write_bullets(
        run_dir,
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
        "",
        *skills_section(
            ("Languages", ["Go", "Rust"]),
            ("Platform", skills_totalling(config_module.CHARS_PER_BULLET + 20)),
        ),
    )

    assert measure(repo_root, run_dir) == ["skills rows 1,2"]


def test_a_row_past_the_two_line_cap_is_a_finding(repo_root, run_dir, config_module):
    """Past two lines the row sheds skills instead, so this one the maker must see."""
    write_bullets(
        run_dir,
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
        "",
        *skills_section(
            ("Languages", ["Go", "Rust"]),
            ("Platform", skills_totalling(3 * config_module.CHARS_PER_BULLET)),
        ),
    )

    printed = measure(repo_root, run_dir)
    assert printed[0].startswith("skills row 2 Platform ")
    assert printed[-1].startswith("skills rows 1,")


def test_a_file_with_no_skills_rows_says_nothing_about_them(repo_root, run_dir):
    """The heading with nothing under it is the escape hatch for a JD the bank
    answers with nothing — there is no argument to print."""
    write_bullets(
        run_dir,
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
        "",
        "## Skills",
    )

    assert measure(repo_root, run_dir) == []


def test_the_rows_are_reported_after_the_bullets(repo_root, run_dir, config_module):
    over = config_module.CHARS_PER_BULLET + 1
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(over)}",
        "",
        *skills_section(("Languages", ["Go", "Rust"]), ("Platform", ["Kafka"])),
    )

    printed = measure(repo_root, run_dir)

    assert printed[0].startswith("2 ")
    assert printed[-1] == "skills rows 1,1"


# --------------------------------------------------------------------------
# A measuring tape, not a lint
# --------------------------------------------------------------------------


def test_finding_an_offender_still_exits_zero(repo_root, run_dir, config_module):
    """Whether the run may proceed stays `render.py`'s to say — this only measures."""
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(config_module.CHARS_PER_BULLET + 40)}",
        "",
        "## Skills",
    )

    result = lengths(repo_root, str(run_dir))

    assert result.returncode == 0
    assert result.stdout


def test_it_writes_nothing_into_the_run_folder(repo_root, run_dir, config_module):
    write_bullets(
        run_dir,
        "## helios-payments",
        f"- helios-payments/c1: {prose(config_module.CHARS_PER_BULLET + 40)}",
        "",
        "## Skills",
    )
    before = (run_dir / "bullets.md").read_bytes()

    lengths(repo_root, str(run_dir))

    assert sorted(path.name for path in run_dir.iterdir()) == ["bullets.md"]
    assert (run_dir / "bullets.md").read_bytes() == before


def test_the_summary_is_measured_against_its_own_budget(repo_root, run_dir, config_module):
    """The Summary is the widest prose on the page, so neither other count applies.

    Reported here rather than only at the compile for the reason everything in this
    file is: it is a number to write to, before a compile is spent
    (`docs/adr/0044-the-page-opens-on-a-summary.md` §6).
    """
    over = ("A backend engineer who builds payment systems and the data under them. " * 6)[
        : config_module.SUMMARY_CHARS + 10
    ]
    write_bullets(
        run_dir,
        "## Summary",
        over,
        "",
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
    )

    findings = measure(repo_root, run_dir)

    assert any(line.startswith(f"summary {len(over)} ") for line in findings), findings


def test_a_summary_inside_its_budget_is_not_a_finding(repo_root, run_dir):
    """The tape stops at the character count. Whether the paragraph actually broke in
    two typeset lines is render.py's post-compile call, and nothing this side of
    pdflatex can answer it — so a legal count is silence here."""
    write_bullets(
        run_dir,
        "## Summary",
        "A backend engineer who builds payment systems and the data work under them.",
        "",
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
    )

    assert not [line for line in measure(repo_root, run_dir) if line.startswith("summary ")]


def test_the_summary_is_not_counted_as_a_bullet_or_a_skill(repo_root, run_dir):
    """It sits above the first entry section and is neither. A parse that let its
    prose fall through to the Bullet matcher would measure it at CHARS_PER_BULLET."""
    write_bullets(
        run_dir,
        "## Summary",
        "- helios-payments/c1: this looks like a Bullet and is inside the Summary.",
        "",
        "## helios-payments",
        "- helios-payments/c1: A Bullet well inside the budget.",
    )

    findings = measure(repo_root, run_dir)

    assert not [line for line in findings if "looks like a Bullet" in line]


# --------------------------------------------------------------------------
# The command surface
# --------------------------------------------------------------------------


def test_a_run_folder_with_no_bullets_fails_and_names_the_file(repo_root, run_dir):
    result = lengths(repo_root, str(run_dir))

    assert result.returncode == 1
    assert "bullets.md" in result.stderr


def test_no_argument_is_a_usage_error(repo_root):
    result = lengths(repo_root)

    assert result.returncode == 2
    assert "usage:" in result.stderr
