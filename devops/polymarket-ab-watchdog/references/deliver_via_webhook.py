"""Generic Discord webhook delivery helper.

Reusable by ANY Hermes cron that needs to post emoji / Unicode / formatted
content to a Discord channel. Paste this into a cron script and call
deliver_via_webhook().

WHY THIS EXISTS (the trap):
  - no_agent cron delivery strips ALL non-ASCII (emoji + box chars dropped).
  - agent-relay verbatim silently drops the payload in this install.
  - A Discord channel WEBHOOK renders emoji + Unicode boxes + code fences
    perfectly and needs NO bot token to POST. This is the reliable path.

CRITICAL: Discord rejects urllib's default `Python-urllib` User-Agent with
HTTP 403. You MUST send an explicit User-Agent header (see below).
"""

import os
import sys
import json
import urllib.request
import urllib.error


def get_webhook_url(env_var: str = "WEBHOOK_URL",
                    companion_file: str | None = None) -> str | None:
    """Resolve the webhook URL.

    Precedence:
      1. Environment variable (e.g. WEBHOOK_URL).
      2. A companion .txt file next to this script (path given by caller).
      3. Auto-detect `<script_dir>/.webhook_url.txt`.

    The URL itself is NEVER hardcoded in the script body / committed.
    """
    if os.environ.get(env_var):
        return os.environ[env_var].strip()
    candidates = []
    if companion_file:
        candidates.append(companion_file)
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        ".webhook_url.txt")
    candidates.append(here)
    for path in candidates:
        try:
            return open(path, encoding="utf-8").read().strip() or None
        except OSError:
            continue
    return None


def deliver_via_webhook(content: str,
                        url: str | None = None,
                        *,
                        username: str | None = None,
                        timeout: int = 20) -> bool:
    """POST `content` (plain text / markdown) to a Discord webhook.

    Returns True on 2xx, False on any failure (and prints a stderr note so the
    cron still exits cleanly). Never raises.

    Args:
        content:  message body (Discord markdown; <=2000 chars).
        url:      webhook URL. If None, resolved via get_webhook_url().
        username: optional override for the posting bot name.
    """
    if url is None:
        url = get_webhook_url()
    if not url:
        print("[WARN] no webhook URL configured; printing to stdout instead.",
              file=sys.stderr)
        print(content)
        return False

    payload = {"content": content}
    if username:
        payload["username"] = username
    data = json.dumps(payload).encode("utf-8")

    # REQUIRED: explicit User-Agent. Without it Discord returns 403 Forbidden.
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "hermes-cron-webhook/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status in (200, 204)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"[ERR] webhook post failed: {type(e).__name__}: {e}",
              file=sys.stderr)
        return False


# --- minimal usage ---------------------------------------------------------
if __name__ == "__main__":
    report = "🟢 **Hello from a cron** — emoji + boxes render via webhook."
    ok = deliver_via_webhook(report, username="my-cron-webhook")
    sys.exit(0 if ok else 1)
