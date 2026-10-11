"""`tools/bank.py`'s place in the build, and the fixture bank's contract.

Two things here that `tests/test_render.py` cannot say. The import boundary: bank.py
is stdlib-only and is imported by `render.py` and nothing else. And what the fixture
bank must keep covering — both Entry types, both Provenance tiers, a Confidence flag,
a `needs-interview` mark, and enough evidence to overflow a page — since that corpus
is what every render test, the calibration and the three skills run against.

bank.py's own parsing is covered where it is used, through `render.py` at the CLI.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

from pack_constants import skills_charge

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"


def imports_of(path: Path) -> set[str]:
    imported = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])
    return imported


# --------------------------------------------------------------------------
# The import boundary
# --------------------------------------------------------------------------
def test_bank_py_is_stdlib_only(repo_root):
    """The bank is read by a line-based parser, not by a dependency.

    Jinja2 is the system's one third-party dependency and it is confined to
    `render.py` (`docs/adr/0007-rendering-approach.md` §10). A parser here would be
    a second one, and it would push a schema back onto a store whose whole design is
    hand-edited prose.
    """
    outside_stdlib = imports_of(repo_root / "tools" / "bank.py") - sys.stdlib_module_names
    assert not outside_stdlib, f"bank.py must be stdlib-only, but imports {outside_stdlib}"


def test_bank_py_is_imported_by_render_py(repo_root):
    """It is the Renderer's reader — the trace check resolves a claim id through it."""
    assert "bank" in imports_of(repo_root / "tools" / "render.py")


#: The only files permitted to name `bank`. `render.py` reads the bank to resolve a
#: citation; `bankcheck.py` exists to read it and say whether it parsed. Nothing else
#: may, and the list is short on purpose — see the test below.
#: The files allowed to read the bank. `coverage.py` joined them when a supporting
#: row's built label reached the page: the label is the entry's own `title` and `org`,
#: it is where a posting's term most often appears verbatim, and the coverage read
#: would otherwise report a term missing from a page that prints it
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §3).
#: It is a safe addition for the reason the rule below is about direction: `pack.py`
#: does not import `coverage.py`, `coverage.py` imports `pack.py`.
#: `xray.py` is on the list because it genuinely reads Evidence — `0052` §1's whole
#: point is that it scores the BANK's material rather than composed prose, which is
#: what makes it safe to consult while writing. The invariant this file protects is
#: unmoved: `pack.py` stays bank-blind, and nothing pack.py imports reaches xray.py.
BANK_READERS = ("bank.py", "bankcheck.py", "render.py", "coverage.py", "xray.py")


def test_bankcheck_py_is_the_only_command_over_bank_py(repo_root):
    """bank.py stays a library; the parse check is the one thing that shells out to it.

    All three skills tell the maker to run this after a bank write, so it has to be a
    real script rather than an inline `python -c`, which no narrow permission grant
    could cover without granting arbitrary Python to every clone.
    """
    source = (repo_root / "tools" / "bankcheck.py").read_text(encoding="utf-8")
    assert "bank" in imports_of(repo_root / "tools" / "bankcheck.py")
    assert '__name__ == "__main__"' in source, "the parse check is a command, not a library"
    assert "def main" not in (repo_root / "tools" / "bank.py").read_text(encoding="utf-8")


def test_nothing_but_the_bank_readers_imports_bank_py(repo_root):
    """The Packer's bank-blindness is a property of the whole `tools/` folder.

    `test_pack.py` holds it for pack.py itself; this holds it for anything that gets
    added beside it, since an import chain through a third file would be just as
    effective at making the Packer bank-aware. `bankcheck.py` is on the list and
    `lengths.py` deliberately is not — a bank reader that pack.py could one day
    import is the failure mode, and the length pass measures sentences, which is a
    fact about the sentence rather than about the bank.
    """
    for path in sorted((repo_root / "tools").glob("*.py")):
        if path.name in BANK_READERS:
            continue
        assert "bank" not in imports_of(path), f"{path.name} must not import bank.py"


