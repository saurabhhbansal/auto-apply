"""tools/coverage.py, driven as a command over a throwaway run folder.

Same convention as the rest of the suite: the run folder's files are the contract.
`allocation.md` is produced by running `pack.py` over the fixture rather than being
hand-written, because *which claims placed* is the Packer's call and a hand-written
allocation would be this test agreeing with itself.

Every test here asserts the exit code is 0. That is the one property the coverage
read must never lose: it is advisory, `render.py` neither calls it nor reads it, and a
diagnostic that can fail a run is a gate
(`docs/adr/0041-the-page-is-read-back-against-the-posting.md` §4).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

SCORES = """# Scores: a hand-written fixture

| entry | claim | type | ended | score | width | reason |
|---|---|---|---|---|---|---|
| helios-payments | c1 | job | 2024-06 | 0.90 | 1 | Kafka consumer work in Go on a hot path, the streaming must-have head-on |
| helios-payments | c2 | job | 2024-06 | 0.60 | 1 | Nightly ledger extracts; Airflow is on its skills line and nowhere in the Evidence |
| ledger-cli | c1 | project | 2023-01 | 0.20 | 1 | A tutorial for a personal tool written in Rust, same field only |

## Leads

| entry | lead |
|---|---|
| helios-payments | y |
| ledger-cli | n |

## Openers

| entry | unit |
|---|---|
| helios-payments | c1 |
"""

BULLETS = """# Bullets: acme-backend-engineer

## Summary
A backend engineer who builds payment systems and the streaming data work under them.

## helios-payments
Lead: The payments reporting cycle was hand-run end to end before any of this.
- helios-payments/c1: Cut checkout p99 latency 40% by batching offset commits in the Go consumer
- helios-payments/c2: Rebuilt the nightly ledger extract as an incremental diff, running hourly

## Skills

### Streaming
- Kafka (helios-payments/c1)
- Protobuf (helios-payments/c1)

### Data
- PostgreSQL (helios-payments/c2)
- SQL (helios-payments/c2)
"""

TERMS = """# Terms: acme-backend-engineer

## Must-have

- kafka
- offset commits
- payments reporting
- Streaming
- Airflow
- Rust
- Kubernetes
- Go
"""


@pytest.fixture
def run_dir(tmp_path: Path, repo_root: Path) -> Path:
    """A packed run folder with a composed page, terms and all."""
    folder = tmp_path / "acme-backend-engineer"
    folder.mkdir()
    (folder / "scores.md").write_text(SCORES, encoding="utf-8")
    (folder / "bullets.md").write_text(BULLETS, encoding="utf-8")
    (folder / "terms.md").write_text(TERMS, encoding="utf-8")
    packed = subprocess.run(
        [sys.executable, "tools/pack.py", str(folder), "--skills-rows", "1,1"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert packed.returncode == 0, packed.stderr
    return folder


def coverage(repo_root: Path, run_dir: Path) -> str:
    result = subprocess.run(
        [sys.executable, "tools/coverage.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"the coverage read is advisory: {result.stderr}"
    return result.stdout


def block(out: str, title: str) -> list[str]:
    """The indented lines under one `<title> (n/m)` heading."""
    match = re.search(
        rf"^{re.escape(title)} \(\d+/\d+\)\n((?:  .*\n)*)", out, re.M
    )
    assert match, f"no `{title}` block in:\n{out}"
    return [line.strip() for line in match.group(1).splitlines()]


def counts(out: str) -> dict[str, tuple[int, int]]:
    return {
        title: (int(part), int(whole))
        for title, part, whole in re.findall(r"^(\D[^(\n]+) \((\d+)/(\d+)\)$", out, re.M)
    }


def line_for(lines: list[str], term: str) -> str:
    hits = [line for line in lines if line.startswith(term)]
    assert len(hits) == 1, f"expected one line for {term!r}, got {hits}"
    return hits[0]


# --------------------------------------------------------------------------
# The three-way split
# --------------------------------------------------------------------------


def test_a_term_on_the_page_is_covered_and_names_where(repo_root, run_dir):
    covered = block(coverage(repo_root, run_dir), "Covered on the page")

    assert "helios-payments/c1 (bullet)" in line_for(covered, "offset commits")
    assert "helios-payments/c1 (skills row)" in line_for(covered, "kafka")
    assert "helios-payments (lead)" in line_for(covered, "payments reporting")
    assert "the Streaming row (skills label)" in line_for(covered, "Streaming")


def test_a_term_only_a_scores_reason_carries_is_absent_from_the_page(repo_root, run_dir):
    """The middle list — the one that did not exist before. `Airflow` is named in
    `helios-payments/c2`'s reason, that claim took a Bullet slot, and the composed
    sentence never says it."""
    out = coverage(repo_root, run_dir)

    in_bank = block(out, "Answered by the bank, absent from the page")
    assert line_for(in_bank, "Airflow").endswith("placed: helios-payments/c2")


def test_a_term_whose_claim_lost_the_page_says_so(repo_root, run_dir):
    """`0009`'s *you have it, the page did not*, sourced instead of remembered."""
    in_bank = block(
        coverage(repo_root, run_dir), "Answered by the bank, absent from the page"
    )

    assert line_for(in_bank, "Rust").endswith("lost the page: ledger-cli/c1")


