#!/usr/bin/env python3
"""Measure the Page-budget constants against templates/resume.tex.j2.

This is the executable half of docs/calibration.md. Read that first — it says
what each constant means and how to judge the output.

It lives under tests/ because it is development machinery, and it deliberately does
not import tools/render.py: calibration must isolate the template, so a bug in
render.py's escaping, lints or compilation cannot move a constant.

Method, in two halves.

Interior elements — the Bullet line, an Entry header, a section heading, the profile
header — are measured with markers riding inside Bullet holes, so the template is
never edited to be measured. A probe Bullet carries
``\\typeout{AUTOAPPLY:<name>:\\the\\pagetotal}``, and the gap between two markers is
the real typeset height of whatever sits between them.

Everything at the bottom of the page — the Skills rows, the Education rows, the
page's own capacity — is measured by overflow or by a whole-page differential
instead: synthetic entries at known Bullet counts, compiled, judged geometrically.
\\pagetotal is useless there, because by the time a marker in the last element fires
the page has already been shipped.

The Summary is a third case and the differential is the reason: it sits directly
under the profile header with no gap to put a marker in, so it is priced against the
same page built with its heading and its call site removed. A \\pagetotal reading
inside its own text would land 9.87pt above where the block begins and charge that
glue to HEADER_LINES. The heading comes out with the prose because \\addvspace merges
the glue between them, so neither half is separately priceable — see SUMMARY_BLOCK.

The geometric criterion is the point: "still one page" is NOT the test, because
pdfTeX compresses vertical glue and keeps cramming rather than breaking.

Usage:
    python tests/calibration/probe.py            # measure and print the report
    python tests/calibration/probe.py --keep     # leave the PDFs in out/ to look at
"""

from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "templates"
TEMPLATE_NAME = "resume.tex.j2"
OUT_DIR = Path(__file__).resolve().parent / "out"

# One TeX point is 1/72.27 inch. Reported for the human reading the report.
PT_PER_INCH = 72.27

# Realistic résumé prose, used to measure how many characters fit on one line.
#
# Deliberately a spread rather than one sentence, and the WORST sample wins:
# character widths differ, the lint is a character count, and it has to hold for
# whichever Bullet Opus actually writes. So the set leans towards what makes a
# line wide — capitalised tech names, capitalised sentence starts, digits, and
# few of the narrow letters (i, l, t, f) that flatter an average.
#
# What is NOT in here is an adversarial string like "WWW MMM WWW". It would win
# every time and drive the budget down by 40%, and it is not English: no Bullet
# Opus writes looks like that. Calibrating against it would cost real lines on
# every résumé to defend against prose nobody will write.
WIDTH_SAMPLES = [
    "Rewrote the order-ingest consumer to batch Kafka commits, cutting p99 "
    "checkout latency 40% and clearing the nightly backlog",
    "Owned the migration of 34 services from a shared Postgres instance to "
    "per-service schemas, coordinating cutover across four teams",
    "Introduced contract tests at the payments boundary after a silent schema "
    "change broke settlement for two days",
    "Rebuilt AWS EKS autoscaling on Karpenter, KEDA and Prometheus, cutting "
    "GPU spend roughly 30% across ML Platform",
    "Wrote the OAuth2 and SAML SSO broker Okta, Google Workspace and Azure AD "
    "all authenticate against today",
    "Cut Kafka Streams rebalance storms by moving RocksDB state to EBS gp3, "
    "halving Black Friday recovery time",
]

# The entry arc's lead line (docs/adr/0032-the-entry-arc.md §4): one unbulleted
# line, wider than a Bullet because it sits one list level shallower. Widest wins,
# same discipline as WIDTH_SAMPLES — realistic sentences carrying a situation and
# an aggregate, the two shapes a lead actually holds.
LEAD_SAMPLES = [
    "The whole monthly reporting cycle was hand-run; automating five of its steps "
    "gave back ~17.5 hours a month.",
    "Manuals had to be translated by hand, line by line; the pipeline got them "
    "~95% usable, run by the writers themselves.",
    "Nothing checked a generated resume's numbers before this project wrote the "
    "checks that do, closing the gap between claimed and provable.",
    "Every release needed a day of manual smoke-testing before a recorded suite "
    "replaced it on every merge, cutting the wait to minutes.",
    "Four data sources needed a dedicated analyst's time until a single copilot "
    "unified them behind one plain-language interface.",
    "The team argued over which of four translation models to trust until a "
    "benchmark against verified text settled it for good.",
]

#: The BOLD runs a lead carries, once the lead is allowed to carry them
#: (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum). This is
#: `LEAD_CHARS`'s bold twin, and it is measured from the two shapes emphasis actually
#: produces and no third: a figure grown over the noun that gives it meaning (`0046`
#: §2) and a declared vocabulary term (`0046` §4). Widest wins, same discipline as
#: every other rate here.
#:
#: WHAT IS DELIBERATELY NOT IN HERE IS A BARE ALL-CAPS ACRONYM — `GPT`, `LLM`, `R&D`.
#: They are real terms and a lead may well bold one; what they are not is a RATE. A
#: three-character all-caps token measures 8.30 pt/char with no lowercase letters to
#: average against, which is the `WWW MMM WWW` case WIDTH_SAMPLES already refuses one
#: block up: it would win every time and drive the budget down by 40%. Measured
#: against a real page, taking it would refuse a real entry's lead — 101
#: characters carrying one 19-character bold span, which typesets 474.74pt inside a
#: 514.40pt line, 40pt to spare. A constant that refuses the sentence this ADR was
#: reopened to set in bold is measuring the wrong thing.
#:
#: The excess a short acronym actually spends is bounded and small — three characters
#: at 8.30 against a charged 6.40 is 5.7pt, well inside the interword shrink a line
#: this length carries — and the gate behind the tape is not this constant anyway: it
#: is `check_overflow`, which reads pdfTeX's own overfull-hbox report and already
#: attributes it to the lead element by marker.
LEAD_BOLD_SAMPLES = [
    # A figure grown over its unit noun (`0046` §2). The caps-heavy unit nouns are
    # the wide end of this shape and one of them wins the whole family.
    "~30% GPU spend",
    "~150 KPIs",
    "~17.5 hours a month",
    "~2,100 lines",
    "~95% usable",
    # A declared vocabulary term (`0046` §4), from one word to the longest realistic.
    "Gemini",
    "Claude Code",
    "Google BigQuery",
    "Apple Health",
    "Machine Learning Platform",
    "Streamlit",
]

# The Summary (docs/adr/0044-the-page-opens-on-a-summary.md): one unbulleted
# paragraph at the top of the page, two typeset lines, at top level rather than
# inside any list — so its \linewidth is the full \textwidth and neither
# CHARS_PER_BULLET nor LEAD_CHARS may stand in for it.
#
# Widest wins, same discipline as WIDTH_SAMPLES and LEAD_SAMPLES. These lean the way
# a real Summary leans, which is what makes them the right samples: it is the one
# element licensed to echo the posting's vocabulary, so it is dense with capitalised
# technology names — the widest characters on the page — at a far higher rate than a
# Bullet ever carries.
SUMMARY_SAMPLES = [
    "Final-year Computer Science undergraduate building generative AI applications "
    "end to end: AI-driven business copilots, NLP pipelines and LLM decision "
    "systems, from data pre-processing through to the Python services around them.",
    "AI application developer across generative AI, natural language processing "
    "and predictive analytics, with production Python, Google BigQuery and "
    "multi-source data automation behind copilots that leadership reads monthly.",
    "Software engineer in AI Native Product Engineering: prompt engineering, model "
    "benchmarking and optimization, cross-functional delivery with clients, and "
    "the software design principles underneath scalable machine learning work.",
]

#: A Summary one clause too long — SUMMARY_SAMPLES[0] with a few more of the terms a
#: posting supplies, which is exactly how a real one goes over. Never composed: it
#: exists so the report can SHOW the runtime fit ceiling sitting between a legal
#: Summary and an illegal one rather than asserting that it does. Kept just over the
#: line on purpose — an obviously enormous string would make that check pass while
#: measuring nothing.
OVERLONG_SUMMARY = SUMMARY_SAMPLES[0] + " Also fluent in TensorFlow, PyTorch and R."


# --------------------------------------------------------------------------
# Rendering and compiling
# --------------------------------------------------------------------------
def jinja_env():
    """The same Jinja2 configuration tools/render.py must use.

    Note what is absent: line_statement_prefix. The template's own comments are
    `%%`-prefixed LaTeX comments, and setting `%%` as a line-statement prefix
    would turn every one of them into a Jinja statement.
    """
    import jinja2

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        undefined=jinja2.StrictUndefined,
    )


SYNTHETIC_PROFILE = {
    "name": "Ada Lovelace",
    "location": "Bengaluru, India",
    "phone": "+91 98765 43210",
    "email": "ada.lovelace@example.com",
    "linkedin": "linkedin.com/in/adalovelace",
    "github": "github.com/adalovelace",
    "education": [
        {
            "institution": "Indian Institute of Technology Bombay",
            "location": "Mumbai, India",
            "degree": "B.Tech., Computer Science and Engineering",
            "dates": "Aug 2013 -- May 2017",
        }
    ],
}


def with_link_targets(profile: dict) -> dict:
    """The profile with the raw `<field>_url` \\href targets render.py adds.

    The synthetic values hold nothing LaTeX escapes, so the raw target is the value.
    """
    return dict(
        profile, **{f"{key}_url": profile[key] for key in ("email", "linkedin", "github")}
    )


def synthetic_profile(education_rows: int) -> dict:
    """SYNTHETIC_PROFILE with the Education block widened to `education_rows` rows.

    The rows are distinguished only by institution name, because the row's cost is
    a function of the macro rather than of what it says.
    """
    return dict(
        SYNTHETIC_PROFILE,
        education=[
            dict(SYNTHETIC_PROFILE["education"][0], institution=f"Institution {i}")
            for i in range(education_rows)
        ],
    )


def entry(type_: str, n: int, bullets: list[str], lead: str | None = None) -> dict:
    """One Entry block. `type_` is the Entry `type` — "job" or "project".

    Callers pass Bullets as plain strings, which is what a measurement is about.
    The `slug` and the per-Bullet `ref` are supplied here because the template
    requires them: they reach nothing but the Overflow check's marker comments,
    which are inert (docs/adr/0018-overflow-check.md). Synthesising them keeps
    every call site about heights and widths rather than about identity.

    `lead` always rides along as a key, `None` by default — the template's
    `entry.lead` guard is read under StrictUndefined, so an entry dict with no key
    at all would fail rather than skip the lead (docs/adr/0032-the-entry-arc.md).
    """
    slug = f"synthetic-{type_}-{n}"
    return {
        "slug": slug,
        "type": type_,
        "title": f"Senior Software Engineer {n}",
        "org": f"Synthetic Org {n}",
        "location": "Bengaluru, India",
        "dates": "Jan 2020 -- Dec 2023",
        # A project's one-row header carries these; a realistic length, since the row
        # must not wrap (docs/adr/0057-the-page-reads-like-a-resume.md §3).
        "stack": "Python, PostgreSQL, Docker" if type_ == "project" else "",
        "link": f"github.com/adalovelace/project-{n}" if type_ == "project" else "",
        "link_url": f"github.com/adalovelace/project-{n}" if type_ == "project" else "",
        "lead": lead,
        "bullets": [
            {"ref": f"{slug}/c{i}", "text": text} for i, text in enumerate(bullets, start=1)
        ],
    }


