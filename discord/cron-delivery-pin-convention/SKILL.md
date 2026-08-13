---
name: cron-delivery-pin-convention
description: Use when creating a cron job, repointing a cron deliver target, or adding a job to an existing delivery channe
---

# Cron Delivery & Pinned-Legend Convention

When a new Hermes cron job is created (or an existing one is repointed), it MUST follow this routing + pinning convention so the Discord server stays self-documenting.

## The two hard rules
1. **Delivery destination** — every cron job delivers to a dedicated text channel inside the **`#📥 Cronjobs Deliveries`** category (guild `1521986755409219634`, category `1525349761387987086`). If no existing channel fits the job's domain, **create a new one** (do not dump into home/`#home-channel`, and do not use `deliver: local` unless the job is intentionally silent).
2. **Pinned legend** — each delivery channel has exactly ONE pinned message: a formatted **job → schedule legend**. When a job is added/removed/repointed, update that channel's legend and re-pin it (unpin the stale one first).

## Channel → job-domain mapping (current state, 2026-07-11)
- `hermes-self-ops` (1525352585392033873) — Hermes self-maintenance & backup
- `code-docs-skills-health` (1525352852711669861) — docs drift, dependency & skill health
- `vault-maintenance` (1525352915269587045) — Vault domain audits & gbrain cleanup
- `trends-media` (1525403103841619968) — skill & YouTube trend scrapers
- `infra-ops` (1525403105506627594) — gateway watchdog & vault backup

If a new job's domain matches one of these, deliver there. Otherwise create a new channel (kebab-case name) under the category and start its legend.

## Toolset reality (CRITICAL — saves a wasted attempt)
- `discord_admin` can **read** the server and **pin/unpin** (`list_channels`, `list_pins`, `pin_message`, `unpin_message`) — but it CANNOT **send a message** and CANNOT **create a channel**.
- Sending messages + creating channels MUST go through the **Discord REST API** with the bot token.
- **Never use Python `urllib` for the REST calls** — it gets `403 error 1010` (TLS/proxy signature block) in this environment. Use **`curl`** via the terminal (git-bash). Python is fine ONLY for safe JSON encoding of the multiline legend text.
- Pinning can use either `discord_admin action=pin_message` OR the REST `PUT /channels/<cid>/pins/<mid>` (204 = success). Unpin = `DELETE /channels/<cid>/pins/<mid>`.

## Procedure
### 1. Discover (don't hardcode IDs in reusable scripts)
```bash
TOKEN=$(grep -oP 'token: \K.*' "/c/Users/Tiger/AppData/Local/hermes/config.yaml" | head -1 | tr -d '"')
curl -s -H "Authorization: Bot $TOKEN" https://discord.com/api/v10/users/@me   # verify token
```
- Category id from `discord_admin action=list_channels guild_id=1521986755409219634`.

### 2. Create channel if needed (REST)
```bash
curl -s -X POST "https://discord.com/api/v10/guilds/1521986755409219634/channels" \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"<kebab-name>","type":0,"parent_id":"1525349761387987086","topic":"<opt>"}'
# capture "id" from response
```

### 3. Repoint the cron job
```bash
cronjob action=update job_id=<job_id> deliver=discord:<channel_id>
```

### 4. Update & pin the legend
Legend format (verified readable in Discord pins):
```
# 📌 Cronjobs — `#channel-name`
*Domain summary · all times **Asia/Jerusalem (UTC+3)** · IDs are short prefixes*

---
**🔧 Active Jobs**
> **Job Display Name** · `<short_id>` · 🕘 09:00 daily

---
**⚠️ Known Issues**   (only if any — pull from cronjob list last_status/last_delivery_error)
> `<id>` last run **error** — <one-line cause>

---
**⚙️ Source Scripts**
> `script.py`

---
*Maintained by Hermes · updated YYYY-MM-DD*
```
Send via curl (Python encodes the multiline content safely):
```bash
JSON=$(python3 -c "import json,sys; print(json.dumps({'content': open('<legend.txt>').read()}))" <(echo legend))
RESP=$(curl -s -X POST "https://discord.com/api/v10/channels/<cid>/messages" \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" -d "$JSON")
NEW=$(echo "$RESP" | grep -o '"id":"[0-9]*"' | head -1 | grep -o '[0-9]*')
curl -s -o /dev/null -w "%{http_code}\n" -X PUT "https://discord.com/api/v10/channels/<cid>/pins/$NEW" -H "Authorization: Bot $TOKEN"
# unpin the previous legend:
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE "https://discord.com/api/v10/channels/<cid>/pins/<old_pin_id>" -H "Authorization: Bot $TOKEN"
```

### 5. Verify
- `discord_admin action=list_pins channel_id=<cid>` → exactly ONE pinned message, the new legend.
- `cronjob action=list` → the job's `deliver` resolves to the category channel.

## Pitfalls
- **`urllib` 403** — use `curl` for ALL Discord REST in this env.
- **`Bot ` prefix** on the token — not `Bearer`, not bare.
- **Don't leave two pins** in a delivery channel — unpin the stale legend when replacing.
- **Stale `last_status=error`** doesn't clear on repoint; `cronjob run <id>` to confirm green.
- **Silent jobs** (`no_agent:true` + `deliver:local`) post nothing — repoint only if you want visibility; otherwise document intent.

## Worked example
On 2026-07-11 all 5 category channels got formatted legends pinned (replacing flat old pins) and all 17 cron jobs confirmed repointed. Script shape: write each legend to a `.txt`, loop channels with a bash driver using `curl` (NOT urllib), pin new + unpin old. Then `discord_admin list_pins` per channel to verify.
