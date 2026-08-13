---
name: windows-silent-cron
description: Use when a Hermes cron job (no_agent script, or any .py/.sh cron) flashes a console window, or when hardening 
---

# Windows Silent Cron — no console flash from Hermes cron jobs

## When to use
- A Hermes cron job pops a visible CMD/console window when it runs (you see `cmd.exe` / `python.exe` / `git.exe` flash).
- You are authoring a new `.py` or `.sh` cron script and want it silent by default.
- After a `hermes update` or venv rebuild, cron jobs start flashing again (the global patch got wiped).

## Root cause (the part everyone gets wrong)
The Hermes cron scheduler runs `.py` jobs with `argv = [sys.executable, script_path]`
(`hermes-agent/cron/scheduler.py`, ~line 2094). `sys.executable` is the **Hermes venv
python** (3.11 in this install), NOT the system python. The outer process is already
hidden (`windows_hide_flags()` at ~line 2099, i.e. `CREATE_NO_WINDOW`), but **any
console child the script spawns** (yt-dlp, git, node, a nested `python.exe`) gets a fresh
console window because the script's own `subprocess` calls don't pass the flag.

The trap: **venv pythons have `ENABLE_USER_SITE = False`**. So a `usercustomize.py` placed
in `~/AppData/Roaming/Python/Python3XX/site-packages` (user site) is **never imported** for
venv children. That's why a "global" usercustomize in user site appears to do nothing for
cron jobs. It must go in the **venv's own site-packages**.

## The two-layer pattern (proven on this machine)

### Layer 1 — global `usercustomize.py` in the VENV site-packages (required)
Install at: `hermes-agent/venv/Lib/site-packages/usercustomize.py`
(absolute: `C:\Users\Tiger\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages\usercustomize.py`)

```python
"""Global silent-subprocess policy for Hermes cron scripts (Windows).
Patches subprocess.Popen so console children spawn with CREATE_NO_WINDOW
(0x08000000) when HERMES_CRON_SESSION=1. Inert for interactive agents.
"""
import os
import subprocess
import sys

_CREATE_NO_WINDOW = 0x08000000  # hide child console window, keep stdio attached

if os.environ.get("HERMES_CRON_SESSION") == "1" and sys.platform == "win32":
    _orig_popen_init = subprocess.Popen.__init__

    def _silent_popen_init(self, *args, **kwargs):
        if "creationflags" not in kwargs:
            kwargs["creationflags"] = _CREATE_NO_WINDOW
        else:
            kwargs["creationflags"] = kwargs["creationflags"] | _CREATE_NO_WINDOW
        _orig_popen_init(self, *args, **kwargs)

    subprocess.Popen.__init__ = _silent_popen_init
```

Why this works: the scheduler sets `HERMES_CRON_SESSION=1` process-wide and passes it into
every child's env (via `_sanitize_subprocess_env`). Interactive gateway/agent sessions never
get the marker, so the patch is inert there. `CREATE_NO_WINDOW` hides the window but keeps
stdio — `capture_output=True` (which the scheduler uses to deliver the report) still works.

**Do NOT use `DETACHED_PROCESS`** — it severs the child's stdio and breaks the scheduler's
output capture (the report would go missing).

### Layer 2 — bash-launched console children (`run_hidden.py`)
`usercustomize` only patches python's `subprocess`. When a `.sh` cron wrapper runs `git` (or
`python.exe`) directly, bash spawns that console child **without** the flag → flash. Cover it
with a `pythonw`-based hidden runner placed in the scripts dir:

`scripts/run_hidden.py`:
```python
#!/usr/bin/env pythonw
"""Windowless launcher for bash cron children (Windows). Usage: run_hidden.py <cmd> [args...]
Runs the child with CREATE_NO_WINDOW, inheriting stdio so $(...) capture + exit codes work."""
import subprocess, sys
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: run_hidden.py <cmd> [args...]\n"); return 2
    stdin = sys.stdin if sys.stdin is not None else subprocess.DEVNULL
    stdout = sys.stdout if sys.stdout is not None else subprocess.DEVNULL
    stderr = sys.stderr if sys.stderr is not None else subprocess.DEVNULL
    return subprocess.run(sys.argv[1:], stdin=stdin, stdout=stdout, stderr=stderr,
                          creationflags=_CREATE_NO_WINDOW).returncode

if __name__ == "__main__":
    sys.exit(main())
```
Route bash's console children through it:
- `git` → `"$HERE/run_hidden.py" git add -A` etc. (the `vault_autopush.sh` wrapper that used this pattern was retired to `hermes/scripts/.trash/` on 2026-07-26; the `vault_autopush.py` port remains the live job and runs `git` directly)
- python children in `.sh` → use `pythonw` (GUI subsystem, never allocates a console) instead of `python.exe`/`python3.14`.

