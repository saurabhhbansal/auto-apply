"""The Entry file reader — bank markdown in, Entries and Claims out.

Stdlib-only, and a library rather than a command. Imported by `render.py` and never
by `pack.py`: the Packer works from the Score table alone, so it cannot read the bank
even by accident. `tests/test_bank.py` holds that import boundary in code.

This does not judge. Unknown keys are surfaced (`unknown_keys`), never dropped and
never rejected — a hand-edited file may carry keys this parser has not heard of. What
*is* rejected is a shape that would make a Claim disappear silently: a mistyped
heading, a `number` with no `provenance`, prose loose between claims. Every failure
names the file, the line and the claim.

## The Entry file shape

    ---
    type: job
    title: Senior Software Engineer
    org: Helios Pay
    location: Bengaluru, India
    started: 2023-01
    ended: present
    domain: payments
    ---

    ## c1
    number: 40%
    provenance: measured
    skills: Go, Kafka, PostgreSQL

    **Assertion:** Cut checkout p99 latency 40% by batching commits.

    **Evidence:** The consumer committed offsets per message, so ...

Two details of that shape:

- One `key: value` pair per line, though two separated by `·` also parse.
- `**Assertion:**` and `**Evidence:**` are the body's two labels. Evidence may be
  absent — a Claim added at a Checkpoint has a near-empty evidence body by
  construction, and refusing it would refuse the only claim write-back can produce.
"""

from __future__ import annotations

import re
from pathlib import Path

#: The loose `key: value` lines a Claim is known to carry. Anything else is kept
#: and surfaced as an unknown key — the list is what this parser *understands*,
#: not what a Claim is allowed to say.
CLAIM_KEYS = ("number", "provenance", "confidence", "needs-interview", "skills")

#: Entry frontmatter, per docs/adr/0004-bank-entry-schema.md §3, as
#: docs/adr/0031-the-entry-header-is-built.md §1 corrects it: `dates` is gone and
#: `started`/`ended` are here in its place. `domain` is a light ranking field and
#: optional; the rest are what the Template's Entry header needs, so their absence is
#: a hole in the résumé rather than a missing nicety.
#:
#: `stack` and `link` are a PROJECT's, and optional: what it was built with and where
#: it lives, typeset on the project's one-row header in place of the employer and
#: office a project does not have — which is also why a project need not carry `org`
#: or `location` (docs/adr/0057-the-page-reads-like-a-resume.md §3).
ENTRY_KEYS = (
    "type", "title", "org", "location", "started", "ended", "domain", "stack", "link",
)
REQUIRED_ENTRY_KEYS = ("type", "title", "org", "location", "started", "ended")
PROJECT_OPTIONAL_KEYS = ("org", "location")

#: `link` lands inside a LaTeX \href target as well as in the visible text. The target
#: is passed raw and the text escaped, so `_` and `~` are fine; what is refused is what
#: a raw target cannot carry — whitespace, `%`, `#`, a backslash or a brace — plus `&`,
#: `$` and `^`. The same rule `bank/profile.md` holds its own link fields to.
LINK_UNSAFE = re.compile(r"[%#&\s\\{}$^]")

#: The two Entry types that COMPETE — scored, ranked, seated by the Packer, and
#: routed to the Experience and Projects sections of the page.
COMPETING_TYPES = ("job", "project")

#: The three that do not. A supporting entry is never scored, never reserved a block
#: and never takes a Bullet slot; it renders as at most one row of a supporting
#: section, and only when the posting calls for it or the page has room left over
#: (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §2).
#:
#: Ordered as the page orders the sections, which is also the order the residue fill
#: offers them in (§5, §7). Nothing reads this order out of a set, so it is a tuple.
SUPPORTING_TYPES = ("certification", "responsibility", "extracurricular")

ENTRY_TYPES = COMPETING_TYPES + SUPPORTING_TYPES

#: Type -> the folder under `bank/` it is filed in. The folder IS the type (`0005`
#: §2), so this table is the whole of the mapping and `load_bank` refuses a file
#: whose frontmatter disagrees with the folder it sits in.
TYPE_FOLDERS = {
    "job": "jobs",
    "project": "projects",
    "certification": "certifications",
    "responsibility": "responsibilities",
    "extracurricular": "extracurriculars",
}

