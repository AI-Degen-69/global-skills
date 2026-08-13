---
name: messaging-gateway-operations
description: Use when operating Hermes messaging gateways across platforms.
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [gateway, telegram, discord, messaging, cron, routing, troubleshooting]
---

# Messaging Gateway Operations

Use this skill when the user asks why Telegram/Discord/Slack/other messaging platforms are not working, asks how the gateway differs from the local TUI/CLI, or needs a reliable setup/check/restart workflow for Hermes messaging integrations.

## Core distinction

- **TUI / CLI**: local interactive conversation with Hermes.
- **Gateway**: long-running bridge that connects external platforms to Hermes sessions and delivers replies back.
- A working TUI does **not** imply the gateway is healthy.

## Standard workflow

1. **Check gateway state first**
   - `hermes gateway status`
   - Look for both:
     - a running process/PID
     - the relevant platform adapter being connected
2. **Inspect logs when status is ambiguous**
   - `~/.hermes/logs/gateway.log`
   - Search for adapter load failures, credential issues, network failures, or chat routing errors.
3. **Confirm platform prerequisites**
   - Bot token / OAuth / whitelist / home channel / allowed chats.
   - Platform-specific Python or Node dependencies when the adapter is library-backed.
4. **Restart after any dependency or config change**
   - The already-running gateway will not magically see a new install or changed env.
   - Use `hermes gateway restart` when the process is healthy enough to replace cleanly.
5. **Verify end-to-end**
   - Send a real inbound message from the external platform.
   - Confirm a reply arrives and the log shows the adapter connected.

## Operator-intent handling

When the user asks to **switch off**, **stop**, or **disable** a gateway/profile gateway, treat that as an execution request, not a teaching opportunity.

- If the target is clear, perform the stop action first, then report what happened.
- Do not default to telling the user which commands to run when you can run them directly.
- Only stop to ask when the scope is genuinely ambiguous, for example: disable one specialist profile, all specialist profiles, or the default Windows autostart task.

## Common Telegram-specific failure mode

If Telegram is configured but the gateway log says the Telegram adapter cannot load because the `python-telegram-bot` module is missing, fix the runtime environment, then restart the gateway.

- Install into Hermes's own venv, not a random system Python.
- Typical Windows path: `.../hermes-agent/venv/Scripts/python.exe -m pip install "python-telegram-bot[webhooks]==22.6"`
- After installation, restart the gateway so the live process can import the new package.

## Cron-to-Telegram verification

When the question is specifically whether **cron output is reaching Telegram**, verify the whole chain instead of only checking that the gateway process exists.

1. Check scheduler state:
   - `hermes cron status`
   - `hermes cron list --all`
   - If status says the gateway is not running, cron jobs will not fire automatically.
2. Check gateway state:
   - `hermes gateway status`
   - Confirm both a running gateway process and a connected Telegram adapter.
3. Check positive Telegram connection evidence in `~/.hermes/logs/gateway.log`:
   - `[Telegram] Connected to Telegram (polling mode)`
   - `✓ telegram connected`
4. Trigger a controlled cron run when you need fresh proof:
   - `hermes cron run <job_id>`
   - Wait for the next scheduler tick, then inspect `~/.hermes/logs/agent.log`.
5. Confirm **delivery**, not just job completion:
   - Look for `Job '<job_id>': delivered to telegram:<chat_id> via live adapter`
   - If the job uses `deliver=origin` and no origin is present, the expected fallback log is `falling back to telegram home channel` immediately before the delivery line.

This is the authoritative positive signal for cron-to-Telegram delivery. `Last run: ok` by itself is insufficient because the job may have completed without reaching Telegram.

## Pitfalls

- `hermes gateway start` can make the scheduled task exist or trigger it, but that does **not** prove the adapter is healthy.
- A running task with no connected adapter is still a broken messaging setup.
- Do not use the local TUI as evidence that Telegram/Discord/etc. is working.
- If a platform comes up after a restart but then fails to route messages, check the gateway log before changing config blindly.
- `hermes cron list --all` showing `Last run: ok` does **not** prove Telegram delivery; require the `delivered to telegram:<chat_id> via live adapter` log line.
- On Windows multi-profile installs, `hermes gateway stop` may drain the service yet leave orphaned `pythonw.exe` gateway processes and stale `gateway.lock` / `gateway.pid` markers behind. If `gateway status` says `No gateway process detected` for the active profile but `hermes gateway list` still shows the profile as running, verify the Windows PID directly and clean the stale runtime markers.
- On Windows git-bash, do **not** use `/proc/<pid>` to validate Hermes gateway PIDs. Use `MSYS2_ARG_CONV_EXCL='*' tasklist.exe /FI "PID eq <pid>" /FO LIST` so Windows receives the filter arguments intact.

## Verification targets

- `hermes gateway status` shows the gateway process running.
- The gateway log shows the adapter connected, not just attempted.
- A real message sent from the external platform reaches Hermes and gets a reply.

## Support files

- `references/telegram-gateway-troubleshooting.md` — concise Telegram gateway diagnosis and repair notes.
- `references/cron-telegram-verification.md` — positive-evidence checklist for proving cron jobs actually reached Telegram.
- `references/telegram-flood-control-mitigation.md` — token-bucket rate limiting, exponential backoff, and batch-cap pattern to prevent Telegram 429 RetryAfter.
- `references/hermes-backup-cron-pattern.md` — reusable Hermes→GitHub backup cron with Telegram notifications (robocopy + git + agent-mode cron).
- `references/windows-multi-profile-gateway-stop-cleanup.md` — Windows-specific cleanup path when profile gateways report stopped but stale `pythonw.exe`/lock state still makes Hermes show them as running.

## Agent-mode cron delivery (recommended for custom messages)

When a cron job needs to send custom Telegram messages (start/success/failure with dynamic timestamps), use **agent-mode** (`no_agent=false`, the default) with the `send_message` tool — not the gateway CLI.

**Why:** The gateway CLI (`hermes gateway send ...`) does not exist. The gateway is a message bridge, not a sender. Agent-mode cron runs the LLM which can call `send_message` tool directly.

**Pattern:**
```yaml
cronjob:
  action: create
  no_agent: false          # default — LLM-driven
  prompt: |
    1. Send start message via send_message to telegram:<chat_id>
    2. Run backup script
    3. Send success/failure via send_message
  deliver: "telegram:<chat_id>"
  schedule: "0 3,15 * * *"
```

**Important same-target caveat:** if the cron job's final delivery target is the **same Telegram chat** as the ad-hoc `send_message` target, Hermes may suppress the explicit send with a message like: `Skipped send_message to telegram:<chat_id>. This cron job will already auto-deliver its final response to that same target.` That guard protects against duplicate final sends, but it also blocks workflows that need extra progress notifications in the same chat.

**Workaround for required extra notifications:** send those start/success/failure messages directly through the Telegram Bot API using `TELEGRAM_BOT_TOKEN` from `~/.hermes/.env`, then let Hermes deliver the final cron response normally. Use this only for explicit additional notifications inside the same cron run; for ordinary single-message cron delivery, keep using `send_message` / standard cron delivery.

See also: `references/cron-same-target-telegram-extra-notifications.md`.

**Verification:** Look for positive Bot API responses (`{"ok": true, ...}`) for the extra notifications, and keep the usual `delivered to telegram:<chat_id> via live adapter` check for Hermes's own cron delivery path.
