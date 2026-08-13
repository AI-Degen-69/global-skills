---
name: skill-maintenance
description: Use when auditing or canonicalizing skills across Hermes profiles.
triggers:
  - "Audit skills or skill audit across profiles"
  - "Canonicalize or fix skill names/mismatches between shared and local"
  - "Missing skills in CLI or skills not loading from shared-skills"
  - "Duplicate frontmatter names in shared-skills"
  - "Audit script giving false positives/negatives"
  - "Profile skill drift from shared-skills canonical source"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, audit, canonicalization, maintenance, multi-profile, shared-skills]
    related_skills: [skill-library, hermes-multi-profile-skills, skill-audit-weekly]
---

# Skill Maintenance & Audit

Maintain skill hygiene across a multi-profile Hermes setup with a `shared-skills` canonical source and per-profile `skills/` directories.

## When to Use

- Weekly/monthly skill audit cron runs (see `skill-audit-weekly`)
- User reports "skill not loading" or "missing from CLI"
- After adding new profiles or modifying `skills.external_dirs`
- Before/after `hermes update` which seeds bundled skills
- When audit script reports false positives

## Core Concepts

### Skill Identity = Frontmatter `name:`, Not Directory Name
The CLI (`hermes skills list`, `/skill-name` dispatch, `skills_list` tool) indexes by **frontmatter `name:`**. Directory names are only filesystem handles. Mismatches cause:
- False "missing from CLI" reports (audit compares dir names)
- Duplicate entries when same frontmatter name appears in two directories
- Local overrides invisible to diff logic (same name, different dir)

**Always compare by frontmatter name.**

### Platform Filtering Is Correct, Not a Bug
Skills with `platforms: [macos]` (e.g., `macos-computer-use`, `imessage`) are **correctly hidden** on Windows. Do not report these as "missing from CLI".

### Audit Script Must Use `skills_list` Tool, Not CLI Table Parsing
The `hermes skills list` output truncates long names with `...`. Parsing the table loses fidelity.
**Use `skills_list()` tool directly** (returns JSON with full names).

```python
from tools.skills_tool import skills_list
result = json.loads(skills_list())
skills = {s["name"] for s in result["skills"]}
```

### Canonical Source Must Be Discovered From Live `skills.external_dirs`
Do **not** hardcode `~/.hermes/shared-skills` as the canonical source unless the live profile configs actually point there. In this installation the real canonical directory is `C:/Users/Tiger/Agents/Global-Skills`, and hardcoding `shared-skills` produced a false `shared_skills_count: 0` outage.

Audit flow:
1. Read each active profile's `config.yaml`
2. Parse `skills.external_dirs`
3. Union all existing configured canonical dirs
4. Fall back to `~/.hermes/shared-skills` only if it actually exists

### Shared Skill Discovery Must Be Recursive
Some valid shared skills live deeper than one category level, e.g. `integrations/handoffs/load-latest-handoff` and `integrations/handoffs/unified-handoff`.
A shallow `shared-skills/*/*/SKILL.md` scan undercounts the canonical source and creates false `extra_skills_in_cli` findings. Use recursive `rglob('SKILL.md')` discovery under each canonical dir.

### Repo-Backed Skill Audits Need Three Truth Surfaces
When auditing or pruning a vendored skill repo (for example `Global-Skills` or a repo-backed pack like `gstack/`), classify evidence before deleting or declaring success:

1. **Hermes load surface** — what `skills_list()` and `skill_view()` can actually load by skill name.
2. **Git truth** — what the repo tracks right now (`git status`, `git ls-files`, `git show HEAD:path`). This catches cases where a filesystem scan says "empty" but git proves a real tracked skill exists or a prior move/delete did not persist the way you thought.
3. **Config suppression truth** — whether the user really wants the skill gone from disk, or only hidden from Hermes. For suppression, prefer `config.yaml -> skills.disabled` via `hermes config set`, not editing bundled repo trees.

Use all three before pruning. Filesystem-only checks (`find`, shallow dir counts, `0 SKILL.md` at one depth) are not enough for repo-backed packs and can produce false deletions or false success claims.

## Canonicalization Checklist

### 1. Directory Name == Frontmatter Name
For every skill in `shared-skills/`:
- Directory name should match `name:` in SKILL.md
- Remove prefixes like `superpowers-` that don't appear in frontmatter
- If two directories have same frontmatter name -> **delete one** (keep the more complete version)

### 2. Resolve Duplicate Frontmatter Names
Scan `shared-skills/` for duplicate `name:` values:
```bash
# Find duplicates
for cat in shared-skills/*/; do
  for skill in "$cat"*/; do
    grep "^name:" "$skill/SKILL.md" | sed 's/name: *//'
  done
done | sort | uniq -d
```
Common duplicates from `superpowers-` prefix:
- `requesting-code-review` (2 dirs)
- `systematic-debugging` (2 dirs)  
- `test-driven-development` (2 dirs)

### 3. Sync Local Overrides to Shared
Skills existing in multiple profiles' local `skills/` but not in `shared-skills`:
- `spike`, `simplify-code` -> add to `shared-skills/software-development/`
- `subagent-driven-development`, `writing-plans` -> ensure frontmatter parity with local versions
- Vault-specific skills (e.g., `compound-engineering-workflow`) -> review for canonization or document as vault-only

### 4. Verify `external_dirs` Config
Every profile's `config.yaml` must have:
```yaml
skills:
  external_dirs:
    - "C:/Users/Tiger/AppData/Local/hermes/shared-skills"
```

## Common Pitfalls

