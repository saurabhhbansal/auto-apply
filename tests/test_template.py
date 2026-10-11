"""templates/resume.tex.j2 — its contract, and that it compiles.

What is asserted here is the template's *contract*: which holes exist, that Entry
`type` routes to the right section, that Education is static, and that the thing
compiles to one page. What is not asserted is how it looks — per the build spec,
template aesthetics are the maker's eye, not an assertion.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def template_source(repo_root: Path) -> str:
    return (repo_root / "templates" / "resume.tex.j2").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def template_code(template_source: str) -> str:
    """The template with its LaTeX comments stripped.

    Anything checking for a *forbidden* construct has to use this. The template
    documents itself heavily, and those comments legitimately name the things the
    file must not contain — Jinja's default `{{` delimiters, `\\today`. Searching the
    raw text would fail on the prose explaining the rule.
    """
    return "\n".join(
        re.sub(r"(?<!\\)%.*$", "", line) for line in template_source.splitlines()
    )


def render(probe, entries, skill_rows=None) -> str:
    return probe.render(entries, probe.rows_for(2) if skill_rows is None else skill_rows)


# --------------------------------------------------------------------------
# Attribution and layout commitments
# --------------------------------------------------------------------------
def test_mit_attribution_to_the_upstream_template(template_source):
    assert "MIT" in template_source
    assert "sb2nov" in template_source or "github.com/sb2nov/resume" in template_source
    assert "Jake" in template_source
    # The licence text itself, not just a mention of it.
    assert "WITHOUT WARRANTY OF ANY KIND" in template_source


def test_single_column(template_code):
    """ATS-safety fixes the layout as single-column, so no multi-column package."""
    for banned in [r"\usepackage{multicol}", "twocolumn", r"\begin{multicols}"]:
        assert banned not in template_code


def test_ats_unicode_mapping_is_on(template_source):
    """The whole reason this lineage is LaTeX — a machine-readable PDF."""
    assert r"\pdfgentounicode=1" in template_source
    assert r"\input{glyphtounicode}" in template_source


def test_no_today_so_a_rebuild_is_byte_identical(template_code):
    assert r"\today" not in template_code


# --------------------------------------------------------------------------
# The Jinja2 holes
# --------------------------------------------------------------------------
def test_holes_use_the_latex_safe_delimiters(template_code):
    r"""\VAR and \BLOCK, never Jinja's default braces, which collide with LaTeX."""
    assert r"\VAR{" in template_code
    assert r"\BLOCK{" in template_code
    assert "{{" not in template_code
    assert "{%" not in template_code


def test_every_named_hole_is_present(probe):
    """Static profile, Entry blocks, Bullets and the Skills rows."""
    tex = render(probe, [probe.entry("job", 1, ["a distinctive bullet"])],
                 skill_rows=[probe.row("Languages", ["Kafka", "Go"])])

    assert probe.SYNTHETIC_PROFILE["name"] in tex          # Static profile
    assert probe.SYNTHETIC_PROFILE["email"] in tex
    assert "Senior Software Engineer 1" in tex             # Entry block
    assert "Synthetic Org 1" in tex
    assert "a distinctive bullet" in tex                   # Bullets
    assert r"\textbf{Languages:} Kafka, Go" in tex         # a Skills row


def test_a_skills_row_is_markered_by_number_and_labelled_in_bold(probe):
    """The label is run-authored text, so it is typeset and never put in a marker.

    A `%` or a stray character inside a marker comment is the breakage the
    Template's own marker block warns about, and the Education row precedent is to
    number instead. The label is not lost — render.py carries the human wording
    separately, which is what lets an overflow be reported as "the AI & GenAI
    skills row" while the marker stays `skills:3`.
    """
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])], skill_rows=[
        probe.row("AI & GenAI", ["Claude Code"]),
        probe.row("Languages", ["Python"]),
    ])
    assert "%% AUTOAPPLY:element:skills:1" in tex
    assert "%% AUTOAPPLY:element:skills:2" in tex
    assert "AI \\& GenAI" not in re.findall(r"%% AUTOAPPLY:element:skills:\S+", tex)
    assert r"\textbf{AI \& GenAI:} Claude Code" in tex


