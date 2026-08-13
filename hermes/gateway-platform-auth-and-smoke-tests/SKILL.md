---
name: gateway-platform-auth-and-smoke-tests
description: Use when the user configured a chat platform and wants to test/smoke it.
---

# Gateway Platform Auth and Smoke Tests

## When to use
- The user says they already configured a chat platform and asks you to test it.
- A platform appears configured but messages are not arriving.
- You need to distinguish gateway-connection problems from simple outbound-delivery problems.
- Discord setup work involves a new server, new channel, or a token reset.

## Core rule
Separate **authentication**, **routing**, and **delivery path** before changing anything.

- **Authentication** = can the bot/platform log in?
- **Routing** = is the configured home channel / target ID correct?
- **Delivery path** = is the user asking for a direct outbound smoke test (`hermes send`) or a full gateway/inbound test?

Do not conflate these. A wrong token and a wrong channel ID produce different fixes.

## Steps
1. **Inspect live state first; do not trust memory or prior chat summaries.**
   - Prefer `$HERMES_HOME` over `~/.hermes` on Windows/git-bash sessions because `~` may resolve somewhere misleading.
   - Check `config.yaml`, `.env`, `channel_directory.json`, and `logs/gateway.log` under `$HERMES_HOME`.

2. **Read the gateway log for the exact failure mode.**
   Classify before acting:
   - `401 Unauthorized` / `Improper token has been passed` on Discord = invalid `DISCORD_BOT_TOKEN` (often rotated/reset), not a channel problem.
   - Successful connection followed by delivery failure = likely target/channel/permissions.
   - Telegram token-in-use / another PID owns token = parallel gateway conflict, not bad credentials.

3. **Confirm the configured routing target separately.**
   - Compare `.env` / config values such as `DISCORD_HOME_CHANNEL` with log evidence and `channel_directory.json`.
   - Treat channel-ID drift as independent from auth drift.

4. **For Discord, ask for the correct secret only.**
   If the user pastes or references these fields, explicitly correct them:
   - **Wrong for login:** Application ID, Public Key, Client Secret (unless a specific integration asks for it).
   - **Required for bot login:** `DISCORD_BOT_TOKEN` from the **Bot** tab.
   Explain that the General Information page is not the bot login credential.

5. **If the user created a new Discord server, verify invite assumptions.**
   The same bot application does **not** automatically join newly created servers.
   - Require an OAuth2 invite to the new guild.
   - Scopes: `bot` and usually `applications.commands`.
   - Missing invite after auth repair will usually become a permissions/access failure rather than 401.

6. **Choose the correct smoke-test path.**
   - Use `hermes send --to <target>` for a direct outbound platform smoke test. This reuses Hermes credentials and does not depend on a healthy long-running gateway for bot-token platforms like Discord/Telegram.
   - Restart / inspect the gateway only when the user wants the full inbound conversational path tested.

7. **For Discord DMs, separate outbound success from inbound authorization.**
   - A successful `hermes send --to discord:<channel-or-dm-id>` proves outbound posting only.
   - If channel posting works but DM interaction is ignored or yields `Unauthorized user`, inspect `DISCORD_ALLOWED_USERS` before debugging prompts or sessions.
   - Prefer **numeric Discord user IDs** in `DISCORD_ALLOWED_USERS` for DM testing. Username-based entries can require resolution against shared guild member lists; that can fail in DM-only setups or when the bot lacks the member context needed to resolve names.
   - After changing `DISCORD_ALLOWED_USERS`, remember the running gateway may still hold the old allowlist in memory until reconnect/restart.

8. **Credential hygiene.**
   If the user pasted a live token into chat, advise rotating it again after the immediate test succeeds. Do not preserve raw secrets in files, notes, memory, or skills.

## Pitfalls
- Treating Discord Application ID or Public Key as the bot token.
- Assuming a new Discord server inherits the bot membership automatically.
- Debugging the wrong home-channel ID before resolving a 401 auth failure.
- Using `~/.hermes` on Windows/git-bash without checking whether it maps to the active Hermes home.
- Claiming the gateway path is broken before trying `hermes send` for a simpler outbound smoke test.
- Assuming `DISCORD_ALLOWED_USERS=<username>` is safe for DMs; in practice, DM authorization is more reliable with the numeric Discord user ID.
- Forgetting that a running gateway may cache the pre-edit allowlist until restart/reconnect.

## Positive verification
A real verification pass should capture at least one of:
- Gateway log line showing successful Discord/Telegram connection.
- `hermes send` success to the requested platform target.
- A confirmed match between configured home-channel ID and the actual intended channel.

## Reference material
- `references/discord-auth-triage.md` — Discord-specific failure signatures and corrective actions.
- `references/discord-dm-allowlist.md` — why DM auth can fail even when channel posting works, and when to use numeric Discord user IDs.