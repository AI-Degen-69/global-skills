---
name: project-onboarding-audit
description: Use when onboarding to an unfamiliar project and auditing its docs and structure.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [project-onboarding, documentation, audit, agent-docs, repository]
    related_skills: [codebase-inspection, verification-plan, github-repo-management]
---

# Project Onboarding Audit

## Trigger

Use this skill when the user asks to:
- investigate or understand an unfamiliar project;
- internalize a docs folder before making recommendations;
- determine whether the project needs `CODEX.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, or other project guidance;
- summarize project purpose, docs hierarchy, implementation shape, and next documentation improvements.

## Success Criteria

A good audit produces:
1. A concise statement of the project's purpose.
2. The canonical docs and reading order.
3. The implementation/runtime shape, verified against files or build commands when appropriate.
4. Gaps in onboarding, agent instructions, generated-file handling, and operational safety.
5. A recommendation-first answer: what to add, why, and what not to change yet.

## Procedure

1. **Map the repository first.**
   - Identify top-level docs, source directories, scripts, generated outputs, package files, and existing agent instruction files.
   - Explicitly check for `CODEX.md`, `AGENTS.md`, `CLAUDE.md`, `AGENT.md`, `README.md`, and docs indexes.

2. **Read docs in layers.**
   - Start with role/strategy files (`AGENT.md`, `STRATEGY.md`, `PARAMETERS.md`) if present.
   - Then read overview and canonical policy docs.
   - Then read detailed explainers and examples.
   - Track duplicated or conflicting rules separately instead of smoothing them over.

3. **Validate docs against implementation.**
   - Inspect scripts, package files, app entrypoints, generated data, and representative source files.
   - Run safe verification commands when useful, such as a frontend build or typecheck.
   - Do not run data-refreshing or side-effectful scripts unless the user asked for a live refresh.

4. **Classify existing docs by audience.**
   - Human onboarding: `README.md`, docs index, architecture overview.
   - Agent behavior: `AGENT.md`, `CODEX.md`, `AGENTS.md`, `CLAUDE.md`.
   - Domain rules: canonical rules / parameters docs.
   - Generated data: provenance and regeneration docs.

5. **Recommend documentation additions.**
   - Prefer `CODEX.md` for coding-agent/repo-operations guidance.
   - Keep domain-role prompts separate from coding-agent instructions when both are useful.
   - Recommend a docs index when the docs folder is dense or overlapping.
   - Recommend a canonical-rules document when thresholds or definitions conflict.

## CODEX.md Recommendation Heuristic

Recommend `CODEX.md` when:
- the project will be touched by coding agents;
- there are generated files, build commands, or side-effectful scripts to avoid running accidentally;
- docs contain domain constraints agents must not guess;
- there is already a role prompt (`AGENT.md`) that should not be overloaded with repo-operation instructions.

Do **not** treat `CODEX.md` as a replacement for a product/domain role prompt. Use it as the operational contract for code agents: commands, boundaries, generated files, safety notes, and canonical docs reading order.

## Common Recommendations

- `README.md` — human project entrypoint: purpose, setup, commands, common workflows.
- `docs/INDEX.md` — docs map and reading order.
- `docs/canonical-rules.md` — one authoritative source for thresholds, invariants, and contradictions.
- Root `.gitignore` — ignore dependencies, build outputs, local databases, logs, virtualenvs.
- `docs/generated-data.md` — what files are generated, by which command, and when not to regenerate them.
- `docs/input-format.md` — expected input/log formats for parsers or dashboards.

## Reporting Template

```markdown
## Core takeaway
[Recommendation first.]

## What I understood
[Purpose, users, workflow, success metrics.]

## What I inspected
[Files/docs/commands verified.]

## Recommendation
[Specific files to add/change, with rationale.]

## What I did not do
[Especially side-effectful scripts intentionally not run.]

## Recommended next step
[One action.]
```

## Pitfalls

- Do not flatten a dense docs folder into a vague summary; identify canonical vs supporting docs.
- Do not silently resolve conflicting parameters; call them out and recommend a canonical source.
- Do not over-infer operational rules from secondary constraints. If the user confirms project canon (for example, "100 shares required" despite an 80% cap appearing elsewhere), patch docs and references to that canon instead of preserving the earlier inference.
- Do not run market-data refreshes, migrations, deploys, or destructive scripts during an audit unless requested.
- Do not turn a domain-role prompt into a coding-agent guide; separate concerns.
- Do not claim repository status, build health, or file presence without checking via tools.
- Do not record transient missing-tool setup as a durable skill lesson; capture only repeatable workflow improvements.

## References

- `references/puthouse-docs-internalization.md` — example audit notes from a PutHouse options-income dashboard/docs onboarding session.
