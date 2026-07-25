---
name: improve
description: "Use when you want to audit a codebase, write self-contained implementation plans, and delegate execution to a cheaper model. Mirrors shadcn/improve's audit-to-plan-to-execute shape: the capable (main) model does recon/audit/prioritization/planning; delegate_task executes the plan in an isolated worktree on a pinned cheaper model. The plan is the product; the skill never implements directly."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [codebase-audit, planning, delegation, cost-arbitrage, agent-skills]
    related_skills: [fable-judge, planning-with-files, source-driven-development, high-agency-critic-mode]
---

# improve — Audit, Plan, Delegate-Execute

## Overview
A reusable workflow that turns a capable model into a **codebase auditor + spec writer**, then hands machine-checkable plans to a **cheaper executor** via `delegate_task`. Adapted from shadcn/improve (GitHub, 8.2k⭐) to Hermes mechanics. The expensive model does the work where intelligence compounds — understanding the codebase, judging what's worth doing, writing the spec. The cheap model does mechanical execution in an isolated git worktree. **The plan is the product. This skill never edits source itself — only `plans/`.**

## When to Use
- "Audit this repo and tell me what's worth fixing."
- "Write an implementation plan for <feature/bug>, then have a cheaper model build it."
- Before a PR: scope the audit to the current branch.
- When you want frontier-model reasoning but don't want to pay frontier tokens for the grunt work.

## Don't Use For
- Trivial one-file changes — just do it (SOUL.md: trivial ask → do, check, two sentences).
- Tasks needing the executor to make judgment calls — keep those on the main model.
- Secret-bearing mutations without a recovery handle (see Hard Rules).

## The Flow
```
you (capable model)  →  /improve            audit → vet → prioritize → plans/
plans/NNN-*.md        →  self-contained specs (verification gates + STOP)
delegate_task        →  cheaper model executes in isolated worktree
fable-judge          →  tech-lead review of the executor's diff
you                  →  merge decision (always yours)
```
Reconcile later (the `/improve reconcile` analog) to retire drifted/fixed findings.

### 1. Recon (read-only)
Map the repo: stack, conventions, exact build/test/lint commands (these become verification gates). Ingest intent docs if present (`CONTEXT.md`, `DESIGN.md`, `AGENTS.md`, `docs/adr/`) so decided tradeoffs aren't re-flagged. Use `search_files`/`read_file`/`terminal` (read-only: `git log`, `grep`, `tree`). **Never mutate the working tree during recon.**

### 2. Audit (fan-out mentally or via delegate_task for parallel categories)
Nine categories: correctness, security, performance, test-coverage, tech-debt, dependencies/migrations, DX, docs, direction (feature ideas — each must cite repo evidence, no generic slop). Every finding carries `file:line` evidence, impact, effort (S/M/L), confidence (HIGH/MED/LOW).

### 3. Vet (you, not a subagent)
Re-read every cited location yourself before showing findings. Drop false positives, correct wrong attributions, record rejections with reasons (so they don't resurface).

### 4. Prioritize
Table ordered by leverage = impact ÷ effort, weighted by confidence. Present to user; they pick what becomes a plan ("plan 1, 3, 5").

### 5. Plan (write to `plans/`)
One file per selected finding. **Three non-negotiable properties** (plans must be executable by the *weakest plausible* executor — a model that never saw this session):
- **Self-contained:** inlined file paths, current-state code excerpts, repo conventions + an exemplar file, verified commands. No "as discussed above."
- **Verification gates:** every step ends with a command + expected output. Done = machine-checkable.
- **Hard boundaries:** explicit out-of-scope list + STOP conditions ("if X, stop and report") instead of letting a small model improvise.
- Stamp the git commit the plan was written against (executor runs a drift check before touching anything).

Filename: `plans/NNN-<short-slug>.md`, zero-padded, with an `index.md` listing priority order + dependency graph. Mirror task IDs into `todo` for TUI visibility (SOUL.md §4).

### 6. Execute (delegate_task + cheaper pin)
Dispatch the executor:
```
delegate_task(
  goal="Implement plans/NNN-<slug>.md exactly. Follow every verification gate; stop at any STOP condition and report. Work only inside the provided git worktree.",
  context="<full plan text> + <repo path> + <worktree path> + <git commit stamp>",
  profile="default"
)
```
**Cost split mechanics (critical):** Hermes `delegate_task` does NOT accept a per-call model. The cheaper executor is realized by pinning **all** delegated children globally:
```yaml
# config.yaml
delegation:
  model: <cheap-model>        # e.g. a free/low-cost coding model
  provider: <cheap-provider>
```
To get the *split* (premium audit + cheap execute): launch the `/improve` session on your capable model (premium), and keep `delegation.model` pinned cheap. Main stays premium; children run cheap. Set via `hermes config set delegation.model <m>` / `delegation.provider <p>` (or edit `config.yaml` directly and restart). ⚠️ This pin is **global** — it affects every future `delegate_task` in this profile, not just `/improve`. Revert after if you don't want it permanent.

The executor should operate in an **isolated git worktree** (`git worktree add`) so its edits are disposable and your main tree stays clean. Merging is always yours.

### 7. Review (fable-judge)
On executor return, load `fable-judge` and run its Closeout Contract: re-run every claimed check, diff actual vs claimed change, issue `VERIFIED`/`CAVEATS`/`REFUTED`. A `REFUTED` blocks the done state. This is the tech-lead pass shadcn/improve does inline. (Main-thread work you observed directly is already covered by `verification-before-completion` — `fable-judge` is required when the closeout rests on a subagent's self-report.)

### 8. Reconcile (next session)
Re-run `/improve` scoped to open plans: verify DONE plans still hold, investigate BLOCKED ones and rewrite around obstacles, refresh drifted plans (re-stamp git commit), retire findings fixed independently.

## Hard Rules
- Never modifies source directly. Only writes go to `plans/`. Executors edit only in disposable worktrees; merging is always yours.
- Never runs mutating commands during recon — read/search only.
- Never reproduces secret values. Locations + credential types only; rotation always recommended.
- Asked to implement? Decline and point at the plan (or offer `execute`).
- Recovery handle before any destructive executor step: create a branch/commit in the worktree first (SOUL.md §6).

## Common Pitfalls
1. **Forgetting the model pin is global.** Setting `delegation.model` cheap makes *all* subagents cheap, not just `/improve`. Revert if needed.
2. **Writing plans that assume context.** "Fix the TODO at search.ts:31" without excerpting the code fails the weakest-executor test. Inline everything.
3. **No verification gate.** A plan step ending in "should work" is unverifiable. Every step needs a command + expected output.
4. **Skipping the vet step.** Subagents over-report; you must re-read cited locations or you'll plan against a false positive.
5. **Executor making judgment calls.** If a STOP condition hits, the executor must report, not improvise. Cheap models improvise — keep scope tight.
6. **gbrain visibility.** If you commit plans to a git-backed vault, they're invisible to `gbrain sync` until committed. Don't claim queryable without a commit + positive `gbrain query`.

## Verification Checklist
- [ ] Recon used read-only commands only (no tree mutation)
- [ ] Findings carry `file:line` evidence + effort + confidence
- [ ] Vetting re-read every cited location (false positives dropped)
- [ ] Each plan: self-contained, has verification gates, has STOP conditions, git-commit stamp
- [ ] `plans/index.md` lists priority order + dependency graph
- [ ] `delegation.model`/`provider` pinned cheap (or user aware main model is used)
- [ ] Executor ran in isolated worktree; main tree untouched
- [ ] `fable-judge` ran on executor return → verdict recorded
- [ ] Merging decision left to user
