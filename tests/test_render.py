"""tools/render.py, driven as a command over a throwaway run folder.

Every test lays out a repo-shaped `tmp_path` — the fixture bank beside a
`runs/<slug>/` folder — writes `allocation.md` and `bullets.md` by hand, runs
`python tools/render.py <run-dir>`, and asserts on the exit code, stderr and the
files that came back. Nothing imports render.py or bank.py.

Two things make that work with no test-only code path in the tool. The bank is found
relative to the run folder (`<run>/../../bank`), which is the real layout. And the
fixture bank's assertions all sit inside CHARS_PER_BULLET and carry their own
softening tildes, so a Bullet that is just the claim's assertion passes every lint —
which lets a test about one lint say nothing about the others.

Tests expecting a PDF are marked `needs_pdflatex` and skip where TinyTeX is absent;
the lint failures stay runnable anywhere.
"""

from __future__ import annotations

import inspect
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from allocation_md import placed

FIXTURE_BANK = Path(__file__).resolve().parent / "fixtures" / "bank"

#: (claim id, the Bullet prose) per placed Entry. The prose is written out rather
#: than lifted from the bank, so a test reads as what it is: this is what Opus
#: composed for this JD.
PLACED = [
    (
        "helios-payments",
        "job",
        [
            ("c1", "Cut checkout p99 latency 40% by batching commits in the order-ingest consumer"),
            ("c3", "Own the payments ledger end to end, from schema design to incident review"),
        ],
    ),
    (
        "ledger-cli",
        "project",
        [("c3", "Wrote the tutorial that turns a new user's first ledger file into a report")],
    ),
]

#: The Skills section as `(category label, [(skill, backing claim)])`. Two rows,
#: because a section is two rows or it is not a section, and every row here is
#: comfortably one typeset line — which is what lets `write_allocation` charge them
#: as `[1, 1]` without restating render.py's own arithmetic back at it.
SKILLS = [
    ("Languages", [("Go", "helios-payments/c1"), ("Rust", "ledger-cli/c1")]),
    ("Platform", [("Kafka", "helios-payments/c1"), ("PostgreSQL", "helios-payments/c1")]),
]


def skill_lines(skills=SKILLS) -> list[int]:
    """The typeset line count per row, as `--skills-rows` would carry it."""
    return [1] * len(skills)


def fixture_ended(slug: str, type_: str) -> str:
    """The `ended` the fixture bank holds for one Entry.

    Read out of the bank rather than made up, because `allocation.md`'s copy of it is
    checked against the bank's own field before anything renders
    (`docs/adr/0031-the-entry-header-is-built.md` §4). A literal here would make every
    render test a test of that check.
    """
    path = FIXTURE_BANK / f"{type_}s" / f"{slug}.md"
    if not path.is_file():
        # An allocation naming an Entry the bank does not hold is a test of its own,
        # and it fails on the slug before anything looks at a date.
        return "present"
    match = re.search(r"^ended: (\S+)$", path.read_text(encoding="utf-8"), re.M)
    assert match, f"{path} carries no `ended` line"
    return match.group(1)


# --------------------------------------------------------------------------
# Driving the tool
# --------------------------------------------------------------------------


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    """A repo-shaped throwaway: the fixture bank, and a run folder beside it."""
    shutil.copytree(FIXTURE_BANK, tmp_path / "bank")
    folder = tmp_path / "runs" / "acme-backend-engineer"
    folder.mkdir(parents=True)
    return folder


