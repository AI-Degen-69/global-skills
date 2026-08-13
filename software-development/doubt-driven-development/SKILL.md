---
name: doubt-driven-development
description: Use when stakes are high (production, security, irreversible), working in unfamiliar code, or a confident outp
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adversarial-review, verification, critical-decisions, doubt-driven, subagent]
    related_skills: [ce-code-review, test-driven-development, systematic-debugging, source-driven-development]
---

# Doubt-Driven Development (DDD)

## Overview

**Doubt-Driven Development** is an adversarial review workflow that prevents agent bias by spawning a **fresh-context second agent** to attack the primary agent's conclusion before it stands. It implements the CLAIM → EXTRACT → DOUBT → RECONCILE → STOP loop (max 3 rounds).

This skill encodes the largest skill in Addy Osmani's `agent-skills` repo (16 KB) — the "headliner" that Bitwise AI called out as genuinely new. The key principle: **if you can't write the claim compactly, you have a vibe, not a decision.**

## When to Use

- Production changes with irreversible consequences (database migrations, auth changes, infra)
- Security-sensitive code (auth, crypto, secrets handling, boundary validation)
- Working in unfamiliar codebases or frameworks
- High-confidence agent outputs that haven't been independently verified
- Architectural decisions (API contracts, module boundaries, data models)
- Any decision where "seems right" is not sufficient evidence

Don't use for:
- Trivial bug fixes with obvious causes
- Routine CRUD operations
- Exploratory spikes (use `spike` skill instead)
- When a human review is already scheduled and sufficient

## The CLAIM → EXTRACT → DOUBT → RECONCILE → STOP Loop

```text
┌─────────────────────────────────────────────────────────────┐
│  PRIMARY AGENT                                              │
│  1. CLAIM      → Write the decision compactly (1-3 lines)  │
│  2. EXTRACT    → Pull supporting evidence, sources, code    │
└──────────────────────┬──────────────────────────────────────┘
                       │ Handoff: claim + evidence (NOT conclusion)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  REVIEWER AGENT (fresh context, no prior conversation)      │
│  3. DOUBT      → Attack the claim: find holes, edge cases, │
│                  missing tests, wrong assumptions,          │
│                  security issues, scalability limits        │
│  4. RECONCILE  → Primary agent responds to doubts;         │
│                  either strengthens claim or pivots         │
└──────────────────────┬──────────────────────────────────────┘
                       │ Max 3 rounds, then:
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. STOP       → Decision stands OR escalate to human      │
└─────────────────────────────────────────────────────────────┘
```

### Critical Rule: Reviewer Never Sees Original Conclusion

The reviewer agent receives **only the claim and extracted evidence** — never the primary agent's reasoning or conclusion. Seeing the conclusion biases toward agreement (confirmation bias). The reviewer must independently reconstruct the reasoning from evidence.

## Workflow Steps

### Step 1: Primary Agent — CLAIM

Write the decision as a **compact, falsifiable claim**:

```
✅ Good: "Switching auth from JWT to PASETO v4 local tokens reduces payload size 40% and eliminates algorithm confusion attacks. Migration path: dual-issue for 30 days, then hard cutoff."

❌ Bad: "We should improve auth." (not falsifiable)
❌ Bad: "PASETO is better than JWT." (no evidence, no migration path)
```

**Claim checklist:**
- [ ] Fits in 1-3 lines
- [ ] Includes measurable outcome
- [ ] Names the alternative considered
- [ ] States migration/rollback path

### Step 2: Primary Agent — EXTRACT

Gather **only the evidence supporting the claim**:

- Code snippets (diff, config, schema)
- Official docs URLs with exact version
- Benchmark numbers with methodology
- Threat model / attack vectors addressed
- Test coverage gaps filled

**Format as a structured handoff document:**

```markdown
# DDD Handoff: [Claim Title]

## Claim
[1-3 line compact claim]

## Evidence
- [ ] Source 1: URL + relevant section
- [ ] Source 2: Code file:lines
- [ ] Source 3: Benchmark methodology + results

## Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Option A    | Reason           |

## Migration / Rollback
[Concrete steps, timeline, rollback trigger]

## Open Questions
- Question 1
- Question 2
```

### Step 3: Reviewer Agent — DOUBT

**Fresh context. No prior conversation.** Load only the handoff document.

