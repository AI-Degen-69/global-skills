---
name: obsidian
description: Use when reading, searching, or editing notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Vault-specific second-brain workflow

When the target vault has a root `AGENTS.md`, treat it as an operating system for the knowledge base, not just a folder of notes.

Recommended traversal order:
1. Read the vault root `AGENTS.md`
2. Read the vault's primary operating guide (for this vault, `vault-guide.md`)
3. Read the vault map / MOC (for this vault, `vault-index.md`)
4. Enter the target domain through `domain/wiki/index.md`
5. Read `domain/wiki/log.md` before making structural or ingestion decisions
6. If present, read domain-local `wiki/AGENTS.md` for subdomain conventions

Operational rules that matter in practice:
- Treat the vault as an **agent-readable knowledge graph**. Prefer domain maps, indexes, and linked durable notes over broad blind search.
- Treat inbox or raw captures as **untrusted intake** until the note body has been read and the metadata verified.
- Never guess canonical wikilink targets, casing, or slugs when the vault depends on exact links. Look them up live first.
- If the vault uses protected schema folders such as `Types/`, treat them as read-only infrastructure unless the user explicitly says otherwise.
- Check durable `outputs/` areas before re-synthesizing work that may already exist.

See also `references/vault-second-brain-patterns.md` for the condensed Robert-vault-specific pattern discovered in session work.
See also `references/vault-powershell-automation.md` for the companion PowerShell control surface used to audit and generate vault prompts.
See also `references/agent-skills-domain-routing.md` for the stricter inbox-first ingestion/routing pattern absorbed from the old ingestion-specific sibling skill.

## Robert vault conventions

When the vault is `C:\Users\Tiger\Vault`, treat it as an agent-readable knowledge graph rather than a loose note directory.

Default navigation order:
1. Read `C:\Users\Tiger\Vault\AGENTS.md`
2. Read `C:\Users\Tiger\Vault\vault-guide.md`
3. Read `C:\Users\Tiger\Vault\vault-index.md`
4. Enter the target domain via that domain's `wiki/index.md`
5. Read the domain's `wiki/log.md` before meaningful edits or ingestion work
6. If you enter a domain with its own `wiki/AGENTS.md`, read and follow it

Operational rules for this vault:
- Treat `_Inbox/` as transient intake, not durable knowledge; verify the note body before trusting frontmatter.
- Never guess `type`, `platform`, `author`, slug spelling, or casing; look up canonical targets live first.
- Never write a wikilink unless the target file already exists.
- Treat `Types/` as read-only infrastructure; do not create, edit, or delete Type files.
- Prefer durable domain notes and `outputs/` before raw captures when answering questions.
- Use `vault-index.md` as the safe map of the curated second-brain surface; do not assume every root folder is part of the curated knowledge graph.
- When the task touches `C:\Program Files\PowerShell\7\scripts\Vault`, treat that folder as the vault automation control surface, not as random utility scripts.
- Before editing that PowerShell suite, create a recovery handle outside the folder, then run the live smoke harness (`Verify-Scripts.ps1 -Fast` on the current suite; `Test-VaultScripts.ps1 -Fast` if the older alias layer is still what exists) before and after changes as the minimum regression gate.
- For Hermes-facing prompt generation or diagnosis, keep the authority order aligned with live vault docs first and use script output as accessory context rather than source of truth.

## Vault PowerShell automation for this vault

When the user asks to audit, improve, or integrate the companion PowerShell suite at `C:\Program Files\PowerShell\7\scripts\Vault`, use this mental model:

- **Current canonical names (preferred):**
  - `Prompt.ps1` = prompt/orchestration generator
  - `Health.ps1` = vault-wide diagnosis entrypoint
  - `Audit.ps1` = structured JSON audit engine
  - `Verify-Scripts.ps1` = smoke/regression harness
- **Legacy/compatibility names may still exist in some sessions:**
  - `New-VaultPrompt.ps1`
  - `Test-VaultHealth.ps1`
  - `Test-VaultAudit.ps1`
  - `Test-VaultScripts.ps1`

Integration guidance:
- The script layer should reinforce the live vault operating model, not replace it.
- Prompt text emitted by the scripts must send Hermes back to live vault docs: `AGENTS.md`, `vault-guide.md`, `vault-index.md`, then domain `wiki/index.md` and `wiki/log.md`.
- Keep automation labels honest: distinguish interactive approval-gated flows from Hermes-safe automated flows.
- Prefer resolving the concrete PowerShell executable inside the scripts instead of assuming `pwsh` is on PATH, especially for nested script invocations.
- Do not hardcode old script names from memory; inspect the live `scripts/Vault` directory and prefer canonical names first, with legacy aliases only as fallback.
- After changes, verify both the regression harness and at least one real entrypoint such as `-ListModes` or JSON health output.
## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Ingestion lane (umbrella subsection)

When the request is not ordinary note editing but **ingestion** of external material into the vault, switch to a stricter intake workflow:

1. Read the vault operating context (`AGENTS.md`, `vault-guide.md`, `CONSTITUTION.md`, `STANDARDS.md`, `vault-index.md`) before touching notes.
2. Start from `_Inbox` unless the vault's own rules say otherwise.
3. Run duplicate/domain/path sanity checks before moving content.
4. Read the full note body; frontmatter is metadata, not truth.
5. Create a recovery handle before destructive moves or deletions.
6. Route by enduring value, not by title alone.
7. Update the domain graph surfaces (`wiki/index.md`, `wiki/log.md`, canonical topic pages, and any required `outputs/` notes).
8. Remove the inbox original only after destination + graph verification.

Use `references/agent-skills-domain-routing.md` for a concrete ingestion/routing example.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
