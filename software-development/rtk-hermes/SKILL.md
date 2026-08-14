---
name: rtk-hermes
description: Use when apply the rtk prefix to terminal commands whose output is verbose and whose exact formatting the mode
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [rtk, token-savings, shell, cli-compression, workaround]
    related_skills: []
---

# RTK in Hermes — Manual Prefix Pattern (NOT the plugin)

RTK (`github.com/rtk-ai/rtk`, binary `rtk` ≥0.42) compresses shell command
output (ls, git, grep, find, logs) to cut LLM token usage. It works great as a
**manual command prefix** in Hermes. The shipped `rtk init --agent hermes`
plugin WORKS on Hermes v0.20.0+ (auto-rewrites terminal commands via `pre_tool_call` — verified 2026-08-05). Manual prefix is the fallback if the plugin isn't loaded.

## When to use
Apply the `rtk` prefix to terminal commands whose output is verbose and whose
exact formatting the model does NOT need verbatim:
- `ls`/`ls -la` on large dirs → `rtk ls -la <dir>`
- recursive `find` → `rtk find <path> -name "..."`
- `grep -r`/`rg` → `rtk grep -r "pat" <dir>` (scope it; never grep the whole repo — see pitfalls)
- `git log`/`git status`/`git diff` → `rtk git log --oneline -N`
- build/test logs → `rtk log` (stdin) or `rtk dotnet`/`rtk tsc`/`rtk jest`
- docker/kubectl/aws output → `rtk docker ...`, `rtk kubectl ...`, `rtk aws ...`

Do NOT wrap: interactive commands, commands whose precise stdout the model must
see byte-for-byte, or anything piped into another process that expects raw shape.

## Exact commands (verified on this machine)
```
rtk ls -la <dir>          # compact perms+name lines
rtk find <path> -name X   # compact tree
rtk grep -r "pat" <dir>   # groups by file, strips whitespace  (SCOPE THE DIR)
rtk git log --oneline -N  # compact log
rtk log                   # stdin: filters [ERROR]/[WARN] log streams only
rtk gain                  # show token-savings tally (global scope)
```

## Native plugin status (updated 2026-08-05)
**On Hermes v0.20.0 + rtk 0.42.4 the plugin WORKS.** `rtk init --agent hermes`
installs `plugins/rtk-rewrite/` which calls `ctx.register_hook("pre_tool_call",
_pre_tool_call)` and rewrites `args["command"]` in place (e.g. `ls -la X` →
`rtk ls -la X`, via `rtk rewrite`). Verified by loading the hook directly: it
registered and rewrote a simulated terminal call. **REQUIRES a Hermes restart**
after `rtk init` — plugins load at process start, so commands stay raw until
you restart. After restart, unprefixed `ls`/`git`/`grep` auto-compress;
confirm with `git status`.

**Why it was dead before:** earlier Hermes builds had a directive-only
`pre_tool_call` that discarded RTK's in-place mutation. That contract changed;
the current plugin uses the supported `register_hook` API and works. (Historic
detail, pre-v0.20.0: the old plugin returned None after mutating args and
relied on PreToolUse command re-execution, which Hermes did not support.)

## Pitfalls
- **Never `rtk grep -r "x" .`** across the whole repo — times out (60s+). Always
  scope to a subdir or pass `-maxdepth`.
- `rtk log` on stdin only compresses `[ERROR]/[WARN]/[INFO]`-shaped lines;
  plain text passes through unchanged (no token win).
- `rtk gain` reports GLOBAL scope (counts Claude Code's rtk hook + cron too),
  not per-session Hermes usage. Don't use it as proof the Hermes hook works.
- Manual prefixing gives PARTIAL savings only (you choose which commands).
  The full automatic integration is unavailable until RTK fixes the plugin or
  Hermes adds a pre_tool_call command-rewrite return shape.

## Upstream fix to track
File/check issue on `rtk-ai/rtk`: `init --agent hermes` produces a plugin
incompatible with Hermes's directive-only `pre_tool_call` contract.
