---
name: safe-maintenance-crons
description: Use when building recurring self-maintenance/hygiene cron jobs that may mutate state.
---

# Safe Maintenance Crons

## When to use

Use for recurring self-maintenance, health review, or hygiene jobs that are allowed to make **small local improvements** without human approval.

Examples:
- daily Hermes maintenance
- agent self-improvement passes
- local repo or config hygiene scans
- report-and-fix jobs with tight safety bounds

---

### Pitfall: vault-index.md not discovered because missing `tags: [system]`

**Symptom:**  
Health script reports `vault-index.md` as missing even though it exists at vault root. System Files score penalized for "missing required system file".

**Root cause:**  
The discovery function `Get-DiscoveredSystemFiles` only scans for `.md` files at vault root that have `tags: [system]` in frontmatter. Core system files without this tag are invisible to the discovery logic.

**Fix:**  
Add `tags: [system]` to frontmatter of all required system files:
- `vault-index.md`
- `vault-guide.md`
- `STANDARDS.md`
- (Optional: `CONSTITUTION.md`, `AGENTS.md` already have it)

The health script's minimum expected list is:
- `vault-guide.md`
- `CONSTITUTION.md`
- `STANDARDS.md`
- `vault-index.md`
- `AGENTS.md`

---

### Pitfall: domain classification uses directory scan instead of vault-index.md canonical list

**Symptom:**  
Health script scans for domains by listing top-level directories and excluding a hardcoded blocklist (`_Inbox`, `Platforms`, `Types`, `tools`, `maintenance`). This incorrectly includes:
- Reference Areas (`Platforms`, `Types`, `Scripts`) from vault-index.md as domains
- Retired domains like `Social Media` that still have a folder but should be excluded
- Future folders that aren't real domains

**Root cause:**  
The canonical domain list lives in `vault-index.md` under `## Domains` table, not in the filesystem directory structure.

**Fix:**  
Parse `vault-index.md` for the Domains section:
1. Read file, find `## Domains` section
2. Extract domain names from markdown table rows: `| Domain | Root | Wiki | Raw | Status |`
3. Exclude `Social Media` (retired) and table headers/separators
4. Use this list to filter directory scan instead of hardcoded blocklist

This ensures:
- Only currently active domains are checked
- Reference Areas (`Platforms`, `Types`, `Scripts`) are never treated as domains
- Retired domains are cleanly excluded
- New folders don't accidentally become "domains" without index entry

---

### Pitfall: inbox reporting lists full file details instead of count only

**Symptom:**  
Cron messages list every inbox file with path, size, frontmatter status — noisy and not actionable for a daily snapshot.

**User preference:**  
Report only the **count** of inbox files:
- `total_files`
- `content_files` (excluding `ingestion-log.md`)
- `ingested_true` (files already marked ingested but still in `_Inbox`)

Do not list individual files, paths, or frontmatter details unless explicitly asked.

---

### Pitfall: Reference Areas in vault-index.md are not domains

**Symptom:**  
Health script reports domain infrastructure gaps for `Concepts` and `Scripts` because they appear as top-level folders but lack `wiki/index.md` and `wiki/log.md`.

**Root cause:**  
`vault-index.md` explicitly separates **Domains** (active knowledge areas) from **Reference Areas** (Platforms, Types, Scripts). Reference Areas are cross-cutting infrastructure, not ingestion targets.

**Fix:**  
When reading `vault-index.md`, only parse the `## Domains` section. Ignore the `## Reference Areas` section entirely for domain scanning. Reference Areas should have their own health checks if needed, but never be treated as vault domains for ingestion/audit rotation.

---

### Pitfall: core system files missing `tags: [system]` breaks discovery

**Symptom:**  
`vault-index.md`, `vault-guide.md`, `STANDARDS.md` exist but are reported missing by health script.

**Root cause:**  
Discovery scans for `tags: [system]` in frontmatter. These three files lacked the tag.

**Affected files:**  
| File | Tag status | Fix |
|------|------------|-----|
| `vault-index.md` | Missing | Add `tags: [system]` |
| `vault-guide.md` | Missing | Add `tags: [system]` |
| `STANDARDS.md` | Missing | Add `tags: [system]` |