| Symptom | Actual Cause | Fix |
|---------|--------------|-----|
| "10 shared skills missing from CLI" | Audit parsed truncated table names | Use `skills_list()` JSON |
| "`superpowers-x` missing" | Dir name `superpowers-x` vs frontmatter `x` | Rename dir to match frontmatter |
| "github-repo-management missing from 4 profiles" | Platform filter? No -- check audit logic | Audit compared dir names, not frontmatter |
| "imessage missing from vault" | `platforms: [macos]` on Windows | Expected -- do not add to shared for Windows |
| Valid root-level shared skills show as `extra_skills_in_cli` | Audit only scans `shared-skills/*/*/SKILL.md` and misses `shared-skills/<skill>/SKILL.md` | Support both category/skill and root-level skill layouts |
| Profiles show `has_external_dirs: false` despite a visible shared-skills block | Audit only detects inline YAML lists | Parse block-style `external_dirs:` children or use YAML parsing |
| Kanban or platform-specific skills show as missing | Audit treats `skills_list()` as a raw filesystem dump | Mirror offer filters: split platform-hidden, environment-hidden, and profile-disabled skills out of actionable missing drift |
| Common local-only skills appear in every active profile | Shared promotion candidate, not deletion candidate | Hash directories across profiles; if identical, promote to `shared-skills` conservatively |
| **`/skill-name` command loads wrong skill or fails** | Duplicate frontmatter `name:` in multiple dirs; filesystem iteration order determines which wins, so CLI and gateway can register different skills | 1. Find dupes: `grep -r "^name:" shared-skills/*/SKILL.md | sort | uniq -d` 2. Rename dir to match frontmatter OR change frontmatter name to be unique (e.g., `superpowers-requesting-code-review`) 3. Remove redundant duplicate 4. Restart gateway (`hermes gateway restart`) and `/new` in Desktop |

| **Ambiguous skill name** errors when loading skills | Skills loaded from both `skills/` and `external_dirs` pointing to different locations | Choose ONE canonical source: either symlink `~/.hermes/skills/` to the canonical source OR configure `external_dirs` to point to it, but NOT both |
| **Ambiguous skill name** persists even after clearing `external_dirs` | A vendored repo under `skills/<category>/<repo>/` contains both a repo-root `SKILL.md` and a nested real skill at `skills/<name>/SKILL.md`, so the index sees two skills with the same frontmatter name from one tree | Keep the canonical packaged skill; remove the redundant repo-root `SKILL.md` only if another umbrella skill already covers that repo-root content. Verify with `skill_view(name='<skill>')` and a focused filesystem search for `SKILL.md` under that repo. |
| **Bare skill load turns ambiguous right after generating Hermes-host docs** | The repo now contains both source skills and generated `.hermes/skills/*/SKILL.md` outputs, and the source umbrella plus generated umbrella expose the same frontmatter name | Treat this as a verification-path issue, not an immediate cleanup bug. Validate the generated skill with an explicit categorized/generated path such as `gstack/.hermes/skills/gstack`, or inspect the generated file directly. See `references/hermes-host-generated-skill-collisions.md`. |
| A repo-backed skill pack looks "wrong" because it contains `repo/.hermes/skills/...` under the skill tree | Hermes-host generation wrote packaged skills back into the vendored repo, so the tree now contains both the source repo and generated Hermes outputs | Do not flatten or delete on sight. First classify the layout: source repo root, generated `.hermes/skills/<skill>/SKILL.md` outputs, and any repo-root umbrella `SKILL.md`. Then make routing explicit in AGENTS.md so future agents invoke the generated skills intentionally instead of guessing from the raw filesystem. See `references/repo-generated-skill-pack-layouts.md`. |
| A verification command from AGENTS.md fails with "file not found" under `AppData/Local/hermes/scripts` | The governance note is written relative to the active profile/project, but the operator ran it from the install root and assumed a global `scripts/` directory | Resolve the real script location from the active profile or repo before encoding the command in closeout. For profile-scoped checks, prefer the profile-local path (for example `profiles/<name>/scripts/_precommit_guard.py`) and report why the root-level path was wrong. |

For the detailed 2026-06-20 false-positive taxonomy, see `references/drift-audit-false-positive-patterns.md`.

## Audit Script Template

See `scripts/skill-audit-collector.py` (in `scripts/` of this skill) -- uses `skills_list()` tool, compares by frontmatter name, detects name mismatches.

## Verification Steps

After changes, run fixed audit:
```bash
cd ~/AppData/Local/hermes && python scripts/skill-audit-collector.py
```
Expected: `shared_skills_missing_from_cli` only contains platform-filtered skills; `name_mismatches` empty; `local_overrides` only truly vault-specific skills.

## References
- `references/skill-audit-architecture.md` -- Data flow: shared-skills -> external_dirs -> profile skills -> CLI
- `references/duplicate-resolution-log.md` -- Historical duplicate resolutions
- `references/slash-command-collision-reproduction.md` -- Slash command collision from duplicate frontmatter names (2026-06-18)
- `references/browser-harness-repo-embedded-skill.md` -- Repair pattern for repo-backed skills that ship both root and nested `SKILL.md` files, including symlink-safe cleanup after upstream updates
- `references/hermes-host-generated-skill-collisions.md` -- Verification pattern when generated `.hermes/skills/*` outputs coexist with source skills and make bare loads ambiguous
- `references/repo-generated-skill-pack-layouts.md` -- How to classify vendored repo-backed skill packs, generated `.hermes` outputs, AGENTS routing updates, and profile-local verification paths
- `scripts/skill-audit-collector.py` -- Fixed audit script (source of truth for cron)