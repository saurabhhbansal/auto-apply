"""tools/bankcheck.py, driven as a command over a throwaway bank.

Every test lays out a bank folder in `tmp_path`, runs
`python tools/bankcheck.py <bank-dir>`, and asserts on the exit code, stdout and
stderr. Nothing imports bankcheck.py or bank.py: the skills depend on the command.

Two parts of the output are contract. `bank parses` on stdout is what the three
skills treat as "go on", and a failure must name the offending file, because
`bank-audit` tells the maker to leave that one out and read the rest.

Above `bank parses` sit the two advisories from
`docs/adr/0031-the-entry-header-is-built.md` — what the Static profile costs the page,
and locations written to two depths. Neither ever moves the exit code, which is what
the tests below hold: an advisory that could fail a run would be a rule, and both of
these are the maker's call.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"


# --------------------------------------------------------------------------
# Driving the tool
# --------------------------------------------------------------------------


@pytest.fixture
def bank_dir(tmp_path: Path) -> Path:
    """A throwaway copy of the fixture bank, for tests that break one file."""
    folder = tmp_path / "bank"
    shutil.copytree(FIXTURE_BANK, folder)
    return folder


def bankcheck(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/bankcheck.py", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def cost_line(stdout: str) -> str:
    """The `Static profile:` line — a `profile:` advisory may sit above it."""
    return next(line for line in stdout.splitlines() if line.startswith("Static profile:"))


def break_claim(path: Path, old: str, new: str) -> None:
    """Rewrite one line of one Entry file, so the reader has something to refuse."""
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{path} no longer contains {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# --------------------------------------------------------------------------
# A bank that parses
# --------------------------------------------------------------------------


def test_the_fixture_bank_parses(repo_root, bank_dir):
    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith("bank parses\n")
    assert result.stderr == ""


def test_an_empty_bank_parses(repo_root, tmp_path):
    """`bank-audit` §1: an empty bank is not an error — and it is what a clone has.

    `bank/jobs/` and `bank/projects/` ship holding only a `.gitkeep`, so the first
    thing this command ever does on a fresh machine is read nothing at all — and no
    `profile.md` either, which the cost line has to survive rather than crash on.
    """
    for folder in ("jobs", "projects"):
        (tmp_path / "bank" / folder).mkdir(parents=True)

    result = bankcheck(repo_root, str(tmp_path / "bank"))

    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith("bank parses\n")


def test_the_repo_bank_is_checked_when_no_folder_is_named(repo_root, tmp_path):
    """No argument means `<repo>/bank`, which is what every skill's call site is.

    Run from a copy of the repo holding the fixture bank, so the suite never reads
    whoever's real bank sits in this checkout.
    """
    copy = tmp_path / "repo"
    for folder in ("tools", "templates"):
        shutil.copytree(repo_root / folder, copy / folder)
    shutil.copytree(FIXTURE_BANK, copy / "bank")

    result = subprocess.run(
        [sys.executable, str(copy / "tools" / "bankcheck.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith("bank parses\n")
    assert str(copy / "bank" / "profile.md") in result.stdout


def test_a_missing_profile_says_what_to_copy(repo_root, bank_dir):
    (bank_dir / "profile.md").unlink()

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "copy templates/profile.example.md to bank/profile.md" in result.stdout


def test_a_profile_render_would_refuse_fails_here_first(repo_root, bank_dir):
    """A typo in the profile surfaces at the first check, not the first PDF."""
    break_claim(bank_dir / "profile.md", "email: ada.lovelace@example.com", "email:")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "`email` is blank" in result.stderr


def test_a_profile_still_holding_the_example_is_pointed_out(repo_root, bank_dir):
    shutil.copy(repo_root / "templates" / "profile.example.md", bank_dir / "profile.md")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "still hold the example's values" in result.stdout
    assert "`name`" in result.stdout


def test_phone_linkedin_and_github_are_optional(repo_root, bank_dir):
    profile = bank_dir / "profile.md"
    text = profile.read_text(encoding="utf-8")
    for key in ("phone", "linkedin", "github"):
        text = "\n".join(line for line in text.splitlines() if not line.startswith(f"{key}:"))
    profile.write_text(text + "\n", encoding="utf-8")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr


# --------------------------------------------------------------------------
# A bank that does not — named, and non-zero
# --------------------------------------------------------------------------


def test_a_number_with_no_provenance_fails_and_names_the_file_line_and_claim(
    repo_root, bank_dir
):
    """The commonest shape, per `bank-audit` §1, and the one bank.py refuses hardest."""
    break_claim(bank_dir / "jobs" / "helios-payments.md", "provenance: measured\n", "")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "helios-payments.md" in result.stderr
    assert "c1" in result.stderr
    assert "provenance" in result.stderr
    assert result.stdout == ""


def test_a_failure_is_one_named_line_rather_than_a_traceback(repo_root, bank_dir):
    """The maker reads this, and so does the next skill step. It is not a stack."""
    break_claim(bank_dir / "jobs" / "helios-payments.md", "provenance: measured\n", "")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.stderr.startswith("bankcheck.py: ")
    assert len(result.stderr.strip().splitlines()) == 1
    assert "Traceback" not in result.stderr


def test_an_entry_still_carrying_dates_fails_and_names_the_two_keys(repo_root, bank_dir):
    """The one migration this schema has had, and the message that walks it.

    A `dates:` line is an Entry file written against the old shape. Reporting it as
    two missing keys would name fields the maker has never heard of, so the reader
    says what happened instead (`docs/adr/0031-the-entry-header-is-built.md` §1).
    """
    break_claim(
        bank_dir / "jobs" / "helios-payments.md",
        "started: 2023-01\nended: present\n",
        "dates: Jan 2023 -- present\n",
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "helios-payments.md" in result.stderr
    assert "started" in result.stderr and "ended" in result.stderr
    assert "dates" in result.stderr


@pytest.mark.parametrize(
    "line, replacement, why",
    [
        ("started: 2023-01", "started: 2023-1", "the month is two digits"),
        ("started: 2023-01", "started: Jan 2023", "prose is what this replaced"),
        ("ended: present", "ended: 2023-13", "there is no thirteenth month"),
        ("ended: present", "ended: 2023", "a year is not a month"),
    ],
)
def test_a_date_that_is_not_the_stored_shape_fails(
    repo_root, bank_dir, line, replacement, why
):
    """`YYYY-MM`, and `present` only on `ended`.

    The Entry header's date string is composed from these two fields, so a value the
    reader lets through is a value that has to typeset — which is how the page came
    to carry `Jan 2026 -- Jul 2026` above `June 2025 -- July 2025` in the first place.
    """
    break_claim(bank_dir / "jobs" / "helios-payments.md", line, replacement)

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1, why
    assert "helios-payments.md" in result.stderr


def test_present_is_accepted_on_ended(repo_root, bank_dir):
    """The fixture bank's own open-ended job — the counterpart to the four above."""
    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "ended: present" in (bank_dir / "jobs" / "helios-payments.md").read_text()


