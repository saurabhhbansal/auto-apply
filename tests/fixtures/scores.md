# Scores: the fixture bank against a backend-platform JD

A Score table over `tests/fixtures/bank/`, written the way the `tailor` skill writes
one: every Claim in the bank gets a row — including the zeros, because the Omission
view needs the losers — scored against the Fit rubric's anchors rather than against
the other claims, each with a one-line reason.

The JD it is scored against is not committed, and does not need to be: a Score table
is Opus's judgement *after* reading one, and everything downstream reads only this.
Take it as a backend platform role asking for Go, Kafka, Postgres at scale, service
ownership and on-call, with observability and infrastructure-as-code preferred.

Used by `tests/test_render.py` to drive the real pipeline — `pack.py` writes the
allocation, `render.py` renders it — so that the two tools are held to each other's
formats and not merely to a test's idea of them.

| entry | claim | type | ended | score | width | reason |
|---|---|---|---|---|---|---|
| helios-payments | c1 | job | present | 1.00 | 1 | The queue-consumer rewrite in Go and Kafka the first must-have describes, on the same hot path |
| helios-payments | c2 | job | present | 0.70 | 1 | Postgres work at real scale, adjacent to the must-have rather than the stream processing asked for |
| helios-payments | c3 | job | present | 0.70 | 1 | Ownership and on-call for a payments system, which the scope paragraph asks for by name |
| helios-payments | c4 | job | present | 0.85 | 1 | Service API design in Go for internal consumers, close to the platform-API must-have |
| atlas-logistics | c1 | job | 2022-12 | 0.85 | 1 | A 34-service Postgres migration, the second must-have head-on but two roles ago |
| atlas-logistics | c2 | job | 2022-12 | 0.90 | 1 | Kafka event-driven integration, directly evidencing the streaming must-have |
| atlas-logistics | c3 | job | 2022-12 | 0.50 | 1 | Standards and review work, one hop from the platform-stewardship line |
| atlas-logistics | c4 | job | 2022-12 | 0.70 | 1 | Read-through caching for latency, adjacent to the performance must-have |
| northwind-retail | c1 | job | 2020-02 | 0.50 | 1 | Checkout work in Python and Django, one hop from the Go services this team runs |
| northwind-retail | c2 | job | 2020-02 | 0.50 | 1 | A batch pipeline at scale, transferable but not the streaming the JD wants |
| northwind-retail | c3 | job | 2020-02 | 0.70 | 1 | Postgres lock diagnosis under load, adjacent to the reliability must-have |
| northwind-retail | c4 | job | 2020-02 | 0.70 | 1 | Contract testing at a payments boundary, named under integration quality |
| orbit-analytics | c1 | job | 2018-05 | 0.20 | 1 | Analytics query cost in ClickHouse — same field, nothing the JD asks for |
| orbit-analytics | c2 | job | 2018-05 | 0.50 | 1 | Event schema design for producers, one hop from the streaming contract work |
| orbit-analytics | c3 | job | 2018-05 | 0.70 | 1 | Terraform and a deploy pipeline, the infrastructure-as-code nice-to-have head-on |
| kestrel-media | c1 | job | 2017-07 | 0.20 | 1 | Early-career Flask API work, same field and well under the scope asked for |
| kestrel-media | c2 | job | 2017-07 | 0.00 | 1 | Front-end accessibility, unrelated to a backend platform role |
| kestrel-media | c3 | job | 2017-07 | 0.50 | 1 | Idempotency on a retry path, transferable to the payments correctness wanted |
| ledger-cli | c1 | project | 2024-06 | 0.20 | 1 | Rust CLI parsing — same field, nothing the posting names |
| ledger-cli | c2 | project | 2024-06 | 0.50 | 1 | Property-based testing, transferable to the correctness bar the JD sets |
| ledger-cli | c3 | project | 2024-06 | 0.20 | 1 | Documentation for a personal tool, same field only |
| ledger-cli | c4 | project | 2024-06 | 0.20 | 1 | Profiling a personal tool, far under the scale the JD works at |
| feedforge | c1 | project | 2023-03 | 0.70 | 1 | Bounded-concurrency fan-out in Go, adjacent to the consumer work asked for |
| feedforge | c2 | project | 2023-03 | 0.20 | 1 | Full-text search over a personal archive, same field only |
| feedforge | c3 | project | 2023-03 | 0.50 | 1 | HTTP caching semantics, one hop from the API efficiency line |
| feedforge | c4 | project | 2023-03 | 0.50 | 1 | Fixture-driven parser testing, transferable to the contract-test line |
| homelab-observability | c1 | project | 2022-08 | 0.70 | 1 | Prometheus and Grafana, the observability nice-to-have head-on |
| homelab-observability | c2 | project | 2022-08 | 0.70 | 1 | Terraform and Ansible, the infrastructure-as-code nice-to-have head-on |
| homelab-observability | c3 | project | 2022-08 | 0.20 | 1 | Network segmentation — same field, nothing asked for |

## Merges

Written to `docs/adr/0049-nothing-qualifying-is-left-out.md`: every qualifying claim of
an entry that reaches the page is cited by a unit, and the merge is how a four-claim
block says all four things in the room a one-page résumé has. Every group here is two
or three claims of one entry, at `width: 2` — an XYZ sentence carrying two claims needs
both lines (`0047` §1).

Entries whose only qualifying claim stands alone — `kestrel-media/c3`, `ledger-cli/c2` —
declare no group: there is nothing to merge them with, and a single claim covers itself.

| entry | claims | width | reason |
|---|---|---|---|
| helios-payments | c1+c4 | 2 | the Go consumer rewrite and the service API it exposed are one piece of platform work |
| helios-payments | c2+c3 | 2 | Postgres at scale and the on-call that goes with owning it; neither lands alone |
| atlas-logistics | c1+c2 | 2 | the Postgres migration and the Kafka integration are the same replatforming |
| atlas-logistics | c3+c4 | 2 | standards work and a caching change, each too small for its own line |
| northwind-retail | c3+c4 | 2 | lock diagnosis and contract testing, both reliability work on the same boundary |
| northwind-retail | c1+c2 | 2 | checkout and the batch pipeline behind it, one story about the same system |
| orbit-analytics | c2+c3 | 2 | event schema design and the Terraform that shipped it |
| feedforge | c1+c3+c4 | 2 | concurrency, caching and parser tests — three pieces of one personal service |
| homelab-observability | c1+c2 | 2 | the metrics stack and the Terraform that stands it up |
