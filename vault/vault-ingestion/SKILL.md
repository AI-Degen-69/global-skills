---
name: vault-ingestion
description: "Use when ingesting selected files, URLs, or inbox items into Robert's Obsidian vault. Always perform the full canonical process: preserve raw source, create or update wiki material, links, logs, audit-fix, and a post-ingestion report."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, ingestion, inbox, provenance]
    related_skills: [vault-audit-fix, vault-graph-hygiene, vault-compounding-loop]
---

# Vault Ingestion

## Overview

This skill governs canonical ingestion into Robert's Obsidian vault. It applies identically to foreground, on-demand, background, and cron ingestion. There are no shortcut modes.

## When to Use

- Robert chooses one or more files to ingest and discuss.
- Robert asks to ingest an inbox item, URL, PDF, webpage, transcript, image OCR result, article, paper, or skill.
- A background or cron job processes pending `_Inbox/` material.
- An external source needs to become durable vault material.

## Non-Negotiable Rule

Foreground and background ingestion use the same quality bar. The only difference is whether Robert is present afterward for discussion.

## Required End State

Every completed ingestion must have:

- source preserved or moved to the correct domain `raw/` location when appropriate;
- durable `wiki/` material created or updated when the source warrants it;
- links created to real existing vault notes where semantically appropriate;
- target domain `wiki/index.md` updated when the new material belongs in the map;
- target domain `wiki/log.md` updated;
- the original intake item either moved out of `_Inbox/` or explicitly cleared as a verified duplicate-resolution;
- an audit-fix pass run afterward;
- a post-ingestion summary report generated.

## Procedure

Follow `references/canonical-ingestion-flow.md` exactly. **Speed optimization (DEFAULT execution layer):** for the mechanical steps (raw preserve, durable writes, audit), use the `vault-ingest-streamlined` skill — `mv` the raw instead of read-then-write, batch independent writes, pre-check + create missing wikilink targets, and verify with a path-filtered audit. This does NOT lower the quality bar. Use `references/approval-gates.md` when deciding what must stop for Robert. For already-ingested source recaptures, also use `references/duplicate-recapture-resolution.md`. If the existing canonical raw has degraded into a placeholder/stub and the inbox file is a richer recapture of the same source, use `references/degraded-canonical-raw-repair.md`. For delegation timeout patterns, see `references/delegation-timeout-pattern.md`. For existing-first search execution and tool-selection rules, see `references/existing-first-search-patterns.md`. For sparse, truncated, or misleading inbox captures that do not actually contain the claimed source payload, use `references/sparse-source-stop-conditions.md` before widening search or creating any durable artifacts. For resumed sessions or any turn where tool work happened but the visible reply was empty/incomplete, use `references/resumed-ingestion-verification.md` before continuing or closing. For git-backed vaults where gbrain/queryability matters after ingest, use `references/gbrain-sync-visibility.md` before claiming the material is searchable.

## Reports and Special Cases

- Use `templates/post-ingestion-report.md` for foreground or on-demand ingestion. **When filling it, replace the `{{UNIQUE_TITLE}}` placeholder with a UNIQUE, source-specific title (include source name + date, e.g. "Headroom Better Stack Ingestion Report"). Never emit the generic "Post-Ingestion Report" as the title — duplicate titles collide in gbrain link resolution and create orphan ambiguity (see skill `gbrain-graph-population`).**
- Use `templates/background-ingestion-report.md` for background or cron ingestion.
- If the source is an agent skill, prompt, workflow, framework, or automation method, include `templates/agent-skill-conclusion.md`.

## Discussion Mode

After foreground or on-demand ingestion, produce the report and then be ready to answer Robert's questions about the contents, implications, opinions, conflicts, and next moves.

## Post-Ingestion Consultation (New Pattern)

When Robert runs the `inbox-action` prompt (Option 1), the generated prompt now embeds a **Post-Ingestion Consultation** loop that the agent must execute after durable outputs are verified. This replaces the old "Discussion Mode" with a structured loop:

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

This replaces the old "Discussion Mode" — the agent must now run this loop before ending the session.

## Background Mode

After background ingestion, produce the report and stop. Do not invent a discussion.

## Common Pitfalls

