---
name: hermes-multi-profile-skills
description: Use when managing or syncing skills across multiple Hermes profiles.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profiles, skills, synchronization, configuration, multi-profile]
    related_skills: [skill-library, hermes-agent, hermes-agent-skill-authoring]
---

# Hermes Multi-Profile Skill Management

Managing skills across multiple Hermes profiles (vault, engineer, reviewer, strategist, writer, etc.) without drift.

## The Problem

Each Hermes profile has its own **profile-scoped skills directory**:
```
~/.hermes/profiles/<name>/skills/
```

When a skill is updated in one profile (e.g., `vault`), the change **only affects that profile**. Other profiles either:
- Have stale local copies of the same skill
- Fall back to the global `~/.hermes/skills/` (symlinked to `/c/Users/Tiger/AI Hub/Global Skills/`)
- See different skill versions depending on load order

This causes **inconsistent behavior** across profiles — the same skill name produces different results.

## Root Cause (Architecture)

From `hermes_constants.py` and `agent/skill_utils.py`:
- `get_skills_dir()` → `get_hermes_home() / "skills"` → profile-scoped
- `scan_skill_commands()` scans local dir first, then `skills.external_dirs` from config.yaml
- No built-in sync, watch, or propagation mechanism exists

## Solution Pattern: Canonical Global Skills Directory via Symlink\n\n**The current mechanism** is to maintain a single canonical skill directory at `C:/Users/Tiger/Agents/Global-Skills` and symlink the Hermes skills directory (`~/.hermes/skills`) to it. This ensures all profiles and any external agents that follow the same skill format use the exact same skill set.\n\n### 1. Set Up the Canonical Skill Directory\nEnsure the global skill directory exists and contains all skills:\n```bash\n# The directory should already exist from prior consolidation\nls -la /c/Users/Tiger/Agents/Global-Skills\n```\n\n### 2. Symlink the Hermes Skills Directory\nReplace the local `skills` directory (or symlink) with a symlink to the canonical location:\n```bash\n# Backup any existing skills directory if needed\nmv ~/.hermes/skills ~/.hermes/skills.backup.$(date +%s)  # if it's a real directory\nln -sf /c/Users/Tiger/Agents/Global-Skills ~/.hermes/skills\n```\n\n### 3. Configure Profiles to Use the Symlinked Skills\nNo `external_dirs` configuration is needed; ensure it is empty in each profile's config.yaml:\n```yaml\nskills:\n  external_dirs: []\n```\nYou can clear it via CLI:\n```bash\nhermes config set skills.external_dirs '[]' --profile <profile_name>\n```\nDo this for each profile (or rely on the default empty list).\n\n### 4. Update Skills Only in the Canonical Location\n- Use `hermes skills install/update` from any profile (writes to `~/.hermes/skills/` which symlinks to the canonical directory)\n- Or write directly to `/c/Users/Tiger/Agents/Global-Skills/<category>/<skill-name>/`\n- All profiles instantly see updates on next skill scan (`/reload-skills` or new session)\n\n### 5. Profile-Specific Overrides Still Work\nIf a profile needs a unique skill variant, it keeps it in its own `profiles/<name>/skills/` — **local dir is scanned first**, so profile-local skills take precedence over the symlinked global skills.\n\n### 6. Vault Skills Location\nVault‑related skills reside under the top‑level `vault/` directory (e.g., `vault/SKILL.md` for the obsidian skill, `vault/vault-ingestion/`, etc.). This keeps all vault‑specific skills together at the class level. This structure was adopted per user preference to eliminate unnecessary nesting (e.g., moving from `note-taking/obsidian/` to flat `vault/`).\n\n### 7. Superpowers Skills Organization\nAll skills from the obra/Superpowers collection are grouped under the top‑level `superpowers/` directory per user request. This includes: test-driven-development, systematic-debugging, verification-before-completion, brainstorming, writing-plans, executing-plans, dispatching-parallel-agents, requesting-code-review, receiving-code-review, using-git-worktrees, finishing-a-development-branch, subagent-driven-development, writing-skills, using-superpowers.\n\n### 8. Browser Skills Organization\nBrowser‑related skills are consolidated under the `browser/` directory. The direct browser control skill resides at `browser/SKILL.md`, while the Hermes‑Browser Use integration lives at `browser/browser-use-hermes-integration/` per user preference to move integration-specific skills into relevant tool domains.\n\n### 9. Removal of Unused Categories\nEntire skill categories that are no longer used (such as `apple/`) have been removed to reduce noise and maintenance overhead, per user direction.