Always verify core system files have `tags: [system]` after any frontmatter edit.

## Core pattern

Split the job into two layers:

1. **Deterministic collector script**
   - Gather local evidence before the LLM runs.
   - Prefer script output over free-form model exploration.
   - Include command exit codes, timeout state, and candidate artifact lists.

2. **Guardrailed LLM cron**
   - Read the script output first.
   - Restrict toolsets to the minimum needed.
   - Use an explicit allowlist and denylist in the cron prompt.
   - Require concise reporting when no safe fix is available.

This reduces hallucinated maintenance, random exploration, and noisy artifact creation.

### Rotating scoped-maintenance pattern

When the system is too large for daily broad cleanup/audit, prefer a rotating scoped cron:
- choose one domain/module/workspace per run from a deterministic sorted list;
- store rotation state outside the maintained corpus under the agent's local state directory;
- run scoped checks for that target only;
- allow only safe deterministic fixes inside the selected scope;
- rerun the same scoped verification after fixes;
- report approval-needed and ambiguous findings instead of broad auto-fixing.

This pattern is especially useful for Robert's vault maintenance: daily per-domain audit/repair is preferred over weekly whole-vault review because it is lighter, focused, and compounds gradually without creating broad-cleanup risk.

## Required guardrails

Every maintenance cron should state these explicitly.

### Allowlist
Only permit actions such as:
- read-only follow-up diagnostics
- low-risk reversible local edits
- class-level skill patches backed by evidence from the run
- durable memory add/replace only for stable facts proven by the run
- self-tightening of the cron's own prompt/script/tool restrictions when fixing a concrete reliability issue
- narrowly-scoped archival moves for old one-off plan files, if the archive rule is explicit

### Denylist
Forbid these by default:
- deleting memory entries
- deleting transcripts, request dumps, state DB content, logs, or state snapshots
- deleting arbitrary files
- auth changes, provider changes, billing actions, package installs, broad update commands, or auto-fix commands like `npm audit fix` / `hermes doctor --fix`
- touching backup repos or mirrored backup paths
- edits to other Hermes profiles unless explicitly requested
- speculative cleanup of `.bak` files
- broad refactors or policy rewrites from a cron run
- creation of new durable notes, plan files, or run-record markdown unless strictly required by a real system change

## Toolset discipline

Prefer the smallest viable toolset.

Typical maintenance job:
- `terminal`
- `file`
- `skills`
- `memory`

Do not grant web/browser/delegation unless the maintenance scope truly needs them.

## Collector script design

The collector script should:
- run deterministic local commands with per-command timeouts
- return structured JSON
- include both stdout/stderr and exit status
- report candidate cleanup targets rather than deleting them
- exclude backup mirrors and self-referential backup paths from cleanup candidate lists
- distinguish between stale plans, stale dumps, stale snapshots, and temp artifacts

If the script times out on a command, capture that as data. Do not fail silently.

## Cleanup policy

The cron may **report** clutter broadly, but unattended cleanup must stay narrow.

Good unattended cleanup:
- move old one-off plan files into a known archive directory under a strict age/use rule

Bad unattended cleanup:
- delete `.bak` files just because they look old
- remove session or cron output history
- wipe state snapshots
- infer that a file is disposable because its name looks temporary

## Pitfalls

### Pitfall: maintenance cron creates its own clutter
A self-improvement cron can accidentally create run-record plan files or durable notes every day. That is anti-maintenance.

Rule: forbid creation of durable notes, plan files, or run-record markdown unless the run made a real change that requires a durable recovery or handoff artifact.

### Pitfall: free-form cron prompt is too open-ended
A vague prompt like "scan the system and improve things" causes scope drift.

Fix: require:
- evidence-first script input
- 0-3 issue cap
- explicit decision rule: fewer, higher-signal changes
- report instead of act when reversibility is unclear

### Pitfall: broad vault/repo audits are too heavy for daily maintenance
A daily cron that tries to audit and fix the whole vault/repo invites long runtimes, noisy reports, broad cleanup pressure, and unsafe cross-domain changes.

