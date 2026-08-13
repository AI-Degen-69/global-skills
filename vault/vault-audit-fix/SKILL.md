---
name: vault-audit-fix
description: Use when auditing Robert's vault, after ingestion, or before/after graph cleanup. Run the full audit, fix safe
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, audit, repair, maintenance]
    related_skills: [vault-ingestion, vault-graph-hygiene, vault-cron-ingestion]
---

# Vault Audit-Fix

## Overview

Robert does not want a weak read-only audit as the default workflow. If you audit, fix what is safe and deterministic, rerun the checks, then clearly separate what remains from what requires approval.

## When to Use

- Robert asks for an audit.
- Robert asks whether vault maintenance is enough.
- You just completed ingestion.
- You are about to make or just made graph hygiene changes.
- An automated background/cron ingestion run needs a closeout safety pass.
- You are performing a scoped domain audit (e.g., Agent Skills) and need to fix deterministic issues.

## Required Loop

1. Run the live audit commands in `references/vault-audit-scripts.md`.
2. Classify findings using `references/safe-fix-matrix.md`.
3. Fix safe deterministic issues now.
4. Rerun the audit.
5. Report:
   - what was fixed;
   - what remains unresolved;
   - what needs Robert approval;
   - exact file paths.

## Approval Gates

Always escalate these instead of doing them autonomously:

- deleting durable notes or raw captures;
- merging duplicate notes;
- renaming durable wiki pages;
- changing `Types/`;
- changing domain taxonomy or creating domains;
- bulk rewrites;
- ambiguous repairs where the intended target is not clear.

## Live Commands

Prefer the live scripts, not remembered flags:

```bash
python scripts/check_vault.py --quick --json
python scripts/build_catalog.py --stats
python scripts/build_index.py --check
```

For scoped domain audits using PowerShell (e.g., Agent Skills), use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Program Files\PowerShell\7\scripts\Vault\Test-VaultAudit.ps1" -Root "C:\Users\Tiger\Vault" -PathPrefix "<Domain Name>" -Json -SkipTodoist -MaxSamples 0
```

Interpret them correctly on Robert's vault:
- `check_vault.py --quick --json` is the structural pass/fail gate.
- `build_catalog.py --stats` is the positive verification pass for current domain/root counts and rewrites the root `vault-index.md` catalog.
- `build_index.py --check` only reports which domain indexes are stale; it does **not** regenerate them.
- To refresh a specific domain index after ingestion, run `python scripts/build_index.py "<Domain Name>"` or the appropriate live equivalent after inspecting the script usage.
- For PowerShell audit, the JSON output includes a `scoped_audit` object with `errors` and `warnings` arrays that can be processed programmatically.
- When Robert asks whether the top-level vault index file is updated, treat that as a **root catalog freshness check**, not a generic search for every `index.md` in the vault. Rebuild with `python scripts/build_catalog.py` when appropriate, then verify the root `vault-index.md` frontmatter `updated:` field and counts directly. Do not conflate `vault-index.md` with per-domain `wiki/index.md` files.

If a command fails or arguments differ, inspect the live script help/source before proceeding.

## Reporting

Use `templates/audit-fix-report.md`. Keep the report outcome-oriented: commands run, safe fixes applied, remaining issues, approval-needed items, and final rerun status.

## Common Pitfalls

1. Stopping after surfacing findings. Audit-only is incomplete unless a blocker prevents safe fixes.
2. Treating approval-gated changes as safe because they look obvious.
3. Declaring success without rerunning the audit.
4. Hiding script failures instead of reporting the exact failed command.
5. Misreading script semantics — especially assuming `build_index.py --check` rebuilt indexes when it only reported staleness, or forgetting that `build_catalog.py --stats` is what refreshes the root `vault-index.md` catalog on this vault.
6. PowerShell variable interpolation errors: using `"$key: $($value)"` inside double quotes can cause parser errors when `$` is followed by a non-variable character. Use concatenation (`$key + ": " + $value + "`n"`) or escape the dollar sign.

## Scoped Domain Audit Fixes

When auditing a specific domain (e.g., Agent Skills) using the PowerShell Test-VaultAudit.ps1 script, the following deterministic fixes are safe to apply automatically:

### raw.linked_extracts errors
- **Symptom**: Domain raw Markdown must link forward to its durable extract or synthesis.
- **Fix**: Populate the raw file's `linked_extracts:` frontmatter list with the durable target wikilink. The PowerShell audit checks that YAML list, not just body text. Ensure the target extract/synthesis note exists in the domain's actual wiki layout before linking it.
- **Layout caveat**: Do not assume every domain uses `wiki/extracts/`. For example, Hermes keeps extract notes directly under `Hermes/wiki/` (e.g., `Hermes/wiki/extract-hermes-*.md`), while other domains may use subfolders. Read the live domain structure first, then either link to an existing extract note or create a minimal placeholder extract in the correct location.

### schema.required_field errors
- **Symptom**: Missing field required by Type schema (e.g., `Article.icon`, `Video.author`, `Extract.origin`, `Company.name`).
- **Fix**: Ensure the file has YAML frontmatter. Add the missing field with an empty string value if absent.

### wikilinks.missing_target warnings
- **Symptom**: Wikilink target basename does not exist.
- **Fix**: Create the missing wiki page under the domain's actual wiki location with the target basename as the title.
- **Historical-log caveat**: If the broken target appears in a domain `wiki/log.md` because an older note was intentionally deleted or renamed, a minimal placeholder/tombstone page is a safe deterministic fix. Use it to preserve log integrity without rewriting historical entries. The placeholder should clearly state that it exists to satisfy historical links and point to the current canonical replacement when one exists.

### index.generic_entities_section warning
- **Symptom**: Domain index uses generic Entities section instead of concrete Type-aligned sections.
- **Fix**: Replace the `## Entities` section in `Agent Skills/wiki/index.md` with sections for each Type found in the domain. For each Type, list all files of that type as wikilinks.

