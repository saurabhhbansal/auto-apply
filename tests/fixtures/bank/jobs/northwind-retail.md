---
type: job
title: Software Engineer
org: Northwind Retail
location: Pune, India
started: 2018-06
ended: 2020-02
domain: e-commerce
---

## c1
number: 21.6%
provenance: measured
skills: Python, Django, PostgreSQL

**Assertion:** Brought cart abandonment down ~22% by rebuilding checkout as a single-page flow.

**Evidence:** Checkout was four page loads and the analytics funnel showed the drop
happening between the third and the fourth. Collapsing it to one page with server-side
validation is what the A/B test ran against, and the 21.6% is that test's read over three
weeks of traffic. The rebuild also removed the double-charge path that had been the
top support ticket, because the payment call moved behind an idempotency key.

## c2
number: 500k
provenance: estimated
skills: Python, Celery, Redis

**Assertion:** Rebuilt the catalogue importer to handle ~500k SKUs without an overnight window.

**Evidence:** The importer loaded the full catalogue into memory and ran once a night,
so a supplier price change took a day to appear. Streaming the import in chunks and
diffing against the stored hash made it incremental and let it run hourly. Half a
million is roughly what the catalogue held then, taken from the supplier feed rather
than measured on our side.

## c3
skills: Incident response, PostgreSQL, Observability

**Assertion:** Found and fixed the lock contention behind our worst outage of the year.

**Evidence:** The site went read-only on a Saturday sale and the on-call rotation had
spent an hour restarting workers. I read the lock graph and found the inventory
decrement holding a row lock across an external call to the pricing service. Moving the
call outside the transaction ended it, and the write-up became the reason we banned
network calls inside transactions.

## c4
skills: Python, Testing, Refactoring

**Assertion:** Introduced contract tests at the payments boundary after a silent schema change.

**Evidence:** A processor changed a field from a string to an object without telling
anyone and settlement broke quietly for two days before finance noticed. The contract
tests run against a recorded processor response and fail the build on a shape change.
It is the least interesting work I did there and the reason nothing like it happened again.
