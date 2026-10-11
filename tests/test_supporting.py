"""The three supporting sections, driven end to end over a throwaway run folder.

`docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md`.

**One file rather than four, and the reason is the feature's shape.** Everything else
in the suite is per-tool because everything else is one tool's business: the Packer
packs, the Renderer renders. A supporting section is the one thing here whose whole
content is a hand-off *across the seam* — Opus signals in `scores.md`, `pack.py` turns
the signal and the leftover room into seats, `render.py` builds a row it never chose
and refuses one nobody seated. Split three ways, each half would be asserted against a
fixture of the other half's output, and the joins are exactly what can break.

Same convention as its neighbours: the tools are run as commands, the run folder's
files are the contract, and nothing imports the tools' internals.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from allocation_md import section

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"

CLAIM_COLUMNS = ["entry", "claim", "type", "ended", "score", "width", "reason"]
SECTION_COLUMNS = ["section", "entry", "ended", "signal", "reason"]

#: The supporting entries the fixture bank holds, with the section each routes to and
#: the `ended` its frontmatter carries. Written out rather than globbed: the point of
#: several of these tests is that the copy in `scores.md` is checked against the bank,
#: and a copy derived from the bank could never disagree with it.
SUPPORTING = {
    "aws-solutions-architect": ("certifications", "2025-03"),
    "deep-learning-specialization": ("certifications", "2024-02"),
    "placement-coordinator": ("responsibilities", "2025-05"),
    "robotics-society": ("extracurriculars", "2024-06"),
}


# --------------------------------------------------------------------------
# Driving the two tools
# --------------------------------------------------------------------------


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    """A repo-shaped throwaway: the fixture bank, and a run folder beside it."""
    shutil.copytree(FIXTURE_BANK, tmp_path / "bank")
    folder = tmp_path / "runs" / "acme-backend-engineer"
    folder.mkdir(parents=True)
    return folder


def table(columns: list[str], rows: list[tuple[str, ...]]) -> list[str]:
    return [
        "| " + " | ".join(columns) + " |",
        "|" + "---|" * len(columns),
        *("| " + " | ".join(row) + " |" for row in rows),
        "",
    ]


def scores_md(
    claims: list[tuple[str, ...]],
    sections: list[tuple[str, ...]] | None = None,
) -> str:
    """A Score table, with the `## Sections` table under it where one is given.

    `None` writes no table at all, which is the state of every bank before the first
    supporting `ingest` session and has to keep packing.
    """
    lines = ["# Scores: a hand-written fixture", "", *table(CLAIM_COLUMNS, claims)]
    if sections is not None:
        lines += ["## Sections", "", *table(SECTION_COLUMNS, sections)]
    return "\n".join(lines)


def signals(*signalled: str) -> list[tuple[str, ...]]:
    """A `## Sections` row for every supporting entry the fixture bank holds.

    Every entry gets a row every run, including the `n`s — the rule the claims
    table's zeros follow, and for the same reason (§4).
    """
    return [
        (
            where,
            slug,
            ended,
            "y" if slug in signalled else "n",
            f'the posting says "certified" and this answers it'
            if slug in signalled
            else "nothing in the posting reaches it",
        )
        for slug, (where, ended) in SUPPORTING.items()
    ]


#: One job, deliberately shallow, so the page has room left over. Two claims at the
#: floor and nothing else: on a 50-line page that leaves a large residue, which is
#: what the room trigger spends.
THIN_CLAIMS = [
    ("helios-payments", "c1", "job", "present", "1.00", "1", "a fixture reason"),
    ("helios-payments", "c3", "job", "present", "0.80", "1", "a fixture reason"),
]


def pack(repo_root: Path, run_dir: Path, *args: str) -> subprocess.CompletedProcess:
    #: THE CAPS ARE LIFTED UNLESS A TEST IS ABOUT THEM. `0051` caps a real page at
    #: three jobs and two projects, and most fixtures here build five to eleven
    #: entries to exercise the Entry floor, the sharing rule and the tie band. Left
    #: at their defaults every one of those would be testing the cap instead of the
    #: thing it was written for. A test that IS about the cap passes its own.
    if not any(flag.startswith("--max-") for flag in args):
        args = (*args, "--max-experience", "11", "--max-projects", "11")
    return subprocess.run(
        [sys.executable, "tools/pack.py", str(run_dir), *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def pack_ok(repo_root: Path, run_dir: Path, *args: str) -> str:
    result = pack(repo_root, run_dir, *args)
    assert result.returncode == 0, f"pack.py failed: {result.stderr}"
    return (run_dir / "allocation.md").read_text(encoding="utf-8")


def render(repo_root: Path, run_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/render.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def seated(allocation: str) -> list[tuple[str, str, str]]:
    """`## Supporting`, as `[(section, slug, how it got there)]` in page order."""
    found: list[tuple[str, str, str]] = []
    where = None
    for line in section(allocation, "Supporting").splitlines():
        heading = re.match(r"^### (\S+) — ", line)
        if heading:
            where = heading.group(1)
            continue
        row = re.match(r"^- (\S+) — ended \S+ — ([^—]+) — ", line)
        if row and where:
            found.append((where, row.group(1), row.group(2).strip()))
    return found


def unspent(allocation: str) -> int:
    """The Room line's own tail — the number the white-space trigger spends."""
    match = re.search(r"(\d+) line\(s\) unspent", allocation)
    assert match, f"no Room line in:\n{allocation}"
    return int(match.group(1))


