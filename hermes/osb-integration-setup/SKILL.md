---
name: osb-integration-setup
description: Use when wiring Open Second Brain into Hermes (cron, MCP, tuning, verify).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, configuration, setup, open-second-brain, cron, mcp]
    related_skills: [hermes-configuration]
---
# OSB Integration Setup for Hermes

## Overview
This skill captures the exact steps performed in the session to connect Hermes with an Open Second Brain (OSB) vault, configure recurring cron jobs for insight generation and system monitoring, tune OSB sensitivity, and optimize the MCP connection for low overhead.

## Prerequisites
- Hermes installed and running.
- OSB plugin installed (`hermes plugins list` shows `open-second-brain`).
- Vault initialized at `C:\Users\Tiger\Vault` (adjust paths if needed).
- Access to a Telegram bot/chat for notifications (you already have a target chat ID and topic IDs).

## 1. Designate Primary Agent (if not already set)
Ensures only one agent runs the deterministic `dream` process when the vault is shared.

```bash
# Find your agent name in %APPDATA%\open-second-brain\config.yaml
# Example output: agent_name: "dark-factory"
o2b brain set-primary <agent-name> --vault "C:\Users\Tiger\Vault"
```

*In this session the agent was already set to `dark-factory`.*

## 2. Enable Passive Signal Capture (Notes → Signals)
Allows OSB to scan your Obsidian‑style notes for `@osb` markers and turn them into signals.

1. Edit the vault‑local config:
   ```yaml
   # File: C:\Users\Tiger\Vault\Brain\_brain.yaml
   notes:
     read_paths:
       - Daily   # relative to vault root; add more folders as needed
   ```
2. Run the scanner:
   ```bash
   o2b brain scan-inline --vault /c/Users/Tiger/Vault
   ```

## 3. Tune Learning Sensitivity
Adjust thresholds in `_brain.yaml` to match how quickly you want ideas to graduate from signal → preference.

Edit the following sections (values used in this session):
```yaml
dream:
  candidate_threshold: 2   # lower = easier to form new unconfirmed prefs
retire:
  stale_evidence_days: 90  # keep for confidence tuning; can be reduced for fast‑changing topics
confidence:
  low_max_applied: 1       # fewer applications needed to leave "low" confidence
```
After editing, test the dream process:
```bash
o2b brain dream --vault /c/Users/Tiger/Vault
# Expect output like: run_id: dream-... changed: false (or true if updates occurred)
```

## 4. Optimize MCP Configuration (Writer Scope)
Reduces the number of tools exposed to Hermes, saving context‑window space while retaining full OSB capability.

Add/replace the `mcp_servers` entry in `C:\Users\Tiger\AppData\Local\hermes\config.yaml`:
```yaml
mcp_servers:
  open-second-brain:
    command: o2b
    args: ["mcp", "--scope", "writer", "--vault", "/c/Users/Tiger/Vault"]
    enabled: true
    # keep other fields (timeout, etc.) as you had them
```
Then restart the Hermes gateway:
```bash
hermes gateway restart
```
*Verification*:
```bash
o2b mcp resource read --uri osb://preferences/active
```
Should return the markdown contents of `Brain/active.md`.

## 5. Create Recurring Cron Jobs
All cron jobs use the Git‑Bash root (`/`) as `workdir` so that `/c/...` paths resolve correctly.

### 5.1 Discipline Report (daily)
Checks whether you are applying the preferences you’ve learned.
```bash
hermes cron create \
  --name "discipline-daily" \
  --deliver "telegram:-1003949932611:6" \
  --workdir "/" \
  "0 21 * * *" \
  "o2b discipline report --vault /c/Users/Tiger/Vault --telegram-target telegram:-1003949932611:6"
```
Runs at 21:00 UTC (00:00 Israel time) each day.