#: Supporting type -> the section of the page it routes to. The plural of the type,
#: with one exception where the plural is not what a résumé calls the section.
#:
#: `tools/pack.py` restates the section names rather than importing them — the Packer
#: may import nothing but the stdlib and `config` — and `tests/test_bank.py` holds
#: the two copies equal, the same arrangement the month pattern already has.
SECTION_OF_TYPE = {
    "certification": "certifications",
    "responsibility": "responsibilities",
    "extracurricular": "extracurriculars",
}

PROVENANCE_TIERS = ("measured", "estimated")

#: A month, and an end date. THE BANK OWNS THIS PATTERN — the Entry header's dates are
#: composed from these two fields rather than typed, so a free-text date here would be
#: a second format on a page that is supposed to have exactly one
#: (docs/adr/0031-the-entry-header-is-built.md §1, §3).
#:
#: `tools/pack.py` restates it rather than importing it, the same way it restates the
#: claim-ref grammar above and for the same reason: the Packer may import nothing but
#: the stdlib and `config`. `tests/test_bank.py` reads both files and holds the two
#: copies equal, so a drift fails there rather than in a run where a date the Packer
#: accepts is a date the bank refuses.
MONTH_PATTERN = r"[0-9]{4}-(?:0[1-9]|1[0-2])"
ENDED_PATTERN = rf"(?:present|{MONTH_PATTERN})"

MONTH = re.compile(rf"^{MONTH_PATTERN}$")
ENDED = re.compile(rf"^{ENDED_PATTERN}$")

#: What `ended: present` reads as on the page. Capitalised, because it sits where a
#: capitalised month otherwise sits; `allocation.md` keeps the lowercase machine form.
PRESENT = "present"
PRESENT_LABEL = "Present"

#: Three letters for all twelve, no exceptions — `Sep`, not `Sept`. Uniform beats
#: idiomatic in a column of dates (docs/adr/0031-the-entry-header-is-built.md §2).
MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)

#: The grammar of a claim ref, `<entry-slug>/c<n>` — the citation that ties a Bullet,
#: a Skill and an allocation row back to one Claim. Unanchored fragments, so the line
#: regexes that read run artifacts can be composed from them; `CLAIM_ID` below is the
#: anchored form, for judging an id on its own. `tools/render.py` builds its three
#: readers from these.
#:
#: `tools/pack.py` restates both rather than importing them, because the Packer may
#: import nothing but the stdlib and `config`. Widening the slug alphabet is a
#: two-file edit.
ENTRY_SLUG_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._-]*"
CLAIM_ID_PATTERN = r"c[1-9][0-9]*"