def test_present_is_not_accepted_on_started(repo_root, bank_dir):
    """An entry with no start date has nothing to render (`0031` §1)."""
    break_claim(bank_dir / "jobs" / "helios-payments.md", "started: 2023-01", "started: present")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "started" in result.stderr


def test_an_entry_that_ends_before_it_begins_fails(repo_root, bank_dir):
    """The only ordering error the format admits, and it costs one comparison."""
    break_claim(bank_dir / "jobs" / "atlas-logistics.md", "started: 2020-03", "started: 2023-03")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "atlas-logistics.md" in result.stderr
    assert "2023-03" in result.stderr and "2022-12" in result.stderr


def test_a_malformed_heading_fails_and_names_the_file(repo_root, bank_dir):
    break_claim(bank_dir / "projects" / "ledger-cli.md", "## c2", "## claim-two")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "ledger-cli.md" in result.stderr


def test_an_entry_filed_under_the_wrong_type_fails(repo_root, bank_dir):
    """The folder and the frontmatter both say the type, so both have to agree."""
    shutil.move(
        bank_dir / "projects" / "ledger-cli.md", bank_dir / "jobs" / "ledger-cli.md"
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 1
    assert "ledger-cli.md" in result.stderr


def test_it_stops_at_the_first_bad_file_and_writes_nothing(repo_root, bank_dir):
    """Read-only is the contract `bank-audit` rule 3 leans on: it repairs nothing."""
    before = {
        path: path.read_bytes() for path in sorted(bank_dir.rglob("*.md"))
    }
    break_claim(bank_dir / "jobs" / "helios-payments.md", "provenance: measured\n", "")
    before[bank_dir / "jobs" / "helios-payments.md"] = (
        bank_dir / "jobs" / "helios-payments.md"
    ).read_bytes()

    bankcheck(repo_root, str(bank_dir))

    assert {path: path.read_bytes() for path in sorted(bank_dir.rglob("*.md"))} == before


# --------------------------------------------------------------------------
# The three advisories — printed, never enforced
# --------------------------------------------------------------------------


def test_the_static_profile_price_is_printed_with_its_arithmetic(
    repo_root, bank_dir, config_module
):
    """What the half of the page that never competes costs the half that does.

    The arithmetic is shown rather than the total alone: the maker is being asked to
    look at a Grade-12 row and decide whether it is worth two Bullet lines, and a
    bare `9` says nothing about where the 9 came from
    (`docs/adr/0031-the-entry-header-is-built.md` §7).
    """
    result = bankcheck(repo_root, str(bank_dir))

    rows = len(re.findall(r"^### \S+", (bank_dir / "profile.md").read_text(), re.M))
    expected = (
        config_module.HEADER_LINES
        # The prose and its own `\section{Summary}` heading, both charged flat
        # (`docs/adr/0044-the-page-opens-on-a-summary.md`, Addendum).
        + config_module.SUMMARY_LINES
        + config_module.SECTION_LINES
        # Education's heading, charged because the rows are there.
        + config_module.SECTION_LINES
        + rows * config_module.ENTRY_HEADER_LINES
    )
    line = cost_line(result.stdout)
    assert line.startswith("Static profile:")
    assert f"= {expected} of {config_module.PAGE_LINES} page lines" in line
    assert f"{rows} row(s) at {config_module.ENTRY_HEADER_LINES}" in line


def test_the_price_counts_the_education_heading_the_budget_charges(
    repo_root, bank_dir, config_module
):
    """A school added to the profile moves the number by one Entry header's worth.

    `pack.bullet_budget` charges the Education `\\section` whenever there are rows at
    all, and the Template drops the section whole when there are none — so the
    heading is part of the rows' price and is in the sum.
    """
    profile = bank_dir / "profile.md"
    profile.write_text(
        profile.read_text()
        + "\n### e2\ninstitution: A Second School\nlocation: Pune, India\n"
        "degree: Higher Secondary\ndates: 2011\n",
        encoding="utf-8",
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    expected = (
        config_module.HEADER_LINES
        + config_module.SUMMARY_LINES
        + config_module.SECTION_LINES  # \section{Summary}
        + config_module.SECTION_LINES  # \section{Education}
        + 2 * config_module.ENTRY_HEADER_LINES
    )
    assert f"= {expected} of" in result.stdout


def test_a_bank_with_no_profile_still_parses_and_says_so(repo_root, bank_dir):
    """A fresh clone has no `bank/profile.md`, and the price line must survive that."""
    (bank_dir / "profile.md").unlink()

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "no " in cost_line(result.stdout)
    assert result.stdout.endswith("bank parses\n")


def test_locations_written_to_one_depth_raise_nothing(repo_root, bank_dir):
    """The fixture bank's addresses are all `City, Country`, and `Remote` is not one."""
    result = bankcheck(repo_root, str(bank_dir))

    assert "bank locations:" not in result.stdout


def test_two_address_depths_are_reported_and_the_bank_still_parses(repo_root, bank_dir):
    """The fault this came from: `Austin, Texas, USA` above `Pune, Maharashtra`.

    Both are correct addresses and neither is the repo's to refuse, so this advises
    and exits 0 (`docs/adr/0031-the-entry-header-is-built.md` §5).
    """
    break_claim(
        bank_dir / "jobs" / "kestrel-media.md",
        "location: Mumbai, India",
        "location: Mumbai, Maharashtra, India",
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "bank locations:" in result.stdout
    assert "kestrel-media" in result.stdout
    assert "helios-payments" in result.stdout
    assert result.stdout.endswith("bank parses\n")


def test_a_location_that_is_not_an_address_is_never_compared(repo_root, bank_dir):
    """`Remote` on a job and `Open source` on a project are answers, not shallow addresses.

    Both are in the fixture bank already; this pins that the rule reads the comma and
    not the Entry's type, which is the version that fired on `orbit-analytics`.
    """
    assert "location: Remote" in (bank_dir / "jobs" / "orbit-analytics.md").read_text()

    result = bankcheck(repo_root, str(bank_dir))

    assert "orbit-analytics" not in result.stdout
    assert "bank locations:" not in result.stdout


def test_a_bank_with_no_standing_block_is_advised_and_never_refused(repo_root, bank_dir):
    """`0044` §3 — the Summary's only source for what the candidate IS, and optional.

    The fixture bank has no `## Standing`, which is the state a real bank starts in.
    It parses, exit 0, and the advisory says what the Summary is left with — because
    what goes in that block is a judgement about a life, and `0010` refused a second
    judgement of prose on the record.
    """
    assert "## Standing" not in (bank_dir / "profile.md").read_text(encoding="utf-8")

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "profile standing: no `## Standing` block" in result.stdout
    assert result.stdout.endswith("bank parses\n")


def test_a_standing_block_is_counted_a_fact_to_a_line(repo_root, bank_dir):
    """One fact per line, counted and never read — the same shallow treatment the
    Education rows get from the line above it."""
    profile = bank_dir / "profile.md"
    profile.write_text(
        profile.read_text(encoding="utf-8")
        + "\n## Standing\n\nA backend engineer.\nBuilds payment systems.\n",
        encoding="utf-8",
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "profile standing: 2 fact(s)" in result.stdout


def test_the_summary_is_in_the_price_of_the_page_that_never_competes(
    repo_root, bank_dir, config_module
):
    """`0044` §5 — charged unconditionally, and nothing else shows it spent.

    The Packer's own `Summary:` line reports it on a run; this is the maker looking
    at the bank with no run in hand, and the number has to include it or the advisory
    understates what the evidence has left to compete for.

    The term is the prose PLUS its `\\section{Summary}` heading, because that is what
    `pack.bullet_budget` takes off flat (that ADR's Addendum) — so it reads 4 where
    `SUMMARY_LINES` reads 2.
    """
    result = bankcheck(repo_root, str(bank_dir))

    charge = config_module.SUMMARY_LINES + config_module.SECTION_LINES
    assert f"Summary {charge}" in cost_line(result.stdout)


# --------------------------------------------------------------------------
# The command surface
# --------------------------------------------------------------------------


def test_too_many_arguments_is_a_usage_error(repo_root, bank_dir):
    result = bankcheck(repo_root, str(bank_dir), str(bank_dir))

    assert result.returncode == 2
    assert "usage:" in result.stderr


def test_the_supporting_entries_are_priced_and_never_refused(repo_root, bank_dir):
    """What the three sections hold, and what each costs if the page shows them.

    Advisory, like the two lines above it and for the same reason: what belongs in
    Certifications, Positions of Responsibility and Extracurriculars is a judgement
    about a life, and `0010` refused a second judgement of prose on the record. What
    it can say is arithmetic — and the arithmetic is the point, because a supporting
    entry costs nothing until it places and then costs a whole heading plus its rows
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §9).
    """
    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "bank supporting: 4 entry(s)" in result.stdout
    assert "certifications: 2 entry(s) — 4 line(s)" in result.stdout
    assert "responsibilities: 1 entry(s) — 3 line(s)" in result.stdout
    assert "extracurriculars: 1 entry(s) — 3 line(s)" in result.stdout
    assert result.stdout.endswith("bank parses\n")


def test_a_bank_with_no_supporting_entries_says_nothing_about_them(repo_root, bank_dir):
    """The absent state is silent, unlike the `## Standing` block's.

    A line saying *no certifications* would fire on every fresh clone and price an
    absence nobody has decided about yet — which is the opposite of the Standing
    advisory, where the absence is exactly the interesting state because the Summary
    has nothing else to describe the candidate with.
    """
    for folder in ("certifications", "responsibilities", "extracurriculars"):
        for path in (bank_dir / folder).glob("*.md"):
            path.unlink()

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "bank supporting:" not in result.stdout


def test_a_project_stack_naming_an_unclaimed_technology_is_named(repo_root, bank_dir):
    """0057 §3 — the stack is typeset and traced by nothing, so bankcheck says so."""
    path = bank_dir / "projects" / "feedforge.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("type: project\n", "type: project\nstack: Go, SQLite, Kubernetes\n", 1),
        encoding="utf-8",
    )

    result = bankcheck(repo_root, str(bank_dir))

    assert result.returncode == 0, result.stderr
    assert "project stack:" in result.stdout
    assert "feedforge: Kubernetes" in result.stdout