Fix: use a **rotating scoped-maintenance pattern**:
- select exactly one domain/component per run from a deterministic sorted list
- store rotation state outside the maintained corpus, e.g. under Hermes local state rather than inside the vault/repo
- run scoped audit/health checks for that domain/component only
- allow only safe deterministic fixes inside the selected scope
- rerun the same scoped verification after fixes
- classify remaining findings as fixed, approval-needed, stale script assumption, acceptable exception, or blocked
- keep whole-system checks limited to lightweight script-health gates, not broad automatic cleanup

### Pitfall: exact-string patching of cron prompts breaks on Unicode variants
`jobs.json` prompt text can contain Unicode dashes/quotes, so raw `patch` replacements fail silently or no-op.

Fix: when updating cron prompts, prefer JSON-structural edits by job `name`, or read the exact saved prompt afterward and compare the changed text before asserting success.

### Pitfall: tool wrapper retry loops after invocation errors
Repeating the same `read_file`/`skill_view`/`web_search` call after a tool invocation mismatch wastes turns.

Fix:
- if the failure came through a wrapper such as `multi_tool_use.parallel`, retry the same operation first as a **single direct tool call** before concluding the underlying tool is unhealthy
- if the direct call still fails, switch to a verified fallback channel (`terminal`, `execute_code`, alternate tool surface), then continue
- do not ask the user to accept skipping the task when a lower-level fallback is still available

This preserves signal: sometimes the wrapper path is what failed, not the underlying read/search capability.

### Pitfall: stale backup skill directories can shadow live skills
Old `.bak` directories left inside the live `skills/` tree can create ambiguous skill-name resolution even when the real skill is healthy.

Fix:
- during a bounded maintenance run, treat old `*.bak` directories under the allowed local cleanup paths as high-signal candidates when they collide with a live skill name
- create a recovery handle first, then remove only the stale backup copy if it is older than the cleanup threshold and not inside excluded backup/session paths
- after cleanup, positively verify that the bare skill name resolves again instead of only confirming the directory is gone

## User-facing output standard

For Robert, maintenance cron output must be short, concrete, and mobile-readable. Use plain day-to-day language.

Structure:
- **bolded job title** followed immediately by a clear success or fail message using 🟢/🟡/🔴 indicator, indicating whether the cron job ran the full intended scope and its dependencies
- cover: what ran, what changed/fixed, any bugs found, anything Robert should know
- light emojis only for scanability: 🐛 bug, 🔧 fix, 🚫 denied, ⚠️ attention, 👉 next steps, ✅ approved/result
- 3-6 bullet points max after the status line
- separate text with a new line when the context changes (for example, `problems` and `fix` should be on separate lines)
- use a separator line (`---`) between sections with different context
- use a separator line (`---`) before the `To stop or manage this job` section at the bottom of the response
- no filler, no senior-engineer narration

Required sections in order:
1. **What ran** — bullet list of actual work
2. **Results** — only what produced output/changed state
3. **Dependency notes** — only if wrapper reports missing scripts or broken paths
4. **Problems** — any bugs/errors from stderr or unexpected exit codes
5. **Fix** — concrete next action if problems found
6. **Next steps** — one line with 👉

## Collector script pattern for Windows + agent-mode cron

On this Windows Hermes host, `cronjob` requires `script` to be relative to `~/.hermes/scripts/`, not an absolute Windows path. Use one wrapper script per cron target under `~/.hermes/scripts/vault_cron_wrappers/` that:
- calls the deterministic collector script directly via `pwsh -File` or a hidden-window `ProcessStartInfo` wrapper
- wraps stdout in simple markers if needed for the agent relay
- preserves the collector's exit code

## PowerShell collection pitfalls

See `references/powershell-cron-wrapper-patterns.md` for the complete Python launcher + PowerShell wrapper template, including the critical **escaped-quote rule for multi-word domain arguments** (`-Domain '"Agent Skills"'`).

### Pitfall: giving the user a Bash one-liner without verifying the live shell

In Hermes-on-Windows sessions, do **not** assume the user's visible terminal surface matches the agent terminal backend. A session can have Bash available to the agent while the user is actively looking at or pasting into PowerShell.