def row(label: str, skills: list[str]) -> dict:
    """One Skills category row, escaped the way render.py will escape it."""
    return {"label": escape_latex(label), "text": escape_latex(", ".join(skills))}


def render(
    entries, skill_rows, profile=None, summary=None, supporting=None, education_first=False
) -> str:
    """Fill the committed template — what every measurement here is taken against."""
    source = (TEMPLATE_DIR / TEMPLATE_NAME).read_text(encoding="utf-8")
    return render_source(
        source, entries, skill_rows, profile, summary, supporting, education_first
    )


def render_source(
    source,
    entries,
    skill_rows,
    profile=None,
    summary=None,
    supporting=None,
    education_first=False,
) -> str:
    """Fill a template supplied as *text*. The one place the Jinja env is driven.

    It takes text rather than a name for the one measurement that needs a template
    other than the committed one: the Header-fit instrumentation claims to move
    nothing on the page, and the only way to show that is to build the same résumé
    from the template with the instrumentation cut out and compare the two. The
    file on disk is still never edited.

    The Summary defaults to a real two-line one rather than to nothing, because it
    is not an optional element: the page always carries one and the budget always
    charges for it (docs/adr/0044-the-page-opens-on-a-summary.md §5). A capacity
    sweep run against a page with no Summary on it would measure a page that never
    ships.
    """
    return jinja_env().from_string(source).render(
        profile=with_link_targets(profile if profile is not None else SYNTHETIC_PROFILE),
        # Education at the bottom by default, where the synthetic profile's 2017
        # degree puts it and where the tail measurements below expect to find it. The
        # capacity sweep measures both placements (EDUCATION_PLACEMENTS).
        education_first=education_first,
        entries=entries,
        skill_rows=skill_rows,
        summary=escape_latex(SUMMARY_SAMPLES[0]) if summary is None else summary,
        # Empty by default, because that is the page that ships on nearly every run:
        # a supporting section is on the page only when the posting called for it or
        # the width pass left room
        # (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md).
        supporting_sections=supporting or [],
    )


#: The Summary section in the committed template — its heading AND its call site,
#: cut out together to measure what having it costs. The probe's second use of a
#: template other than the one on disk, for the same reason as the first: the only way
#: to price an element is to build the same résumé without it. The file on disk is
#: never edited, and a source this does not find EXACTLY ONCE fails loudly rather than
#: silently measuring nothing.
#:
#: THE TWO LINES GO TOGETHER AND THAT IS A MEASUREMENT DECISION, not tidiness.
#: `\section` contributes its space through `\addvspace`, which MERGES with the skip
#: already on the vertical list rather than adding to it, so the heading and the
#: paragraph under it share glue. Cutting only the paragraph leaves `\section{Summary}`
#: welded to `\section{Experience}`, where the two headings' skips merge into one and
#: the differential reads 38.00pt for a block that is nowhere near that. Cutting only
#: the heading moves the paragraph onto the header's own glue instead. Neither half is
#: separately priceable, so the pair is priced against `SECTION_LINES + SUMMARY_LINES`
#: (docs/adr/0044-the-page-opens-on-a-summary.md, Addendum).
SUMMARY_BLOCK = (
    "\\section{Summary}\n"
    "%% AUTOAPPLY:element:summary:page\n"
    "\\resumeSummary{\\summaryLine}\n"
)


def without_summary(source: str) -> str:
    """The committed template with the Summary section — heading and prose — removed."""
    if source.count(SUMMARY_BLOCK) != 1:
        raise SystemExit(
            f"expected exactly one `{SUMMARY_BLOCK.strip()}` in {TEMPLATE_NAME}, found "
            f"{source.count(SUMMARY_BLOCK)} — the Summary's cost cannot be measured"
        )
    return source.replace(SUMMARY_BLOCK, "")


def compile_tex(tex: str, stem: str) -> tuple[int, str]:
    """Compile and return (page count, pdflatex log).

    Writes into OUT_DIR. tests/conftest.py monkeypatches that to tmp_path, so tests
    cannot inherit a stale .aux from each other or from a hand-run of the probe — a
    build over an existing .aux is not the same build as a fresh one, which is
    exactly what the byte-identical-PDF check is sensitive to.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tex_path = OUT_DIR / f"{stem}.tex"
    tex_path.write_text(tex, encoding="utf-8")
    proc = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-output-directory={OUT_DIR}",
            str(tex_path),
        ],
        capture_output=True,
        text=True,
        env={
            "SOURCE_DATE_EPOCH": "0",
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(Path.home()),
        },
    )
    log = (OUT_DIR / f"{stem}.log").read_text(encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-4000:] + "\n")
        raise SystemExit(f"pdflatex failed on {tex_path}; see {OUT_DIR / (stem + '.log')}")
    m = re.search(r"Output written on .*?\((\d+) pages?", log)
    if not m:
        raise SystemExit(f"could not read a page count out of {stem}.log")
    return int(m.group(1)), log


# --------------------------------------------------------------------------
# Markers
# --------------------------------------------------------------------------
#: The same set tools/render.py escapes, applied the same way — in ONE pass, so a
#: rule never chews on the escape another rule just wrote (see escape_latex there).
_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_ESCAPABLE = re.compile("|".join(re.escape(character) for character in _LATEX_ESCAPES))


def escape_latex(text: str) -> str:
    """Escape a plain-prose Bullet the way render.py will.

    The probe needs this because a realistic Bullet says "40%", and an unescaped
    `%` comments out the rest of the line. It measures the width of the escaped
    form while counting the characters of the plain form — which is exactly what
    the length lint does, since Opus writes plain prose and never sees the escaping.

    It stays a copy rather than an import: the calibration isolates the template, so
    a bug in render.py must not be able to move a constant.
    """
    return _ESCAPABLE.sub(lambda match: _LATEX_ESCAPES[match.group()], text)


def marker(name: str, text: str = "") -> str:
    r"""A Bullet that reports \pagetotal — the page height consumed so far.

    The trailing text makes the Bullet an ordinary one-line Bullet, so the marker
    measures a real line rather than an empty one.
    """
    body = text or f"Synthetic bullet {name} standing in for one line of real prose"
    return rf"\typeout{{AUTOAPPLY:{name}:\the\pagetotal}}{body}"


def read_markers(log: str) -> dict[str, float]:
    """Marker name -> points. \\the\\pagetotal prints like `123.45678pt`.

    FIRST reading wins, and that is not a tie-break — it is the whole reason a
    marker can ride inside the Summary. The Template expands `\\summaryLine` twice:
    once where the block typesets, and once at the end of the document inside the
    Summary-fit \\parbox, which is measured and never shipped. A probe in that text
    therefore fires twice, and the second firing reports \\pagetotal at the bottom of
    a finished page. Taking the last would put the whole page's height on whatever
    the marker was measuring.
    """
    out: dict[str, float] = {}
    for name, value in re.findall(r"AUTOAPPLY:([A-Za-z0-9_]+):([0-9.]+)pt", log):
        out.setdefault(name, float(value))
    return out


def read_dimen(log: str, name: str) -> float:
    m = re.search(rf"AUTOAPPLYDIM:{name}:([0-9.]+)pt", log)
    if not m:
        raise SystemExit(f"marker {name} did not appear in the log")
    return float(m.group(1))


# --------------------------------------------------------------------------
# The measurements
# --------------------------------------------------------------------------
#: Skills category rows, as label and skills. Real categories over real skills: a
#: measurement taken on `Row 1, Row 2` would measure the wrong string lengths, and
#: the widths are what decide whether a row wraps.
ROW_SAMPLES = [
    ("AI & GenAI", ["Prompt engineering", "Custom GPT configuration",
                    "Google Gemini API", "Claude Code"]),
    ("Data & Analytics", ["Google BigQuery", "PostgreSQL", "Excel", "Model evaluation"]),
    ("Languages", ["Python", "TypeScript"]),
    ("Delivery & Testing", ["Cross-team coordination", "User acceptance testing"]),
    ("Infrastructure", ["Docker", "GitHub Actions"]),
    ("Practices", ["Code review", "Pair programming"]),
    ("Reporting", ["Looker Studio", "Tableau"]),
]

#: A Bullet long enough to typeset on two lines, and short enough not to reach a
#: third. The ladder behind it: 150 characters measures 24.06pt and 200 measures
#: 26.00pt for the SAME two lines — the difference is only how deep the last line's
#: descenders run — so the longer one is the worst case, and the worst case is what a
#: budget charging two lines has to hold against
#: (docs/adr/0025-bullet-wrap-cost.md §5).
WRAPPED_BULLET_SAMPLE = (
    "Went unasked to the other product teams to prove the translation pipeline "
    "generalised past the one product it was built against, then fixed the PDF "
    "layout failures their own manuals turned up in testing"
)

#: Realistic labels for the BOLD character rate. The widest wins, for the reason
#: WIDTH_SAMPLES records for plain prose: the count has to hold for whichever label
#: the run writes, and a label is charged separately because bold is wider than
#: regular (docs/adr/0020-skills-section.md §6).
LABEL_SAMPLES = [
    "AI & GenAI",
    "Data & Analytics",
    "Delivery & Testing",
    "Cloud & Infrastructure",
    "Machine Learning Platform",
    "Languages",
]

#: Skills long enough to wrap a row onto a second line, and the count it takes to
#: reach a third. A row is capped at two typeset lines on the page; the third rung
#: exists so the wrap increment can be confirmed rather than assumed.
WRAPPING_SKILLS = [
    "Amazon Web Services", "Kubernetes", "Terraform", "Docker", "GitHub Actions",
    "Datadog", "PagerDuty", "HashiCorp Vault", "Prometheus", "Grafana",
    "Apache Airflow", "Snowflake", "Elasticsearch", "RabbitMQ", "Consul",
]
OVERLONG_SKILLS = WRAPPING_SKILLS + [
    "Apache Kafka", "Redis", "MongoDB", "Jenkins", "ArgoCD", "Istio",
    "OpenTelemetry", "Packer", "Ansible", "CloudFormation",
]


#: Realistic supporting rows — a built label (the entry's title, bold) and the text
#: after it (its org, its dates, and a composed tail). Long enough to be honest about
#: what a real credential line looks like, and short enough to stay on ONE typeset
#: line, which is what a supporting row is charged and what render.py enforces
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §6).
SUPPORTING_SAMPLES = [
    ("AWS Certified Solutions Architect", "--- Amazon Web Services, Mar 2025"),
    ("Google Cloud Professional Data Engineer", "--- Google Cloud, Aug 2024"),
    ("Placement Coordinator", "--- Training \\& Placement Cell, Aug 2024 -- May 2025"),
    ("Secretary, Robotics Society", "--- Halden Institute, Jul 2023 -- Jun 2024"),
    ("Deep Learning Specialization", "--- DeepLearning.AI, Feb 2024"),
]


def supporting_for(count: int) -> list[dict]:
    """One supporting section of `count` rows, in the Template's own context shape."""
    if count > len(SUPPORTING_SAMPLES):
        raise SystemExit(f"only {len(SUPPORTING_SAMPLES)} supporting samples exist")
    if not count:
        return []
    return [
        {
            "name": "certifications",
            "heading": "Certifications",
            "rows": [
                {"slug": f"sample-{index}", "label": label, "text": text}
                for index, (label, text) in enumerate(SUPPORTING_SAMPLES[:count], 1)
            ],
        }
    ]