1. Treating background ingestion as a faster, lower-quality shortcut.
2. Trusting frontmatter before reading the actual source body.
3. Skipping existing-first checks and creating duplicate durable notes.
4. Treating a re-captured inbox item as a new ingest when a canonical raw + wiki + extract chain already exists elsewhere in the vault.
5. **Discarding a richer recapture because a canonical raw filename already exists** — If the canonical raw has degraded into a placeholder/stub while downstream notes already treat it as the superseding source, repair that canonical raw path from the richer recapture instead of keeping the degraded file or creating parallel provenance. See `references/degraded-canonical-raw-repair.md`.
6. Adding speculative links to notes that do not exist.
7. Ending the task before running `vault-audit-fix`.
8. **Treating the canonical chain as proof that ingestion is fully closed** — On resumed sessions or handoff-driven follow-up work, `raw/` + `wiki/` pages may already exist while the original `_Inbox/` item still sits uncleared. Before declaring ingestion complete, explicitly verify whether the intake file was moved or cleared; if it remains in `_Inbox/`, resolve it as duplicate-recapture with a recovery copy, log entry, and verified removal.
9. **Delegating to librarian profile for already-ingested files** — When a file in the vault already has `Ingested: true` in frontmatter and corresponding wiki pages exist, the vault's automatic ingestion has completed. Delegating to the `librarian` profile in this case can timeout (600s) because the profile attempts redundant processing. Check `Ingested: true` and wiki page existence before delegating.
10. **Using MSYS `/c/...` paths with file-write tools on Windows** — `terminal` accepts MSYS paths like `/c/Users/Tiger/Vault`, but `write_file`, `patch`, and other file tools may resolve `/c/...` as `C:\\c\\...` outside the real vault. For vault writes on Windows, use native absolute paths such as `C:\\Users\\Tiger\\Vault\\...`; if a stray `C:\\c\\...` file is accidentally created, remove it before verification.
11. **Incorrect domain selection for agent/tool documentation** — When ingesting documentation about Hermes integrations, tools, or agent workflows (e.g., Open Second Brain, Claude Code, Codex), place the material in the `Hermes/` domain rather than creating a new domain. The raw file should go to `Hermes/raw/` and the extract to `Hermes/wiki/`, with appropriate updates to `Hermes/wiki/index.md` and `Hermes/wiki/log.md`. This ensures the documentation is discoverable through the Hermes domain's index and follows the established pattern for agent/tool references in the vault.

12. **External calls may hang** — Ingesting sources that require network calls (e.g., YouTube metadata, GitHub stars, remote web pages) can cause the ingestion process to hang if the remote service is slow or unreachable. If you observe timeouts or long pauses, consider skipping external enrichment, using cached metadata, or proceeding with a minimal ingest that relies only on the local source file. You can always enrich the note later with a separate update once connectivity is restored.
13. **Botching existing-first search with the wrong tool semantics** — `search_files(target='files')` expects a glob-like filename pattern, while `search_files(target='content')` expects a regex to search inside file contents. Do not pass shell wildcards like `*foo*` into content search, and do not repeat the same zero-result query multiple times. If recall is weak, pivot to filename-token searches, direct directory listing, or a validated `grep -r 'term' path` command rather than malformed shell snippets or identical retries.
14. **Sparse or misleading inbox captures need an early stop, not speculative recall** — If the selected file exists but its body is only a stub/fragment and does not contain the promised source, do not broaden into title-keyword hunts across the vault and do not ingest from neighboring materials. Treat it as blocked on source quality, report the blocker, and wait for a better capture or a different selected item.
15. **Closing a resumed ingest without reader-side verification** — If a prior turn executed tools but returned an empty/partial response, do not assume the ingest is clean just because files now exist. Resume from live vault state: verify raw/wiki/extract/index/log/inbox artifacts, inspect the exact edited slice of `wiki/index.md` and `wiki/log.md`, and fix formatting corruption such as malformed list markers or accidental duplicate adjacent entries before declaring success.
16. **Inventing the durable extract path instead of following the domain's live layout** — Do not assume every domain stores extracts under `wiki/extracts/`, and do not assume a bare basename like `[[foo]]` will be picked up by the domain index. Before creating the durable note, inspect how that domain currently names and places extracts (for example, `Agent Skills` indexes `extract-*.md` pages directly under `wiki/`). If you created the note in the wrong place, repair the chain: move/create the extract at the canonical location, update `raw.linked_extracts`, regenerate the domain index, and verify the index actually contains the new entry before closing.
17. **Treating a global audit FAIL as proof the ingestion itself failed** — `check_vault.py` can surface unrelated pre-existing debt in other domains. After an ingest, distinguish (a) failures introduced by this ingestion, which must be fixed before closeout, from (b) older unrelated failures, which should be reported explicitly as pre-existing debt. Do not falsely claim a clean audit, but do not abandon a structurally-correct ingest just because the whole vault already had unrelated issues.
18. **Assuming `gbrain sync` sees uncommitted ingest artifacts** — In Robert's git-backed vault workflow, new raw/extract/report files may be invisible to `gbrain sync --source vault-tiger` until they are committed. A sync that reports "1 changed source" but `~0 new tokens`, followed by `gbrain query` returning no results, usually means the ingest lives only in the working tree. Commit the ingestion set first, then re-run sync and verify retrieval with a positive query instead of trusting the sync exit code alone.