Fix:
- when the task is to change or verify a cron, prefer executing it yourself through Hermes tools instead of telling the user to paste a command
- if you must hand the user a command, verify the target shell first from live evidence (terminal output, screenshot, or explicit user statement) and write for that shell only
- do not provide Bash line continuations, quoting rules, or pipelines to a PowerShell surface
- after any shell-targeted instruction, positively verify the result instead of assuming the paste worked

Rule: for cron/gateway maintenance, `execute yourself > ask user to paste`; and when user execution is unavoidable, `verify shell first, then give one-shell-specific syntax`

When scanning files and building output arrays in PowerShell, do NOT use:
- `@(Get-ChildItem ... | ForEach-Object { [pscustomobject]@{ ... } })`
with collection types that are predeclared as fixed arrays. This triggers:
`Exception calling "Add" with "1 argument(s): "Collection was of a fixed size."`

Safe pattern:
```powershell
$items = New-Object System.Collections.Generic.List[pscustomobject]
foreach ($item in Get-ChildItem ...) {
    [void]$items.Add([pscustomobject]@{ ... })
}
[pscustomobject]@{ items = @($items) }
```

Rule: once a variable is created as a fixed-size collection, switch to `New-Object System.Collections.Generic.List[T]` and explicit `Add()` before appending inside loops.

## Pitfall: cron delivery failure gets misdiagnosed as job failure
A maintenance cron can complete successfully while the notification layer fails afterward. Treating that as a prompt or script problem leads to bad edits.

Fix:
- inspect the latest cron output artifact first to confirm whether the job itself completed
- only then inspect gateway logs for delivery-path evidence such as `delivery error: Telegram send failed`, repeated `[Telegram] Connect attempt` retries, `Timed out`, `getaddrinfo failed`, or `All connection attempts failed`
- if the artifact exists and the job completed, leave the cron logic unchanged and classify the incident as delivery/gateway degradation unless stronger evidence says otherwise
- if a cleanup candidate from the injected scan is already gone on live check, report it as already resolved rather than stale pending work

### Pitfall: self-improvement prompt scope creep
Adding self-improvement sections to maintenance prompts can accidentally expand cron safety boundaries.

Fix: keep these sections explicitly bounded:
- proposals: 0-3 items, concrete, low-risk, reversible, already within current allow/deny lists
- audit: read-only observations only, no mutations
- test-time eval: propose one variant and record it only; do not mutate during the same run

Do not turn maintenance into a planning assistant. The daily run remains fix-first, report-when-uncertain.

### Pitfall: Telegram cron messages read like ops reports instead of useful updates
A cron can be technically correct but still hard to read on mobile if it sounds like a senior engineer writing for other engineers.

Fix:
- write like a technically capable friend giving a quick useful update
- use light emojis only to improve scanability, not for decoration overload
- prefer short headings such as `🛠 What I changed`, `🙅 What I left alone`, `➡️ What I'd do next`
- explain what happened in simple day-to-day language first; only use deeper jargon when it materially changes meaning
- for cleanup/backup relays, transform raw script output into a short Telegram-shaped summary instead of dumping verbatim text when the prompt allows it
- use one bold main status line and short italic labels like `*Time:*` when timestamps matter
- do not rely on underline formatting for Telegram delivery

### Pitfall: backup relay jobs only send the final status
If a backup script hangs or dies mid-run, a single completion message leaves the human unsure whether the job started at all.

Fix:
- send a start notification immediately before launching the backup or sync script
- capture stdout/stderr and exit code from the script
- compute a fresh completion timestamp after the script returns
- on success, send a short outcome summary instead of logs
- on failure, include the useful script output directly in the failure message
- clean up any one-off plan artifact created only to coordinate the run
- if the extra start/success/failure messages target the same Telegram chat as the cron's final delivery target, use a direct Bot API send for those extra messages instead of relying on same-target `send_message` delivery
- when reading `TELEGRAM_BOT_TOKEN` from `.env` inside inline Python or shell helpers, compare the env key name and then split on `=`; do not match the full `KEY=value` literal because secret redaction or masking can break the script text

### Pitfall: backup mirrors pollute cleanup candidates
If a system contains backup mirrors, naive recursive scans double-count artifacts and tempt bad deletions.