# --------------------------------------------------------------------------
# The table, and what it refuses
# --------------------------------------------------------------------------


def test_a_bank_with_no_supporting_entries_packs_and_says_so(repo_root, run_dir):
    """No `## Sections` table is the normal state of a bank, not a malformed file."""
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS), encoding="utf-8")

    allocation = pack_ok(repo_root, run_dir)

    assert "Supporting: no section." in allocation
    assert "No supporting section placed." in section(allocation, "Supporting")
    assert "The bank holds no supporting entries." in allocation


@pytest.mark.parametrize(
    "row, refusal",
    [
        (("degrees", "aws-solutions-architect", "2025-03", "y", "why"), "not a supporting section"),
        (("certifications", "aws-solutions-architect", "2025-03", "maybe", "why"), "neither `y` nor `n`"),
        (("certifications", "aws-solutions-architect", "2025", "y", "why"), "not `YYYY-MM`"),
        (("certifications", "aws-solutions-architect", "2025-03", "y", ""), "the reason is empty"),
        (("certifications", "helios-payments", "2024-06", "y", "why"), "also scored in the claims table"),
    ],
)
def test_the_sections_table_refuses_what_it_cannot_mean(repo_root, run_dir, row, refusal):
    """Each cell is checked, and the refusal says which one and why.

    The last case is the load-bearing one: a slug in both tables would be an Entry
    that took Bullet slots *and* rendered as a row — one thing in two places on one
    page, which is the failure §2 exists to make impossible.
    """
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, [row]), encoding="utf-8")

    result = pack(repo_root, run_dir)

    assert result.returncode == 1
    assert refusal in result.stderr, result.stderr


def test_one_entry_gets_one_row(repo_root, run_dir):
    rows = signals() + [("certifications", "aws-solutions-architect", "2025-03", "y", "again")]
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, rows), encoding="utf-8")

    result = pack(repo_root, run_dir)

    assert result.returncode == 1
    assert "already has a Sections row" in result.stderr


# --------------------------------------------------------------------------
# The two triggers
# --------------------------------------------------------------------------


def test_a_called_section_is_reserved_off_the_budget_before_anything_competes(
    repo_root, run_dir, config_module
):
    """The posting's call takes its lines ahead of the packing, like the Skills section.

    Asserted as a DIFFERENCE between two runs of the same claims, which is the only
    way to say "it came off the budget" without restating the budget formula back at
    the tool. One certification is a heading plus one row: `SECTION_LINES` plus
    `ceil(SKILLS_ROW_PT / BULLET_LINE_PT)`.
    """
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, signals()), encoding="utf-8")
    without = int(re.search(r"Budget: (\d+) lines", pack_ok(repo_root, run_dir)).group(1))

    (run_dir / "scores.md").write_text(
        scores_md(THIN_CLAIMS, signals("aws-solutions-architect")), encoding="utf-8"
    )
    allocation = pack_ok(repo_root, run_dir)
    with_call = int(re.search(r"Budget: (\d+) lines", allocation).group(1))

    charge = config_module.SECTION_LINES + 1
    assert without - with_call == charge
    assert ("certifications", "aws-solutions-architect", "the posting's call") in seated(allocation)


def test_an_uncalled_section_places_out_of_the_room_the_width_pass_left(repo_root, run_dir):
    """The white-space trigger, on a page with room to spare.

    Two claims on one job leave a large residue, and the fill spends it in the fixed
    order — certifications, then responsibilities, then extracurriculars.
    """
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, signals()), encoding="utf-8")

    allocation = pack_ok(repo_root, run_dir)

    assert [(where, slug) for where, slug, _ in seated(allocation)] == [
        ("certifications", "aws-solutions-architect"),
        ("certifications", "deep-learning-specialization"),
        ("responsibilities", "placement-coordinator"),
        ("extracurriculars", "robotics-society"),
    ]
    assert {how for _, _, how in seated(allocation)} == {"the room left over"}


