---
type: project
title: Homelab observability stack
org: Personal project
location: Self-hosted
started: 2022-05
ended: 2022-08
domain: infrastructure
---

## c1
skills: Prometheus, Grafana, Docker

**Assertion:** Stood up metrics and alerting for a home network I stopped guessing about.

**Evidence:** The network died every few weeks and diagnosis was rebooting things until
it came back. Prometheus scraping the router, the NAS and the containers, with alerts
that reach my phone, turned that into a graph that names the culprit. It was the access
point overheating.

## c2
number: 90%
provenance: measured
skills: Terraform, Ansible, Infrastructure as code

**Assertion:** Codified the stack so 90% of it rebuilds from scratch with one command.

**Evidence:** The first version was hand-configured and I lost it to a failed SD card.
Rebuilding from Ansible playbooks and Terraform state is now a command and a wait; the
remaining tenth is the router, which has no API worth automating. Ninety per cent is
the share of services in the playbooks, counted rather than estimated.

## c3
skills: Networking, Security, Linux

**Assertion:** Segmented the network so untrusted devices cannot reach anything that matters.

**Evidence:** Everything shared one flat network, including a smart plug that phones
home to a vendor I know nothing about. VLANs and firewall rules put those devices in
their own segment with outbound access only. Nothing since has needed a rule loosened,
which suggests the split was drawn in the right place.