def render(repo_root: Path, run_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/render.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def render_ok(repo_root: Path, run_dir: Path) -> subprocess.CompletedProcess:
    result = render(repo_root, run_dir)
    assert result.returncode == 0, f"render.py failed: {result.stderr}"
    return result


def render_fails(repo_root: Path, run_dir: Path, *names: str) -> str:
    """Run it, insist it failed, and hand back the message that named the offender."""
    result = render(repo_root, run_dir)
    assert result.returncode == 1, (
        f"expected a hard failure, got {result.returncode}: {result.stdout}{result.stderr}"
    )
    for name in names:
        assert name in result.stderr, f"the failure does not name {name!r}:\n{result.stderr}"
    return result.stderr


def skills_paragraph(skill_lines_: list[int]) -> str:
    """The Packer's `Skills:` line — what the second pass charged the section.

    render.py reads this back, so a fixture that omits it is refused as a
    reservation. The two shapes are the Packer's two final-pass forms.
    """
    if not skill_lines_:
        return "Skills: no section — 0 composed row(s) is under the 2-row floor."
    return (
        f"Skills: {len(skill_lines_)} row(s), "
        f"{','.join(str(n) for n in skill_lines_)} typeset line(s) each, "
        f"charged 4 line(s) including the heading."
    )


def write_allocation(
    run_dir: Path, placed=PLACED, skill_lines_=None, widths=None, ended=None
) -> None:
    """`allocation.md` in the shape tools/pack.py writes it.

    `widths` is `{"<slug>/<claim>": 2}` for the slots granted a second line; every
    other slot is written as `1 line`. The claim line's third field is contract —
    `render.py` reads the granted width out of it — so it is written here rather
    than defaulted (`docs/adr/0025-bullet-wrap-cost.md` §6).

    `ended` is `{"<slug>": "<YYYY-MM>"}`, for a test that moves a bank entry's own
    `ended` and needs the Packer's copy of it to move too. Left alone, each entry's
    line carries what the fixture bank holds, since a mismatch is a hard failure of
    its own (`docs/adr/0031-the-entry-header-is-built.md` §4).
    """
    if skill_lines_ is None:
        skill_lines_ = skill_lines()
    widths = widths or {}
    lines = [
        "# Allocation: acme-backend-engineer",
        "",
        "Budget: 36 lines for Entry headers and Bullets, of 50 on the page.",
        "",
        skills_paragraph(skill_lines_),
        "",
        "## Placed",
        "",
        "In page order — every `job` under Experience, then every `project` under Projects.",
        "",
    ]
    for slug, type_, claims in placed:
        lines.append(
            f"### {slug} — {type_} — "
            f"ended {(ended or {}).get(slug) or fixture_ended(slug, type_)} — "
            f"entry score 0.80 — {len(claims)} bullets"
        )
        lines += [
            f"- {slug}/{claim_id} — 0.80 — "
            f"{widths.get(f'{slug}/{claim_id}', 1)} line"
            f"{'s' if widths.get(f'{slug}/{claim_id}', 1) > 1 else ''} — "
            f"a fixture reason"
            for claim_id, _ in claims
        ]
        lines.append("")
    lines += ["## Silent calls", "", "Nothing was decided by rule on this run.", ""]
    lines += ["## Did not place", "", "### Entries", "", "Every scored Entry placed.", ""]
    (run_dir / "allocation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


#: The Summary every fixture page carries. It is a fixed part of the page and the
#: budget charges SUMMARY_LINES for it on every run, so a `bullets.md` without one is
#: not a page render.py will look at — which makes it fixture furniture rather than
#: something each test opts into (docs/adr/0044-the-page-opens-on-a-summary.md §5).
#: Carries no figure, because none of them may.
SUMMARY = "A backend engineer who builds payment systems and the data work under them."


def summary_section(summary: str | None = SUMMARY) -> list[str]:
    """The `## Summary` block as bullets.md's first section, or nothing at all."""
    return ["## Summary", summary, ""] if summary is not None else []


def write_bullets(run_dir: Path, placed=PLACED, skills=SKILLS, summary=SUMMARY) -> None:
    """`bullets.md` — the Summary, a section per placed Entry, then the Skills rows."""
    lines = ["# Bullets: acme-backend-engineer", ""] + summary_section(summary)
    for slug, _, claims in placed:
        lines.append(f"## {slug}")
        lines += [f"- {slug}/{claim_id}: {text}" for claim_id, text in claims]
        lines.append("")
    lines.append("## Skills")
    for label, row in skills:
        lines += ["", f"### {label}"]
        lines += [f"- {name} ({ref})" for name, ref in row]
    (run_dir / "bullets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_checkpoint(run_dir: Path, *refs: str, section: str = "Decided by rule") -> None:
    """`checkpoint.md` with a Decided-by-rule section naming `refs`.

    No run folder here writes one unless a test asks for it, which is the shape the
    drop check has to survive: the file is written on every real run, and a check
    that died on its absence would fail the run for the wrong reason. The prose
    around the ref is deliberate — the section is written for a person, and the ref
    is the only part of the line render.py reads.
    """
    lines = [
        "# Checkpoint: acme-backend-engineer",
        "",
        "## Angle",
        "",
        "Read as a payments-platform role. The page leads with Helios.",
        "",
        f"## {section}",
        "",
    ]
    lines += [
        f"- **`{ref}` composed without its figure.** Its own Evidence undercuts the "
        f"number for this posting's angle."
        for ref in refs
    ]
    (run_dir / "checkpoint.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run(run_dir: Path, placed=PLACED, skills=SKILLS, widths=None, summary=SUMMARY) -> None:
    """The pair, agreeing with each other — the state every run starts from."""
    write_allocation(run_dir, placed, skill_lines(skills), widths)
    write_bullets(run_dir, placed, skills, summary)


def one_bullet(slug: str, type_: str, claim_id: str, text: str):
    """A one-Entry, one-Bullet run — the smallest thing that renders."""
    return [(slug, type_, [(claim_id, text)])]


def one_skill(name: str, ref: str):
    """A Skills section carrying one skill under test, and a second row beside it.

    The second row is not decoration: a section is two rows or the whole thing is
    refused, so a one-row fixture would fail on the floor rather than on the thing
    the test is about.
    """
    return [("Under test", [(name, ref)]), ("Languages", [("Go", "helios-payments/c1")])]


def tex(run_dir: Path) -> str:
    return (run_dir / "resume.tex").read_text(encoding="utf-8")


def profile_path(run_dir: Path) -> Path:
    return run_dir.parent.parent / "bank" / "profile.md"


def entry_path(run_dir: Path, slug: str) -> Path:
    """A fixture bank job file. The bank sits beside `runs/`, which is the real
    layout the tool resolves against and not a test affordance."""
    return run_dir.parent.parent / "bank" / "jobs" / f"{slug}.md"


# --------------------------------------------------------------------------
# The whole thing, end to end
# --------------------------------------------------------------------------
@pytest.mark.needs_pdflatex
def test_a_hand_written_bank_and_allocation_produce_a_real_pdf(repo_root, run_dir):
    """The proof the whole build is aimed at: bank + allocation + bullets -> PDF."""
    write_run(run_dir)
    result = render_ok(repo_root, run_dir)

    assert (run_dir / "resume.pdf").is_file()
    assert (run_dir / "resume.tex").is_file()
    assert "3 bullets" in result.stdout

    body = tex(run_dir)
    # The figure is wrapped by \resumeEmph before it reaches the page
    # (docs/adr/0043-the-number-carries-the-emphasis.md), so the prose around it is
    # what stays contiguous — asserting on the whole sentence would be asserting
    # that nothing is emphasised.
    assert "Cut checkout p99 latency" in body
    assert r"\resumeEmph{40\%}" in body
    assert "Helios Pay" in body                    # the Entry header, from the bank
    assert "Ada Lovelace" in body                  # the Static profile
    assert r"\textbf{Languages:} Go, Rust" in body  # a Skills category row
    assert r"\textbf{Platform:} Kafka, PostgreSQL" in body


@pytest.mark.needs_pdflatex
def test_the_template_is_filled_whole_and_the_tex_is_never_read_back(repo_root, run_dir):
    """Each run renders the Template whole; nothing parses or splices a `.tex`."""
    (run_dir / "resume.tex").write_text("this is not LaTeX and nothing may read it\n")
    write_run(run_dir)
    render_ok(repo_root, run_dir)

    body = tex(run_dir)
    assert "this is not LaTeX" not in body
    assert r"\documentclass[a4paper,11pt]{article}" in body       # the preamble
    assert r"\end{document}" in body
    assert "sb2nov" in body                                       # the MIT attribution


@pytest.mark.needs_pdflatex
def test_the_documented_invocation_takes_a_relative_run_folder(repo_root, run_dir):
    """`python tools/render.py runs/<jd-slug>` — the form the spec documents and the
    maker types.

    Worth its own test because every other one here passes an absolute `tmp_path`
    and cannot see the failure: pdflatex is run with the run folder as its working
    directory, so a path relative to the repo gets resolved a second time against
    that folder and disappears.
    """
    write_run(run_dir)
    result = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "render.py"), "runs/acme-backend-engineer"],
        cwd=run_dir.parent.parent,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (run_dir / "resume.pdf").is_file()


@pytest.mark.needs_pdflatex
def test_an_unchanged_run_folder_rebuilds_to_a_byte_identical_pdf(repo_root, run_dir):
    """A git diff has to mean something actually changed."""
    write_run(run_dir)
    render_ok(repo_root, run_dir)
    first = (run_dir / "resume.pdf").read_bytes()

    render_ok(repo_root, run_dir)
    assert (run_dir / "resume.pdf").read_bytes() == first


#: Neutral prose used to pad a fixture assertion out to a two-line Bullet. It carries
#: no digit, so the number-trace check has nothing to trace, and no `-ise`/`-ize` word,
#: so the spelling check sees no convention to mix.
PADDING = (
    "and then the same work again on the neighbouring service, with the on-call rota "
    "left exactly as it was found"
)


def two_line_page(cap: int):
    """`(placed, widths)` — every fixture Claim as a Bullet that fills a two-line slot.

    The overstuffed page. Every Claim in the fixture bank at one line no longer
    overflows — `PAGE_LINES` went from 50 to 53 when the page became A4 — so each
    Bullet is granted the second line the Packer can grant it and written to fill it.
    Every one is still inside the width its slot was granted (`2 x CHARS_PER_BULLET`),
    which is the point: nothing here is a prose-length fault.
    """
    placed, widths = [], {}
    for slug, type_, claims in fixture_entries():
        rows = []
        for claim_id, prose in claims:
            rows.append((claim_id, f"{prose} {PADDING}"[: cap + 40]))
            widths[f"{slug}/{claim_id}"] = 2
        placed.append((slug, type_, rows))
    return placed, widths


@pytest.mark.needs_pdflatex
def test_the_page_count_assert_fires_and_blames_the_constants(repo_root, run_dir, config_module):
    """Overstuff the page deliberately: every Claim in the fixture bank, allocated.

    Every one of those Bullets is inside the width its slot was granted, which is
    exactly why the message must not send the maker off to shorten prose — the
    failure means the Page-budget constants promised lines the page does not have.
    """
    placed, widths = two_line_page(config_module.CHARS_PER_BULLET)
    total = sum(len(claims) for _, _, claims in placed)
    lines = len(placed) * config_module.ENTRY_HEADER_LINES + 2 * total
    assert lines > config_module.PAGE_LINES, (
        f"the fixture bank is too small to overflow a page: {lines} lines"
    )

    write_run(run_dir, placed, skills=SKILLS, widths=widths)
    message = render_fails(repo_root, run_dir, "miscalibrated", "tools/config.py")
    assert "docs/calibration.md" in message
    assert "pages" in message


@pytest.mark.needs_pdflatex
def test_the_real_pipeline_from_the_fixture_score_table(repo_root, run_dir, config_module):
    """Score table -> pack.py -> bullets -> render.py, with nothing hand-shaped between.

    Every other test here writes `allocation.md` itself, which proves render.py reads
    the shape those tests believe in. This one runs the Packer and renders what it
    actually wrote, so the two tools are held to each other rather than to a fixture
    of the format — and it is the end-to-end proof the build is aimed at.
    """
    shutil.copy(FIXTURE_BANK.parent / "scores.md", run_dir / "scores.md")

    def pack(*flags: str) -> None:
        packed = subprocess.run(
            [sys.executable, "tools/pack.py", str(run_dir), *flags],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        assert packed.returncode == 0, packed.stderr

    # Pass one reserves four single-line rows; pass two is told what was composed.
    # Both are run here rather than only the second, because the reservation is
    # what the Bullets have to be composed against and the reconcile is what
    # settles the budget the page actually renders from.
    pack()
    assert "RESERVATION" in (run_dir / "allocation.md").read_text(encoding="utf-8")
    pack("--skills-rows", "1,1")

    assertions = {
        f"{slug}/{claim_id}": prose
        for slug, _, claims in fixture_entries()
        for claim_id, prose in claims
    }
    def prose_for(slug: str, unit: str) -> str:
        """One unit's Bullet — a merge coordinates its members' assertions.

        The fixture score table declares merges, so the pipeline has to be driven
        through merged refs as well as single ones.
        The join is crude on purpose: this test proves the two tools agree on the
        FORMAT, and `0034`'s rules about what a merged sentence may assert are the
        merge verifier's business, not the Renderer's.
        """
        parts = [assertions[f"{slug}/{claim_id}"] for claim_id in unit.split("+")]
        room = 170 if "+" in unit else 95
        return "; ".join(parts)[:room]

    lines = ["# Bullets: from the fixture score table", ""] + summary_section()
    cited = []
    allocation = (run_dir / "allocation.md").read_text(encoding="utf-8")
    for slug, units in placed(allocation):
        lines.append(f"## {slug}")
        for unit in units:
            ref = f"{slug}/{unit}"
            lines.append(f"- {ref}: {prose_for(slug, unit)}")
            cited.append(ref)
        lines.append("")
    # A Skills row cites ONE Claim — the one whose `skills:` line carries the skill —
    # so it takes the merge group's first member rather than the group's ref.
    carrier = cited[0].split("+")[0]
    lines += ["## Skills", "", "### Languages", f"- Go ({carrier})",
              "", "### Platform", f"- Kafka ({carrier})"]
    (run_dir / "bullets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = render_ok(repo_root, run_dir)
    assert f"{len(cited)} bullets" in result.stdout
    assert (run_dir / "resume.pdf").is_file()


def fixture_entries():
    """Every fixture Entry as `(slug, type, [(claim id, its assertion)])`.

    The assertion doubles as the Bullet, which is what the neutral assertion is for:
    render's default phrasing. Read out of the committed files rather than restated,
    so the overflow case grows with the fixture bank.
    """
    entries = []
    for type_, folder in (("job", "jobs"), ("project", "projects")):
        for path in sorted((FIXTURE_BANK / folder).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            claims = re.findall(
                r"^## (c\d+)$.*?^\*\*Assertion:\*\* (.+?)$", text, re.M | re.S
            )
            assert claims, f"{path} parses to no claims"
            entries.append((path.stem, type_, [(cid, prose.rstrip(".")) for cid, prose in claims]))
    return entries


# --------------------------------------------------------------------------
# Step 1 — Profile validation, the one seam
# --------------------------------------------------------------------------
def test_a_missing_profile_key_fails_naming_the_key(repo_root, run_dir):
    write_run(run_dir)
    path = profile_path(run_dir)
    path.write_text(
        re.sub(r"^email:.*$", "", path.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8"
    )
    render_fails(repo_root, run_dir, "email", "profile.md")


def test_an_unknown_profile_key_fails_naming_the_key(repo_root, run_dir):
    """A typo in your own contact block stops the run instead of rendering a blank."""
    path = profile_path(run_dir)
    path.write_text(
        re.sub(
            r"^(phone: .*)$",
            r"\1\nnickname: The Countess",
            path.read_text(encoding="utf-8"),
            flags=re.M,
        ),
        encoding="utf-8",
    )
    write_run(run_dir)
    message = render_fails(repo_root, run_dir, "nickname")
    assert "profile.example.md" in message, "the message should point at the contract"


def test_a_blank_profile_value_fails(repo_root, run_dir):
    path = profile_path(run_dir)
    path.write_text(
        re.sub(r"^location: .*$", "location:", path.read_text(encoding="utf-8"), flags=re.M),
        encoding="utf-8",
    )
    write_run(run_dir)
    render_fails(repo_root, run_dir, "location", "blank")


@pytest.mark.needs_pdflatex
def test_phone_linkedin_and_github_may_be_left_out(repo_root, run_dir):
    """Not everyone has a GitHub. Each optional field drops with its separator."""
    path = profile_path(run_dir)
    kept = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith(("phone:", "github:"))
    ]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    write_run(run_dir)
    render_ok(repo_root, run_dir)
    body = tex(run_dir)
    assert "github.com/adalovelace" not in body
    assert "98765" not in body
    assert "linkedin.com/in/adalovelace" in body


def test_no_pdflatex_is_a_message_saying_what_to_install(repo_root, run_dir):
    """A stranger's likeliest first failure gets a sentence, not a traceback — and
    last run's PDF does not survive beside this run's source."""
    write_run(run_dir)
    (run_dir / "resume.pdf").write_bytes(b"stale")
    result = subprocess.run(
        [sys.executable, "tools/render.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": "/nonexistent"},
    )
    assert result.returncode == 1
    assert "pdflatex is not on PATH" in result.stderr
    assert "Traceback" not in result.stderr
    assert not (run_dir / "resume.pdf").exists()


def test_a_link_field_that_is_not_url_safe_fails_naming_the_field(repo_root, run_dir):
    """`email`, `linkedin` and `github` land inside \\href targets as well as in the
    visible text, where a character like `#` breaks the link instead of the compile —
    so nothing downstream would catch it."""
    path = profile_path(run_dir)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "github.com/adalovelace", "github.com/ada#lovelace"
        ),
        encoding="utf-8",
    )
    write_run(run_dir)
    render_fails(repo_root, run_dir, "github", "href")


@pytest.mark.needs_pdflatex
def test_an_underscore_in_a_link_field_is_escaped_in_the_text_and_raw_in_the_target(
    repo_root, run_dir
):
    """`jane_doe@example.com` is a common address. The visible copy needs `\\_`; the
    \\href target needs the raw `_`, or the link points somewhere else."""
    path = profile_path(run_dir)
    path.write_text(
        path.read_text(encoding="utf-8")
        .replace("github.com/adalovelace", "github.com/ada_l")
        .replace("ada.lovelace@example.com", "ada_l@example.com"),
        encoding="utf-8",
    )
    write_run(run_dir)
    render_ok(repo_root, run_dir)
    body = tex(run_dir)
    assert r"\href{https://github.com/ada_l}{\underline{github.com/ada\_l}}" in body
    assert r"\href{mailto:ada_l@example.com}" in body


def test_more_education_rows_than_the_allocation_charged_for_fails(repo_root, run_dir):
    """A profile edited after the pack: the page promises lines it does not have.

    Without this the failure still surfaces — as the page-count assert — but that
    message blames the calibration. The allocation names the rows it was packed for.
    """
    path = profile_path(run_dir)
    extra = (
        "\n### e2\ninstitution: School 2\nlocation: Pune, India\n"
        "degree: M.Tech., Distributed Systems\ndates: Aug 2017 -- May 2019\n"
    )
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    write_run(run_dir)
    allocation = run_dir / "allocation.md"
    allocation.write_text(
        allocation.read_text(encoding="utf-8") + "\nEducation: 1 row(s), charged 3 line(s).\n",
        encoding="utf-8",
    )
    render_fails(repo_root, run_dir, "2 Education rows", "Re-run pack.py")


def test_pack_counts_the_education_rows_it_charges_for(repo_root, run_dir):
    """Nobody edits a constant per school: pack.py reads the count off the profile."""
    path = profile_path(run_dir)
    extra = (
        "\n### e2\ninstitution: School 2\nlocation: Pune, India\n"
        "degree: M.Tech., Distributed Systems\ndates: Aug 2017 -- May 2019\n"
    )
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    shutil.copy(FIXTURE_BANK.parent / "scores.md", run_dir / "scores.md")
    packed = subprocess.run(
        [sys.executable, "tools/pack.py", str(run_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert packed.returncode == 0, packed.stderr
    assert "Education: 2 row(s)" in (run_dir / "allocation.md").read_text(encoding="utf-8")


def test_profile_validation_runs_before_anything_reads_the_bullets(repo_root, run_dir):
    """The seam is on every path that produces a PDF, so it fires first.

    This is what issue #32's Header-fit check needs in order to land here without
    restructuring: one named place the profile is validated, reached by every run.
    """
    path = profile_path(run_dir)
    path.write_text(
        path.read_text(encoding="utf-8").replace("email:", "e-mail:"), encoding="utf-8"
    )
    write_allocation(run_dir)
    (run_dir / "bullets.md").write_text("this does not parse either\n", encoding="utf-8")

    message = render_fails(repo_root, run_dir, "profile.md", "email")
    assert "bullets.md" not in message


# --------------------------------------------------------------------------
# Step 2 — the structural check
# --------------------------------------------------------------------------
def test_a_bullet_citing_an_id_that_does_not_resolve_fails(repo_root, run_dir):
    write_run(run_dir, one_bullet("helios-payments", "job", "c9", "A claim that is not there"))
    render_fails(repo_root, run_dir, "helios-payments/c9", "c9")


def test_a_bullet_citing_an_entry_that_is_not_in_the_bank_fails(repo_root, run_dir):
    write_run(run_dir, one_bullet("mystery-corp", "job", "c1", "Work nobody ingested"))
    render_fails(repo_root, run_dir, "mystery-corp")


def test_an_extra_bullet_beyond_the_allocation_fails(repo_root, run_dir):
    """The Packer decides how many lines the page has."""
    write_allocation(run_dir)
    extra = [(slug, type_, list(claims)) for slug, type_, claims in PLACED]
    extra[0][2].append(("c2", "Cut nightly settlement reconciliation ~30% with partitioned reads"))
    write_bullets(run_dir, extra)
    render_fails(repo_root, run_dir, "helios-payments/c2", "no slot")


def test_an_unfilled_slot_fails(repo_root, run_dir):
    write_allocation(run_dir)
    short = [(slug, type_, list(claims)) for slug, type_, claims in PLACED]
    short[0] = (short[0][0], short[0][1], short[0][2][:1])
    write_bullets(run_dir, short)
    render_fails(repo_root, run_dir, "helios-payments/c3", "allocated")


def test_bullets_out_of_page_order_fail(repo_root, run_dir):
    write_allocation(run_dir)
    write_bullets(run_dir, list(reversed(PLACED)))
    render_fails(repo_root, run_dir, "page order")


def test_one_claim_cannot_take_two_bullets(repo_root, run_dir):
    """Two lines from one Claim spend two of the page's lines on one piece of evidence."""
    twice = [
        (
            "helios-payments",
            "job",
            [
                ("c1", "Cut checkout p99 latency 40% by batching commits"),
                ("c1", "Cut checkout p99 latency by batching commits in the consumer"),
            ],
        )
    ]
    write_run(run_dir, twice)
    render_fails(repo_root, run_dir, "helios-payments/c1", "already has a Bullet")


@pytest.mark.parametrize(
    "line, named",
    [
        ("- helios-payments/c1 no colon here", "Bullet line"),
        ("- c1: the entry slug is missing", "Bullet line"),
        ("just some prose Opus felt like writing", "Bullet line"),
    ],
)
def test_a_bullets_line_that_does_not_parse_fails_naming_the_line(
    repo_root, run_dir, line, named
):
    write_allocation(run_dir)
    (run_dir / "bullets.md").write_text(
        f"## Summary\n{SUMMARY}\n\n## helios-payments\n{line}\n\n"
        f"## Skills\n- Go (helios-payments/c1)\n",
        encoding="utf-8",
    )
    render_fails(repo_root, run_dir, named, line.split()[0] if line.startswith("-") else "prose")


def test_bullets_with_no_skills_section_fails(repo_root, run_dir):
    write_run(run_dir)
    text = (run_dir / "bullets.md").read_text(encoding="utf-8").split("## Skills")[0]
    (run_dir / "bullets.md").write_text(text, encoding="utf-8")
    render_fails(repo_root, run_dir, "Skills")


def test_a_run_folder_without_the_files_fails_by_name(repo_root, run_dir):
    render_fails(repo_root, run_dir, "bullets.md")
    write_bullets(run_dir)
    render_fails(repo_root, run_dir, "allocation.md")


def test_an_allocation_that_disagrees_with_the_bank_about_ended_fails(repo_root, run_dir):
    """The Packer's copy of `ended` is checked against the field it was copied from.

    `pack.py` reads `scores.md` and only `scores.md` (`0006`), so the column there is
    a copy of the bank's own field — and the Packer ordered the page on the copy
    while the page prints a date built from the bank. Nothing else ties the two
    together (`docs/adr/0031-the-entry-header-is-built.md` §4).
    """
    write_run(run_dir)
    set_entry_field(run_dir, "helios-payments", "ended", "2024-01")

    message = render_fails(repo_root, run_dir, "helios-payments", "scores.md")
    assert "present" in message and "2024-01" in message, "both sides are quoted"
    assert not (run_dir / "resume.tex").exists(), "nothing is written until it agrees"


# --------------------------------------------------------------------------
# Step 3 — the Bullet-length lint
# --------------------------------------------------------------------------
def test_the_length_lint_names_the_one_over_budget_bullet(repo_root, run_dir, config_module):
    """It fails and names the Bullet so Opus rephrases *that one* shorter."""
    long_bullet = ("Owned the ledger " + "and the reconciliation path " * 6).strip()
    assert len(long_bullet) > config_module.CHARS_PER_BULLET
    placed = [
        (
            "helios-payments",
            "job",
            [
                ("c1", "Cut checkout p99 latency 40% by batching commits"),
                ("c3", long_bullet),
            ],
        )
    ]
    write_run(run_dir, placed)

    message = render_fails(repo_root, run_dir, "helios-payments/c3", str(len(long_bullet)))
    assert "helios-payments/c1" not in message, "only the offending Bullet is named"
    assert not (run_dir / "resume.tex").exists(), "nothing is written until the lints pass"


def test_a_bullet_is_measured_against_the_width_its_slot_was_granted(
    repo_root, run_dir, config_module
):
    """The lint is `width x CHARS_PER_BULLET`, read off the allocation's claim line.

    The same prose passes in a two-line slot and fails in a one-line one, because
    what changed is what the page was charged for — not the sentence.
    """
    prose = "Owned the payments ledger end to end, " + "x" * 80
    assert config_module.CHARS_PER_BULLET < len(prose) <= 2 * config_module.CHARS_PER_BULLET
    placed = one_bullet("helios-payments", "job", "c3", prose)

    write_run(run_dir, placed, widths={"helios-payments/c3": 2})
    render_ok(repo_root, run_dir)

    write_run(run_dir, placed)
    message = render_fails(repo_root, run_dir, "helios-payments/c3")
    assert f"1 x {config_module.CHARS_PER_BULLET}" in message, (
        "the failure has to say what the slot was charged for"
    )


def test_a_bullet_over_even_its_granted_two_lines_still_fails(
    repo_root, run_dir, config_module
):
    """The grant raises the ceiling; it does not remove it."""
    prose = "Owned the ledger " + "and every reconciliation path " * 8
    assert len(prose) > 2 * config_module.CHARS_PER_BULLET
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c3", prose),
        widths={"helios-payments/c3": 2},
    )

    render_fails(repo_root, run_dir, "helios-payments/c3", str(2 * config_module.CHARS_PER_BULLET))


def test_a_bullet_written_under_its_granted_width_still_renders(repo_root, run_dir):
    """Failing a run because a sentence came out crisp would be absurd.

    It wastes whitespace and cannot over-promise, so `tools/lengths.py` reports it as
    a finding and the render goes ahead (`docs/adr/0025-bullet-wrap-cost.md` §6).
    """
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c3", "Owned the payments ledger end to end"),
        widths={"helios-payments/c3": 2},
    )

    render_ok(repo_root, run_dir)


def test_a_claim_line_with_no_readable_width_is_refused(repo_root, run_dir):
    """The third field is contract: an allocation the Renderer cannot read is not one.

    A claim line whose width is missing reads as a slot that is not there, and an
    Entry with no slots is something the Packer never writes.
    """
    write_run(run_dir)
    allocation = (run_dir / "allocation.md").read_text(encoding="utf-8")
    (run_dir / "allocation.md").write_text(
        allocation.replace(" — 1 line — ", " — "), encoding="utf-8"
    )

    render_fails(repo_root, run_dir, "placed with no Bullet slots")


def test_an_over_budget_bullet_is_never_truncated(repo_root, run_dir):
    """Truncation is rejected outright: a cut sentence can assert something the
    Claim does not, and dropping loses a slot the Packer earned."""
    long_bullet = ("Owned the payments ledger " + "and every reconciliation path " * 6).strip()
    write_run(run_dir, one_bullet("helios-payments", "job", "c3", long_bullet))
    render_fails(repo_root, run_dir)
    assert not (run_dir / "resume.pdf").exists()


def test_a_skills_row_past_two_typeset_lines_fails(repo_root, run_dir, config_module):
    """A row is allowed to wrap; what is capped is how far.

    Past two lines the section stops reading as a breadth list, so the run sheds
    skills from the least prominent end rather than typesetting a paragraph.
    """
    long_row = [
        ("Languages", [("Go", "helios-payments/c1")] * (config_module.CHARS_PER_BULLET // 2)),
        ("Platform", [("Kafka", "helios-payments/c1")]),
    ]
    write_allocation(run_dir, PLACED, [2, 1])
    write_bullets(run_dir, PLACED, long_row)
    render_fails(repo_root, run_dir, "Languages", "typeset lines")


def test_a_one_row_skills_section_is_no_section_at_all(repo_root, run_dir):
    """Its heading costs SECTION_LINES, so one row spends three lines to show one.

    The failure has to be loud rather than a silent drop: the Packer already handed
    the whole reservation back, so a page that renders the row anyway is a line the
    budget never granted.
    """
    write_allocation(run_dir, PLACED, [])
    write_bullets(run_dir, PLACED, [("Languages", [("Go", "helios-payments/c1")])])
    render_fails(repo_root, run_dir, "1 row(s)", "2 rows or it is not a section")


@pytest.mark.needs_pdflatex
def test_a_skills_section_the_allocation_did_not_charge_for_fails(repo_root, run_dir):
    """`--skills-rows` is an argument, so nothing else ties the budget to the page.

    Charge too little and the run dies at the page-count assert blaming the
    constants; charge too much and evidence is left off for room nobody used.
    """
    write_allocation(run_dir, PLACED, [1, 1, 1])
    write_bullets(run_dir, PLACED, SKILLS)
    render_fails(repo_root, run_dir, "allocation.md was charged for 1,1,1", "--skills-rows 1,1")


def test_a_reservation_is_refused_rather_than_rendered(repo_root, run_dir):
    """Pass one's allocation is a budget for four rows nobody composed."""
    write_run(run_dir)
    allocation = (run_dir / "allocation.md").read_text(encoding="utf-8")
    (run_dir / "allocation.md").write_text(
        allocation.replace(
            skills_paragraph(skill_lines()),
            "Skills: 4 row(s) reserved at one typeset line each, charged 5 line(s) "
            "including the heading. This is a RESERVATION, not the composed section.",
        ),
        encoding="utf-8",
    )
    render_fails(repo_root, run_dir, "RESERVATION", "--skills-rows")


# --------------------------------------------------------------------------
# Step 4 — the set checks
# --------------------------------------------------------------------------
#: Openers for a made-up page, one per Bullet and all different, so a test about the
#: length distribution never trips the opener rule by accident.
OPENERS = [
    "Owned", "Rebuilt", "Retired", "Untangled", "Handed", "Folded", "Carried",
    "Paired", "Held", "Traced", "Argued", "Pulled", "Kept", "Walked",
]

#: Filler with no digits in it, no `-ise`/`-ize` word, and **no word the fixture
#: bank declares as a skill**, so a Bullet padded to an exact length still says
#: nothing the Number-trace check, the spelling rule or the emphasis rule can object
#: to. What is under test is how long the line is, and nothing else — and a declared
#: term is charged at the bold rate, so one in here would push a Bullet written to
#: the cap over it (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §6).
#: It said `on-call rota` until that rule arrived, and `On-call` is a fixture skill.
FILLER = (
    "the ledger service end to end so the overnight rota stopped being woken by it, "
    "and wrote down what the team had been carrying in their heads "
)


def unnumbered_claims() -> list[tuple[str, str, str]]:
    """`(slug, type, claim id)` for every fixture Claim that stores no number.

    A Bullet composed from one of these may say anything without digits and still
    pass the Number-trace check and its mirror — which is what lets a test about the
    length *distribution* write prose of an exact length rather than one that also
    has to keep a figure in it. Read out of the committed files, like
    `fixture_entries`, so it grows with the fixture bank.
    """
    claims = []
    for slug, type_, entry_claims in fixture_entries():
        text = (FIXTURE_BANK / f"{'jobs' if type_ == 'job' else 'projects'}"
                / f"{slug}.md").read_text(encoding="utf-8")
        for claim_id, _ in entry_claims:
            body = re.search(rf"^## {claim_id}$(.*?)(?=^## |\Z)", text, re.M | re.S)
            if not re.search(r"^number:", body[1], re.M):
                claims.append((slug, type_, claim_id))
    return claims


def page_of(lengths: list[int], wide: tuple[int, ...] = ()):
    """`(placed, widths)` — one Bullet per length, each an exact number of characters.

    Entries come out in the order the fixture bank gives them, jobs first, and each
    Bullet gets its own opening word, so the only thing that varies between two calls
    is the distribution the spread rule reads. `wide` names the positions granted a
    second line, which is what puts them outside the rule.
    """
    claims = unnumbered_claims()
    assert len(lengths) <= len(claims), (
        f"the fixture bank has {len(claims)} claims with no stored number, "
        f"and this page wants {len(lengths)}"
    )
    by_entry: dict[tuple[str, str], list[tuple[str, str]]] = {}
    widths: dict[str, int] = {}
    for at, ((slug, type_, claim_id), length, first) in enumerate(
        zip(claims, lengths, OPENERS)
    ):
        prose = f"{first} {FILLER * 3}"[:length].rstrip()
        prose += "x" * (length - len(prose))  # only ever where the cut fell on a space
        assert len(prose) == length, f"{length} is too short for an opener and a space"
        by_entry.setdefault((slug, type_), []).append((claim_id, prose))
        if at in wide:
            widths[f"{slug}/{claim_id}"] = 2
    jobs = [(slug, t, c) for (slug, t), c in by_entry.items() if t == "job"]
    placed = jobs + [(slug, t, c) for (slug, t), c in by_entry.items() if t != "job"]
    return placed, widths


def near_the_cap(cap: int, count: int) -> list[int]:
    """`count` Bullet lengths jammed against the cap — the page a spread describes.

    Every one is **over** the spread threshold (`cap - 15`) and **under** the cap, so
    the page's only possible finding is the spread itself. Derived from the cap rather
    than written out, because a re-calibration moves both ends of that band at once:
    at `CHARS_PER_BULLET = 103` this is the literal `95..102` these tests used to
    carry, and at 99 it is `91..98`. `tests/test_lengths.py` keeps its own copy, for
    the reason every fixture there is a copy — neither file imports the other.
    """
    return [cap - 8 + (index % 8) for index in range(count)]


def test_a_page_of_bullets_all_written_to_the_cap_fails_the_spread_rule(
    repo_root, run_dir, config_module
):
    """The shape a real run shipped twice: 14 one-line Bullets, none finishing early.

    `0027` said this in prose and two composed pages later the number had gone up.
    The failure is the page's, not any one Bullet's, so it names the count rather
    than a ref.
    """
    cap = config_module.CHARS_PER_BULLET
    placed, widths = page_of(near_the_cap(cap, 14))
    write_run(run_dir, placed, widths=widths)

    message = render_fails(repo_root, run_dir, "spread")
    assert f"0/5 of 14 one-line bullets at or under {cap - 15}" in message
    assert f"shortest is {cap - 8}" in message


@pytest.mark.needs_pdflatex
def test_the_same_page_with_a_third_of_its_lines_finishing_early_passes(
    repo_root, run_dir, config_module
):
    """One in three, and the rest may sit at the cap: the rule is deliberately weak."""
    cap = config_module.CHARS_PER_BULLET
    short = cap - 15
    placed, widths = page_of([short] * 5 + near_the_cap(cap, 9))
    write_run(run_dir, placed, widths=widths)

    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_five_bullets_all_at_the_cap_are_not_a_distribution(
    repo_root, run_dir, config_module
):
    """Under six one-line Bullets there is no rule — a short run has no spread."""
    placed, widths = page_of(near_the_cap(config_module.CHARS_PER_BULLET, 5))
    write_run(run_dir, placed, widths=widths)

    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_granted_second_line_does_not_count_toward_the_six(
    repo_root, run_dir, config_module
):
    """A second line was granted because the claim needed it, so filling it is the
    point rather than evidence of writing to the cap (`0027` §5).

    Five one-line Bullets at the cap and three wide ones is eight Bullets and no
    distribution: the rule sees five.
    """
    cap = config_module.CHARS_PER_BULLET
    placed, widths = page_of(
        near_the_cap(cap, 5) + [2 * cap - 2, 2 * cap - 1, 2 * cap], wide=(5, 6, 7)
    )
    write_run(run_dir, placed, widths=widths)

    render_ok(repo_root, run_dir)


def test_a_wide_bullet_cannot_make_up_the_count_either(repo_root, run_dir, config_module):
    """The same page with one more one-line Bullet fails, and a short wide slot
    beside it changes nothing — the rule is about the lines that had a choice."""
    cap = config_module.CHARS_PER_BULLET
    placed, widths = page_of(near_the_cap(cap, 6) + [60, 61], wide=(6, 7))
    write_run(run_dir, placed, widths=widths)

    message = render_fails(repo_root, run_dir, "spread")
    assert "0/2 of 6 one-line bullets" in message


def test_two_bullets_in_one_entry_opening_on_the_same_word_fail_and_name_both(
    repo_root, run_dir
):
    """A reader meets them one under the other (docs/adr/0057 §6)."""
    placed = [
        ("helios-payments", "job", [
            ("c2", "Built the payments ledger end to end"),
            ("c3", "Built the reconciliation report on top of it"),
        ]),
    ]
    write_run(run_dir, placed)

    message = render_fails(repo_root, run_dir, "helios-payments/c2", "helios-payments/c3")
    assert "built" in message


def test_a_third_bullet_on_the_page_opening_on_the_same_word_fails(repo_root, run_dir):
    """Twice to a page is allowed, in different entries; a third is a pattern."""
    placed = [
        ("helios-payments", "job", [("c3", "Built the payments ledger end to end")]),
        ("orbit-analytics", "job", [("c3", "Built the event schema the warehouse reads")]),
        ("ledger-cli", "project", [("c3", "built the tutorial a new user starts from")]),
    ]
    write_run(run_dir, placed)

    message = render_fails(repo_root, run_dir, "ledger-cli/c3")
    assert "built" in message and "at most 2" in message


@pytest.mark.needs_pdflatex
def test_the_same_opener_once_in_each_of_two_entries_is_fine(repo_root, run_dir):
    """`Built` under a job and `built` under a project is not a fault (case-blind)."""
    placed = [
        ("helios-payments", "job", [("c3", "Built the payments ledger end to end")]),
        ("ledger-cli", "project", [("c3", "built the tutorial a new user starts from")]),
    ]
    write_run(run_dir, placed)
    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_hyphenated_opener_is_one_word(repo_root, run_dir):
    """`Hand-mapping` and `Hand-rolling` are different openings to a reader, and
    splitting them at the hyphen would fail a page on a distinction nobody sees."""
    placed = [
        ("helios-payments", "job", [("c3", "Hand-mapping the ledger was the old way")]),
        ("ledger-cli", "project", [("c3", "Hand-rolling the tutorial beat generating it")]),
    ]
    write_run(run_dir, placed)

    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_skills_row_label_is_not_an_opener(repo_root, run_dir):
    """A row label is a noun lifted from the posting's vocabulary under `0020`.

    It is chosen under a different set of rules and has no opener problem, so a
    Bullet may open on the word a row is labelled with.
    """
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c3", "Platform work: owned the ledger"),
        skills=[
            ("Platform", [("Kafka", "helios-payments/c1")]),
            ("Languages", [("Go", "helios-payments/c1")]),
        ],
    )

    render_ok(repo_root, run_dir)


def test_two_spellings_of_one_convention_fail_and_name_both_words(repo_root, run_dir):
    """A Bullet and a Skills row, which is where a real run had them.

    The Skills rows are prose the reader reads, so they are inside the rule even
    though they are outside the opener one.
    """
    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c3",
            "Owned the ledger and generalised it past the one team it was built for",
        ),
        skills=[
            ("Data", [("Data standardization", "helios-payments/c1")]),
            ("Languages", [("Go", "helios-payments/c1")]),
        ],
    )

    message = render_fails(repo_root, run_dir, "generalised", "standardization")
    assert "one convention to a page" in message


@pytest.mark.needs_pdflatex
@pytest.mark.parametrize(
    "first, second",
    [
        # One convention throughout, either one. Which is correct is not the
        # check's business — it fails on the mixture, never on the choice.
        ("generalised it past the one team", "organised the rota around it"),
        ("generalized it past the one team", "organized the rota around it"),
        # `supervised` and `comprises` are not the suffix, however they look.
        ("supervised the rota and comprised the whole of it", "standardization work"),
        # `analyses` is the plural of `analysis` as often as it is a verb.
        ("analyses the ledger nightly and files what it finds", "standardization work"),
    ],
)
def test_a_page_that_only_looks_mixed_still_renders(repo_root, run_dir, first, second):
    placed = [
        ("helios-payments", "job", [("c3", f"Owned the ledger and {first}")]),
        ("ledger-cli", "project", [("c3", f"Wrote the tutorial after {second}")]),
    ]
    write_run(run_dir, placed)

    render_ok(repo_root, run_dir)


# --------------------------------------------------------------------------
# Step 5 — the Number-trace check
# --------------------------------------------------------------------------
@pytest.mark.needs_pdflatex
@pytest.mark.parametrize(
    "claim, text",
    [
        # helios-payments/c1 is `number: 40%`, measured: flat or softened.
        ("c1", "Cut checkout p99 latency 40% by batching commits"),
        ("c1", "Cut checkout p99 latency ~40% by batching commits"),
        # helios-payments/c2 is `number: 30%`, estimated: softened only.
        ("c2", "Cut nightly settlement reconciliation ~30% with partitioned reads"),
        # A figure the Claim states in its prose but does not store as its number.
        ("c1", "Took checkout p99 from 1.4s to 830ms by batching commits"),
        # A Claim that stores no number owes the page no figure.
        ("c3", "Own the payments ledger end to end, from schema design to incident review"),
    ],
)
def test_a_number_that_traces_renders(repo_root, run_dir, claim, text):
    write_run(run_dir, one_bullet("helios-payments", "job", claim, text))
    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_softened_number_may_round_its_measured_source(repo_root, run_dir):
    """A Measured 21.6% still shows as ~22% — "~" is a rounding convention on both
    tiers, not a doubt signal."""
    write_run(
        run_dir,
        one_bullet("northwind-retail", "job", "c1", "Cut cart abandonment ~22% at checkout"),
    )
    render_ok(repo_root, run_dir)


def test_a_softened_number_may_not_round_to_something_else(repo_root, run_dir):
    write_run(
        run_dir,
        one_bullet("northwind-retail", "job", "c1", "Cut cart abandonment ~35% at checkout"),
    )
    render_fails(repo_root, run_dir, "northwind-retail/c1", "35%")


def test_an_estimated_number_rendered_flat_fails_and_names_the_bullet(repo_root, run_dir):
    """The silent upgrade: it renders flat, passes every other lint, and is
    undetectable once shipped."""
    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c2", "Cut nightly settlement reconciliation 30% outright"
        ),
    )
    message = render_fails(repo_root, run_dir, "helios-payments/c2", "estimated")
    assert "~30%" in message, "the message should say what the fix is"


def test_an_estimated_number_its_own_evidence_states_flat_still_may_not_render_flat(
    repo_root, run_dir
):
    """The hole the check's ordering closes, and the reason it has one.

    `orbit-analytics/c1` is `number: 60%`, estimated — and its evidence sentence
    writes "60%" flat, as evidence usually does. A figure written in a Claim's prose
    is otherwise allowed to render flat, so if that fallback were consulted first,
    every estimated number would have a way round its own tier: restate it in the
    evidence and render it hard. The stored `number` is matched first for exactly
    this reason, and nothing but this test says so.
    """
    write_run(
        run_dir,
        one_bullet("orbit-analytics", "job", "c1", "Cut dashboard query cost 60% on ClickHouse"),
    )
    render_fails(repo_root, run_dir, "orbit-analytics/c1", "estimated")


def rewrite_claim(run_dir: Path, slug: str, was: str, becomes: str) -> None:
    """Edit one hand-written Claim in the throwaway copy of the fixture bank.

    The fixture bank is a committed corpus every other test reads, so a shape it does
    not happen to contain — a `number:` carrying more than one figure, an estimated
    Claim whose evidence states a second figure — is made here rather than added
    there, where it would quietly change what a dozen unrelated tests are rendering.
    """
    path = entry_path(run_dir, slug)
    original = path.read_text(encoding="utf-8")
    assert was in original, f"{path} does not contain {was!r}"
    path.write_text(original.replace(was, becomes, 1), encoding="utf-8")


#: `helios-payments/c2` with its estimate written three ways in one `number:` line —
#: the ordinary shape of a stored number, and one figure of it, not three.
MULTI_FIGURE = ("## c2\nnumber: 30%", "## c2\nnumber: 30% (2.5h to 1.75h)")


def test_an_estimated_numbers_later_figures_may_not_render_flat_either(repo_root, run_dir):
    """The tier governs the Claim, not the first token of its `number:` line.

    `number: 30% (2.5h to 1.75h)` is one estimate written three ways. If only the
    first figure were tier-checked, the other two would be a way round the tier that
    needs no evidence sentence at all — write the estimate out longhand in `number:`
    and render the long form hard.
    """
    rewrite_claim(run_dir, "helios-payments", *MULTI_FIGURE)
    write_run(
        run_dir,
        one_bullet(
            "helios-payments",
            "job",
            "c2",
            "Took nightly settlement reconciliation from 2.5h to 1.75h with partitioned reads",
        ),
    )
    message = render_fails(repo_root, run_dir, "helios-payments/c2", "estimated")
    assert "~2.5" in message, "the message should say what the fix is"


@pytest.mark.needs_pdflatex
def test_an_estimated_numbers_later_figures_render_softened(repo_root, run_dir):
    """The same Bullet, spent down: every figure of the estimate carries its `~`."""
    rewrite_claim(run_dir, "helios-payments", *MULTI_FIGURE)
    write_run(
        run_dir,
        one_bullet(
            "helios-payments",
            "job",
            "c2",
            "Took nightly settlement reconciliation from ~2.5h to ~1.75h with partitioned reads",
        ),
    )
    render_ok(repo_root, run_dir)


def test_a_figure_only_the_evidence_states_still_answers_to_an_estimated_tier(
    repo_root, run_dir
):
    """A figure a Claim writes only in its prose renders flat — but not on this tier.

    `orbit-analytics/c1` is estimated, and its evidence is where the estimate came
    from, so a second figure stated there is the same soft magnitude in another form.
    Rendering it flat is the silent upgrade with an extra step, and the check has no
    way to tell that step from the sanctioned one; the `~` is what an estimated Claim
    costs. (An estimated tier with no `number:` at all cannot be constructed —
    bank.py fails a `provenance:` with no number, since the pair rides together.)
    """
    rewrite_claim(
        run_dir,
        "orbit-analytics",
        "made the dashboards feel instant.",
        "made the dashboards feel instant. A board that took 9s came back in 2s.",
    )
    write_run(
        run_dir,
        one_bullet(
            "orbit-analytics",
            "job",
            "c1",
            "Took dashboard load from 9s to 2s by moving aggregates to ClickHouse",
        ),
    )
    message = render_fails(repo_root, run_dir, "orbit-analytics/c1", "estimated")
    assert "~9" in message, "the message should say what the fix is"


def test_a_number_with_no_counterpart_in_the_claim_fails(repo_root, run_dir):
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c1", "Cut checkout p99 latency 65% by batching"),
    )
    render_fails(repo_root, run_dir, "helios-payments/c1", "65%")


