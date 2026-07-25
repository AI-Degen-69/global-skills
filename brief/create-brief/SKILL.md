---
name: create-brief
description: Create a session brief for any project.
version: 0.2.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Brief, Handoff, Session, Context]
---

# Create Brief

Creates one brief document that is both machine-parseable (YAML frontmatter)
and human-readable. Written to the canonical briefs directory. Includes a
verification checklist, 3 follow-up options with a recommendation, and
integrates with `load-brief` for session resumption.

**Generic by design.** This skill is NOT tied to any project. It detects the
active repo from git (cwd's repo root, or `--project-root`), derives the
project name from `package.json`/`pyproject.toml`, and derives verification
commands from the project's manifest (`npm run build`/`test`/`lint`,
`pytest`, `python -m build`, etc.). Design-system-specific checks (Tailwind
raw-color / signature-element guards) are opt-in via `--design-system` and
only run when that flag is passed.

> The term "handoff" is now referred to as "brief" in this skill and
> related skills.

## When to Use
- Ending a session (manual or context limit)
- Phase transition (plan→work, work→review, review→compound)
- Subagent completion
- Any point where a fresh agent/session needs to continue from exactly here
- **When to use session-brief instead**: if the session was primarily discussion,
  planning, or decision-making without implementation work, use the
  `session-brief` skill for a lighter-weight, conversation-focused brief.

## Prerequisites
- Git repo at/under the cwd (or pass `--project-root`).
- Python 3.10+. No third-party deps (stdlib only).
- The `load-brief` skill present at
  `C:/Users/Tiger/AppData/Local/hermes/skills/brief/load-brief/`.

## How to Run
Invoke the bundled script through the `terminal` tool:

```bash
# From the repo you want to brief (or pass --project-root)
python "C:/Users/Tiger/AppData/Local/hermes/skills/brief/create-brief/scripts/create_brief.py" \
  --phase-from discuss-gate-retest \
  --phase-to run-commit-harness \
  --session-id poly-taker-gate-retest-20260722

# Opt-in design-system checks (statistics-style repos only):
#   --design-system
# Attach session notes (repeatable):
#   --note "Harness proven on 15 windows: ungated 80% / gated 100%"
```

The script auto-detects repo root, project name, ecosystem verify commands,
and writes the brief to `C:/Users/Tiger/AppData/Local/hermes/briefs/`
with the filename pattern
`brief-{profile}-{project}-{phase_from}-to-{phase_to}-{YYYYMMDD-HHMM}.md`.

## Quick Reference
```
--phase-from   source phase (required)
--phase-to     target phase  (required)
--session-id   session identifier (required)
--profile      profile name (default: default)
--project-root explicit repo root (else git toplevel of cwd, else cwd)
--design-system opt-in Tailwind/design-system guards
--note         repeatable session-note line
```
Canonical dir: `C:/Users/Tiger/AppData/Local/hermes/briefs/`
Load: `python "C:/Users/Tiger/AppData/Local/hermes/skills/brief/load-brief/scripts/load_brief.py"`

## Procedure
1. **Be in or point at the repo.** `cd` into the project, or pass
   `--project-root <abs-path>`. The script resolves git toplevel itself.
2. **Run the script** with `--phase-from`, `--phase-to`, `--session-id`.
   Add `--note` lines for anything the auto-derived sections miss.
3. **Script collects** git metadata, derives ecosystem verify commands,
   runs them, and generates the brief with machine frontmatter + human
   sections (context, done, current state, blocking decisions, risks,
   verification checklist, quick-start).
4. **Read the verification message** — it prints each check's pass/fail.
   Fill in the `*add row*` placeholders (Blocking Decisions / Risks) with
   real session content before handing off.
5. **Next agent loads it** via `load-brief`, which reads the most
   recent brief, displays it, and (per its own contract) deletes it after
   consumption.

## Pitfalls
- **Don't hardcode a project.** The old v0.1 script pinned
  `PROJECT_ROOT=C:/Users/Tiger/Agents/Projects/statistics` and npm-only
  checks — running it on any other repo produced a broken, off-topic
  brief. v0.2 derives everything from the live repo. If you ever see a
  brief referencing `statistics` or `npm run build` on a Python repo,
  you're on the old script — replace it.
- **Verification commands are derived, not assumed.** On a repo with no
  `build`/`test`/`lint` script, those checks are simply omitted; only
  `git status` (git_clean) always runs.
- **Design-system checks need `--design-system`.** Without it, the
  slate/zinc/signature-element greps never fire — that's intended, so
  non-design repos don't get false failures.
- **Placeholders remain for you to fill.** Blocking Decisions / Risks
  ship as `*add row*` stubs; the script can't invent your decisions.
- **Load path is `brief/load-brief`, NOT `devops/load-brief`.**
  The v0.1 SKILL.md referenced a wrong path.

## Verification
A correct v0.2 run is proven by:
```bash
python "C:/Users/Tiger/AppData/Local/hermes/skills/brief/create-brief/scripts/create_brief.py" \
  --phase-from test --phase-to test --session-id selfcheck-001 \
  --project-root "C:/Users/Tiger/Agents/Projects/AI Trading/polymarket-taker"
```
Positive evidence: the printed brief path resolves, its frontmatter
`project: polymarket-taker` (not `statistics`), and its body contains
no `npm run build` line (Python repo) unless one exists in `pyproject.toml`.
