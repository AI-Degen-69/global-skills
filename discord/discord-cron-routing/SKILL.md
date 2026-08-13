---
name: discord-cron-routing
description: Use when restructuring which Discord channels Hermes cron jobs deliver to.
---

# Discord Cron Routing

Restructure where Hermes cron jobs deliver on Discord. The goal: one channel per
job-group, all nested under a single category, with a pinned legend naming the
jobs that land in each.

## Toolset reality (important)
Hermes' `discord_admin` toolset can **read** the server and **pin/unpin** messages:
`list_guilds`, `server_info`, `list_channels`, `channel_info`, `list_roles`,
`member_info`, `list_pins`, `pin_message`, `unpin_message`, `delete_message`,
`add_role`, `remove_role`.

It CANNOT:
- create a channel (`create_channel` does not exist)
- move/reparent a channel
- **send a message** (`send_message` does not exist)

So channel creation and message sending MUST go through the Discord REST API
with the bot token Hermes already stores. Pinning can use either `discord_admin
action=pin_message` or REST — your choice; REST is convenient when you already
have the message id from a send call.

## Prerequisites — discover, don't hardcode
1. Guild ID: `discord_admin action=list_guilds`.
2. Channel tree + target category id: `discord_admin action=list_channels guild_id=<id>`.
3. Bot token (in Hermes discord config):
   ```bash
   TOKEN=$(grep -oP 'token: \K.*' "$APPDATA/hermes/config.yaml" | head -1 | tr -d '"')
   ```
   On MSYS use `/c/Users/<user>/AppData/Local/hermes/config.yaml`.
   Verify before mutating:
   ```bash
   curl -s -H "Authorization: Bot $TOKEN" https://discord.com/api/v10/users/@me
   # → {"id":...,"username":...,"bot":true}
   ```

## REST patterns (verified)
Base `https://discord.com/api/v10`. Auth: `Authorization: Bot $TOKEN`.

### Create text channel inside a category
```bash
curl -s -X POST "https://discord.com/api/v10/guilds/<guild_id>/channels" \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"<kebab-name>","type":0,"parent_id":"<category_id>","topic":"<opt>"}'
```
- `type:0` text. `parent_id` nests it under the category at create time (no move step).
- Capture `"id"` from the response for later steps.
- Names: lowercase, hyphens, no spaces.

### Send a message (e.g. routing legend)
```bash
BODY=$(python3 -c "import json,sys; print(json.dumps({'content': sys.argv[1]}))" "$LEGEND")
RESP=$(curl -s -X POST "https://discord.com/api/v10/channels/<channel_id>/messages" \
  -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" -d "$BODY")
MID=$(echo "$RESP" | grep -o '"id":"[0-9]*"' | head -1 | grep -o '[0-9]*')
```
`python3 -c json.dumps` safely encodes Hebrew/emoji/quotes.

### Pin (REST alt to discord_admin pin_message)
```bash
curl -s -o /dev/null -w "%{http_code}" -X PUT \
  "https://discord.com/api/v10/channels/<channel_id>/pins/<message_id>" \
  -H "Authorization: Bot $TOKEN"
# 204 = success
```

## Repoint cronjob deliver (the actual binding)
Only the cronjob tool binds job→channel; Discord just hosts the channel:
```
cronjob action=update job_id=<job_id> deliver=discord:<channel_id>
```

## Workflow
1. `discord_admin list_channels` → confirm category exists, note its id.
2. For each new channel: create via REST with `parent_id=category_id`; capture id.
3. `cronjob list` → `cronjob update deliver=discord:<id>` per job.
4. For each channel: POST a legend, PIN it (REST or `discord_admin pin_message`).
5. Verify (see below).

## Verification
- `discord_admin list_channels` → new channels nested under the category.
- `cronjob list` → every `deliver` resolves to a category channel (zero `discord` home / `local` unless intentional).
- `discord_admin list_pins channel_id=<id>` (or GET `/pins`) → legend pinned.

## Pitfalls
- **Don't hunt for `discord_admin create_channel`/`send_message`** — they don't exist; use REST.
- **`Bot ` prefix** on the token, not `Bearer`, not bare. Wrong prefix → 401.
- **Don't hardcode guild/category/channel IDs** in reusable scripts — discover per run.
- **Stale `last_status=error`**: repointing doesn't clear a job's historical error flag. Trigger it (`cronjob run`) or wait a tick to confirm green.
- **`parent_id` at create time** avoids a separate PATCH move. To move an existing channel: `PATCH /channels/<id>` with `{"parent_id":...}`.
- **Silent jobs**: `deliver: local` / `no_agent:true` jobs post nothing to Discord — repoint only if you want visibility.

## Worked example (this environment)
Category `📥 Cronjobs Deliveries` (1525349761387987086) got 5 channels:
hermes-self-ops, code-docs-skills-health, vault-maintenance (pre-existing) +
trends-media, infra-ops (created via REST). All 17 cron jobs repointed;
a job→schedule legend pinned in each. IDs are environment-specific — use as shape reference only.