Fix: explicitly exclude backup repo paths like `hermes-backup` and backup directories from collector candidate lists.

### Pitfall: broad recursive artifact scans can exceed cron script timeouts
A collector that does `Path.rglob()` across the whole Hermes home for temp files can spend most of the 120s pre-run budget inside backup mirrors, profile backups, `node_modules`, virtualenvs, or other irrelevant subtrees. The script may work manually with a long timeout but still fail as a cron pre-run script.

Fix:
- replace broad `rglob()` cleanup scans with a pruned walker (`os.walk` with `dirs[:]` filtering) or a small allowlist of maintenance paths
- exclude `.backups`, `backups`, `hermes-backup`, `node_modules`, `.git`, `.venv`, `venv`, and `__pycache__`
- measure total collector runtime under the actual cron script timeout, not only per-subcommand timeouts
- leave cross-profile backup files alone unless the user explicitly approved that profile scope

### Pitfall: no_agent script delivery produces empty output on Windows
On this Windows Hermes host, a `no_agent=true` cron with a Python script under `~/.hermes/scripts/` produced a 'silent (empty output)' run artifact despite the same script printing normally when run directly. The scheduler's stdout capture appears to lose output in this configuration.

Fix: prefer **agent-mode relay** for delivery-sensitive cron jobs on Windows — have the script run as the pre-run `script` (injecting stdout into the agent prompt), then use a minimal agent prompt that echoes the injected output verbatim. Only use `no_agent=true` for watchdog-style silent jobs where empty output is the expected "healthy" signal.

### Pitfall: PowerShell collector wrapper loses command context on Windows re-entry
A terminal command that shells through `pwsh.exe > tool layer > skill_manage` can be parsed as if the boundary collapsed in `pwsh -Command`, returning nothing or acting on one wrapper layer while the agent assumes a later boundary worked. Treat any artifact produced from inline `-Command '...'` re-entry as lower-fidelity than direct script execution. Verify through the original script path, not through the quoted wrapper that got re-parsed on re-entry.

Fix:
- prefer scripted verification paths over inline command wrappers
- when a scripted verification path does not clearly produce a matching artifact, do not mark the wrapper stage as success
A direct `send_message` to Telegram can succeed while the cron executor path is failing — and the reverse can also happen. Do not assume transport health tells you whether scheduled jobs are actually running.

Fix:
- treat transport verification and cron-executor verification as separate checks
- after any manual cron trigger, verify all three: a new `last_run_at`, a new output file under `cron/output/<job_id>/`, and updated delivery status
- if `cronjob run` returns success but none of those three move, do **not** claim the cron ran; diagnose the scheduler/executor path instead
- when demonstrating end-to-end behavior for a user, you may send the would-be report manually to Telegram, but label it clearly as a manual relay rather than a cron-run success

### Pitfall: patching scheduler code before reproducing the failure on a minimal smoke job
A stale incident report or partial evidence can make the scheduler look broken when the current executor path is actually healthy again.

Fix:
- before editing cron scheduler code, create a minimal one-shot local smoke job with a tiny deterministic script that prints one line
- trigger it with `cronjob(action='run', ...)` or the CLI equivalent, then run a tick if needed
- require positive evidence: a fresh output artifact under `cron/output/<job_id>/` and, when the job remains listed, an updated `last_run_at`
- if the smoke job produces the artifact, stop chasing a stale scheduler premise and move to the real remaining problem (message shape, delivery target, prompt wording, or specific job logic)
- clean up the smoke script, output directory, and one-off plan once verification is complete

### Pitfall: Telegram formatting requests get implemented only in chat, not in the actual cron prompts
A user can approve a better cron message style, but if you only mirror that style in the current conversation, the next scheduled run still emits the old format.

Fix:
- apply formatting changes at the cron prompt/job definition layer so future scheduled runs inherit them automatically
- prefer Telegram-safe markdown: `**bold**` section labels and short `*italic*` qualifiers
- do **not** rely on underline formatting for this transport; if the user asks for it, implement the strongest reliable formatting instead and say so plainly
- verify the new format with a local formatting smoke job or by inspecting the next output artifact before claiming the change is live
- normalize every recurring Telegram report to the canonical schema in `references/cron-report-schema.md`

