---
name: frontend-quality-pass
description: Use when a frontend/web repository looks functional on the surface but fails basic shipping gates, or when the
---

# Frontend Quality Pass

## When to use
Use this when a frontend/web repository looks functional on the surface but fails basic shipping gates, or when the user asks to "clean it up", "execute the improvements", "get it ready", or "make the suggestions real".

Typical signals:
- TypeScript/build/test failures block confidence.
- Repo hygiene is off: important docs/scripts are ignored, temporary artifacts accumulate, staged scope is muddy.
- UI/design issues are real, but release blockers need to be separated from larger refactors.
- Bundle size is suspicious and needs measurement before optimization claims.

## Outcome
Produce a **green, stageable handoff**:
- compiler/lint/tests/build pass,
- intentional files are stageable and tracked,
- temporary scratch artifacts are removed,
- deferred larger refactors are called out explicitly instead of being half-started.

## Core rule
Do not start with aesthetics. Start with **trust-restoring gates**.

Order matters:
1. Repository contract / trackability
2. Compiler/type errors
3. Failing tests
4. Small high-confidence UI hygiene fixes
5. Build and bundle inspection
6. Final staged-scope audit

## Execution sequence

### 1) Establish the contract first
- Read project routing/governance files first (`AGENTS.md`, `CONTEXT.md`, `STRATEGY.md` when present).
- Create a durable plan file for non-trivial work.
- Define success as a finite set of commands and repo-state checks.

### 2) Fix trackability before polish
If important docs, scripts, or governance files are ignored by `.gitignore`, repair that before doing broader work.

Why:
- untracked canonical files create fake progress,
- verification can pass while the real handoff is incomplete,
- later staging becomes noisy and error-prone.

Checks:
- confirm critical files are no longer ignored,
- confirm generated output directories remain ignored when appropriate,
- stage only intentional deliverables.

### 3) Clear compiler errors before judging structure
Fix TypeScript/compile issues before making broader architectural comments. Broken types distort everything downstream.

Principles:
- make the smallest correct fix,
- prefer aligning tests/types/components over adding fallback complexity,
- keep fixes surgical.

### 4) Repair tests to match product intent, not stale wording
When render/integration tests fail after UI/content evolution:
- determine whether the product changed intentionally,
- update the test if the behavior/copy changed for valid reasons,
- only change product code when the test reveals a real regression.

Pitfall:
- Do not preserve stale assertions just because they used to pass.

### 5) Separate release blockers from deep refactors
Call the shot clearly:
- **required now**: issues that block trust, correctness, tracking, or buildability.
- **defer intentionally**: large component decomposition, routing redesign, semantic cleanup across many pages, package-manager normalization unless currently breaking installs/CI.

Do not mix these. Users need one clean pass first.

### 6) Use high-confidence design fixes only in the same pass
Safe same-pass fixes:
- remove raw design-token violations,
- align a component to existing primitives,
- reduce obvious duplication when needed for correctness.

Unsafe same-pass fixes:
- broad visual rewrites,
- cross-app semantic refactors,
- "while we're here" redesigns.

### 7) Measure performance before claiming improvement
For bundle/perf work:
- run the build,
- inspect actual emitted chunk sizes,
- prefer chunk-boundary changes with clear caching value,
- report the measured delta, not a vibe.

Good pattern:
- isolate stable vendor families (react/ui/math/charts) when the toolchain supports it.

### 8) Final hygiene gate before closeout
Before declaring success:
- `git diff --check`
- staged diff check
- full compiler/lint/test/build rerun
- final `git status --short`
- confirm no temporary scratch files remain
- confirm no generated artifacts were accidentally staged

## Pitfalls
- Passing app gates while critical docs/scripts are still ignored.
- Reporting success before `git diff --check` on both working tree and staged changes.
- Letting temporary planning/progress scratch files survive in repo root.
- Sliding from a quality pass into an unbounded redesign.
- Treating build success as proof that the staged handoff is clean.

## Closeout pattern
Report in four buckets:
1. What was actually changed
2. Exact verification evidence
3. What was intentionally deferred
4. The best next three follow-up moves

Keep the recommendation decisive: one obvious next step, one adjacent step, one divergence step.

## Support files
- `references/statisti-kal-example.md` — concrete example of a frontend quality pass covering ignore-rule repair, test alignment, bundle chunking, and final staged-scope verification.