def test_a_full_page_seats_nothing_supporting(repo_root, run_dir):
    """On a full page nothing supporting places — a full page has no white space.

    The order of payment is Bullets at their charged widths, then supporting rows,
    so a page whose evidence has taken every line it can offers the fill nothing.
    Built by declaring every slot at two lines.

    IT ASSERTS A RESIDUE TOO SMALL TO BUY A SECTION RATHER THAN A RESIDUE OF ZERO,
    and the difference is `0047` §3's doing. When a second line was granted out of
    the residue, the grants ran until the purse was empty and a full page landed on
    exactly 0. A charged width is indivisible: a page with one line left cannot seat
    a two-line Bullet in it, so an odd line is stranded and the residue lands on 0
    or 1 depending on the parity of what fitted. Neither can pay for a supporting
    section, whose first row costs 3 (its own row plus SECTION_LINES for the
    heading), and that — not the zero — is what this test is about.
    """
    (run_dir / "scores.md").write_text(
        scores_md(a_full_page_of_claims(), signals()), encoding="utf-8"
    )

    allocation = pack_ok(repo_root, run_dir)

    assert unspent(allocation) < 3, "the residue must not be able to buy a section"
    assert seated(allocation) == []
    assert "No supporting section placed." in section(allocation, "Supporting")


def test_the_room_a_called_section_took_is_not_offered_twice(repo_root, run_dir):
    """A signalled entry is seated once, on the call, and never again out of the room."""
    (run_dir / "scores.md").write_text(
        scores_md(THIN_CLAIMS, signals("placement-coordinator")), encoding="utf-8"
    )

    allocation = pack_ok(repo_root, run_dir)

    rows = [(slug, how) for _, slug, how in seated(allocation)]
    assert rows.count(("placement-coordinator", "the posting's call")) == 1
    assert not any(
        slug == "placement-coordinator" and how == "the room left over" for slug, how in rows
    )


def a_full_page_of_claims() -> list[tuple[str, ...]]:
    """A claims table that genuinely leaves the page no white space.

    FIVE ENTRIES, NOT THREE, and the difference is `0048`'s. Three entries of six
    two-line claims used to fill the page, because an Entry could take all six of its
    units and spend twelve lines doing it. An Entry is capped at MAX_BULLET_LINES = 6
    lines now, so three of them reach twenty-four and leave room the supporting fill
    would take — which would make both tests below pass for the wrong reason, or fail
    for one that is not about supporting sections at all.

    Filling the page is therefore a matter of ENTRY COUNT rather than of claim depth,
    which is `0048` §2 working as intended: an Entry can no longer monopolise the
    page, so only a bank with more entries than the page has room for can exhaust it.
    """
    return [
        (slug, f"c{n}", type_, ended, "1.00", "2", "a fixture reason")
        for slug, type_, ended in (
            ("helios-payments", "job", "present"),
            ("orbit-analytics", "job", "2018-05"),
            ("atlas-streaming", "job", "2016-04"),
            ("ledger-cli", "project", "2024-06"),
            ("feed-reader", "project", "2023-02"),
        )
        for n in range(1, 7)
    ]


def test_what_did_not_place_loses_visibly(repo_root, run_dir):
    """The Omission view's third subsection — cut by structure, never by the signal.

    A page with no room left over shows every supporting entry the bank holds as a
    loss, with the reason the maker wrote beside it, for the reason the claims half
    lists the zeros: the thing being hunted is a signal that was judged wrong, and
    filtering on the signal hides exactly those.
    """
    (run_dir / "scores.md").write_text(
        scores_md(a_full_page_of_claims(), signals()), encoding="utf-8"
    )

    allocation = pack_ok(repo_root, run_dir)

    lost = section(allocation, "Did not place")
    for slug in SUPPORTING:
        assert slug in lost
    assert "not called by the posting" in lost


def test_the_supporting_line_reports_the_working(repo_root, run_dir):
    """The Silent call that makes the white-space trigger auditable rather than magic."""
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, signals()), encoding="utf-8")

    allocation = pack_ok(repo_root, run_dir)

    line = next(
        one for one in section(allocation, "Silent calls").splitlines()
        if one.startswith("- Supporting:")
    )
    assert "line(s) unspent after the width pass" in line
    assert "The room went to" in line


# --------------------------------------------------------------------------
# The page the Renderer builds
# --------------------------------------------------------------------------


