---
name: vault-guardrails
description: Use when modifying vault guardrail policy, shell-hook enforcement, or deciding which vault actions are always 
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [vault, guardrails, hooks, governance]
    related_skills: [vault-umbrella, verification-plan, hermes-agent]
---

# Vault Guardrails

## Purpose

This skill defines the enforceable safety boundary for the `vault` Hermes profile.

Guardrails have three layers:
1. **Prompt rules** in `AGENTS.md`
2. **Skill procedures** for vault workflows
3. **Shell hooks** in `C:\Users\Tiger\AppData\Local\hermes\profiles\vault\config.yaml`

Use all three. Do not rely on prompt text alone when a path can be blocked mechanically.

## Current Hook Reality

Hermes shell hooks support `pre_tool_call`, not `pre_tool_use`.
They support **block** or **no-op** behavior, not a native interactive `warn + confirm` handshake.

Therefore:
- **Never Do** rules should be enforced as hard blocks.
- **Ask First** rules should be enforced as approval-required hard stops when mechanical enforcement is needed.
- Any softer advisory warning belongs in skill text or AGENTS guidance, not in the shell-hook contract.

## Enforcement Boundary

Vault hooks screen the **outer tool call**, not every downstream filesystem mutation.

- Direct `write_file` / `patch` path edits can be blocked by path.
- `terminal` hooks can only inspect the command string; they do not see files later written by a Python script, so known mutating scripts need explicit command policy.
- `execute_code` can mutate files through Python APIs unless separately guarded or forbidden for vault writes.
- Known mutating vault scripts need command-level policy, not just protected-path regexes.

See `references/shell-hook-enforcement-boundary.md` for the proven mutation paths and recommended guardrail shape.

## Policy Table

| Category | Meaning | Enforcement |
|---|---|---|
| Always Do | Safe default maintenance that should happen automatically | skill procedure + verification plan |
| Ask First | Sensitive edits that require explicit Robert approval | hard stop with approval-needed reason |
| Never Do | Protected structural edits or prohibited behaviors | hard stop |

## Current Protected Paths

### Never Do
- `C:\Users\Tiger\Vault\Types\*`
- `C:\Users\Tiger\Vault\STANDARDS.md`
- `C:\Users\Tiger\Vault\CONSTITUTION.md`
- `C:\Users\Tiger\Vault\vault-guide.md`
- `C:\Users\Tiger\Vault\scripts\*`
- `C:\Users\Tiger\Vault\vault-index.md`
- `C:\Users\Tiger\Vault\AGENTS.md`
- `C:\Users\Tiger\Vault\master-tasks.md`

### Ask First
- `C:\Users\Tiger\Vault\*\wiki\index.md`
- `C:\Users\Tiger\Vault\*\wiki\log.md`

## Implementation Files

- Config: `C:\Users\Tiger\AppData\Local\hermes\profiles\vault\config.yaml`
- Hook script: `C:\Users\Tiger\AppData\Local\hermes\profiles\vault\hooks\vault_never_do_guardrail.py`
- Hook script: `C:\Users\Tiger\AppData\Local\hermes\profiles\vault\hooks\vault_ask_first_guardrail.py`
- Allowlist: `C:\Users\Tiger\AppData\Local\hermes\profiles\vault\shell-hooks-allowlist.json`

## Procedure

1. Verify Hermes hook schema before changing guardrails.
2. Create a recovery handle for `config.yaml` before mutation.
3. Update hook scripts first when logic changes.
4. Patch `config.yaml` only after the hook command paths are correct.
5. Cover `execute_code` anywhere `write_file|patch|terminal` coverage matters.
6. Verify with both positive and negative tests, including known mutating vault scripts and `execute_code` payloads.
7. Keep the policy table in AGENTS/skills aligned with the actual enforced paths.

## Verification Commands

```bash
hermes -p vault hooks list
printf '%s' '{"tool_name":"write_file","tool_input":{"path":"C:/Users/Tiger/Vault/Types/Test.md"}}' | python '/c/Users/Tiger/AppData/Local/hermes/profiles/vault/hooks/vault_never_do_guardrail.py'
printf '%s' '{"tool_name":"write_file","tool_input":{"path":"C:/Users/Tiger/Vault/AI Sphere/wiki/index.md"}}' | python '/c/Users/Tiger/AppData/Local/hermes/profiles/vault/hooks/vault_ask_first_guardrail.py'
printf '%s' '{"tool_name":"terminal","tool_input":{"command":"python scripts/build_catalog.py"}}' | python '/c/Users/Tiger/AppData/Local/hermes/profiles/vault/hooks/vault_never_do_guardrail.py'
printf '%s' '{"tool_name":"terminal","tool_input":{"command":"HERMES_VAULT_TARGET_DOMAIN=Hermes python scripts/build_index.py Hermes"}}' | python '/c/Users/Tiger/AppData/Local/hermes/profiles/vault/hooks/vault_ask_first_guardrail.py'
printf '%s' '{"tool_name":"execute_code","tool_input":{"code":"from pathlib import Path\nPath(\"C:/Users/Tiger/Vault/vault-index.md\").write_text(\"x\")"}}' | python '/c/Users/Tiger/AppData/Local/hermes/profiles/vault/hooks/vault_never_do_guardrail.py'
```

## Pitfalls

- Do not document a `warn` hook action that Hermes does not support.
- Do not protect files in prose without deciding whether the rule is enforceable.
- Do not leave hook scripts unallowlisted after configuring them.
- Do not forget terminal-path coverage; terminal is the easiest bypass route.

## Verification Checklist

- [ ] Hook schema verified against live Hermes docs or source.
- [ ] Recovery handle created before config mutation.
- [ ] Protected paths block as expected.
- [ ] Safe paths return no-op.
- [ ] Config, scripts, and policy docs agree.
