---
name: windows-terminal-popup-fix
description: Use when fixing the Windows conhost terminal-popup flash on process spawn.
version: 1.0.0
author: Hermes
tags:
  - Windows
  - subprocess
  - conhost
  - console-flash
  - Discord
  - gateway
  - watchdog
---

# Windows Terminal-Window Popup Fix

## When to use
- On Windows, every time the agent runs a `terminal` tool call (or any background
  process), a new console window (conhost) flashes/pops up visibly — even though the
  process is supposed to be headless. Frequently noticed "while the bot is typing".
- Symptom: a black terminal window briefly appears per command. On a GUI host (Hermes
  Desktop) this is jarring and accumulates into many windows.

## Root cause
`CREATE_NO_WINDOW` (`0x08000000`, what `windows_hide_flags()` returns) only hides the
**immediate** child's console. When that child (e.g. `bash.exe`) launches a console
**grandchild** — `git`, `python`, `node`, `cmd`, anything with a console subsystem —
Windows allocates a fresh `conhost` for the grandchild. That grandchild console is
visible. So `windows_hide_flags()` alone does NOT stop the flash for real agent
workloads.

Two affected spawn sites in hermes-agent:
1. `tools/environments/local.py::_run_bash` — the foreground terminal-tool path
   (default `pty=False`). Used for normal `terminal()` calls. This is the primary
   flash source.
2. PTY paths (`tools/process_registry.py` PTY branch, `hermes_cli/win_pty_bridge.py`)
   — spawn `winpty.PtyProcess` with no console suppression. pywinpty mostly hides its
   own console, but the canonical fix still applies.

## The fix (canonical, tree-wide)
Use **`STARTUPINFO` with `wShowWindow=SW_HIDE` + `dwFlags=STARTF_USESHOWWINDOW`**
alongside `CREATE_NO_WINDOW`. `STARTUPINFO` propagates the hidden-window flag down the
entire spawned process tree, so grandchildren never get a visible console.

Helper added to `hermes_cli/_subprocess_compat.py`:

```python
def windows_hide_startupinfo():
    """Return a subprocess.STARTUPINFO that hides the child console window
    across the whole spawned tree (grandchildren included). None on non-Windows."""
    if not IS_WINDOWS:
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    return si
```
(also add `import subprocess` to that module if missing.)

Apply in `local.py::_run_bash` after building `_popen_kwargs`:

```python
_popen_kwargs = {"creationflags": windows_hide_flags()} if _IS_WINDOWS else {}
if _IS_WINDOWS:
    _popen_kwargs["startupinfo"] = windows_hide_startupinfo()
proc = subprocess.Popen(args, ..., start_new_session=True, cwd=_popen_cwd, **_popen_kwargs)
```
(import `windows_hide_startupinfo` alongside `windows_hide_flags`.)

For PTY spawns, wrap the argv in `winpty` with the same hidden intent where the API
allows; otherwise ensure the foreground pipe path (already covered) is the default.

## Verification
1. `python -c "from hermes_cli._subprocess_compat import windows_hide_startupinfo,
   windows_hide_flags; si=windows_hide_startupinfo(); assert si.wShowWindow==0 and
   si.dwFlags & subprocess.STARTF_USESHOWWINDOW"` — must pass on Windows.
2. Run a real console grandchild under the new kwargs, e.g. `git --version` via
   `subprocess.Popen([...], creationflags=windows_hide_flags(),
   startupinfo=windows_hide_startupinfo(), start_new_session=True)` — exit 0, and
   NO visible window during execution.
3. Restart the gateway (`hermes gateway restart`) so patched `local.py` loads.
4. Trigger agent terminal calls from Discord/Telegram and confirm no window pops.

## Watchdog pattern (catch a dead/inbound-broken gateway)
A `no_agent=True` cron script that stays SILENT when healthy (exit 0) and prints a
diagnostic only on failure (exit 2) — so the cron delivery alerts you instead of
spamming every tick. See `scripts/discord_gateway_watchdog.py` (in this profile's
Hermes home). It checks, in order:
  1. `gateway_state.json` exists and `gateway_state == "running"`.
  2. The recorded gateway PID is actually alive (guards stale state after a crash).
  3. `platforms.discord.state == "connected"`.
  4. Live outbound probe `hermes send --to discord "..."` succeeds (token + delivery).
  5. Inbound liveness: scans `logs/agent.log` for a `platform=discord` inbound turn in
     the last N hours; WARN-only if stale (bot "connected" but not answering).
Register with `cronjob create schedule='*/15 * * * *' no_agent=true
script='scripts/discord_gateway_watchdog.py' deliver='discord'`.

## Pitfalls
- `CREATE_NO_WINDOW` ≠ full suppression. If you only add that flag and still see
  flashes, the grandchild-console case is what's biting you — add `STARTUPINFO`.
- `startupinfo` is ignored on POSIX; always gate with `if _IS_WINDOWS` / return `None`
  off-Windows so the helper is a safe no-op elsewhere.
- Restart the gateway after editing `local.py`/`_subprocess_compat.py` — the running
  process holds the stale code in memory; a fresh `hermes send` can still succeed while
  inbound dispatch is dead. Verify with a live inbound message, not just outbound.
- A "connected" Discord state in `gateway_state.json` does NOT prove the bot answers.
  Always confirm with a real inbound test message; the 100-message
  `discord_nonconversational_messages.json` tracker only records the bot's OWN outbound
  status bumps, not inbound drops.
