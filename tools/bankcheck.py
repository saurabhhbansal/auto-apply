#!/usr/bin/env python3
"""The bank parse check — read the whole bank, and say whether the reader accepts it.

    python tools/bankcheck.py [bank-dir]

Reads nothing else and writes nothing.

    profile: …            only when bank/profile.md is missing or still the example's
    Static profile: …     what the part of the page that never competes costs
    profile standing: …   what the Summary has to describe the candidate with
    bank supporting: …    only when the bank holds entries that never compete
    bank locations: …     only when the job entries are written in two shapes
    project stack: …      only when a project's stack names a technology no claim carries
    bank parses            every Entry file read cleanly; exit 0
    bankcheck.py: <path>:<line>: <what is wrong>
                           the first file the reader refuses, or a profile.md
                           render.py would refuse; exit 1

`bank parses` is the LAST line of a clean run and is what the three skills read as
"go on". The lines above it are **advisories**: they never change the exit code
and never stop a run. They are here because the parts of the page that never compete
for a slot are the parts nothing else looks at, and both of these are the maker's
call rather than the repo's (docs/adr/0031-the-entry-header-is-built.md §5, §7).

An empty bank parses: an empty glob is an empty bank, not an error. So does a bank
with no `profile.md`, which is a fresh clone — it gets a line saying what to copy.
A `profile.md` that exists is validated by render.py's own `Profile`, so a typo in
it surfaces here rather than at the end of the first run.

The bank is found beside this script (`<repo>/bank`), not relative to the caller, so
the check says the same thing from any working directory. A different folder can be
named on the command line.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank  # noqa: E402  (tools/ is not a package; the Entry file reader)
import config  # noqa: E402  (the page-budget block the cost line is arithmetic over)
import render  # noqa: E402  (the Profile validation; Jinja2 is imported only to render)
from pack import MAX_SUPPORTING_ROWS  # noqa: E402  (the cap the cost line stops at)

REPO = Path(__file__).resolve().parents[1]
DEFAULT_BANK = REPO / "bank"

#: One school in the Static profile. Counted here, never validated — `render.py`'s
#: `Profile` is the seam that validates that file, and it fails a profile this check
#: must survive: there is no `bank/profile.md` in a fresh clone, and an empty bank has
#: to parse. So this counts rows and says nothing about what is in them.
EDUCATION_ROW = re.compile(r"^###\s+\S+\s*$", re.M)

#: The Static profile's optional `## Standing` block — free prose, one fact a line,
#: the Summary's only source for what the candidate IS
#: (docs/adr/0044-the-page-opens-on-a-summary.md §3). Read the same shallow way the
#: Education rows are: this counts and says nothing about what is in them.
STANDING_BLOCK = re.compile(r"^##\s+Standing\s*$(?P<body>.*?)(?=^##\s|\Z)", re.M | re.S)


def static_profile_cost(bank_dir: Path) -> str:
    """What the half of the page that never competes spends, in Bullet lines.

    Not a rule and not a failure. `docs/adr/0013-ingestion-shape.md` §7 settled that
    Education never competes and the Static profile is not a Bank entry, and this
    does not reopen it — it prints the price so the maker can see it. On the page
    this was written against, the profile spent 9 of 50 lines before a single piece
    of evidence competed, and one of the two Education rows was a Grade-12 school.

    The Summary is in the sum because it is charged the same way: never competes,
    charged unconditionally, and nothing else on this line's side of the page shows
    it spent (docs/adr/0044-the-page-opens-on-a-summary.md §5). It is not part of the
    Static profile and is named separately for that reason — 11 of 50 now.

    Its `\\section` heading rides in the same term, because `pack.bullet_budget`
    charges it the same way: flat, on every page, with no condition to test
    (docs/adr/0044-the-page-opens-on-a-summary.md, Addendum). That is why the term
    reads `Summary 4` where the constant reads 2.

    The Education `\\section` heading is in the sum because `pack.bullet_budget`
    charges it in the sum: the Template drops the section whole when there are no
    rows, so the heading exists because the rows do. `pack.EDUCATION_ROWS` is
    deliberately not read here — this prints what the profile on disk costs, and
    `render.py` is where a profile the budget was not charged for fails the run.
    """
    profile = bank_dir / "profile.md"
    summary_lines = config.SUMMARY_LINES + config.SECTION_LINES
    summary = f" + Summary {summary_lines}"
    if not profile.is_file():
        return (
            f"Static profile: no {profile} — header {config.HEADER_LINES}{summary} is "
            f"{config.HEADER_LINES + summary_lines} lines before any evidence"
        )
    rows = len(EDUCATION_ROW.findall(bank.strip_comments(profile.read_text(encoding="utf-8"))))
    education = config.SECTION_LINES + rows * config.ENTRY_HEADER_LINES if rows else 0
    total = config.HEADER_LINES + summary_lines + education
    heading = f"Education heading {config.SECTION_LINES} + " if rows else ""
    return (
        f"Static profile: header {config.HEADER_LINES}{summary} + {heading}{rows} row(s) "
        f"at {config.ENTRY_HEADER_LINES} = {total} of {config.PAGE_LINES} page lines"
    )


def standing_advisory(bank_dir: Path) -> str:
    """What the Summary has to say who the candidate is with, counted, never judged.

    The Summary is the one element on the page that describes the CANDIDATE rather
    than a piece of work, and the bank holds almost nothing of that kind: a Claim is
    an assertion about something that was done, and an Entry header is a title and an
    employer. `## Standing` is where the rest lives, and it is optional — so the
    interesting state is the absent one, and the maker is the only person who can
    fill it (docs/adr/0044-the-page-opens-on-a-summary.md §3).

    **This never fails, and the shape of the check is why.** Every other line the
    Summary is bound by is mechanical — a character count, a figure, a height. What
    goes in `## Standing` is a judgement about a life, and `0010` refused a second
    judgement of prose on the record. So this counts lines and prices the absence,
    exactly as `static_profile_cost` prices Education rather than ruling on them
    (`docs/adr/0031-the-entry-header-is-built.md` §5, §7).
    """
    profile = bank_dir / "profile.md"
    if not profile.is_file():
        return f"profile standing: no {profile} — the Summary has the Claims and nothing else"
    match = STANDING_BLOCK.search(bank.strip_comments(profile.read_text(encoding="utf-8")))
    facts = [line.strip() for line in match.group("body").splitlines() if line.strip()] if match else []
    if not facts:
        return (
            f"profile standing: no `## Standing` block in {profile}. Nothing fails on "
            f"this — the Summary is composed from the entry headers and the Claims "
            f"instead. What it cannot then say is what you ARE, only what you did, and "
            f"a title you do not hold is not available to it to invent"
        )
    return (
        f"profile standing: {len(facts)} fact(s) in {profile}, which is what the "
        f"Summary says who you are from"
    )


def location_advisory(entries: dict[str, bank.Entry]) -> str | None:
    """The entries whose `location` is not written to the depth its neighbours are.

    Compared by comma count, which is all a machine can see of an address:
    `Austin, Texas, USA` above `Pune, Maharashtra` is two shapes in one column, and
    both of them are correct addresses. So this ADVISES and never refuses — the shape
    is `City, Region, Country` and the choice is the maker's
    (docs/adr/0031-the-entry-header-is-built.md §5).

    **A location with no comma in it is not compared at all.** `Remote`,
    `Open source`, `Self-hosted` are not addresses written shallow — they are a
    different kind of answer, and a job may give one as readily as a project may.
    The comma is the only signal here that a value was written as an address, and
    filtering on the Entry's `type` instead would fire on a remote job.
    """
    shapes: dict[int, list[bank.Entry]] = {}
    for entry in entries.values():
        if "," in entry.location:
            shapes.setdefault(entry.location.count(","), []).append(entry)
    if len(shapes) < 2:
        return None
    lines = [
        f"    {entry.slug}: {entry.location}"
        for _, group in sorted(shapes.items())
        for entry in sorted(group, key=lambda found: found.slug)
    ]
    return (
        f"bank locations: {len(shapes)} address shapes, and one column of the page "
        f"shows them together:\n"
        + "\n".join(lines)
        + "\n    The shape is `City, Region, Country`. Nothing fails on this — it is "
        "your address to write."
    )


def supporting_advisory(entries: dict[str, bank.Entry]) -> str | None:
    """What the three supporting sections hold, and what each would cost the page.

    Advisory, never a failure, for the standing reason the two lines above it are:
    what belongs in Certifications, Positions of Responsibility and Extracurriculars
    is a judgement about a life, and `0010` refused a second judgement of prose on
    the record. What this can say is arithmetic — how many rows there are and what
    they would spend if a posting called for them
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §9).

    THE COST IS THE POINT OF THE LINE. A supporting entry costs nothing until it
    places, and then it costs a whole section heading plus its rows — three lines for
    one credential. A maker looking at a bank with one certification in it should be
    able to see that before a run spends them.

    What this cannot say is whether the entry is worth showing. A certification the
    posting never mentions costs the page nothing at all, and one it names by name is
    worth its heading three times over — which of those a run is looking at is
    `tailor`'s judgement against a posting, and there is no posting here.

    Absent entirely when the bank holds none, which is every bank before the first
    such `ingest` session. A line saying *no certifications* would fire on every
    clone and price an absence nobody has decided about yet.
    """
    supporting = [entry for entry in entries.values() if entry.supporting]
    if not supporting:
        return None
    parts = []
    for type_, section in bank.SECTION_OF_TYPE.items():
        held = [entry for entry in supporting if entry.type == type_]
        if not held:
            continue
        rows = min(len(held), MAX_SUPPORTING_ROWS)
        points = config.SKILLS_ROW_PT * rows
        cost = math.ceil(points / config.BULLET_LINE_PT) + config.SECTION_LINES
        capped = f", {len(held) - rows} past the {MAX_SUPPORTING_ROWS}-row cap" if len(held) > rows else ""
        parts.append(f"    {section}: {len(held)} entry(s){capped} — {cost} line(s) if the page shows them")
    return (
        f"bank supporting: {len(supporting)} entry(s) that never compete for a Bullet "
        f"slot. They cost the page nothing until a posting calls for them or the width "
        f"pass leaves room:\n" + "\n".join(parts)
    )


def stack_advisory(entries: dict[str, bank.Entry]) -> str | None:
    """A project `stack:` technology that no Claim in that project carries.

    The stack is typeset beside the project's name and traced by nothing — render.py
    checks a Bullet's figures and a Skills row's citations, not a header. So the one
    thing that keeps it honest is that every technology in it is one some Claim of the
    same project already records in its `skills:` line. Advisory: the fix is a word in
    one file, and which file is the user's call
    (docs/adr/0057-the-page-reads-like-a-resume.md §3).
    """
    lines: list[str] = []
    for entry in entries.values():
        if entry.type != "project" or not entry.stack:
            continue
        carried = {skill.strip().lower() for claim in entry.claims for skill in claim.skills}
        loose = [
            item.strip()
            for item in entry.stack.split(",")
            if item.strip() and item.strip().lower() not in carried
        ]
        if loose:
            lines.append(f"    {entry.slug}: {', '.join(loose)}")
    if not lines:
        return None
    return (
        "project stack: technologies on a project's header that none of its claims' "
        "`skills:` lines carry — add them to the claim that used them, or drop them "
        "from `stack:`:\n" + "\n".join(lines)
    )


def profile_check(bank_dir: Path) -> str | None:
    """`bank/profile.md`, validated the way render.py will — or what to do without one.

    Returns an advisory line, or None. Raises `render.RenderError` for a profile
    render.py would refuse, which is a failure here too: nothing renders past it.
    """
    profile = bank_dir / "profile.md"
    if not profile.is_file():
        return (
            f"profile: no {profile} — copy templates/profile.example.md to "
            f"bank/profile.md and fill it in. Nothing renders without it"
        )
    loaded = render.Profile.load(profile)
    example, _, _ = render.Profile._parse(render.PROFILE_EXAMPLE)
    left = [
        key
        for key, value in example.items()
        if key != "location" and value and loaded.fields.get(key) == value
    ]
    if left:
        return (
            f"profile: {', '.join(f'`{key}`' for key in left)} in {profile} still "
            f"hold the example's values — replace them with yours"
        )
    return None


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("usage: python tools/bankcheck.py [bank-dir]", file=sys.stderr)
        return 2
    bank_dir = Path(argv[1]) if len(argv) == 2 else DEFAULT_BANK
    try:
        entries = bank.load_bank(bank_dir)
    except bank.BankError as error:
        print(f"bankcheck.py: {error}", file=sys.stderr)
        return 1
    try:
        profile = profile_check(bank_dir)
    except render.RenderError as error:
        print(f"bankcheck.py: {error}", file=sys.stderr)
        return 1
    if profile:
        print(profile)
    print(static_profile_cost(bank_dir))
    print(standing_advisory(bank_dir))
    for advisory in (
        supporting_advisory(entries),
        location_advisory(entries),
        stack_advisory(entries),
    ):
        if advisory:
            print(advisory)
    print("bank parses")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
