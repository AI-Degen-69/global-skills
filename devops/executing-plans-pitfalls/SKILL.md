---
name: executing-plans-pitfalls
description: Use when studying PowerShell plan-execution pitfalls and patterns.
category: software-development
tags: [powershell, cron, vault, pitfalls, patterns]
---

# PowerShell Plan Execution Pitfalls

Use when executing implementation plans that refactor PowerShell scripts or shared helper modules.

## Import-safe helper scripts

When a helper `.ps1` both defines functions and supports direct CLI execution, guard the executable footer so dot-sourcing does not emit output or run side effects:

```powershell
if ($MyInvocation.InvocationName -ne ".") {
    $result = Test-SomeHealth
    if ($Json) { $result | ConvertTo-Json -Depth 6 }
    else { "Human summary..." }
}
```

Verification pattern:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -Command ". 'C:\path\to\Helper.ps1'; if (Get-Command Test-SomeHealth -ErrorAction SilentlyContinue) { 'dot-source-ok' }"
```

## Dot-sourcing inside functions

Dot-sourcing a helper inside a function loads functions into that function's scope. Do not assume the imported function will exist later in the caller/script scope. Either:

1. dot-source the helper at script scope before any function uses it, or
2. call the imported helper from inside the same wrapper function that dot-sourced it.

Safe wrapper pattern:

```powershell
function Get-HealthFromHelper {
    $helperPath = Join-Path $PSScriptRoot "Helper.ps1"
    if (-not (Test-Path -LiteralPath $helperPath)) { return $null }

    . $helperPath
    if (-not (Get-Command Test-SomeHealth -ErrorAction SilentlyContinue)) { return $null }

    return Test-SomeHealth
}
```

## Verification discipline for long plan chains

For multi-plan work, update durable plan checkboxes and `todo` state at every completed plan boundary. If execution is interrupted by context/tool-call limits, the final response must include:

- last completed plan/task,
- exact active task id/status,
- files changed,
- verifications already run,
- next command/check to run.

This makes resumption deterministic instead of relying on chat reconstruction.

## Bounded verification for slow PowerShell health/audit paths

Some vault health/audit scripts have optional slow phases such as similarity scans. If the exact verification command times out at the harness foreground cap, do not mark the plan failed immediately when the slow phase is orthogonal to the refactor. Preserve the verification intent with an explicit bounded mode such as `-NoSimilarity` or `-Fast`, and record the timeout in the durable plan checklist. The follow-up smoke plan should own bounded coverage for the slow path.

Pattern:

```powershell
$out = & "C:\path\to\Test-VaultHealth.ps1" -VaultRoot "C:\Users\Tiger\Vault" -Json -NoSimilarity
$obj = $out | ConvertFrom-Json
if ($obj.recommended_mode -notin @("targeted-ingest", "full-vault-diagnosis", "no-action-needed")) {
    throw "Unsupported recommended_mode: $($obj.recommended_mode)"
}
```

## Smoke tests should not leave vault artifacts

When refactoring smoke suites, write reports/prompts/progress files under a unique temp root instead of the vault's `maintenance/scripts-outputs` tree unless the test specifically verifies that production output location. Clean the temp root before exit and add a positive cleanup check when practical.

Pattern:

```powershell
$smokeRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("vault-script-smoke-{0}" -f ([guid]::NewGuid()))
try {
    # write reports/prompts/progress under $smokeRoot
}
finally {
    Remove-Item -LiteralPath $smokeRoot -Recurse -Force -ErrorAction SilentlyContinue
}
```

## Negative controls for retired-term regressions

For smoke tests that assert retired commands/modes do not reappear, add a negative-control check using a temporary mock file, not the real script. This proves the detector would fail if a retired term existed while avoiding dirtying production files.

Pattern:

```powershell
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("negative-control-{0}" -f ([guid]::NewGuid()))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
try {
    $mock = Join-Path $tempDir "mock.md"
    "Use tasks-review" | Set-Content -LiteralPath $mock -Encoding UTF8
    $retired = Select-String -Path (Join-Path $tempDir "*.md") -Pattern "inbox-review|tasks-review|master-tasks\.md|full-vault-cleanup" -SimpleMatch:$false
    if (-not $retired) { throw "Negative control failed: retired term was not detected." }
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
```

## Hermes profile hook guardrail cleanup plans

When a plan edits Hermes profile-local guardrails (for example `profiles/<name>/hooks/*.py` or profile `config.yaml`), treat it as cross-profile work and pass the tool's explicit cross-profile opt-in after the user has directed that profile edit. Do not modify the current/default profile by assumption; first verify the runtime profile with `hermes -p <profile> hooks list`.

Guardrail cleanup verification should use direct JSON payloads against the hook scripts, not real protected-file edits. Cover at least:

- deny paths: protected docs, `Types/*`, and `scripts/*` should return a JSON `decision: block`;
- safe path: a temp path outside the vault should return `{}` / pass;
- ask-first paths: domain `wiki/index.md` and `wiki/log.md` should return the configured approval block/warn behavior.

Run `python -m py_compile` on edited hook modules and `hermes -p <profile> hooks doctor` after edits. If doctor reports "script modified since approval" but the hook still exists, is allowlisted, and emits valid JSON, do **not** automatically run `hermes hooks revoke`; revocation requires next-runtime user consent and is an admin follow-up, not a functional plan failure.

## PowerShell cron wrapper pattern for Hermes scheduled jobs

When a cron job runs a PowerShell script via Hermes, the cron system invokes the script as Python by default. Create a thin Python launcher that invokes `pwsh`/`powershell.exe` with proper encoding:

```python
import subprocess, sys, os
script = os.path.join(os.path.dirname(__file__), 'your_wrapper.ps1')
ps = r'C:\Program Files\PowerShell\7\powershell.exe'
if not os.path.exists(ps): ps = 'powershell.exe'
res = subprocess.run([ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script],
                     capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
print(res.stdout)
if res.stderr: print(res.stderr, file=sys.stderr)
sys.exit(res.returncode)
```

Key points:
- Use `encoding='utf-8', errors='replace'` to handle non-UTF-8 bytes from PowerShell output
- Use hidden window style in the PowerShell wrapper: `$psi.WindowStyle = 'Hidden'`
- Cron `script` field must be relative to `~/.hermes/scripts/` (e.g., `vault_cron_wrappers/vault_cron_agent_skills.py`)

## Windows/MSYS Python package install pattern for Hermes maintenance

When running from the Hermes desktop/cron shell on Windows, commands execute under Git Bash/MSYS, not PowerShell. Do not assume a venv exposes a runnable `pip` entrypoint at `.../.venv/Scripts/pip` or that invoking `pip.exe` by path will work cleanly from bash. Prefer the exact interpreter path and `-m pip`:

```bash
/c/Users/Tiger/AppData/Local/hermes/hermes-agent/.venv/Scripts/python.exe -m pip install <package>
```

Why this matters:
- avoids false negatives from missing or non-runnable `pip` shims;
- guarantees the package operation targets the interpreter you just inspected;
- reduces confusion when a repo contains both `.venv/` and `venv/` or mixed Windows/POSIX launchers.

Verification pattern:
1. inspect `.../.venv/Scripts/` first to confirm the interpreter path exists;
2. run `python.exe -m pip install ...` instead of bare `pip install ...`;
3. read the install target in stdout to confirm which environment actually received the package.

## Cron job output format requirements

User requires consistent Telegram output format across all cron jobs:

**Title line (first agent output line):** Bold job name with status emoji
```
**🟢 OK — Vault Daily Check — Agent Skills**
```

**Section headers:** Bold with colon
```
**What ran:**, **Results:**, **Dependency notes:**, **Problems:**, **Fix:**, **Next steps:**
```

**Separators:** Exactly three hyphens between sections
```
---
```

**Emoji keywords:** Consistent light emojis for scanability
- 🐛 bug, 🔧 fix, 🚫 denied, ⚠️ attention, 👉 next steps, ✅ approved/result

**Style:** Short day-to-day language, bullet points only, no long paragraphs.

## Vault health script patterns

### System file detection via frontmatter tags

Core vault files (`vault-index.md`, `vault-guide.md`, `STANDARDS.md`, `CONSTITUTION.md`, `AGENTS.md`) must have `tags: [system]` in frontmatter for discovery:

```yaml
tags: [system]
```

Discovery function scans vault root for `*.md` with `[system]` tag; minimum expected list is cross-checked.

### Domain classification from vault-index.md

Canonical domain list comes from `vault-index.md` "## Domains" table only (not Reference Areas). Parse only lines under that section:

```powershell
if ($line -match '^##\s+Domains') { $inDomainsSection = $true; continue }
if ($line -match '^##\s+') { $inDomainsSection = $false }
if ($inDomainsSection -and $line -match '^\s*\|\s*([A-Za-z0-9\s]+?)\s*\|\s*[`A-Za-z0-9/\-\s]+\s*\|') {
    $name = $matches[1].Trim()
    if ($name -and $name -notmatch '^(Domain|---|Social Media)$') { $domainNames += $name }
}
```

Exclude retired domains (e.g., "Social Media") and non-domain sections.

### Inbox reporting: count only

Inbox status returns counts only, not file listings:

```powershell
return [pscustomobject]@{
    total_files = $count
    content_files = $contentCount
    ingested_true = $ingestedTrueCount
}
```

## Post-Ingestion Consultation pattern

Embed a required consultation loop in `inbox-action` prompts after ingestion completes:

```markdown
## Post-Ingestion Consultation (REQUIRED — execute after ingestion complete)

### 1. Expert Synthesis
3-5 bullet summary: key insights, context, gaps

### 2. Connect to Existing Vault Knowledge
Search wiki/index.md, wiki/log.md, cross-domain links, existing plugins/skills

### 3. Recommend Next Steps with Tradeoffs
For each action: what, benefits, costs/risks, dependencies, integration check (e.g., "can this plugin install in Hermes?")

### 4. Ask Robert (Conversational, No Artifact)
"Do you want to: (a) Discuss integration, (b) Dive deep, (c) Build/implement, (d) Defer, (e) Something else?"

### 5. Clarification Protocol
If uncertain: "I'm unsure about [X]. Robert, can you clarify [specific question]?"

### 6. Brainstorming Mode
Use `brainstorming` skill, stay conversational until "let's do [X]", then propose concrete plan.
```

Key constraints: No artifact produced, factual only (ask if uncertain), conversational until concrete plan, use `brainstorming` skill for option generation.