# --------------------------------------------------------------------------
# The fixture bank
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def fixture_files() -> dict[str, str]:
    """Every fixture Entry file, keyed by `<folder>/<slug>`."""
    return {
        f"{path.parent.name}/{path.stem}": path.read_text(encoding="utf-8")
        for folder in FOLDERS
        for path in sorted((FIXTURE_BANK / folder).glob("*.md"))
    }


#: Every folder of the bank, and the `type` its files must declare. Written out
#: rather than read from `bank.TYPE_FOLDERS`, which is the point: this file holds the
#: fixture bank to the layout independently of the parser that reads it.
FOLDERS = {
    "jobs": "job",
    "projects": "project",
    "certifications": "certification",
    "responsibilities": "responsibility",
    "extracurriculars": "extracurricular",
}


def claim_blocks(text: str) -> list[str]:
    """Each `## c<n>` section of one Entry file, below its id heading.

    The heading is dropped because `c1` is itself a digit, and a claim that holds no
    number at all is one of the things the fixture bank has to keep covering.
    """
    return [
        block.split("\n", 1)[1] for block in re.split(r"^## (?=c\d+$)", text, flags=re.M)[1:]
    ]


def every_claim(fixture_files: dict[str, str]) -> list[tuple[str, str]]:
    return [(name, block) for name, text in fixture_files.items() for block in claim_blocks(text)]


def literal_of(path: Path, name: str) -> str:
    """The string a module assigns to `NAME`, bare or wrapped in `re.compile(...)`.

    Read out of the source rather than imported, which is the suite's convention for
    a constant that has to be compared across the bank-blind seam: importing both
    would be the one thing `pack.py` may not do.
    """
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            continue
        value = node.value.args[0] if isinstance(node.value, ast.Call) else node.value
        if isinstance(value, ast.Constant):
            return value.value
        if isinstance(value, ast.JoinedStr):
            # An f-string built out of another pattern: the hole comes back as
            # `{NAME}` so the caller can substitute the thing it names.
            return "".join(
                part.value
                if isinstance(part, ast.Constant)
                else "{" + ast.unparse(part.value) + "}"
                for part in value.values
            )
        raise AssertionError(f"`{name}` in {path} is not a string literal")
    raise AssertionError(f"no `{name}` assignment in {path}")


def literal_of_dict(path: Path, name: str) -> str:
    """The source of whatever a module assigns to `NAME`, for `ast.literal_eval`.

    `literal_of` above unwraps `re.compile(...)` and returns a string's value; this
    hands back the expression's own source, which is what a dict or a tuple needs.
    Read rather than imported for the same reason: comparing a bank constant with a
    Packer constant must not import both.
    """
    source = path.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.get_source_segment(source, node.value)
    raise AssertionError(f"no `{name}` assignment in {path}")


def test_the_packers_end_date_pattern_is_the_banks(repo_root):
    """One shape for an end date, in two files, held equal here.

    `bank.py` owns it: the Entry header's dates are composed from `started`/`ended`,
    so the bank decides what a date is. `pack.py` restates it rather than importing
    it, because the Packer may import nothing but the stdlib and `config` — the same
    two-file arrangement `CLAIM_ID` and `ENTRY_SLUG` already have. Drift between the
    two is a date the Packer accepts and the bank refuses, discovered in a run rather
    than here (`docs/adr/0031-the-entry-header-is-built.md` §3).
    """
    bank_py = repo_root / "tools" / "bank.py"
    owned = literal_of(bank_py, "MONTH_PATTERN")
    ended = literal_of(bank_py, "ENDED_PATTERN").replace("{MONTH_PATTERN}", owned)

    assert literal_of(repo_root / "tools" / "pack.py", "ENDED") == f"^{ended}$"


