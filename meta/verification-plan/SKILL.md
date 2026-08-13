---
name: verification-plan
description: Use when starting a multi-step task and needing a measurable success-verification plan.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [verification, quality, checkpoints, evaluation]
    related_skills: [completion-contract-loop, vault-audit-fix, verifier-codex-critic]
---

# Verification Plan

## Trigger

Use this skill before any task with more than one meaningful step, especially:
- vault ingestion or maintenance;
- code or config changes;
- research synthesis or briefings;
- dashboard or UI work;
- skill creation or skill refactoring.

## Output Contract

Every plan must include:

```markdown
Verification Plan:
- Success criteria: [measurable, task-specific]
- Checkpoints: [step -> verify: check]
- Critic model: [deterministic script / codex / second model / none]
- External signals: [tests, audit script, diff scope, historical examples, health check]
```

## Procedure

1. Define the measurable end state.
2. Break the work into checkpoints that each have a direct verification action.
3. Choose the cheapest critic that can actually catch the failure mode.
4. Add an external signal when model judgment alone is weak.
5. Refuse to use vague criteria like "looks good" unless the user explicitly wants subjective review.
6. When a bug fix changes behavior, explicitly verify downstream user-facing surfaces that may have drifted behind the implementation: CLI help/output text, slash-command output, docs, and other operator-visible wording.
7. If success has multiple requirements or vague done criteria, also use `completion-contract-loop` to track each requirement as missing, weak, proved, or contradicted.

## Critic Selection

- **Deterministic scripts first** — tests, linters, audit scripts, grep hits, file existence checks.
- **Codex critic** — use `verifier-codex-critic` when the task is code-heavy, spans multiple files, or needs an independent implementation review.
- **Second model** — reserve for high-stakes synthesis, architecture, or ambiguous prose evaluation.
- **None** — acceptable only when direct deterministic checks fully cover success.

## Default Templates

Reference: `C:\Users\Tiger\Vault\Agent Skills\wiki\evaluation-criteria-templates.md`

Use the live vault reference for:
- vault ingestion report
- code change / feature
- research synthesis / briefing
- vault maintenance / audit
- dashboard / UI work
- skill creation / modification

## Examples

### Vault maintenance
```markdown
Verification Plan:
- Success criteria: config contains the intended hooks and hook scripts return the correct block decisions.
- Checkpoints:
  1. Backup config -> verify: backup file exists.
  2. Write hook scripts -> verify: files exist and parse cleanly.
  3. Patch config -> verify: expected hook entries present.
  4. Test hook behavior -> verify: protected path blocks, safe path no-ops.
- Critic model: deterministic verification only.
- External signals: `hermes -p vault hooks list`, direct script output.
```

### Code change
```markdown
Verification Plan:
- Success criteria: requested behavior works and only task-relevant files changed.
- Checkpoints:
  1. Failing test or repro -> verify: issue reproduced.
  2. Fix applied -> verify: targeted tests pass.
  3. Scope review -> verify: diff contains no orthogonal edits.
  4. Independent review -> verify: Codex returns PASS or specific issues are resolved.
- Critic model: codex.
- External signals: test suite, lint, type-check.
```

## Pitfalls

- Do not confuse a checklist with measurable proof.
- Do not skip external signals when the failure mode is objective.
- Do not choose an expensive critic when a script can catch the issue.
- Do not claim completion without checkpoint evidence.
- For tasks with several acceptance criteria, do not keep requirement status mentally; use `completion-contract-loop` as the proof ledger.
- Separate "spec is valid" from "runtime can actually discover and execute it". For repo-local workflows, plugins, or wrappers, add an explicit discovery/resolution checkpoint before claiming the thing is runnable.
- When a wrapper/entrypoint behaves differently from the underlying engine, stop probing blindly: read the resolution logic, identify the missing root/config/runtime assumption, then verify with the lowest-level path that still exercises the real system.

## Verification Checklist

- [ ] Success criteria are measurable.
- [ ] Every checkpoint has a verification action.
- [ ] Critic choice matches task risk.
- [ ] External signals are named where relevant.
- [ ] Plan exists before execution starts.
