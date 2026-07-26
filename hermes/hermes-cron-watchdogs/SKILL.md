---
name: hermes-cron-watchdogs
description: Build, repair, and verify Hermes cron jobs backed by local scripts, especially silent-on-healthy watchdogs and dependency monitors.
---

# Hermes Cron Watchdogs

## When to use
- Creating or repairing a Hermes cron job that runs a local script.
- Building uptime/dependency monitors that should stay quiet when healthy and alert only on actionable failures.
- Verifying whether a Hermes cron actually fires, delivers, and records output end-to-end.

## PowerShell wrapper argv rule
When a PowerShell `ProcessStartInfo.Arguments` string contains a value with spaces (e.g. `-Domain 'Agent Skills'`), **quote the individual arg value** so it survives the `-join ' '` concatenation intact. Use escaped quotes: `'\"Agent Skills\"'`.

**Pitfall: ArgumentList is read-only in .NET Core / PowerShell 7**
`ProcessStartInfo.ArgumentList` returns a mutable-looking list but is read-only — `New-Object ...List[string]` assignment fails with `'ArgumentList' is a ReadOnly property`, and calling `.Add()` on the existing instance throws `You cannot call a method on a null-valued expression`. Do not use `ArgumentList`.

**Working pattern (Arguments string with quoted values):**
```powershell
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $ps7
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WindowStyle = 'Hidden'

$argList = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', $collector,
    '-VaultRoot', 'C:\Users\Tiger\Vault',
    '-Domain', '"Agent Skills"',     # escaped quotes around spaced value
    '-GroupName', '"Agent Skills"'
)
$psi.Arguments = $argList -join ' '

$p = [System.Diagnostics.Process]::Start($psi)
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()
$exitCode = $p.ExitCode

if ($stdout) { $stdout }
elseif ($stderr) { $stderr }
exit $exitCode
```

The `Arguments` string approach works reliably across all PS/.NET versions on this Windows host.

## cronjob tool update caveat
`cronjob action='update'` with no mutation payload can return success while leaving the job unchanged. After an update that should change config, verify by rereading the job/config source of truth instead of assuming the change persisted.

## Source-of-truth rule for cron model/provider changes
When deciding whether to repin or migrate a cron job's model/provider, do **not** trust a single `cronjob list` echo or a stale `last_status` at face value.

**Required checks before any model/provider migration:**
1. Inspect the latest output artifact timestamp for the target `job_id` under `~/.hermes/cron/output/<job_id>/`.
2. Read the newest artifact and classify the failure:
   - **model/provider issue**: auth failure, spend-guard/provider drift, unsupported route, quota/provider-specific rejection.
   - **environment/update-window issue**: missing CA bundle during update, transient file-not-found while the app/venv is being replaced, stale scheduler process, delivery package missing, script path mismatch.
3. Verify the persisted cron config source of truth (on this host, `cron/jobs.json`) rather than trusting the API echo alone.
4. Only migrate the model/provider if the failure is actually model/provider-related.

**Rule:** stale error statuses from an earlier update window are not evidence that a different model is better. Fix or ignore the stale env churn first, then evaluate model fit.

**Practical implication:**
- If `jobs.json` shows the intended provider/model but `cronjob list` echoes an older value, treat the list response as cached/stale until disproved.
- If multiple recent runs on the same provider are `ok`, do not migrate sibling jobs just for consistency.

## Stagger watchdogs away from planned maintenance windows
If a watchdog monitors a service that is intentionally restarted by a known scheduler event (desktop self-update, image migration, profile restart, backup drain window), do not leave the watchdog exactly on the same cadence boundary.

**Pattern:** move the watchdog a few minutes off the maintenance tick instead of piling on grace-period logic alone.
- Example: if maintenance commonly hits at `:00/:15/:30/:45`, run the watchdog at `:07/:22/:37/:52`.
- Keep the script's grace window, but treat schedule staggering as the first line of defense against false alerts.

**Why:** a watchdog that wakes on the same minute as the planned restart can report a healthy maintenance event as an outage, even when the script itself is correct.

**Verification:** after `cronjob action='update'`, re-list the job and confirm `schedule`, `next_run_at`, and `last_status` reflect the intended offset.

