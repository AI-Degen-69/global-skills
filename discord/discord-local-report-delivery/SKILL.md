---
name: discord-local-report-delivery
description: Use when a local cron report must be surfaced into a Discord message on Windows.
---

# Discord Local Report Delivery (Windows, local files)

When a cron job generates an HTML (or other) report on the user's local
Windows machine and must surface it in a Discord message:

**DO:**
- Emit the on-disk path inside a Discord **code block** (``` ... ```).
  Example:
  ```
  C:\Users\Tiger\Agents\Docs-and-Research\Last30Days\2026-07-19\brief.html
  ```
- Add a one-line tip: "copy the path above into Explorer or your browser's
  address bar to open the report."

**DON'T:**
- Don't attach the file as a Discord upload (`discord_post_file.py` multipart).
  The user said attaching adds friction and gives him nothing — he can't open
  the attachment inline in Discord, and it's more steps than a path.
- Don't stand up a localhost HTTP server (e.g. `report_server.py` on
  `127.0.0.1`) to produce a clickable `http://` link. Discord DOES auto-
  linkify bare `http://` URLs, BUT:
  - the server is unreachable from the user's actual client unless it's
    running persistently (it isn't by default),
  - `schtasks /Create` is blocked by the sandbox ("Access is denied"),
  - so the "clickable" link is dead from the user's side. Claiming it
    "serves" the file is false if the server isn't a live persistent process.
- Don't use `file://` URLs or bare `file://` paths in the message — Discord
  does NOT linkify `file://` paths, and a path inside a code block is already
  copy-pasteable, which is what the user wants.

**Why (user's stated model):** he runs Hermes Desktop / Discord on the same
Windows box. The lowest-friction path for him is: read the path in Discord →
paste into Explorer or browser → double-click. Anything that requires a
running service or an attachment download is friction he explicitly rejected.

**Verification note:** if you ever DO test a localhost server, verify it is
reachable as a *persistent* process from the user's perspective before
claiming it works. A throwaway test process that dies when your tool call
ends does not count.

## When this applies
Cron jobs that write report files to local disk and deliver a Discord message:
- `skill-trend-every-3-days` (script `send_skill_trend.py`)
- `hermes-youtube-trend-every-3-days` (script `hermes-youtube-trend_collect.py`)
Both already render a designed HTML page (`build_html.py` /
`build_html_youtube.py`) and deliver the path in a code block.
