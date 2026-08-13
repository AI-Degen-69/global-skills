---
name: browser-use-hermes-integration
description: Use when the user wants Hermes itself to gain Browser Use capability.
version: 1.0.0
created_by: agent
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
---

# Browser Use + Hermes integration

## When to use

Use this when the user wants Hermes itself to gain Browser Use capability, including either:

- Hermes native Browser Use cloud browser backend
- `browser-harness` local/global CLI installation
- Browser Use API key setup and verification
- Windows-specific install/verification of `browser-harness`

## Core rule

Do not stop at config writes. Verify with a real command path that proves Browser Use works.

## Preferred sequence

1. Read Browser Use docs starting with `llms.txt` and the Hermes integration page.
2. Save `BROWSER_USE_API_KEY` into the active Hermes profile `.env`.
3. Set Hermes config `browser.cloud_provider: browser-use`.
4. Clone `browser-harness` into a durable path such as `~/Developer/browser-harness`.
5. Install it as an editable global tool.
6. Verify both layers:
   - `hermes status` shows Browser Use configured
   - `browser-harness` runs
   - a real Browser Use-backed browser session can be created and used

## Hermes native cloud-browser setup

Write the API key to the active profile env file as:

```env
BROWSER_USE_API_KEY=...
```

Then set:

```yaml
browser:
  cloud_provider: browser-use
```

Positive verification:

- `hermes status` should show `Browser Use` as configured.
- Read back the relevant `config.yaml` block or line to confirm `cloud_provider: browser-use`.

## browser-harness install

Recommended durable repo path:

```bash
~/Developer/browser-harness
```

Preferred install command:

```bash
uv tool install -e .
```

### Windows pitfall: uv-managed Python mismatch on editable install

On Windows, editable `uv tool install -e .` can fail inside uv-managed Python with `AssertionError: SRE module mismatch`.

When that happens, retry by forcing uv to use the live Hermes/session interpreter and disable uv-managed Python for the tool build:

```bash
uv tool install -e . --python "<live-python-exe>" --no-managed-python --force
```

Use the currently-running Hermes/session interpreter path, not a guessed system Python.

## Verification standard

`browser-harness --doctor` alone is not enough. It can show no active browser connection even when installation succeeded and cloud mode is usable.

Separate verification into two paths on Windows:

### 1) Cloud path

Use a real cloud-browser exercise for positive verification:

- provision Browser Use cloud browser
- open a known URL such as `https://example.com/`
- confirm the returned title/URL from `page_info()` or equivalent runtime output
- stop the remote daemon/browser cleanly

### 2) Local Chrome attach path

If the user wants `browser-harness` to control their already-open local Chrome, require positive proof from Chrome itself and from a real harness action:

- open `chrome://inspect/#remote-debugging`
- enable **Allow remote debugging for this browser instance**
- confirm Chrome shows a server such as `127.0.0.1:9222`
- then run a real harness action like:
  - `new_tab('https://example.com')`
  - `wait_for_load()`
  - `page_info()`

Do not treat an earlier `--doctor` failure as final if remote debugging was still disabled at that time. Re-run attach verification after the Chrome setting is enabled.

6. Stop the remote daemon/browser cleanly.

Success criteria:

- Browser ID returned
- Live URL returned
- `page_info()` reports the expected page URL/title
- Remote daemon stopped cleanly

## Local-browser mode note

If `browser-harness --doctor` reports Chrome running but daemon attach unavailable, local-profile Chrome remote debugging is still not enabled. For local shared-browser mode, the human must enable it in Chrome via:

```text
chrome://inspect/#remote-debugging
```

Then tick **Allow remote debugging for this browser instance** and approve the popup.

This does not block Browser Use cloud mode.

## References

- `references/windows-verification.md` — concrete Windows verification flow and pitfalls for Browser Use + browser-harness.

## Pitfalls

- Do not declare success after only writing `.env` or config.
- Do not treat `browser-harness --doctor` as sufficient proof of Browser Use cloud functionality.
- Do not guess Python paths on Windows when uv editable install fails; use the live interpreter path from the current session.
- Do not block closeout on local Chrome remote-debugging if the user only needs cloud-browser mode and cloud verification already passed.

## Closeout

Report separately:

- config state verified
- tool install verified
- real Browser Use session verified
- local Chrome mode still pending or not needed
