---
name: hermes-bootstrap-validation
description: Use when validating a fresh Hermes install on Linux/WSL and wiring auth.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [Hermes, WSL, install, bootstrap, open-second-brain, workflows, verification]
    related_skills: [hermes-clean-reinstall, hermes-model-optimization, hermes-agent]
---

# Hermes Bootstrap Validation

Use when Hermes has just been installed or reinstalled on Linux/WSL and you need to turn it into a working stack: auth, model config, gateway, memory provider, plugins, and a first end-to-end workflow run.

This skill is for the **post-install reality check**. Do not stop at "installer exited 0".

## When to use

- Fresh Hermes install on Linux/WSL
- Clean reinstall after moving an old `~/.hermes` aside
- First-time Open Second Brain setup
- First-time `hermes-workflows` setup
- "It installed, but does it actually work?"

## Core rules

1. **Preserve before replacing.** If `~/.hermes` already exists, inspect it first. If the user wants a clean reinstall, move it to a timestamped backup path instead of deleting it outright.
2. **Avoid installer wizard stalls.** Prefer installer flags that skip interactive setup when you are deliberately doing a manual bootstrap/verification flow.
3. **Auth is not enough.** A fresh login can still fail real usage if the config points at the wrong default provider/model.
4. **Verify by task path, not by status page.** `hermes doctor` passing is necessary but not sufficient; run a real `hermes chat` smoke test.
5. **Plugin install is not CLI publication.** After installing a plugin, verify whether its wrapper command is actually on PATH.
6. **Complete one real workflow run.** For workflows, validation means a spec that validates **and** a run that reaches a terminal state with expected output.

## Recommended sequence

### 1. Inspect and preserve old state

- Check whether `~/.hermes` already exists and whether it is a real environment (size, sessions, profiles, cron, auth, gateway state).
- If doing a clean reinstall, stop gateway/user services if needed and move the old home aside:
  - Example pattern: `mv ~/.hermes ~/.hermes-backup-<timestamp>`
- Report the recovery handle.

### 2. Reinstall Hermes cleanly

- Run the installer in a way that does **not** immediately trap you in the setup wizard if you intend to do manual configuration next.
- After install, verify:
  - `hermes --version`
  - `hermes doctor`
  - `hermes status`

### 3. Re-auth and fix default model config

After `hermes auth add <provider>` succeeds, do **not** assume the stack is usable.

Run a real smoke test, e.g.:

```bash
hermes chat -q "Reply with exactly: OK" -Q --provider openai-codex -m gpt-5.4
```

If that works only with explicit provider/model flags, normalize config immediately:

```bash
hermes config set model.provider openai-codex
hermes config set model.default gpt-5.4
```

Then retest without relying on stale template defaults.

**Pitfall:** a fresh config can still inherit or ship with a template default like an Anthropic model; auth may be valid while normal chat still fails.

### 4. Start and verify gateway

- Start/restart the gateway after config/auth changes.
- Verify the gateway, then continue to plugin and memory setup.

### 5. Install and bind Open Second Brain

Recommended flow:

1. Install and enable the plugin.
2. Publish its CLI if needed.
3. Initialize a dedicated vault/brain.
4. Activate it as Hermes memory provider.
5. Run doctor/status checks.

Typical path:

```bash
hermes plugins install itechmeat/open-second-brain --enable
~/.hermes/plugins/open-second-brain/scripts/o2b install-cli
o2b init --vault <vault-path> --name <brain-name> --agent-name <agent-name> --timezone <tz>
o2b brain init --vault <vault-path> --primary-agent <agent-name>
hermes memory setup open-second-brain
```

### 6. Handle `o2b doctor` deterministically

If `o2b doctor` fails on `code_graph`, inspect **where** it is running from.

**Observed pitfall:** doctor can inspect the wrong adjacent directory (for example an alphabetically earlier folder like `.nvm`) instead of the actual project you intended.

Fix pattern:

- Run doctor from a real repo directory
- Pass explicit repo/vault args when available
- If `codegraph` is installed globally, initialize it in the intended repo first

Example pattern:

```bash
cd ~/.hermes/plugins/open-second-brain
codegraph init .
o2b doctor --vault <vault-path> --repo ~/.hermes/plugins/open-second-brain
```

### 7. Install and publish `hermes-workflows`

Install and enable the plugin, then verify three layers separately:

1. plugin is enabled
2. CLI wrapper exists and is callable
3. Hermes reports workflows/tool availability

**Pitfall:** plugin install may clone the repo but leave the CLI wrapper off PATH.

Check for an in-repo wrapper like `bin/hermes-workflows`. If the command is missing but the wrapper exists, publish it yourself, for example by symlinking into `~/.local/bin`.

### 8. Verify with a minimal workflow

Create a tiny **global/manual** workflow for smoke testing.

Guidelines:

- Use `scope: global` so it does not clutter boards
- Use a single `agent_task`
- Add explicit success and failure branches
- End in terminal `finish` nodes
- Validate and compile preview before running
- Run to completion and inspect the actual terminal output

This is the acceptance test for the workflows layer.

## Acceptance checklist

Do not call the bootstrap complete until all are true:

- Hermes installed and reachable
- `hermes doctor` passes materially
- auth works for the intended provider
- default provider/model config matches the intended stack
- a real `hermes chat` smoke test succeeds
- gateway is running
- Open Second Brain is initialized and active as memory provider
- `o2b doctor` passes against the intended repo/vault
- `hermes-workflows` command is callable
- workflows tool availability is visible in Hermes
- at least one workflow validates cleanly
- at least one workflow run completes successfully with expected output

## What not to do

- Do not declare success after installer exit alone
- Do not delete an old `~/.hermes` without first creating a recovery handle
- Do not stop at `auth add` without a real chat smoke test
- Do not treat plugin enablement as proof the CLI is on PATH
- Do not trust a doctor failure until you verify the tool is checking the intended repo/path

## References

- `references/dark-factory-wsl-bootstrap.md` — concrete command patterns and pitfalls from a full WSL bootstrap with Open Second Brain and Hermes Workflows