def test_a_qualitative_claim_that_grew_a_number_fails(repo_root, run_dir):
    """helios-payments/c3 stores no number and writes none in its prose."""
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c3", "Own the payments ledger for 7 product teams"),
    )
    render_fails(repo_root, run_dir, "helios-payments/c3", "7")


@pytest.mark.needs_pdflatex
def test_an_identifier_that_contains_digits_is_not_a_number(repo_root, run_dir):
    """`p99`, `OAuth2`, `gp3` — a digit run welded to letters is an identifier, and
    failing a run for writing one would be worse than the blind spot."""
    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c3", "Own the ledger p99 path, from OAuth2 to EC2 capacity"
        ),
    )
    render_ok(repo_root, run_dir)


# --------------------------------------------------------------------------
# Step 4 — the drop check, the Number-trace check's mirror
# --------------------------------------------------------------------------
#: `helios-payments/c2` is `number: 30%`, and this line says what the work was
#: without saying what it bought. It was a passing case of the trace check until
#: `docs/adr/0029-when-a-number-may-leave.md`; the diff is the decision.
DROPPED = (
    "helios-payments",
    "job",
    "c2",
    "Rewrote nightly settlement reconciliation as partitioned reads",
)


def test_a_bullet_that_drops_its_claims_number_fails_and_names_the_claim(repo_root, run_dir):
    """The mirror of the trace check: a figure that traced to something, then vanished.

    Nothing else catches it. The line is grammatical, inside its budget, traces
    clean — it is simply missing the most defensible fact the Claim owns.
    """
    write_run(run_dir, one_bullet(*DROPPED))
    message = render_fails(repo_root, run_dir, "helios-payments/c2", "30%")
    assert "Decided by rule" in message, "the message should say where a legal drop is recorded"


