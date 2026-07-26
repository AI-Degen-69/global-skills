---
name: polymarket-ab-watchdog
description: >-
  Build/repair a Hermes cron that monitors the live Polymarket A/B-test
  dashboard (Railway bots -> Turso -> Vercel) and delivers a rich report
  (real emoji + box-drawing table) to a Discord channel. THE KEY LESSON:
  Hermes cron delivery mangles non-ASCII. no_agent strips all non-ASCII
  (emoji/box chars dropped silently); agent-relay verbatim silently drops
  the payload; the ONLY reliable path for emoji + Unicode boxes is
  self-delivery via a Discord channel WEBHOOK. Use this skill for any cron
  that must post formatted/emoji content to Discord.
---

# polymarket-ab-watchdog

Monitors the live Polymarket A/B significance system and posts a status
report to Discord. The headline value of this skill is the **delivery
constraint arc** discovered the hard way (6 failed iterations) — read it
before building any emoji/table cron.

## What the watchdog monitors

```
Railway bots (bone, early_lean)  ->  Turso DB  ->  Vercel dashboard
                                                  /health.json   (bot liveness + Turso connectivity)
                                                  /data.json     (metrics, per_market pnl/vol series)
```

No credentials needed — the dashboard HTTP API is public. The old watchdog
pointed at a **retired local SQLite** and was dead. Never point it back at
local state; read the dashboard.

## 🔴 The delivery-constraint arc (read this first)

Three delivery paths were tested. Only the third works for rich content.

### Path A — `no_agent: true`, cron `deliver: discord:CH`
The script's stdout is shipped verbatim. **This path strips ALL non-ASCII.**
- ❌ Real emoji (🟢📊) → dropped silently
- ❌ Box-drawing Unicode (┌┬┐│─┼) + triple-backtick fence → dropped silently
- ✅ Pure ASCII (`[OK]`, `+----+`, `#....` bars) → delivered fine
- Verdict: use only for ASCII reports. Reliable, zero token cost.

### Path B — `no_agent: false` (agent cron) with "relay stdout verbatim" prompt
The agent runs the script and is told to paste output exactly. **Both runs
reported `last_status: ok` yet NEVER landed in the channel** — the agent
silently dropped the verbatim payload. Tested with model `null` and with
`anthropic/claude-3.5-haiku`. Both failed.
- Verdict: DO NOT use agent-relay for verbatim formatted payloads in this
  install. The agent "helpfully" strips what it deems noise.

### Path C — ✅ Script self-delivers via a Discord channel WEBHOOK
The script POSTs its own formatted report to a webhook URL. Webhooks render
real emoji, Unicode box tables, and code fences perfectly (different send
path from both cron paths).
- Cron set to `no_agent: true` + `deliver: local` so it ONLY runs the script
  (no double-post from the broken stdout path).
- Verdict: the reliable path for emoji + boxes. Costs nothing (webhooks need
  no bot token to POST).

**Rule of thumb:** plain status text → Path A is fine. Anything with emoji or
Unicode tables → Path C (webhook). Skip Path B entirely.

## Webhook setup

1. In the target channel: Edit Channel → Integrations → Webhooks → New
   Webhook → Copy Webhook URL. (The `config.yaml` `discord:` value is a USER
   token — `POST /channels/.../webhooks` returns 401 with it. Don't try to
   mint webhooks programmatically; paste the URL the user creates.)
2. Save the URL to a companion file next to the script (e.g.
   `.ab_watchdog_webhook.txt`) or pass via `WEBHOOK_URL` env. Keep it out of
   the script body / git.

## ⚠️ Critical pitfall: Discord 403 on webhook POST

`urllib.request.urlopen` sends `User-Agent: Python-urllib/x.y`, which Discord
**rejects with 403 Forbidden**. You MUST set an explicit User-Agent header or
the webhook post fails. (curl works without it; Python does not.)

```python
req = urllib.request.Request(
    url, data=payload,
    headers={"Content-Type": "application/json",
             "User-Agent": "hermes-ab-watchdog/1.0"},   # REQUIRED
    method="POST")
```

## Report design (proven)

- **Health section** 🩺: per-arm status dot (🟢HEALTHY / 🟡STALE / 🔴DEAD) +
  last-activity age; dashboard→Turso connectivity.
- **Conditional columns**: during accumulation show only
  `arm / resolved / win% / pnl / pnl-per-vol`. **Hide `z` and `edge` until both
  arms hit TARGET (300) resolved markets** — that's the only point a z-test is
  meaningful. At the milestone, reveal the full table with z + edge verdict.
- **Progress bars** 🟩⬜ to significance.
- **Alert block** 🚨 when an arm is DEAD/STALE or Turso connectivity lost.
- **Significance block** 🏆 at TARGET: full table + conclusion (edge vs luck at
  p<0.05, two-sided z>1.96).
