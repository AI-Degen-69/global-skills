---
name: kanban-operations
description: Use when orchestrating or running Hermes Kanban worker lanes.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, orchestration, worker, multi-agent, routing]
---

# Kanban Operations

Umbrella skill for Hermes Kanban usage across both orchestrator and worker roles.

## When to use
- Routing work through the Kanban board
- Decomposing a request into assigned cards
- Running as a dispatched worker that must complete, block, or hand off work correctly
- Recovering from retries, blocked tasks, or bad assignments

## Role split

### Orchestrator lane
Use when your job is decomposition and routing.
- Discover real profile names first
- Split independent lanes into separate cards
- Encode dependencies with parents at creation time
- Do not "just do the work yourself"

### Worker lane
Use when spawned to execute a single card.
- `kanban_show` first
- Work inside the assigned workspace kind
- Leave structured summaries and metadata on completion
- Use `kanban_comment` + `kanban_block` instead of trying to clarify with a live user

## Shared rules
1. Use the board for durable, multi-step, multi-specialist, or review-heavy work.
2. Do not invent assignee names.
3. Use explicit dependency links for true gates.
4. Prefer precise block reasons and richer context in comments.
5. Treat retries as evidence; inspect prior run outcomes before retrying the same path.

## Verification
- Cards created with real returned IDs
- Assignees exist
- Parents reflect real dependencies
- Worker summaries include enough metadata for downstream tasks

## Pitfalls & Recovery Patterns

### Worker completes but artifact not registered
**Symptom:** Task shows `completed` but no `artifacts` array in the completion event; workspace directory may not exist; file written to worker's cwd instead of workspace.

**Root cause:** Worker wrote output to its working directory (`cwd`) rather than the assigned workspace path. The kanban completion handler only registers artifacts explicitly returned via the workspace path.

**Recovery:**
1. Check `hermes kanban runs <task-id>` for the completion summary — it often describes what was created.
2. Check `hermes kanban log <task-id>` for the worker's final output (may mention the filename).
3. Search common locations: `~/AppData/Local/hermes/kanban/workspaces/<task-id>/`, worker's cwd, project root.
4. If source material exists (parent task output), regenerate the artifact directly into the workspace.
5. Add a comment to the task with `hermes kanban comment <task-id> "Artifact recovered: <path>"` for traceability.

**Prevention (for worker prompts):** Explicitly instruct workers to write outputs to the workspace path (available via `KANBAN_WORKSPACE` env var or `kanban_show` output), not cwd. Verify workspace exists before writing.

### Workspace directory not created
**Symptom:** `ls` on workspace path returns "No such file or directory" even for running/completed tasks.

**Root cause:** Workspace is created lazily on first `claim` or when worker writes to it. If worker never writes to workspace path, directory never materializes.

**Recovery:** `mkdir -p` the workspace path manually, then place artifact there.

### Stale "running" state
**Symptom:** Task shows `running` with heartbeats but no process found; `hermes kanban reclaim` fails with "not running or unknown id"; `promote` fails with "task is 'done'".

**Root cause:** Worker process died or completed but heartbeat lock expired before completion event was processed. State machine shows `running` but underlying process is gone.

**Recovery:** 
- Run `hermes kanban show <task-id>` — if it shows `completed` with a timestamp, the task is actually done.
- If truly stuck: `hermes kanban reclaim` (if lock exists) → `hermes kanban promote` (if todo/blocked) → re-claim and restart.

## References
- `references/kanban-worker-recovery.md` — detailed recovery recipes, log patterns, and workspace conventions