@pytest.mark.needs_pdflatex
def test_a_drop_recorded_as_decided_by_rule_renders(repo_root, run_dir):
    """The escape: one line in a file the run already writes, and no halt."""
    write_run(run_dir, one_bullet(*DROPPED))
    write_checkpoint(run_dir, "helios-payments/c2")
    render_ok(repo_root, run_dir)


def test_a_ref_recorded_in_some_other_section_does_not_excuse_the_drop(repo_root, run_dir):
    """One section is the check's whole input, which is what makes it teachable.

    A Claim named under `## Notifications` has been *mentioned*; a Claim named under
    `## Decided by rule` has had a compose-time call recorded against it. Reading the
    file loosely would make every Fork and every gap an escape hatch.
    """
    write_run(run_dir, one_bullet(*DROPPED))
    write_checkpoint(run_dir, "helios-payments/c2", section="Notifications")
    render_fails(repo_root, run_dir, "helios-payments/c2", "30%")


@pytest.mark.needs_pdflatex
def test_a_number_softened_on_the_page_is_a_number_kept(repo_root, run_dir):
    """`~22%` off a measured 21.6% satisfies both halves of step 4 at once.

    The rounding the trace check sanctions is not a drop, and the two checks agree
    about it because they ask the same `numbers()` what a figure is.
    """
    write_run(
        run_dir,
        one_bullet("northwind-retail", "job", "c1", "Cut cart abandonment ~22% at checkout"),
    )
    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_run_folder_with_no_checkpoint_still_renders(repo_root, run_dir):
    """A missing `checkpoint.md` reads as *nothing recorded*, never as a crash.

    The failing side of the same fact is the first test in this section, which runs
    against a run folder that has no `checkpoint.md` either and still names the Claim
    rather than raising out of the parser.
    """
    assert not (run_dir / "checkpoint.md").exists()
    write_run(run_dir)
    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_number_field_that_is_not_a_figure_arms_nothing(repo_root, run_dir):
    """`number: half the fleet` leaves the Bullet nothing to keep.

    The same blind spot the trace check carries and documents: the field is
    human-readable text, and a check that demanded digits of a Bullet whose Claim
    has none would fail runs over a sentence.
    """
    rewrite_claim(
        run_dir, "helios-payments", "## c2\nnumber: 30%", "## c2\nnumber: half the nights"
    )
    write_run(run_dir, one_bullet(*DROPPED))
    render_ok(repo_root, run_dir)


def test_a_skill_the_cited_claim_does_not_carry_fails_and_is_named(repo_root, run_dir):
    """The cheapest route to claiming a skill nothing backs."""
    write_run(run_dir, PLACED, one_skill("Haskell", "helios-payments/c1"))
    message = render_fails(repo_root, run_dir, "Haskell", "helios-payments/c1")
    assert "Go, Kafka, PostgreSQL" in message, "the message should say what the claim does carry"


@pytest.mark.needs_pdflatex
def test_a_skill_is_matched_without_regard_to_case(repo_root, run_dir):
    """What lets a run normalise `prompt engineering` to `Prompt engineering` without
    touching the skill's identity, which is the bank's to own."""
    write_run(run_dir, PLACED, one_skill("go", "helios-payments/c1"))
    render_ok(repo_root, run_dir)


def test_a_skill_citing_an_unresolvable_claim_fails(repo_root, run_dir):
    write_run(run_dir, PLACED, one_skill("Go", "helios-payments/c9"))
    render_fails(repo_root, run_dir, "helios-payments/c9")


# --------------------------------------------------------------------------
# Step 6 — the Entry header's dates, built rather than copied
# --------------------------------------------------------------------------
#: The date cell of every `\resumeSubheading` on the page, in page order. Education
#: rows are not in it: they go through `\resumeEducationRow` and are Static profile.
ENTRY_DATES = re.compile(
    r"\\resumeSubheading\n\s*\{[^}]*\}\{([^}]*)\}"
    # A project's one-row header nests braces in its left cell, so its dates are the
    # last group on the line (docs/adr/0057-the-page-reads-like-a-resume.md §3).
    r"|\\resumeProjectHeading\n[^\n]*\}\{([^}]*)\}$",
    re.MULTILINE,
)