def rows_for(count: int) -> list[dict]:
    """The first `count` sample rows, none of which wraps."""
    if count > len(ROW_SAMPLES):
        raise SystemExit(f"only {len(ROW_SAMPLES)} sample rows exist; asked for {count}")
    return [row(label, skills) for label, skills in ROW_SAMPLES[:count]]


def skills_sample() -> list[dict]:
    """The composition every measurement that is not *about* the Skills section uses."""
    return rows_for(4)


@dataclass
class Heights:
    """Every element's typeset height, in points."""

    bullet: float
    entry_header: float
    project_header: float
    section: float
    profile_header: float
    summary: float
    education_row: float
    skills_row: float
    skills_row_wrap: float
    text_height: float
    bullet_line_width: float
    skills_row_width: float
    summary_width: float


def measure_heights(skills_row: float, skills_row_wrap: float) -> Heights:
    r"""One compile, laid out so every constant falls out of \pagetotal deltas.

    The two Skills-row costs are passed in rather than measured here: they take a
    dozen compiles of their own (`measure_skills_row`), and the report wants the
    ladder behind them as well as the numbers.

    The skeleton is two jobs then one project, so the log contains a marker
    before and after each element whose height we need:

        [profile header] [Experience section] [job1 header] j1b1..j1b4
                                              [job2 header] j2b1 j2b2
        [Projects section]                    [proj1 header] p1b1 p1b2
        [Skills section]                      sk1
        [Education section]                   (rows, measured separately)
    """
    dim_probe = (
        r"\typeout{AUTOAPPLYDIM:textheight:\the\textheight}"
        r"\typeout{AUTOAPPLYDIM:bulletwidth:\the\linewidth}"
    )
    entries = [
        entry("job", 1, [
            marker("j1b1") + dim_probe,
            marker("j1b2"),
            marker("j1b3"),
            marker("j1b4"),
            marker("j1b5"),
        ]),
        entry("job", 2, [marker("j2b1"), marker("j2b2")]),
        entry("project", 1, [marker("p1b1"), marker("p1b2")]),
        entry("project", 2, [marker("p2b1")]),
    ]
    skills = skills_sample()
    skills[0] = dict(
        skills[0],
        text=r"\typeout{AUTOAPPLYDIM:skillswidth:\the\linewidth}" + skills[0]["text"],
    )
    summary = (
        r"\typeout{AUTOAPPLYDIM:summarywidth:\the\linewidth}"
        + escape_latex(SUMMARY_SAMPLES[0])
    )
    pages, log = compile_tex(render(entries, skills, summary=summary), "heights")
    if pages != 1:
        raise SystemExit(
            f"the height probe itself spilled to {pages} pages — shrink it before trusting anything"
        )
    m = read_markers(log)

    # One Bullet's height, from the interior gaps of one entry. The FIRST gap is
    # excluded on purpose: \pagetotal is read as the item's line is contributed,
    # and the itemize's top glue lands between the first and second readings, so
    # gap 1 is reliably larger than the rest. That glue is a per-Entry cost and
    # is picked up below, inside entry_header.
    interior = [
        m["j1b3"] - m["j1b2"],
        m["j1b4"] - m["j1b3"],
        m["j1b5"] - m["j1b4"],
    ]
    spread = max(interior) - min(interior)
    if spread > 0.5:
        raise SystemExit(f"Bullet heights are not uniform ({interior}); the model does not hold")
    bullet = sum(interior) / len(interior)
    first_gap_excess = (m["j1b2"] - m["j1b1"]) - bullet

    # Crossing from the last Bullet of job1 to the first of job2 costs: the rest
    # of that Bullet's own line, plus job2's \resumeSubheading and the itemize
    # open/close glue around it. All of that is charged per Entry, so it belongs
    # in ENTRY_HEADER_LINES.
    entry_header = (m["j2b1"] - m["j1b5"]) - bullet

    # A project's header is its own one-row macro (docs/adr/0057 §3), measured the
    # same way across the boundary between the two projects.
    project_header = (m["p2b1"] - m["p1b2"]) - bullet

    # Crossing from job2's last Bullet into the Projects section costs one
    # Bullet line, one \section, and one PROJECT header.
    section = (m["p1b1"] - m["j2b2"]) - bullet - project_header

    # Everything above the first Bullet, less the Experience \section and job1's
    # own Entry header. The first reading lags by the itemize top glue that
    # entry_header already charges for, so add it back rather than double-counting
    # it against what is above. On a page with a Summary this is the header AND the
    # Summary — the two are stacked with nothing between them to put a marker in.
    header_plus_summary = m["j1b1"] - section - entry_header + first_gap_excess

    # So the two are separated the way measure_lead_row and measure_education_row
    # separate theirs: a second document differing by nothing but the element.
    #
    # A \pagetotal reading taken inside the Summary's own text would be cheaper and
    # WRONG. It lands 9.87pt above where the block's own material begins — the glue
    # \end{center} contributes when the next paragraph starts — and the whole of
    # that would be charged to HEADER_LINES, a constant this element has no business
    # moving. The differential attributes shared glue to neither.
    #
    # What comes out is the SECTION: the \section{Summary} heading and the paragraph
    # under it, priced as one, because \addvspace merges the glue between them and
    # neither half is separately priceable — see SUMMARY_BLOCK.
    without = compile_tex(
        render_source(
            without_summary((TEMPLATE_DIR / TEMPLATE_NAME).read_text(encoding="utf-8")),
            entries,
            skills,
        ),
        "heights_nosummary",
    )[1]
    no_summary = read_markers(without)
    profile_header = no_summary["j1b1"] - section - entry_header + first_gap_excess

    # The whole element: the \section{Summary} heading, two typeset lines of \small
    # prose and the \vspace under them, which is the quantity SECTION_LINES +
    # SUMMARY_LINES has to cover (docs/adr/0044-the-page-opens-on-a-summary.md §6 and
    # its Addendum).
    summary_height = header_plus_summary - profile_header

    # Both of these sit at the bottom of the page with nothing after them to put a
    # marker in, and \pagetotal is unreliable there — the final page has not been
    # shipped out when the marker fires, and the trailing glue has not been
    # discarded yet. They are measured as a whole-page differential instead: two
    # documents that differ only by the element in question, each read just before
    # \end{document}. The Education row's own whole-line cost is re-derived by
    # overflow in measure_tail_costs(); the Skills rows' points are the measurement
    # the budget spends, since a row is never charged alone.
    education_row = measure_education_row()

    return Heights(
        bullet=bullet,
        entry_header=entry_header,
        project_header=project_header,
        section=section,
        profile_header=profile_header,
        summary=summary_height,
        education_row=education_row,
        skills_row=skills_row,
        skills_row_wrap=skills_row_wrap,
        text_height=read_dimen(log, "textheight"),
        bullet_line_width=read_dimen(log, "bulletwidth"),
        skills_row_width=read_dimen(log, "skillswidth"),
        summary_width=read_dimen(log, "summarywidth"),
    )


def tail_position(
    education_rows: int,
    skill_rows: list[dict],
    stem: str,
    supporting: list[dict] | None = None,
) -> float:
    r"""Total page height consumed by a whole document, in points.

    The Skills rows and the Education rows are the elements with no Bullet after
    them, so neither can be measured by a delta between two markers inside the
    page. Instead the whole page is measured from the bottom: a marker is appended
    just before \end{document}, and the element's cost is the difference between
    two documents that differ only by that element.

    Appending one line to the *rendered* .tex is not the forbidden splicing —
    nothing is parsed, and this is a dev probe rather than a run.
    """
    profile = synthetic_profile(education_rows)
    entries = [entry("job", 1, [marker("only")])]
    tex = render(entries, skill_rows, profile=profile, supporting=supporting)
    tex = tex.replace(
        r"\end{document}",
        r"\typeout{AUTOAPPLY:tail:\the\pagetotal}" + "\n" + r"\end{document}",
    )
    _, log = compile_tex(tex, stem)
    return read_markers(log)["tail"]


def measure_education_row() -> float:
    r"""One Education row: two rows minus one row, so no heading or glue is in it."""
    sample = skills_sample()
    return tail_position(2, sample, "edu2") - tail_position(1, sample, "edu1")


def measure_supporting_row() -> float:
    r"""The marginal cost of one supporting row, in points — measured, not assumed.

    THE ONE THING THE CALIBRATION OWES THE SUPPORTING SECTIONS. `config.py` gains no
    constant for them because a supporting row IS a Skills row — the same
    `\resumeItem` with a bold label, in the same list geometry — so `SKILLS_ROW_PT`
    charges both call sites. That is a claim about the template, and this is what
    holds it: measured the same way `measure_skills_row` measures its own, documents
    at 0 through 5 rows, differenced, the first difference dropped because it carries
    the `\section` heading (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §6).

    If the two ever part company, the fix is to tighten a macro rather than to split
    the constant — the same instruction `ENTRY_HEADER_LINES` carries for its own two
    macros, and for the same reason: a second name for one element lets the two drift
    apart silently.
    """
    rows = rows_for(2)
    positions = [
        tail_position(1, rows, f"support{count}", supporting_for(count))
        for count in range(0, 6)
    ]
    marginals = [positions[i] - positions[i - 1] for i in range(2, 6)]
    return sum(marginals) / len(marginals)


