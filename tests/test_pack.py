"""tools/pack.py, driven as a command over a throwaway run folder.

Every test writes a hand-written `scores.md` into `tmp_path`, runs
`python tools/pack.py <run-dir>`, and asserts on the exit code and on
`allocation.md`. Nothing imports pack.py: the run folder's files are the contract, so
these stay true through any rewrite of the internals.

`config.py` is imported via the `config_module` fixture only to size fixtures against
the real page budget, so a re-calibration changes what these tests build rather than
breaking them. The budget formula is docs/calibration.md's, not one read back out of
pack.py.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from allocation_md import placed, section
from pack_constants import (
    education_rows_charged,
    skills_charge,
)

COLUMNS = ["entry", "claim", "type", "ended", "score", "width", "reason"]
HEADER_ROW = "| " + " | ".join(COLUMNS) + " |"
DELIMITER_ROW = "|" + "---|" * len(COLUMNS)


# --------------------------------------------------------------------------
# Driving the tool
# --------------------------------------------------------------------------


def scores_md(rows: list[tuple[str, ...]]) -> str:
    """A Score table, from `(entry, claim, type, ended, score, width, reason)`.

    A six-cell row is widened with a `width` of `1` — the want almost every claim
    declares — so only the tests that are *about* the width have to say one. A row
    that is short for any other reason is written out as raw text by the test that
    wants it malformed.
    """
    widened = [
        row if len(row) == len(COLUMNS) else (*row[:5], "1", *row[5:]) for row in rows
    ]
    lines = [
        "# Scores: a hand-written fixture",
        "",
        HEADER_ROW,
        DELIMITER_ROW,
        *("| " + " | ".join(row) + " |" for row in widened),
        "",
    ]
    return "\n".join(lines)


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    """A run folder, named the way the maker would name one."""
    folder = tmp_path / "acme-backend-engineer"
    folder.mkdir()
    return folder


def write_scores(run_dir: Path, rows: list[tuple[str, ...]]) -> None:
    (run_dir / "scores.md").write_text(scores_md(rows), encoding="utf-8")


def pack(repo_root: Path, run_dir: Path, *flags: str) -> subprocess.CompletedProcess:
    #: THE CAPS ARE LIFTED UNLESS A TEST IS ABOUT THEM. `0051` caps a real page at
    #: three jobs and two projects, and most fixtures here build five to eleven
    #: entries to exercise the Entry floor, the sharing rule and the tie band. Left
    #: at their defaults every one of those would be testing the cap instead of the
    #: thing it was written for. A test that IS about the cap passes its own.
    if not any(flag.startswith("--max-") for flag in flags):
        flags = (*flags, "--max-experience", "11", "--max-projects", "11")
    return subprocess.run(
        [sys.executable, "tools/pack.py", str(run_dir), *flags],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def pack_ok(repo_root: Path, run_dir: Path, *flags: str) -> str:
    """Run the Packer, insist it succeeded, and hand back `allocation.md`.

    No flags is pass one — the reservation. Every test that is not *about* the
    second pass drives pass one, because that is the budget the Bullets are
    composed against.
    """
    result = pack(repo_root, run_dir, *flags)
    assert result.returncode == 0, f"pack.py failed: {result.stderr}"
    return (run_dir / "allocation.md").read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Reading allocation.md back — this is the contract render.py will parse
# --------------------------------------------------------------------------


def placed_slugs(allocation: str) -> list[str]:
    return [slug for slug, _ in placed(allocation)]


def bullets_of(allocation: str, slug: str) -> list[str]:
    found = [claims for entry, claims in placed(allocation) if entry == slug]
    assert len(found) <= 1, f"{slug} appears {len(found)} times in Placed"
    return found[0] if found else []


def lines_of(body: str) -> list[str]:
    return [line for line in body.splitlines() if line.startswith("- ")]


def silent_calls(allocation: str) -> list[str]:
    return lines_of(section(allocation, "Silent calls"))


def omitted(allocation: str) -> str:
    return section(allocation, "Did not place")


def omitted_entries(allocation: str) -> list[str]:
    body = omitted(allocation)
    match = re.search(r"^### Entries\n(.*?)(?=^### |\Z)", body, re.M | re.S)
    return lines_of(match.group(1)) if match else []


def omitted_claims(allocation: str) -> list[str]:
    body = omitted(allocation)
    match = re.search(r"^### Claims\n(.*?)(?=^### |\Z)", body, re.M | re.S)
    return lines_of(match.group(1)) if match else []


def entry_score(allocation: str, slug: str) -> str:
    match = re.search(
        rf"^### {re.escape(slug)} .*?entry score (\d\.\d\d)", allocation, re.M
    )
    assert match, f"{slug} has no entry score in Placed:\n{allocation}"
    return match.group(1)


def line_naming(lines: list[str], *needles: str) -> str:
    """The single line mentioning all of `needles` — asserts there is exactly one."""
    hits = [line for line in lines if all(needle in line for needle in needles)]
    assert len(hits) == 1, f"expected one line naming {needles}, got {hits}\n{lines}"
    return hits[0]


# --------------------------------------------------------------------------
# The page budget, per docs/calibration.md
# --------------------------------------------------------------------------


def bullet_budget(
    config,
    *,
    jobs: bool,
    projects: bool,
    education_rows: int | None = None,
    skills_rows: list[int] | None = None,
) -> int:
    """Lines left for Entry headers and Bullets once the fixed overhead is paid.

    The formula is docs/calibration.md's, written out here so these tests size
    themselves against a re-calibration instead of hard-coding today's constants.
    `education_rows` defaults to what the Packer charges with no profile beside the
    run, which is every fixture run folder here (`pack_constants`).

    `skills_rows` defaults to `None`, which is pass one: the reservation. The
    Skills section carries its own `\\section` heading inside `skills_charge`,
    since whether it has one is a fact about what was composed.

    The Summary carries one too, and unconditionally — hence the flat
    `SECTION_LINES` outside the `sections` count
    (`docs/adr/0044-the-page-opens-on-a-summary.md`, Addendum).
    """
    if education_rows is None:
        education_rows = education_rows_charged()
    sections = int(jobs) + int(projects) + int(education_rows > 0)
    overhead = (
        config.HEADER_LINES
        + config.SUMMARY_LINES
        + config.SECTION_LINES  # \section{Summary}, on every page
        + sections * config.SECTION_LINES
        + education_rows * config.ENTRY_HEADER_LINES
        + skills_charge(config, skills_rows)
    )
    return config.PAGE_LINES - overhead


def entry_rows(
    slug: str,
    scores: list[str],
    *,
    type_: str = "job",
    ended: str = "2024-06",
    reason: str | None = None,
) -> list[tuple[str, ...]]:
    """One entry's rows, its claims numbered c1.. in the order given."""
    return [
        (
            slug,
            f"c{i + 1}",
            type_,
            ended,
            score,
            reason or f"{slug} c{i + 1} scored {score}",
        )
        for i, score in enumerate(scores)
    ]


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def test_an_entry_places_with_its_claims_in_score_order(repo_root, run_dir):
    write_scores(run_dir, entry_rows("acme-platform", ["0.60", "0.90", "0.75"]))

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["acme-platform"]
    assert bullets_of(allocation, "acme-platform") == ["c2", "c3", "c1"]