@pytest.mark.needs_pdflatex
@pytest.mark.parametrize(
    "started, ended, expected",
    [
        ("2026-01", "2026-07", "Jan 2026 -- Jul 2026"),
        ("2026-07", "present", "Jul 2026 -- Present"),
        ("2023-09", "2023-10", "Sep 2023 -- Oct 2023"),
        ("2018-12", "2019-01", "Dec 2018 -- Jan 2019"),
    ],
)
def test_the_entry_header_date_string_is_built_in_one_house_format(
    repo_root, run_dir, started, ended, expected
):
    """`Mon YYYY -- Mon YYYY`, composed from the two stored fields.

    THE POINT OF THE WHOLE SCHEMA CHANGE. `dates:` was free text and the page it came
    from carried `Jan 2026 -- Jul 2026` above `June 2025 -- July 2025`, four lines
    apart. Three letters for all twelve months, no exceptions — `Sep`, not `Sept` —
    and `Present` capitalised, since it sits where a capitalised month otherwise sits
    (`docs/adr/0031-the-entry-header-is-built.md` §2).
    """
    write_run(run_dir)
    set_entry_field(run_dir, "helios-payments", "started", started)
    set_entry_field(run_dir, "helios-payments", "ended", ended)
    write_allocation(
        run_dir,
        placed=[(slug, type_, claims) for slug, type_, claims in PLACED],
        ended={"helios-payments": ended},
    )
    render_ok(repo_root, run_dir)

    assert "".join(ENTRY_DATES.findall(tex(run_dir))[0]) == expected


@pytest.mark.needs_pdflatex
def test_every_entry_header_on_the_page_reads_the_same_shape(repo_root, run_dir):
    """The fault was a page, not an entry: no two headers may be written differently.

    Nothing composes these but `bank.Entry.display_dates`, so this holds the property
    the maker actually cares about rather than the function that supplies it.
    """
    write_run(run_dir)
    render_ok(repo_root, run_dir)

    cells = [job or project for job, project in ENTRY_DATES.findall(tex(run_dir))]
    assert len(cells) == len(PLACED)
    for cell in cells:
        assert re.fullmatch(r"[A-Z][a-z]{2} \d{4} -- ([A-Z][a-z]{2} \d{4}|Present)", cell), cell


# --------------------------------------------------------------------------
# Step 5 — escaping
# --------------------------------------------------------------------------
@pytest.mark.needs_pdflatex
def test_latex_special_characters_survive_into_the_tex_escaped(repo_root, run_dir):
    """Opus writes plain prose; nothing it writes can break a compile."""
    text = r"Ran the & $ # _ { } ~ ^ \ half of the migration"
    write_run(run_dir, one_bullet("helios-payments", "job", "c3", text))
    render_ok(repo_root, run_dir)

    body = tex(run_dir)
    assert r"Ran the \& \$ \# \_ \{ \} $\sim$ \textasciicircum{}" in body
    assert r"\textbackslash{}" in body
    assert text not in body, "the raw prose must not reach the .tex unescaped"


@pytest.mark.needs_pdflatex
def test_a_bullet_full_of_backslashes_and_braces_still_compiles(repo_root, run_dir):
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c3", r"\begin{document} }{ \\ \item \end{document}"),
    )
    render_ok(repo_root, run_dir)
    assert (run_dir / "resume.pdf").is_file()


@pytest.mark.needs_pdflatex
def test_a_percent_sign_in_a_bullet_does_not_comment_out_the_line(repo_root, run_dir):
    """The escaping bug that would fail quietly rather than loudly: an unescaped `%`
    swallows the rest of the line and the résumé silently loses its Bullet."""
    write_run(
        run_dir,
        one_bullet("helios-payments", "job", "c1", "Cut checkout latency 40% at the tail end"),
    )
    render_ok(repo_root, run_dir)
    assert "at the tail end" in tex(run_dir)


# --------------------------------------------------------------------------
# Step 7 — the Header-fit check
# --------------------------------------------------------------------------
#: Header field values that make a line run over, and ones that do not. All of
#: them are ordinary: LinkedIn appends digits when the plain handle is taken, and
#: people have long names. What is being tested is a header the maker could
#: plausibly type, not an adversarial one.
FITS = "linkedin.com/in/adalovelace"
WRAPS = "linkedin.com/in/ada-lovelace"
LONG_NAME = "Venkataraghavan Chandrasekhar Balasubramanian"


def set_field(path: Path, key: str, value: str) -> None:
    """Rewrite one `key: value` line of a hand-written bank file.

    The first match only: `location:` appears in profile.md's frontmatter and again
    inside the Education row, and the header is built from the frontmatter.
    """
    text, count = re.subn(
        rf"(?m)^{key}: .*$", f"{key}: {value}", path.read_text(encoding="utf-8"), count=1
    )
    assert count == 1, f"no `{key}:` line in {path}"
    path.write_text(text, encoding="utf-8")


def set_profile_field(run_dir: Path, key: str, value: str) -> None:
    set_field(profile_path(run_dir), key, value)


def set_entry_field(run_dir: Path, slug: str, key: str, value: str) -> None:
    set_field(entry_path(run_dir, slug), key, value)


@pytest.mark.needs_pdflatex
def test_a_contact_line_that_wraps_fails_naming_it_and_how_much_to_cut(repo_root, run_dir):
    """The failure this whole check exists for, and it has to be actionable.

    A wrapped header is silent — a centred line breaks legally, so LaTeX warns
    about nothing — and it is set once and then wrong on every résumé forever. The
    message names the offending line and says roughly how many characters to lose,
    because "it is 6.75pt too wide" is not something a maker can act on.
    """
    write_run(run_dir)
    set_profile_field(run_dir, "linkedin", WRAPS)

    message = render_fails(repo_root, run_dir, "the contact line wraps", "profile.md")
    assert "the name line wraps" not in message, "the name fits; naming it would misdirect"
    assert re.search(r"shorten it by about \d+ character", message), message
    assert WRAPS in message, "the message quotes the line back"


@pytest.mark.needs_pdflatex
def test_a_name_line_that_wraps_fails_the_same_way(repo_root, run_dir):
    """The name is the other half of the header and has the identical flaw."""
    write_run(run_dir)
    set_profile_field(run_dir, "name", LONG_NAME)

    message = render_fails(repo_root, run_dir, "the name line wraps", LONG_NAME)
    assert "the contact line wraps" not in message
    assert re.search(r"shorten it by about \d+ character", message), message


@pytest.mark.needs_pdflatex
def test_both_header_lines_wrapping_names_both(repo_root, run_dir):
    """One run reports every offender, rather than one per run."""
    write_run(run_dir)
    set_profile_field(run_dir, "name", LONG_NAME)
    set_profile_field(run_dir, "linkedin", WRAPS)

    render_fails(
        repo_root, run_dir, "the name line wraps", "the contact line wraps", LONG_NAME, WRAPS
    )


@pytest.mark.needs_pdflatex
def test_a_contact_line_wider_than_the_page_line_still_renders(repo_root, run_dir):
    """The check agrees with TeX, not with a width comparison.

    One character shorter than the wrapping handle above, this line is still wider
    than the line it sits on — and TeX sets it on one line anyway by shrinking its
    interword glue. A strict width test would refuse a header the page has room
    for, on every run, forever.
    """
    write_run(run_dir)
    set_profile_field(run_dir, "linkedin", FITS)

    render_ok(repo_root, run_dir)
    assert (run_dir / "resume.pdf").is_file()


@pytest.mark.needs_pdflatex
def test_a_name_full_of_descenders_is_not_a_wrapped_name(repo_root, run_dir):
    """Descenders make the header measurably taller without breaking a line, so the
    check has to compare a line against itself rather than against a height."""
    write_run(run_dir)
    set_profile_field(run_dir, "name", "Jyoti Bhargava Ramanujan")
    render_ok(repo_root, run_dir)


@pytest.mark.needs_pdflatex
def test_a_wrapped_header_is_reported_as_a_header_and_not_as_the_constants(
    repo_root, run_dir
):
    """The ordering, which is the misdiagnosis this check was written to remove.

    Overstuff the page *and* wrap the header. Both faults are real, and the
    page-count assert's message would send the maker off to re-run the calibration
    and re-commit the Page-budget constants — for a header that is four characters
    too long. The Header-fit check runs first, so the header wins the report.
    """
    write_run(run_dir, fixture_entries(), skills=SKILLS)
    set_profile_field(run_dir, "linkedin", WRAPS)

    message = render_fails(repo_root, run_dir, "the contact line wraps")
    assert "miscalibrated" not in message, message
    assert "docs/calibration.md" not in message


# --------------------------------------------------------------------------
# Step 8 — the Overflow check
# --------------------------------------------------------------------------
#: Content that runs past the right margin, measured against the Template. All of
#: it is ordinary: a job title with the team name in it, a university department
#: written out in full, and a dashboard URL pasted into a Bullet. The values are
#: pinned the way FITS and WRAPS are above, and a change to the Template's margins
#: moves all of them.
LONG_TITLE = "Senior Staff Software Engineer, Payments Platform and Ledger Infrastructure Group"
LONG_INSTITUTION = (
    "Indian Institute of Technology Bombay, Department of Computer Science and Engineering"
)
#: A Bullet that is ONE token — inside CHARS_PER_BULLET, and still wider than the
#: line, because a character count cannot see that nothing in it may be broken.
#: This is the case the length lint is blind to and the whole reason Bullets are in
#: the Overflow check's scope (`docs/adr/0018-overflow-check.md`).
LONG_TOKEN = (
    "https://grafana.internal.example.com/d/A7F3C9B2/"
    "PaymentsCheckoutLatencyWeeklyRollupSummaryOverview"
)
#: A name with no space in it, so the header cannot wrap and overflows instead.
#: The Header-fit check sees nothing here — its two boxes measure the same height —
#: which is what makes the shipped header the two checks' shared boundary.
UNBREAKABLE_NAME = "Venkataraghavanchandrasekharbalasubramanianvenkataraghavan"


@pytest.mark.needs_pdflatex
def test_an_over_long_entry_header_fails_naming_the_bank_entry(repo_root, run_dir):
    """The failure this check exists for, and it has to send the maker somewhere.

    An overfull box costs the page no height, so the PDF is still one page and
    pdflatex still exits 0 — nothing else in the run notices. TeX reports a line
    number in `resume.tex`, which the next run overwrites, so the message has to
    name the Bank entry the title was read out of instead.
    """
    write_run(run_dir)
    set_entry_field(run_dir, "helios-payments", "title", LONG_TITLE)

    message = render_fails(
        repo_root,
        run_dir,
        "past the right margin",
        "the Entry header for helios-payments",
        "bank/jobs/helios-payments.md",
    )
    assert LONG_TITLE in message, "the message quotes the header back"
    assert re.search(r"\d+\.\d+pt too wide", message), message


@pytest.mark.needs_pdflatex
def test_an_over_long_education_row_fails_naming_the_profile(repo_root, run_dir):
    """The other half of the pair, and it lives in a different file.

    An Education row is Static profile, so the fix is in bank/profile.md — which is
    exactly what LaTeX's own message cannot say: `in alignment` distinguishes the
    element class from a Bullet's `in paragraph`, and nothing more.
    """
    write_run(run_dir)
    set_profile_field(run_dir, "institution", LONG_INSTITUTION)

    message = render_fails(
        repo_root, run_dir, "past the right margin", "Education row 1", "profile.md"
    )
    assert LONG_INSTITUTION in message
    assert "the Entry header" not in message, "no Entry header ran long; naming one misdirects"


@pytest.mark.needs_pdflatex
def test_a_bullet_of_one_unbreakable_token_fails_the_length_lint_cannot_see(
    repo_root, run_dir, config_module
):
    """The second lint on a Bullet's width, and the two are not redundant.

    CHARS_PER_BULLET is pre-compile and counts characters, so it catches long prose
    before a compile is spent. It cannot see that this Bullet is one token: the
    count passes and the line still overflows, because there is nowhere in it for
    TeX to break.
    """
    assert len(LONG_TOKEN) <= config_module.CHARS_PER_BULLET, (
        "this case is only interesting while the length lint lets it through"
    )
    write_run(run_dir, one_bullet("helios-payments", "job", "c3", LONG_TOKEN))

    message = render_fails(
        repo_root, run_dir, "past the right margin", "the Bullet for helios-payments/c3"
    )
    assert "bullets.md" in message, "the prose is Opus's, so the fix is a rephrase"
    assert str(config_module.CHARS_PER_BULLET) not in message, (
        "the length lint passed; quoting its budget would send the maker to count "
        "characters that are already inside it"
    )


@pytest.mark.needs_pdflatex
def test_the_header_fit_measurement_is_not_reported_as_a_second_overflow(repo_root, run_dir):
    """The Header-fit instrumentation measures inside a \\parbox that breaks for real.

    An unbreakable name overflows that box too, and that box is never shipped. The
    measurement sits at the very end of the document, after the last element marker
    there is, so an unfiltered check does not merely report the same defect twice —
    it hangs the second report on whatever element happens to come last.

    One offender, once, is therefore the assertion: the shipped header stays in
    scope and the copy of it is dropped.
    """
    write_run(run_dir)
    set_profile_field(run_dir, "name", UNBREAKABLE_NAME)

    message = render_fails(
        repo_root, run_dir, "past the right margin", "the Static profile header"
    )
    assert len(re.findall(r"too wide", message)) == 1, message
    assert "wraps" not in message, (
        "a single token cannot wrap, so the Header-fit check has nothing to say — "
        "this is the shipped header failing loudly instead of silently"
    )


@pytest.mark.needs_pdflatex
def test_two_elements_that_overflow_are_both_named(repo_root, run_dir):
    """One run reports every offender, rather than one per run."""
    write_run(run_dir)
    set_entry_field(run_dir, "helios-payments", "title", LONG_TITLE)
    set_profile_field(run_dir, "institution", LONG_INSTITUTION)

    render_fails(
        repo_root,
        run_dir,
        "the Entry header for helios-payments",
        "Education row 1",
        "bank/jobs/helios-payments.md",
        "profile.md",
    )


@pytest.mark.needs_pdflatex
def test_a_run_with_no_skills_still_renders(repo_root, run_dir):
    """The Overflow check insists the Template's markers and its own table match.

    Every other test here exercises that check passing on a full page. This is the
    one place the two sets are allowed to be smaller: an empty Skills breadth list
    drops the whole section from the Template, marker and all, so the table has to
    drop the same row — and a mismatch fails the run rather than the render.
    """
    write_run(run_dir, skills=[])
    render_ok(repo_root, run_dir)

    assert (run_dir / "resume.pdf").is_file()
    assert r"\section{Technical Skills}" not in tex(run_dir)