def measure_skills_row() -> tuple[float, float, list[float], list[tuple[int, int, float]]]:
    r"""(first typeset line pt, each line after, the per-row marginals, the ladder).

    Two measurements, because a row's height stopped being a fact about the macro
    the moment a row was allowed to wrap (docs/adr/0021-skills-row-cost.md):

    **The row.** Documents at 0 through 6 rows, differenced. The first difference
    carries the `\section` heading and is excluded; the rest are the marginal cost
    of one more row, and their uniformity is what makes `N x <one number>` true in
    points.

    **The wrap.** One-row documents at rising character counts, differenced against
    the one-line rung so the heading cancels. The increment is the SMALLEST positive
    step, and the other rungs must then be whole multiples of it — which is how the
    line count of each rung is read off the measurement rather than assumed from the
    character formula the measurement exists to check.
    """
    positions = [
        tail_position(1, rows_for(count), f"rows{count}") for count in range(0, 7)
    ]
    marginals = [positions[i] - positions[i - 1] for i in range(2, 7)]
    first_line = sum(marginals) / len(marginals)

    ladder_skills = [
        ["Python", "TypeScript"],
        WRAPPING_SKILLS[:8],
        WRAPPING_SKILLS,
        OVERLONG_SKILLS,
    ]
    base = None
    points = []
    for index, skills in enumerate(ladder_skills):
        at = tail_position(1, [row("Cloud & Infrastructure", skills)], f"wrap{index}")
        if base is None:
            base = at
        points.append(first_line + (at - base))

    steps = [value - first_line for value in points if value - first_line > 0.5]
    wrap_line = min(steps) if steps else first_line
    ladder = [
        (len(", ".join(skills)), round(1 + (value - first_line) / wrap_line), value)
        for skills, value in zip(ladder_skills, points)
    ]
    return first_line, wrap_line, marginals, ladder


def measure_wrapped_bullet(stem: str = "wrapped") -> tuple[float, float]:
    r"""(a one-line Bullet, a two-line Bullet) in points, from interior gaps.

    The same \pagetotal method `measure_heights` uses, and it excludes the first gap
    for the same reason: the itemize's top glue lands between the first two readings.
    So the entry carries four Bullets and the two measured gaps are both interior.

    This measures a fact that earns NO CONSTANT. A Bullet's second typeset line is
    12.00pt — the same number as `SKILLS_ROW_WRAP_PT`, and for the same reason, since
    `\resumeItem`'s `\vspace{-2pt}` is charged once per item rather than once per
    line. Nothing would ever spend a `BULLET_WRAP_PT`, because the Packer charges the
    integer 2; what protects the page is the check below, which is what would catch a
    font or margin change pushing that second line past 14.00pt and turning the
    charge of 2 into an over-promise (docs/adr/0025-bullet-wrap-cost.md §5).
    """
    entries = [
        entry("job", 1, [
            marker("wb1"),
            marker("wb2"),
            marker("wb3", escape_latex(WRAPPED_BULLET_SAMPLE)),
            marker("wb4"),
        ])
    ]
    pages, log = compile_tex(render(entries, skills_sample()), stem)
    if pages != 1:
        raise SystemExit(f"the wrapped-Bullet probe spilled to {pages} pages")
    m = read_markers(log)
    return m["wb3"] - m["wb2"], m["wb4"] - m["wb3"]


def measure_widths(strings: list[str], stem: str = "widths") -> tuple[float, list[float]]:
    r"""(Bullet line width, typeset width of each string) in points.

    \sbox measures a string's natural unbroken width at the template's font and
    size, inside the real Bullet environment. A string whose width exceeds the line
    width is one that wraps.
    """
    probe_bullets = [
        rf"\sbox0{{{escape_latex(s)}}}\typeout{{AUTOAPPLYDIM:w{i}:\the\wd0}}sample {i}"
        for i, s in enumerate(strings)
    ]
    probe_bullets[0] += r"\typeout{AUTOAPPLYDIM:linewidth:\the\linewidth}"
    _, log = compile_tex(render([entry("job", 1, probe_bullets)], skills_sample()), stem)
    return (
        read_dimen(log, "linewidth"),
        [read_dimen(log, f"w{i}") for i in range(len(strings))],
    )


def measure_bold_widths(stem: str = "boldwidths") -> list[tuple[str, float]]:
    r"""(label, points per bold character) for every realistic label.

    A Skills row is `\textbf{<label>:} <skills>`, and bold is wider than regular, so
    charging the label at CHARS_PER_BULLET's rate would over-promise — the one
    direction tools/config.py forbids. `\sbox` around the bold run, inside the real
    Bullet environment, is the same method the plain rate uses.

    The colon is inside the bold run and the space after it is not, which is why the
    divisor is `len(label) + 1` here while the fit formula charges `len(label) + 2`:
    the formula pays for the space too, at the bold rate, which is the safe rounding.
    """
    probes = [
        rf"\sbox0{{\textbf{{{escape_latex(label)}:}}}}"
        rf"\typeout{{AUTOAPPLYDIM:L{i}:\the\wd0}}sample {i}"
        for i, label in enumerate(LABEL_SAMPLES)
    ]
    _, log = compile_tex(
        render([entry("job", 1, probes)], skills_sample()), stem
    )
    return [
        (label, read_dimen(log, f"L{i}") / (len(label) + 1))
        for i, label in enumerate(LABEL_SAMPLES)
    ]


#: The Template's Header-fit instrumentation, as it reaches the log — one value
#: per line, because pdfTeX wraps the .log at 79 columns.
HEADER_FIT = re.compile(r"AUTOAPPLY:headerfit:([a-z]+):([a-z]+):([0-9.]+)pt")


def header_profile(**overrides) -> dict:
    """SYNTHETIC_PROFILE with header fields replaced, Education left alone."""
    return dict(SYNTHETIC_PROFILE, **overrides)


def measure_header_fit(profile: dict, stem: str = "headerfit") -> dict[str, dict[str, float]]:
    r"""What the Template measured for one profile's two header lines.

    Four numbers each: `flat`, the line's height as an unbreakable \hbox; `broken`,
    its height after TeX line-breaks it inside the real \linewidth; the line's
    natural `width`; and the `avail`able width. `broken` above `flat` is TeX itself
    saying the line wrapped — the reading tools/render.py's Header-fit check acts on
    (docs/adr/0017-header-fit-check.md).

    Unlike everything else here this measures the Static profile rather than a
    template constant, which is the point: HEADER_LINES charges a one-line name over
    a one-line contact line, and this is what says whether that holds.
    """
    entries = [entry("job", 1, [marker("hf")])]
    _, log = compile_tex(render(entries, skills_sample(), profile=profile), stem)
    found: dict[str, dict[str, float]] = {}
    for line, what, value in HEADER_FIT.findall(log):
        found.setdefault(line, {})[what] = float(value)
    if not found:
        raise SystemExit(f"no Header-fit measurements in {stem}.log")
    return found


def measure_chars_per_bullet(bullet_line_width: float) -> tuple[int, list[tuple[str, float]]]:
    r"""How many characters of prose fit on one Bullet line.

    The answer is the most pessimistic sample, because the length lint is a
    character count and it has to hold for whichever Bullet Opus actually writes.
    """
    _, widths = measure_widths(WIDTH_SAMPLES, "chars_per_bullet")
    per_sample = [
        (sample, width / len(sample)) for sample, width in zip(WIDTH_SAMPLES, widths)
    ]
    worst_pt_per_char = max(w for _, w in per_sample)
    return math.floor(bullet_line_width / worst_pt_per_char), per_sample


def measure_lead_widths(stem: str = "leadwidths") -> tuple[float, list[float]]:
    r"""(the lead's own \linewidth, each LEAD_SAMPLES sentence's typeset width).

    Same \sbox technique as measure_widths, run inside \resumeEntryLead's own
    \item rather than inside a Bullet's \resumeItem: the lead sits one list level
    shallower than a Bullet (docs/adr/0032-the-entry-arc.md §4), so its \linewidth
    is wider and CHARS_PER_BULLET must not be reused for it. All six probes ride in
    one lead string — sequential \sbox/\typeout pairs reusing box register 0, each
    captured before the next overwrites it.
    """
    probes = "".join(
        rf"\sbox0{{{escape_latex(s)}}}\typeout{{AUTOAPPLYDIM:ld{i}:\the\wd0}}"
        for i, s in enumerate(LEAD_SAMPLES)
    )
    probes += r"\typeout{AUTOAPPLYDIM:leadwidth:\the\linewidth}"
    entries = [entry("job", 1, [marker("after")], lead=probes)]
    _, log = compile_tex(render(entries, skills_sample()), stem)
    return (
        read_dimen(log, "leadwidth"),
        [read_dimen(log, f"ld{i}") for i in range(len(LEAD_SAMPLES))],
    )


def measure_lead_chars() -> tuple[int, float, list[tuple[str, float]]]:
    r"""(LEAD_CHARS, the lead's own \linewidth, per-sample pt/char).

    Worst sample wins, exactly as measure_chars_per_bullet: the lint is a
    character count and has to hold for whichever lead sentence is composed.
    """
    lead_width, widths = measure_lead_widths()
    per_sample = [(sample, width / len(sample)) for sample, width in zip(LEAD_SAMPLES, widths)]
    worst_pt_per_char = max(w for _, w in per_sample)
    return math.floor(lead_width / worst_pt_per_char), lead_width, per_sample


def measure_lead_bold_widths(stem: str = "leadboldwidths") -> tuple[float, list[float]]:
    r"""(the lead's own \linewidth, each LEAD_BOLD_SAMPLES span's BOLD typeset width).

    `measure_lead_widths` with `\textbf` around the box, which is the whole of the
    difference: same `\sbox`, same `\resumeEntryLead` item, same `\small`, same
    `\linewidth`. Measuring the two families in the same place is the point — the
    charge this feeds is a ratio of two counts taken at ONE width, so anything that
    moved between them would move the ratio for a reason that is not the font.

    This is `measure_bold_widths`'s method one element over. That one boxes
    `\textbf{<label>:}` because a Skills row's bold run IS the label and its colon;
    this one boxes the span bare, because a lead's bold run is a figure or a term
    with no punctuation welded to it.
    """
    probes = "".join(
        rf"\sbox0{{\textbf{{{escape_latex(s)}}}}}\typeout{{AUTOAPPLYDIM:lb{i}:\the\wd0}}"
        for i, s in enumerate(LEAD_BOLD_SAMPLES)
    )
    probes += r"\typeout{AUTOAPPLYDIM:leadwidth:\the\linewidth}"
    entries = [entry("job", 1, [marker("after")], lead=probes)]
    _, log = compile_tex(render(entries, skills_sample()), stem)
    return (
        read_dimen(log, "leadwidth"),
        [read_dimen(log, f"lb{i}") for i in range(len(LEAD_BOLD_SAMPLES))],
    )