def test_the_skills_heading_carries_no_adjective(probe):
    """`Skills`, not `Technical Skills`.

    A Category row's label is named from the posting's own vocabulary under `0020`,
    and a posting may state a non-technical must-have as plainly as a technical one —
    the page this changed on carried a `Collaboration` row under the old heading. The
    heading's height is SECTION_LINES whatever the string, so this owes no
    recalibration (`docs/adr/0031-the-entry-header-is-built.md` §6).
    """
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])], skill_rows=[
        probe.row("Languages", ["Python"]),
        probe.row("Collaboration", ["User acceptance testing"]),
    ])
    assert r"\section{Skills}" in tex
    # The Template's own comment says what the heading used to be, and comments are
    # copied into every rendered resume.tex — so this reads the headings, not the file.
    assert re.findall(r"^\\section\{(.+)\}$", tex, re.M) == [
        "Summary", "Experience", "Skills", "Education"
    ]


def test_a_run_with_no_skills_rows_drops_the_section_heading_and_all(probe):
    """The Packer hands the whole reservation back below the two-row floor, so the
    heading has to go with the rows or the budget and the page disagree."""
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])], skill_rows=[])
    assert r"\section{Skills}" not in tex
    assert not re.search(r"^\s+\\resumeSkillsListStart", tex, re.M)
    assert not re.search(r"^%% AUTOAPPLY:element:skills:", tex, re.M)


def test_an_undefined_hole_is_an_error_not_a_blank(probe):
    """StrictUndefined, so a renaming mistake fails loudly rather than rendering
    an empty header."""
    import jinja2

    with pytest.raises(jinja2.UndefinedError):
        probe.jinja_env().get_template(probe.TEMPLATE_NAME).render(
            profile={"name": "Ada"}, entries=[], skill_rows=[]
        )


# --------------------------------------------------------------------------
# Section routing
# --------------------------------------------------------------------------
def section_body(tex: str, name: str) -> str:
    """The text between one \\section and the next (or the end)."""
    match = re.search(
        r"\\section\{" + re.escape(name) + r"\}(.*?)(?=\\section\{|\\end\{document\})",
        tex,
        re.S,
    )
    assert match, f"no {name!r} section in the rendered .tex"
    return match.group(1)


def test_job_routes_to_experience_and_project_to_projects(probe):
    tex = render(probe, [
        probe.entry("job", 1, ["job bullet one"]),
        probe.entry("project", 1, ["project bullet one"]),
    ])

    experience = section_body(tex, "Experience")
    assert "job bullet one" in experience
    assert "project bullet one" not in experience

    projects = section_body(tex, "Projects")
    assert "project bullet one" in projects
    assert "job bullet one" not in projects


def test_routing_ignores_the_order_entries_arrive_in(probe):
    """The Packer hands over one score-ordered pool, so a project can precede a
    job. Routing must still put each in its own section."""
    tex = render(probe, [
        probe.entry("project", 1, ["project first"]),
        probe.entry("job", 1, ["job second"]),
    ])
    assert "project first" in section_body(tex, "Projects")
    assert "job second" in section_body(tex, "Experience")


def test_a_section_with_no_entries_is_omitted_entirely(probe):
    """An empty itemize is a LaTeX error, so the section has to disappear."""
    tex = render(probe, [probe.entry("job", 1, ["only a job"])])
    assert r"\section{Projects}" not in tex
    assert r"\section{Experience}" in tex


def test_bullets_appear_in_the_order_given(probe):
    tex = render(probe, [probe.entry("job", 1, ["first bullet", "second", "third"])])
    body = section_body(tex, "Experience")
    assert body.index("first bullet") < body.index("second") < body.index("third")