@pytest.mark.needs_pdflatex
def test_an_overflow_is_reported_before_the_page_count_blames_the_constants(
    repo_root, run_dir
):
    """The convention, which is all this ordering is.

    An overflow leaves the page height untouched, so it can neither cause nor be
    caused by a second page — unlike a wrapped header, which is why `0017`'s
    ordering was load-bearing and this one is not. What the convention buys is that
    a failure the maker fixes in their own data is reported before the one whose
    message is an instruction to re-run the calibration.
    """
    write_run(run_dir, fixture_entries(), skills=SKILLS)
    set_entry_field(run_dir, "helios-payments", "title", LONG_TITLE)

    message = render_fails(repo_root, run_dir, "the Entry header for helios-payments")
    assert "miscalibrated" not in message, message
    assert "docs/calibration.md" not in message


# --------------------------------------------------------------------------
# What bank.py surfaces
# --------------------------------------------------------------------------
@pytest.mark.needs_pdflatex
def test_an_unknown_key_in_the_bank_is_surfaced_and_not_dropped(repo_root, run_dir):
    """The bank is hand-edited, so an unheard-of key is the maker's business — but a
    silently ignored `provenence:` typo would be a number rendering flat forever."""
    path = entry_path(run_dir, "helios-payments")
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "## c1\nnumber: 40%", "## c1\nprovenence: measured\nnumber: 40%"
        ),
        encoding="utf-8",
    )
    write_run(run_dir)
    result = render_ok(repo_root, run_dir)
    assert "provenence" in result.stdout
    assert "helios-payments/c1" in result.stdout


@pytest.mark.parametrize(
    "was, becomes, named",
    [
        ("## c1\nnumber: 40%\nprovenance: measured", "## c1\nnumber: 40%", "provenance"),
        (
            "## c1\nnumber: 40%\nprovenance: measured",
            "## c1\nnumber: 40%\nprovenance: guessed",
            "guessed",
        ),
        ("## c1\n", "## see-the-one-below\n", "c<n>"),
        ("type: job", "type: employment", "employment"),
        ("**Assertion:** Cut checkout", "Cut checkout", "Assertion"),
    ],
    ids=[
        "number-without-provenance",
        "unknown-tier",
        "bad-claim-heading",
        "bad-type",
        "no-assertion",
    ],
)
def test_a_bank_file_that_would_read_wrongly_fails_by_name(repo_root, run_dir, was, becomes, named):
    """bank.py refuses the shapes that would make a Claim mean something else.

    Every one of these is a file that parses to *something* — the failure mode being
    guarded is a Claim quietly changing meaning, not a crash.
    """
    path = entry_path(run_dir, "helios-payments")
    original = path.read_text(encoding="utf-8")
    assert was in original
    path.write_text(original.replace(was, becomes, 1), encoding="utf-8")
    write_run(run_dir)
    render_fails(repo_root, run_dir, named)


def test_the_probes_copy_of_the_row_lines_formula_matches_the_renderers(repo_root, probe):
    """The calibration restates render.py's arithmetic rather than importing it, so
    a bug in the Renderer cannot move a constant. The cost of that is a copy which
    can drift, and a drifted copy would calibrate against a section shape the page
    never renders. This is what holds the two together.

    It is run through the CLI seam like everything else here: `lengths.py` prints
    the Renderer's own line counts, so what is compared is what a run would use.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "auto_apply_config_for_rows", repo_root / "tools" / "config.py"
    )
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    cases = [
        probe.row("Languages", ["Python", "TypeScript"]),
        probe.row("AI & GenAI", ["Prompt engineering", "Custom GPT configuration"]),
        probe.row("Cloud & Infrastructure", probe.WRAPPING_SKILLS[:8]),
        probe.row("Cloud & Infrastructure", probe.OVERLONG_SKILLS),
    ]
    for case in cases:
        label = case["label"].replace(r"\&", "&")
        text = case["text"].replace(r"\&", "&")
        by_probe = probe.measured_row_lines(
            case, config.BOLD_CHARS_PER_BULLET, config.CHARS_PER_BULLET
        )
        by_renderer = row_lines_via_lengths(repo_root, label, text)
        assert by_probe == by_renderer, (
            f"the probe says {by_probe} lines and render.py says {by_renderer} for "
            f"`{label}: {text}`"
        )


def row_lines_via_lengths(repo_root: Path, label: str, text: str) -> int:
    """render.py's row-lines answer, read out of the `skills rows` argument."""
    import tempfile

    with tempfile.TemporaryDirectory() as folder:
        run = Path(folder)
        (run / "bullets.md").write_text(
            "\n".join([
                "## Summary",
                SUMMARY,
                "",
                "## helios-payments",
                "- helios-payments/c1: A Bullet well inside the budget.",
                "",
                "## Skills",
                "",
                f"### {label}",
                *(f"- {name} (helios-payments/c1)" for name in text.split(", ")),
            ]) + "\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "tools/lengths.py", str(run)],
            cwd=repo_root, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        printed = [line for line in result.stdout.splitlines() if line.startswith("skills rows ")]
        assert len(printed) == 1, result.stdout
        return int(printed[0].removeprefix("skills rows "))


# --------------------------------------------------------------------------
# The entry arc: the lead line and merged Bullets (docs/adr/0032-0038)
# --------------------------------------------------------------------------

ONE_BULLET_PLACED = one_bullet("helios-payments", "job", "c1", "Batched commits, cutting p99 latency ~40%")


def add_lead_block(run_dir: Path, slug: str, block: str) -> None:
    path = entry_path(run_dir, slug)
    path.write_text(path.read_text(encoding="utf-8") + "\n" + block + "\n", encoding="utf-8")


def write_lead_allocation(run_dir: Path, *, lead: bool, placed=ONE_BULLET_PLACED) -> None:
    lines = [
        "# Allocation: acme-backend-engineer",
        "",
        "Budget: 36 lines for Entry headers and Bullets, of 50 on the page.",
        "",
        skills_paragraph(skill_lines()),
        "",
        "## Placed",
        "",
        "In page order.",
        "",
    ]
    for slug, type_, claims in placed:
        lead_field = " — lead" if lead else ""
        lines.append(
            f"### {slug} — {type_} — ended {fixture_ended(slug, type_)} — "
            f"entry score 0.80{lead_field} — {len(claims)} bullets"
        )
        lines += [
            f"- {slug}/{claim_id} — 0.80 — 1 line — a fixture reason"
            for claim_id, _ in claims
        ]
        lines.append("")
    lines += ["## Silent calls", "", "Nothing was decided by rule on this run.", ""]
    lines += ["## Did not place", "", "### Entries", "", "Every scored Entry placed.", ""]
    (run_dir / "allocation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_lead_bullets(run_dir: Path, lead_text: str | None, placed=ONE_BULLET_PLACED) -> None:
    lines = ["# Bullets: acme-backend-engineer", ""] + summary_section()
    for slug, _, claims in placed:
        lines.append(f"## {slug}")
        if lead_text is not None:
            lines.append(f"Lead: {lead_text}")
        lines += [f"- {slug}/{claim_id}: {text}" for claim_id, text in claims]
        lines.append("")
    lines.append("## Skills")
    for label, row in SKILLS:
        lines += ["", f"### {label}"]
        lines += [f"- {name} ({ref})" for name, ref in row]
    (run_dir / "bullets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_a_charged_lead_must_be_written(repo_root, run_dir):
    """A lead the allocation paid for and `bullets.md` left out is a line nobody wrote."""
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\n\n**Situation:** The whole reporting cycle was run by hand.",
    )
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, None)  # no `Lead:` line composed

    render_fails(repo_root, run_dir, "composes none")


@pytest.mark.needs_pdflatex
def test_a_bank_lead_the_run_marked_n_is_simply_not_on_the_page(repo_root, run_dir):
    """0057 §5, reversing 0035 §1 — a lead is the run's choice, not the bank's."""
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\n\n**Situation:** The whole reporting cycle was run by hand.",
    )
    write_lead_allocation(run_dir, lead=False)
    write_lead_bullets(run_dir, None)

    render_ok(repo_root, run_dir)
    assert r"\resumeEntryLead{" not in tex(run_dir)


def test_a_composed_lead_needs_a_bank_block_to_come_from(repo_root, run_dir):
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, "A lead nothing in the bank backs.")

    render_fails(repo_root, run_dir, "no `## lead` block")


def test_a_lead_written_that_nothing_charged_fails(repo_root, run_dir):
    write_lead_allocation(run_dir, lead=False)
    write_lead_bullets(run_dir, "A lead the allocation never paid for.")

    render_fails(repo_root, run_dir, "charged it none")


def test_a_lead_over_lead_chars_fails_naming_it(repo_root, run_dir, config_module):
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\n\n**Situation:** The whole reporting cycle was run by hand, every month, "
        "for years, across every team that ever touched it, with nobody ever fixing it.",
    )
    write_lead_allocation(run_dir, lead=True)
    over_budget = "x" * (config_module.LEAD_CHARS + 10)
    write_lead_bullets(run_dir, over_budget)

    render_fails(repo_root, run_dir, "the lead for helios-payments")


def test_a_lead_figure_must_trace_to_the_leads_own_number(repo_root, run_dir):
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\nnumber: ~17.5 hours per month\nprovenance: estimated\n\n"
        "**Situation:** The whole reporting cycle was run by hand.\n\n"
        "**Aggregate:** Automating it gave back about 17.5 hours a month.",
    )
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, "Automating it gave back about 22 hours a month.")

    render_fails(repo_root, run_dir, "renders `22`")


def test_an_estimated_lead_aggregate_must_render_softened(repo_root, run_dir):
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\nnumber: ~17.5 hours per month\nprovenance: estimated\n\n"
        "**Situation:** The whole reporting cycle was run by hand.\n\n"
        "**Aggregate:** Automating it gave back about 17.5 hours a month.",
    )
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, "Automating it gave back about 17.5 hours a month.")

    render_fails(repo_root, run_dir, "renders `17.5` flat")


def test_a_range_never_reaches_the_page(repo_root, run_dir):
    """`0033` §3 — a range collapses at compose time; the page never carries one."""
    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c2",
            "Took nightly settlement reconciliation from 25--35% faster with partitioned reads",
        ),
    )

    render_fails(repo_root, run_dir, "a range")


def test_a_ranges_midpoint_renders_softened_regardless_of_tier(repo_root, run_dir):
    """`0033` §4 — a midpoint is a figure nobody measured, softened whatever the
    tier of the range it came from — even a `measured` one."""
    path = entry_path(run_dir, "helios-payments")
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "Nobody clocked\nthe before and after — the number is my read of when the job started "
            "finishing.",
            "It brought the fix-forward window from 44--56 minutes down to single digits, "
            "clocked on the on-call dashboard.",
            1,
        ),
        encoding="utf-8",
    )

    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c2",
            "Took nightly settlement reconciliation down ~30% and the on-call window to 50 minutes",
        ),
    )

    render_fails(repo_root, run_dir, "50", "midpoint")


def test_a_ranges_midpoint_traces_when_softened(repo_root, run_dir):
    path = entry_path(run_dir, "helios-payments")
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "Nobody clocked\nthe before and after — the number is my read of when the job started "
            "finishing.",
            "It brought the fix-forward window from 44--56 minutes down to single digits, "
            "clocked on the on-call dashboard.",
            1,
        ),
        encoding="utf-8",
    )

    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c2",
            "Took nightly settlement reconciliation down ~30% and the on-call window to ~50 minutes",
        ),
    )

    render_ok(repo_root, run_dir)


# --------------------------------------------------------------------------
# A merge group's stored sum discharges its constituents (docs/adr/0034 §8)
# --------------------------------------------------------------------------


def test_a_merged_bullets_figure_traces_to_the_groups_stored_sum(repo_root, run_dir):
    add_lead_block(
        run_dir,
        "helios-payments",
        "## merge c1+c2\nnumber: ~1.3x\nprovenance: estimated\n\n"
        "**Evidence:** c1's batching and c2's partitioning together roughly bought back "
        "1.3x the throughput headroom. Spoken at a Checkpoint.",
    )
    write_lead_allocation(
        run_dir, lead=False,
        placed=[("helios-payments", "job", [("c1+c2", "merged")])],
    )
    write_lead_bullets(
        run_dir, None,
        placed=[
            (
                "helios-payments", "job",
                [("c1+c2", "Batched consumer commits and partitioned reconciliation reads, "
                           "buying back ~1.3x the throughput")],
            )
        ],
    )

    render_ok(repo_root, run_dir)


def test_a_merged_bullet_with_no_stored_sum_still_owes_its_members_figures(repo_root, run_dir):
    """No `## merge` block for this group yet: falls back to the ordinary
    per-claim rule (`docs/adr/0034-a-merged-bullet-coordinates.md` §8)."""
    write_lead_allocation(
        run_dir, lead=False,
        placed=[("helios-payments", "job", [("c1+c3", "merged")])],
    )
    write_lead_bullets(
        run_dir, None,
        placed=[
            (
                "helios-payments", "job",
                [("c1+c3", "Batched consumer commits and now owns the payments ledger end to end")],
            )
        ],
    )

    render_fails(repo_root, run_dir, "no group sum to discharge")


@pytest.mark.needs_pdflatex
def test_a_merged_bullets_drop_recorded_under_its_merged_ref_renders(repo_root, run_dir):
    """`## Decided by rule` naming `helios-payments/c1+c3` excuses that Bullet."""
    write_lead_allocation(
        run_dir, lead=False,
        placed=[("helios-payments", "job", [("c1+c3", "merged")])],
    )
    write_lead_bullets(
        run_dir, None,
        placed=[
            (
                "helios-payments", "job",
                [("c1+c3", "Batched consumer commits and now owns the payments ledger end to end")],
            )
        ],
    )
    write_checkpoint(run_dir, "helios-payments/c1+c3")

    render_ok(repo_root, run_dir)


# --------------------------------------------------------------------------
# bank.py's `## lead` / `## merge` schema (covered at the CLI, per this file's own
# convention — bank.py's parsing is exercised through render.py and nowhere else)
# --------------------------------------------------------------------------


def test_a_lead_number_with_no_aggregate_is_a_schema_error(repo_root, run_dir):
    add_lead_block(
        run_dir, "helios-payments",
        "## lead\nnumber: ~5 hours\nprovenance: estimated\n\n"
        "**Situation:** The whole reporting cycle was run by hand.",
    )
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, "The whole reporting cycle was run by hand.")

    render_fails(repo_root, run_dir, "Aggregate")


def test_a_merge_citing_an_unknown_claim_is_a_schema_error(repo_root, run_dir):
    add_lead_block(
        run_dir, "helios-payments",
        "## merge c1+c9\nnumber: ~2x\nprovenance: estimated\n\n**Evidence:** made up.",
    )
    write_lead_allocation(
        run_dir, lead=False, placed=[("helios-payments", "job", [("c1+c9", "merged")])]
    )
    write_lead_bullets(
        run_dir, None,
        placed=[("helios-payments", "job", [("c1+c9", "A line citing a claim that does not exist")])],
    )

    render_fails(repo_root, run_dir, "c9")