### 5.2 Proactive Insights (weekly + monthly)
- **Weekly ideas** – surfaces 5 next‑direction candidates.
```bash
hermes cron create \
  --name "weekly-ideas" \
  --deliver "telegram:-1003949932611:7" \
  --workdir "/" \
  "0 10 * * 0" \
  "o2b brain ideas --vault /c/Users/Tiger/Vault --limit 5"
```
- **Monthly synthesis** – longer‑term reflection.
```bash
hermes cron create \
  --name "monthly-synthesis" \
  --deliver "telegram:-1003949932611:8" \
  --workdir "/" \
  "0 8 1 * *" \
  "o2b brain monthly --vault /c/Users/Tiger/Vault --format markdown"
```

### 5.3 Monthly Metrics Report (system health)
Aggregates all OSB metric files into a readable summary.
```bash
hermes cron create \
  --name "monthly-metrics" \
  --deliver "telegram:-1003949932611:9" \
  --workdir "/" \
  "0 9 1 * *" \
  "cat /c/Users/Tiger/Vault/Brain/metrics/*.jsonl | jq -s 'group_by(.surface) | map({surface: .[0].surface, count: length, latest: .[-1].payload})' | head -n 20"
```

### 5.4 Quarterly Recall‑Gate Effectiveness
Measures how often the brain’s knowledge is actually retrieved.
```bash
hermes cron create \
  --name "quarterly-recall" \
  --deliver "telegram:-1003949932611:10" \
  --workdir "/" \
  "0 9 1 */3 *" \
  "cat /c/Users/Tiger/Vault/Brain/metrics/brain_recall_telemetry.jsonl | jq -s 'map(select(.operation == \"gate_summary\")) | .[-10:]'"
```

### 5.5 Bi‑monthly Self‑Tuning Review
Shows the latest auto‑tuning results (if `search_self_tuning_enabled:true`).
```bash
hermes cron create \
  --name "bimonthly-tuning" \
  --deliver "telegram:-1003949932611:11" \
  --workdir "/" \
  "0 10 1,15 * *" \
  "cat /c/Users/Tiger/Vault/Brain/metrics/self_tuning.jsonl | jq -s '.[-5:]'"
```

## 6. Enable Recall‑Gate Telemetry (optional but recommended)
Turns on logging of whether each automatic recall attempt was allowed to proceed.

Edit `_brain.yaml`:
```yaml
recall_gate_telemetry: true
```
(The cron job above will then start reporting.)

## 7. Verification Checklist
- [ ] Primary agent set (`o2b brain doctor` shows `primary_agent: <your‑name>`).
- [ ] Notes scanning runs without error and creates signals (check `Brain/inbox/`).
- [ ] Dream process completes (`o2b brain dream …` returns a `run_id`).
- [ ] MCP writer scope is active: `o2b mcp resource read --uri osb://preferences/active` returns content.
- [ ] Cron jobs appear in `hermes cron list` with correct schedules and delivery targets.
- [ ] Test each cron manually with `hermes cron run <job-id>` to confirm Telegram delivery.
- [ ] Adjust thresholds in `_brain.yaml` as your workflow evolves; re‑run `o2b brain dream` to see effect.

## 8. Reference Files
- `references/cron-examples.md` – full command strings for each cron job (copy‑paste ready).
- `references/mcp-config-snippet.yaml` – exact YAML block to insert into Hermes config.
- `references/brain-config-snippet.yaml` – adjusted `_brain.yaml` sections for sensitivity and telemetry.

## How to Teach This Skill
When another agent or a future you needs to recreate this setup, simply:
1. Follow the numbered steps above.
2. Use the reference files to avoid typos.
3. Run the verification checklist to confirm everything is wired correctly.

## Maintenance
- Periodically review `_brain.yaml` thresholds as your signal volume changes.
- If you add new vaults, consider the **Workspace Insight Suite** (see `references/workspace-insight.md`).
- Restart the Hermes gateway after any MCP config change.

---
*This skill encapsulates the concrete actions taken in the session to make OSB a fully automated, observable, and self‑improving memory layer for Hermes.*