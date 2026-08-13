---
name: vault-cron-ingestion
description: Use when designing or running autonomous vault ingestion jobs. Cron must reuse canonical ingestion and audit-f
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, cron, ingestion, automation]
    related_skills: [vault-ingestion, vault-audit-fix, vault-umbrella]
---

# Vault Cron Ingestion

## Overview

This skill is a cron-safe wrapper around canonical ingestion. It does not define a second ingestion process. It exists to impose autonomous constraints while reusing `vault-ingestion` and `vault-audit-fix`.

## When to Use

- Creating or reviewing a cron job that processes vault intake.
- Designing a background ingestion prompt.
- Auditing whether a vault ingestion cron is bounded and safe.

## Required Pairing

Load this skill together with:

- `vault-ingestion`
- `vault-audit-fix`

## Autonomous Constraints

- Cron prompts must be self-contained.
- Cron runs cannot ask questions in the middle of execution.
- Process bounded inputs only, preferably `C:\Users\Tiger\Vault\_Inbox`.
- Use canonical ingestion. No cron shortcuts.
- Leave ambiguous or destructive decisions untouched and report them.
- Generate a report whenever work was done. Quiet watchdog behavior is a separate explicit design choice.

## Implementation Rules

- Prefer `_Inbox/` as the controlled queue.
- Limit items per run when needed to prevent oversized autonomous batches.
- Never invent new domains.
- Never delete, merge, rename, change `Types/`, or make ambiguous destructive changes without approval.

## Common Pitfalls

1. Sneaking in a simplified background-only ingestion path.
2. Making the prompt depend on current chat context.
3. Letting cron process unbounded sources outside the queue.
4. Treating skipped ambiguous items as failures instead of reportable decisions.

## Verification Checklist

- [ ] Cron design explicitly reuses `vault-ingestion` and `vault-audit-fix`.
- [ ] Input bounds are defined.
- [ ] Approval-gated actions are excluded.
- [ ] Reporting behavior is explicit.
- [ ] No separate shortcut ingestion workflow was introduced.
