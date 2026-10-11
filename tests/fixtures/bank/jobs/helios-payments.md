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

**Assertion:** Cut checkout p99 latency 40% by batching commits in the order-ingest consumer.

**Evidence:** The consumer committed offsets per message, so every checkout paid a
round trip to the broker while holding the payment row lock. Batching commits to a
50ms window and moving the lock release ahead of the commit took the p99 from 1.4s to
830ms on the Grafana panel we watched through the December peak. The batch window was
the third thing we tried; a bigger connection pool and a read replica both moved the
mean and left the tail alone.

## c2
number: 30%
provenance: estimated
skills: PostgreSQL, SQL, Airflow

**Assertion:** Took nightly settlement reconciliation down ~30% by rewriting it as partitioned reads.

**Evidence:** Reconciliation walked one day of ledger entries in a single transaction
and had started overrunning into business hours, which meant support answered "the
numbers are not final yet" every morning. Partitioning the walk by processor and
running the partitions concurrently brought it back inside its window. Nobody clocked
the before and after — the number is my read of when the job started finishing.

## c3
skills: Distributed systems, On-call, Incident response

**Assertion:** Own the payments ledger end to end, from schema design through on-call and incident review.

**Evidence:** I wrote the double-entry schema the ledger runs on, carry the pager for
it, and run the review after anything the ledger touched goes wrong. The scope was not
handed to me as a title; the previous owner left and I was the one who understood the
reconciliation path, so it stayed with me. What changed is that ledger corrections stopped
being a spreadsheet somebody kept privately and became a reviewed change with a paper trail.

## c4
number: 12
provenance: estimated
confidence: uncertain
skills: Go, gRPC, API design

**Assertion:** Shaped the payout API that ~12 internal services now integrate against.

**Evidence:** The payout path had grown three callers with three different shapes of
request, so I took the union, wrote it as one gRPC service, and migrated the callers.
Twelve is what I remember from the service registry when I left the team; it could have
been ten. What I am sure of is that every payout in the company goes through that one
door now, and that adding a payout type stopped being a change in three codebases.