# --------------------------------------------------------------------------
# Emphasis — docs/adr/0043-the-number-carries-the-emphasis.md, widened by
# docs/adr/0046-every-impact-figure-and-the-declared-keyword.md
#
# These import render.py directly, which the module docstring above says the other
# tests never do. The reason is that emphasis is chosen BEFORE escaping, on offsets
# into the maker's own prose, and the thing worth pinning is the span — asserting on
# the compiled `.tex` alone would test the escaper as much as the rule. The
# end-to-end tests at the bottom still go through the command.
# --------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import render as render_module  # noqa: E402

#: A small declared vocabulary, standing in for the union of the bank's `skills:`
#: names, `bank/vocabulary.md` and this run's `terms.md`. Longest first, because
#: `keyword_vocabulary` returns it that way and `keyword_spans` relies on it.
VOCABULARY = tuple(
    sorted(
        [
            "Google BigQuery", "BigQuery", "Python", "Streamlit", "grafana",
            "Next.js", "machine learning", "automation",
        ],
        key=lambda term: (-len(term), term.casefold()),
    )
)


#: The keyword pass is off on the page (every `MAX_*_KEYWORDS` is 0, `0057` §4) but is
#: still the mechanism that recognises a version number, so it is tested at a cap
#: that lets it be seen.
MECHANISM_CAP = 2


def bolded(text: str, vocabulary=(), cap=MECHANISM_CAP) -> list[str]:
    """The substrings render.py would set in bold, in reading order."""
    return [
        text[start:end]
        for start, end in render_module.emphasis_spans(text, vocabulary, cap)
    ]


# --- the figures -----------------------------------------------------------


def test_a_percentage_carries_its_own_unit_and_takes_no_word_after_it():
    """`~95% came out usable` bolded `~95% came` on a real page."""
    assert bolded("Fixed layouts until ~95% came out usable") == ["~95%"]
    assert bolded("Ran it 3x faster than before") == ["3x"]
    assert bolded("Owned ~60 of 150+ KPIs") == ["~60", "150+ KPIs"]


def test_the_page_bolds_no_keyword_only_figures():
    """0057 §4 — every keyword cap is zero, so a declared term is plain on the page."""
    assert render_module.MAX_BULLET_KEYWORDS == 0
    assert render_module.MAX_SUMMARY_KEYWORDS == 0
    assert render_module.MAX_LEAD_KEYWORDS == 0
    text = "Shipped the translator as a Streamlit app used by 10 teams"
    assert bolded(text, VOCABULARY, render_module.MAX_BULLET_KEYWORDS) == ["10 teams"]


def test_every_figure_on_the_line_is_bolded_not_just_one():
    """0046 §2's whole change from 0043 §1, in one assertion."""
    assert bolded("Owned 60 of a new scorecard's 150 KPIs, automating the heaviest") == [
        "60",
        "150 KPIs",
    ]


def test_a_bare_figure_takes_the_noun_that_gives_it_meaning():
    assert bolded("Owned 40 of the dashboards the team ships") == ["40"]
    assert bolded("Cut 40 dashboards from the nightly refresh") == ["40 dashboards"]


def test_the_span_stops_at_punctuation():
    assert bolded("Cut 40 dashboards, then rewrote the loader") == ["40 dashboards"]


def test_the_span_takes_a_rate_tail():
    assert bolded("Gave back 40 hours a month of hand reconciliation") == ["40 hours a month"]


def test_a_line_with_no_figure_and_no_keyword_gets_no_bold():
    assert bolded("Rebuilt the retry path so a failed capture is replayed once") == []


def test_no_claim_is_read_to_choose_a_figure():
    """0046 §2: the trace check proved every figure, so the Claim decides nothing.

    `emphasis_spans` takes prose and a vocabulary and nothing else — the signature
    is the statement, and this pins it against a later change quietly reading the
    bank back in.
    """
    signature = inspect.signature(render_module.emphasis_spans)
    assert list(signature.parameters) == ["text", "vocabulary", "keyword_cap"]


# --- the figures that are not impact ---------------------------------------


def test_a_bare_year_is_a_date_and_is_never_bolded():
    assert bolded("Ran the migration through 2024 without a rollback") == []


def test_a_four_digit_quantity_is_not_mistaken_for_a_year():
    """Each of the three things that makes 2100 a quantity rather than a date."""
    assert bolded("Wrote ~2,100 lines of prose") == ["~2,100 lines"]
    assert bolded("Wrote ~2100 lines of prose") == ["~2100 lines"]
    assert bolded("Cut 2100 rows from the nightly load") == ["2100 rows"]


def test_a_version_number_after_a_declared_term_is_not_impact():
    assert bolded("Ported the loader to Python 3.11 across the fleet", VOCABULARY) == [
        "Python"
    ]


def test_a_figure_not_following_a_declared_term_is_still_impact():
    assert bolded("Ported 3 loaders to the new fleet", VOCABULARY) == ["3 loaders"]


# --- the keywords ----------------------------------------------------------


def test_a_declared_term_on_the_line_is_bolded():
    assert bolded("Shipped the translator as a Streamlit app", VOCABULARY) == ["Streamlit"]


def test_a_term_no_source_declares_is_not_bolded():
    assert bolded("Shipped the translator as a Gradio app", VOCABULARY) == []


def test_the_longest_matching_term_wins_and_the_two_never_nest():
    spans = bolded("Moved the cuts onto Google BigQuery", VOCABULARY)
    assert spans == ["Google BigQuery"]


def test_a_term_is_never_bolded_out_of_the_middle_of_a_compound():
    assert bolded("Built an automation-first reporting cycle", VOCABULARY) == []


def test_a_term_is_never_bolded_out_of_the_middle_of_a_url():
    """A URL is not prose, and `\\b` alone would take four characters out of one."""
    assert bolded("Linked https://grafana.internal.example.com/d/A7F3C9B2", VOCABULARY) == []


def test_a_term_that_ends_a_sentence_still_matches_through_its_own_dot():
    assert bolded("Rewrote the client on Next.js.", VOCABULARY) == ["Next.js"]


def test_a_term_under_the_minimum_length_is_dropped_from_the_vocabulary():
    """`R` is a real Qualification and is inside `Rewrote`."""
    vocabulary = render_module.keyword_vocabulary({}, "- R\n- Go\n- Python\n", "")
    assert vocabulary == ("Python",)


def test_the_keyword_cap_keeps_the_leftmost_and_the_figures_are_uncapped():
    text = "Moved Python and Streamlit and BigQuery onto 3 hosts cutting 40% of the load"
    assert bolded(text, VOCABULARY) == ["Python", "Streamlit", "3 hosts", "40%"]


def test_a_keyword_inside_a_figures_unit_noun_is_not_bolded_twice():
    """`extend_over_unit` already took the word; a second macro around it is a bug."""
    text = "Ported 3 Pythons to the new fleet"
    assert bolded(text, ("Pythons",)) == ["3 Pythons"]
    assert render_module.emphasised_latex(
        text, render_module.emphasis_spans(text, ("Pythons",), 2)
    ).count(r"\resumeEmph{") == 1


def test_only_a_plural_noun_joins_its_figure_in_bold():
    """0057 §4 — the adjective in front of the noun stays plain."""
    assert bolded("an API ~12 internal services now use") == ["~12"]
    assert bolded("Replaced 8 polling integrations") == ["8"]
    assert bolded("Split 34 services off one database") == ["34 services"]
    assert bolded("saving ~4.5 hours a cycle") == ["~4.5 hours a cycle"]


@pytest.mark.parametrize(
    ("text", "figure"),
    [("Grew the team from 4 as the lead engineer", "4"), ("Cut it to 3 this quarter", "3")],
)
def test_a_word_ending_in_s_that_is_not_a_noun_stays_plain(text, figure):
    """Only a plural noun joins its figure; `as` and `this` are not units."""
    assert bolded(text) == [figure]


# --- the vocabulary --------------------------------------------------------


def test_the_vocabulary_unions_the_bank_the_declared_file_and_the_posting():
    import bank as bank_module

    entries = bank_module.load_bank(FIXTURE_BANK)
    vocabulary = render_module.keyword_vocabulary(
        entries, "- Streamlit\n", "## Must-have\n\n- machine learning\n"
    )
    assert "Streamlit" in vocabulary
    assert "machine learning" in vocabulary
    # Something the fixture bank's Claims actually carry as a skill.
    assert any(term in vocabulary for term in ("grafana", "Grafana"))


def test_a_missing_vocabulary_file_costs_bold_and_never_a_run():
    assert render_module.read_if_present(Path("no/such/file.md")) == ""
    assert render_module.keyword_vocabulary({}, "", "") == ()


def test_the_vocabulary_is_longest_first():
    vocabulary = render_module.keyword_vocabulary({}, "- BigQuery\n- Google BigQuery\n", "")
    assert vocabulary == ("Google BigQuery", "BigQuery")


def test_coverage_reads_terms_through_the_same_parser():
    """One reading of `terms.md`, so the count and the bold can never disagree."""
    import coverage as coverage_module

    text = "## Must-have\n\n- generative AI\n- NLP\n- NLP\n"
    assert coverage_module.terms(text) == render_module.listed_items(text)
    assert coverage_module.terms(text) == ["generative AI", "NLP"]


# --- what reaches the .tex -------------------------------------------------


def test_bolding_introduces_no_new_text():
    """Strip the macro back out and the escaped prose is byte-identical."""
    for text in [
        "Cut checkout p99 latency 40% by batching commits",
        "Gave back ~40 hours a month of hand reconciliation",
        "Rebuilt the retry path so a failed capture is replayed once",
        "Owned 12 of the 30 services on the Python payment path",
    ]:
        latex = render_module.emphasised_latex(
            text, render_module.emphasis_spans(text, VOCABULARY)
        )
        stripped = latex.replace(r"\resumeEmph{", "").replace("}", "")
        assert stripped == render_module.escape_latex(text).replace("}", "")


def test_the_spans_never_nest_and_never_cover_the_whole_line():
    spans = render_module.emphasis_spans("Cut 40% off one job and 30% off another", ())
    assert spans == sorted(spans)
    assert all(spans[i][1] <= spans[i + 1][0] for i in range(len(spans) - 1))
    with pytest.raises(render_module.RenderError, match="entire line"):
        render_module.emphasised_latex("40%", [(0, 3)])


def test_the_bold_runs_are_charged_at_the_bold_rate(config_module):
    """A bolded line costs more than the same characters plain — the whole point."""
    plain = render_module.bullet_line_cost("x" * 100)
    bold = render_module.bullet_line_cost("x" * 100, [(0, 10), (20, 30)])
    assert bold > plain
    # 20 bold characters are charged at the bold rate and the other 80 plain.
    assert bold == pytest.approx(
        80 / config_module.CHARS_PER_BULLET + 20 / config_module.BOLD_CHARS_PER_BULLET
    )


def test_the_bold_penalty_is_a_font_ratio_and_needs_no_second_width(config_module):
    """0046 §6: what lets `SUMMARY_CHARS` be charged for bold with no new constant."""
    assert render_module.BOLD_PENALTY == Fraction(
        config_module.CHARS_PER_BULLET, config_module.BOLD_CHARS_PER_BULLET
    )
    # Ten bold characters cost the same extra whatever budget they are charged to.
    assert render_module.bold_equivalent_chars("x" * 50, [(0, 10)]) == pytest.approx(
        50 + 10 * (float(render_module.BOLD_PENALTY) - 1)
    )


def test_the_summary_sets_no_keyword_in_bold(tmp_path, config_module):
    """0057 §4: a posting's terms are never bolded, so they cost the Summary nothing."""
    summary = "Google BigQuery " * 3 + "x" * (config_module.SUMMARY_CHARS - 53)
    assert len(summary) <= config_module.SUMMARY_CHARS
    assert render_module.emphasis_spans(
        summary, VOCABULARY, render_module.MAX_SUMMARY_KEYWORDS
    ) == []
    render_module.check_summary_length(tmp_path / "bullets.md", summary, VOCABULARY)


def test_a_lead_carries_the_same_emphasis_a_bullet_does():
    """The lead's figures, on the Bullet's rules, and no keyword (0057 §4).

    Same `emphasis_spans`, so the year and version exclusions and the unit extension
    come with it and nothing here re-decides them.
    """
    text = "Automating five steps of the hand-run cycle on Python gave back 17.5 hours a month"
    assert bolded(text, VOCABULARY, render_module.MAX_LEAD_KEYWORDS) == [
        "17.5 hours a month",
    ]
    # A number spelled as a word is not a figure, in a lead as in a Bullet (§3).
    assert "five" not in bolded(text, VOCABULARY, render_module.MAX_LEAD_KEYWORDS)


def test_a_leads_bold_is_charged_at_the_leads_own_penalty(config_module):
    """The whole of what BOLD_LEAD_CHARS buys over reusing the Bullet's ratio.

    0046 §6 proved the penalty is width-independent and that is still true; what is
    not width-independent is the SAMPLE FAMILY the two counts were measured from, and
    a lead's is bold spans rather than lead sentences. So the lead's penalty is
    dearer, and it is dearer because it was measured rather than derived.
    """
    assert render_module.LEAD_BOLD_PENALTY == Fraction(
        config_module.LEAD_CHARS, config_module.BOLD_LEAD_CHARS
    )
    assert render_module.LEAD_BOLD_PENALTY > render_module.BOLD_PENALTY
    assert render_module.bold_equivalent_chars(
        "x" * 50, [(0, 10)], render_module.LEAD_BOLD_PENALTY
    ) == pytest.approx(50 + 10 * (float(render_module.LEAD_BOLD_PENALTY) - 1))


def test_a_lead_that_fits_plain_is_refused_once_its_figure_is_bold(tmp_path, config_module):
    """The lead's tape charges bold, and names the bold when it refuses."""
    lead = "Gave back 17.5 hours a month " + "x" * (config_module.LEAD_CHARS - 29)
    assert len(lead) == config_module.LEAD_CHARS
    with pytest.raises(render_module.RenderError, match="set in bold"):
        render_module.check_lead_lengths(tmp_path / "bullets.md", {"helios-payments": lead})
    # The same length with no figure in it fits, which is what makes the bold the cause.
    render_module.check_lead_lengths(
        tmp_path / "bullets.md", {"helios-payments": "x" * config_module.LEAD_CHARS}
    )


