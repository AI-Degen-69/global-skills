---
name: completion-contract-loop
description: Use when a task has vague done criteria, multiple requirements, high risk of premature completion claims, or n
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, completion, autonomy, planning, quality]
    related_skills: [verification-plan, verification-before-completion, writing-plans]
---

# Completion Contract Loop

## Overview

Use a completion contract when “done” can drift. The loop converts a task into a small requirement ledger and keeps working only while new evidence closes a requirement.

Core rule: **completion means every required item has current proof, not that work feels finished.**

## When to Use

Use this before or during:
- multi-step build, fix, audit, ingestion, cleanup, or research tasks;
- tasks where Robert asks to “implement,” “finish,” “verify,” “make it work,” or “clean this up”;
- tasks with several acceptance criteria or hidden integration risk;
- any task where an agent might say “done” after partial tests.

Do not use for simple factual answers with no action or persistent state.

## The Contract

Create or maintain this ledger in chat, `todo`, or a plan/progress file:

| Requirement | Evidence needed | Status | Current evidence |
|---|---|---|---|
| Concrete requirement | Command, file, UI, audit, or source check that proves it | missing / weak / proved / contradicted | Exact output, path, URL, or blocker |

Status meanings:
- **missing** — no evidence yet.
- **weak** — related evidence exists, but it does not prove the requirement.
- **proved** — fresh evidence directly satisfies the requirement.
- **contradicted** — current evidence shows the requirement is not met.

## Loop

1. Define the required outcomes and non-goals.
2. For each requirement, name the proof that would satisfy it.
3. Take one bounded action that should close one or more requirements.
4. Verify with the named proof source.
5. Update the ledger immediately.
6. Continue only while the next action is safe, scoped, and likely to close a missing/weak/contradicted requirement.
7. Stop when all requirements are proved, progress stalls, budget is exhausted, or an approval gate is reached.

## Required Stop Rules

Stop and report instead of pushing forward when:
- the next step is destructive, irreversible, credential-sensitive, financial, or customer-facing;
- a requirement depends on Robert’s preference or external access only he can provide;
- two attempts fail without new evidence;
- the work would expand beyond the original scope;
- available evidence contradicts the claimed outcome.

## Closeout Contract

Final response must include:
- what changed or what was learned;
- each important requirement and its proof;
- remaining missing/weak/contradicted items, if any;
- the recommended next action.

Never mark the task complete if any required item is missing, weak, or contradicted. Report partial completion instead.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Treating tests as proof for every requirement | Map each requirement to its own proof source. |
| Keeping the ledger only mentally | Write it in chat, `todo`, or a progress file. |
| Continuing after scope changes | Stop and get a new contract. |
| Reporting “done except…” | That means partial, not done. |
| Accepting subagent self-reports | Verify the artifact, path, command, URL, or diff yourself. |

## Quick Template

```markdown
Completion Contract:
- Requirement: ...
  Proof needed: ...
  Status: missing
  Current evidence: none yet
- Requirement: ...
  Proof needed: ...
  Status: missing
  Current evidence: none yet
Stop rules: approval-gated/destructive/scope expansion/two failed attempts/no new evidence.
```

## Verification Checklist

- [ ] Requirements are explicit.
- [ ] Each requirement has a named proof source.
- [ ] Ledger is updated after each bounded action.
- [ ] Final claim matches the ledger state.
- [ ] Any partial or blocked result is labeled honestly.
