"""The ATS X-ray, driven as a command over a throwaway run folder.

`docs/adr/0052-the-x-ray-runs-before-the-page-is-written.md`.

Same convention as its neighbours: the tool is run as a command, the run folder's
files are the contract, and nothing imports its internals.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"

TERMS = """# Terms: acme-backend-engineer

## Must-have
- Kafka
- Postgres
- Kubernetes
- Go

## Nice-to-have
- Terraform
- Elixir
"""

SCORES = """# Scores: a hand-written fixture

| entry | claim | type | ended | score | width | reason |
|---|---|---|---|---|---|---|
| helios-payments | c1 | job | present | 1.00 | 1 | the streaming must-have |
| helios-payments | c2 | job | present | 0.70 | 1 | Postgres at scale |
"""


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    shutil.copytree(FIXTURE_BANK, tmp_path / "bank")
    folder = tmp_path / "runs" / "acme-backend-engineer"
    folder.mkdir(parents=True)
    (folder / "terms.md").write_text(TERMS, encoding="utf-8")
    (folder / "scores.md").write_text(SCORES, encoding="utf-8")
    return folder


def xray(repo_root: Path, run_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/xray.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def pack(repo_root: Path, run_dir: Path, *flags: str) -> None:
    result = subprocess.run(
        [sys.executable, "tools/pack.py", str(run_dir), *flags],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_it_writes_xray_md_and_exits_zero(repo_root, run_dir):
    """Advisory, like `coverage.py`: it reports, it never gates."""
    pack(repo_root, run_dir)

    result = xray(repo_root, run_dir)

    assert result.returncode == 0
    assert (run_dir / "xray.md").is_file()
    assert "Coverage:" in result.stdout


def test_the_score_prints_its_own_arithmetic(repo_root, run_dir):
    """`0052` §2: one number, ours, with the working under it.

    The whole reason it is not five per-platform numbers is that no vendor publishes
    a scoring algorithm — so the one number it does print has to be auditable.
    """
    pack(repo_root, run_dir)
    xray(repo_root, run_dir)

    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    assert "must-have terms answered" in report
    assert "nice-to-have answered" in report
    assert "red flags" in report
    assert "no number here is any platform's" in report


def test_a_must_have_no_placed_evidence_carries_is_invisible_without(repo_root, run_dir):
    """The list the maker acts on. `Kubernetes` is nowhere in the fixture bank."""
    pack(repo_root, run_dir)
    xray(repo_root, run_dir)

    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    invisible = report.split("## Invisible without")[1].split("##")[0]
    assert "Kubernetes" in invisible


def test_a_term_the_evidence_carries_is_credited_to_the_claim(repo_root, run_dir):
    """A verdict names the claim behind it, so every line is a lead that can be checked."""
    pack(repo_root, run_dir)
    xray(repo_root, run_dir)

    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    assert "helios-payments/c1" in report


def test_it_reads_the_evidence_and_never_the_composed_page(repo_root, run_dir):
    """`0052` §1: it runs before a Bullet exists, so it cannot be reading one.

    The guard that matters — a report scoring the prose could be satisfied by editing
    the prose, which is the failure `0041` refused. Scoring the evidence cannot be.
    """
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(
        "## helios-payments\n- helios-payments/c1: Kubernetes Kubernetes Kubernetes\n",
        encoding="utf-8",
    )

    xray(repo_root, run_dir)
    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    invisible = report.split("## Invisible without")[1].split("##")[0]
    assert "Kubernetes" in invisible, "the X-ray read bullets.md and was fooled by it"


def test_a_short_term_is_declined_rather_than_counted(repo_root, run_dir):
    """`Go` is inside `Google`. Under MIN_TERM_CHARS a substring count means nothing."""
    pack(repo_root, run_dir)
    xray(repo_root, run_dir)

    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    assert "Too short to count" in report
    assert "`Go`" in report.split("Too short to count")[1]


def test_an_entry_with_no_lead_is_not_a_red_flag(repo_root, run_dir):
    """0057 §5 — a bare heading is the normal résumé shape, not a hole."""
    pack(repo_root, run_dir)
    xray(repo_root, run_dir)

    report = (run_dir / "xray.md").read_text(encoding="utf-8")

    assert "no lead line" not in report


def test_it_survives_a_run_folder_with_no_allocation(repo_root, run_dir):
    """An advisory never fails a run, and an old folder still gets an answer."""
    result = xray(repo_root, run_dir)

    assert result.returncode == 0
    assert (run_dir / "xray.md").is_file()