def test_a_term_nothing_answers_is_answered_nowhere(repo_root, run_dir):
    nowhere = block(coverage(repo_root, run_dir), "Answered nowhere")

    assert "Kubernetes" in nowhere[0]


def test_the_page_is_checked_before_the_reasons(repo_root, run_dir):
    """`Streaming` is on a Skills label AND in `c1`'s reason. A term on the page is
    covered; the three lists partition the terms and never double-count."""
    out = coverage(repo_root, run_dir)

    assert "Streaming" in " ".join(block(out, "Covered on the page"))
    assert "Streaming" not in " ".join(
        block(out, "Answered by the bank, absent from the page")
    )


def test_the_four_lists_add_up_to_the_terms_file(repo_root, run_dir):
    out = coverage(repo_root, run_dir)
    tally = counts(out)

    total = {whole for _part, whole in tally.values()}
    assert total == {8}
    assert sum(part for part, _whole in tally.values()) == 8


def test_matching_is_case_insensitive(repo_root, run_dir):
    """`kafka` is written lower-case in `terms.md` and `Kafka` on the page."""
    assert "kafka" in " ".join(block(coverage(repo_root, run_dir), "Covered on the page"))


def test_a_term_too_short_to_count_is_named_and_counted_nowhere_else(repo_root, run_dir):
    """`Go` is inside `Google`, and on a real posting `R` was inside every line of
    the page. Refused as a measurement rather than answered wrongly."""
    out = coverage(repo_root, run_dir)

    assert "Go" in block(out, "Too short to count")[0]
    assert not any(line.startswith("Go ") for line in block(out, "Covered on the page"))


# --------------------------------------------------------------------------
# It prints and never raises
# --------------------------------------------------------------------------


def test_a_run_folder_with_no_terms_file_skips_cleanly(repo_root, run_dir):
    """An old run folder must still render — and still get an answer here."""
    (run_dir / "terms.md").unlink()

    out = coverage(repo_root, run_dir)

    assert "terms.md" in out
    assert "Covered on the page" not in out


def test_a_run_folder_with_no_composed_page_skips_cleanly(repo_root, run_dir):
    (run_dir / "bullets.md").unlink()

    assert "bullets.md" in coverage(repo_root, run_dir)


def test_an_unparseable_page_prints_and_still_exits_zero(repo_root, run_dir):
    (run_dir / "bullets.md").write_text("- a line with no entry heading\n", encoding="utf-8")

    assert "coverage.py:" in coverage(repo_root, run_dir)


def test_an_unparseable_score_table_prints_and_still_exits_zero(repo_root, run_dir):
    (run_dir / "scores.md").write_text("# Scores\n\nnothing scored\n", encoding="utf-8")

    assert "coverage.py:" in coverage(repo_root, run_dir)


def test_a_missing_allocation_leaves_the_annotation_off(repo_root, run_dir):
    """It cannot say *lost the page* about a page it could not read."""
    (run_dir / "allocation.md").unlink()

    in_bank = block(
        coverage(repo_root, run_dir), "Answered by the bank, absent from the page"
    )

    assert line_for(in_bank, "Airflow").endswith("helios-payments/c2")
    assert "placed" not in line_for(in_bank, "Airflow")


def test_a_term_the_summary_carries_is_covered_by_it(repo_root, run_dir):
    """`0044` §2 — the Summary is the one line licensed to carry the posting's words.

    Leaving it out of the surface would report a term as missing from a page that
    says it in its first sentence. It cites nothing by design, so it is named as
    itself rather than as a claim — which is the reading the maker wants: the page
    has the word, and no Claim was found to put it on a line.
    """
    (run_dir / "terms.md").write_text(
        TERMS + "- streaming data\n", encoding="utf-8"
    )

    covered = block(coverage(repo_root, run_dir), "Covered on the page")

    assert "the Summary" in line_for(covered, "streaming data")


def test_a_term_only_the_summary_carries_is_not_reported_as_a_gap(repo_root, run_dir):
    """The middle list is *answered by the bank, absent from the page*, and a term in
    the Summary is on the page. Reporting it there would send the maker to write a
    Bullet for something the résumé already says."""
    (run_dir / "terms.md").write_text(TERMS + "- streaming data\n", encoding="utf-8")

    out = coverage(repo_root, run_dir)

    in_bank = block(out, "Answered by the bank, absent from the page")
    assert not [line for line in in_bank if "streaming data" in line]
