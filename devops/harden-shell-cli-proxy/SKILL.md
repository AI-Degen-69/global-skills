---
name: harden-shell-cli-proxy
description: Use when wiring a CLI proxy (rtk) into a shell safely.
---

# Harden a shell CLI-proxy into the user's shell

Use this when a user installs a context-compression CLI proxy (rtk, or similar)
and wants it wired into their shell as the default for noisy commands — safely,
with no footguns. The goal is **zero friction**: aliases that can't hang,
errors that are honest, and tooling that never false-fails an installed binary.

## Preconditions
- Identify the proxy binary and confirm it resolves on PATH: `command -v rtk`.
- Identify the shell rc file: prefer `~/.bashrc` (works for login + non-login
  under bash). For zsh use `~/.zshrc`. Read it first; never overwrite.
- Know the user's home: on Windows/MSYS use `$HOME` (resolves to
  `C:/Users/<user>`), not `$USERPROFILE` in bash context.

## Step 1 — verify the proxy actually works
Before touching rc, prove the binary loads and proxies a real command:
```bash
rtk --help 2>&1 | head -5
rtk ls 2>&1 | head -3          # current-dir only, must be fast
rtk git log --oneline -3 2>&1  # needs a real repo to test against
```
If `git` complains "not a repo", cd into a known repo (`find $HOME -maxdepth 3
-name .git -type d | head -1`) before testing.

## Step 2 — probe the proxy's sharp edges (do NOT skip)
Run each with an 8s cap so one bad call can't hang the batch:
```bash
timeout 8 rtk ls -R 2>&1 | head   # RECURSION HANG? buffers whole tree, no SIGPIPE
timeout 8 rtk ls --color=always 2>&1 | head  # unknown flag silently DROPPED?
timeout 8 rtk grep -i RTK ~/.bashrc 2>&1 | head  # case flag passthrough?
timeout 8 rtk git branch -a 2>&1 | head  # subcommand passthrough?
timeout 8 rtk git frobnicate 2>&1 | head  # nonsense subcmd -> graceful or corrupt?
timeout 8 rtk err false 2>&1; echo "rc=$?"  # exit-code preserved?
timeout 8 rtk summary echo hi 2>&1  # underlying output preserved?
```
Record the findings. For rtk specifically (verified):
- 🔴 `rtk ls -R` HANGS (no SIGPIPE short-circuit; >60s on a big repo).
- 🟡 Unknown flags silently DROPPED (rc=0, no warning).
- 🟢 git/grep passthrough, `err` exit codes, unsupported subcmds fall through
  to native — does NOT corrupt.

## Step 3 — add bounded aliases (safe subset only)
Append inside a `command -v rtk` guard so sourcing rc without rtk installed is
a no-op:
```bash
if command -v rtk >/dev/null 2>&1; then
  alias ll='rtk ls'
  alias la='rtk ls -a'
  alias lt='rtk tree'          # rtk tree ignores .git/node_modules by default — no hang
  alias gr='rtk grep'
  alias rrg='rtk rg'
  alias glog='rtk git log --oneline'
  alias gst='rtk git status'
  alias gdiff='rtk diff'
  alias derr='rtk err'
fi
```
Rule: only alias subcommands you verified return fast and bounded. Never alias
recursion (`-R`) or anything that hit the hang in Step 2.

## Step 4 — add a timeout kill-switch wrapper
Curbs the hang class. Route hang-prone calls through it, NOT the daily aliases.
```bash
rtkq() {
  timeout 15 rtk "$@"
  local rc=$?
  if [ "$rc" -eq 124 ]; then
    echo "[rtkq] killed after 15s timeout (likely unbounded recursion)" >&2
  elif [ "$rc" -ne 0 ]; then
    echo "[rtkq] rtk exited with code $rc" >&2
  fi
  return "$rc"
}
```
Put `rtkq` inside the same `command -v rtk` guard. Tune 15s per user tolerance.