def test_the_packers_section_names_are_the_banks(repo_root):
    """The three supporting sections, named in two files, held equal here.

    `bank.py` owns the type -> section mapping because the type is a bank fact and
    the folder is the type. `pack.py` restates the section NAMES because the Packer
    may import nothing but the stdlib and `config`, and it has to validate the
    `## Sections` table's first column — the same two-file arrangement the month
    pattern above already has, and the same failure if it drifts: a section name the
    Packer accepts and the Renderer cannot route
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §1).

    Order matters as well as membership: it is the page's order and the residue
    fill's order, and `pack.SUPPORTING_SECTIONS` is what both read.
    """
    mapping = ast.literal_eval(literal_of_dict(repo_root / "tools" / "bank.py", "SECTION_OF_TYPE"))
    types = ast.literal_eval(literal_of_dict(repo_root / "tools" / "bank.py", "SUPPORTING_TYPES"))
    sections = ast.literal_eval(
        literal_of_dict(repo_root / "tools" / "pack.py", "SUPPORTING_SECTIONS")
    )
    headings = ast.literal_eval(
        literal_of_dict(repo_root / "tools" / "pack.py", "SECTION_HEADINGS")
    )

    assert tuple(mapping[type_] for type_ in types) == tuple(sections)
    assert set(headings) == set(sections), "every section is named on the page"


def test_the_five_entry_types_each_have_exactly_one_folder(repo_root):
    """The folder IS the type, so the mapping is a bijection or a file has two homes."""
    bank_py = repo_root / "tools" / "bank.py"
    folders = ast.literal_eval(literal_of_dict(bank_py, "TYPE_FOLDERS"))
    types = ast.literal_eval(literal_of_dict(bank_py, "COMPETING_TYPES")) + ast.literal_eval(
        literal_of_dict(bank_py, "SUPPORTING_TYPES")
    )

    assert set(folders) == set(types)
    assert len(set(folders.values())) == len(folders)


def test_the_fixture_bank_holds_every_entry_type(fixture_files):
    """All five, because each one routes to a different section of the page."""
    for folder in FOLDERS:
        assert any(name.startswith(f"{folder}/") for name in fixture_files), folder


def test_every_fixture_entry_declares_the_type_its_folder_says(fixture_files):
    """The filename slug is the Entry id and the folder is the type, so the two must
    agree — a `job` filed under `projects/` routes to the wrong section."""
    for name, text in fixture_files.items():
        folder = name.split("/")[0]
        assert f"type: {FOLDERS[folder]}" in text, f"{name} does not declare {FOLDERS[folder]}"


def test_a_credential_with_no_expiry_writes_its_issue_month_twice(fixture_files):
    """How `started == ended` is written, and what it makes the row print.

    `row_dates` collapses the pair to one month, so the page shows `Mar 2025` rather
    than a range to itself. Never `present`: *present* says still going, and an exam
    that was passed is not going
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §3,
    `ingest` §9.2).
    """
    certs = {name: text for name, text in fixture_files.items() if name.startswith("certifications/")}
    assert certs
    for name, text in certs.items():
        started = re.search(r"^started: (\S+)$", text, re.M).group(1)
        ended = re.search(r"^ended: (\S+)$", text, re.M).group(1)
        assert ended != "present", f"{name} writes `ended: present` on a credential"
        assert ended >= started, name


@pytest.mark.parametrize(
    "marker, why",
    [
        ("provenance: measured", "a number from a real measurement"),
        ("provenance: estimated", "a number believed but not measured"),
        ("confidence: uncertain", "the hand-set Confidence flag, which fires a Fork"),
        ("needs-interview: yes", "a Claim owed an ingestion interview"),
    ],
)
def test_the_fixture_bank_covers_every_mark_a_claim_can_carry(fixture_files, marker, why):
    hits = [name for name, text in fixture_files.items() if marker in text]
    assert hits, f"no fixture claim carries `{marker}` — {why}"


