---
name: skill-library
description: Use when deciding whether/how to update, capture, or skip a skill-library entry.
---

# Skill Library Maintenance

How to maintain the skill library. This skill encodes the framework for deciding WHEN to update, WHAT to capture, WHERE to put it, and WHAT TO SKIP.

## Signals That Warrant Action

Any one of these is sufficient — act immediately when you notice it:

| Signal | What it looks like |
|--------|-------------------|
| **User corrected your style/tone/format** | "stop doing X", "too verbose", "don't format like this", "why are you explaining", "just give me the answer", "you always do Y and I hate it", or "remember this" about how you communicate |
| **User corrected your workflow/approach** | A 1-2 sentence correction about the sequence of steps, which tools to use, the order of operations |
| **Non-trivial technique emerged** | A debugging path, workaround, tool-usage pattern, or fix that a future session would benefit from repeating |
| **A loaded/consulted skill was wrong** | A skill had missing steps, wrong commands, outdated info, or unexpected pitfalls |

## Priority Order for Updates

Prefer the **earliest action** that fits:

1. **Patch the currently-loaded skill** — if the new learning relates to a skill that was loaded via `/skill-name` or `skill_view()` in this session, patch that one first
2. **Patch an existing umbrella** — if no loaded skill fits but an existing class-level skill covers the territory, extend it (add subsection, pitfall, or broaden the trigger)
3. **Add a support file under an existing umbrella** — `references/` for detail/transcripts, `templates/` for boilerplate, `scripts/` for re-runnable actions. Add a one-line pointer in parent SKILL.md
4. **Create a new class-level umbrella** — only when no existing skill covers the class

## What NOT to Capture

These become persistent self-imposed constraints that bite later:

- **Environment-dependent failures** — missing binaries, fresh-install errors, path mismatches, "command not found", unconfigured credentials, uninstalled packages. These are not durable rules.
- **Negative claims about tools/features** — "browser tools do not work", "X tool is broken", "cannot use Y from execute_code". These harden into refusals cited against the agent for months after the issue was fixed.
- **Transient errors that resolved** — if retrying worked, the lesson is the retry pattern, not the original failure.
- **One-off task narratives** — "summarize today's market" is not a class of work.

If a tool failed because of setup state: capture the **fix** (install command, config step, env var) under an existing setup or troubleshooting skill. Never "this tool does not work" as a standalone constraint.

## Preference Embedding

When the user expressed a style/format/workflow preference:

- The update belongs in the **SKILL.md body**, not just memory.
- Memory captures "who the user is and what the current situation and state of your operations are."
- Skills capture "how to do this class of task for this user."
- When they complain about how you handled a task, the skill that governs that task needs to carry the lesson.

## External Skill Installer Hygiene

When adding skills through an external installer such as `npx skills add`, verify both the skill content and the agent targets after installation.

- Prefer non-interactive flags when scope is known: `--yes --global --copy`, plus explicit `--skill <name>`.
- Inspect resulting registrations with the installer's list command and verify the actual Hermes skill file exists.
- Watch for installer defaults that select additional agents. If they conflict with Robert's preferences or current policy, remove only the unintended agent target/copy, not the Hermes install.
- Capture the reusable hygiene pattern here; only capture the exact installer transcript in `references/` if it documents a durable CLI quirk.

## Repo-backed Skill Packaging Hygiene

When a skill lives inside a Python/package repo, distinguish three different things before editing:

- the user-facing Hermes skill file;
- package-internal skill/help assets used by the CLI or tests;
- duplicate mirrors created by nested `skills/` directories or symlinked views.

Rules:

- Do not delete a package-internal `SKILL.md` blindly just because it shows up in search results.
- First verify whether packaging or runtime code reads it (`pyproject.toml`, `importlib.resources`, tests, CLI `skill` command).
- If an internal package asset is being indexed as a user-facing duplicate, prefer renaming that packaged asset to an internal filename (for example `INTERNAL_SKILL.md`) and patch every consumer, instead of leaving two public skill names or breaking runtime help.
- After any repo-backed skill cleanup, verify both layers separately: (1) skill registry surface (`skills_list`, `skill_view`) and (2) real runtime behavior (the actual CLI/help/smoke path).
- Watch for overlapping mirrors such as `skills/<category>/<skill>/...` versus `skills/skills/<category>/<skill>/...`; fixing one duplicate may still leave a second source of ambiguity elsewhere.

## Plan-Execution Drift Capture

When a session executes from a written plan and the live system has moved since the plan was written, capture the correction at the class level.