### Pitfall: transport health gets answered while report schema remains undefined

A user can ask two different cron questions back-to-back: **is delivery working?** and **what is the message schema?** If you answer the first one and keep free-form explaining the second, the user experiences this as noise: communication is open, but the report is still illegible.

Fix:
- separate **delivery-path verification** from **message-shape normalization**
- when the user asks to normalize a delivered report, stop discussing transport unless transport is actually broken
- define a concrete report schema and apply it at the cron prompt/job layer, not only in chat
- keep the delivered message in one mobile-readable shape: status line -> one-sentence summary -> findings bullets -> single action block when needed
- if the user says `what are you suggesting`, answer with one recommended action sentence first, then supporting detail only if needed
- empty sections are forbidden; omit headings like `Dependency notes` or `Fix` when they add no signal

### Pitfall: documentation-drift cron heuristics confuse internal code changes with user-facing doc changes
A repo-monitoring cron can look at broad files like `hermes_cli/main.py`, `hermes_cli/config.py`, or `tools/*.py` and over-report "docs drift" even when the PR only changed internal control flow, startup wiring, or process-env plumbing. That produces noisy alerts and teaches the user to ignore the report.

Fix:
- trigger drift findings only for **user-facing surface changes**, not for broad file touches alone
- CLI docs drift requires a change to syntax, flags, help text, subcommand semantics, or other documented invocation behavior — not just internal logic inside `main.py`
- env-var docs drift requires a user-facing env var add/remove/rename/deprecation or a material change to the meaning/precedence of a documented variable — not internal guard vars or subprocess safe-env plumbing
- config docs drift requires a real change to a documented option's key, values, default, or meaning
- before reporting a gap, require one short quoted proof point from the diff that demonstrates the user-facing contract changed
- suppress uncertain cases; for drift-detection jobs, false positives are worse than misses
- after the first noisy run, patch the cron prompt immediately with explicit calibration examples instead of letting the bad heuristic repeat next week
- see `references/doc-drift-calibration.md` for a concrete calibration pattern and real examples

### Pitfall: output truncation in long-form LLM cleanup prompts
The original cleanup cron used a massive prompt with ~50 explicit `rm -rf` commands. When the LLM executed them, the combined stdout exceeded the response length limit and failed with `RuntimeError: Response truncated due to output length limit`.

Fix: move the deletion logic into a deterministic Python script that internally enforces a max-deletion quota and emits a concise summary. The cron then just relays that summary — no token budget exhausted.

## Verification

After creating or updating the cron:
1. verify the job definition exists and has the intended name, script, toolsets, and `deliver=origin`
2. if the job depends on a local script, run that script directly first and require a clean local exit before leaving the job enabled
3. for monitoring/alerting jobs, inspect the script for placeholder targets like `example.com`, dummy ports, or sample hostnames; if placeholders remain, pause the job instead of allowing noisy false alerts
4. trigger a manual run
5. verify `last_run_at`, `last_status`, and output artifact/log
6. inspect the first run for accidental artifact creation or alert spam risk
7. tighten the prompt immediately if the first run created clutter, attempted out-of-bounds actions, or would have produced false positives

### Pitfall: backup relays and daily maintenance crons drift from the approved output format
A user can approve a better cron message style, but if the style is only mirrored in the current conversation, the next scheduled run still emits the old format.

Fix:
- apply formatting changes at the cron prompt/job definition layer (`cronjob action=update`) so future scheduled runs inherit them automatically
- prefer Telegram-safe markdown: `**bold**` section labels and short `*italic*` qualifiers
- do **not** rely on underline formatting for this transport; if the user asks for it, implement the strongest reliable formatting instead and say so plainly
- verify the new format with a manual cron run (`cronjob action=run`) and inspect the next output artifact before claiming the change is live

### Pitfall: vault maintenance cron collapsing system/inbox/skills into a single job