def test_a_project_header_is_one_row_and_a_job_header_is_two(probe):
    """0057 §3 — a project has no employer or office, so its header is one row with
    the stack and link beside the name. Each macro is charged by its own constant,
    ENTRY_HEADER_LINES and PROJECT_HEADER_LINES, and the probe measures both."""
    tex = render(probe, [probe.entry("job", 1, ["a"]), probe.entry("project", 1, ["b"])])
    assert len(re.findall(r"\\resumeSubheading", section_body(tex, "Experience"))) == 1
    assert r"\resumeProjectHeading" not in section_body(tex, "Experience")
    projects = section_body(tex, "Projects")
    assert len(re.findall(r"\\resumeProjectHeading", projects)) == 1
    assert r"\resumeSubheading" not in projects
    assert "Python, PostgreSQL, Docker" in projects
    assert r"\href{https://github.com/adalovelace/project-1}" in projects


def test_education_leads_the_page_when_the_profile_says_so(probe):
    """0057 §2 — a student's Education sits above Experience; the section is the same."""
    entries = [probe.entry("job", 1, ["a job bullet"])]
    source = (probe.TEMPLATE_DIR / probe.TEMPLATE_NAME).read_text(encoding="utf-8")
    env = probe.jinja_env()
    first = env.from_string(source).render(
        profile=probe.with_link_targets(probe.SYNTHETIC_PROFILE), education_first=True,
        entries=entries,
        skill_rows=probe.rows_for(2), summary="s", supporting_sections=[],
    )
    last = render(probe, entries)
    assert first.index(r"\section{Education}") < first.index(r"\section{Experience}")
    assert last.index(r"\section{Education}") > last.index(r"\section{Experience}")
    # At the top, the one row is the last row and takes the -8pt twin (§2's spacing).
    assert first.count("\\resumeEducationRowAbove\n") == 1
    assert last.count("\\resumeEducationRow\n") == 1


# --------------------------------------------------------------------------
# Education is static
# --------------------------------------------------------------------------
def test_education_is_a_static_block_from_the_profile(probe):
    tex = render(probe, [probe.entry("job", 1, ["a job bullet"])])
    education = section_body(tex, "Education")
    school = probe.SYNTHETIC_PROFILE["education"][0]
    assert school["institution"] in education
    assert school["degree"] in education
    assert "a job bullet" not in education


def test_education_rows_use_their_own_macro(probe):
    r"""Education is typeset by \resumeEducationRow, not \resumeSubheading.

    Splitting the two is what let ENTRY_HEADER_LINES drop from 3 to 2 (issue #31):
    an Education row is the taller element, and welded to the Entry header's macro
    it could not be tightened, because the same trailing \vspace also sets the gap
    above the first Bullet. Nothing sits under an Education row, so on its own macro
    it tightens for free.

    This is a rendering-side check only. That the two macros stay within ONE shared
    constant is a question about typeset height, which only the calibration probe
    can answer — see its "Education row costs the same lines as an Entry header".
    """
    tex = render(probe, [probe.entry("job", 1, ["a job bullet"])])
    education = section_body(tex, "Education")
    assert len(re.findall(r"\\resumeEducationRow", education)) == 1
    assert r"\resumeSubheading" not in education


def test_education_never_competes_with_entries(probe):
    """It comes from profile.md, so no Entry can land in it and it renders whatever
    the entries are."""
    with_entries = render(probe, [probe.entry("job", 1, ["x"])])
    school = probe.SYNTHETIC_PROFILE["education"][0]["institution"]
    assert school in section_body(with_entries, "Education")

    many = render(probe, [probe.entry("job", i, ["x"]) for i in range(6)])
    assert school in section_body(many, "Education")


# --------------------------------------------------------------------------
# Compiling
# --------------------------------------------------------------------------
@pytest.mark.needs_pdflatex
def test_synthetic_data_compiles_to_one_page(probe, tmp_path):
    entries = probe.build_entries(jobs=3, projects=2, total_bullets=9)
    tex = render(probe, entries, skill_rows=probe.rows_for(4))
    pages, _ = probe.compile_tex(tex, "test_onepage")
    assert pages == 1


@pytest.mark.needs_pdflatex
def test_a_full_page_of_synthetic_entries_still_fits_the_budget(probe, config_module):
    """The budget config.py publishes must actually fit, or every downstream run is
    working from a number the page will not honour."""
    jobs, projects, education_rows = 3, 2, 1
    budget = probe.predict_bullet_capacity(
        config_module, jobs, projects, education_rows, probe.skills_sample()
    )

    tex = render(probe, probe.build_entries(jobs, projects, budget),
                 skill_rows=probe.skills_sample())
    pages, _ = probe.compile_tex(tex, "test_budget")
    assert pages == 1


