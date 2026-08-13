---
name: gbrain-sync-git-retry-patch
description: "Use when doctor reports sync_failures: N (UNKNOWN) with git HEAD verification failed: spawnSync git ETIMEDOUT"
---

# gbrain sync — git spawnSync timeout retry patch

## Problem (root cause)
On Windows (MSYS/git-bash), cold `git` spawns (DLL load, AV scan, parallel
sync workers) intermittently exceed the 30s `execFileSync` timeout even for
trivial calls like `rev-parse HEAD` (≈0.1s warm). The timeout throws inside
`sync.ts`'s `git()` helper, which is used by the post-sync HEAD-verification
gate (`sync.ts` ~line 2681, `git(repoPath, ['rev-parse','HEAD'])`).

When that one call times out, gbrain records a `<head>` sentinel failure in
`~/.gbrain/sync-failures.jsonl`:
```
git HEAD verification failed: spawnSync git ETIMEDOUT
```
The `<head>` sentinel is a **hard-block**: even `gbrain sync --skip-failed`
will NOT clear it (by design, `sync.ts` ~line 2713). So a single flaky
timeout wedges the source until the ledger entry is manually acknowledged.

This is environmental, NOT a content error. `git rev-parse HEAD` runs in
~0.1s when warm.

## Fix
Patch the `git()` helper in `src/commands/sync.ts` to **retry up to 2× with
backoff** on `ETIMEDOUT`/`SIGTERM`, keeping the 30s per-call cap so genuine
hangs still surface.

gbrain is a Bun script (`exec bun src/cli.ts`) — Bun transpiles TS on the fly,
so **no build step** is needed. The patch takes effect on the next `gbrain`
invocation.

## Detection (run this first)
```
gbrain doctor --fast 2>&1 | grep -i "sync_failures"
grep '"path":"<head>"' ~/.gbrain/sync-failures.jsonl
```
Symptom: `sync_failures: N (UNKNOWN)` and a `<head>` entry with
`spawnSync git ETIMEDOUT`.

## Apply the patch
Locate the `git()` helper. It looks like (pre-patch):
```ts
function git(repoPath: string, args: string[], configs: string[] = []): string {
  return execFileSync('git', buildGitInvocation(repoPath, args, configs), {
    encoding: 'utf-8',
    timeout: 30000,
    maxBuffer: 100 * 1024 * 1024,
  }).trim();
}
```
Replace the whole function body with the patched version in
`references/patched-git-helper.ts`. Use the Hermes `patch` tool in `replace`
mode, matching on the exact pre-patch block above. See
`references/apply.patch` for a V4A patch if preferred.

## Verify (positive proof)
Run a sync on the affected source and watch the log:
```
gbrain sync --source <source_id> --no-embed 2>&1 | tail -15
```
Expected on success (flake hit, retry saved it):
```
[git retry 1/2] rev-parse HEAD in <repo> timed out; retrying in 500ms
Text imported. Run 'gbrain embed --stale' to generate embeddings.
Synced <sha>..<sha>: +N added, ~M modified, -K deleted
EXIT=0
```
Then confirm NO new `<head>` entry was recorded:
```
gbrain doctor --fast 2>&1 | grep -i sync_failures   # should read OK / acknowledged
```

## Clearing the stale <head> ledger entries (post-patch)
Because `--skip-failed` cannot clear `<head>` sentinels, mark them
`acknowledged` directly in the JSONL ledger (do NOT delete — preserve audit
trail). Use `references/acknowledge_head_failures.py`:
```
python3 <skill_dir>/references/acknowledge_head_failures.py
```
It flips only `path=="<head>" && code=="UNKNOWN" && ETIMEDOUT && state=="open"`
entries to `acknowledged` with a reason, leaving everything else untouched.

## Durability — CRITICAL
The patch lives in **local gbrain source** (`$GBRAIN_SRC/src/commands/sync.ts`).
`gbrain upgrade` overwrites `src/`, silently reverting the fix. After ANY
upgrade:
1. Re-detect (doctor / grep the ledger).
2. If `<head>` timeouts return → re-apply this skill.
3. The in-comment version stamp `v0.42.57.1 (local patch)` is how you tell
   whether the current source already has the patch:
   ```
   grep -c "v0.42.57.1 (local patch)" "$GBRAIN_SRC/src/commands/sync.ts"
   ```
   `1` = patched, `0` = re-apply needed.

## Pitfalls
- Do NOT lower the 30s timeout to "fix" this — real hangs must still surface.
- Do NOT delete `<head>` ledger entries; acknowledge them so the audit trail
  survives and a future real history-rewrite block is still visible.
- `git pull failed` warnings during sync are EXPECTED if you deliberately
  don't push/pull third-party upstreams (e.g. a forked `garrytan/gstack`).
  That is not the flake — the flake is the `<head>` spawnSync timeout.
