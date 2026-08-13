---
name: vault-external-workflow-evaluation
description: Use when evaluating external repos, prompt packs, workflows, or automation systems for Robert's vault. Inspect
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, evaluation, external, workflows]
    related_skills: [vault-compounding-loop, vault-ingestion, vault-umbrella]
---

# Vault External Workflow Evaluation

## Overview

This skill evaluates external repos, agent skills, Obsidian frameworks, workflow packs, and automation systems before anything is adapted into Robert's environment. Inspect the external system outside the vault. Borrow procedures where useful, but do not install foreign schemas directly.

## When to Use

- Robert asks you to review a repo, framework, prompt pack, or workflow.
- You want to adapt an idea from another Obsidian or AI-agent system.
- You need a structured adopt, adapt, reject, or monitor conclusion.

## Rules

- Inspect outside the vault first.
- Do not install foreign schemas directly.
- Borrow procedure, reject schema conflicts.
- Always explain what was borrowed and why in plain language.
- If the source is an agent skill or workflow, include an adopt, adapt, reject, or monitor conclusion.
- If the source includes scripts, tests, or setup tooling, smoke-test the smallest safe executable path outside the vault when practical; if the preferred test runner is unavailable, verify the core script behavior directly rather than treating the repo as unverified.
- If the adaptation belongs in Hermes skills, update the skill layer rather than vault content unless source-backed vault ingestion is explicitly requested.

## Reporting

Use `templates/external-workflow-evaluation-report.md`.

## Common Pitfalls

1. Equating a good idea with permission to import the entire external structure.
2. Failing to explain what was borrowed in understandable terms.
3. Writing vault content when the real change belongs in Hermes skills.
4. Ignoring Robert's current vault schema in favor of a generic system.

## Verification Checklist

- [ ] External system inspected outside the vault.
- [ ] Borrowed procedures were separated from rejected schemas.
- [ ] Conclusion states adopt, adapt, reject, or monitor.
- [ ] Any resulting changes were applied in the right layer.