def test_a_reason_carrying_an_escaped_pipe_survives_parsing(repo_root, run_dir):
    write_scores(
        run_dir,
        [("acme-platform", "c1", "job", "2024-06", "0.90", r"Kafka \| Postgres, both")],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert "Kafka | Postgres, both" in allocation


# --- Malformed input: a hard failure that names the row, never a skipped line ---


def test_a_missing_score_table_fails(repo_root, run_dir):
    (run_dir / "scores.md").write_text("# Scores\n\nNothing scored yet.\n", encoding="utf-8")

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert not (run_dir / "allocation.md").exists()


def test_a_missing_scores_file_fails(repo_root, run_dir):
    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "scores.md" in result.stderr


def test_a_short_row_fails_and_names_it(repo_root, run_dir):
    run_dir.joinpath("scores.md").write_text(
        "\n".join(
            [
                HEADER_ROW,
                DELIMITER_ROW,
                "| acme-platform | c1 | job | 2024-06 | 0.90 | 1 | fine |",
                "| beta-shop | c1 | job | 2023-01 | 0.40 | 1 |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "beta-shop" in result.stderr
    assert "row 4" in result.stderr
    assert not (run_dir / "allocation.md").exists(), "a bad row must stop the run, not be skipped"


def test_a_duplicate_entry_claim_pair_fails_and_names_both_rows(repo_root, run_dir):
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "first"),
            ("acme-platform", "c2", "job", "2024-06", "0.80", "second"),
            ("acme-platform", "c1", "job", "2024-06", "0.10", "and again"),
        ],
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "acme-platform/c1" in result.stderr
    assert "row 7" in result.stderr and "row 5" in result.stderr


@pytest.mark.parametrize(
    "bad_row",
    [
        pytest.param(("acme-platform", "c1", "job", "2024-06", "1.20", "over"), id="above-one"),
        pytest.param(("acme-platform", "c1", "job", "2024-06", "0.9", "one dp"), id="one-decimal"),
        pytest.param(("acme-platform", "c1", "job", "2024-06", "high", "words"), id="not-a-number"),
        pytest.param(("acme-platform", "c1", "side", "2024-06", "0.90", "?"), id="bad-type"),
        pytest.param(("acme-platform", "c1", "job", "June 2024", "0.90", "?"), id="bad-ended"),
        pytest.param(("acme-platform", "1", "job", "2024-06", "0.90", "?"), id="bad-claim-id"),
        pytest.param(("acme-platform", "c1", "job", "2024-06", "0.90", ""), id="empty-reason"),
        pytest.param(
            ("acme-platform", "c1", "job", "2024-06", "0.90", "3", "three lines"),
            id="width-past-the-cap",
        ),
        pytest.param(
            ("acme-platform", "c1", "job", "2024-06", "0.90", "0", "no lines"),
            id="width-zero",
        ),
        pytest.param(
            ("acme-platform", "c1", "job", "2024-06", "0.90", "wide", "words"),
            id="width-not-a-number",
        ),
    ],
)
def test_an_unparseable_cell_fails_and_names_the_row(repo_root, run_dir, bad_row):
    write_scores(
        run_dir,
        [("beta-shop", "c1", "job", "2023-01", "0.70", "a good row above it"), bad_row],
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "row 6" in result.stderr, result.stderr
    assert not (run_dir / "allocation.md").exists()


def test_pack_py_is_stdlib_only_and_never_reads_the_bank(repo_root):
    """The Packer's bank-blindness, enforced in the code rather than merely stated.

    It is what keeps the bank pure prose: nothing downstream of the Score table may
    look at an Entry file, so `bank.py` — and any third-party parser — must not be
    reachable from here.
    """
    import ast

    source = (repo_root / "tools" / "pack.py").read_text(encoding="utf-8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])

    assert "bank" not in imported, "pack.py must never reach the bank"
    outside_stdlib = imported - sys.stdlib_module_names - {"config"}
    assert not outside_stdlib, f"pack.py must be stdlib-only, but imports {outside_stdlib}"


def test_one_entry_declaring_two_types_fails(repo_root, run_dir):
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "as a job"),
            ("acme-platform", "c2", "project", "2024-06", "0.80", "as a project"),
        ],
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "acme-platform" in result.stderr


# --- Rollup and ordering ---


def test_entry_score_is_the_mean_of_the_top_three_claims(repo_root, run_dir):
    """A fourth, weak claim cannot drag an entry down — it is ranked on its best three."""
    write_scores(
        run_dir,
        entry_rows("acme-platform", ["0.90", "0.80", "0.70", "0.00"], ended="2024-06")
        + entry_rows("beta-shop", ["0.85", "0.75", "0.70"], ended="2023-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert entry_score(allocation, "acme-platform") == "0.80"  # (0.90+0.80+0.70)/3
    assert entry_score(allocation, "beta-shop") == "0.77"  # (0.85+0.75+0.70)/3
    assert placed_slugs(allocation) == ["acme-platform", "beta-shop"]


def test_the_ranking_window_stays_at_three_when_the_block_holds_six(repo_root, run_dir):
    """Six qualifying claims, and the entry is still ranked on its best three.

    The window did not follow `MAX_BULLETS` to six. A mean over six would be the
    entry's *average* quality: here it would rank `deep-shop` at 0.75 and put
    `flat-shop` above it, on the strength of having written fewer claims.
    """
    write_scores(
        run_dir,
        entry_rows(
            "deep-shop", ["0.90", "0.90", "0.90", "0.60", "0.60", "0.60"], ended="2024-06"
        )
        + entry_rows("flat-shop", ["0.80", "0.80", "0.80"], ended="2023-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert entry_score(allocation, "deep-shop") == "0.90"
    assert entry_score(allocation, "flat-shop") == "0.80"
    assert placed_slugs(allocation) == ["deep-shop", "flat-shop"]


def test_adding_an_honest_claim_never_demotes_the_entry_that_owns_it(repo_root, run_dir):
    """The incentive the three-wide window exists to protect.

    The other half of this system is a skill whose whole job is to add claims, so a
    ranking that falls when one is added is a ranking pointed the wrong way.
    """
    write_scores(run_dir, entry_rows("orbit-analytics", ["0.90", "0.90", "0.90"]))
    thin = entry_score(pack_ok(repo_root, run_dir), "orbit-analytics")

    write_scores(run_dir, entry_rows("orbit-analytics", ["0.90", "0.90", "0.90", "0.55"]))
    thick = entry_score(pack_ok(repo_root, run_dir), "orbit-analytics")

    assert thick == thin == "0.90"


def test_a_claim_below_the_floor_counts_toward_neither_the_page_nor_the_rank(
    repo_root, run_dir
):
    """The window reads the same set as the slots — claims that could take a Bullet.

    `0.90 / 0.20 / 0.20` used to rank at 0.43 on the strength of two claims that can
    never appear on any page at any cap.
    """
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.20", "0.20"]))

    allocation = pack_ok(repo_root, run_dir)

    assert entry_score(allocation, "acme-platform") == "0.90"
    assert bullets_of(allocation, "acme-platform") == ["c1"]


def test_an_entry_with_fewer_than_three_claims_is_not_padded_with_zeros(repo_root, run_dir):
    """One 0.90 claim means 0.90, not 0.30 — padding would rank it on claims it never wrote."""
    write_scores(
        run_dir,
        entry_rows("solo-runway", ["0.90"], ended="2022-01")
        + entry_rows("broad-shop", ["0.80", "0.80", "0.80"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert entry_score(allocation, "solo-runway") == "0.90"
    assert placed_slugs(allocation) == ["solo-runway", "broad-shop"]


def test_a_gap_under_epsilon_is_a_tie_broken_by_recency(repo_root, run_dir):
    """0.85 vs 0.83 is second-decimal noise, so the more recent entry leads."""
    write_scores(
        run_dir,
        entry_rows("older-but-better", ["0.85", "0.85", "0.85"], ended="2021-03")
        + entry_rows("newer-and-close", ["0.83", "0.83", "0.83"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["newer-and-close", "older-but-better"]


def test_a_gap_of_exactly_epsilon_is_not_a_tie(repo_root, run_dir):
    """0.05 is the band's edge and sits outside it, so raw score order stands."""
    write_scores(
        run_dir,
        entry_rows("older-but-better", ["0.85", "0.85", "0.85"], ended="2021-03")
        + entry_rows("newer-but-lower", ["0.80", "0.80", "0.80"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["older-but-better", "newer-but-lower"]


def test_a_tie_at_the_same_recency_is_broken_by_entry_id(repo_root, run_dir):
    write_scores(
        run_dir,
        entry_rows("zeta-tools", ["0.84", "0.84", "0.84"], ended="2024-06")
        + entry_rows("alpha-works", ["0.82", "0.82", "0.82"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["alpha-works", "zeta-tools"]


def test_present_outranks_every_dated_entry_inside_a_tie(repo_root, run_dir):
    write_scores(
        run_dir,
        entry_rows("last-year", ["0.85", "0.85", "0.85"], ended="2025-12")
        + entry_rows("still-there", ["0.82", "0.82", "0.82"], ended="present"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["still-there", "last-year"]


def test_every_tie_broken_by_rule_is_logged_with_its_reason(repo_root, run_dir):
    write_scores(
        run_dir,
        entry_rows("older-but-better", ["0.85", "0.85", "0.85"], ended="2021-03")
        + entry_rows("newer-and-close", ["0.83", "0.83", "0.83"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    logged = line_naming(silent_calls(allocation), "tie", "newer-and-close", "older-but-better")
    assert "0.85" in logged and "0.83" in logged
    assert "2024-06" in logged, "the reason has to say what broke the tie"


# --- Slots: min(6, claims >= 0.50) ---


def test_eight_claims_above_the_floor_still_get_six_bullets(repo_root, run_dir):
    write_scores(
        run_dir,
        entry_rows(
            "acme-platform",
            ["0.90", "0.85", "0.80", "0.75", "0.70", "0.65", "0.60", "0.55"],
        ),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1", "c2", "c3", "c4", "c5", "c6"]


def test_five_claims_above_the_floor_get_five_bullets(repo_root, run_dir):
    """The cap is six, so five qualifying claims are five Bullets, not three.

    This is the complaint that opened #47, as a test: at a cap of three, eight
    qualifying claims were dropped onto a page with twelve idle lines.
    """
    write_scores(
        run_dir, entry_rows("acme-platform", ["0.90", "0.85", "0.80", "0.75", "0.70"])
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1", "c2", "c3", "c4", "c5"]


def test_one_claim_above_the_floor_gets_one_bullet_on_an_empty_page(repo_root, run_dir):
    """Free space never pads an entry to a quota — the floor is absolute."""
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.49", "0.49"]))

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1"]


def test_a_claim_exactly_at_the_floor_takes_a_slot(repo_root, run_dir):
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.50", "0.49"]))

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1", "c2"]


def test_an_entry_with_no_claim_above_the_floor_does_not_place(repo_root, run_dir):
    write_scores(
        run_dir,
        entry_rows("acme-platform", ["0.90", "0.80", "0.70"])
        + entry_rows("thin-shop", ["0.40", "0.30"], ended="2023-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["acme-platform"]


# --- Packing: the Entry floor, top-first depth, and the ceiling ---


def entry_ceiling(
    config, *, jobs: bool, projects: bool, leads: bool = False, project_entries: int = 0
) -> int:
    """How many Entries a page seats at their reserved minimum block.

    `PAGE_LINES // (ENTRY_HEADER_LINES + 1)`, less the fixed overhead — derived, and
    deliberately not a constant anywhere. Below it the **Entry floor** means nothing
    that qualifies falls off the page; at it, the reservation queue decides who is
    cut, and that is the only case where the queue's order is observable.

    `leads` says the entries each declare one, which is what a real page's usually do:
    the reserved block is then `ENTRY_HEADER_LINES + LEAD_LINES + 1`, so the page
    seats fewer of them (`docs/adr/0035-the-lead-crosses-the-seam.md` §3).

    `project_entries` is how many of the seated Entries are projects, whose one-row
    header is `ENTRY_HEADER_LINES - PROJECT_HEADER_LINES` cheaper
    (`docs/adr/0057-the-page-reads-like-a-resume.md` §3) — what they save is room
    for more of the rest.
    """
    lead_lines = config.LEAD_LINES if leads else 0
    saved = project_entries * (config.ENTRY_HEADER_LINES - config.PROJECT_HEADER_LINES)
    return (bullet_budget(config, jobs=jobs, projects=projects) + saved) // (
        config.ENTRY_HEADER_LINES + lead_lines + 1
    )


def ladder(
    config,
    count: int,
    *,
    claims_each: int = 1,
    type_of=None,
) -> tuple[list[tuple[str, ...]], list[str]]:
    """`count` entries in strict score order, every claim of a rung above the floor.

    Scores step down by exactly ε, which is *outside* the tie band, so the order is
    an ordering rather than a tie; `ended` descends with the score so recency never
    fights it. Returns the rows and the slugs in score order.

    Eleven rungs is the most this can build: 1.00 down to 0.50 in ε steps, and a
    twelfth would fall under the **Bullet floor** and stop qualifying at all.

    """
    rows: list[tuple[str, ...]] = []
    slugs: list[str] = []
    for index in range(count):
        score = (100 - 5 * index) / 100
        assert score >= 0.50, (
            f"rung {index + 1} scores {score:.2f}, under the bullet floor — this "
            "ladder cannot build more than eleven qualifying entries"
        )
        slug = f"rung-{index + 1:02d}"
        slugs.append(slug)
        rows += entry_rows(
            slug,
            [f"{score:.2f}"] * claims_each,
            type_=type_of(index) if type_of else "job",
            ended=f"{2030 - index:04d}-06",
        )
    return rows, slugs


def lines_spent(config, allocation: str) -> int:
    return sum(
        config.ENTRY_HEADER_LINES + len(claims) for _, claims in placed(allocation)
    )


def sizes_of(allocation: str) -> list[int]:
    """Bullets per placed entry, in the allocation's page order."""
    return [len(claims) for _, claims in placed(allocation)]


def test_every_qualifying_entry_is_reserved_a_block(repo_root, run_dir, config_module):
    """Crossing the Bullet floor buys presence. Nothing that qualifies falls off.

    A page that seats *n* entries seats all *n* of them even when every one of them
    wants six Bullets and the page has nothing like the room — what they compete for
    is width, never whether they appear.
    """
    ceiling = entry_ceiling(config_module, jobs=True, projects=False)
    rows, slugs = ladder(config_module, ceiling, claims_each=6)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == slugs
    assert all(size >= 1 for size in sizes_of(allocation))
    assert omitted_entries(allocation) == []


def test_the_remainder_goes_top_first_and_a_deep_entry_keeps_its_six(
    repo_root, run_dir, config_module
):
    """The floor buys presence; score buys depth.

    Five entries each wanting six on a page that cannot give thirty: the top takes
    its fill before the next is offered anything, so the strongest evidence is
    untouched and the shortfall lands at the bottom.
    """
    rows, slugs = ladder(config_module, 5, claims_each=6)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    sizes = sizes_of(allocation)
    assert placed_slugs(allocation) == slugs
    assert sizes[0] == 6, "the top entry did not keep its six"
    assert sizes == sorted(sizes, reverse=True), "depth went out of score order"
    assert sizes[-1] < 6, "this fixture is meant to run the page short"
    assert lines_spent(config_module, allocation) <= bullet_budget(
        config_module, jobs=True, projects=False
    )


def test_an_entry_short_of_lines_keeps_its_best_claims(repo_root, run_dir, config_module):
    """A shrunk entry drops its OWN lowest Bullet, and says which one it dropped."""
    rows, _ = ladder(config_module, 5, claims_each=6)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    for slug, claims in placed(allocation):
        assert claims == [f"c{n}" for n in range(1, len(claims) + 1)], (
            f"{slug} kept something other than its best claims: {claims}"
        )
        for dropped in range(len(claims) + 1, 7):
            logged = line_naming(silent_calls(allocation), "shrink", f"{slug}/c{dropped}")
            assert "line" in logged, f"a shrink has to say what ran out: {logged}"


def test_past_the_ceiling_the_lowest_scoring_entry_is_cut_and_logged(
    repo_root, run_dir, config_module
):
    """Above the ceiling the guarantee breaks, and it breaks lowest-score-first.

    Every entry here declares a lead, which is what a real page's do and what keeps
    this fixture buildable: a lead raises the reserved block from 3 lines to 4, and
    the ladder can only climb eleven rungs — 1.00 down to the 0.50 Bullet floor in ε
    steps. Without the leads a 53-line page seats eleven entries and the twelfth this
    test needs does not exist to be cut.
    """
    ceiling = entry_ceiling(
        config_module, jobs=True, projects=True, leads=True, project_entries=1
    )
    rows, slugs = ladder(
        config_module,
        ceiling + 1,
        type_of=lambda index: "project" if index == 0 else "job",
    )
    (run_dir / "scores.md").write_text(
        with_tables(rows, leads_table([(slug, "y") for slug in slugs])), encoding="utf-8"
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == sorted(slugs[:-1]) or set(
        placed_slugs(allocation)
    ) == set(slugs[:-1])
    assert not bullets_of(allocation, slugs[-1])
    logged = line_naming(silent_calls(allocation), "page full", slugs[-1])
    assert "reserve" in logged, f"the cut has to say what there was no room for: {logged}"


def test_the_top_of_the_page_never_funds_the_bottom_entry_presence(
    repo_root, run_dir, config_module
):
    """The guarantee is paid from the bottom of the placed set upward.

    Adding a weak entry to the bottom of the bank must not cost the strongest entry a
    Bullet — that is the property top-first buys over round-robin, and the reason a
    deep entry keeps its six.
    """
    rows, _ = ladder(config_module, 4, claims_each=6)
    write_scores(run_dir, rows)
    before = sizes_of(pack_ok(repo_root, run_dir))

    rows += entry_rows("weak-tail", ["0.50"], ended="2015-06")
    write_scores(run_dir, rows)
    after = sizes_of(pack_ok(repo_root, run_dir))

    assert after[0] == before[0], "the top entry paid for the weak entry's presence"
    assert after[-1] == 1, "the weak entry placed at its reserved line"


# --- The Experience floor: the head of the reservation queue ---


def test_the_two_most_recent_jobs_are_reserved_before_higher_scoring_projects(
    repo_root, run_dir, config_module
):
    """Only observable above the ceiling — below it everything is reserved anyway.

    So the fixture is one entry past what the page seats: eight projects outscoring
    three jobs, and the entry that gets cut is the one job the head does not name.
    The projects each declare a lead, which brings their one-row header's block back
    to a job's three lines, so the page's ceiling is one number for every Entry.
    """
    ceiling = entry_ceiling(config_module, jobs=True, projects=True)
    projects, project_slugs = ladder(
        config_module, ceiling - 2, type_of=lambda _index: "project"
    )
    jobs = (
        entry_rows("newest-job", ["0.60"], ended="2031-06")
        + entry_rows("middle-job", ["0.55"], ended="2030-12")
        + entry_rows("oldest-job", ["0.50"], ended="2029-12")
    )
    (run_dir / "scores.md").write_text(
        with_tables(
            projects + jobs,
            leads_table(
                [(slug, "y") for slug in project_slugs]
                + [(slug, "n") for slug in ("newest-job", "middle-job", "oldest-job")]
            ),
        ),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "newest-job") == ["c1"]
    assert bullets_of(allocation, "middle-job") == ["c1"]
    assert not bullets_of(allocation, "oldest-job"), "the head names two jobs, not three"
    assert all(bullets_of(allocation, slug) for slug in project_slugs)


def test_the_experience_floor_never_pads_a_job_below_the_bullet_floor(
    repo_root, run_dir, config_module
):
    """The 0.50 floor is absolute, and the head passes to the next qualifying job.

    A job with nothing above the floor cannot be padded into a Bullet — the floor
    exists to stop an *empty* Experience section, and padding would trade the
    emptiness for something worse.
    """
    ceiling = entry_ceiling(config_module, jobs=True, projects=True)
    projects, project_slugs = ladder(
        config_module, ceiling - 2, type_of=lambda _index: "project"
    )
    jobs = (
        entry_rows("nothing-to-say", ["0.40", "0.30"], ended="2031-06")
        + entry_rows("middle-job", ["0.55"], ended="2030-12")
        + entry_rows("oldest-job", ["0.50"], ended="2029-12")
    )
    write_scores(run_dir, projects + jobs)

    allocation = pack_ok(repo_root, run_dir)

    assert not bullets_of(allocation, "nothing-to-say")
    assert bullets_of(allocation, "middle-job") == ["c1"]
    assert bullets_of(allocation, "oldest-job") == ["c1"]
    assert all(bullets_of(allocation, slug) for slug in project_slugs)


# --- The Share line: how the page was shared out, on every run ---


def test_the_share_line_is_written_on_every_run(repo_root, run_dir):
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.80"]))

    allocation = pack_ok(repo_root, run_dir)

    share = line_naming(silent_calls(allocation), "Share:")
    assert "reserved 1" in share
    assert "acme-platform +1" in share
    assert "no entry placed at its reserved line only" in share


def test_the_share_line_names_every_entry_left_at_its_reserved_line(
    repo_root, run_dir, config_module
):
    """The signal that the bank has outgrown the page, and the reason it is always on."""
    ceiling = entry_ceiling(config_module, jobs=True, projects=False)
    rows, _ = ladder(config_module, ceiling, claims_each=6)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    share = line_naming(silent_calls(allocation), "Share:")
    stubs = [slug for slug, claims in placed(allocation) if len(claims) == 1]
    assert stubs, "this fixture is meant to leave the page full of reserved lines"
    assert "placed at their reserved line only" in share
    for slug in stubs:
        assert slug in share


# --- The width pass: evidence outranks room ---


def a_page_spending(
    config, lines: int, *, asking: int = 0
) -> tuple[list[tuple[str, ...]], list[str]]:
    """Rows that seat exactly `lines` of the Bullet budget, `asking` of them wide.

    Entries of six Bullets — the slot cap — until the last one, which carries what
    is left over. Every block is legal and the whole thing fits, so `pack_page`
    seats every claim written and the residue handed to the width pass is
    `budget - lines` exactly. That is what lets these tests name a number instead
    of re-deriving one from the allocation they are checking.

    The `asking` lowest-scoring claims are the ones declaring `width: 2`. Returns
    the rows, and those claims' refs in grant order — highest score first, so the
    last of them is the first to be refused.
    """
    counts: list[int] = []
    block = config.ENTRY_HEADER_LINES
    left = lines
    while left:
        assert left >= block + 1, f"{lines} lines do not divide into legal blocks"
        take = min(6, left - block)
        # Whatever this block leaves has to be nothing at all or a legal block of
        # its own — a header and one Bullet. Shrink this one by the shortfall, and
        # if that would take it under a Bullet, swallow the remainder instead. The
        # old form shrank by exactly one and worked only for the totals the budget
        # happened to produce; it stopped dividing the day SUMMARY_LINES came off
        # the top (docs/adr/0044-the-page-opens-on-a-summary.md §5).
        remainder = left - take - block
        if 0 < remainder < block + 1:
            take = max(1, take - (block + 1 - remainder))
            take = min(take, left - block)
        counts.append(take)
        left -= take + block
    rows: list[tuple[str, ...]] = []
    for index, count in enumerate(counts):
        rows += entry_rows(
            f"rung-{index + 1:02d}",
            [f"{(100 - 5 * index) / 100:.2f}"] * count,
            ended=f"{2030 - index:04d}-06",
        )
    wide = range(len(rows) - asking, len(rows))
    return [
        (*row[:5], "2", *row[5:]) if index in wide else row
        for index, row in enumerate(rows)
    ], [f"{rows[index][0]}/{rows[index][1]}" for index in wide]


def test_a_granted_width_rides_on_the_claim_line(repo_root, run_dir):
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "2", "wants the room"),
            ("acme-platform", "c2", "job", "2024-06", "0.80", "1", "says it in one"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert "- acme-platform/c1 — 0.90 — 2 lines — wants the room" in allocation
    assert "- acme-platform/c2 — 0.80 — 1 line — says it in one" in allocation


def test_the_width_is_written_on_every_claim_wide_or_not(repo_root, run_dir):
    """A field always present is one a reader cannot misread as defaulted."""
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.80", "0.70"]))

    allocation = pack_ok(repo_root, run_dir)

    for line in lines_of(section(allocation, "Placed")):
        assert re.match(r"^- \S+/c\d+ — \d\.\d\d — [12] lines? — ", line), line


def test_a_declared_width_is_charged_not_granted(repo_root, run_dir):
    """`0047` §3: the width column is a charge the Packer honours, not a want.

    Three claims that all declare two lines all GET two lines on a page with room
    for them, and nothing decides between them. Under `0025` §6 the same table
    seated all three at one line and then bought the second lines back out of the
    residue in claim-score order — which is what the deleted assertion here used to
    pin (`c2, c3, c1`, score order and not table order).
    """
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.70", "2", "third by score"),
            ("acme-platform", "c2", "job", "2024-06", "0.90", "2", "first by score"),
            ("acme-platform", "c3", "job", "2024-06", "0.80", "2", "second by score"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    bullets = [line for line in lines_of(section(allocation, "Placed")) if line.startswith("- ")]
    assert len(bullets) == 3
    assert all(" — 2 lines — " in line for line in bullets), bullets


def test_a_seated_claim_is_never_written_to_less_than_it_declared(
    repo_root, run_dir, config_module
):
    """`0025`'s invariant, restated for a charged width — and it still holds.

    It used to hold because widths were granted AFTER placement: a want could be
    refused, but a slot already seated was never taken away. It holds now for the
    opposite reason — the width is part of what a unit costs to place at all, so a
    unit the page cannot seat at its declared width is leapfrogged before it is ever
    seated. Either way, no line on the page is a sentence squeezed out of the room
    it was written for, which under `0047` matters more than it did: an XYZ sentence
    written to one line has lost a slot of the formula, not a decoration.
    """
    rows, _ = ladder(config_module, 5, claims_each=6)
    write_scores(run_dir, [(*row[:5], "2", *row[5:]) for row in rows])

    allocation = pack_ok(repo_root, run_dir)

    bullets = [line for line in lines_of(section(allocation, "Placed")) if line.startswith("- ")]
    assert all(" — 2 lines — " in line for line in bullets), bullets
    assert lines_spent(config_module, allocation) <= bullet_budget(
        config_module, jobs=True, projects=False
    ), "the page spent lines it did not have"


def test_a_width_the_page_cannot_afford_drops_the_unit(
    repo_root, run_dir, config_module
):
    """A width is no longer refusable — the unit it belongs to is what gives way.

    Under `0025` §6 the lowest-scoring asker kept its slot and was written to one
    line, and `Room:` named it. There is no such state now: `pack_page` leapfrogs
    the unit it cannot seat at full width, and the Omission view is where it turns
    up instead. Same evidence lost, reported in a different place.
    """
    rows, _ = ladder(config_module, 5, claims_each=6)
    write_scores(run_dir, rows)
    narrow = placed(pack_ok(repo_root, run_dir))

    write_scores(run_dir, [(*row[:5], "2", *row[5:]) for row in rows])
    allocation = pack_ok(repo_root, run_dir)

    assert "shrink:" in allocation, "a page of two-line claims must run out and say so"
    bullets = sum(len(claims) for _, claims in placed(allocation))
    assert bullets < sum(len(claims) for _, claims in narrow), (
        "doubling every width must cost the page evidence"
    )


def test_the_room_line_is_written_even_when_nothing_was_left(repo_root, run_dir):
    """Its absence must never have to be interpreted (`0025` §7)."""
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.80"]))

    allocation = pack_ok(repo_root, run_dir)

    room = line_naming(silent_calls(allocation), "Room:")
    assert "every one of them charged its declared width" in room
    assert "line(s) unspent" in room


def test_the_room_line_and_the_budget_header_subtract(
    repo_root, run_dir, config_module
):
    """The defect this pins: a reader does the arithmetic and it comes out.

    `Room:`'s residue is what the header says is left, and — since `0047` §3 left
    nothing to grant between the two — the unspent tail is the same number a third
    time. Nothing else in the suite holds them to each other.
    """
    budget = bullet_budget(config_module, jobs=True, projects=False)
    rows, _ = a_page_spending(config_module, budget - 7, asking=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    left = int(re.search(r"Spent \d+, (\d+) left\.", allocation).group(1))
    room = line_naming(silent_calls(allocation), "Room:")
    residue = int(re.search(r"Room: (\d+) line", room).group(1))
    unspent = int(re.search(r"(\d+) line\(s\) unspent", room).group(1))

    assert residue == unspent == left


def test_a_full_page_leaves_nothing_for_the_supporting_sections(
    repo_root, run_dir, config_module
):
    """The bill stated plainly: a full page has no white space to answer with."""
    budget = bullet_budget(config_module, jobs=True, projects=False)
    rows, _ = a_page_spending(config_module, budget, asking=0)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    room = line_naming(silent_calls(allocation), "Room:")
    assert "Room: 0 line(s) left after the Bullets were seated" in room
    assert "0 line(s) unspent" in room


def test_a_two_line_slot_is_charged_two_lines_of_page(repo_root, run_dir, config_module):
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.80"]))
    narrow = pack_ok(repo_root, run_dir)

    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "2", "wide"),
            ("acme-platform", "c2", "job", "2024-06", "0.80", "1", "narrow"),
        ],
    )
    wide = pack_ok(repo_root, run_dir)

    spent = lambda text: int(re.search(r"Spent (\d+),", text).group(1))
    assert spent(wide) == spent(narrow) + 1


# --- The Omission view ---


def test_a_non_placing_entry_says_there_was_no_room_to_reserve_a_block(
    repo_root, run_dir, config_module
):
    ceiling = entry_ceiling(config_module, jobs=True, projects=True)
    rows, slugs = ladder(
        config_module,
        ceiling,
        type_of=lambda index: "project" if index == 0 else "job",
    )
    rows += entry_rows(
        "lost-cause",
        ["0.50", "0.20"],
        ended="2019-01",
        reason="Kafka here was ops-only; the JD wants stream-processing design",
    )
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    assert not bullets_of(allocation, "lost-cause")
    line = line_naming(omitted_entries(allocation), "lost-cause")
    assert "0.50" in line, "the entry score belongs on the line"
    assert "no room to reserve a block" in line, "the structural reason"
    assert f"seated {len(placed(allocation))} entries" in line
    assert "Kafka here was ops-only" in line, "the best claim's reason, carried verbatim"


def test_an_entry_with_nothing_above_the_floor_says_so_on_its_own_line(
    repo_root, run_dir
):
    """The other way an Entry loses, and it is not a shortage of page."""
    write_scores(
        run_dir,
        entry_rows("acme-platform", ["0.90"])
        + entry_rows("thin-shop", ["0.40", "0.30"], ended="2023-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    line = line_naming(omitted_entries(allocation), "thin-shop")
    assert "no claim at or above the 0.50 bullet floor" in line
    assert "no room" not in line, "the page had all the room in the world"


def test_a_claim_that_lost_a_slot_inside_a_placed_entry_is_named_with_its_reason(
    repo_root, run_dir
):
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "the best one"),
            ("acme-platform", "c2", "job", "2024-06", "0.85", "second"),
            ("acme-platform", "c3", "job", "2024-06", "0.80", "third"),
            ("acme-platform", "c4", "job", "2024-06", "0.75", "fourth"),
            ("acme-platform", "c5", "job", "2024-06", "0.70", "fifth"),
            ("acme-platform", "c6", "job", "2024-06", "0.65", "sixth"),
            ("acme-platform", "c7", "job", "2024-06", "0.60", "over the cap"),
            ("acme-platform", "c8", "job", "2024-06", "0.40", "under the floor"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1", "c2", "c3", "c4", "c5", "c6"]
    capped = line_naming(omitted_claims(allocation), "acme-platform/c7")
    assert "over the cap" in capped and "0.60" in capped
    assert "6-unit cap" in capped, "the reason follows the cap (docs/adr/0037 §6)"
    floored = line_naming(omitted_claims(allocation), "acme-platform/c8")
    assert "under the floor" in floored
    assert "0.50" in floored, "a claim below the floor should say which floor"
    assert capped != floored


def test_a_bullet_lost_to_a_shrink_is_named_in_the_omission_view(
    repo_root, run_dir, config_module
):
    rows, _ = ladder(config_module, 5, claims_each=6)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    shrunk_slug, kept = placed(allocation)[-1]
    assert len(kept) < 6, "this fixture is meant to shrink the entry at the bottom"
    for claim in [f"c{n}" for n in range(len(kept) + 1, 7)]:
        line = line_naming(omitted_claims(allocation), f"{shrunk_slug}/{claim}")
        assert "shrunk to fit the page" in line


def test_the_omission_view_scales_with_the_bank_not_with_the_page(
    repo_root, run_dir, config_module, tmp_path
):
    """A structural cut: no band around the cut line, no top-N."""

    def omitted_count(extra: int) -> int:
        folder = tmp_path / f"run-{extra}"
        folder.mkdir()
        rows, _ = ladder(config_module, 3, claims_each=3)
        for index in range(extra):
            rows += entry_rows(
                f"same-field-{index}", ["0.20", "0.20"], ended="2018-06"
            )
        write_scores(folder, rows)
        return len(omitted_entries(pack_ok(repo_root, folder)))

    assert omitted_count(6) - omitted_count(2) == 4


def test_a_placed_entry_is_not_restated_in_the_omission_view(repo_root, run_dir):
    write_scores(run_dir, entry_rows("acme-platform", ["0.90", "0.80", "0.70"]))

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["acme-platform"]
    assert omitted_entries(allocation) == []


# --- Determinism, and the promise that no row is ever quietly skipped ---


def test_the_same_scores_pack_to_the_same_allocation(repo_root, run_dir, config_module):
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    first = pack_ok(repo_root, run_dir)
    second = pack_ok(repo_root, run_dir)

    assert first == second


def test_a_table_row_stranded_after_the_table_fails(repo_root, run_dir):
    """A blank line ends the table, so anything after it would otherwise vanish."""
    run_dir.joinpath("scores.md").write_text(
        "\n".join(
            [
                HEADER_ROW,
                DELIMITER_ROW,
                "| acme-platform | c1 | job | 2024-06 | 0.90 | 1 | scored |",
                "",
                "Some notes the maker left here.",
                "",
                "| beta-shop | c1 | job | 2023-01 | 0.80 | 1 | stranded below the notes |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "beta-shop" in result.stderr
    assert "row 7" in result.stderr
    assert not (run_dir / "allocation.md").exists()


def test_the_allocation_records_the_budget_it_spent(repo_root, run_dir, config_module):
    """What the page cost, so a surprising selection can be read rather than re-derived."""
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    budget = bullet_budget(config_module, jobs=True, projects=False)
    assert f"Budget: {budget} lines" in allocation
    assert f"Spent {lines_spent(config_module, allocation)}" in allocation


def test_a_tie_for_the_last_slot_inside_an_entry_is_logged(repo_root, run_dir):
    """Two claims at the same score, one slot: the claim id decides, so say so."""
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "the best one"),
            *(
                ("acme-platform", f"c{n}", "job", "2024-06", "0.70", f"tied, and c{n}")
                for n in range(2, 9)
            ),
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == [
        "c1", "c2", "c3", "c4", "c5", "c6"
    ]
    logged = line_naming(silent_calls(allocation), "tie", "acme-platform/c6")
    assert "acme-platform/c7" in logged and "acme-platform/c8" in logged
    assert "0.70" in logged


# --- Page order, and the band's outer edge ---


def test_placed_is_in_page_order_experience_then_projects(repo_root, run_dir):
    """The template routes by type, so the page reads jobs first whatever the scores."""
    write_scores(
        run_dir,
        entry_rows("top-project", ["0.95", "0.95", "0.95"], type_="project", ended="2024-11")
        + entry_rows("middling-job", ["0.70", "0.70", "0.70"], ended="present")
        + entry_rows("lesser-project", ["0.60", "0.60", "0.60"], type_="project", ended="2022-01")
        + entry_rows("older-job", ["0.55", "0.55", "0.55"], ended="2020-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == [
        "middling-job",
        "older-job",
        "top-project",
        "lesser-project",
    ]


def test_the_band_is_transitive_across_a_middle_entry(repo_root, run_dir):
    """0.90 / 0.86 / 0.83: every adjacent gap is under ε, so all three are one tie.

    The middle entry is within ε of both of its neighbours. Closing the group
    against whichever entry happened to lead it would tie 0.90 with 0.86 and then
    order 0.86 above 0.83 — the same 0.03 gap read two ways, decided by a third
    entry rather than by the two being compared. One group, broken by recency.
    """
    write_scores(
        run_dir,
        entry_rows("top-and-oldest", ["0.90", "0.90", "0.90"], ended="2019-01")
        + entry_rows("middle-rung", ["0.86", "0.86", "0.86"], ended="2020-01")
        + entry_rows("bottom-and-newest", ["0.83", "0.83", "0.83"], ended="present"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == [
        "bottom-and-newest",
        "middle-rung",
        "top-and-oldest",
    ]


def test_a_chain_of_near_neighbours_is_one_tie_group(repo_root, run_dir):
    """Four rungs, each 0.04 below the last: the chain makes all four one tie.

    This is the band's honest cost — the group spans 0.12 and recency hands the
    page to the lowest-scoring entry. Every link in the chain is a real tie, and
    the rule refuses to break one in the middle.
    """
    write_scores(
        run_dir,
        entry_rows("best-and-oldest", ["1.00", "1.00", "1.00"], ended="2019-01")
        + entry_rows("second-rung", ["0.96", "0.96", "0.96"], ended="2020-01")
        + entry_rows("third-rung", ["0.92", "0.92", "0.92"], ended="2021-01")
        + entry_rows("worst-and-newest", ["0.88", "0.88", "0.88"], ended="present"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == [
        "worst-and-newest",
        "third-rung",
        "second-rung",
        "best-and-oldest",
    ]


def test_a_full_epsilon_gap_still_closes_a_chain(repo_root, run_dir):
    """The chain only links gaps *under* ε: an exact 0.05 step ends the group.

    0.90 and 0.87 tie; 0.82 is a full ε below 0.87 and starts a group of its own,
    so the newest entry leads the first pair and stays behind both of them.
    """
    write_scores(
        run_dir,
        entry_rows("top-and-oldest", ["0.90", "0.90", "0.90"], ended="2019-01")
        + entry_rows("second-and-newest", ["0.87", "0.87", "0.87"], ended="present")
        + entry_rows("below-the-band", ["0.82", "0.82", "0.82"], ended="2024-06"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == [
        "second-and-newest",
        "top-and-oldest",
        "below-the-band",
    ]


def test_entries_inside_the_band_are_still_ordered_by_recency(repo_root, run_dir):
    """The 0.04 gap at the top of that ladder is a tie, and recency breaks it."""
    write_scores(
        run_dir,
        entry_rows("best-and-oldest", ["1.00", "1.00", "1.00"], ended="2019-01")
        + entry_rows("second-rung", ["0.96", "0.96", "0.96"], ended="2020-01"),
    )

    allocation = pack_ok(repo_root, run_dir)

    assert placed_slugs(allocation) == ["second-rung", "best-and-oldest"]


# --------------------------------------------------------------------------
# The two passes, and the reconcile between them
# --------------------------------------------------------------------------


def test_pass_one_reserves_four_single_line_rows_and_says_so(repo_root, run_dir, config_module):
    """The budget has to exist before anyone can compose against it, so pass one
    assumes a Skills section nobody has written yet — and marks its output as a
    reservation, so it cannot be mistaken for the page that will render."""
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    assert "RESERVATION" in allocation
    assert "--skills-rows" in allocation
    assert f"Budget: {bullet_budget(config_module, jobs=True, projects=False)} lines" in allocation


@pytest.mark.parametrize(
    "composed, moves",
    [
        # Composing one row fewer than reserved hands back exactly one line, and
        # that is newer than it looks. A row was 10.00pt against a 14.00pt line
        # until the 2026-08-10 re-measure, so the rounding absorbed a row and only
        # dropping to two rows moved anything — the finding `0021` §4 was built on.
        # A row is one Bullet line now, so the section's charge is its row count and
        # the reconcile is linear. Nothing in `pack.py` changed to make it so; these
        # numbers follow from `SKILLS_ROW_PT` alone.
        ("1,1,1,1", 0),
        ("1,1,1", 1),
        ("1,1", 2),
        ("", 6),
        # And the pass can TAKE lines as well as give them.
        ("1,2,1,1", -1),
        ("2,2,2,2", -4),
    ],
)
def test_the_second_pass_settles_up_in_both_directions(
    repo_root, run_dir, config_module, composed, moves
):
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    reserved = bullet_budget(config_module, jobs=True, projects=False)
    pack_ok(repo_root, run_dir)
    allocation = pack_ok(repo_root, run_dir, "--skills-rows", composed)

    assert f"Budget: {reserved + moves} lines" in allocation
    assert "Skills reconcile:" in section(allocation, "Silent calls")


def test_the_reconcile_is_logged_even_when_it_moves_nothing(repo_root, run_dir, config_module):
    """Unlike a rule inside one pass, this is a whole second pass — a reader has to
    be able to confirm it ran."""
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir, "--skills-rows", "1,1,1,1")

    assert "the budget is unchanged" in section(allocation, "Silent calls")


def test_a_composed_section_under_the_floor_takes_its_heading_with_it(
    repo_root, run_dir, config_module
):
    """One row spends three lines of page to show one, so the section goes whole."""
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir, "--skills-rows", "1")

    assert "no section" in allocation
    assert f"Budget: {bullet_budget(config_module, jobs=True, projects=False, skills_rows=[])} lines" in allocation


def test_a_row_past_the_two_line_cap_is_refused(repo_root, run_dir, config_module):
    """A row that would run to three sheds skills instead, so there is no such row
    for the Packer to be told about."""
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    result = pack(repo_root, run_dir, "--skills-rows", "1,3")

    assert result.returncode != 0
    assert "capped at 2" in result.stderr


def test_a_malformed_skills_rows_argument_names_the_cell(repo_root, run_dir, config_module):
    rows, _ = ladder(config_module, 5, claims_each=3)
    write_scores(run_dir, rows)

    result = pack(repo_root, run_dir, "--skills-rows", "1,two")

    assert result.returncode != 0
    assert "'two'" in result.stderr


# --------------------------------------------------------------------------
# The entry arc: `## Leads` and `## Merges` (docs/adr/0032, 0034, 0035, 0037)
# --------------------------------------------------------------------------


def with_tables(scores_rows: list[tuple[str, ...]], *extra_sections: str) -> str:
    """A Score table plus `## Leads` and/or `## Merges`, appended after it."""
    return scores_md(scores_rows) + "\n" + "\n\n".join(extra_sections) + "\n"


def leads_table(rows: list[tuple[str, str]]) -> str:
    lines = ["## Leads", "", "| entry | lead |", "|---|---|"]
    lines += [f"| {entry} | {value} |" for entry, value in rows]
    return "\n".join(lines)


def merges_table(rows: list[tuple[str, str, str, str]]) -> str:
    lines = ["## Merges", "", "| entry | claims | width | reason |", "|---|---|---|---|"]
    lines += [f"| {entry} | {ids} | {width} | {reason} |" for entry, ids, width, reason in rows]
    return "\n".join(lines)


def openers_table(rows: list[tuple[str, str]]) -> str:
    lines = ["## Openers", "", "| entry | unit |", "|---|---|"]
    lines += [f"| {entry} | {unit} |" for entry, unit in rows]
    return "\n".join(lines)


def five_claims() -> list[tuple[str, ...]]:
    """`acme-platform`, five claims — three mergeable, two standing alone."""
    return [
        ("acme-platform", "c1", "job", "2024-06", "0.85", "1", "a mergeable one"),
        ("acme-platform", "c2", "job", "2024-06", "1.00", "1", "the strongest claim"),
        ("acme-platform", "c3", "job", "2024-06", "0.60", "1", "a mergeable one"),
        ("acme-platform", "c4", "job", "2024-06", "0.85", "1", "a mergeable one"),
        ("acme-platform", "c5", "job", "2024-06", "0.70", "1", "stands alone"),
    ]


def test_every_scored_entry_needs_a_leads_row(repo_root, run_dir):
    """`0035` §2 — a forgotten lead and an absent one must be different bytes."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), leads_table([])), encoding="utf-8"
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "acme-platform" in result.stderr


def test_a_leads_value_that_is_not_y_or_n_is_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), leads_table([("acme-platform", "maybe")])),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "maybe" in result.stderr


def test_an_entry_with_a_lead_reserves_lead_lines_and_marks_the_heading(
    repo_root, run_dir, config_module
):
    """`0032` §6 — the reservation minimum grows by LEAD_LINES, and the Placed
    heading records the lead it charged (`0035` §2)."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), leads_table([("acme-platform", "y")])),
        encoding="utf-8",
    )
    without_lead = pack_ok(repo_root, run_dir)
    assert "— lead —" in without_lead
    spent_with_lead = re.search(r"Spent (\d+)", without_lead).group(1)

    write_scores(run_dir, five_claims())
    without = pack_ok(repo_root, run_dir)
    assert "— lead —" not in without
    spent_without_lead = re.search(r"Spent (\d+)", without).group(1)

    assert int(spent_with_lead) == int(spent_without_lead) + config_module.LEAD_LINES


def test_a_merge_group_places_as_one_row_and_frees_a_line(repo_root, run_dir):
    """`0034` §3 — a merge of 3 at width 2 reserves 2 lines where 3 claims would
    have reserved 3, and the freed line is what puts the 4th claim on the page."""
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(), merges_table([("acme-platform", "c1+c3+c4", "2", "none lands alone")])
        ),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c2", "c1+c3+c4", "c5"]
    assert "acme-platform/c1+c3+c4 — 0.85 — 2 lines — none lands alone" in allocation


def test_a_merged_claims_own_width_must_read_one(repo_root, run_dir):
    """`0034` §2 — a merged claim's own claims-table width is ambiguous unless 1."""
    rows = [
        ("acme-platform", "c1", "job", "2024-06", "0.85", "2", "a mergeable one"),
        ("acme-platform", "c3", "job", "2024-06", "0.60", "1", "a mergeable one"),
    ]
    (run_dir / "scores.md").write_text(
        with_tables(rows, merges_table([("acme-platform", "c1+c3", "2", "none lands alone")])),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "c1" in result.stderr


def test_a_claim_in_two_merges_is_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(),
            merges_table(
                [
                    ("acme-platform", "c1+c3", "1", "first"),
                    ("acme-platform", "c1+c4", "1", "second"),
                ]
            ),
        ),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0


def test_the_cap_counts_units_not_claims(repo_root, run_dir):
    """`0037` §6 — an entry of 7 qualifying claims with one 3-merge places 5 units,
    never 7, and the merge frees the line that puts the 7th claim on the page."""
    rows = five_claims() + [
        ("acme-platform", "c6", "job", "2024-06", "0.65", "1", "the sixth"),
        ("acme-platform", "c7", "job", "2024-06", "0.55", "1", "the seventh"),
    ]
    (run_dir / "scores.md").write_text(
        with_tables(rows, merges_table([("acme-platform", "c1+c3+c4", "2", "none lands alone")])),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c2", "c1+c3+c4", "c5", "c6", "c7"]


def test_the_merges_section_carries_the_reason_verbatim(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(),
            merges_table(
                [("acme-platform", "c1+c3+c4", "2", "none of the three lands alone")]
            ),
        ),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert "## Merges" in allocation
    assert "none of the three lands alone" in allocation


# --------------------------------------------------------------------------
# Declared openers: `## Openers` (docs/adr/0040-fit-orders-the-page-force-orders-the-block.md)
# --------------------------------------------------------------------------


def merged_five() -> str:
    """`five_claims()` with `c1+c3+c4` merged — the shape a real run had.

    By score the block reads `c2` (1.00), `c1+c3+c4` (0.85), `c5` (0.70), which is
    the entry the ADR argues from: every quantified outcome sits under an
    unquantified line because 1.00 > 0.85.
    """
    return merges_table([("acme-platform", "c1+c3+c4", "2", "none lands alone")])


def test_the_declared_opener_moves_to_the_top_of_its_block(repo_root, run_dir):
    """`0040` §2 — force orders the block, and the move is a Silent call."""
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(), merged_five(), openers_table([("acme-platform", "c1+c3+c4")])
        ),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1+c3+c4", "c2", "c5"]
    moved = line_naming(silent_calls(allocation), "Opener:", "moved to the top")
    assert "acme-platform/c1+c3+c4" in moved
    assert "from position 2 by score" in moved


def test_an_opener_already_first_by_score_is_still_logged(repo_root, run_dir):
    """The common and correct answer, said out loud — the table exists so that
    answer is made rather than inherited (`0040` §1)."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), merged_five(), openers_table([("acme-platform", "c2")])),
        encoding="utf-8",
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c2", "c1+c3+c4", "c5"]
    assert "acme-platform/c2" in line_naming(
        silent_calls(allocation), "Opener:", "already first by score"
    )


def test_no_openers_table_keeps_score_order_and_says_it_was_inherited(repo_root, run_dir):
    """The table absent entirely is `parse_leads`'s tolerance, not a refusal — a run
    folder scored before `0040` still packs, and the Silent call says what happened."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), merged_five()), encoding="utf-8"
    )

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c2", "c1+c3+c4", "c5"]
    assert "inherited, not chosen" in line_naming(
        silent_calls(allocation), "Opener:", "acme-platform"
    )


def test_the_opener_moves_nothing_but_the_print_order(repo_root, run_dir):
    """THE INVARIANT THIS STAGE LIVES OR DIES ON (`0040` §2).

    Entry score and slot count are byte-identical before and after an `## Openers`
    change, and so is the page budget: the same units place, charged the same
    widths, in a different order. Selection reads score order and this never
    reaches it.
    """
    variants = {}
    for name, sections in {
        "none": (merged_five(),),
        "top": (merged_five(), openers_table([("acme-platform", "c2")])),
        "third": (merged_five(), openers_table([("acme-platform", "c5")])),
    }.items():
        (run_dir / "scores.md").write_text(
            with_tables(five_claims(), *sections), encoding="utf-8"
        )
        variants[name] = pack_ok(repo_root, run_dir)

    headings = {
        name: re.findall(r"^### .*$", allocation, re.M)
        for name, allocation in variants.items()
    }
    assert headings["none"] == headings["top"] == headings["third"]
    assert "entry score 0.90" in headings["none"][0]
    assert "3 bullets" in headings["none"][0]

    budgets = {re.search(r"^Budget: .*$", a, re.M).group(0) for a in variants.values()}
    assert len(budgets) == 1

    units = {
        name: sorted(bullets_of(allocation, "acme-platform"))
        for name, allocation in variants.items()
    }
    assert units["none"] == units["top"] == units["third"]

    # …and the one thing that did move.
    assert bullets_of(variants["third"], "acme-platform") == ["c5", "c2", "c1+c3+c4"]


def test_a_placed_entry_with_no_openers_row_is_refused(repo_root, run_dir):
    """`0040` §3 — a table that exists and skips a placed entry is the inheritance
    the table was written to stop, wearing a table's clothes."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), openers_table([])), encoding="utf-8"
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "acme-platform" in result.stderr


def test_an_opener_that_did_not_place_is_refused(repo_root, run_dir):
    """`0040` §3 — an opener is chosen from the units that reach the page, and
    which those are is the allocation's call. `c7` is the seventh unit against a
    six-unit cap."""
    rows = [
        ("acme-platform", f"c{n}", "job", "2024-06", "0.90", "1", f"claim {n}")
        for n in range(1, 8)
    ]
    (run_dir / "scores.md").write_text(
        with_tables(rows, openers_table([("acme-platform", "c7")])), encoding="utf-8"
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "acme-platform/c7" in result.stderr
    assert "did not place" in result.stderr


def test_an_opener_naming_a_claim_inside_a_merge_group_is_refused(repo_root, run_dir):
    """`0040` §3 — `c1` reads like a unit everywhere else in the run; inside a merge
    group it is a part of one, and the group is what takes the slot."""
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), merged_five(), openers_table([("acme-platform", "c1")])),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "c1+c3+c4" in result.stderr


def test_an_opener_below_the_bullet_floor_is_refused(repo_root, run_dir):
    rows = five_claims() + [
        ("acme-platform", "c6", "job", "2024-06", "0.20", "1", "same field only")
    ]
    (run_dir / "scores.md").write_text(
        with_tables(rows, openers_table([("acme-platform", "c6")])), encoding="utf-8"
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "bullet floor" in result.stderr


def test_an_opener_naming_an_undeclared_group_is_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(), merged_five(), openers_table([("acme-platform", "c2+c5")])
        ),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "`## Merges`" in result.stderr


def test_an_opener_naming_four_claims_is_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), openers_table([("acme-platform", "c1+c2+c3+c4")])),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "c1+c2+c3+c4" in result.stderr


def test_an_openers_row_for_an_unscored_entry_is_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(five_claims(), openers_table([("ghost-corp", "c1")])), encoding="utf-8"
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "ghost-corp" in result.stderr


def test_two_openers_rows_for_one_entry_are_refused(repo_root, run_dir):
    (run_dir / "scores.md").write_text(
        with_tables(
            five_claims(),
            openers_table([("acme-platform", "c2"), ("acme-platform", "c5")]),
        ),
        encoding="utf-8",
    )

    result = pack(repo_root, run_dir)

    assert result.returncode != 0
    assert "one entry opens on one unit" in result.stderr


def test_the_summary_comes_off_the_budget_before_anything_competes(
    repo_root, run_dir, config_module
):
    """`0044` §5 — charged like HEADER_LINES, not like a lead.

    The Packer runs before a word is composed and cannot see whether a Summary
    arrived, so it charges for one on every run. Pinned against `PAGE_LINES` rather
    than against the helper that mirrors it, so this fails if both drift together.
    """
    rows, _ = ladder(config_module, 3, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    budget = int(re.search(r"Budget: (\d+) lines", allocation).group(1))
    assert budget == bullet_budget(config_module, jobs=True, projects=False)
    assert budget <= (
        config_module.PAGE_LINES
        - config_module.SUMMARY_LINES
        - config_module.SECTION_LINES  # its heading, charged the same way
    )


def test_the_allocation_says_what_the_summary_took(repo_root, run_dir, config_module):
    """A line the page spends that the allocation cannot show spent is how a budget
    stops being auditable. The Summary never competes and never varies, so nothing
    else in this file would ever mention it."""
    rows, _ = ladder(config_module, 3, claims_each=3)
    write_scores(run_dir, rows)

    allocation = pack_ok(repo_root, run_dir)

    assert (
        f"Summary: {config_module.SUMMARY_LINES} line(s) of prose plus "
        f"{config_module.SECTION_LINES} for its heading" in allocation
    )


# --------------------------------------------------------------------------
# The depth cap (docs/adr/0048-the-depth-cap-is-a-line-budget.md)
# --------------------------------------------------------------------------


def test_an_entry_is_capped_at_six_bullet_lines_not_six_units(repo_root, run_dir):
    """`0048` §1: six two-line claims get three Bullets, not six.

    The whole page is available to one entry here, so nothing but its own cap can
    stop it. Before `0048` it took all six units and twelve lines of a one-page
    résumé with them.
    """
    write_scores(
        run_dir,
        [
            ("acme-platform", f"c{n}", "job", "2024-06", "1.00", "2", "needs the room")
            for n in range(1, 7)
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert len(bullets_of(allocation, "acme-platform")) == 3


def test_the_line_cap_and_the_unit_cap_agree_on_a_page_of_one_line_bullets(
    repo_root, run_dir
):
    """`0048` §1's claim to being a repair rather than a new policy.

    Where every Bullet is one line the two caps are the same number, so the page
    `0026` designed comes out unchanged. If this ever fails, `0048` has stopped being
    an amendment to `0026`'s arithmetic and become a different decision about depth.
    """
    write_scores(run_dir, entry_rows("acme-platform", ["1.00"] * 8))

    allocation = pack_ok(repo_root, run_dir)

    assert len(bullets_of(allocation, "acme-platform")) == 6


def test_the_reserved_unit_is_charged_against_the_entrys_own_budget(
    repo_root, run_dir
):
    """`0048` §2: a block opening on a two-line Bullet has four of its six left."""
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "1.00", "2", "the opener, wide"),
            *[
                ("acme-platform", f"c{n}", "job", "2024-06", "0.90", "1", "says it in one")
                for n in range(2, 8)
            ],
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    # 2 lines for the opener leaves 4, and four one-line Bullets fill them.
    assert len(bullets_of(allocation, "acme-platform")) == 5


def test_a_unit_lost_to_the_depth_cap_says_so_and_not_that_the_page_ran_out(
    repo_root, run_dir
):
    """`0048` §3: the two causes send the maker to opposite repairs.

    One entry, the whole page to itself — so nothing here is about room, and a line
    claiming the page ran out would be false.
    """
    write_scores(
        run_dir,
        [
            ("acme-platform", f"c{n}", "job", "2024-06", "1.00", "2", "needs the room")
            for n in range(1, 7)
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    assert "depth cap: acme-platform dropped acme-platform/c4" in allocation
    lost = omitted(allocation)
    assert "own 6-line depth cap, not for want of room on the page" in lost
    assert "shrunk to fit the page" not in lost


# --------------------------------------------------------------------------
# A résumé is a selection (docs/adr/0057-the-page-reads-like-a-resume.md §5)
# --------------------------------------------------------------------------


def eight_lone_claims() -> list[tuple[str, ...]]:
    """One entry, eight qualifying claims, none merged — more than its share."""
    return [
        ("acme-platform", f"c{n}", "job", "2024-06", "0.90", "1", "a fixture reason")
        for n in range(1, 9)
    ]


@pytest.mark.parametrize("flags", [(), ("--skills-rows", "1,1")])
def test_a_placed_entry_seats_its_best_claims_and_reports_the_rest(
    repo_root, run_dir, flags
):
    """0057 §5, reversing 0049: the weaker claims lose their line, the Omission view
    names them, and neither pass refuses or advises a merge to fit them in."""
    write_scores(run_dir, eight_lone_claims())

    allocation = pack_ok(repo_root, run_dir, *flags)

    assert bullets_of(allocation, "acme-platform") == [f"c{n}" for n in range(1, 7)]
    lost = omitted(allocation)
    assert "acme-platform/c7" in lost and "acme-platform/c8" in lost
    assert "Coverage:" not in allocation
    assert "merge" not in "\n".join(silent_calls(allocation))


def test_the_depth_cap_holds_for_a_block_of_merges_too(repo_root, run_dir):
    """`0049` §4 let an all-merge block borrow past its six lines. With merges rare
    (0057 §5) the exception is gone: four two-line merges seat three."""
    rows = [
        ("acme-platform", f"c{n}", "job", "2024-06", "0.90", "1", "a fixture reason")
        for n in range(1, 9)
    ]
    merges = [
        ("acme-platform", "c1+c2", "2", "merged"),
        ("acme-platform", "c3+c4", "2", "merged"),
        ("acme-platform", "c5+c6", "2", "merged"),
        ("acme-platform", "c7+c8", "2", "merged"),
    ]
    (run_dir / "scores.md").write_text(with_tables(rows, merges_table(merges)), "utf-8")

    allocation = pack_ok(repo_root, run_dir)

    assert bullets_of(allocation, "acme-platform") == ["c1+c2", "c3+c4", "c5+c6"]
    assert line_naming(silent_calls(allocation), "depth cap:", "acme-platform")
    assert "soft cap" not in allocation


# --------------------------------------------------------------------------
# The entry caps (docs/adr/0051-the-page-carries-three-jobs-and-two-projects.md)
# --------------------------------------------------------------------------


def mixed_bank() -> list[tuple[str, ...]]:
    """Five jobs and four projects, strict score order, no ties."""
    rows: list[tuple[str, ...]] = []
    for index, (slug, type_) in enumerate(
        [(f"job-{n}", "job") for n in range(1, 6)]
        + [(f"proj-{n}", "project") for n in range(1, 5)]
    ):
        rows += entry_rows(
            slug, [f"{(95 - 5 * index) / 100:.2f}"], type_=type_, ended=f"{2030 - index:04d}-06"
        )
    return rows


def test_the_page_carries_three_jobs_and_two_projects_by_default(repo_root, run_dir):
    """`0051` §1. Nine entries compete; five reach the page."""
    write_scores(run_dir, mixed_bank())

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "3", "--max-projects", "2")

    slugs = placed_slugs(allocation)
    assert sum(1 for slug in slugs if slug.startswith("job-")) == 3
    assert sum(1 for slug in slugs if slug.startswith("proj-")) == 2


def test_the_caps_are_configurable(repo_root, run_dir):
    """The two knobs the maker turns, and `allocation.md` records what it packed under."""
    write_scores(run_dir, mixed_bank())

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "2", "--max-projects", "1")

    slugs = placed_slugs(allocation)
    assert sum(1 for slug in slugs if slug.startswith("job-")) == 2
    assert sum(1 for slug in slugs if slug.startswith("proj-")) == 1


def test_a_capped_entry_is_named_apart_from_one_the_page_had_no_room_for(
    repo_root, run_dir
):
    """`0051` §2: the cap is not this page being full.

    A capped entry never competed, and a page with lines to spare would have cut it
    just the same — so it must not be reported as though room were the problem.
    """
    write_scores(run_dir, mixed_bank())

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "3", "--max-projects", "2")

    lost = omitted(allocation)
    assert "did not compete — the page carries 3 experience entries" in lost
    assert "did not compete — the page carries 2 project entries" in lost


def test_a_job_wins_a_tie_against_a_project_and_only_a_tie(repo_root, run_dir):
    """`0051` §1: the priority is a tie-break, never an ordering of the two kinds.

    `proj-hot` outscores `job-cold` by more than the tie band and keeps its place; a
    job inside the band goes first. A rule that put every job above every project
    would drop the strongest project on the page for the weakest job.
    """
    write_scores(
        run_dir,
        [
            ("proj-hot", "c1", "project", "2024-06", "0.90", "1", "far and away the best"),
            ("job-tied", "c1", "job", "2023-06", "0.88", "1", "inside the tie band"),
            ("job-cold", "c1", "job", "2022-06", "0.55", "1", "well below both"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir)

    # `## Placed` is in PAGE order — every job, then every project — so competition
    # order is read off the tie log, which is where the rule actually shows.
    tie = line_naming(silent_calls(allocation), "tie:", "proj-hot")
    assert tie.endswith("job-tied, proj-hot")
    assert "ordered jobs first" in tie
    assert set(placed_slugs(allocation)) == {"job-tied", "proj-hot", "job-cold"}


def test_the_two_most_recent_jobs_survive_the_cap(repo_root, run_dir):
    """`0051` §1: the Experience floor outranks the cap.

    `job-recent` is the newest job and the worst-scoring of the four. A cap applied
    on score alone would cut it and quietly break the guarantee that the page always
    shows the last two jobs.
    """
    write_scores(
        run_dir,
        [
            ("job-old-a", "c1", "job", "2019-06", "0.95", "1", "strongest, oldest"),
            ("job-old-b", "c1", "job", "2018-06", "0.90", "1", "strong, older"),
            ("job-old-c", "c1", "job", "2017-06", "0.85", "1", "strong, oldest"),
            ("job-recent", "c1", "job", "2026-06", "0.55", "1", "newest, weakest"),
            ("job-second", "c1", "job", "2025-06", "0.60", "1", "second newest"),
            # Two projects, so the job cap actually binds: with none, §3's lending
            # would hand Experience the unused project slots and seat all five.
            ("proj-a", "c1", "project", "2024-06", "0.80", "1", "a real project"),
            ("proj-b", "c1", "project", "2023-06", "0.75", "1", "another"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "3", "--max-projects", "2")

    jobs = [slug for slug in placed_slugs(allocation) if slug.startswith("job-")]
    assert "job-recent" in jobs and "job-second" in jobs
    assert len(jobs) == 3


def test_a_section_lends_the_slots_the_other_cannot_use(repo_root, run_dir):
    """`0051` §3: the cap binds against competition, not for its own sake.

    Four jobs and one project. The project cap of two has a slot nothing can fill, so
    Experience takes it and seats four. What the caps exist to prevent is a page of
    nothing but Experience while real Projects wait — not an Experience section held
    to three when there is nothing to hold it for.
    """
    write_scores(
        run_dir,
        [
            ("job-a", "c1", "job", "2026-06", "0.95", "1", "a job"),
            ("job-b", "c1", "job", "2025-06", "0.90", "1", "a job"),
            ("job-c", "c1", "job", "2024-06", "0.85", "1", "a job"),
            ("job-d", "c1", "job", "2023-06", "0.80", "1", "a job"),
            ("proj-only", "c1", "project", "2022-06", "0.75", "1", "the only project"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "3", "--max-projects", "2")

    slugs = placed_slugs(allocation)
    assert sum(1 for slug in slugs if slug.startswith("job-")) == 4
    assert "proj-only" in slugs


def test_lending_never_starves_the_section_that_could_have_used_the_slot(
    repo_root, run_dir
):
    """`0051` §3's guard: only UNUSED capacity moves.

    Four projects against four jobs. Nothing is unused, so nothing is lent and the
    page seats three and two — the maker's actual complaint was a page that resorts
    to filling only Experience when projects exist, and this is what stops it.
    """
    write_scores(
        run_dir,
        [
            (f"job-{n}", "c1", "job", f"{2026 - n:04d}-06", f"{(96 - n) / 100:.2f}", "1", "a job")
            for n in range(1, 5)
        ]
        + [
            (f"proj-{n}", "c1", "project", f"{2020 - n:04d}-06", f"{(80 - n) / 100:.2f}", "1", "a project")
            for n in range(1, 5)
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "3", "--max-projects", "2")

    slugs = placed_slugs(allocation)
    assert sum(1 for slug in slugs if slug.startswith("job-")) == 3
    assert sum(1 for slug in slugs if slug.startswith("proj-")) == 2


def test_an_entry_with_nothing_at_the_floor_takes_no_cap_slot(repo_root, run_dir):
    """A cap slot goes to an entry that can place a Bullet.

    `proj-new` is the newest project in the tie band but has no claim at 0.50, so it
    places nothing. Seating it under the project cap would cut `proj-b`, which can.
    """
    write_scores(
        run_dir,
        [
            ("job-a", "c1", "job", "2026-06", "0.90", "1", "a job"),
            ("proj-new", "c1", "project", "2026-06", "0.49", "1", "newest, below the floor"),
            ("proj-a", "c1", "project", "2024-06", "0.56", "1", "a project"),
            ("proj-b", "c1", "project", "2023-06", "0.52", "1", "another"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "1", "--max-projects", "2")

    slugs = placed_slugs(allocation)
    assert "proj-a" in slugs and "proj-b" in slugs
    assert "did not compete" not in omitted(allocation)


@pytest.mark.parametrize("cap", ["0", "1"])
def test_an_experience_cap_below_two_is_never_exceeded(repo_root, run_dir, cap):
    """The two-most-recent-jobs guarantee yields to a cap set below it."""
    write_scores(
        run_dir,
        [
            ("job-a", "c1", "job", "2026-06", "0.90", "1", "a job"),
            ("job-b", "c1", "job", "2025-06", "0.85", "1", "a job"),
            ("job-c", "c1", "job", "2024-06", "0.80", "1", "a job"),
            ("proj-a", "c1", "project", "2023-06", "0.75", "1", "a project"),
            ("proj-b", "c1", "project", "2022-06", "0.70", "1", "a project"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", cap, "--max-projects", "2")

    jobs = [slug for slug in placed_slugs(allocation) if slug.startswith("job-")]
    assert len(jobs) == int(cap)
    if cap == "1":
        assert jobs == ["job-a"]


def test_a_negative_cap_is_refused(repo_root, run_dir):
    write_scores(run_dir, entry_rows("acme-platform", ["0.90"]))
    result = pack(repo_root, run_dir, "--max-experience", "-1")
    assert result.returncode != 0
    assert "negative" in result.stderr


def test_a_capped_job_that_outscores_a_kept_one_is_not_told_it_scored_lower(
    repo_root, run_dir
):
    """The two most recent jobs are kept whatever they score, so the log says how
    the room was filled rather than claiming everything kept scored higher."""
    write_scores(
        run_dir,
        [
            ("job-a", "c1", "job", "2026-06", "0.60", "1", "newest"),
            ("job-b", "c1", "job", "2025-06", "0.60", "1", "second newest"),
            ("job-d", "c1", "job", "2020-06", "0.90", "1", "old, strongest"),
            ("proj-a", "c1", "project", "2023-06", "0.75", "1", "a project"),
            ("proj-b", "c1", "project", "2022-06", "0.70", "1", "a project"),
        ],
    )

    allocation = pack_ok(repo_root, run_dir, "--max-experience", "2", "--max-projects", "2")

    assert "job-d" not in placed_slugs(allocation)
    lost = omitted(allocation)
    assert "scored above it" not in lost
    assert "the two most recent jobs first" in lost


def test_a_below_floor_claim_of_a_placed_entry_stays_off_the_page(repo_root, run_dir):
    """0057 §5: a 0.20 claim on the page argues against the maker, so it does not place."""
    write_scores(
        run_dir,
        [
            ("acme-platform", "c1", "job", "2024-06", "0.90", "1", "carries the entry"),
            ("acme-platform", "c2", "job", "2024-06", "0.20", "1", "well below the floor"),
        ],
    )

    result = pack(repo_root, run_dir, "--skills-rows", "1,1")

    assert result.returncode == 0, result.stderr
    allocation = (run_dir / "allocation.md").read_text(encoding="utf-8")
    assert "acme-platform/c2 — 0.20 — below the 0.50 bullet floor" in allocation


def test_a_below_floor_claim_reaches_the_page_inside_a_merge(repo_root, run_dir):
    """And the remedy is the one the refusal names — a merge group carries it.

    A merge group's members never had to clear the floor individually (`0037` §2), so
    the mechanism `0053` §3 needs already existed; what changed is that the Packer now
    insists it be used.
    """
    rows = [
        ("acme-platform", "c1", "job", "2024-06", "0.90", "1", "carries the entry"),
        ("acme-platform", "c2", "job", "2024-06", "0.20", "1", "well below the floor"),
    ]
    merges = [("acme-platform", "c1+c2", "2", "one story, told once")]
    (run_dir / "scores.md").write_text(with_tables(rows, merges_table(merges)), "utf-8")

    allocation = pack_ok(repo_root, run_dir, "--skills-rows", "1,1")

    assert "acme-platform/c1+c2" in allocation
    assert "below the 0.50 bullet floor" not in omitted(allocation)