Note: `cygstart` is **missing** on this MSYS install — don't rely on it; `pythonw` + `run_hidden.py` is the reliable path.

### Layer 3 (optional belt-and-suspenders) — per-script `CREATE_NO_WINDOW`
You can also patch the script's own `subprocess.run` calls directly:
```python
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
subprocess.run([...], creationflags=_CREATE_NO_WINDOW)
```
Once Layer 1 is proven in the venv, this is redundant and can be stripped for cleanliness.

## Pitfalls
- **User site-packages is a trap for venv-run cron.** Always install `usercustomize.py` in
  `hermes-agent/venv/Lib/site-packages/`, never in `~/AppData/Roaming/Python/...`.
- After `hermes update` or a venv recreate, re-deploy Layer 1 (the venv dir is rebuilt).
- `DETACHED_PROCESS` breaks report delivery — never use it.
- `urllib` gets `403 error 1010` for Discord REST in this env — use `curl`, not Python urllib.
- Don't edit `hermes-agent/` core source (pull-only upstream); `usercustomize` + `run_hidden.py`
  are external files and survive updates.

## Verification
```bash
# 1. Confirm usercustomize loads + patches Popen under the cron marker (venv python):
HERMES_CRON_SESSION=1 /c/Users/Tiger/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import usercustomize, subprocess, inspect
print('usercustomize loaded:', usercustomize.__name__)
print('wrapper def present:', hasattr(usercustomize, '_silent_popen_init'))
print('Popen patched:', subprocess.Popen.__init__ is usercustomize._silent_popen_init)
"
# expect: loaded=True, wrapper def=True, patched=True

# 2. Confirm pristine outside cron (no over-patch):
/c/Users/Tiger/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import subprocess, inspect
print('pristine:', subprocess.Popen.__init__.__qualname__ == 'Popen.__init__')
"

# 3. Live: fire the cron job, confirm it delivers to Discord with no visible window.
```
Note: `inspect.getsource(subprocess.Popen.__init__)` can read as the *wrapper* or *orig*
depending on import timing — prefer the identity check
(`subprocess.Popen.__init__ is usercustomize._silent_popen_init`) which is unambiguous.

## Coverage map (this install)
| Layer | File | Covers |
|---|---|---|
| 1 | `venv/Lib/site-packages/usercustomize.py` | all `.py` cron jobs' `subprocess` children (yt-dlp, git, nested python) |
| 2 | `scripts/run_hidden.py` + `pythonw` | `.sh` wrappers' direct `git` / `python` children |
| 3 | per-script `CREATE_NO_WINDOW` | optional redundancy; strip once Layer 1 proven |

## Re-deploy guard (post-hermes update)
`hermes update` / a venv recreate wipes `venv/Lib/site-packages/usercustomize.py`,
silently bringing back the console flash. Two ways to catch it:

**1. One-line post-update check (alerts if the guard was wiped):**
```bash
test -f "${HERMES_HOME:-$HOME/AppData/Local/hermes}/hermes-agent/venv/Lib/site-packages/usercustomize.py" || { echo "ALERT: venv usercustomize.py missing - cron console-flash guard gone after update. Re-deploy Layer 1 from this skill."; exit 1; }
```

**2. Self-healing script (recommended):** `scripts/cron_flash_guard_check.sh`
re-deploys from the user-site source if present, alerts (exit 1) only if both
copies are missing. Run it manually after an update, or wire it as a `no_agent=True`
cron watchdog (e.g. `0 9 * * *`) so an update-triggered wipe is auto-fixed before
the next manual cron tick would flash:
```bash
bash "$HERMES_HOME/skills/devops/windows-silent-cron/scripts/cron_flash_guard_check.sh"
```

