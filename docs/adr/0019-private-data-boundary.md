# The private-data boundary: `bank/` and `runs/` keep their own git, and never this repo's

**Status:** accepted

## Context

The v1 decisions were taken for a private single-user repo, and two of them put the maker's
own data under the project's version control. The **bank storage format**
(`docs/adr/0005-bank-storage-format.md`) is markdown-in-git; the **run folder**
(`SPEC.md` §"Tailoring — selection locus" item 9) is "committed to git in full", which is what
buys the property that a re-run overwrites in place and `git diff` says what changed. The
`tailor` skill's last step is literally `git add runs/<jd-slug> && git commit`.

That was sound while the repo was private and stayed private. The intent has changed: this
repo is meant to be open-sourced. Under that intent the same two decisions publish
`bank/profile.md` — real name, phone, email, links — plus every run folder, each of which
carries the same header inside `resume.tex` and `resume.pdf`, along with the maker's whole
career history in their own words and an honest account of where it is thin.

The naive fix is to gitignore both directories. It works, and it silently spends something:
ignoring `runs/` means a re-run overwrites the previous résumé and gap report with **nothing
to diff against**, which is the exact property SPEC §9 chose the slug-per-run design to get.
The bank loses the same thing at ingestion, where `/ingest` deliberately writes as it goes and
leans on the maker reading `git diff` before committing.

## Decision

### The boundary is the repository, not version control

`bank/` and `runs/` are ignored by this repo wholesale — including their contents' inner
`.git` — and **each is its own git repository** on the maker's machine, with no remote.

This keeps both halves. The project repo can go public without carrying a line of the maker's
data or one commit of its history. The maker keeps `git diff` on a re-run, keeps the
write-as-you-go safety net at ingestion, and keeps a run folder that is a complete record of
itself. What they lose is the *single* history — a run and the tool version that produced it
are now two repositories apart. That is the cost, and it is small: the run folder already
records the run's own reasoning in full, which is what the "complete record of itself"
property was ever about.

**No remote is the whole enforcement.** Not a hook, not a check in `render.py` — an inner
repo with no remote cannot be pushed, and the outer repo cannot see the files. Anything more
is a mechanism guarding against a mistake the layout does not permit.

### The `.gitkeep` files stay tracked

`bank/.gitkeep`, `bank/jobs/.gitkeep`, `bank/projects/.gitkeep` and `runs/.gitkeep` remain in
this repo, because git cannot track an empty directory and without them the directories do not
ship at all. That is not cosmetic: the README's first setup step is
`cp templates/profile.example.md bank/profile.md`, which fails outright — *"cannot create
regular file: No such file or directory"* — on a clone that has no `bank/`.

The ignore rules are written as an exclude-everything with those four re-included, which also
means a new file type dropped into either directory is ignored by default — the correct
direction for the failure to fall.

*(This ADR first claimed the `.gitkeep` files also keep `bankcheck.py` reporting "your bank is
empty" rather than "no such directory". They do not: run against a checkout with no `bank/` at
all, `bankcheck.py` prints `bank parses` and exits 0. That is a defect in `bankcheck.py` — a
missing bank should not read as a passing one — and it is unrelated to this decision.)*

### History was rewritten, once

One run — `runs/zs-btsa/` — had reached the remote before this decision. It was dropped by
rebase and the branch force-pushed, so the public history starts with no maker data in it
rather than with a deletion commit that anyone can `git show`. This is a single-user repo with
no other clones, which is the only reason a rewrite is cheap; it is not a precedent.

## Consequences

- `SPEC.md` §"Tailoring — selection locus" item 9 and the `tailor` skill's step 8 are amended:
  the run folder is still committed in full, to `runs/`'s own repo (`git -C runs …`).
- The bank edit that **checkpoint write-back** leaves for the maker to review
  (`docs/adr/0008-checkpoint-write-back.md`) is now reviewed and committed in `bank/`'s repo.
  The reason it is not part of the run's commit is unchanged, and now also structural.
- `docs/adr/0005-bank-storage-format.md` keeps its "markdown-in-git" rationale intact — this
  changes *which* git, not whether.
- A contributor cloning the open-source repo gets no bank and no runs, which is right: there
  is nothing generic in either. `templates/profile.example.md` is the entry point, and the
  README says to copy it.
- Anyone adopting this repo inherits the boundary by default, rather than discovering it the
  first time they push their own résumé to a public remote.