@pytest.mark.needs_pdflatex
def test_the_leads_figure_reaches_the_pdf_wrapped_in_the_template_macro(repo_root, run_dir):
    """0046 left the lead plain and named the measurement; this is the page after it."""
    add_lead_block(
        run_dir,
        "helios-payments",
        "## lead\nnumber: ~17.5 hours per month\nprovenance: estimated\n\n"
        "**Situation:** The whole reporting cycle was run by hand.\n\n"
        "**Aggregate:** Automating it gave back about 17.5 hours a month.",
    )
    write_lead_allocation(run_dir, lead=True)
    write_lead_bullets(run_dir, "Automating the cycle gave back ~17.5 hours a month.")

    render_ok(repo_root, run_dir)

    assert r"\resumeEntryLead{Automating the cycle gave back " \
           r"\resumeEmph{$\sim$17.5 hours a month}.}" in tex(run_dir)


def test_a_bullet_that_only_fits_plain_is_refused_once_its_figure_is_bold(repo_root, run_dir):
    """The lint's new direction: bold costs characters, and the line gets shorter."""
    # 103 characters exactly, ending in the claim's own figure so a span is chosen.
    text = "Cut checkout p99 latency by batching commits in the Go order-ingest consumer, all of it, by 40%"
    text = text + "x" * (103 - len(text))
    write_run(run_dir, placed=one_bullet("helios-payments", "job", "c1", text))

    message = render_fails(repo_root, run_dir, "helios-payments/c1")
    assert "bold" in message


@pytest.mark.needs_pdflatex
def test_the_figure_reaches_the_pdf_wrapped_in_the_template_macro(repo_root, run_dir):
    write_run(
        run_dir,
        placed=one_bullet(
            "helios-payments", "job", "c1",
            "Cut checkout p99 latency 40% by batching commits in the order-ingest consumer",
        ),
    )
    render_ok(repo_root, run_dir)

    assert r"\resumeEmph{40\%}" in tex(run_dir)


@pytest.mark.needs_pdflatex
def test_emphasis_moves_no_element_marker(repo_root, run_dir):
    """`\\resumeEmph` sits inside a `\\resumeItem`'s argument, so it opens no element.

    The Overflow check attributes an overfull line to a page element by reading the
    `%% AUTOAPPLY:element:` markers back out of the `.tex`; if emphasis introduced or
    displaced one, `check_markers_account_for` would start blaming the wrong Bullet.
    """
    with_figure = one_bullet(
        "helios-payments", "job", "c1", "Cut checkout p99 latency 40% by batching commits"
    )
    # c3 stores no `number:`, so a Bullet on it legally carries no figure — which is
    # what makes it the no-bold half of this comparison. Reusing c1 would trip
    # check_number_kept instead, and the test would be about a different rule.
    without = one_bullet(
        "helios-payments", "job", "c3", "Rebuilt the retry path so a failed capture replays once"
    )

    def marker_shape(run: Path) -> list[str]:
        """The markers with the claim ref dropped — the page's element STRUCTURE.

        The ref differs between the two fixtures by construction (they cite
        different claims), and it is not what this test is about: what must not
        move is which elements exist and in what order.
        """
        return [
            marker.rsplit(":", 1)[0]
            for marker in re.findall(r"%% AUTOAPPLY:element:\S+", tex(run))
        ]

    write_run(run_dir, placed=with_figure)
    render_ok(repo_root, run_dir)
    bold_shape, bold_tex = marker_shape(run_dir), tex(run_dir)

    write_run(run_dir, placed=without)
    render_ok(repo_root, run_dir)

    assert bold_shape == marker_shape(run_dir)
    # And the bolded run really did emit the macro, inside the item rather than
    # anywhere a marker lives.
    assert r"\resumeEmph{" in bold_tex
    assert not any(r"\resumeEmph" in line for line in bold_tex.splitlines()
                   if "AUTOAPPLY:element:" in line)


# --------------------------------------------------------------------------
# The Summary — docs/adr/0044-the-page-opens-on-a-summary.md
# --------------------------------------------------------------------------


@pytest.mark.needs_pdflatex
def test_the_summary_reaches_the_page_above_every_section(repo_root, run_dir):
    """It is the first prose on the page, and it goes through the Template's macro.

    Both halves matter. Above the sections is what the element *is* — the page's
    opening claim about the candidate. Through `\\resumeSummary` is `0007`'s rule:
    the Renderer hands over prose and the Template owns how it is set.
    """
    write_run(run_dir)

    render_ok(repo_root, run_dir)

    page = tex(run_dir)
    assert r"\resumeSummary{" in page
    assert SUMMARY in page
    assert page.index(SUMMARY) < page.index(r"\section{Experience}")


def test_a_page_with_no_summary_is_refused(repo_root, run_dir):
    """`0044` §5 — the budget charged for one before a word was composed.

    The Skills section's precedent exactly: the Packer runs first, cannot see what
    was composed, and charged the page either way. A missing Summary is therefore a
    line of evidence left off for room nobody used, not an empty space.
    """
    write_run(run_dir, summary=None)

    message = render_fails(repo_root, run_dir, "Summary")
    assert "0044" in message


def test_the_summary_is_the_first_section_of_the_file(repo_root, run_dir):
    """`bullets.md` is written in page order, and the Summary opens the page.

    The twin of `## Skills` having to be last. A Summary further down would still
    render at the top, so the file would stop being readable as the page.
    """
    write_run(run_dir)
    body = (run_dir / "bullets.md").read_text(encoding="utf-8")
    moved = body.replace(f"## Summary\n{SUMMARY}\n\n", "").replace(
        "## Skills", f"## Summary\n{SUMMARY}\n\n## Skills"
    )
    (run_dir / "bullets.md").write_text(moved, encoding="utf-8")

    render_fails(repo_root, run_dir, "Summary", "first")


def test_a_summary_past_its_budget_fails_saying_how_much_to_cut(
    repo_root, run_dir, config_module
):
    """The length lint's third twin, against the Summary's own wider budget."""
    over = "A backend engineer who builds payment systems, " * 20
    write_run(run_dir, summary=over[: config_module.SUMMARY_CHARS + 12].strip())

    message = render_fails(repo_root, run_dir, "Summary")
    assert str(config_module.SUMMARY_CHARS) in message
    assert "character(s) shorter" in message


@pytest.mark.needs_pdflatex
def test_the_summary_is_measured_against_its_own_wider_budget(repo_root, run_dir, config_module):
    """A Summary longer than any Bullet or lead may still be legal.

    The point of `SUMMARY_CHARS` being a third constant. Measured at
    `CHARS_PER_BULLET` or at `LEAD_CHARS` this page would be refused, and the room
    the block was actually charged for would go unused.
    """
    long_but_legal = (
        "A backend engineer who builds payment ledgers, the streaming that feeds them "
        "and the reporting the finance team reads every month."
    )
    assert config_module.LEAD_CHARS < len(long_but_legal) <= config_module.SUMMARY_CHARS
    write_run(run_dir, summary=long_but_legal)

    render_ok(repo_root, run_dir)


@pytest.mark.parametrize(
    "summary",
    [
        "A backend engineer with 6 years on payment systems and the data work under them.",
        "A backend engineer who has cut checkout latency ~40% across four payment teams.",
    ],
)
def test_a_figure_in_the_summary_is_refused(repo_root, run_dir, summary):
    """`0044` §4 — the Summary cites nothing, so a figure here traces to nothing.

    Both shapes are refused and neither is a style call: the first invents a fact
    about the candidate, the second borrows a real one off a Claim it does not cite
    and reports it as though it described a career. The check cannot tell them
    apart, which is the argument for refusing the figure rather than the claim.
    """
    write_run(run_dir, summary=summary)

    message = render_fails(repo_root, run_dir, "Summary")
    assert "traces to nothing" in message or "nothing for a number" in message


def test_the_summary_is_read_by_the_spelling_check(repo_root, run_dir):
    """The page's one convention, and the Summary is where the other one arrives.

    It is the line licensed to echo the posting (`0044` §2), and a posting is
    exactly where an `-ize` reaches a page that otherwise writes `-ise`. So it is
    inside the set check's spelling half, on the same terms as a lead.
    """
    placed_ = one_bullet(
        "helios-payments", "job", "c1", "Standardised the commit batching in the order consumer"
    )
    write_run(
        run_dir,
        placed=placed_,
        summary="A backend engineer who specializes in payment systems and the data under them.",
    )

    render_fails(repo_root, run_dir, "two different ways")


def test_the_summary_is_outside_the_opener_check(repo_root, run_dir):
    """It is not a Bullet, so it does not compete for an opening word.

    Same standing a lead has under `0032` §7, and harder: there is one Summary, so
    a repeated opener is not a quantity it can have. A page whose Summary opens on
    a Bullet's opening word renders.
    """
    placed_ = one_bullet(
        "helios-payments", "job", "c1", "Cut checkout p99 latency 40% by batching commits"
    )
    write_run(run_dir, placed=placed_, summary="Cut through payment systems for a living.")

    result = render(repo_root, run_dir)
    assert "opens on" not in result.stderr


@pytest.mark.needs_pdflatex
def test_the_summary_carries_its_own_element_marker(repo_root, run_dir):
    """The Overflow check has to be able to name it, and `check_markers_account_for`
    holds the Template's markers and `page_elements` to the same set — so a run that
    got this far already proves both directions."""
    write_run(run_dir)

    render_ok(repo_root, run_dir)

    assert "%% AUTOAPPLY:element:summary:page" in tex(run_dir)


@pytest.mark.needs_pdflatex
def test_a_summary_inside_its_character_budget_can_still_be_too_tall(
    repo_root, run_dir, config_module
):
    """The reason `SUMMARY_CHARS` is a tape and the compile is the gate (`0044` §6).

    A character count cannot say where TeX will break a paragraph. This one is
    inside the budget and still runs to a third typeset line, which is invisible
    everywhere else: it breaks legally, so LaTeX warns about nothing and the page
    comes out a line short of what the allocation was packed for.
    """
    wide = ("MMM " * 55).strip()
    assert len(wide) <= config_module.SUMMARY_CHARS
    write_run(run_dir, summary=wide)

    message = render_fails(repo_root, run_dir, "Summary")
    assert "does not fit" in message
    assert "typeset lines" in message


@pytest.mark.needs_pdflatex
def test_a_standing_block_in_the_profile_is_parsed_and_never_typeset(repo_root, run_dir):
    """`0044` §3 — the Summary's source for what the candidate is, and nothing else.

    It reaches no hole in the Template: the Summary is composed from it at §5 of the
    skill, by a reader, and what lands on the page is that composed sentence. So the
    page must come out with no trace of it — a block that leaked into the PDF would
    be free-prose furniture nothing measured and nothing budgeted.
    """
    path = profile_path(run_dir)
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n## Standing\n\nA backend engineer of some standing.\n",
        encoding="utf-8",
    )
    write_run(run_dir)

    render_ok(repo_root, run_dir)

    assert "of some standing" not in tex(run_dir)


def test_an_unknown_block_in_the_profile_fails_naming_it(repo_root, run_dir):
    """`## Standing` is parsed rather than skipped, and this is what that buys.

    Everything else in this file is validated to the letter — an unknown frontmatter
    key is a hard failure — so a `## ` block that parsed by being ignored would be
    the one place a typo in the maker's own file went quietly nowhere.
    """
    path = profile_path(run_dir)
    path.write_text(
        path.read_text(encoding="utf-8") + "\n## Standign\n\nA backend engineer.\n",
        encoding="utf-8",
    )
    write_run(run_dir)

    message = render_fails(repo_root, run_dir, "Standign")
    assert "Standing" in message, "the message should name the block it expected"


# --------------------------------------------------------------------------
# Lower-bound figures and years (docs/adr/0054-a-figure-may-say-more-than.md)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Cut nightly settlement reconciliation by over 30% across the estate",
        "Cut nightly settlement reconciliation 30%+ across the estate",
        "Cut nightly settlement reconciliation by more than 30% across the estate",
        "Cut nightly settlement reconciliation by at least 30% across the estate",
    ],
)
def test_a_lower_bound_satisfies_an_estimated_tier(repo_root, run_dir, text):
    """`over 30%` and `30%+` are softening, exactly as `~30%` is.

    The tilde alone made some true facts unwritable: a claim whose Evidence says
    "over 150 KPIs" could render neither `150` (flat, refused) nor `~150` (which
    misstates it), so the figure came off the page — and it was a denominator, which
    `0039` calls the first thing a Bullet should reach for.
    """
    write_run(run_dir, one_bullet("helios-payments", "job", "c2", text))

    render_ok(repo_root, run_dir)


def test_a_lower_bound_still_may_not_invent_a_value(repo_root, run_dir):
    """Softening a figure is not a licence to change it. `over 80%` traces to nothing."""
    write_run(
        run_dir,
        one_bullet(
            "helios-payments", "job", "c2", "Cut nightly settlement reconciliation by over 80%"
        ),
    )

    render_fails(repo_root, run_dir, "helios-payments/c2")


def test_a_bare_year_is_a_date_and_not_an_impact_figure(repo_root, run_dir):
    """Both halves of render.py now agree about what a year is.

    `figure_spans` already called `2026` a date and declined to bold it, while
    `check_number_trace` called it an impact figure and demanded it render softened
    against an estimated source. `~2026` is not a thing anyone can write, so a year
    inside an estimated Claim could not be stated at all.
    """
    write_run(
        run_dir,
        one_bullet(
            "helios-payments",
            "job",
            "c2",
            "Cut nightly settlement reconciliation ~30% for the 2026 ledger format",
        ),
    )

    render_ok(repo_root, run_dir)


# --------------------------------------------------------------------------
# 0057 §2 — where Education sits
# --------------------------------------------------------------------------
def profile_with(education_dates: list[str], **fields) -> "render_module.Profile":
    return render_module.Profile(
        Path("profile.md"),
        {"name": "Ada", **fields},
        [{"institution": "X", "dates": dates} for dates in education_dates],
    )


@pytest.mark.parametrize(
    "dates, first",
    [
        (["Expected May 2027"], True),   # still studying
        (["2026"], True),                # finishing this year
        (["Aug 2021 -- May 2025"], True),  # graduated within the year
        (["2018 -- 2022"], False),       # four years on, the work leads
        (["2016", "2027"], True),        # the latest row decides
        (["no year here"], False),
    ],
)
def test_education_leads_while_the_degree_is_recent(dates, first):
    today = __import__("datetime").date(2026, 10, 10)
    assert profile_with(dates).education_first(today) is first


def test_the_profile_can_say_where_education_sits():
    today = __import__("datetime").date(2026, 10, 10)
    assert profile_with(["2018"], education_first="yes").education_first(today) is True
    assert profile_with(["2027"], education_first="no").education_first(today) is False