@pytest.mark.needs_pdflatex
def test_no_realistic_bullet_at_the_character_budget_wraps(probe, config_module):
    """CHARS_PER_BULLET is only meaningful if a Bullet that long does not wrap.

    A wrapped Bullet costs two lines while the budget charges one, which is exactly
    how you get a two-page PDF with every length lint passing — the case the spec
    says means the constants are miscalibrated.

    Asserted by measuring typeset width directly rather than by looking at where
    content landed on the page: width is the property the constant encodes, and a
    page-geometry check would also be picking up glue.
    """
    at_budget = [s[: config_module.CHARS_PER_BULLET] for s in probe.WIDTH_SAMPLES]
    line_width, widths = probe.measure_widths(at_budget, "test_widths")

    for sample, width in zip(at_budget, widths):
        assert width <= line_width, (
            f"a {len(sample)}-character Bullet typesets to {width:.1f}pt, over the "
            f"{line_width:.1f}pt line: {sample[:60]}..."
        )


@pytest.mark.needs_pdflatex
def test_no_lead_at_the_bold_aware_budget_wraps(probe, config_module):
    """BOLD_LEAD_CHARS is only meaningful if a lead spending it does not wrap.

    The Bullet check above, at the lead's own `\\linewidth` and with the lead's own
    bold charge. A wrapped lead costs two lines where LEAD_LINES charges one, and the
    failure is silent: a paragraph breaks legally and warns about nothing
    (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).

    The samples are composed the way `check_lead_lengths` will charge them — a real
    bold span, the plain remainder cut to whatever the tape has left — so this is the
    budget being spent rather than a length being asserted.
    """
    at_budget = probe.measure_lead_at_budget(
        config_module.LEAD_CHARS, config_module.BOLD_LEAD_CHARS, "test_lead_budget"
    )
    line_width, _ = probe.measure_lead_widths("test_lead_width")

    for text, plain, width in at_budget:
        assert width <= line_width, (
            f"a lead spending the full {config_module.LEAD_CHARS}-character budget "
            f"({plain} plain characters and a bold span) typesets to {width:.1f}pt, "
            f"over the {line_width:.1f}pt line: {text[:60]}..."
        )


@pytest.mark.needs_pdflatex
def test_the_character_budget_is_not_needlessly_tight(probe, config_module):
    """The budget should be near the real limit, not far under it.

    A CHARS_PER_BULLET well below what fits costs a line of evidence on every
    résumé, and it would pass the test above trivially, so the tightness is worth
    asserting too. One character over the budget is allowed to still fit — the
    constant is the worst case over several samples, not the best.
    """
    over_budget = [s[: config_module.CHARS_PER_BULLET + 12] for s in probe.WIDTH_SAMPLES]
    line_width, widths = probe.measure_widths(over_budget, "test_widths_over")
    assert any(w > line_width for w in widths), (
        "every sample still fits 12 characters over the budget, so CHARS_PER_BULLET "
        "is leaving usable width on the table — re-run the calibration"
    )


# --------------------------------------------------------------------------
# The Header-fit check's instrumentation
# --------------------------------------------------------------------------
#: The Template brackets everything that exists to be measured rather than
#: typeset. Cutting between the markers yields the same Template without the
#: Header-fit instrumentation, which is what the neutrality check builds against.
INSTRUMENTATION = re.compile(
    r"^%% BEGIN header-fit instrumentation$.*?^%% END header-fit instrumentation$\n?",
    re.M | re.S,
)

#: A wrap costs a whole line; an unwrapped line measures the same in both boxes.
#: The two are an order of magnitude apart, so this floor is not a delicate number.
#:
#: It is deliberately a copy of tools/render.py's WRAP_NOISE_PT rather than an
#: import, for the reason tests/conftest.py gives for the probe: what is asserted
#: below is the *template's* behaviour, and a bug in render.py must not be able to
#: change the answer.
WRAP_FLOOR_PT = 1.0


