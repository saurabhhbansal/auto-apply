---
type: job
title: Software Engineer
org: Atlas Logistics
location: Bengaluru, India
started: 2020-03
ended: 2022-12
domain: logistics
---

## c1
number: 34
provenance: measured
skills: PostgreSQL, Migrations, Terraform

**Assertion:** Split 34 services off one shared Postgres instance onto per-service schemas.

**Evidence:** Every service shared one database and one connection pool, so a slow
report in the billing service throttled dispatch. I counted the services off the
connection log, wrote the cutover runbook, and ran it service by service over two
quarters with no scheduled downtime. The failure we were bracing for — a service
holding a cross-schema join nobody knew about — happened twice, and both were caught
in staging because the runbook made every service prove its queries first.

## c2
number: 8
provenance: measured
skills: Kafka, Go, Event-driven architecture

**Assertion:** Replaced 8 polling integrations with a Kafka event stream carriers publish to.

**Evidence:** Each carrier integration polled a status endpoint every minute, which
made shipment tracking a minute stale at best and hammered partners who charged per
call. The stream let carriers push, and the tracking page went to seconds. Two carriers
refused to push, so the poller survives for them behind the same event interface — which
turned out to be the design decision that mattered, because consumers never learned
which carriers were which.

## c3
skills: Mentoring, Code review, Technical writing

**Assertion:** Drafted the service checklist every new backend service at Atlas is reviewed against.

**Evidence:** New services arrived without health endpoints, without dashboards, and
occasionally without a runbook, and the review that caught it was whoever happened to
be on the pull request. I wrote down what the good services already did, argued it
through two design reviews, and it became the checklist. What changed is that the
argument stopped being re-had per service.

## c4
number: 3x
provenance: estimated
skills: Redis, Caching, Go

**Assertion:** Put a read-through cache on route lookups, ~3x faster on the dispatch board.

**Evidence:** The board recomputed every route on every poll, and dispatchers had
started keeping a second tab open because the first was always loading. A read-through
cache keyed by route version took the recompute off the request path. The 3x is what
it felt like next to the old page and what dispatchers said; we never put a timer on it.