## Verification Checklist

After setup, verify all profiles see identical skill sets:
```bash
hermes skills list --profile vault
hermes skills list --profile engineer
hermes skills list --profile reviewer
# All should show identical skills sourced from the canonical Global-Skills directory
```

## Profile Rename / Deletion Audits

When a profile has been renamed or replaced and Robert wants to delete the old profile, do not compare only `config.yaml`. Audit aliases, normalized profile files, hooks, profile-local skills, memories, `state.db`, cron jobs, scripts/templates/runtime directories, auth provider coverage, gateway/channel state, and any profile-owned git working trees. Use `references/profile-rename-deletion-audit.md` for the checklist and deletion-readiness wording.

## Alternative: Symlink Approach (Simpler, Less Flexible)

If zero-config is preferred and profile-specific overrides are never needed:
```bash
for p in vault engineer reviewer strategist writer; do
  rm -rf "/c/Users/Tiger/AppData/Local/hermes/profiles/$p/skills"
  ln -s "/c/Users/Tiger/AppData/Local/hermes/shared-skills" "/c/Users/Tiger/AppData/Local/hermes/profiles/$p/skills"
done
```
**Trade-off:** Any profile updating a skill affects all profiles immediately. No override capability.

## Key Implementation Details

### Skill Discovery Order (from `agent/skill_commands.py::scan_skill_commands`)
1. Local profile skills dir (`~/.hermes/profiles/<name>/skills/`)
2. Each directory in `skills.external_dirs` (in config order)
3. Global `~/.hermes/skills/` is **not** scanned by default unless listed in `external_dirs`

### Config Cache Behavior
`get_external_skills_dirs()` caches results keyed on `config.yaml` mtime — changes picked up automatically on next scan.

### Platform-Specific Disabled Skills
Each profile can have its own `skills.platform_disabled` mapping — shared skills respect the consuming profile's disabled list.

## Pitfalls to Avoid

| Pitfall | Why It Fails | Fix |
|---------|--------------|-----|
| Editing global `~/.hermes/skills/` directly | Other profiles don't auto-reload; symlink may point elsewhere | Use `shared-skills/` as canonical; update there |
| Assuming `hermes skills update` propagates | It only updates the active profile's skills dir | Run from default profile targeting `shared-skills/`, or write directly |
| Forgetting profile-specific `disabled` lists | A skill enabled globally may be disabled in one profile | Check `hermes skills config` per profile after sync |
| Using absolute paths in `external_dirs` that differ across machines | Breaks portability | Use paths relative to Hermes root (`shared-skills`) |
| Replacing a junctioned `skills/` directory with a copied real directory during profile rename | The successor profile silently drifts from the shared skill source even if it works today | Preserve the existing directory as a timestamped backup, recreate the same junction target, then verify both profiles report the same skill count |
| Declaring a renamed successor profile deletion-ready after only checking skills/config | Profile-local memories, scripts, templates, auth pools, session DBs, and aliases can still be old-profile-only | Run the deletion-readiness checklist in `references/profile-renaming-junction-migration.md`; distinguish operational switchover from no-loss deletion |
| Having duplicate skill categories (e.g., both `obsidian/` and `note-taking/obsidian/`) | Causes ambiguity and splits related skills; complicates discovery | Keep skills under a single canonical category; move or delete duplicates; prefer nesting under a broader domain (e.g., place obsidian skills under `note-taking/`) |

## Related Files\n\n- `references/shared-skills-setup.md` — Step-by-step setup transcript and verification\n- `references/global-symlink-approach.md` — Global symlink approach for shared skills (alternative to external_dirs)\n- `references/profile-renaming-junction-migration.md` — Checklist and Windows junction pattern for replacing an old profile with a renamed successor while preserving shared skills and deletion readiness.\n- `templates/shared-skills-config.yaml` — Minimal config snippet to add to each profile\n- `scripts/verify-skill-sync.py` — Verification script to run after setup

## When to Use This Skill

- Setting up a new Hermes profile that should share the team/organization skill set
- Debugging inconsistent skill behavior across profiles
- Establishing a canonical skill source for CI/CD or team distribution
- Migrating from ad-hoc per-profile skills to managed shared skills