def wrapped(measured: dict) -> bool:
    """TeX's verdict on one header line: did the line-broken box come out taller?"""
    return measured["broken"] > measured["flat"] + WRAP_FLOOR_PT


def page_drawing_stream(pdf_path) -> bytes:
    """Page one's decompressed content stream — every glyph and where it landed."""
    from pypdf import PdfReader

    return PdfReader(str(pdf_path)).pages[0].get_contents().get_data()


@pytest.mark.needs_pdflatex
def test_neither_header_line_of_a_realistic_profile_wraps(probe):
    """The header analogue of the Bullet-width test above, and the same stake.

    HEADER_LINES charges a one-line name over a one-line contact line. A wrapped
    header costs a second line that nothing charges for, and unlike an over-long
    Bullet it is silent — a centred line breaks legally, so LaTeX warns about
    nothing.
    """
    fit = probe.measure_header_fit(probe.SYNTHETIC_PROFILE, "test_hf_ok")
    for line in ("name", "contact"):
        assert not wrapped(fit[line]), (
            f"the {line} line of the synthetic profile wraps "
            f"({fit[line]['width']:.1f}pt against a {fit[line]['avail']:.1f}pt line), "
            f"so HEADER_LINES was calibrated against a header it should refuse"
        )


@pytest.mark.needs_pdflatex
@pytest.mark.parametrize(
    "line, overrides",
    [
        ("contact", {"linkedin": "linkedin.com/in/ada-lovelace"}),
        ("name", {"name": "Venkataraghavan Chandrasekhar Balasubramanian"}),
    ],
)
def test_a_header_line_that_runs_long_shows_up_as_a_taller_box(probe, line, overrides):
    """Both header lines are guarded, and the wrap is visible as height.

    Both values are ordinary — a LinkedIn handle with the hyphen the site puts in a
    two-word name, and a name of a length people have. They are measured against the
    template's margins, so they are pinned here and again in tests/test_render.py,
    and a change to those margins moves both. A4 moved them: the handle that wraps is
    now the hyphenated one, and the unhyphenated one below is the character shorter
    that still fits.
    """
    fit = probe.measure_header_fit(probe.header_profile(**overrides), "test_hf_wrap")
    assert wrapped(fit[line]), (
        f"the {line} line typesets {fit[line]['width']:.1f}pt against a "
        f"{fit[line]['avail']:.1f}pt line and TeX did not break it"
    )
    other = "name" if line == "contact" else "contact"
    assert not wrapped(fit[other]), "only the line that ran long may be reported"


@pytest.mark.needs_pdflatex
def test_a_header_line_wider_than_the_page_can_still_fit(probe):
    """Why the check reads a height and not a width.

    A contact line one character shorter than the wrapping one above is *still*
    1.87pt wider than the line it sits on, and TeX sets it on one line anyway by
    shrinking its interword glue. How far that glue will shrink is a property of
    the line's own content, so a width comparison is not conservative — it is
    wrong, and it would reject a header the page has room for.
    """
    fit = probe.measure_header_fit(
        probe.header_profile(linkedin="linkedin.com/in/adalovelace"), "test_hf_edge"
    )
    contact = fit["contact"]
    assert contact["width"] > contact["avail"], (
        "this case is only interesting while the line measures over-width; re-pick "
        "the value if the template's margins have moved"
    )
    assert not wrapped(contact)


@pytest.mark.needs_pdflatex
def test_descenders_raise_the_header_without_wrapping_it(probe):
    """A taller header line is not a wrapped one.

    The check compares one line against itself, not against a fixed height, which
    is what keeps a name full of descenders — measurably taller than one without —
    from reading as a failure.
    """
    plain = probe.measure_header_fit(probe.header_profile(name="Ada Lovelace"), "test_hf_a")
    descending = probe.measure_header_fit(
        probe.header_profile(name="Jyoti Bhargava Ramanujan"), "test_hf_b"
    )
    assert descending["name"]["flat"] > plain["name"]["flat"]
    assert not wrapped(descending["name"])