CLAIM_ID = re.compile(rf"^{CLAIM_ID_PATTERN}$")
FIELD_LINE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):(?P<value>.*)$")
CLAIM_HEADING = re.compile(r"^##\s+(?P<id>.+?)\s*$")
BODY_LABEL = re.compile(
    r"^\*\*\s*(?P<label>assertion|evidence|situation|aggregate)\s*:?\s*\*\*\s*:?\s*", re.I
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

#: The `## lead` block's fields (docs/adr/0032-the-entry-arc.md §2) and a `##
#: merge <ids>` block's (docs/adr/0034-a-merged-bullet-coordinates.md Consequences)
#: — both borrow exactly `number`/`provenance` from a Claim, the same two fields
#: meaning the same thing.
LEAD_KEYS = ("number", "provenance")
MERGE_KEYS = ("number", "provenance")

#: `## merge c1+c3+c4` — 2 or 3 claim ids, `+`-joined, ADR 0034 §2-3's cap.
MERGE_HEADING = re.compile(
    rf"^merge\s+(?P<ids>{CLAIM_ID_PATTERN}(?:\+{CLAIM_ID_PATTERN}){{1,2}})$"
)


class BankError(Exception):
    """A malformed bank file. Always names the file and the line."""


def strip_comments(text: str) -> str:
    """Blank out HTML comments, keeping every newline so line numbers still hold.

    `templates/profile.example.md` tells the maker they may leave its comment block
    in place, so ignoring comments is part of the contract rather than a courtesy.
    """
    return HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def split_fields(line: str) -> list[tuple[str, str]]:
    """The `key: value` pairs on one line — normally one, occasionally two.

    `docs/adr/0005-bank-storage-format.md` prints `number: 40%  ·  provenance:
    measured` in its example of a Claim, so a maker who copies that example gets a
    file that parses. Splitting on the interpunct is the whole of the support: no
    other separator is honoured, and a line that does not match FIELD_LINE at all is
    still an error.
    """
    chunks = [chunk for chunk in line.split("·")] if "·" in line else [line]
    pairs = []
    for chunk in chunks:
        match = FIELD_LINE.match(chunk.strip())
        if not match:
            return []
        pairs.append((match.group("key").strip().lower(), match.group("value").strip()))
    return pairs


def parse_skills(value: str) -> list[str]:
    """`Go, Kafka, PostgreSQL` — or `[go, kafka]`, which the storage ADR prints."""
    return [item.strip() for item in value.strip("[]").split(",") if item.strip()]


class Claim:
    """One Claim: its id, its loose `key: value` lines, and its prose body.

    The atomic stored unit of the bank, and the unit truth attaches to — every
    rendered Bullet cites exactly one of these, and `render.py`'s Number-trace check
    resolves against it by id.
    """

    def __init__(
        self,
        entry: str,
        claim_id: str,
        fields: dict[str, str],
        assertion: str,
        evidence: str,
        line: int,
    ):
        self.entry = entry
        self.id = claim_id
        self.fields = fields
        self.assertion = assertion
        self.evidence = evidence
        self.line = line

    @property
    def ref(self) -> str:
        return f"{self.entry}/{self.id}"

    @property
    def number(self) -> str | None:
        """The stored number as human-readable text (`40%`), or None if qualitative."""
        return self.fields.get("number")

    @property
    def provenance(self) -> str | None:
        """`measured` or `estimated`. Rides with the number; None without one."""
        return self.fields.get("provenance")

    @property
    def confidence(self) -> str | None:
        """`uncertain` when the Confidence flag is raised, else None."""
        return self.fields.get("confidence")

    @property
    def needs_interview(self) -> bool:
        return self.fields.get("needs-interview") == "yes"

    @property
    def skills(self) -> list[str]:
        return parse_skills(self.fields.get("skills", ""))

    @property
    def unknown_keys(self) -> list[str]:
        """Keys this parser does not understand — surfaced, never dropped."""
        return [key for key in self.fields if key not in CLAIM_KEYS]

    @property
    def prose(self) -> str:
        """Everything the Claim says, for the trace check to resolve a number against.

        Assertion and evidence plus every field value, because a figure the maker
        wrote as scale texture in the evidence is as much a stored fact as the one
        in `number:` — and the Claim-level trace asks only that a rendered claim be
        present in, or entailed by, the entry's evidence.
        """
        return "\n".join([self.assertion, self.evidence, *self.fields.values()])


class Lead:
    """The entry arc's frame — one unbulleted lead line's source facts.

    Not a Claim: never scored, never cited, never a candidate for a slot
    (docs/adr/0032-the-entry-arc.md §1). `situation` and `aggregate` are each
    independently optional; `number`/`provenance` ride with `aggregate` exactly as
    they ride with a Claim's own number. `evidence` is the per-claim reading behind
    a stored sum (docs/adr/0036-the-closing-move.md §3), written the same shape a
    `## merge` block uses.
    """

    def __init__(
        self,
        fields: dict[str, str],
        situation: str,
        aggregate: str,
        evidence: str,
        line: int,
    ):
        self.fields = fields
        self.situation = situation
        self.aggregate = aggregate
        self.evidence = evidence
        self.line = line

    @property
    def number(self) -> str | None:
        return self.fields.get("number")

    @property
    def provenance(self) -> str | None:
        return self.fields.get("provenance")

    @property
    def unknown_keys(self) -> list[str]:
        return [key for key in self.fields if key not in LEAD_KEYS]


class Merge:
    """A stored sum over 2 or 3 Claims, spoken once at a Checkpoint and never re-asked.

    Not a Claim either: never scored, never ranked, never a candidate for a slot on
    its own (docs/adr/0034-a-merged-bullet-coordinates.md §5). `ids` is the heading's
    own declared order; lookup is by the SET, since a citation in `bullets.md` and
    the bank's own heading only ever need to agree on which claims, not their order.
    """

    def __init__(
        self, ids: tuple[str, ...], fields: dict[str, str], evidence: str, line: int
    ):
        self.ids = ids
        self.fields = fields
        self.evidence = evidence
        self.line = line

    @property
    def ref(self) -> str:
        return "+".join(self.ids)

    @property
    def number(self) -> str | None:
        return self.fields.get("number")

    @property
    def provenance(self) -> str | None:
        return self.fields.get("provenance")

    @property
    def unknown_keys(self) -> list[str]:
        return [key for key in self.fields if key not in MERGE_KEYS]


class Entry:
    """One Bank entry — the block that competes for the page, and its Claims in file order."""

    def __init__(
        self,
        slug: str,
        path: Path,
        frontmatter: dict[str, str],
        claims: list[Claim],
        lead: Lead | None = None,
        merges: list[Merge] | None = None,
    ):
        self.slug = slug
        self.path = path
        self.frontmatter = frontmatter
        self.claims = claims
        self.lead = lead
        self.merges = merges or []

    def merge(self, ids) -> Merge | None:
        """The stored `## merge` block over exactly this set of claim ids, if any."""
        key = frozenset(ids)
        for merge in self.merges:
            if frozenset(merge.ids) == key:
                return merge
        return None

    @property
    def type(self) -> str:
        """What routes the Entry to a section of the page — one of `ENTRY_TYPES`."""
        return self.frontmatter["type"]

    @property
    def supporting(self) -> bool:
        """Whether this Entry is one of the three that never compete.

        The single test everything else asks. A supporting entry is absent from the
        Score table by construction, so nothing downstream of the seam has to know
        this — it is the bank-side readers (`bankcheck.py`, the Renderer's row
        builder) that do
        (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §2).
        """
        return self.type in SUPPORTING_TYPES

    @property
    def title(self) -> str:
        return self.frontmatter["title"]

    @property
    def org(self) -> str:
        return self.frontmatter.get("org", "")

    @property
    def location(self) -> str:
        return self.frontmatter.get("location", "")

    @property
    def stack(self) -> str:
        """A project's technologies, as written — `Python, LaTeX, Claude Code`."""
        return self.frontmatter.get("stack", "")

    @property
    def link(self) -> str:
        """A project's link without its scheme — `github.com/you/thing`."""
        return self.frontmatter.get("link", "")

    @property
    def started(self) -> str:
        """`YYYY-MM`, validated. The machine form; nothing typesets it."""
        return self.frontmatter["started"]

    @property
    def ended(self) -> str:
        """`YYYY-MM` or the literal `present`, validated.

        The bank owns this field and `scores.md` carries a copy of it, which
        `render.py` checks against this one before it will render
        (docs/adr/0031-the-entry-header-is-built.md §4).
        """
        return self.frontmatter["ended"]

    @property
    def display_dates(self) -> str:
        """The Entry header's date string, built: `Jan 2026 -- Jul 2026`.

        THE ONE HOUSE FORMAT, and the reason `dates:` stopped being prose. Two entries
        cannot disagree about the shape of a date because neither of them writes one —
        `Jan`/`Jul` above `June`/`July` was four lines apart on the page this came from
        (docs/adr/0031-the-entry-header-is-built.md §2).

        The `--` is the Template's existing en-dash and is unchanged.
        """
        return f"{month_label(self.started)} -- {month_label(self.ended)}"

    @property
    def row_dates(self) -> str:
        """A supporting row's date string, built the same way — with one collapse.

        WHERE `started` AND `ended` ARE THE SAME MONTH, THIS IS THAT ONE MONTH. A
        credential with no expiry is issued and held, so the bank writes the issue
        month into both fields and the row prints `Mar 2025` rather than
        `Mar 2025 -- Mar 2025`, which is a range to itself and reads as a mistake
        (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §3).

        Stated as a rule about the two fields rather than about the `certification`
        type, so it has no type to special-case: a one-month responsibility collapses
        for the same reason. `display_dates` is deliberately NOT given the same
        collapse — an Entry header's date column is read down a page and its shape is
        the thing `0031` fixed.
        """
        if self.started == self.ended:
            return month_label(self.started)
        return self.display_dates

    @property
    def unknown_keys(self) -> list[str]:
        return [key for key in self.frontmatter if key not in ENTRY_KEYS]

    def claim(self, claim_id: str) -> Claim | None:
        for claim in self.claims:
            if claim.id == claim_id:
                return claim
        return None


def parse_entry(text: str, slug: str, path: Path) -> Entry:
    """One Entry file: frontmatter, then Claims, at most one `## lead`, any `## merge`.

    A Claim heading is `## c<n>`; the two non-Claim sections are `## lead` — the
    entry arc's frame — and `## merge <ids>` — a stored sum over 2 or 3 of this
    entry's own Claims. Neither is a Claim, and neither may share a claim
    heading's `c<n>` shape (`docs/adr/0032-the-entry-arc.md`,
    `docs/adr/0034-a-merged-bullet-coordinates.md`).
    """
    lines = strip_comments(text).splitlines()
    frontmatter, index = parse_frontmatter(lines, path)
    validate_entry_frontmatter(frontmatter, path)

    claims: list[Claim] = []
    lead: Lead | None = None
    pending_merges: list[Merge] = []
    seen: dict[str, int] = {}
    while index < len(lines):
        line = lines[index]
        heading = CLAIM_HEADING.match(line)
        if heading is None:
            if line.strip():
                raise BankError(
                    f"{path}:{index + 1}: this line sits outside any section — a section "
                    f"heading is `## c<n>`, `## lead` or `## merge <ids>` and nothing else "
                    f"belongs between them: {line.strip()}"
                )
            index += 1
            continue

        raw_id = heading.group("id")
        end = index + 1
        while end < len(lines) and not CLAIM_HEADING.match(lines[end]):
            end += 1
        block_lines = lines[index + 1 : end]
        heading_line = index + 1

        if raw_id == "lead":
            if lead is not None:
                raise BankError(
                    f"{path}:{heading_line}: a second `## lead` block — an Entry carries "
                    f"at most one"
                )
            lead = parse_lead(block_lines, path, heading_line)
            index = end
            continue

        merge_match = MERGE_HEADING.fullmatch(raw_id)
        if merge_match:
            ids = tuple(merge_match.group("ids").split("+"))
            if len(set(ids)) != len(ids):
                raise BankError(
                    f"{path}:{heading_line}: `## {raw_id}` repeats a claim id"
                )
            pending_merges.append(parse_merge(ids, block_lines, path, heading_line))
            index = end
            continue

        claim_id = raw_id
        if not CLAIM_ID.fullmatch(claim_id):
            raise BankError(
                f"{path}:{heading_line}: heading `## {claim_id}` is not `## c<n>`, "
                f"`## lead` or `## merge <ids>`"
            )
        if claim_id in seen:
            raise BankError(
                f"{path}:{heading_line}: claim {claim_id} is already defined on line "
                f"{seen[claim_id]}"
            )
        seen[claim_id] = heading_line
        claims.append(parse_claim(block_lines, slug, claim_id, path, heading_line))
        index = end

    if not claims:
        raise BankError(f"{path}: no claims — an Entry file with no `## c<n>` section is empty")

    claim_ids = {claim.id for claim in claims}
    merges: list[Merge] = []
    seen_sets: set[frozenset] = set()
    for merge in pending_merges:
        unknown = [claim_id for claim_id in merge.ids if claim_id not in claim_ids]
        if unknown:
            raise BankError(
                f"{path}:{merge.line}: `## merge {merge.ref}` cites {unknown[0]}, which is "
                f"not a claim in this entry"
            )
        key = frozenset(merge.ids)
        if key in seen_sets:
            raise BankError(
                f"{path}:{merge.line}: `## merge {merge.ref}` duplicates an earlier merge "
                f"over the same claims"
            )
        seen_sets.add(key)
        merges.append(merge)

    return Entry(slug, path, frontmatter, claims, lead, merges)


def _parse_fields_and_body(
    lines: list[str],
    path: Path,
    heading_line: int,
    where: str,
    body_hint: str = "its body",
) -> tuple[dict[str, str], dict[str, str]]:
    """The loose `key: value` lines above a body, then the body's labelled parts.

    Shared by a Claim, the lead and a merge block — all three are `key: value`
    lines followed by one or more `**Label:**` sections, and only which labels are
    legal differs between them.
    """
    fields: dict[str, str] = {}
    body: dict[str, list[str]] = {}
    label: str | None = None

    for offset, line in enumerate(lines):
        number = heading_line + offset + 1
        marker = BODY_LABEL.match(line)
        if marker:
            label = marker.group("label").lower()
            if label in body:
                raise BankError(f"{path}:{number}: {where} has a second `{label}` body")
            body[label] = [line[marker.end() :].strip()]
            continue
        if label is not None:
            body[label].append(line)
            continue
        if not line.strip():
            continue
        pairs = split_fields(line)
        if not pairs:
            raise BankError(
                f"{path}:{number}: {where} takes `key: value` lines above {body_hint}, and "
                f"this is neither: {line.strip()}"
            )
        for key, value in pairs:
            if key in fields:
                raise BankError(f"{path}:{number}: {where} repeats `{key}`")
            fields[key] = value

    return fields, {label: "\n".join(part).strip() for label, part in body.items()}


def parse_frontmatter(lines: list[str], path: Path) -> tuple[dict[str, str], int]:
    """The `---` fenced `key: value` block, and the line the body starts on.

    Deliberately knows nothing about Entries: `render.py` reads `bank/profile.md`
    with this too, and the **Static profile** carries different keys entirely. What
    both files share is the shape — a fence at the top, loose pairs inside — and
    sharing the reader is what keeps them from drifting into two dialects of it.
    """
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or lines[start].strip() != "---":
        raise BankError(f"{path}: no `---` frontmatter block at the top of the file")

    fields: dict[str, str] = {}
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            return fields, index + 1
        if not line.strip():
            continue
        pairs = split_fields(line)
        if not pairs:
            raise BankError(
                f"{path}:{index + 1}: frontmatter takes `key: value` lines and this is "
                f"not one: {line.strip()}"
            )
        fields.update(pairs)
    raise BankError(f"{path}: the `---` frontmatter block is never closed")


def month_label(month: str) -> str:
    """`2026-01` -> `Jan 2026`, and `present` -> `Present`.

    Assumes a value `MONTH`/`ENDED` has already accepted; the frontmatter check runs
    before anything asks for a display string.
    """
    if month == PRESENT:
        return PRESENT_LABEL
    year, number = month.split("-")
    return f"{MONTH_NAMES[int(number) - 1]} {year}"


def validate_entry_frontmatter(fields: dict[str, str], path: Path) -> None:
    """The scalars an Entry header cannot be typeset without, plus its type and dates."""
    for key in REQUIRED_ENTRY_KEYS:
        if fields.get("type") == "project" and key in PROJECT_OPTIONAL_KEYS:
            continue
        if not fields.get(key):
            if "dates" in fields and key in ("started", "ended"):
                # The one migration this schema has had. A `dates:` line is a file
                # written against the old shape, so say that rather than reporting
                # two missing keys the maker never knew about
                # (docs/adr/0031-the-entry-header-is-built.md §1).
                raise BankError(
                    f"{path}: frontmatter carries `dates: {fields['dates']}`, which nothing "
                    f"reads any more. Replace it with `started:` and `ended:`, both "
                    f"`YYYY-MM` (`ended` also takes `present`) — the header's date string "
                    f"is composed from them now, so the page has one date format instead "
                    f"of one per entry"
                )
            raise BankError(f"{path}: frontmatter is missing `{key}`")
    if fields["type"] not in ENTRY_TYPES:
        raise BankError(
            f"{path}: frontmatter `type: {fields['type']}` is not one of "
            + ", ".join(f"`{known}`" for known in ENTRY_TYPES)
        )
    link = fields.get("link", "")
    if link.startswith(("http://", "https://")):
        raise BankError(
            f"{path}: frontmatter `link: {link}` carries its scheme — write it as the "
            f"page should show it, `github.com/you/thing`; the link target adds https://"
        )
    if LINK_UNSAFE.search(link):
        raise BankError(
            f"{path}: frontmatter `link: {link}` contains a character that is not "
            f"URL-safe in a LaTeX link target (spaces, % # & $ ^ \\ {{ }})"
        )
    if not MONTH.fullmatch(fields["started"]):
        raise BankError(
            f"{path}: frontmatter `started: {fields['started']}` is not `YYYY-MM` — the "
            f"month is two digits, `2026-01` and never `2026-1`"
        )
    if not ENDED.fullmatch(fields["ended"]):
        raise BankError(
            f"{path}: frontmatter `ended: {fields['ended']}` is neither `YYYY-MM` nor "
            f"`present` — an entry that has not finished writes the word"
        )
    if fields["ended"] != PRESENT and fields["started"] > fields["ended"]:
        raise BankError(
            f"{path}: frontmatter says `started: {fields['started']}` and `ended: "
            f"{fields['ended']}`, which ends before it begins"
        )


def parse_claim(
    lines: list[str], slug: str, claim_id: str, path: Path, heading_line: int
) -> Claim:
    """One `## c<n>` section: its loose fields, then `**Assertion:**` and `**Evidence:**`."""
    fields, body = _parse_fields_and_body(
        lines, path, heading_line, claim_id, "its `**Assertion:**`"
    )
    extra = set(body) - {"assertion", "evidence"}
    if extra:
        raise BankError(
            f"{path}:{heading_line}: {claim_id} has a `**{sorted(extra)[0].title()}:**` "
            f"body, which a claim does not take — only Assertion and Evidence"
        )
    claim = Claim(
        slug,
        claim_id,
        fields,
        assertion=body.get("assertion", ""),
        evidence=body.get("evidence", ""),
        line=heading_line,
    )
    validate_claim(claim, path)
    return claim


def parse_lead(lines: list[str], path: Path, heading_line: int) -> Lead:
    """The `## lead` block: the entry arc's frame (docs/adr/0032-the-entry-arc.md §2).

    `situation:` and `aggregate:` are each independently optional — an entry may
    open on a condition and close on nothing, or the reverse (§5). `number` and
    `provenance` ride with `aggregate` exactly as they ride with a Claim's own
    number: neither may appear without the other, and neither may appear without
    the sentence it summarises.
    """
    fields, body = _parse_fields_and_body(lines, path, heading_line, "the lead")
    extra = set(body) - {"situation", "aggregate", "evidence"}
    if extra:
        raise BankError(
            f"{path}:{heading_line}: the lead has a `**{sorted(extra)[0].title()}:**` "
            f"body, which a lead does not take — only Situation, Aggregate and Evidence"
        )
    situation, aggregate = body.get("situation", ""), body.get("aggregate", "")
    evidence = body.get("evidence", "")
    if not situation and not aggregate:
        raise BankError(
            f"{path}:{heading_line}: `## lead` has neither a **Situation:** nor an "
            f"**Aggregate:** — an empty lead block is not a block"
        )
    number, provenance = fields.get("number"), fields.get("provenance")
    if number and not provenance:
        raise BankError(
            f"{path}:{heading_line}: the lead carries `number: {number}` with no "
            f"`provenance` — the pair rides together"
        )
    if provenance and not number:
        raise BankError(
            f"{path}:{heading_line}: the lead carries `provenance: {provenance}` with no "
            f"`number` — the pair rides together"
        )
    if provenance and provenance not in PROVENANCE_TIERS:
        raise BankError(
            f"{path}:{heading_line}: the lead has `provenance: {provenance}`, which is "
            f"neither `measured` nor `estimated`"
        )
    if number and not aggregate:
        raise BankError(
            f"{path}:{heading_line}: the lead carries `number: {number}` with no "
            f"**Aggregate:** — a number needs the sentence it summarises"
        )
    if aggregate and not number:
        raise BankError(
            f"{path}:{heading_line}: the lead has an **Aggregate:** with no `number` — "
            f"the pair rides together"
        )
    return Lead(fields, situation, aggregate, evidence, heading_line)


def parse_merge(
    ids: tuple[str, ...], lines: list[str], path: Path, heading_line: int
) -> Merge:
    """A `## merge <ids>` block: a stored sum, spoken once at a Checkpoint.

    (docs/adr/0034-a-merged-bullet-coordinates.md §5). Unlike the lead, `number`
    and `provenance` are not optional here — a merge block exists only because a
    sum was vouched for, so a block with neither is not one.
    """
    ref = "+".join(ids)
    fields, body = _parse_fields_and_body(lines, path, heading_line, f"`## merge {ref}`")
    extra = set(body) - {"evidence"}
    if extra:
        raise BankError(
            f"{path}:{heading_line}: `## merge {ref}` has a "
            f"`**{sorted(extra)[0].title()}:**` body, which a merge block does not take "
            f"— only Evidence"
        )
    evidence = body.get("evidence", "")
    if not evidence:
        raise BankError(
            f"{path}:{heading_line}: `## merge {ref}` has no **Evidence:** — a stored "
            f"sum needs the reading behind it"
        )
    number, provenance = fields.get("number"), fields.get("provenance")
    if not number or not provenance:
        raise BankError(
            f"{path}:{heading_line}: `## merge {ref}` needs both `number` and "
            f"`provenance` — a merge block only exists to hold a vouched sum"
        )
    if provenance not in PROVENANCE_TIERS:
        raise BankError(
            f"{path}:{heading_line}: `## merge {ref}` has `provenance: {provenance}`, "
            f"which is neither `measured` nor `estimated`"
        )
    return Merge(ids, fields, evidence, heading_line)


def validate_claim(claim: Claim, path: Path) -> None:
    """The few shapes that would make a Claim quietly mean something else.

    Deliberately short. Shallowness is judged by a person (`bank-audit`), not here,
    and an unknown key is surfaced rather than refused. What is refused is a Claim
    the Number-trace check would read wrongly — a number whose tier is missing or
    misspelt renders flat and passes every lint, which is the one failure
    `docs/adr/0015-numbers-at-ingestion.md` §3 calls undetectable forever.
    """
    where = f"{path}:{claim.line}: {claim.id}"
    if not claim.assertion:
        raise BankError(f"{where} has no `**Assertion:**` — every Claim asserts something")

    number, provenance = claim.number, claim.provenance
    if number and not provenance:
        raise BankError(
            f"{where} carries `number: {number}` with no `provenance` — the pair rides "
            f"together, and a tier-less number renders flat and traces clean"
        )
    if provenance and not number:
        raise BankError(
            f"{where} carries `provenance: {provenance}` with no `number` — the pair "
            f"rides together"
        )
    if provenance and provenance not in PROVENANCE_TIERS:
        raise BankError(
            f"{where} has `provenance: {provenance}`, which is neither `measured` nor "
            f"`estimated`"
        )
    if claim.confidence is not None and claim.confidence != "uncertain":
        raise BankError(
            f"{where} has `confidence: {claim.confidence}` — the flag is written "
            f"`confidence: uncertain` when raised and omitted otherwise"
        )
    if "needs-interview" in claim.fields and not claim.needs_interview:
        raise BankError(
            f"{where} has `needs-interview: {claim.fields['needs-interview']}` — the mark "
            f"is written `needs-interview: yes` when set and omitted otherwise"
        )
    if "skills" in claim.fields and not claim.skills:
        raise BankError(f"{where} has an empty `skills` line — omit it instead")


def load_bank(bank_dir: Path) -> dict[str, Entry]:
    """Every Entry under `bank/`, keyed by slug — the five folders of `TYPE_FOLDERS`.

    The filename slug **is** the Entry id (`0005` §2), and the folder is the Entry
    type. Both say the type, so both must agree: a `job` filed under `projects/`
    would route to the wrong section of the résumé and nothing downstream could tell.

    The slug is unique **across all five folders**, not within one. It is the Entry
    id, `bullets.md` and `scores.md` address entries by it alone, and a
    `certification` sharing a slug with a `job` would make a citation ambiguous —
    which is exactly the failure the check below refuses, unchanged from when there
    were two folders
    (docs/adr/0045-a-supporting-section-is-earned-or-paid-for-out-of-the-room.md §1).

    A folder that does not exist is an empty folder, not an error: a bank with no
    certifications in it has no `bank/certifications/`, and an empty bank parses.
    """
    entries: dict[str, Entry] = {}
    for type_, folder in TYPE_FOLDERS.items():
        for path in sorted((bank_dir / folder).glob("*.md")):
            slug = path.stem
            if slug in entries:
                raise BankError(
                    f"{path}: the slug `{slug}` is also {entries[slug].path} — the slug is "
                    f"the Entry id, so two files cannot share one"
                )
            entry = parse_entry(path.read_text(encoding="utf-8"), slug, path)
            if entry.type != type_:
                raise BankError(
                    f"{path}: frontmatter says `type: {entry.type}` but the file sits in "
                    f"bank/{folder}/, which is the `{type_}` half of the bank"
                )
            entries[slug] = entry
    return entries