def compose(run_dir: Path, allocation: str, tails: dict[str, str] | None = None) -> None:
    """`bullets.md` against an allocation — the Bullets, the Skills, the rows seated."""
    lines = [
        "## Summary",
        "A backend engineer who builds payment systems and the data work under them.",
        "",
        "## helios-payments",
        "- helios-payments/c1: Cut checkout p99 latency 40% by batching commits in the consumer",
        "- helios-payments/c3: Own the payments ledger end to end, from schema design to review",
        "",
        "## Skills",
        "",
        "### Languages",
        "- Go (helios-payments/c1)",
        "- Rust (ledger-cli/c1)",
        "",
        "### Platform",
        "- Kafka (helios-payments/c1)",
        "- PostgreSQL (helios-payments/c1)",
    ]
    rows = seated(allocation)
    if rows:
        lines += ["", "## Supporting"]
        for _, slug, _ in rows:
            tail = (tails or {}).get(slug)
            lines.append(f"- {slug}/c1: {tail}" if tail else f"- {slug}")
    (run_dir / "bullets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def a_page(repo_root: Path, run_dir: Path, sections_, **compose_kwargs) -> str:
    """Pack both passes over the thin claims, compose against it, and hand it back."""
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, sections_), encoding="utf-8")
    pack_ok(repo_root, run_dir)
    allocation = pack_ok(repo_root, run_dir, "--skills-rows", "1,1")
    compose(run_dir, allocation, **compose_kwargs)
    return allocation


@pytest.mark.needs_pdflatex
def test_a_page_with_supporting_sections_renders_to_one_page(repo_root, run_dir):
    """The whole hand-off, once, through pdflatex — including the marker accounting.

    `check_markers_account_for` runs on every render and fails when the Template's
    markers and `page_elements` name different sets, so a `supporting` marker the
    Renderer could not name would fail here rather than misattributing an overflow.
    """
    a_page(repo_root, run_dir, signals())

    result = render(repo_root, run_dir)

    assert result.returncode == 0, result.stderr
    assert "4 supporting row(s)" in result.stdout
    tex = (run_dir / "resume.tex").read_text(encoding="utf-8")
    assert "\\section{Certifications}" in tex
    assert "\\section{Positions of Responsibility}" in tex
    assert "\\section{Extracurriculars}" in tex
    assert "%% AUTOAPPLY:element:supporting:aws-solutions-architect" in tex


def test_the_row_is_built_from_the_bank_not_composed(repo_root, run_dir):
    """The title, the issuer and the dates come off the frontmatter, never off a tail.

    And a credential whose `started` and `ended` are one month prints that one month
    rather than a range to itself, which is what no expiry looks like (§3).
    """
    a_page(repo_root, run_dir, signals())

    result = render(repo_root, run_dir)
    assert result.returncode == 0, result.stderr
    tex = (run_dir / "resume.tex").read_text(encoding="utf-8")

    assert (
        "\\resumeSupportingRow{AWS Certified Solutions Architect}"
        "{--- Amazon Web Services, Mar 2025}" in tex
    )
    assert "Mar 2025 -- Mar 2025" not in tex
    assert (
        "{--- Training and Placement Cell, Aug 2024 -- May 2025}" in tex
    ), "a post held prints its range"