## Core rules
1. **Prefer real dependency checks over placeholder URLs.** Do not monitor docs pages, fake `/health` endpoints, or provider homepages unless the user explicitly says those surfaces are business-critical.
2. **Use the cheapest auth-sensitive smoke check that proves the real integration path works.** For provider APIs, prefer a low-cost authenticated list/status/usage endpoint over a generation call.
3. **Data-collection scripts exit 0 when collection succeeds, even if findings are bad.** Vulnerabilities, failed checks, drift, or degraded dependencies are report payload, not script failure. Reserve non-zero exits for collector/runtime failures (missing binary, parse crash, missing project path) or the scheduler will mark the cron failed before the agent can act.
4. **Healthy runs should be silent.** Design the script to emit a deterministic healthy marker like `NO_ISSUES`, then map that to `[SILENT]` in the cron prompt so Telegram stays quiet.
5. **Verify the cron path, not just the script path.** A local `python script.py` success is necessary but insufficient.
6. **Use local CLI probes when they test the real configured integration.** For Hermes-local services, `hermes cron status` or `hermes honcho status` can be stronger than a guessed raw endpoint.
7. **If the agent can perform the cron repair itself, do that instead of asking the user to paste commands.** Only hand off a command when the environment is truly inaccessible from tools.
8. **When the user asks what a cron job does, explain the job behavior before the implementation.** Lead with: when it runs, what it checks/cleans/sends, and what happens when something is wrong. Keep it non-technical unless the user asks for internals.

## Windows Hermes host pitfall
When creating Hermes cron jobs whose scripts live under `~/.hermes/scripts`, pass the script as the scheduler-relative name (example: `--script <name>.py`) instead of a literal `~/.hermes/scripts/<name>.py` path. The scheduler resolves scripts from its scripts directory; the relative form is the reliable one to preserve first.

> ⚠️ `check-uptime.py` was retired and moved to `hermes/scripts/.trash/` (2026-07-26); the example above uses a placeholder, not a live script.

## User-visible shell mismatch pitfall
On this Windows setup, **the agent's `terminal` tool may run through bash while the user's visible terminal pane is PowerShell**. Do not assume they are the same shell.

**Rules:**
1. Before telling the user to paste a command, verify which shell the user is actually looking at.
2. If the user is in PowerShell, give PowerShell-compatible syntax — not bash continuations, quoting, or here-doc patterns.
3. For routine cron inspection, repair, update, or forced-run work, prefer doing it yourself with tools instead of handing the user a one-liner.
4. If you must give a manual command, make it a single-line command in the correct shell and say which shell it is for.

**Pitfall:** A technically correct bash command is still wrong if the user is staring at a PowerShell prompt. In this situation, shell verification is part of task verification.

## Backup cron timeout pattern
For backup/sync cron jobs that time out under the scheduler but succeed manually or partially, instrument each expensive phase before changing the cron timeout. Measure copy/sync, staging, status, commit, push, and any compression/network step separately. In Git-backed backups, a large volatile diff often makes `git add`/`commit`/`push` exceed the script budget even when the file copy is fast. Fix the backup scope first: exclude runtime caches, logs, generated cron output, screenshots/audio cache, LSP/node_modules/bin trees, local repository checkouts, profile-retirement backups, lock/pid files, and database WAL/SHM files unless the user explicitly needs them preserved. Clean previously copied excluded directories from the destination repo before the next mirror, because mirror tools may not remove directories after they become excluded. Set `GIT_TERMINAL_PROMPT=0` for unattended git operations so credential prompts fail instead of hanging. See `references/git-backed-hermes-backup-timeouts.md` for the concrete diagnostic pattern.

## Backup cron reporting contract
For backup jobs that use tools with non-standard success codes (especially `robocopy` on Windows), make the script emit an explicit classification line instead of forcing the agent to infer health from a raw return code. Example pattern: `Robocopy classification: acceptable rc=3 (...)` for success-class exit codes and `failure rc=<n>` for real copy failures. Then align the cron prompt to treat the explicit `acceptable rc=...` marker as healthy.

Also emit positive verification evidence in the script output itself:
- `git status` entry count and representative changed paths
- commit SHA after a successful commit/push
- an explicit final line like `Backup status: OK`

This prevents false `DEGRADED` reports when the script itself succeeded but the agent overreacts to an acceptable non-zero code or to missing evidence.

## Recommended workflow
1. Inspect the existing job state first (`cronjob list`) and note whether the job is paused, the current `job_id`, and the last run status.
2. Inspect the backing script before changing the job.
3. Replace placeholder checks with real local or provider dependency probes.
4. For provider checks, choose low-cost authenticated endpoints that return stable structured data.
5. Run the script directly and fix runtime or false-positive issues first.
6. Resume the cron only after a clean local script run.
7. Force a run (`cronjob action=run`) when you need immediate verification.
8. Confirm an output artifact was written under `~/.hermes/cron/output/<job_id>/...`.
9. Read the artifact and verify both the injected script output and the final cron response (for healthy watchdogs, expect `[SILENT]`).
10. Re-check `cronjob list` and confirm `last_run_at`, `last_status`, and `next_run_at` advanced as expected.

## Trigger-now + explain contract
When the user says some version of **"trigger it now and explain its workflow"**, treat that as a two-part ownership task, not a fire-and-forget run.

**Required sequence:**
1. trigger the target job
2. inspect the newest output artifact for that exact `job_id`
3. inspect the live job config / prompt contract
4. explain the operating loop (`when it runs -> what inputs it reads -> what artifacts it writes -> where delivery goes`)
5. if the forced run failed, explain the failure mode and the broken contract in the same pass

