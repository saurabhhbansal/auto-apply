"""The plain-English read, driven as a command over a throwaway run folder.

`docs/adr/0056-the-bullet-is-written-in-plain-english.md`.

Same convention as its neighbours: the tool is run as a command, the run folder's
files are the contract, and nothing imports its internals. The `--paw` half is not
covered here — it needs an optional package that builds a native extension and
downloads a model, so the suite asserts only that its absence is reported and does
not break the pass.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"

SCORES = """# Scores: a hand-written fixture

| entry | claim | type | ended | score | width | reason |
|---|---|---|---|---|---|---|
| helios-payments | c1 | job | present | 1.00 | 1 | the streaming must-have |
| helios-payments | c2 | job | present | 0.70 | 1 | Postgres at scale |
"""

CLAUDISH = """## Summary
A final-year student building data systems.

## helios-payments
- helios-payments/c1: Kept the ledger honest to its evidence by owning the arithmetic \
outside the model, rather than trusting it
- helios-payments/c2: Held the schema's rules in the database: a check per column, a \
constraint per row, and an index on the rest

## Skills

### Languages
- Go (helios-payments/c1)

### Data
- Postgres (helios-payments/c2)
"""

PLAIN = """## Summary
A final-year student building data systems.

## helios-payments
- helios-payments/c1: Cut checkout p99 latency 40% by batching offset commits in the Go \
Kafka consumer
- helios-payments/c2: Own a payments ledger end to end, from double-entry schema design \
through on-call

## Skills

### Languages
- Go (helios-payments/c1)

### Data
- Postgres (helios-payments/c2)
"""


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    shutil.copytree(FIXTURE_BANK, tmp_path / "bank")
    folder = tmp_path / "runs" / "acme-backend-engineer"
    folder.mkdir(parents=True)
    (folder / "scores.md").write_text(SCORES, encoding="utf-8")
    return folder


def pack(repo_root: Path, run_dir: Path, *flags: str) -> None:
    result = subprocess.run(
        [sys.executable, "tools/pack.py", str(run_dir), *flags],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def plainish(repo_root: Path, run_dir: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/plainish.py", str(run_dir), *flags],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def test_it_reports_and_never_gates(repo_root, run_dir):
    """`0056` §3: advisory, the standing `xray.py` and `coverage.py` hold.

    A page full of markers still exits 0 — what decides is the cold read, and a lint
    over a fixed vocabulary that could fail a run would be answered by making the
    page worse.
    """
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(CLAUDISH, encoding="utf-8")

    result = plainish(repo_root, run_dir)

    assert result.returncode == 0
    assert result.stdout.strip(), "a Claudish page reported nothing"


def test_it_names_the_families_the_guide_names(repo_root, run_dir):
    """Each marker is one `plain-english.md` move, so the finding names which."""
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(CLAUDISH, encoding="utf-8")

    out = plainish(repo_root, run_dir).stdout

    assert "metaphor" in out, "`kept … honest` and `held the rules in` went unseen"
    assert "contrast" in out, "`rather than` went unseen"
    assert "list" in out, "the colon holding three claims in a row went unseen"


def test_a_plain_page_reports_nothing(repo_root, run_dir):
    """The empty report is the pass. `0030` §2's species: a list, or an empty one."""
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(PLAIN, encoding="utf-8")

    result = plainish(repo_root, run_dir)

    assert result.returncode == 0
    assert result.stdout == "", result.stdout


def test_a_standard_compound_is_not_a_finding(repo_root, run_dir):
    """`plain-english.md` §1.2's exception, and the spec's own rule.

    `server-side` and `row-level` are what these things are called. A lint that
    reported them would be obeyed by writing a worse page.
    """
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(
        PLAIN.replace(
            "Own a payments ledger end to end, from double-entry schema design through on-call",
            "Verified every check-in server-side, with row-level security on the invites table",
        ),
        encoding="utf-8",
    )

    out = plainish(repo_root, run_dir).stdout

    assert "compound" not in out, out


def test_a_lost_citation_is_reported(repo_root, run_dir):
    """The half that is not about voice.

    Composing for voice means rewriting, and a rewrite is where a ref goes missing.
    `render.py` fails the run on the same mismatch; this names it before a compile
    is spent.
    """
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(
        PLAIN.replace("- helios-payments/c2: ", "- helios-payments/c1: "),
        encoding="utf-8",
    )

    out = plainish(repo_root, run_dir).stdout

    assert "citation helios-payments/c2" in out, out


def test_the_paw_backstop_is_optional(repo_root, run_dir):
    """`0056` §4: an unvendored dependency no run may require.

    Absent, the flag prints one line saying so and the rest of the pass still runs —
    which is what keeps the page's voice checkable on a machine that cannot build
    `llama-cpp-python`.
    """
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(CLAUDISH, encoding="utf-8")

    result = plainish(repo_root, run_dir, "--paw", "--paw-lib=/nonexistent")

    assert result.returncode == 0
    assert "paw programasweights not importable" in result.stdout
    assert "metaphor" in result.stdout, "the marker report stopped at the missing package"


def test_it_reads_the_leads_too(repo_root, run_dir):
    """A lead is the widest line on the page and composed prose like any other."""
    pack(repo_root, run_dir)
    (run_dir / "bullets.md").write_text(
        PLAIN.replace(
            "## helios-payments\n",
            "## helios-payments\nLead: Held the reporting cycle to a monthly rhythm, "
            "rather than a weekly one\n",
        ),
        encoding="utf-8",
    )

    out = plainish(repo_root, run_dir).stdout

    assert "helios-payments/lead" not in out, "the ref is not printed; the line number is"
    assert "Held the reporting cycle" in out, out