def measure_bold_lead_chars() -> tuple[int, float, list[tuple[str, float]]]:
    r"""(BOLD_LEAD_CHARS, the lead's own \linewidth, per-sample pt/char).

    LEAD_CHARS's bold twin, and the reason it exists rather than the lead borrowing
    the Bullet's `BOLD_PENALTY`: `0046` §6 established that the bold penalty is a
    property of the FONT and not of the column, and that claim let the Summary be
    charged with no constant of its own. It is still true here — the per-string
    bold/plain ratio measures ~1.15 at this width as it does at a Bullet's — but
    `0046`'s own *Rejected* section promised that if the lead were reopened it would
    be reopened **as a calibration**, with this count measured off a compiled page
    rather than derived. This is that measurement, and it is a third width at which
    the width-independence claim can be checked instead of assumed.

    Worst sample wins, exactly as measure_lead_chars: the lint is a character count
    and has to hold for whichever span the composer's prose hands the renderer.
    """
    lead_width, widths = measure_lead_bold_widths()
    per_sample = [
        (sample, width / len(sample))
        for sample, width in zip(LEAD_BOLD_SAMPLES, widths)
    ]
    worst_pt_per_char = max(w for _, w in per_sample)
    return math.floor(lead_width / worst_pt_per_char), lead_width, per_sample


def measure_lead_at_budget(
    lead_chars: int, bold_lead_chars: int, stem: str = "leadatbudget"
) -> list[tuple[str, int, float]]:
    r"""Each sample composed to the tape's last word, with a bold span, and measured.

    (text, plain characters, typeset width) per sample. This is the check the RATIO
    cannot make: a bold charge in the safe direction, spent against a budget that was
    too generous to begin with, still puts a lead on a second line — and `LEAD_LINES`
    charges one.

    So it builds the worst legal lead rather than reasoning about one. Every
    word-prefix of every LEAD_SAMPLES sentence is paired with the WIDEST span in
    LEAD_BOLD_SAMPLES, charged the way `check_lead_lengths` will charge it, and the
    longest that stays inside `LEAD_CHARS` is kept. Word boundaries for the reason
    `word_prefixes` gives: a prefix cut mid-word measures a line TeX would never set.

    The width is the `\sbox` NATURAL width, with none of the interword shrink TeX
    would spend before breaking — the same conservative reading every other width
    here is taken at, and the reason a real 114-character lead can measure 521pt and
    still set on one line.
    """
    penalty = lead_chars / bold_lead_chars
    span = max(LEAD_BOLD_SAMPLES, key=lambda s: len(s))
    charged_span = len(span) * penalty

    built: list[str] = []
    for sample in LEAD_SAMPLES:
        admitted = [
            prefix
            for prefix in word_prefixes(sample.rstrip("."))
            if len(prefix) + 1 + charged_span <= lead_chars
        ]
        if not admitted:
            raise SystemExit(
                "no prefix of a lead sample survives the bold-aware budget; "
                "BOLD_LEAD_CHARS is measuring the wrong thing"
            )
        built.append(f"{max(admitted, key=len)} {span}")

    probes = "".join(
        rf"\sbox0{{{escape_latex(text[: -len(span)])}"
        rf"\textbf{{{escape_latex(span)}}}}}"
        rf"\typeout{{AUTOAPPLYDIM:ab{i}:\the\wd0}}"
        for i, text in enumerate(built)
    )
    entries = [entry("job", 1, [marker("after")], lead=probes)]
    _, log = compile_tex(render(entries, skills_sample()), stem)
    return [
        (text, len(text), read_dimen(log, f"ab{i}")) for i, text in enumerate(built)
    ]


def lead_tail_position(lead: str | None, stem: str) -> float:
    """One document's tail \\pagetotal, an Entry with one Bullet and an optional lead."""
    entries = [entry("job", 1, [marker("only")], lead=lead)]
    tex = render(entries, skills_sample())
    tex = tex.replace(
        r"\end{document}",
        r"\typeout{AUTOAPPLY:tail:\the\pagetotal}" + "\n" + r"\end{document}",
    )
    _, log = compile_tex(tex, stem)
    return read_markers(log)["tail"]


def measure_lead_row() -> float:
    r"""One lead line's own height cost, in points, by whole-page differential.

    Nothing typeset follows the lead that would isolate it with an interior
    \pagetotal gap without also changing the Bullet it sits above — the lead's
    own \vspace interacts with the itemize glue the Bullet after it opens, so the
    two documents have to differ by nothing but the lead itself. Same method as
    measure_education_row: two documents, one with a lead and one without, read
    at the tail.
    """
    without = lead_tail_position(None, "lead_without")
    with_lead = lead_tail_position(LEAD_SAMPLES[0], "lead_with")
    return with_lead - without


#: SUMMARY_LINES, restated rather than imported for the same reason MIN_SKILLS_ROWS
#: is: the calibration isolates the template from the running tools. It is fixed by
#: decision rather than measured (docs/adr/0044-the-page-opens-on-a-summary.md §1) —
#: what IS measured is whether the element the decision charges for costs what it is
#: charged, and how many characters fit inside it. The charge is this plus
#: SECTION_LINES since the Addendum put a `\section{Summary}` heading over the prose,
#: and the check is made against the pair because the pair is what is measurable.
SUMMARY_LINES = 2


def measure_summary_widths(stem: str = "summarywidths") -> tuple[float, list[float]]:
    r"""(the Summary's own \linewidth, each SUMMARY_SAMPLES paragraph's flat width).

    Same \sbox technique as measure_widths and measure_lead_widths, run inside
    \resumeSummary's own argument — so the box inherits the \small the macro sets,
    and \linewidth is read where the paragraph actually breaks. The Summary sits at
    TOP LEVEL, outside every itemize, so that width is the widest on the page and
    LEAD_CHARS must not be reused for it.

    Each sample is boxed unbroken, which is the point: the width of the whole
    paragraph as one line, divided by its characters, is the pt/char rate the
    character budget is built from.
    """
    probes = "".join(
        rf"\sbox0{{{escape_latex(s)}}}\typeout{{AUTOAPPLYDIM:sm{i}:\the\wd0}}"
        for i, s in enumerate(SUMMARY_SAMPLES)
    )
    probes += r"\typeout{AUTOAPPLYDIM:summarywidth:\the\linewidth}"
    entries = [entry("job", 1, [marker("after")])]
    _, log = compile_tex(render(entries, skills_sample(), summary=probes), stem)
    return (
        read_dimen(log, "summarywidth"),
        [read_dimen(log, f"sm{i}") for i in range(len(SUMMARY_SAMPLES))],
    )


def word_prefixes(text: str) -> list[str]:
    """Every prefix of `text` that ends on a word boundary, shortest first.

    Word boundaries rather than character offsets because a composed Summary ends
    on a word, and a prefix cut mid-word measures a line TeX would never set.
    """
    words = text.split()
    return [" ".join(words[: n + 1]) for n in range(len(words))]


def measure_summary_chars(ceiling_pt: float, stem: str = "summarychars") -> tuple[int, list[int]]:
    r"""SUMMARY_CHARS, and the longest fitting prefix of each sample.

    THIS ONE IS NOT A RATE, and that is the difference between it and
    CHARS_PER_BULLET, LEAD_CHARS and BOLD_CHARS_PER_BULLET. Those bound a ONE-line
    element, where "how many characters fit" and "how many lines is this" are the
    same question, so a worst-case pt/char and a division answer it.

    A Summary is two lines, and a paragraph breaks at word boundaries. Divide the
    doubled \linewidth by a pt/char rate and the answer is the count that would fit
    if the first line could be filled to the last scaled point — which no line
    break does. That count comes out around a word too generous, and what it buys
    is a composer who meets the tape and is then refused by the compile.

    So this measures the thing itself. Every word-prefix of every sample is boxed in
    a \parbox at the Summary's real \linewidth, in ONE compile, and the answer is
    the longest prefix whose height is inside the ceiling render.py enforces — the
    smallest such length across the samples wins, same worst-case discipline as its
    siblings. The tape and the gate are then measuring one quantity by construction
    (docs/adr/0044-the-page-opens-on-a-summary.md §6).
    """
    probes = []
    keys: list[list[tuple[str, int]]] = []
    for index, sample in enumerate(SUMMARY_SAMPLES):
        keys.append([])
        for position, prefix in enumerate(word_prefixes(sample)):
            name = f"sc{index}w{position}"
            keys[index].append((name, len(prefix)))
            probes.append(
                rf"\sbox0{{\parbox{{\linewidth}}{{\small {escape_latex(prefix)}}}}}"
                rf"\dimen0=\ht0 \advance\dimen0 by \dp0 "
                rf"\typeout{{AUTOAPPLYDIM:{name}:\the\dimen0}}"
            )
    entries = [entry("job", 1, [marker("after")])]
    _, log = compile_tex(render(entries, skills_sample(), summary="".join(probes)), stem)

    longest = []
    for sample_keys in keys:
        fitting = [
            length for name, length in sample_keys if read_dimen(log, name) <= ceiling_pt
        ]
        if not fitting:
            raise SystemExit("no prefix of a Summary sample fits the ceiling; check the macro")
        longest.append(max(fitting))
    return min(longest), longest


#: The Template's Summary-fit measurement, as it reaches the log.
SUMMARY_FIT = re.compile(r"AUTOAPPLY:summaryfit:([a-z]+):([0-9.]+)pt")


def measure_summary_fit(text: str, stem: str) -> float:
    r"""One Summary's \parbox height — the number tools/render.py's gate reads.

    The Template boxes the composed paragraph at the width it typesets at and
    reports the height; render.py fails the run when that exceeds
    `SUMMARY_LINES x BULLET_LINE_PT`. Measured here for both a legal Summary and an
    over-long one, so the report SHOWS the ceiling sitting between them rather than
    claiming it does.
    """
    entries = [entry("job", 1, [marker("after")])]
    _, log = compile_tex(render(entries, skills_sample(), summary=escape_latex(text)), stem)
    found = dict(SUMMARY_FIT.findall(log))
    if "height" not in found:
        raise SystemExit(f"no Summary-fit measurement in {stem}.log")
    return float(found["height"])


# --------------------------------------------------------------------------
# Turning heights into the constants, then checking them
# --------------------------------------------------------------------------
def measure_education_lines() -> int:
    r"""The Education row's cost in whole Bullet lines, by overflow.

    A differential between two page-capacity measurements that differ only by that
    one row, so the answer is already in the integer unit the budget spends and no
    rounding decision is needed. The Skills section has no equivalent here: it is
    charged in points and rounded once at the sum, so a whole-line reading of one
    row would be the wrong quantity.
    """
    base = max_bullets_within_margins(3, 2, 1, skills_sample(), "tail_base")
    two_edu = max_bullets_within_margins(3, 2, 2, skills_sample(), "tail_edu")
    return base - two_edu


@dataclass
class Constants:
    BULLET_LINE_PT: float
    PAGE_LINES: int
    HEADER_LINES: int
    SECTION_LINES: int
    ENTRY_HEADER_LINES: int
    PROJECT_HEADER_LINES: int
    CHARS_PER_BULLET: int
    BOLD_CHARS_PER_BULLET: int
    SKILLS_ROW_PT: float
    SKILLS_ROW_WRAP_PT: float
    SUMMARY_LINES: int
    SUMMARY_CHARS: int