def test_every_fixture_entry_stores_its_dates_in_the_machine_shape(fixture_files):
    """`started`/`ended`, and no `dates:` left anywhere in the corpus.

    The header's date string is composed from these two, so a fixture that kept the
    old free-text field would render nothing and fail the parse
    (`docs/adr/0031-the-entry-header-is-built.md` §1).
    """
    for name, text in fixture_files.items():
        assert re.search(r"^started: \d{4}-\d{2}$", text, re.M), name
        assert re.search(r"^ended: (\d{4}-\d{2}|present)$", text, re.M), name
        assert not re.search(r"^dates:", text, re.M), f"{name} still carries `dates:`"


def test_the_fixture_bank_holds_an_entry_that_has_not_ended(fixture_files):
    """`ended: present` is the one value that renders as a word rather than a month,
    so the corpus has to carry one or nothing ever composes `Present`."""
    assert any(
        re.search(r"^ended: present$", text, re.M) for text in fixture_files.values()
    )


def test_the_fixture_bank_holds_a_purely_qualitative_claim(fixture_files):
    """A Claim with no number *and no digits in its prose* — the only thing that can
    prove the Number-trace check catches a qualitative claim that grew a number."""
    qualitative = [
        name
        for name, block in every_claim(fixture_files)
        if "number:" not in block and not re.search(r"\d", block)
    ]
    assert qualitative, "no fixture claim is free of digits altogether"


def test_every_fixture_number_rides_with_a_provenance(fixture_files):
    """The pair travels together: a tier-less number renders flat and traces clean."""
    for name, block in every_claim(fixture_files):
        if "number:" in block:
            assert "provenance:" in block, f"a claim in {name} has a number with no tier"


def test_every_fixture_assertion_fits_one_bullet_line(config_module, fixture_files):
    """The assertion is render's default phrasing, so it has to fit the page.

    It is also what `tests/test_render.py` composes its overflow case from, which is
    only a test of the *page* if none of those Bullets is over-length.
    """
    for name, text in fixture_files.items():
        for assertion in re.findall(r"^\*\*Assertion:\*\* (.+)$", text, re.M):
            assert len(assertion.rstrip(".")) <= config_module.CHARS_PER_BULLET, (
                f"{name} has a {len(assertion)}-character assertion, over the "
                f"{config_module.CHARS_PER_BULLET}-character line: {assertion}"
            )


def test_an_estimated_fixture_assertion_softens_its_own_number(fixture_files):
    """Downgrade-only, written into the corpus: an estimated number may only render
    softened, so an assertion that states one flat could never be used verbatim."""
    for name, block in every_claim(fixture_files):
        if "provenance: estimated" not in block:
            continue
        assertion = re.search(r"^\*\*Assertion:\*\* (.+)$", block, re.M)
        assert assertion, f"a claim in {name} has no assertion"
        if re.search(r"(?<![A-Za-z0-9.])\d", assertion.group(1)):
            assert "~" in assertion.group(1), (
                f"{name}: an estimated claim's assertion states a number flat: "
                f"{assertion.group(1)}"
            )


def test_the_fixture_bank_is_big_enough_to_overflow_a_page(config_module, fixture_files):
    """Allocating every Claim must not fit, or the page-count assert has no fixture.

    The arithmetic is docs/calibration.md's, so a re-calibration changes what this
    demands of the fixture bank rather than breaking it.
    """
    entries = len(fixture_files)
    claims = len(every_claim(fixture_files))
    sections = 2 + 1  # Experience, Projects, Education — Skills carries its own
    overhead = (
        config_module.HEADER_LINES
        + sections * config_module.SECTION_LINES
        + config_module.ENTRY_HEADER_LINES  # one Education row
        + skills_charge(config_module)  # the reservation, heading included
    )
    budget = config_module.PAGE_LINES - overhead
    spent = entries * config_module.ENTRY_HEADER_LINES + claims

    assert spent > budget + 4, (
        f"the fixture bank spends {spent} lines against a {budget}-line budget, which is "
        f"not decisively over — add an entry, or the overflow case stops proving anything"
    )


