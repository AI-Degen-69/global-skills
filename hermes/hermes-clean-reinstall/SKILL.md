---
name: hermes-clean-reinstall
description: Use when reinstalling Hermes cleanly on Linux/WSL without losing live state.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, reinstall, wsl, linux, recovery, setup]
    related_skills: [hermes-agent, hermes-profile-operations, messaging-gateway-operations]
---

# Hermes Clean Reinstall

## Overview

Use this when the user wants a fresh Hermes install on Linux or WSL, but an existing `~/.hermes` may already contain live state: auth, gateway config, cron jobs, profiles, sessions, or plugins.

The key rule: **do not trust the installer to create a clean environment if `~/.hermes` already exists**. The installer will reuse that home, keep old `.env` / `config.yaml`, and may stop in interactive prompts caused by leftover messaging tokens or auth state.

## When to Use

- The user wants to "start over" or "uninstall the old one and install a new one".
- `hermes status` shows unexpected old state: configured messaging, cron jobs, sessions, profiles, or stale auth.
- The installer reports `Existing installation found, updating...` when a clean install was expected.
- The setup flow gets dragged into old provider auth, old gateway prompts, or migrated legacy config.

## Success Criteria

A real clean reinstall means:
- the previous Hermes home is preserved under a recovery path;
- a new `~/.hermes` is created from scratch;
- `hermes status` shows no old sessions, cron jobs, messaging config, or stale profiles;
- the new install can proceed through auth and setup as a first-run environment.

## Procedure

### 1. Inspect before touching anything

Verify whether this is actually a live environment.

Check for:
- `hermes status`
- `hermes doctor`
- size and structure of `~/.hermes`
- configured gateway, sessions, cron jobs, auth providers, and profiles

If it is a real environment, do **not** delete it blindly.

### 2. Create a recovery handle first

Before any destructive change, preserve the old home by moving it aside with a timestamped path.

Example:

```bash
wsl.exe bash -lc 'systemctl --user stop hermes-gateway 2>/dev/null || true; mv /home/<user>/.hermes /home/<user>/.hermes-backup-YYYYMMDD-HHMMSS'
```

Preferred recovery shape:
- `/home/<user>/.hermes-backup-YYYYMMDD-HHMMSS`

Report that exact backup path in closeout.

### 3. Make sure the active path is truly gone

After the move, verify that `/home/<user>/.hermes` no longer exists before rerunning the installer.

If the old home is still present, the installer will reuse it and the reinstall is **not** clean.

### 4. Rerun the installer non-interactively first

Use the official installer with `--skip-setup` so the base install completes without pausing in the wizard.

```bash
wsl.exe bash -lc 'curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup'
```

This avoids getting stuck mid-install on provider choice or gateway prompts.

### 5. Normalize the new install

Run:

```bash
wsl.exe bash -lc 'source ~/.bashrc >/dev/null 2>&1 || true; hermes doctor --fix'
```

Then verify the new home is clean:

```bash
wsl.exe bash -lc 'source ~/.bashrc >/dev/null 2>&1 || true; hermes status'
```

Expected signs of a clean state:
- gateway stopped
- no messaging platforms configured
- zero cron jobs
- zero sessions
- no stale auth providers configured
- default/built-in memory only unless intentionally changed

### 6. Do provider auth only after the clean install is verified

For OpenAI Codex, start auth after the clean install is in place:

```bash
wsl.exe bash -lc 'source ~/.bashrc >/dev/null 2>&1 || true; hermes auth add openai-codex'
```

If using background execution, immediately poll for the device code and URL so the user sees progress and can act.

### 7. Continue with plugin and workflow setup only after auth works

Do not move into plugin installs or workflow setup until a basic model call succeeds.

## Common Pitfalls

- **Big one:** rerunning the installer while `~/.hermes` still exists. That reuses old state and defeats the clean reinstall.
- Stopping at "installer completed" without checking whether `config.yaml` and `.env` were recreated from template.
- Letting old messaging tokens trigger gateway prompts during install.
- Treating an old 5+ GB Hermes home as disposable without a recovery handle.
- Starting provider setup before confirming the new install is actually isolated.
- Using shell commands where host-side path rewriting mangles WSL paths; prefer `wsl.exe bash -lc '...'` with literal Linux paths.

## Reference

- Session-specific failure patterns and command examples: `references/wsl-clean-reinstall.md`

## Verification Checklist

- [ ] Old Hermes home preserved under a timestamped backup path.
- [ ] Active `~/.hermes` was absent before reinstall.
- [ ] Installer completed with `--skip-setup`.
- [ ] `hermes doctor --fix` ran on the new install.
- [ ] `hermes status` confirms a genuinely clean state.
- [ ] Provider auth was started only after clean-state verification.