@pytest.mark.needs_pdflatex
def test_the_header_fit_instrumentation_moves_nothing_on_the_page(probe, template_source):
    """It measures the shipped document, so it must not change the shipped document.

    This is what lets HEADER_LINES stay at 3 with no recalibration owed: the same
    résumé built from the Template with the instrumentation cut out draws exactly
    the same bytes. \\sbox measures into a register and \\typeout writes to the log,
    and the measurement is placed after the last section so that no font it touches
    can renumber a font resource the page uses.
    """
    stripped = INSTRUMENTATION.sub("", template_source)
    assert stripped != template_source, "the instrumentation markers have moved"
    assert r"\headerNameLine" in stripped, "the header macros are not instrumentation"

    entries = probe.build_entries(jobs=2, projects=1, total_bullets=6)
    skills = probe.rows_for(2)
    probe.compile_tex(probe.render(entries, skills), "test_hf_instrumented")
    probe.compile_tex(probe.render_source(stripped, entries, skills), "test_hf_plain")

    instrumented = probe.OUT_DIR / "test_hf_instrumented.pdf"
    plain = probe.OUT_DIR / "test_hf_plain.pdf"
    assert page_drawing_stream(instrumented) == page_drawing_stream(plain)


# --------------------------------------------------------------------------
# The Overflow check's markers and threshold
# --------------------------------------------------------------------------
#: Every marker the Overflow check attributes a report to, whole lines. Cutting
#: them yields the same Template with no attribution, which is what the inertness
#: check below builds against. Anchored at column 0, so the indented example inside
#: the Template's own comment block is not one of them.
ELEMENT_MARKERS = re.compile(r"^%% AUTOAPPLY:element:[a-z]+:\S+\n", re.M)

#: pdfTeX's own words, and the only thing render.py's Overflow check reads.
OVERFULL = re.compile(r"Overfull \\hbox \(([0-9.]+)pt too wide\)")

#: An Entry title that runs past the right margin by less than the Template's own
#: \hfuzz — measured at 0.88pt, against a 2pt threshold and pdfTeX's own 0.1pt
#: reporting floor, so it has room either side. It is pinned rather than searched
#: for; the assertions below fail loudly if the margins or the font have moved it.
#: They did, when the page became A4: the old title ran 17pt over on the narrower
#: line and this is its re-pick.
BARELY_OVER = "Senior Staff Software Engineer, Payments Platform and Ledger Alignment"


@pytest.mark.needs_pdflatex
def test_the_overflow_markers_move_nothing_on_the_page(probe, template_source):
    """They exist to name a file in a failure message, so they must not typeset.

    A LaTeX comment on its own line contributes nothing to the output — not even an
    inter-token space — which is what lets the attribution owe no recalibration,
    where making the macros wrap instead would owe a full one.

    It is the *own line, between macro calls* half that has to hold, not the comment
    syntax: `%` eats the rest of the line **and the line break**, so one dropped
    into running prose welds the word before it to the word after. Every marker here
    sits between two macro calls, and this compares the page's drawing stream with
    them and without them to say so.
    """
    stripped = ELEMENT_MARKERS.sub("", template_source)
    assert stripped != template_source, "the element markers have moved"
    assert not ELEMENT_MARKERS.search(stripped)

    entries = probe.build_entries(jobs=2, projects=1, total_bullets=6)
    skills = probe.rows_for(2)
    probe.compile_tex(probe.render(entries, skills), "test_markers_on")
    probe.compile_tex(probe.render_source(stripped, entries, skills), "test_markers_off")

    on = probe.OUT_DIR / "test_markers_on.pdf"
    off = probe.OUT_DIR / "test_markers_off.pdf"
    assert page_drawing_stream(on) == page_drawing_stream(off)


