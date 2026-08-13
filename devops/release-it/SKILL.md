---
name: release-it
description: Use when designing, hardening, or reviewing production systems for stability, resilience, and operational read
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [production, resilience, stability, operations, architecture, reliability]
    related_skills: [system-design, clean-architecture, ddia-systems, high-perf-browser, debugging-hermes-tui-commands]
---

# Release It! — Production Readiness Patterns

## Overview

Michael Nygard's *Release It!* is the definitive field guide for software that survives production. This skill encodes Nygard's stability patterns, capacity patterns, and operational mindset into a repeatable agent workflow. It doesn't just list patterns — it applies them as a **production gate**: given a system design, what will break, and how do we harden it before it ships?

## When to Use

- **Architecture review** — evaluating a design for production risks before build
- **Pre-launch hardening** — identifying and fixing stability gaps in a release candidate
- **Incident postmortem** — structuring analysis around stability/anti-patterns
- **Capacity planning** — modeling failure domains and scaling limits
- **Operational readiness** — defining runbooks, alerts, and degradation modes
- **Don't use for:** greenfield prototyping, local dev ergonomics, or feature design (use system-design skill instead)

## Core Pattern Catalog

### Stability Patterns (Prevent Cascading Failures)

| Pattern | Purpose | When to Apply |
|---------|---------|---------------|
| **Circuit Breaker** | Stop calling a failing dependency; fail fast, recover automatically | Any remote call (HTTP, DB, queue, external API) |
| **Bulkhead** | Isolate critical resources so one failure doesn't starve others | Thread pools, connection pools, CPU/memory partitions |
| **Timeout** | Bound every external call; prevent indefinite blocking | All network calls, locks, queue operations |
| **Retry with Backoff** | Transient failures self-heal; exponential backoff + jitter | Idempotent operations after circuit breaker half-open |
| **Deadletter Queue** | Capture poison messages without blocking the pipeline | Async processing, event-driven architectures |
| **Fail Fast** | Validate inputs early; reject bad requests before they consume resources | API gateways, service boundaries |

### Capacity Patterns (Handle Load Gracefully)

| Pattern | Purpose | When to Apply |
|---------|---------|---------------|
| **Queue Length Limit** | Reject/shed load before memory OOM | Ingestion pipelines, webhook handlers |
| **Workload Prioritization** | Serve high-value traffic under load | Multi-tenant, tiered customers |
| **Connection Pool Sizing** | Match pool to downstream capacity + headroom | DB, HTTP clients, message brokers |
| **Horizontal Scaling Triggers** | Define when to scale out (not just CPU) | Custom metrics: queue depth, latency p99, error rate |

### Operational Patterns (Survive the Real World)

| Pattern | Purpose | When to Apply |
|---------|---------|---------------|
| **Log Structured & Correlated** | Trace requests across services; enable fast debugging | All services; add request IDs, span IDs |
| **Health Endpoints** | Liveness (process alive) vs Readiness (can serve traffic) | Kubernetes probes, load balancer checks |
| **Graceful Degradation** | Disable non-critical features under stress | Feature flags tied to capacity signals |
| **Chaos Experimentation** | Validate resilience hypotheses in staging/prod | Game days, automated fault injection |
| **Runbook-First Design** | Every alert has a runbook; every runbook has an owner | On-call rotation, incident response |

## Skill Usage Patterns

### Pattern: Architecture Stability Review
```
Use release-it skill to review [architecture doc / diagram / service list].
Focus: stability patterns, failure domains, operational gaps.
Deliver: risk matrix (pattern → coverage → gap → fix priority), top 5 hardening tasks.
```

### Pattern: Pre-Launch Production Gate
```
Use release-it skill as production gate for [service name] v[X.Y.Z].
Scope: circuit breakers, timeouts, bulkheads, health checks, logging, alerts, runbooks.
Output: PASS/FAIL per pattern, blocking issues, deferrable items with owner + date.
```

### Pattern: Incident-Driven Hardening
```
Use release-it skill to analyze [incident timeline / postmortem].
Map: root cause → missing pattern → systemic fix.
Output: pattern gap, fix, verification test, rollout plan.
```

### Pattern: Capacity Stress Test Design
```
Use release-it skill to design load test for [service].
Target: find breaking point, observe degradation mode, validate circuit breakers.
Output: test scenarios, success criteria, rollback triggers.
```

## Example Invocations

> **User:** "Review our payment service architecture for production readiness. Use release-it skill."
>
> **Agent applies:**
> 1. Map service dependencies (DB, Fraud API, Ledger, Message Bus)
> 2. For each boundary: circuit breaker? timeout? bulkhead? retry policy?
> 3. Check health endpoints: liveness vs readiness differentiated?
> 4. Verify structured logging with correlation IDs
> 5. Confirm runbooks exist for each alert
> 6. Return: stability matrix, top 3 blocking gaps, 1-week hardening plan

> **User:** "We had a cascade failure when Fraud API timed out. Use release-it skill to harden."
>
> **Agent applies:**
> 1. Identify missing circuit breaker on Fraud API call
> 2. Add timeout + bulkhead (separate thread pool)
> 3. Define fallback: async review queue + approve-below-threshold
> 4. Add alert on circuit breaker open state
> 5. Write runbook: "Fraud API circuit open → enable fallback, page on-call"
> 6. Return: diff-ready code changes, config updates, test cases

## Common Pitfalls

1. **Treating patterns as checkboxes** — A circuit breaker without monitoring/alerting is theater. Every pattern needs observability and a runbook.
2. **Applying all patterns everywhere** — Not every service needs bulkheads. Apply based on **criticality × blast radius**.
3. **Confusing resilience with reliability** — Resilience = survives failure. Reliability = doesn't fail. This skill targets resilience.
4. **Ignoring the "human" patterns** — Runbooks, on-call hygiene, chaos experiments are as critical as code patterns.
5. **Setting timeouts globally** — Timeout must match *downstream SLA*, not a default. A 30s DB timeout kills the circuit breaker's purpose.
6. **Skipping the "half-open" state test** — Circuit breakers must be tested transitioning from open → half-open → closed.

## Verification Checklist

- [ ] Every external dependency has: circuit breaker, timeout, retry policy, bulkhead (if critical)
- [ ] Health endpoints distinguish liveness vs readiness
- [ ] Structured logging with correlation IDs across service boundaries
- [ ] Every alert has: runbook, owner, escalation path
- [ ] Capacity limits defined (queue depth, connection pool, concurrent requests)
- [ ] Degradation modes documented: what fails first, what stays up
- [ ] Chaos experiment plan for top 3 failure scenarios
- [ ] Output is diff-ready: config changes, code snippets, test cases

## One-Shot Recipes

### Recipe: New Service Production Checklist
```
Use release-it skill to generate production checklist for [new service name].
Dependencies: [list downstream services, DBs, queues].
Output: markdown checklist with pattern → implementation → verification → owner.
```

### Recipe: Migration Hardening
```
Use release-it skill to harden [migration plan: service A → service B].
Focus: dual-write risks, rollback triggers, data consistency, traffic shifting.
Output: stability gates per migration phase, abort criteria, verification queries.
```

### Recipe: Game Day Scenario
```
Use release-it skill to design game day for [system].
Scenarios: [pick 3: DB failover, dependency latency spike, AZ loss, cert expiry].
Output: experiment steps, expected behavior, success/fail criteria, rollback.
```