- Before executing a plan literally, verify the key assumptions against live state: target files, config schema, path existence, existing skill coverage, and whether the planned change already landed.
- If the plan is partially complete, internally contradictory, or uses stale interface names, do **not** replay it mechanically. Surface the mismatch and switch to a delta-execution recommendation.
- Config and hook plans deserve an extra gate: verify the live hook/event names against docs or source before editing config.
- If a policy says "warn/confirm" but the live system only supports hard block or no-op, encode the enforceable equivalent and document the semantic downgrade explicitly.
- Good capture shape: a pitfall or explicit review step in the governing execution/planning skill. Bad capture shape: a one-off note saying only that a specific plan was stale.

## Governance Alignment Drift Capture

When a session edits root governance files (`SOUL.md`, profile `SOUL.md`, routing contracts, closeout policy), do not stop at the first corrected artifact.

- After patching the source-of-truth file, sweep the adjacent skill layer for stale canonical terms, old flow rules, and policy-shadow copies.
- Typical drift pattern: root file says `librarian` while an umbrella skill still says `vault profile`; root GitHub flow changes while a behavior skill still teaches the old sequence.
- When two directives look like they compete (for example cost tiering vs preferred provider lane, or `do not surface choices` vs `numbered next steps`), resolve the ambiguity in the governing artifact with one explicit clarifier sentence instead of leaving future sessions to infer precedence.
- Capture the invariant in the class-level maintenance skill, not as a one-off session note.

**Good capture shape:** a pitfall/checklist step like "after governance edits, search related skills for stale aliases and mirrored policy text."
**Bad capture shape:** "today we renamed vault to librarian."

## Support File Types

Skills can be packaged with three kinds of support files:

| Directory | Purpose | Example |
|-----------|---------|---------|
| `references/<topic>.md` | Session-specific detail, condensed knowledge, API docs, domain notes | Error transcripts, reproduction recipes, provider quirks, external authoritative excerpts |
| `templates/<name>.<ext>` | Starter files meant to be copied and modified | Boilerplate configs, scaffolding templates, known-good examples |
| `scripts/<name>.<ext>` | Statically re-runnable actions the skill can invoke directly | Verification scripts, fixture generators, deterministic probes |

## Name Rules for New Skills

- Must be **class-level** — covers a category of work, not a single session
- Must NOT be: a specific PR number, error string, feature codename, library-alone name, or `fix-X / debug-Y / audit-Z-today` session artifact
- If the proposed name only makes sense for today's task, it's wrong

## Protected Skills

These must NOT be edited:

- **Bundled skills** — shipped with Hermes (e.g. `hermes-agent`)
- **Hub-installed skills** — installed via `hermes skills install`

Pinned skills are different: pinning blocks deletion/archive/consolidation, not improvement. If a pinned skill is agent-created and has a missing step, stale command, or pitfall discovered in-session, patch it normally.

If the only skills that need updating are protected bundled/hub-installed skills, say 'Nothing to save.' and stop. If the protected skill exposed a reusable operational pitfall, capture the pattern in the closest non-protected umbrella skill instead of editing the protected skill.

## Source-Grounded Invariants From Protected Skills

When a session requires inspecting Hermes core code or another protected skill, prefer capturing the **implementation invariant** rather than the surface task narrative.

- If a handoff, audit, or user instruction assumes a behavior (for example: profile loading, prompt composition, delivery defaults, or context-file inheritance), verify the behavior against source before encoding the lesson.
- Save the invariant only when it is durable and class-level: e.g. "delegate_task children are created with `skip_context_files=True` and a standalone child prompt, so thin profile designs that assume global SOUL + profile concatenation are unsafe until the implementation changes."
- Do **not** save the one-off session story. Save the reusable gate/check that future sessions should perform before making the same class of change.
- Good capture shape: a pitfall or checklist step in a non-protected umbrella skill. Bad capture shape: "today's refactor failed" or a skill named after the handoff file.

For architecture or persona refactors, this usually means: inspect the actual code path first, then decide whether the planned file writes are safe under the current implementation.

---

## Support Files

- `references/bundled-skills-opt-out.md` — Durable workaround for Hermes' auto-seeding of bundled skills on update; includes the `hermes skills opt-out --remove --yes` command, marker file semantics, re-enable procedure, and pitfalls.

## "Nothing to save" Rule

'Nothing to save.' is a real option but should NOT be the default. If the session ran smoothly with no corrections and produced no new technique, just say 'Nothing to save.' and stop. Otherwise, act.