Daily vault maintenance cron design benefits from explicit separation:
- dedicated domain jobs for larger domains (`Agent Skills`, `AI Sphere`, `Hermes`)
- one combined rotating job for smaller domains (`Academia`, `Finance`)
- one system readiness job with bounded PowerShell vault-script folder health plus source-of-truth existence checks
- one inbox job that is **frontmatter-only preparation**, never ingestion
- one vault-skills health job to confirm skill metadata/references and stale retired-workflow references

Each report should stay short, factual, Telegram-friendly, and scoped to that job. All jobs should use the same output format standard defined above.

### Pitfall: creating the cron before proving the checker script is runnable
A scheduler job can be created successfully while the underlying script is still syntactically broken or still pointed at placeholder endpoints. That produces either a dead job or recurring false outage noise.

Fix:
- create the job if needed, but do not consider it live yet
- run the script directly with the local interpreter and require exit code 0
- if the script fails syntax/runtime checks, patch it immediately and re-run
- if it still targets sample hosts like `api.example.com` or `docs.example.com`, pause the cron until real endpoints are supplied
- only leave the job enabled once the direct script run proves the alert logic is meaningful

## Inspecting existing cron runs

## Inspector pattern

Use this when the task is to explain an existing cron or verify it after edits.
1. `cronjob action=list` to identify the job.
2. Read its latest output artifact under `C:\Users\Tiger\AppData\Local\hermes\cron\output\<job_id>\`.
3. Read the current prompt directly only to resolve specific wording questions.
4. Before claiming success, inspect the same artifacts again.

## Key Files

- `C:/Users/Tiger/AppData/Local/hermes/cron/jobs.json` — cron job definitions
- `C:/Users/Tiger/AppData/Local/hermes/scripts/hermes_self_improvement_scan.py` — pre-run health scan
- `C:/Users/Tiger/AppData/Local/hermes/scripts/hermes-cleanup-daily.py` — deterministic cleanup relay
- `C:/Users/Tiger/AppData/Local/hermes/.hermes/plans/` — durable plans and archives
- `C:/Users/Tiger/.hermes/plans/archive/` — archive destination for completed plan files
- `C:/Users/Tiger/AppData/Local/hermes/.hermes/plans/operator-fallback-ladders.md` — documented tool/provider recovery ladders

## Reference

See `references/maintenance-prompts.md` for prompt wording examples.
See `references/cleanup-patterns.md` for deterministic cleanup design notes.
See `references/delivery-routing.md` for Telegram target normalization and chat-id conventions.
See `references/cron-smoke-and-formatting.md` for one-shot executor verification and Telegram formatting smoke-test patterns.
See `references/backup-relay-pattern.md` for start/finish notification structure around deterministic backup scripts.
---

### Pitfall: PowerShell cron wrapper executed as Python script on Windows

**Symptom:**  
`SyntaxError: invalid syntax at line 2 ($ErrorActionPreference = 'SilentlyContinue')` — the cron executor ran the `.ps1` file as a Python script.

**Root cause:**  
On this Windows Hermes host, `cronjob` requires `script` relative to `~/.hermes/scripts/`, but it executes the file with the Python interpreter regardless of extension.

**Fix:**  
- Create a thin Python launcher (e.g. `vault_cron_agent_skills.py`) that invokes `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <wrapper.ps1>`  
- Use `encoding='utf-8', errors='replace'` in the Python `subprocess.run` so non-UTF-8 bytes from PowerShell output don't crash the reader thread  
- Point the cron `script` field at the `.py` launcher, not the raw `.ps1`  

**Reference:** `references/powershell-cron-wrapper-patterns.md` for full launcher/wrapper templates.

---

### Pitfall: multi-word domain arguments split by `-join ' '` in PowerShell wrapper

**Symptom:**  
Collector throws `Domain mismatch: AI is not an auditable current domain` even though the wrapper passes `-Domain AI Sphere`.

**Root cause:**  
`-join ' '` concatenates the argument array with spaces, turning `-Domain AI Sphere` into two separate positional args.

**Fix:**  
Quote multi-word string args in the wrapper's argument array:  
`-Domain '"AI Sphere"'` (not `-Domain 'AI Sphere'`)

**Affected parameters:** `-Domain`, `-GroupName`, `-StatePath`, any user-supplied string that may contain spaces.  

See `references/powershell-cron-wrapper-patterns.md` for the exact pattern.
