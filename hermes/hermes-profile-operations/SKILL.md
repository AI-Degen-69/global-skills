---
name: hermes-profile-operations
category: devops
description: Use when creating, cloning, syncing, or maintaining Hermes profiles.
---

# Skill: hermes-profile-operations

Class-level skill for Hermes profile lifecycle management: create, clone, sync, and maintain profiles across machines.

## Triggers
- Creating a new profile from an existing one
- Retiring/discontinuing a profile after another profile inherits its role
- Setting up profile-specific symlinks/junctions (vault, skills, configs)
- Bulk path replacement in config.yaml when renaming profiles
- Profile migration between machines
- Repointing profile aliases so old commands target the successor profile

## Core Techniques

### Clone Profile with Symlinks
When creating a new profile from a template (e.g., `vault` → `librarian`):

1. **Create profile directory** — `mkdir -p ~/.hermes/profiles/<new-name>`
2. **Copy config & SOUL** — Selective copy (config.yaml, SOUL.md, hooks/, AGENTS.md, profile.yaml, README.md, .env, shell-hooks-allowlist.json). Skip massive state files (state.db, models_dev_cache.json, .skills_prompt_snapshot.json).
3. **Bulk path replace in config.yaml** — `sed -i 's|old-profile-path|new-profile-path|g' config.yaml`
   - Targets: `terminal.cwd`, `hooks.pre_tool_call.command` paths
4. **Update SOUL.md** — Change `# Profile: OldName` → `# Profile: NewName`, update `Role` line
5. **Symlink shared resources**:
   - `ln -sf /path/to/Vault ~/.hermes/profiles/<new-name>/Vault`
   - `ln -sf /path/to/Agent-Skills ~/.hermes/profiles/<new-name>/skills`
6. **Verify** — Check `cwd`, hook paths, symlink targets

### Retire a Profile into a Successor
When retiring an old profile after a successor inherits its role (e.g., `vault` → `librarian`), prefer a graceful move-out over immediate deletion:

1. **Snapshot successor first** — Copy the successor's current `config.yaml`, `auth.json`, `SOUL.md`, `AGENTS.md`, `profile.yaml`, `.env`, `shell-hooks-allowlist.json`, and local `memories/`, `scripts/`, `templates/`, `runtime/`, `cron/` into `profile-retirement-backups/<successor>-pre-<old>-retirement-<timestamp>/`.
2. **Migrate role assets** — Copy old-profile `memories/*.md`, `scripts/`, `templates/`, and `runtime/` into the successor; normalize absolute old-profile paths in copied scripts/configs to the successor profile path.
3. **Merge auth, do not overwrite blindly** — Merge `auth.json` `providers` and `credential_pool` keys from old into successor, preserving successor credentials where keys already exist.
4. **Archive old session state** — Copy old `state.db`, `state.db-wal`, `state.db-shm`, `channel_directory.json`, and `gateway_state.json` into `profiles/<successor>/retired-<old>-session-archive/` instead of replacing successor `state.db`.
5. **Repoint aliases before removing old profile** — Use `hermes profile alias <old> --remove`, then `hermes profile alias <successor> --name <old>` so old wrapper commands route to the successor.
6. **Move, then verify** — Rename/move `profiles/<old>` to `profile-retirement-backups/<old>-profile-retired-backup-<timestamp>` rather than deleting immediately. Verify `hermes profile show <old>` fails and `hermes profile show <successor>` shows the expected alias.

### Windows Junction / `mklink` Notes
- On Git Bash/MSYS, `cmd.exe /C mklink /J` is sensitive to slash/backslash conversion. The safest pattern is to call `cmd.exe` from Python `subprocess.run([...])` with native `C:\\...` paths, or use Windows-native commands directly.
- If a malformed relative junction is created, remove only the malformed junction entry before retrying. Do not delete the target directory.
- Confirm both POSIX view (`ls -ld`) and Windows reparse view (`cmd /c dir /AL ...`) when matching another profile's junction attributes.

### Align Open Second Brain Across Existing Profiles
When bringing specialist profiles into parity with the default profile's OSB setup on Windows:

1. **Use the live profile tree under `%HERMES_HOME%\\profiles\\<name>`** — on this install topology the real profiles live under `C:\\Users\\Tiger\\AppData\\Local\\hermes\\profiles`, not a legacy `~/.hermes/profiles` path.
2. **Audit each profile's own `config.yaml` directly** for:
   - `memory.provider: open-second-brain`
   - `memory.flush_min_turns: 6`
   - `memory.nudge_interval: 10`
   - `mcp_servers.open-second-brain` with `command: o2b`, `args: [mcp, --scope, writer, --vault, /c/Users/Tiger/Vault]`, `enabled: true`, `timeout: 30`
   - top-level `MEMORY_PROVIDER: open-second-brain`
3. **Create a per-profile recovery copy beside the file before editing** (for example `config.pre-osb-fix-<timestamp>.yaml`).
4. **Patch the profile files directly and read them back**; do not rely on a generic `hermes config path` probe to prove which profile file is being targeted.
5. **Verify with both YAML read-back and profile-level health checks** such as `hermes profile list`, plus any local profile guard script (for example librarian's `_precommit_guard.py`).

### Pitfalls to Avoid
- **Don't `cp -r` the whole profile as the only backup** — state.db, caches, logs, and junctions can make it slow or confusing; use a targeted successor snapshot plus a move-out backup of the old profile.
- **Don't rely solely on `hermes profile export` for large profiles** — if it is slow/hangs, use simple filesystem copy/move commands into a timestamped retirement folder.
- **Don't overwrite successor session DB** — archive old session state separately so the successor keeps its active history while preserving old recall data.
- **Don't forget hook paths** — pre_tool_call hooks reference absolute paths to the old profile.
- **Don't leave stale aliases** — old wrapper scripts must be removed or repointed before the old profile leaves `profiles/`.
- **Clean up auto-created dirs before symlinking/junctioning** — Hermes auto-creates `vault/`, `skills/` dirs on first run; remove/backup them before creating links.
- **Use `ln -sf` only for POSIX symlinks** — On Windows, match the existing profile's reparse-point style (often a junction via `mklink /J`) rather than assuming a POSIX symlink.

## Related Skills
- `hermes-multi-profile-skills` — manages skill sync across profiles (complementary)
- `hermes-agent` — general Hermes configuration (bundled, protected)

## References
- `references/clone-profile-with-vault-symlink.md` — step-by-step recipe from vault→librarian session
- `references/profile-retirement-checklist.md` — graceful old-profile retirement checklist: migrate assets, archive sessions, repoint aliases, move old profile to backup, verify clean discontinuation