@pytest.mark.needs_pdflatex
def test_an_overflow_a_reader_could_not_see_is_never_reported(probe, template_source):
    r"""The Overflow check's threshold lives here, in \hfuzz, and TeX applies it.

    render.py fails on anything TeX still reports and carries no constant of its
    own, so the judgement about what is visible on a printed page is made once, in
    TeX's units — the same move the Header-fit check makes one level up.

    The second half is what keeps this from passing vacuously. A title that simply
    fitted would satisfy the first assertion forever; compiling the same title with
    the threshold dropped to zero pins that it really is over-wide, and by how much.
    """
    entries = [dict(probe.entry("job", 1, ["an ordinary bullet"]), title=BARELY_OVER)]
    _, log = probe.compile_tex(probe.render(entries, probe.rows_for(2)), "test_hfuzz_on")
    assert not OVERFULL.findall(log), "a sub-\\hfuzz overhang reached the log"

    loosened = template_source.replace(r"\hfuzz=2pt", r"\hfuzz=0pt")
    assert loosened != template_source, "the Template no longer sets \\hfuzz to 2pt"
    _, log = probe.compile_tex(
        probe.render_source(loosened, entries, probe.rows_for(2)), "test_hfuzz_off"
    )

    reported = [float(points) for points in OVERFULL.findall(log)]
    assert reported, "re-pick BARELY_OVER: this title now fits the line outright"
    assert 0 < reported[0] < 2, (
        f"BARELY_OVER runs {reported[0]:.2f}pt over, which is no longer inside the "
        f"Template's 2pt \\hfuzz — re-pick the title, or the threshold has moved"
    )


@pytest.mark.needs_pdflatex
def test_two_builds_of_the_same_tex_are_byte_identical(probe):
    """An unchanged run folder must yield an unchanged PDF, so that a git diff
    always means something actually changed.

    Two *fresh* builds, under different stems, so neither inherits the other's
    .aux — that is the claim worth making, and it is the one that catches pdfTeX's
    creation-date and random-trailer-ID stamps.
    """
    tex = render(probe, probe.build_entries(2, 1, 6))
    probe.compile_tex(tex, "test_repro_a")
    probe.compile_tex(tex, "test_repro_b")
    first = (probe.OUT_DIR / "test_repro_a.pdf").read_bytes()
    second = (probe.OUT_DIR / "test_repro_b.pdf").read_bytes()
    assert first == second


@pytest.mark.needs_pdflatex
def test_a_recompile_over_an_existing_aux_is_byte_identical(probe):
    """The re-run case: the run folder already holds last run's .aux and .out."""
    tex = render(probe, probe.build_entries(2, 1, 6))
    probe.compile_tex(tex, "test_repro_rerun")
    probe.compile_tex(tex, "test_repro_rerun")
    settled = (probe.OUT_DIR / "test_repro_rerun.pdf").read_bytes()
    probe.compile_tex(tex, "test_repro_rerun")
    assert (probe.OUT_DIR / "test_repro_rerun.pdf").read_bytes() == settled


def test_the_summary_sits_above_every_section(probe):
    """`0044` §1 — the page's opening claim, and the first prose on it."""
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])])

    assert r"\resumeSummary{\summaryLine}" in tex
    body = tex[tex.index(r"\begin{document}"):]
    assert body.index(r"\resumeSummary") < body.index(r"\section{Experience}")


def test_the_summary_is_not_guarded_by_emptiness(probe):
    """Unlike Skills and Projects, which vanish whole when there is nothing in them.

    The budget charges SUMMARY_LINES unconditionally, so the Template has nowhere to
    put a guard that would not make the page disagree with what was packed —
    render.py refuses a run with no `## Summary` instead (`0044` §5).
    """
    tex = probe.render_source(
        (probe.TEMPLATE_DIR / probe.TEMPLATE_NAME).read_text(encoding="utf-8"),
        [probe.entry("job", 1, ["a bullet"])],
        probe.rows_for(2),
        summary="",
    )

    assert r"\resumeSummary{\summaryLine}" in tex


def test_the_summary_carries_an_element_marker_on_its_own_line(probe):
    """Every element that can overflow carries one, and a marker welded to running
    prose would comment out the line after it."""
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])])

    lines = tex.splitlines()
    marker = lines.index("%% AUTOAPPLY:element:summary:page")
    assert lines[marker + 1].strip().startswith(r"\resumeSummary")