## Duplicate Re-capture Rule

When the selected `_Inbox/` item is the same source and same subject as an already-ingested canonical raw capture:

1. Create a recovery copy before deleting or clearing the inbox item.
2. Compare the new intake against the canonical raw/wiki/extract chain, not just against `_Inbox/`.
3. If the canonical raw itself is degraded (placeholder/stub/incomplete) and the inbox recapture is the same source but materially richer, repair the canonical raw path from the recapture instead of treating the existing file as good enough. See `references/degraded-canonical-raw-repair.md`.
4. If the new capture is not materially richer, resolve it as a duplicate instead of creating a second raw note.
5. If the new capture adds one useful connection or clarification, patch the existing durable note(s) and log the duplicate-resolution explicitly.
6. Clear the `_Inbox/` copy only after the canonical chain and log entry are verified.
7. If the duplicate points to another already-known repository, method, or concept, prefer updating the existing durable note with that cross-link instead of creating parallel provenance.

## Verification Checklist

- [ ] Existing-first check completed.
- [ ] Domain selected from existing vault domains.
- [ ] Source preserved in `raw/` when appropriate.
- [ ] Wiki or extract material created or updated.
- [ ] Links added only to real targets.
- [ ] Domain `wiki/index.md` updated when needed.
- [ ] Domain `wiki/log.md` updated.
- [ ] Original `_Inbox/` item moved, cleared, or duplicate-resolved with recovery handle + verified removal.
- [ ] Audit-fix run after ingestion.
- [ ] Post-ingestion report produced.
- [ ] **Pre-delegation check: If `Ingested: true` in frontmatter and wiki pages exist, ingestion is complete — do not delegate to librarian profile.**

---

## Advanced Patterns & Lessons Learned

### Companion Sources (Multi-Format Same Subject)
When a subject has multiple source formats (e.g., GitHub repo + author blog + YouTube analysis):
1. Run existing-first check across **all formats** — search by repo name, author, title keywords, video ID.
2. Treat as **companion sources** per S-023 if they provide materially different angles (author's deep-dive + independent analysis).
3. Create **one unified extract** synthesizing all sources; link all raw captures to it.
4. Log the relationship explicitly: "3 companion sources, same subject."

### Lifecycle Discrepancy: `Ingested: true` + Missing Linked Extract
**Pattern:** Raw capture has `Ingested: true` but `linked_extracts` references a non-existent extract.
**Fix:** Complete the missing durable chain (create extract, concept notes, index/log entries) — do NOT re-ingest the raw. Patch the raw's frontmatter with the new extract link once created. Log as "Fixed lifecycle discrepancy."

### Concept Note Extraction (Atomic Reusable Ideas)
When ingesting a framework/tool with multiple distinct patterns:
- Create **one concept note per reusable idea** (e.g., `doubt-driven-development`, `anti-rationalization`, `scope-discipline`).
- Concept notes live in `wiki/concepts/` with `type: "[[Doc]]"` and link back to the unified extract.
- This enables retrieval by concept, not just by source — critical for graph connectivity.
- Name concept files `lowercase-kebab.md` matching the canonical term.

### Wikilink Pre-Validation Before Extract Creation
**Before writing an extract that references concept wikilinks:**
1. Create all referenced concept pages FIRST.
2. Verify each `[[Concept Name]]` resolves (audit CK08).
3. Then write the extract with confident wikilinks.
**Why:** Audit runs after ingestion; failed wikilinks require re-edit cycles. Pre-creating avoids this.

### Extract Type Platform Field Restriction
The `Extract` type schema does **not** include a `platform:` field (unlike `Article`, `Video`, `Repository`). 
- Do not add `platform:` to Extract frontmatter — it will fail CK11.
- Source/platform provenance lives in `source:` array and the raw captures themselves.

### Audit-Driven Fix Loop
Standard cycle:
1. Run `python scripts/check_vault.py` after ingestion.
2. Separate FAIL items into:
   - **ingestion-caused issues** in the files just touched, which must be fixed before closeout;
   - **pre-existing unrelated vault debt**, which must be reported accurately if it blocks a full PASS.
3. Fix all ingestion-caused FAIL items (wikilink targets, platform field, naming, malformed edits).
4. Re-run audit.
5. If the vault still fails only because of unrelated pre-existing debt, verify the touched ingestion artifacts directly and say so explicitly in the report.
This is part of "Audit-fix run after ingestion" — not optional, even when a full-vault PASS is not immediately achievable.