Attack vectors (non-exhaustive):
- **Assumptions**: What implicit assumptions does the claim rely on?
- **Edge cases**: What happens at 10x load? Network partition? Clock skew?
- **Security**: Timing attacks? Injection? Privilege escalation? Supply chain?
- **Testing**: What's not covered? Integration vs unit? Chaos tests?
- **Rollback**: Does rollback actually work? Data loss risk?
- **Dependencies**: Version pinning? Transitive deps? License compliance?
- **Operational**: Observability? Alerting? Debuggability?
- **Hyrum's Law**: What observable behaviors will callers depend on?

**Output: Structured Doubt Report**

```markdown
# DDD Doubt Report: [Claim Title]

## Critical (blocks STOP)
- [ ] Doubt 1: Evidence + why it blocks
- [ ] Doubt 2: ...

## Major (requires reconciliation)
- [ ] Doubt 3: ...

## Minor (document, don't block)
- [ ] Doubt 4: ...
```

### Step 4: Primary Agent — RECONCILE

Address each doubt **with evidence, not argument**:

- For each Critical/Major doubt: provide code fix, additional test, doc update, or pivot claim
- Update the handoff document with resolutions
- If a doubt cannot be resolved → **pivot the claim** (narrow scope, change approach)
- Max 3 reconciliation rounds

### Step 5: STOP

Decision criteria:
- **Zero Critical doubts remaining** → Claim stands, proceed to implementation
- **Critical doubts unresolved after 3 rounds** → Escalate to human with full DDD trace
- **Claim pivoted significantly** → Restart from Step 1 with new claim

## Integration with Hermes / CE Loop

| CE Skill | Integration Point |
|----------|-------------------|
| `ce-plan` | Add DDD gate for tasks tagged `security`, `irreversible`, `architectural` |
| `ce-code-review` | DDD as a pre-review gate; 12-persona review runs after DDD passes |
| `ce-work` | Subagent spawned via `delegate_task` with isolated context |
| `systematic-debugging` | Use DDD when root cause is uncertain and fix is risky |

**Hermes subagent pattern:**
```python
# Primary agent creates handoff doc
# Then spawns reviewer:
delegate_task(
    goal="Review DDD claim: [claim title]. Load handoff at [path]. Produce doubt report.",
    context="Source: handoff doc at [path]. No prior context. Apply adversarial review.",
    toolsets=["file", "terminal", "web"],
    role="leaf"
)
```

## Common Pitfalls

1. **Primary agent argues instead of evidencing** — Reconcile with code/tests/docs, not prose
2. **Reviewer sees primary's reasoning** — Biases toward agreement; use fresh context only
3. **Claim too vague** — "Improve performance" → "Reduce p95 latency from 800ms to <300ms by adding Redis cache layer"
4. **Skipping EXTRACT** — No evidence = no review possible; claim is a vibe
5. **Unbounded rounds** — Hard limit: 3 rounds, then STOP or escalate
6. **Treating Minor doubts as blockers** — Document them; don't stall
7. **No migration/rollback in claim** — Irreversible changes without rollback = Critical doubt

## Verification Checklist

- [ ] Claim written as 1-3 line falsifiable statement
- [ ] Evidence extracted with sources (URLs, file:lines, benchmarks)
- [ ] Handoff document created
- [ ] Reviewer agent spawned with fresh context (no prior conversation)
- [ ] Doubt report produced with Critical/Major/Minor classification
- [ ] All Critical doubts resolved with evidence
- [ ] Max 3 reconciliation rounds observed
- [ ] STOP decision recorded: claim stands OR escalated to human
- [ ] Full DDD trace saved for audit (handoff + doubt report + resolutions)

## One-Shot Recipes

### Recipe: Secure Auth Migration Gate
```bash
# 1. Primary agent writes claim + evidence to docs/ddd/auth-migration-claim.md
# 2. Spawn reviewer:
hermes delegate_task --goal "DDD Review: auth migration claim" \
  --context "Handoff: docs/ddd/auth-migration-claim.md. Fresh context. Adversarial review." \
  --toolsets file,terminal,web
# 3. Reviewer writes doubt report to docs/ddd/auth-migration-doubts.md
# 4. Primary reconciles, updates claim
# 5. If Critical doubts remain after 3 rounds → escalate
```

### Recipe: API Contract Change
Trigger DDD before any breaking API change. Claim: "Adding `X-Request-ID` header to all responses; 30-day deprecation of old correlation-id format."
Evidence: OpenAPI diff, client impact analysis, rollback via feature flag.
```