- Always-on (post every tick, including healthy) — the user wants a heartbeat,
  not a silent watchdog.

### Statistics (don't get this wrong)
- Per-market `pnl_per_volume_pct` from the dashboard is already **NET of taker
  fees** (0.07). Null hypothesis per arm = mean == 0 (profitability vs luck).
- z-test: `z = mean / (std/sqrt(n))` over per-market pnl/vol series. Significance
  at `|z| > 1.96` (95% two-sided). "luck" if not significant, "EDGE" if significant.
- `TARGET = 300` resolved markets/arm (env `AB_TARGET_OVERRIDE` for debug).
- Dashboard `HEALTHY` threshold ~420s; mirror `HEALTHY_MAX_AGE = 420`.

## Reference implementation (full working script)

> ⚠️ `ab_watchdog.py` was retired and moved to `hermes/scripts/.trash/` (2026-07-26). The polymarket-bot workflow is dormant. The skeleton below is historical reference only.

Live copy (retired): `~/AppData/Local/hermes/scripts/.trash/ab_watchdog.py`. The skeleton:

```python
import os, sys, json, math, datetime, urllib.request, urllib.error

DASHBOARD = os.environ.get("AB_DASHBOARD",
            "https://polymarket-ab-dashboard.vercel.app").rstrip("/")
TARGET   = int(os.environ.get("AB_TARGET_OVERRIDE", "300"))
Z_CRIT   = 1.96
HEALTHY_MAX_AGE = 420
ARMS = ("bone", "early_lean")
PM_KEY = {"bone": "bone", "early_lean": "early"}   # per_market key differs
UA = {"User-Agent": "hermes-ab-watchdog/1.0"}

def webhook_url():
    if os.environ.get("WEBHOOK_URL"):
        return os.environ["WEBHOOK_URL"].strip()
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        ".ab_watchdog_webhook.txt")
    try:
        return open(here, encoding="utf-8").read().strip() or None
    except OSError:
        return None

# ... fetch_json, ztest over per_market series, conditional columns,
#     box_table (with ┌┬┐│─┼), health_alert, significance_report ...
# key: deliver() POSTs report to webhook_url() with UA header; returns bool.

def deliver(report):
    url = webhook_url()
    if not url:
        print(report); return False
    payload = json.dumps({"content": report}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "hermes-ab-watchdog/1.0"},  # REQUIRED
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status in (200, 204)
    except Exception as e:
        print(f"[ERR] webhook post failed: {e}", file=sys.stderr)
        return False

def main():
    return 0 if deliver(build_report()) else 1
```

## Cron wiring (final, working)

```
cronjob update ff88c43340df \
  --no_agent true \
  --deliver local \
  --enabled_toolsets '["terminal"]' \
  --script ab_watchdog.py
```
`no_agent + deliver:local` = run script only; script self-delivers via webhook.
No double-post.

## Verification (do all of these before declaring done)

1. **Compile**: `python -m py_compile ab_watchdog.py`
2. **Webhook live test**: run the script directly; confirm exit 0 and a new
   `bot-cron-webhook` message in the channel with emoji + box table rendered.
3. **No 403**: if you see `[ERR] webhook post failed: HTTP Error 403`, the
   User-Agent header is missing — add it.
4. **Cron end-to-end**: `cronjob run <id>`; wait ~12s; `fetch_messages` on the
   channel → exactly ONE new webhook message, none from `hermes_bot4321`
   (proves no double-post / broken stdout path).
5. **Conditional columns**: confirm z/edge absent during accumulation; force
   `AB_TARGET_OVERRIDE=2` to confirm the significance block appears with z+edge.

## Pitfalls summary

- ❌ Don't use `no_agent` for emoji/Unicode — it strips non-ASCII silently.
- ❌ Don't use agent-relay verbatim — it silently drops the payload.
- ❌ Don't POST to Discord webhook without a User-Agent — 403.
- ❌ Don't point the watchdog at retired local SQLite — read the dashboard.
- ❌ Don't show z/edge before TARGET resolved — meaningless before then.
- ✅ Webhook self-delivery + `no_agent`/`deliver:local` cron = reliable emoji.

> ⚠️ `cron_delivery_lint.py` was retired and moved to `hermes/scripts/.trash/` (2026-07-26). The companion-lint section below is historical reference only; do not run it against current crons.

When first written it caught two pre-existing traps the user didn't know
about: `c24a9a0e6970` (skill-trend, ⭐🔥🌐💡) and `b96fbcc734a0` (gbrain
brain maintenance, 🧠🔴🟢Δ) — both relied on `no_agent`+Discord `deliver` and
were silently stripped. The A/B watchdog itself is correctly NOT flagged
(deliver:`local` + webhook self-delivery), and the Discord Gateway Watchdog
is INFO'd as a double-post risk.
