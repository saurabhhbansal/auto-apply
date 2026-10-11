---
type: job
title: Junior Software Engineer
org: Kestrel Media
location: Mumbai, India
started: 2016-07
ended: 2017-07
domain: media
---

## c1
number: 4
provenance: measured
skills: Python, Flask, REST

**Assertion:** Landed the internal API 4 editorial tools were rewritten against.

**Evidence:** Every editorial tool talked to the CMS database directly, so a column
rename meant finding whoever owned each tool. One read API in front of it let the tools
stop knowing the schema. Four is the number that had migrated by the time I left; the
last two were still on direct queries.

## c2
skills: JavaScript, Accessibility

**Assertion:** Made the newsroom publishing tool usable with a keyboard alone.

**Evidence:** A sub-editor who could not use a mouse comfortably was doing her whole
day through a screen magnifier and a lot of patience. I sat with her for an afternoon,
listed what was unreachable, and fixed it over a sprint. It is the smallest thing on
this list and the one somebody thanked me for by name.

## c3
skills: MySQL, Debugging

**Assertion:** Traced the duplicate-article bug to a retry with no idempotency key.

**Evidence:** Articles occasionally published twice and the editors had assumed
double-clicking was the cause. The publish call retried on timeout and the second
attempt inserted a second row. Keying the insert on the draft id ended it. I was six
months in and it was the first time I found something the seniors had shrugged at.
