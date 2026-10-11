---
type: job
title: Backend Engineer
org: Orbit Analytics
location: Remote
started: 2017-08
ended: 2018-05
domain: analytics
---

## c1
number: 60%
provenance: estimated
skills: Go, ClickHouse, Query optimisation

**Assertion:** Dropped dashboard query cost ~60% by moving aggregates from Postgres to ClickHouse.

**Evidence:** Dashboards ran group-bys over a year of events in Postgres and the
database spent most of its day serving them. Moving the aggregate path to ClickHouse
and keeping Postgres for the transactional side made the dashboards feel instant. The
60% is read off the instance downsizing that followed rather than off a query benchmark.

## c2
skills: Python, ETL, Data modelling

**Assertion:** Designed the event schema every downstream analytics job still reads today.

**Evidence:** Events arrived as free-form JSON, so every consumer wrote its own parser
and each one broke differently when a producer changed a key. I ran a week of interviews
with the three consuming teams, wrote a versioned schema with a required envelope, and
enforced it at the ingest edge. New event types stopped being a negotiation.

## c3
skills: AWS, Terraform, CI/CD

**Assertion:** Moved the deploy from a hand-run script to Terraform and a pipeline anyone can run.

**Evidence:** Deploys were a shell script on one engineer's laptop with credentials
that lived nowhere else, so releases waited on that person being awake. Codifying the
infrastructure and putting the deploy behind a pipeline is what let the rest of us ship,
and it removed the weekend where that engineer was on holiday and nothing could go out.
