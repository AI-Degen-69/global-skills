---
name: task-execution-guidance
description: Use when handing off structured execution guidance to a worker.
---

# Task Execution Guidance

## Who
- Writer/planner: strategist
- Implementer: engineer
- Reviewer: reviewer
- Orchestrator: delegate_task via Hermes subagents

## Prompt setup
- Use the exact task brief the user approves.
- Include:
  - file path scope
  - evidence/patch files to follow
  - acceptance criteria
  - verification command

## Plan + skill
- Active plan: docs/plans/*.md
- Execution: executing-plans
- Legacy safety: working-with-legacy-code
- Done gate: verification-before-completion
- UI changes: frontend-design

## Status format
1. Done
2. Not done
3. Current plan or blocker
4. Likely owner
5. Recommended action