**RULES:**
- Do not stop at `the cron failed` or paste back the failure notice.
- If the prompt says `use injected script output`, verify that the job actually has a non-null `script` configured.
- If the prompt expects structured payloads, verify the payload shape matches the formatter's expectation before trusting the report.
- When config and prompt disagree, explain the mismatch directly: `this job now expects script-injected data, but no script is attached`, or equivalent.
- If the job used to work and now fails after a prompt/config rewrite, treat the rewrite mismatch as the primary diagnosis until disproved.

**Pitfall:** A user-facing failure notification without diagnosis is not a complete cron-support response. Close the loop by identifying why the job failed and what would restore normal behavior.

## Windows desktop cron stdout pitfall
On Windows desktop Hermes, a no-agent cron script can **write its normal artifact files successfully while the scheduler still logs `empty stdout — silent run`**. A durable cause is the cron runner invoking Python scripts through `sys.executable` when the long-lived app process is effectively on `pythonw.exe`, which can swallow captured stdout semantics for watchdog-style jobs.

**Repair pattern:**
1. Verify the script output exists independently (for example, the script's own archive/output file updates with fresh timestamps and non-empty content).
2. Inspect the scheduler implementation in `hermes-agent/cron/scheduler.py`.
3. On Windows, make the Python-script branch prefer `python.exe` when `sys.executable` resolves to `pythonw.exe`:
   ```python
   py_exec = sys.executable
   if sys.platform == "win32":
       py_path = Path(py_exec)
       if py_path.name.lower() == "pythonw.exe":
           python_console = py_path.with_name("python.exe")
           if python_console.exists():
               py_exec = str(python_console)
   argv = [py_exec, str(path)]
   ```
4. Re-run the job from a **fresh Hermes CLI process** (`hermes cron run <job_id>`) or restart the gateway/scheduler process. Do not trust forced runs issued from the already-running chat process after patching the source file; that process may still have the old imported scheduler code.
5. Only after the fresh-process run, trust the delivery log line and `last_status`.

**Verification contract:**
- If `cron_stdout_latest.txt` (or equivalent script-owned artifact) contains a full fresh report but `agent.log` still says `empty stdout — silent run`, the script is not the problem; the live scheduler process is stale or using the wrong interpreter path.
- The decisive proof is a fresh-process log line like:
  `cron.scheduler: Job '<job_id>': delivered to discord:<channel_id>`

See `references/windows-cron-pythonw-stdout.md` for the exact symptom chain and repair sequence.

## Verification checklist
- Direct script execution returns the intended healthy or unhealthy marker.
- Cron output artifact exists for the target `job_id`.
- Artifact content matches the intended contract between script output and prompt behavior.
- `cronjob list` shows `last_status: ok` after the forced run.
- If the watchdog is meant to stay quiet when healthy, the artifact should show `[SILENT]` as the final response.
- On Windows desktop Hermes, if you patched cron runner code, verify using a **fresh Hermes process** (`hermes cron run ...`) or after a gateway restart — not only from the already-running chat process.

## Pitfalls
- Do not leave placeholder endpoints in a recurring monitor; they create guaranteed noise.
- Do not claim a cron works just because the job was created successfully.
- If a cron prompt says to use injected script output, verify the job has a non-null `script` field and the CLI lists the expected script; otherwise the agent will have no injected evidence and may report stale or inferred status.
- Do not use expensive generation endpoints for heartbeat checks when a models/list/usage endpoint is available.
- Do not add every possible provider; alerting should follow the user’s real dependency path, not theoretical integrations.

### Pitfall: declaring cron health from `hermes doctor` alone
A Hermes self-maintenance pass can look healthy after `hermes doctor` or `hermes doctor --fix`, while scheduled jobs still cannot fire because the profile gateway/scheduler is down.

**Fix:** after any doctor-based repair on a profile that owns cron jobs, verify the scheduler path separately:
1. run `hermes cron list` and note whether jobs are active and whether the CLI warns that the gateway is not running
2. run `hermes gateway status` for the same profile
3. if the profile is supposed to execute scheduled jobs and no gateway process is detected, start it and re-check status before claiming cron health
4. only then summarize remaining issues from `hermes doctor`

**Rule:** `doctor health` and `cron execution health` are separate checks. A migrated config is not proof that scheduled automation is live.

## Support files
- `references/uptime-monitor-endpoints.md` — example endpoint choices, prompt contract, and verification pattern from a real Hermes uptime monitor session.
- `references/powershell-wrapper-quoting.md` — complete working pattern for quoting multi-word domain arguments in Windows PowerShell cron wrappers (`-Domain '"Agent Skills"'`), including the .NET Core `ArgumentList` read-only pitfall.
