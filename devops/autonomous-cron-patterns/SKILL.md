---
name: autonomous-cron-patterns
description: Use when converting report-only cron jobs into autonomous maintenance loops.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [cron, autonomous, agent-mode, remediation, troubleshooting, working-directory]
---

# Autonomous Cron Job Patterns

This skill covers the class of work: taking existing cron jobs that only report findings and converting them to **autonomous agents that analyze, fix, verify, and report actions taken**.

## Core Problem Patterns

### 1. Working Directory Mismatch (Common Failure)

**Symptom**: Cron job fails with `RuntimeError: [Errno 2] No such file or directory` for scripts that exist and run manually.

**Root Cause**: Hermes cron runner resolves relative script paths from its working directory (not the `scripts/` folder). Jobs using subdirectory paths (`vault_cron_wrappers/...`) fail.

**Fix**: Set `workdir` on the cron job to the scripts folder:
```bash
hermes cron update <job_id> --workdir "C:/Users/Tiger/AppData/Local/hermes/scripts"
```

**Prevention**: All cron jobs using scripts in `scripts/` or subdirectories should have explicit `workdir` set.

---

### 2. Report-Only → Autonomous Conversion Pattern

**Before (Report Only)**:
```yaml
prompt: "Use injected script output as single source of truth for Telegram report. Start with bolded line..."
script: "vault_cron_wrappers/vault_cron_small_domains.py"
```

**After (Autonomous Fixer)**:
```yaml
prompt: |
  You are the Vault maintenance agent. The injected script output contains a `scoped_audit` field with audit JSON: `errors`, `warnings`, `info` arrays with `category`, `path`, `message`, `detail`.
  
  Your job:
  1. Parse the injected script output JSON — extract `scoped_audit.output`
  2. For each **fixable error/warning**, execute the fix:
     - `raw.linked_extracts` errors → add forward links from raw files to extracts in wiki/extracts/
     - `schema.required_field` errors → add missing frontmatter fields
     - `wikilinks.missing_target` warnings → create missing wiki pages or fix broken links
     - `Index.generic_entities_section` warning → replace with Type-aligned sections
     - `wikilinks.ambiguous_domain_page` → disambiguate with domain prefix
  3. Re-run the scoped audit for the same domain to verify fixes
  4. Report: what was found, what you fixed, what remains, next run recommendations
  
  Use terminal/file/skills tools. Be decisive — fix what you can, note what needs manual review.
no_agent: false  # default - LLM-driven
```

**Key Differences**:
- Prompt instructs agent to **parse structured data** (JSON) not format text
- Agent **executes fixes** using tools (`terminal`, `file`, `skills`)
- Agent **verifies** by re-running collector
- Report summarizes **actions taken**, not just findings

---

### 3. Structured Collector Output Requirement

For autonomous fixing to work, collectors **must output structured JSON** with actionable fields:

```json
{
  "kind": "vault_domain_maintenance_collect",
  "scoped_audit": {
    "exit_code": 0,
    "output": {
      "errors": [
        {"category": "raw.linked_extracts", "path": "Finance/raw/file.md", "message": "Missing forward link", "detail": {"extract": "Finance/wiki/extracts/file.md"}}
      ],
      "warnings": [
        {"category": "wikilinks.missing_target", "path": "Finance/wiki/page.md", "message": "Target missing: Micha.Stocks", "detail": {"target": "Micha.Stocks"}}
      ]
    }
  }
}
```

**Required fields per finding**: `category`, `path`, `message`, `detail` (with actionable sub-fields)

---

### 4. Known Hermes Tool Executor Bug (Cron Sessions)

**Bug**: In cron agent sessions, `read_file` and `patch` tools fail with:
```
TypeError: _install_invoke_tool_patch.<locals>.patched_invoke_tool() takes from 4 to 7 positional arguments but 9 were given
```

**Workaround**: Agent works around by using `terminal` commands for file operations:
- Instead of `read_file`: `type "path"` or `cat "path"` via terminal
- Instead of `patch`: `sed`/`python` script via terminal to edit files
- `search_files` and `write_file` work normally

**Status**: Known Hermes core bug. Does not block autonomous operation — agent adapts using terminal.

---

### 5. Network Connectivity Troubleshooting

**Telegram Gateway Failure Pattern**:
- DNS resolves but TCP connections timeout → network-level block (firewall/ISP)
- Fallback IPs also timeout → confirmed block
- **Auto-recovery**: Gateway retries with exponential backoff; recovers when network allows

**Verification**:
```bash
# Test connectivity
curl -v --connect-timeout 10 https://api.telegram.org
ping -n 4 149.154.166.110

# Check gateway logs for positive signal
tail -f ~/.hermes/logs/gateway.log
# Look for: "[Telegram] Connected to Telegram (polling mode)" + "✓ telegram connected"
```

---

### 6. Disabled MCP endpoint leak-stop pattern

**Symptom**: Gateway logs keep emitting warnings like `getaddrinfo failed`, `NXDOMAIN`, or `MCP: 0 tool(s)` for an MCP server that should have been disabled in config.

**Root Cause**: The config edit landed, but the running gateway process is still on stale in-memory config loaded before the edit. `enabled: false` only takes effect after restart.