def test_the_fixture_score_table_scores_every_claim_and_nothing_else(fixture_files):
    """Every Claim of a COMPETING entry gets a row — including the zeros, because the
    Omission view needs the losers — and no row names a Claim that is not there.

    The two files drift apart the moment either is edited alone, and the drift is
    silent: a missing row is simply a Claim that never competed.

    **A supporting entry's claims are not in this table and must not be.** They are
    never scored: a `certification` takes no Bullet slot, so a row for it would put an
    Entry into the competition that has no business in it, and `pack.py` refuses a
    slug that appears in both tables
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §2).
    """
    competing = {
        name: text
        for name, text in fixture_files.items()
        if FOLDERS[name.split("/")[0]] in ("job", "project")
    }
    in_bank = {
        f"{name.split('/')[1]}/{claim_id}"
        for name, text in competing.items()
        for claim_id in re.findall(r"^## (c\d+)$", text, re.M)
    }
    table = (FIXTURE_BANK.parent / "scores.md").read_text(encoding="utf-8")
    scored = {
        f"{entry}/{claim}"
        for entry, claim in re.findall(r"^\| (\S+) \| (c\d+) \|", table, re.M)
    }
    assert scored == in_bank, (
        f"scored but not in the bank: {sorted(scored - in_bank)}; "
        f"in the bank but unscored: {sorted(in_bank - scored)}"
    )


def test_the_fixture_profile_matches_the_committed_contract(repo_root):
    """`profile.md` is validated by field name against `templates/profile.example.md`,
    so the fixture has to carry exactly those keys or every render test fails at
    step 1 for a reason that has nothing to do with what it was testing."""
    example = (repo_root / "templates" / "profile.example.md").read_text(encoding="utf-8")
    fixture = (FIXTURE_BANK / "profile.md").read_text(encoding="utf-8")
    assert field_names(fixture) == field_names(example)


def field_names(profile: str) -> set[str]:
    return set(re.findall(r"^([a-z-]+):", profile, re.M))


# --------------------------------------------------------------------------
# 0057 §3 — a project's one-row header
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def bank_module(repo_root):
    """tools/bank.py, imported by path — tools/ is not a package."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("auto_apply_bank", repo_root / "tools" / "bank.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _project(extra: str) -> str:
    return (
        "---\ntype: project\ntitle: thing\nstarted: 2026-01\nended: present\n"
        + extra
        + "---\n\n## c1\n\n**Assertion:** Built it.\n\n**Evidence:** It was built.\n"
    )


def test_a_project_needs_no_org_or_location_and_carries_stack_and_link(bank_module, tmp_path):
    entry = bank_module.parse_entry(
        _project("stack: Python, LaTeX\nlink: github.com/you/thing\n"), "thing", tmp_path / "t.md"
    )
    assert (entry.org, entry.location) == ("", "")
    assert entry.stack == "Python, LaTeX"
    assert entry.link == "github.com/you/thing"


@pytest.mark.parametrize("link", ["https://github.com/you/thing", "github.com/you/my#thing"])
def test_a_project_link_is_written_as_the_page_shows_it(bank_module, tmp_path, link):
    with pytest.raises(bank_module.BankError, match="link"):
        bank_module.parse_entry(_project(f"link: {link}\n"), "thing", tmp_path / "t.md")


def test_a_project_link_may_carry_an_underscore_or_a_tilde(bank_module, tmp_path):
    """The \\href target is passed raw and only the visible text is escaped."""
    entry = bank_module.parse_entry(
        _project("link: github.com/you/my_thing/~x\n"), "thing", tmp_path / "t.md"
    )
    assert entry.link == "github.com/you/my_thing/~x"


def test_a_job_still_needs_its_employer_and_office(bank_module, tmp_path):
    text = _project("").replace("type: project", "type: job")
    with pytest.raises(bank_module.BankError, match="org"):
        bank_module.parse_entry(text, "thing", tmp_path / "t.md")
