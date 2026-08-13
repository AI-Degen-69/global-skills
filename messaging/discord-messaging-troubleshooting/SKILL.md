---
name: discord-messaging-troubleshooting
description: Use when - Discord messages are not arriving in Hermes or from Hermes
version: 0.1.0
author: Hermes
platforms:
- windows
- linux
- macos
metadata:
  hermes:
    tags:
    - Discord
    - Gateway
    - Troubleshooting
    - Messaging
---

# Discord Messaging Troubleshooting

Diagnose and resolve common issues preventing Hermes from sending/receiving messages via Discord. Covers gateway status, bot authentication, server membership, allowlist, and config errors.

## When to Use

- Discord messages are not arriving in Hermes or from Hermes
- Gateway logs show `401 Unauthorized`, `403 Forbidden`, or `AttributeError: 'list' object has no attribute 'items'`
- Bot appears offline in Discord despite gateway running
- `/reset` works but normal chat returns "Sorry, I encountered an unexpected error"

## Prerequisites

- Hermes installed and running
- Access to the host filesystem (to read `.env`, `config.yaml`, logs)
- Discord bot token and application ID available
- Basic familiarity with Discord Developer Portal

## How to Run

Follow the Procedure steps below, using the `terminal` tool for shell commands and `read_file`/`patch` for file edits. Each step can be run independently; stop when the issue is resolved.

## Quick Reference

- `hermes gateway status` – check gateway process and adapter connections
- `grep -i discord ~/.hermes/logs/gateway.log` – scan for errors
- `hermes secrets set DISCORD_BOT_TOKEN` – update bot token securely
- `hermes gateway restart` – restart gateway after config/env changes
- Check `.env` for `DISCORD_ALLOWED_USERS` or set `DISCORD_ALLOW_ALL_USERS=true` for testing
- `hermes config set DISCORD_ALLOW_ALL_USERS true` writes to `config.yaml`, but Discord auth reads the live `.env` vars; use `.env` (or `hermes secrets` if you have a supported secret workflow), not `config.yaml`, for this flag.

## Procedure

### 1. Verify gateway is running and Discord adapter connected
```bash
hermes gateway status
```
Look for:
- `✓ Gateway process running (PID: xxxx)`
- `✓ discord connected` (or `✗ discord failed to connect`)

If Discord shows disconnected or failed, proceed to step 2.

### 2. Examine gateway logs for specific errors
```bash
grep -iE "discord|error|unauthorized|forbidden|attributeerror" ~/.hermes/logs/gateway.log | tail -30
```
Common patterns and fixes:

- **401 Unauthorized / Improper token has been passed**  
  → Bot token is invalid or reset in Discord Developer Portal.  
  → Regenerate token at https://discord.com/developers/applications → your app → Bot → Reset Token.  
  → Update in Hermes:  
    ```bash
    hermes secrets set DISCORD_BOT_TOKEN
    ```
    (paste new token)  
    → `hermes gateway restart`

- **403 Forbidden / Missing Access**  
  → Bot lacks permission to read/send in the target channel or is not in the server.  
  → Invite bot to server:  
    1. Discord Developer Portal → OAuth2 → URL Generator  
    2. Scopes: `bot` (and `applications.commands` for slash commands)  
    3. Bot Permissions: at least `Send Messages`, `Read Message History`, `View Channel`  
    4. Copy generated URL, add bot to your server, authorize.  
  → Ensure target channel ID in `DISCORD_HOME_CHANNEL` is correct (or omit to use home channel).

- **AttributeError: 'list' object has no attribute 'items'**  
  → Misconfigured `mcp_servers` in `config.yaml` (list instead of dict).  
  → Edit `C:\\Users\\<user>\\AppData\\Local\\hermes\\config.yaml`:  
    Change:  
    ```yaml
    mcp_servers:
      - url: https://mcp.nousresearch.com
        name: nous-mcp
        priority: 1
    ```  
    To:  
    ```yaml
    mcp_servers:
      nous-mcp:
        url: https://mcp.nousresearch.com
        priority: 1
    ```  
    → Save file, **then restart the gateway** so the running process reloads the corrected config:  
    ```bash
    hermes gateway restart
    ```

- **Unauthorized user: <id> (<name>) on discord**  
  → Username in `DISCORD_ALLOWED_USERS` did not resolve to your Discord ID (requires shared guild).  
  → Find your numeric Discord user ID (enable Developer Mode in Discord → right-click your profile → Copy ID).  
  → Set directly:  
    ```bash
    hermes secrets set DISCORD_ALLOWED_USERS=<your-numeric-id>
    ```  
    (or temporarily set `DISCORD_ALLOW_ALL_USERS=true` for testing).

### 3. Test inbound/outbound messaging
- **Outbound**:  
  ```bash
  hermes send --to discord "test message"
  ```
  Should return `sent`. Check target channel/DM. **Important:** this proves Discord delivery and bot auth, but it does **not** prove the inbound agent path is healthy; `hermes send` can succeed even while inbound DM/chat turns still crash.

- **Inbound**: Send a DM to the bot or `@hermes_bot4321 <msg>` in a shared channel.  
  Watch logs:  
  ```bash
  tail -f ~/.hermes/logs/gateway.log
  ```  
  Look for `inbound message: platform=discord` followed by a response, not an `Agent error`.

### 4. Verify resolution
- Gateway status shows `✓ discord connected`
- No new errors in `gateway.log` after sending/receiving test messages
- Hermes responds in Discord to normal messages (not just `/reset`)

## Pitfalls

- Re-read the live file before telling the user to edit it manually. In this class of issue, `config.yaml` may already be fixed on disk while the gateway is still running stale config in memory; the right action is then restart + re-test, not re-explaining the YAML edit.
- The `DISCORD_ALLOWED_USERS` allowlist resolves usernames to numeric IDs only if the bot shares a guild with the user. If you only interact via DMs, set the allowlist to your numeric user ID directly.
- Editing `config.yaml` or `.env` requires bypassing Hermes write guards; use `hermes secrets set` for secrets or edit files directly with a text editor.
- After changing the bot token, allowlist, or server membership, the gateway may retry automatically (exponential backoff). Use `hermes gateway restart` to force an immediate re-attempt.
- The "Session reset~" message from `/reset` does **not** indicate the agent is healthy; it only means the session was reset. Subsequent chat may still fail with "Sorry, I encountered an unexpected error" if the underlying config error persists.

## Verification
Send a test message via `hermes send --to discord "Verification OK"` and confirm it appears in the target Discord channel or DM within 5 seconds.