**Fix pattern**:
1. Prove the MCP endpoint is actually dead with an independent DNS check.
2. Confirm the config contains `mcp_servers.<name>.enabled: false`.
3. Confirm the registration logic skips disabled servers entirely.
4. Restart the gateway from **outside** the gateway process tree.
5. Verify there are **no leak lines after the restart boundary** (for example after the last `Starting Hermes Gateway` log line).

**Critical pitfall**: On Hermes desktop, `hermes gateway restart` can be blocked from a terminal session that is itself a child of the running gateway. Use a separate shell or a detached one-shot cron/script for the restart, then a second one-shot verifier cron to grep the post-restart logs.

See `references/gateway-restart-and-disabled-mcp-verification.md`.

---

### 7. Hermes CLI Subprocess Hang (Windows + venv)

**Symptom**: Cron jobs or scripts that call `hermes` CLI subcommands via `subprocess.run()` hang indefinitely — the process never returns, timing out after the configured limit (default 120s). Error message often misleading: `RuntimeError: [Errno 2] No such file or directory` even though the script exists.

**Root Cause**: On Windows, the Hermes venv Python (`venv/Scripts/python.exe`) hangs on module imports or subprocess spawning. The `hermes` CLI entry point (installed in venv) inherits this hang when invoked via subprocess from another Python process.

**Fix**: **Do not call `hermes` CLI via subprocess from Python scripts**. Instead, use direct Python imports:

```python
# ❌ BAD: subprocess call hangs
result = subprocess.run(["hermes", "status", "--all"], capture_output=True, timeout=30)

# ✅ GOOD: direct import (works with system Python + sys.path)
import sys
sys.path.insert(0, r"C:\Users\Tiger\AppData\Local\hermes\hermes-agent")
from hermes_cli.status import show_status
import argparse
args = argparse.Namespace(all=True, deep=False)
show_status(args)
```

**Key Hermes CLI modules available for direct import**:
| Module | Function | Purpose |
|--------|----------|---------|
| `hermes_cli.status` | `show_status(args)` | Full system status |
| `hermes_cli.curator` | `_cmd_status(args)` | Curator status |
| `hermes_cli.memory_setup` | `memory_command(args)` | Memory provider status |
| `hermes_cli.cron` | `cron_command(args)` | Cron list/status |
| `hermes_cli.config` | `config_command(args)` | Config check |
| `hermes_cli.doctor` | `run_doctor(args)` | Diagnostics (may still be slow) |

**Workaround for collector scripts**: If a collector script must gather Hermes status, refactor it to import and call the internal functions directly instead of spawning `hermes` subprocesses. This avoids the venv hang entirely.

**Venv Python hang diagnostic**: The Hermes venv Python (`/c/Users/Tiger/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`) hangs on simple `import` statements. System Python (`python`) with `sys.path.insert(0, hermes_agent_root)` works correctly. This is a Windows-specific venv issue, not a code bug.

---

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Missing `workdir` | "No such file or directory" on valid scripts | Set explicit `workdir` to scripts folder |
| Collector outputs markdown only | Agent can't parse findings for action | Collector must output structured JSON with `errors`/`warnings` arrays |
| Agent tries to use `read_file`/`patch` in cron | Tool executor bug: argument count error | Work around with `terminal` commands (known Hermes bug) |
| Prompt says "format for report" | Agent produces report, no fixes | Prompt must say "analyze findings, execute fixes, verify, report actions" |
| No verification step | Agent claims fixes but doesn't confirm | Always include "re-run collector/audit to verify" in prompt |
| Disabled MCP still logs warnings after config edit | Gateway loaded old config before the change | Restart from outside the gateway process tree, then verify no leak lines **after** the restart boundary |
| `hermes gateway restart` blocked from current session | Terminal is a child of the running gateway | Use a detached one-shot cron/script or a separate external shell |
| **Hermes CLI subprocess hang (Windows)** | Cron/script calling `hermes` via subprocess times out; misleading "No such file or directory" error | **Use direct Python imports** (`from hermes_cli.module import func`) instead of subprocess; run with system Python + `sys.path.insert(0, hermes_agent_root)` |

---

## Conversion Checklist

When converting a report-only cron job to autonomous:

- [ ] Collector outputs structured JSON (errors/warnings/info with category, path, message, detail)
- [ ] Cron job has `workdir` set to script location
- [ ] Prompt instructs: parse JSON → execute fixes per category → verify → report actions
- [ ] `enabled_toolsets` includes `terminal`, `file`, `skills` (as needed)
- [ ] `deliver` set to Telegram for notifications
- [ ] Test manually: `hermes cron run <job_id>` and verify Telegram delivery

---

## References

- `references/cron-workdir-fix.md` — Working directory fix details
- `references/autonomous-conversion-template.md` — Template prompt for conversion
- `references/telegram-gateway-network-troubleshooting.md` — Network troubleshooting guide
- `references/gateway-restart-and-disabled-mcp-verification.md` — Dead MCP endpoint disable/restart/verification pattern
- `references/hermes-cli-direct-import-patterns.md` — Direct import patterns to avoid Windows venv subprocess hang