### wikilinks.ambiguous_domain_page warnings
- **Symptom**: Ambiguous wikilink to shared domain page basename (e.g., `[[index]]` could refer to multiple domain indexes).
- **Fix**: Prefix the ambiguous target with the domain name (e.g., `[[index]]` → `[[Agent Skills/index]]`).

## Verification Checklist

- [ ] Ran the live audit commands or documented why a command could not run.
- [ ] Applied every safe deterministic fix in scope.
- [ ] Reran the audit after fixes.
- [ ] Reported exact paths for remaining and approval-needed items.
- [ ] Did not perform approval-gated destructive work.

---\n\n### Pitfall: core system files missing `tags: [system]` breaks discovery and audit\n\n**Symptom:**  \nHealth script and audit report `vault-index.md`, `vault-guide.md`, `STANDARDS.md` as missing even though they exist at vault root. System Files score penalized, audit flags missing files.\n\n**Root cause:**  \n`Get-DiscoveredSystemFiles` only scans for `.md` files at vault root with `tags: [system]` in frontmatter. Files without this tag are invisible.\n\n**Required core system files (must have `tags: [system]`):**\n- `vault-index.md`\n- `vault-guide.md`\n- `STANDARDS.md`\n- `CONSTITUTION.md` (already has it)\n- `AGENTS.md` (already has it)\n\nFix: Add `tags: [system]` to frontmatter of `vault-index.md`, `vault-guide.md`, `STANDARDS.md`.\n\n---\n\n### Pitfall: domain classification uses directory scan instead of vault-index.md canonical list\n\n**Symptom:**  \nAudit scans domains by listing top-level directories and excluding a hardcoded blocklist (`_Inbox`, `Platforms`, `Types`, `tools`, `maintenance`). This incorrectly includes:\n- Reference Areas (`Platforms`, `Types`, `Scripts`) from `vault-index.md` as domains\n- Retired domains like `Social Media` that still have a folder but should be excluded\n- Future folders that aren't real domains\n\n**Root cause:**  \nThe canonical domain list lives in `vault-index.md` under `## Domains` table, not in the filesystem directory structure.\n\n**Fix:**  \nParse `vault-index.md` for the Domains section:\n1. Read file, find `## Domains` section\n2. Extract domain names from markdown table rows: `| Domain | Root | Wiki | Raw | Status |`\n3. Exclude `Social Media` (retired) and table headers/separators\n4. Use this list to filter directory scan instead of hardcoded blocklist\n\n**Why it matters:**  \nReference Areas (`Platforms`, `Types`, `Scripts`) are cross-cutting infrastructure listed under `## Reference Areas` in `vault-index.md` — they are explicitly NOT domains and should never be scanned as such. Including them creates false \"domain infrastructure gaps\" findings.\n\n---\n\n### Pitfall: inbox reporting lists full file details instead of count only\n\n**Symptom:**  \nAudit/inbox check returns every file with path, size, frontmatter status — noisy, not actionable for daily snapshot.\n\n**User preference:**  \nReport only **counts**:\n- `total_files`\n- `content_files` (excluding `ingestion-log.md`)\n- `ingested_true` (files marked `Ingested: true` but still in `_Inbox`)\n\nDo not list individual files, paths, or frontmatter details unless explicitly asked.\n