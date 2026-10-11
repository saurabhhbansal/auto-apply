"""Reading `allocation.md` back, for the tests of both tools that touch it.

The Packer writes it and the Renderer reads it, so both test files parse it here
rather than keeping two copies that could drift apart.

A plain module rather than fixtures: these are functions over a string, with nothing
to set up or tear down. pytest collects `test_*.py`, so nothing here is collected.
"""

from __future__ import annotations

import re


def section(allocation: str, title: str) -> str:
    """The body of a `## <title>` section, up to the next `## `."""
    match = re.search(
        rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", allocation, re.M | re.S
    )
    assert match, f"allocation.md has no '## {title}' section:\n{allocation}"
    return match.group(1)


def placed(allocation: str) -> list[tuple[str, list[str]]]:
    """The placed entries in page order, as `[(entry-slug, [unit refs])]`.

    A unit ref is one claim id, or a `+`-joined merge group exactly as
    `bullets.md` cites it (`docs/adr/0034-a-merged-bullet-coordinates.md`).
    """
    entries: list[tuple[str, list[str]]] = []
    for line in section(allocation, "Placed").splitlines():
        heading = re.match(r"^### (\S+)", line)
        if heading:
            entries.append((heading.group(1), []))
            continue
        bullet = re.match(r"^- (\S+)/(c\d+(?:\+c\d+)*)", line)
        if bullet:
            assert entries, f"a bullet before any entry heading: {line}"
            assert bullet.group(1) == entries[-1][0], (
                f"bullet {line!r} sits under entry {entries[-1][0]}"
            )
            entries[-1][1].append(bullet.group(2))
    return entries