#: The (jobs, projects) shapes PAGE_LINES is calibrated against and verified on.
#: Spread deliberately: a résumé with two jobs and no projects has the least
#: per-Entry rounding slack absorbing the page-level rounding, so it is the shape
#: that catches an over-promising PAGE_LINES. Leaving it out is how you ship a
#: budget that works on your own bank and breaks on a shorter one.
SWEEP_SHAPES = [(2, 0), (2, 1), (3, 1), (3, 2), (4, 3), (5, 2), (6, 1)]


def derive_element_costs(
    h: Heights, chars_per_bullet: int, bold_chars_per_bullet: int, summary_chars: int
) -> Constants:
    """Everything except PAGE_LINES, which needs the sweep.

    Element costs round UP: a cost rounded down would let the budget promise a line
    the page does not have. The two Skills-row costs are the stated exception and
    stay in points — a row is never charged alone, so the rounding happens once, at
    the section's sum (docs/adr/0021-skills-row-cost.md §1).
    """
    return Constants(
        BULLET_LINE_PT=round(h.bullet, 2),
        PAGE_LINES=math.floor(h.text_height / h.bullet),  # provisional; see calibrate_page_lines
        HEADER_LINES=math.ceil(h.profile_header / h.bullet),
        SECTION_LINES=math.ceil(h.section / h.bullet),
        ENTRY_HEADER_LINES=math.ceil(h.entry_header / h.bullet),
        PROJECT_HEADER_LINES=math.ceil(h.project_header / h.bullet),
        CHARS_PER_BULLET=chars_per_bullet,
        BOLD_CHARS_PER_BULLET=bold_chars_per_bullet,
        SKILLS_ROW_PT=round(h.skills_row, 2),
        SKILLS_ROW_WRAP_PT=round(h.skills_row_wrap, 2),
        # Fixed by decision, not derived — like LEAD_LINES. What the probe owes it
        # is the check below that the element actually fits in two Bullet lines.
        SUMMARY_LINES=SUMMARY_LINES,
        SUMMARY_CHARS=summary_chars,
    )


def calibrate_page_lines(c: Constants) -> tuple[int, list[tuple[int, int, int, int]]]:
    r"""Read PAGE_LINES off the compiled page rather than off \textheight.

    floor(\textheight / one Bullet) is the right first guess but it is not the
    answer: the per-element costs are each rounded up, and how much of that
    rounding is available to absorb the page-level rounding depends on how many
    Entries the page holds. So the honest value is the largest PAGE_LINES that
    over-promises on NO shape:

        PAGE_LINES = min over shapes of (measured capacity + that shape's overhead)

    Returns the value and the per-shape rows behind it.
    """
    rows = []
    for jobs, projects in SWEEP_SHAPES:
        education_rows = len(SYNTHETIC_PROFILE["education"])
        actual = max_bullets_within_margins(
            jobs, projects, education_rows, skills_sample(), f"cal_{jobs}_{projects}"
        )
        overhead = c.PAGE_LINES - predict_bullet_capacity(
            c, jobs, projects, education_rows, skills_sample()
        )
        rows.append((jobs, projects, actual, actual + overhead))
    return min(r[3] for r in rows), rows


def build_entries(jobs: int, projects: int, total_bullets: int) -> list[dict]:
    """Spread total_bullets across the entries, round-robin.

    Deliberately NOT capped at 3 Bullets per entry. The constants encode how many
    lines the page holds; the soft cap of ~3 Bullets is the Packer's allocation
    rule, not a fact about layout. Capping here would make it impossible to spend
    a budget larger than 3x the entry count, and the probe would then measure the
    cap instead of the page.
    """
    blocks = [("job", i + 1) for i in range(jobs)] + [
        ("project", i + 1) for i in range(projects)
    ]
    per = [0] * len(blocks)
    for i in range(total_bullets):
        per[i % len(blocks)] += 1
    text = (
        "Rewrote the order-ingest consumer to batch Kafka commits, cutting p99 "
        "checkout latency by a clear margin"
    )
    return [
        entry(type_, n, [text] * count)
        for (type_, n), count in zip(blocks, per)
        if count
    ]


def content_extent(pdf_path: Path) -> tuple[float, float, float]:
    """(page height, topmost baseline, bottommost baseline) in points."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    ys: list[float] = []

    def visit(text, cm, tm, font, size):
        # tm[5] is the baseline's y. Drop blanks, and drop y<=1 — a handful of
        # artefacts land at exactly 0 and are not real content.
        if text.strip() and tm[5] > 1:
            ys.append(tm[5])

    page.extract_text(visitor_text=visit)
    if not ys:
        raise SystemExit(f"no text found in {pdf_path}")
    return float(page.mediabox.height), max(ys), min(ys)


#: Where Education may sit: at the bottom, and at the top of a student's page, where
#: the template adds 4pt under it (docs/adr/0057-the-page-reads-like-a-resume.md §2).
#: Capacity is the SMALLER of the two, so PAGE_LINES holds wherever it lands.
EDUCATION_PLACEMENTS = (False, True)


def max_bullets_within_margins(
    jobs: int, projects: int, education_rows: int, skill_rows: list[dict], stem: str
) -> int:
    """The page's real capacity, at whichever Education placement holds less."""
    return min(
        max_bullets_at(jobs, projects, education_rows, skill_rows, f"{stem}_{int(first)}", first)
        for first in EDUCATION_PLACEMENTS
    )


def max_bullets_at(
    jobs: int,
    projects: int,
    education_rows: int,
    skill_rows: list[dict],
    stem: str,
    education_first: bool,
) -> int:
    r"""The largest total Bullet count that fits WITHOUT the page being squeezed.

    Page count alone is the wrong criterion, and this is the subtlest thing in the
    whole calibration. TeX does not break a page the moment content passes
    \textheight: \raggedbottom makes the page box stretchable, the itemize glue has
    shrink, and there are penalties against breaking inside a list. So pdfTeX will
    happily *compress* the vertical glue and keep going, with no overfull warning.
    Measured on this template, bullets 29 through 35 push the last baseline down by
    a total of 5pt — six Bullets' worth of material absorbed by squeezing. The PDF
    is one page and every line is technically present, but the leading is visibly
    tighter than the same résumé one Bullet shorter.

    Budgeting against that cliff would mean every résumé rides on how much TeX
    happens to be willing to shrink. So the criterion here is geometric: content
    must leave a bottom margin at least as large as the top margin. That is what a
    human eye checks, it is stable, and PAGE_LINES derived from \textheight lands
    almost exactly on it.
    """
    profile = synthetic_profile(education_rows)

    def fits(n: int) -> bool:
        tex = render(
            build_entries(jobs, projects, n),
            skill_rows,
            profile=profile,
            education_first=education_first,
        )
        pages, _ = compile_tex(tex, stem)
        if pages != 1:
            return False
        height, top, bottom = content_extent(OUT_DIR / f"{stem}.pdf")
        return bottom >= (height - top)

    lo, hi = 1, 2
    while fits(hi):
        lo, hi = hi, hi * 2
        if hi > 256:
            raise SystemExit("page never overflows; something is wrong with the probe")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if fits(mid):
            lo = mid
        else:
            hi = mid
    return lo


#: A Skills section is two rows or it is not a section: its heading costs
#: SECTION_LINES, so one surviving row spends three lines of page to show one. Below
#: the floor the whole section goes, heading included (tools/pack.py MIN_SKILLS_ROWS,
#: docs/adr/0020-skills-section.md §4). Restated here rather than imported, because
#: the calibration isolates the template from the running tools.
MIN_SKILLS_ROWS = 2


def measured_row_lines(r: dict, bold_chars: int, chars: int) -> int:
    """Typeset lines a row takes, from character counts — tools/render.py's formula.

    Restated rather than imported for the same reason `escape_latex` is: a bug in
    the Renderer must not be able to move a constant. What that costs is a copy
    that can drift, so `tests/test_render.py` holds the two against each other.
    """
    label = r["label"].replace(r"\&", "&")
    text = r["text"].replace(r"\&", "&")
    return max(1, math.ceil((len(label) + 2) / bold_chars + len(text) / chars))


def skills_charge(c: Constants, skill_rows: list[dict]) -> int:
    """Lines the Skills section costs, heading included — tools/pack.py's charge.

    `ceil(section points / one Bullet line)`, so the rounding happens ONCE at the
    sum rather than per row. Charging one line per row instead — the charting
    assumption — over-promises by up to three lines as soon as rows wrap, and it is
    this function's job to prove that on the compiled page rather than in prose.
    """
    if len(skill_rows) < MIN_SKILLS_ROWS:
        return 0
    points = sum(
        c.SKILLS_ROW_PT
        + c.SKILLS_ROW_WRAP_PT
        * (measured_row_lines(r, c.BOLD_CHARS_PER_BULLET, c.CHARS_PER_BULLET) - 1)
        for r in skill_rows
    )
    return math.ceil(points / c.BULLET_LINE_PT) + c.SECTION_LINES


def predict_bullet_capacity(
    c: Constants, jobs: int, projects: int, education_rows: int, skill_rows: list[dict]
) -> int:
    """The budget arithmetic the Packer will do, spelled out.

    Fixed overhead: the profile header; the Summary, which every page carries and
    the budget therefore charges unconditionally
    (docs/adr/0044-the-page-opens-on-a-summary.md §5), together with its own
    `\\section` heading, charged flat for the same reason (that ADR's Addendum); a
    \\section for each of Experience, Projects and Education; an Entry header per
    placed Entry and per Education row (different macros since issue #31, but the same
    charge — see ENTRY_HEADER_LINES in tools/config.py); and the Skills section, whose
    own heading is charged inside `skills_charge` because whether it has one depends on
    what was composed.
    """
    sections = (1 if jobs else 0) + (1 if projects else 0) + (1 if education_rows else 0)
    overhead = (
        c.HEADER_LINES
        + c.SUMMARY_LINES
        + c.SECTION_LINES  # \section{Summary}, on every page
        + sections * c.SECTION_LINES
        + (jobs + education_rows) * c.ENTRY_HEADER_LINES
        + projects * c.PROJECT_HEADER_LINES
        + skills_charge(c, skill_rows)
    )
    return c.PAGE_LINES - overhead


