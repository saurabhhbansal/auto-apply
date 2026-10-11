---
type: project
title: ledger-cli
org: Personal project
location: Open source
started: 2024-02
ended: 2024-06
domain: developer tools
---

## c1
number: 900
provenance: measured
skills: Rust, CLI design, Parsing

**Assertion:** Wrote a plain-text double-entry ledger tool that parses 900 entries in under a second.

**Evidence:** I wanted my own accounts in a file I could diff, and the existing tools
either wanted a database or a subscription. The parser is hand-written rather than
generated, which is why the error messages can point at the column. The 900 is my own
file, timed with the shell's own timer before and after the parser rewrite.

## c2
needs-interview: yes
skills: Rust, Property-based testing

**Assertion:** Property tests generate random ledgers and assert the books balance after every run.

**Evidence:** Added at a checkpoint; not yet excavated.

## c3
skills: Documentation, Open source

**Assertion:** Published the tutorial that turns a new user's first ledger file into a working report.

**Evidence:** Two people opened issues that were both "I do not know what to type
first", so the fix was not code. The tutorial walks one real month end to end. The
issues stopped, and the next three issues were about features instead.

## c4
number: 2x
provenance: estimated
skills: Rust, Profiling

**Assertion:** Indexed accounts on first read, making report generation about ~2x faster.

**Evidence:** Every report walked the whole entry list per account, so the run time
grew with accounts times entries. Building an account index once at load made it linear.
Twice is the shape of the improvement on my own file; I did not benchmark it properly.