## Step 5 — add tool front-ends as CALL-TIME functions (not aliases)
For heavy tools (docker/kubectl), define functions that check the binary at
CALL time. This self-activates when the user installs the tool mid-session
(no re-source) and yields a clean "not installed" (rc 127) instead of a
confusing command-not-found.
```bash
dk() {
  command -v docker >/dev/null 2>&1 || { echo "dk: docker not installed" >&2; return 127; }
  rtk docker "$@"
}
kc() {
  command -v kubectl >/dev/null 2>&1 || { echo "kc: kubectl not installed" >&2; return 127; }
  rtk kubectl "$@"
}
# Extending to more tools uses the SAME call-time-function shape. For a tool the
# proxy DOES cover (docker compose), route through rtk; for a tool it does NOT
# cover (helm — rtk has no helm subcommand), proxy the native binary directly.
dc() {
  command -v docker >/dev/null 2>&1 || { echo "dc: docker not installed" >&2; return 127; }
  rtk docker compose "$@"
}
hm() {
  command -v helm >/dev/null 2>&1 || { echo "hm: helm not installed" >&2; return 127; }
  helm "$@"
}
```
Rule of thumb: if `rtk <tool> --help` lists the subcommand → use `rtk <tool>`;
if it does not → proxy native `<tool>` directly. Always guard on the binary.
CRITICAL design decisions proven this session:
- **Keep `dk`/`kc` OFF `rtkq`.** `rtkq`'s 15s kill would murder streaming
  commands — `kubectl logs -f`, `exec -it`, `port-forward`, `docker logs -f`.
  For hang-prone cluster READS use `rtkq kubectl <cmd>` explicitly.
- **`rtk docker`/`rtk kubectl` fall through to native** for off-menu subcommands
  (build/apply/run) — verified: they return real Docker/kubectl help, rc=0, so
  nothing false-fails. No need to special-case them.
- **Do NOT wrap `dk`/`kc`/`rtkq` with external `timeout`.** `timeout` is a binary
  and cannot wrap a shell function — it fails silently with "No such file or
  directory". The timeout lives INSIDE `rtkq` already.

## Step 6 — verify in an INTERACTIVE shell (non-negotiable)
Non-interactive `bash -c` does NOT expand aliases. Test with `bash -i -c`:
```bash
bash -i -c 'source ~/.bashrc; alias ll la lt gr glog gst gdiff derr; type dk kc rtkq'
bash -i -c 'source ~/.bashrc; cd <real repo>; glog -1'        # bounded alias works
bash -i -c 'source ~/.bashrc; rtkq ls -R >/dev/null; echo rc=$?'  # hang killed @15s
```
Test the absent branch by shadowing `command -v`:
```bash
bash -i -c 'source ~/.bashrc; command(){ case "$2" in docker|kubectl) return 1;; *) builtin command "$@";; esac; }; dk --version; echo rc=$?; kc get pods; echo rc=$?'
# expect: "dk: docker not installed" rc=127, "kc: kubectl not installed" rc=127,
# "dc: docker not installed" rc=127, "hm: helm not installed" rc=127
```
Test the real-binary happy path (once the daemon/cluster is up):
```bash
bash -i -c 'source ~/.bashrc; dk ps; dk images; kc get pods'   # real compact output
```
Confirm `bash -n ~/.bashrc` passes at the end.

## Step 7 — persist a compact memory note
Save the hazards + mitigation (bounded aliases, `rtkq`, `dk`/`kc`) so a future
session doesn't re-derive them. One entry, under `memory` target.

## Pitfalls (learned the hard way this session)
1. Non-interactive `bash -c` won't expand aliases → always verify with `bash -i -c`.
2. `timeout dk ...` fails — external timeout can't wrap a shell function. Put the
   timeout INSIDE the wrapper function, or call `rtkq` directly.
3. Alias-guarding on `command -v docker` at LOAD time means installing the tool
   later needs a re-source → use call-time functions instead.
4. Routing streaming tools through a timeout wrapper silently breaks `logs -f`,
   `exec -it`, `port-forward` → keep them off the kill-switch.
5. A blind generic passthrough (e.g. `summ() { rtk summary "$@"; }`) is riskier
   than bounded aliases — `rtk summary` keeps only 2 lines and can hide a real
   failure. Prefer bounded.

## Verification gate (all must pass before claiming done)
- [ ] `bash -n` on rc passes.
- [ ] All aliases + functions resolve after `source` in `bash -i -c`.
- [ ] Known hang killed at the timeout, rc=124, message printed.
- [ ] Bounded alias returns real output on a real repo.
- [ ] Absent-branch (shadowed binary) → clean rc=127, no "command not found".
- [ ] Real-binary happy path returns genuine compact output (daemon/cluster up).
- [ ] Memory note saved.