def test_the_summary_fit_measurement_reaches_the_log(probe):
    """The Summary's overflow is silent — it breaks legally — so the Template asks
    TeX how tall it came out and render.py refuses the run on the answer."""
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])])
    assert r"\summaryFitLine" in tex

    _, log = probe.compile_tex(tex, "test_summaryfit")

    assert probe.SUMMARY_FIT.search(log), "no AUTOAPPLY:summaryfit measurement in the log"


def test_the_summary_measurement_sits_inside_the_instrumentation_brackets(probe):
    """It measures a box that is never shipped, and that box reports overfull \\hbox
    warnings of its own — so render.py has to be able to drop them, which it does by
    ignoring everything between the BEGIN/END markers."""
    tex = render(probe, [probe.entry("job", 1, ["a bullet"])])

    begin = tex.index("%% BEGIN header-fit instrumentation", tex.index(r"\begin{document}"))
    end = tex.index("%% END header-fit instrumentation", begin)
    assert begin < tex.index(r"\summaryFitLine", begin) < end


# --------------------------------------------------------------------------
# The supporting sections
# --------------------------------------------------------------------------


def document_body(tex: str) -> str:
    """Everything the page actually typesets, preamble and macros excluded.

    Split on the LAST `\\begin{document}`, not the first: the template's own header
    comment names it while explaining where the instrumentation lives, and every `%%`
    comment there is copied verbatim into each rendered resume.tex.
    """
    return re.split(r"^\\begin\{document\}$", tex, flags=re.M)[-1]


def test_a_run_with_no_supporting_sections_emits_none_of_the_three(probe):
    """The usual page. All three vanish whole — heading, list and markers.

    They are on a page for one of exactly two reasons and neither holds on most runs
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §7).
    """
    tex = probe.render(probe.build_entries(jobs=1, projects=1, total_bullets=4), probe.rows_for(2))

    for heading in ("Certifications", "Positions of Responsibility", "Extracurriculars"):
        assert f"\\section{{{heading}}}" not in tex
    assert "AUTOAPPLY:element:supporting" not in tex
    assert "\\resumeSupportingRow" not in document_body(tex)


def test_the_supporting_sections_sit_between_skills_and_education(probe):
    """Page order, which is where the white space the room trigger spends actually is."""
    tex = probe.render(
        probe.build_entries(jobs=1, projects=1, total_bullets=4),
        probe.rows_for(2),
        supporting=probe.supporting_for(2),
    )
    body = document_body(tex)

    assert body.index("\\section{Skills}") < body.index("\\section{Certifications}")
    assert body.index("\\section{Certifications}") < body.index("\\section{Education}")


def test_every_supporting_row_carries_a_marker_on_its_own_line(probe):
    """One marker per row, keyed by slug — the Overflow check attributes by nearest above."""
    tex = probe.render(
        probe.build_entries(jobs=1, projects=1, total_bullets=4),
        probe.rows_for(2),
        supporting=probe.supporting_for(3),
    )

    markers = [
        line for line in tex.splitlines() if line.startswith("%% AUTOAPPLY:element:supporting:")
    ]
    assert len(markers) == 3
    for marker in markers:
        assert marker.strip() == marker, "a marker welded to something else on its line"


@pytest.mark.needs_pdflatex
def test_the_supporting_markers_move_nothing_on_the_page(probe, template_source):
    """The same guarantee the other markers carry, on the rows that are new.

    A comment on its own line contributes nothing to the output, which is what lets
    the attribution owe no recalibration — and it has to be re-shown here because
    these markers sit inside a list rather than between two \\section blocks.
    """
    stripped = ELEMENT_MARKERS.sub("", template_source)
    entries = probe.build_entries(jobs=1, projects=1, total_bullets=4)
    skills = probe.rows_for(2)
    supporting = probe.supporting_for(3)

    probe.compile_tex(probe.render(entries, skills, supporting=supporting), "test_sup_on")
    probe.compile_tex(
        probe.render_source(stripped, entries, skills, supporting=supporting), "test_sup_off"
    )

    on = probe.OUT_DIR / "test_sup_on.pdf"
    off = probe.OUT_DIR / "test_sup_off.pdf"
    assert page_drawing_stream(on) == page_drawing_stream(off)