def test_a_tail_composes_from_the_cited_claim(repo_root, run_dir):
    a_page(
        repo_root,
        run_dir,
        signals(),
        tails={"robotics-society": "Ran the workshops."},
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 0, result.stderr
    tex = (run_dir / "resume.tex").read_text(encoding="utf-8")
    assert "Jun 2024. Ran the workshops.}" in tex


def test_a_tail_that_does_not_trace_fails_the_run(repo_root, run_dir):
    """A supporting row is bound by the Number-trace check exactly as a Bullet is.

    The one that matters most on this element: a credential line reads as fact, so a
    figure invented here is the shape a résumé lies in most easily (§8).
    """
    a_page(
        repo_root,
        run_dir,
        signals(),
        tails={"robotics-society": "Ran 940 sessions."},
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert "940" in result.stderr
    assert "robotics-society/c1" in result.stderr


def test_a_row_that_would_wrap_is_refused(repo_root, run_dir):
    """One typeset line, hard — the cap the section's whole charge rests on (§6)."""
    a_page(
        repo_root,
        run_dir,
        signals(),
        tails={
            "placement-coordinator": (
                "Ran the campus placement drive across six branches and about forty "
                "visiting companies over the year, owning the scheduling calendar that "
                "had been a shared spreadsheet nobody owned before."
            )
        },
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert "a supporting row is one" in result.stderr
    assert "placement-coordinator" in result.stderr


def test_a_row_with_no_seat_is_refused(repo_root, run_dir):
    allocation = a_page(repo_root, run_dir, signals())
    text = (run_dir / "bullets.md").read_text(encoding="utf-8")
    (run_dir / "bullets.md").write_text(text + "- ledger-cli\n", encoding="utf-8")

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert "no seat in allocation.md" in result.stderr


def test_a_seat_with_no_row_is_refused(repo_root, run_dir):
    a_page(repo_root, run_dir, signals())
    text = (run_dir / "bullets.md").read_text(encoding="utf-8")
    (run_dir / "bullets.md").write_text(
        text.replace("- robotics-society\n", ""), encoding="utf-8"
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert "and none was written" in result.stderr


@pytest.mark.parametrize(
    "line, refusal",
    [
        ("- aws-solutions-architect/c1", "reaches no word on the page"),
        ("- aws-solutions-architect: a tail with no citation", "traces to nothing"),
    ],
)
def test_a_row_cites_and_composes_together_or_does_neither(repo_root, run_dir, line, refusal):
    a_page(repo_root, run_dir, signals())
    text = (run_dir / "bullets.md").read_text(encoding="utf-8")
    (run_dir / "bullets.md").write_text(
        text.replace("- aws-solutions-architect\n", line + "\n"), encoding="utf-8"
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert refusal in result.stderr


def test_the_ended_copy_is_checked_against_the_bank(repo_root, run_dir):
    """The seam's own check, one level down from a placed Entry's.

    A supporting entry never reaches the claims table, so `## Sections` is where its
    copy travelled — and the Packer ordered the room it spent on that copy while the
    row prints a date built from the bank.
    """
    rows = [
        (where, slug, "2019-01" if slug == "aws-solutions-architect" else ended, "n", "why")
        for slug, (where, ended) in SUPPORTING.items()
    ]
    a_page(repo_root, run_dir, rows)

    result = render(repo_root, run_dir)

    assert result.returncode == 1
    assert "ended `2019-01`" in result.stderr
    assert "scores.md" in result.stderr


def test_the_supporting_section_is_last_in_bullets_md(repo_root, run_dir):
    """Page order, which is what `bullets.md`'s section order has always meant."""
    a_page(repo_root, run_dir, signals())
    text = (run_dir / "bullets.md").read_text(encoding="utf-8")
    (run_dir / "bullets.md").write_text(
        text.replace("## Supporting", "## Supporting", 1).replace(
            "## Skills", "## Supporting-was-here", 1
        ),
        encoding="utf-8",
    )

    result = render(repo_root, run_dir)

    assert result.returncode == 1


# --------------------------------------------------------------------------
# The seam, and the length pass
# --------------------------------------------------------------------------


def test_the_packer_never_reads_the_bank_for_any_of_this(repo_root, run_dir):
    """A supporting entry crosses the seam in `scores.md` and nowhere else.

    Packing against a `## Sections` table naming entries the bank does not hold still
    works, because the Packer has no way to look — which is what keeps the arithmetic
    on the script's side of the seam.
    """
    rows = [("certifications", "not-in-the-bank", "2025-03", "y", "a fixture reason")]
    (run_dir / "scores.md").write_text(scores_md(THIN_CLAIMS, rows), encoding="utf-8")

    allocation = pack_ok(repo_root, run_dir)

    assert ("certifications", "not-in-the-bank", "the posting's call") in seated(allocation)


def test_the_length_pass_measures_a_supporting_row(repo_root, run_dir):
    """`lengths.py` names an over-long row before a compile is spent on it."""
    a_page(
        repo_root,
        run_dir,
        signals(),
        tails={
            "placement-coordinator": (
                "Ran the campus placement drive across six branches and about forty "
                "visiting companies over the year, owning the scheduling calendar that "
                "had been a shared spreadsheet nobody owned before."
            )
        },
    )

    result = subprocess.run(
        [sys.executable, "tools/lengths.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "supporting row" in result.stdout
    assert "placement-coordinator" in result.stdout


def test_the_coverage_read_sees_a_built_label(repo_root, run_dir):
    """A credential's name is a posting term as often as it is a title.

    Reporting it absent from a page that prints it in bold would be a false lead, and
    the coverage read's whole job is that its lines are leads worth checking.
    """
    a_page(repo_root, run_dir, signals())
    (run_dir / "terms.md").write_text(
        "# Terms\n\n## Must-have\n- AWS Certified Solutions Architect\n", encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, "tools/coverage.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "aws-solutions-architect (supporting label)" in result.stdout
