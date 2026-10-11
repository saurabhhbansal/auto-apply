---
type: project
title: FeedForge
org: Personal project
location: Open source
started: 2023-01
ended: 2023-03
domain: developer tools
---

## c1
number: 200
provenance: measured
skills: Go, RSS, Concurrency

**Assertion:** Built a feed aggregator that fans out to 200 sources on a worker pool.

**Evidence:** My reader was fetching feeds one after another and taking most of a
minute. A bounded worker pool with a per-host limiter brought it under five seconds
without getting me rate-limited. Two hundred is the size of my own subscription list,
counted from the OPML file.

## c2
skills: SQLite, Full-text search

**Assertion:** Added full-text search over archived posts so the archive is worth keeping.

**Evidence:** The archive was a folder nobody opened, because finding the post you
half-remembered meant grep over HTML. SQLite's FTS index over the extracted text made
it a search box. I use it most weeks, which is the only usage number this project has.

## c3
number: 15%
provenance: estimated
skills: Go, HTTP, Caching

**Assertion:** Saved ~15% of bandwidth by honouring conditional requests on every feed fetch.

**Evidence:** The fetcher ignored ETag and Last-Modified and re-downloaded unchanged
feeds every cycle, which is rude to the servers and slow for me. Sending the validators
means most fetches now come back empty. The 15% is my read of the traffic graph on the
home router, not a measurement of the process.

## c4
skills: Testing, Go

**Assertion:** Recorded real feeds as fixtures so the parser is tested against malformed ones.

**Evidence:** Real feeds are broken in ways no specification predicts, and every bug
report was a feed I could not reproduce. Saving each reported feed as a fixture turned
the bug reports into a regression suite. The parser has not regressed on a fixed feed since.