def verify(
    c: Constants, jobs: int, projects: int, skill_rows: list[dict], stem: str = "verify"
) -> tuple[int, int, int]:
    """Compare the budget the Packer will compute against the page's real capacity.

    Returns (predicted, actual, slack). The one thing that must never happen is
    predicted > actual: that is a budget which over-promises, and it surfaces
    downstream as a two-page PDF blamed on the template. Slack in the other
    direction is inherent to integer line costs and is reported, not tuned away.
    """
    education_rows = len(SYNTHETIC_PROFILE["education"])
    predicted = predict_bullet_capacity(c, jobs, projects, education_rows, skill_rows)
    actual = max_bullets_within_margins(jobs, projects, education_rows, skill_rows, stem)
    return predicted, actual, actual - predicted


#: The Skills compositions the charge is checked against, from "no section at all"
#: to every row wrapping. Once a row may wrap, a section is no longer summarised by
#: its row count, so each one is a named composition rather than a number.
def wrap_compositions() -> list[tuple[str, list[dict]]]:
    wrapping = row("Cloud & Infrastructure", WRAPPING_SKILLS[:8])
    return [
        ("no section", []),
        ("2 rows", rows_for(2)),
        ("4 rows, none wrap", rows_for(4)),
        ("4 rows, 1 wraps", rows_for(3) + [wrapping]),
        ("4 rows, 2 wrap", rows_for(2) + [wrapping] * 2),
        ("4 rows, all wrap", [wrapping] * 4),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="leave the probe PDFs in out/")
    args = ap.parse_args()

    if shutil.which("pdflatex") is None:
        sys.stderr.write(
            "pdflatex not on PATH. Install TinyTeX or TeX Live first — see docs/calibration.md.\n"
        )
        return 2

    skills_row, skills_row_wrap, marginals, ladder = measure_skills_row()
    h = measure_heights(skills_row, skills_row_wrap)
    chars, per_sample = measure_chars_per_bullet(h.bullet_line_width)
    bold_rates = measure_bold_widths()
    bold_chars = math.floor(h.bullet_line_width / max(rate for _, rate in bold_rates))
    lead_chars, lead_width, lead_per_sample = measure_lead_chars()
    bold_lead_chars, _, lead_bold_per_sample = measure_bold_lead_chars()
    lead_row_pt = measure_lead_row()
    summary_ceiling_pt = SUMMARY_LINES * round(h.bullet, 2)
    summary_chars, summary_longest = measure_summary_chars(summary_ceiling_pt)
    summary_width, summary_widths = measure_summary_widths()
    summary_per_sample = [
        (sample, width / len(sample)) for sample, width in zip(SUMMARY_SAMPLES, summary_widths)
    ]
    summary_fit_pt = measure_summary_fit(SUMMARY_SAMPLES[0], "summaryfit_ok")
    summary_overlong_pt = measure_summary_fit(OVERLONG_SUMMARY, "summaryfit_over")
    c = derive_element_costs(h, chars, bold_chars, summary_chars)
    from_textheight = c.PAGE_LINES
    c.PAGE_LINES, sweep_rows = calibrate_page_lines(c)
    one_line_pt, two_line_pt = measure_wrapped_bullet()

    print(f"Measured heights (points, 1in = {PT_PER_INCH}pt)")
    print(f"  one Bullet line          {h.bullet:8.2f}")
    print(f"  two-line Bullet          {two_line_pt:8.2f}   "
          f"(charged 2 x {h.bullet:.2f}; the second line earns no constant)")
    print(f"  Entry header + glue      {h.entry_header:8.2f}")
    print(f"  Project header + glue    {h.project_header:8.2f}")
    print(f"  section heading          {h.section:8.2f}")
    print(f"  Static profile header    {h.profile_header:8.2f}")
    print(f"  Summary + its heading    {h.summary:8.2f}   "
          f"(charged ({SUMMARY_LINES} + {c.SECTION_LINES}) x {h.bullet:.2f} = "
          f"{(SUMMARY_LINES + c.SECTION_LINES) * h.bullet:.2f})")
    print(f"  Education row            {h.education_row:8.2f}")
    print(f"  Skills row, first line   {h.skills_row:8.2f}")
    print(f"  Skills row, each after   {h.skills_row_wrap:8.2f}")
    print(f"  \\textheight              {h.text_height:8.2f}")
    print(f"  Bullet \\linewidth        {h.bullet_line_width:8.2f}")
    print(f"  Skills row \\linewidth    {h.skills_row_width:8.2f}")
    print(f"  Summary \\linewidth       {h.summary_width:8.2f}")
    print()
    # These three are the assumptions the constant set rests on. They are checked
    # rather than asserted in prose, because each one silently becomes a
    # miscalibration the page-count assert would blame on the template.
    print("Sanity checks")
    checks = []

    edu_lines = measure_education_lines()

    # An Education row and an Entry header must cost the SAME NUMBER OF LINES,
    # since there is no EDUCATION_LINES constant to charge them separately.
    checks.append((
        "Education row costs the same lines as an Entry header",
        edu_lines == c.ENTRY_HEADER_LINES,
        f"{edu_lines} lines by overflow vs ENTRY_HEADER_LINES={c.ENTRY_HEADER_LINES}",
    ))

    # A WRAPPED BULLET MUST FIT IN THE TWO LINES IT IS CHARGED. The Packer grants a
    # slot one line or two and charges the integer; no constant holds the second
    # line's real height, so this check is the only thing standing between a template
    # change and a budget that over-promises on every wide Bullet. The sample must
    # also actually wrap, or the check passes while measuring nothing.
    wrapped = two_line_pt > one_line_pt + 0.5
    checks.append((
        "a two-line Bullet costs no more than two Bullet lines",
        wrapped and two_line_pt <= 2 * c.BULLET_LINE_PT + 0.01,
        f"{len(WRAPPED_BULLET_SAMPLE)}ch measures {two_line_pt:.2f}pt against "
        f"2 x {c.BULLET_LINE_PT:.2f} = {2 * c.BULLET_LINE_PT:.2f}pt"
        + ("" if wrapped else " — AND IT DID NOT WRAP, so this measured nothing"),
    ))

    # A SUPPORTING ROW COSTS WHAT A SKILLS ROW COSTS. `supporting_charge` spends
    # SKILLS_ROW_PT on it and config.py carries no name of its own for it, so this is
    # the whole of what stops the two drifting apart. Half a point of slack, which is
    # the same tolerance the wrapped-Bullet check works to.
    supporting_row = measure_supporting_row()
    checks.append((
        "a supporting row costs the same as a Skills row",
        abs(supporting_row - h.skills_row) <= 0.5,
        f"{supporting_row:.2f}pt vs SKILLS_ROW_PT={c.SKILLS_ROW_PT:.2f} "
        f"(measured Skills row {h.skills_row:.2f}pt)",
    ))

    # A Skills row must be at least a Bullet wide, which is what makes the two
    # character rates safe to predict a row's width at. It is allowed to be wider —
    # that direction only leaves width unused.
    slack_pt = h.skills_row_width - h.bullet_line_width
    checks.append((
        "Skills row is at least as wide as a Bullet",
        slack_pt >= -1.0,
        f"{slack_pt:+.2f}pt wider than a Bullet",
    ))

    # One more row must cost the same as the last one, or the section's cost stops
    # being expressible as a sum over rows and SKILLS_ROW_PT means nothing.
    spread = max(marginals) - min(marginals)
    checks.append((
        "one more Skills row always costs the same",
        spread <= 0.5,
        f"rows 2..6 marginal {min(marginals):.2f}..{max(marginals):.2f}pt, "
        f"spread {spread:.2f}pt",
    ))

    # The character formula decides a row's line count BEFORE the compile, and the
    # budget is built on it. It may over-count — that only costs a skill — and must
    # never under-count, which would promise a line the page does not have.
    formula_holds = True
    formula_detail = []
    for chars_of_skills, typeset, _points in ladder:
        predicted = math.ceil(
            (len("Cloud & Infrastructure") + 2) / bold_chars + chars_of_skills / chars
        )
        formula_holds = formula_holds and predicted >= typeset
        formula_detail.append(f"{chars_of_skills}ch {typeset}->{predicted}")
    checks.append((
        "the row-lines formula never under-counts what TeX typeset",
        formula_holds,
        ", ".join(formula_detail),
    ))

    # LEAD_LINES = 1 is fixed by decision, not derived (docs/adr/0032-the-entry-arc.md
    # §4) — but a one-line lead that measures well past a Bullet line would be an
    # over-promise nobody chose, so it is checked rather than assumed.
    checks.append((
        "a one-line lead costs no more than one Bullet line",
        lead_row_pt <= c.BULLET_LINE_PT + 0.5,
        f"{lead_row_pt:.2f}pt against BULLET_LINE_PT={c.BULLET_LINE_PT:.2f}pt",
    ))

    # SUMMARY_LINES = 2 is fixed by decision the same way
    # (docs/adr/0044-the-page-opens-on-a-summary.md §1), and owes the same proof:
    # the whole section — the \section{Summary} heading, two typeset lines of \small
    # prose and the \vspace under them — has to fit in the four Bullet lines the
    # budget charges for it. It is at the TOP of the page, so an over-promise here is
    # paid by whatever loses the last slot, with nothing said.
    #
    # HEADING AND PROSE ARE ONE CHECK BECAUSE THEY ARE ONE MEASUREMENT. \section
    # contributes its space through \addvspace, which merges with the skip already on
    # the vertical list, so the glue between the two belongs to neither on its own —
    # see SUMMARY_BLOCK for what the two half-differentials read instead.
    summary_charge = SUMMARY_LINES + c.SECTION_LINES
    checks.append((
        "the Summary and its heading cost no more than the four lines charged",
        h.summary <= summary_charge * c.BULLET_LINE_PT + 0.01,
        f"{h.summary:.2f}pt against ({SUMMARY_LINES} + {c.SECTION_LINES}) x "
        f"{c.BULLET_LINE_PT:.2f} = {summary_charge * c.BULLET_LINE_PT:.2f}pt",
    ))

    # THE BOLD PENALTY IS A PROPERTY OF THE FONT, NOT OF THE COLUMN — the claim
    # render.py rests on when it charges the Summary's bold spans against
    # SUMMARY_CHARS, a budget measured at a different and wider \linewidth, without a
    # BOLD_SUMMARY_CHARS anybody took
    # (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md §6).
    #
    # It holds because both counts are the same width divided by a pt/char rate, so
    # the width cancels and CHARS_PER_BULLET / BOLD_CHARS_PER_BULLET is the ratio of
    # the two rates. What is checked is the direction that matters: the ratio the
    # constants express must be AT LEAST the ratio TeX measured, or a bold character
    # is charged less than it costs — and under-counting is the one thing this file
    # forbids. The two `floor`s that produced the constants push it the safe way.
    charged_ratio = c.CHARS_PER_BULLET / c.BOLD_CHARS_PER_BULLET
    measured_ratio = (
        max(rate for _, rate in bold_rates) / max(ppc for _, ppc in per_sample)
    )
    checks.append((
        "a bold character is charged at least what it measures, at any width",
        charged_ratio >= measured_ratio - 0.001,
        f"CHARS_PER_BULLET/BOLD_CHARS_PER_BULLET = {charged_ratio:.4f} against a "
        f"measured {max(rate for _, rate in bold_rates):.3f}/"
        f"{max(ppc for _, ppc in per_sample):.3f} = {measured_ratio:.4f} pt/char",
    ))

    # THE SAME CHECK AT THE LEAD'S OWN WIDTH, which is the whole of what the lead's
    # bold twin buys over reusing the Bullet's ratio. `check_lead_lengths` charges a
    # lead's bold spans at LEAD_CHARS / BOLD_LEAD_CHARS, and both of those counts are
    # the lead's 514.40pt divided by a pt/char rate — so the direction that matters is
    # the same one §6 names for the Bullet: the ratio the constants express must be AT
    # LEAST the ratio TeX measured at this width, or a bold character in a lead is
    # charged less than it costs
    # (docs/adr/0046-every-impact-figure-and-the-declared-keyword.md, Addendum).
    lead_charged_ratio = lead_chars / bold_lead_chars
    lead_measured_ratio = (
        max(rate for _, rate in lead_bold_per_sample)
        / max(ppc for _, ppc in lead_per_sample)
    )
    checks.append((
        "a bold character in a lead is charged at least what it measures",
        lead_charged_ratio >= lead_measured_ratio - 0.001,
        f"LEAD_CHARS/BOLD_LEAD_CHARS = {lead_charged_ratio:.4f} against a measured "
        f"{max(rate for _, rate in lead_bold_per_sample):.3f}/"
        f"{max(ppc for _, ppc in lead_per_sample):.3f} = {lead_measured_ratio:.4f} pt/char",
    ))

    # And the budget the charge guards has to be the RIGHT SIZE, which the ratio
    # cannot say on its own: a safe ratio over a budget that was too generous still
    # spills a lead onto a second line, and LEAD_LINES charges one. So every sample is
    # composed out to the last word the bold-aware tape admits, with a real bold span
    # in it, and the width TeX gives the result is read back.
    at_budget = measure_lead_at_budget(lead_chars, bold_lead_chars)
    widest = max(at_budget, key=lambda built: built[2])
    checks.append((
        "a lead composed to the bold-aware budget still fits the lead's line",
        all(width <= lead_width for _, _, width in at_budget),
        f"{len(at_budget)} samples at the tape's edge, widest {widest[1]}ch at "
        f"{widest[2]:.2f}pt against a {lead_width:.2f}pt line",
    ))

    # And the runtime gate has to be able to TELL the two apart. render.py refuses a
    # Summary whose \parbox measures past SUMMARY_LINES x BULLET_LINE_PT, which is
    # only a gate if a legal two-line Summary lands under it and a three-line one
    # lands over it. Both are measured rather than reasoned about, because the
    # ceiling is an integer line charge and the paragraph is \small: nothing makes
    # it obvious in which gap the two heights fall.
    ceiling = SUMMARY_LINES * c.BULLET_LINE_PT
    checks.append((
        "the Summary-fit ceiling separates a two-line Summary from a three-line one",
        summary_fit_pt <= ceiling < summary_overlong_pt,
        f"2 lines {summary_fit_pt:.2f}pt <= {ceiling:.2f}pt < 3 lines "
        f"{summary_overlong_pt:.2f}pt",
    ))

    for label, ok_, detail in checks:
        print(f"  [{'ok' if ok_ else 'FAIL'}] {label}  ({detail})")
    checks_ok = all(ok_ for _, ok_, _ in checks)
    print()
    print("Characters per line, by sample (points per character)")
    for sample, ppc in per_sample:
        fits = math.floor(h.bullet_line_width / ppc)
        print(f"  {ppc:5.3f} pt/char -> {fits:3d} chars   {sample[:52]}...")
    print(f"  worst case wins: CHARS_PER_BULLET = {c.CHARS_PER_BULLET}")
    print()
    print(f"Lead line — its own \\linewidth is {lead_width:.2f}pt "
          f"({lead_width - h.bullet_line_width:+.2f}pt against a Bullet's)")
    for sample, ppc in lead_per_sample:
        fits = math.floor(lead_width / ppc)
        print(f"  {ppc:5.3f} pt/char -> {fits:3d} chars   {sample[:52]}...")
    print(f"  worst case wins: LEAD_CHARS = {lead_chars}")
    print("  and the same line's BOLD budget — the twin "
          "docs/adr/0046 promised would be measured")
    print("  rather than derived, taken at this same \\linewidth so the ratio is the "
          "font's:")
    for sample, ppc in lead_bold_per_sample:
        fits = math.floor(lead_width / ppc)
        print(f"  {ppc:5.3f} pt/char -> {fits:3d} chars   bold {sample}")
    print(f"  worst case wins: BOLD_LEAD_CHARS = {bold_lead_chars}   "
          f"(a lead's bold penalty is {lead_chars}/{bold_lead_chars} = "
          f"{lead_chars / bold_lead_chars:.4f})")
    for text, plain, width in at_budget:
        print(f"  {plain:3d}ch at the tape's edge -> {width:7.2f}pt   {text[:44]}...")
    print(f"  one lead line measures {lead_row_pt:.2f}pt against "
          f"BULLET_LINE_PT = {c.BULLET_LINE_PT:.2f}pt (LEAD_LINES is 1, by decision, "
          f"not derived — docs/adr/0032-the-entry-arc.md §4)")
    print()
    print(f"Summary — its own \\linewidth is {summary_width:.2f}pt "
          f"({summary_width - h.bullet_line_width:+.2f}pt against a Bullet's, "
          f"{summary_width - lead_width:+.2f}pt against a lead's)")
    print("  measured directly, by boxing every word-prefix — not by a pt/char rate,")
    print("  which over-promises here by about a word (the `would fit` column):")
    for (sample, ppc), fits in zip(summary_per_sample, summary_longest):
        naive = math.floor(SUMMARY_LINES * summary_width / ppc)
        print(f"  {ppc:5.3f} pt/char -> {fits:3d} chars fit, {naive:3d} would "
              f"fit at that rate   {sample[:34]}...")
    print(f"  worst case wins: SUMMARY_CHARS = {summary_chars} "
          f"({SUMMARY_LINES} lines' worth)")
    print(f"  the section — heading and prose, priced together because \\addvspace "
          f"merges\n  the glue between them — measures {h.summary:.2f}pt against "
          f"({SUMMARY_LINES} + {c.SECTION_LINES}) x {c.BULLET_LINE_PT:.2f} = "
          f"{(SUMMARY_LINES + c.SECTION_LINES) * c.BULLET_LINE_PT:.2f}pt "
          f"(SUMMARY_LINES is 2, by decision,\n  not derived — "
          f"docs/adr/0044-the-page-opens-on-a-summary.md §1)")
    print(f"  render.py's fit gate: 2-line \\parbox {summary_fit_pt:.2f}pt, ceiling "
          f"{SUMMARY_LINES * c.BULLET_LINE_PT:.2f}pt, 3-line \\parbox "
          f"{summary_overlong_pt:.2f}pt")
    print()
    print("Bold characters per line, by label (points per character)")
    for label, rate in bold_rates:
        print(f"  {rate:5.3f} pt/char -> {math.floor(h.bullet_line_width / rate):3d} "
              f"chars   {label}")
    print(f"  worst case wins: BOLD_CHARS_PER_BULLET = {c.BOLD_CHARS_PER_BULLET}")
    print()
    print("What a Skills category row costs")
    print(f"  one more row     {h.skills_row:6.2f}pt = "
          f"{h.skills_row / h.bullet:.3f} Bullet lines")
    print(f"  each line after  {h.skills_row_wrap:6.2f}pt = "
          f"{h.skills_row_wrap / h.bullet:.3f} Bullet lines")
    print("  chars of skills   typeset lines   measured")
    for chars_of_skills, typeset, points in ladder:
        print(f"  {chars_of_skills:15d}   {typeset:13d}   {points:6.2f}pt")
    print()
    print("PAGE_LINES, calibrated against the compiled page")
    print(f"  floor(\\textheight / one Bullet) = {from_textheight}   (first guess only)")
    print("  jobs  projects  capacity  + overhead = implied PAGE_LINES")
    for jobs, projects, actual, implied in sweep_rows:
        print(f"  {jobs:4d}  {projects:8d}  {actual:8d}  "
              f"{'':11s}{implied}{'   <-- binding' if implied == c.PAGE_LINES else ''}")
    print(f"  the smallest wins, so PAGE_LINES = {c.PAGE_LINES}")
    print()
    print("Derived constants (element costs rounded up, PAGE_LINES from the sweep)")
    for k, v in vars(c).items():
        print(f"  {k:20s} {v}")
    print()

    print("Verification — predicted budget vs the page's real capacity")
    print("  jobs  projects  predicted  actual  slack")
    ok = checks_ok
    for jobs, projects in SWEEP_SHAPES:
        predicted, actual, slack = verify(c, jobs, projects, skills_sample())
        flag = "" if slack >= 0 else "   <-- OVER-PROMISES"
        if slack < 0:
            ok = False
        print(f"  {jobs:4d}  {projects:8d}  {predicted:9d}  {actual:6d}  {slack:5d}{flag}")
    print()
    print("  Slack must never be negative — a negative number is a budget that")
    print("  over-promises, and it surfaces later as a two-page PDF blamed on the")
    print("  template. Positive slack is the inherent cost of integer line charges.")
    print()

    # The same check along the other axis. A row's height is a function of its
    # CONTENT once a row may wrap, so the Skills charge has to hold at every wrap
    # count, not only on the composition the sweep happens to use. It is run on the
    # (2, 0) shape, which has the least per-Entry rounding slack absorbing the
    # page's own rounding and is therefore the shape that catches an over-promise;
    # the sweep above covers the Entry-count axis.
    print("The Skills charge, at every wrap count — (2, 0), the tightest shape")
    print("  composition          charged  predicted  actual  slack")
    for index, (name, skill_rows) in enumerate(wrap_compositions()):
        predicted, actual, slack = verify(c, 2, 0, skill_rows, f"wrapcheck{index}")
        flag = "" if slack >= 0 else "   <-- OVER-PROMISES"
        if slack < 0:
            ok = False
        print(f"  {name:20s}  {skills_charge(c, skill_rows):7d}  {predicted:9d}  "
              f"{actual:6d}  {slack:5d}{flag}")
    print()
    print("  Charging one line per row instead — the shape this design was charted")
    print("  with — over-promises by up to three lines as soon as rows wrap. That is")
    print("  not a conservative simplification; it is a two-page PDF.")
    print()
    print("RESULT:", "constants hold" if ok else "CONSTANTS DO NOT HOLD")

    if not args.keep:
        shutil.rmtree(OUT_DIR, ignore_errors=True)
    else:
        print(f"\nProbe output left in {OUT_DIR}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
