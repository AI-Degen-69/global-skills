---
name: vault-ingest-streamlined
description: "Faster canonical vault ingestion for _Inbox GitHub-repo / source captures. Preserves the FULL quality bar from vault-ingestion (raw preserve, durable wiki, links, index/log, audit, report) but uses mv + batched writes + pre-checked wikilink targets to cut tool round-trips. DEFAULT optimized execution layer for vault-ingestion. Load when ingesting one or more _Inbox items and you want the fast path."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, ingestion, inbox, speed, mv-optimization]
    related_skills: [vault-ingestion, vault-audit-fix]
---

# Vault Ingest — Streamlined (fast path)

## When to use
- Ingesting `_Inbox/` files (GitHub repos, articles, docs) where the source is a single self-contained capture.
- You want the speed optimization without lowering the canonical quality bar from `vault-ingestion`.
- This is the **DEFAULT optimized implementation** of the canonical flow — same end state, fewer tool round-trips.

## What changes vs the naive path (speed, NOT scope)
1. **`mv` the raw, do not read-then-write-then-delete.** Move the inbox file straight into `Domain/raw/YYYY-MM-DD-slug.md`. The body is preserved verbatim (no 36KB re-read/re-write). Fix frontmatter in place with `patch` (set `Ingested: true`, add `linked_extracts`, repair malformed fields). You already have the source content from the discovery step — do not re-read the whole file.
2. **Pre-check wikilink targets in ONE batched turn.** Before writing any durable page, run all `search_files` existence checks together: creator page (`[[xbtlin]]` etc.), platform (`[[GitHub]]`), type pages (`[[Repository]]`, `[[Company]]`, `[[Person]]`), domain index/log. If a target is missing, CREATE it — never emit broken wikilinks (fails CK08/CK11).
3. **Name every new file lowercase-kebab.** `Xbtlin.md` fails CK04 (Filename violates lowercase-kebab). Use `xbtlin.md`. Applies to creator/Person/Company pages too.
4. **Batch the writes.** Write the repo page, creator page, and patch index.md + log.md in a single turn where edits are independent. Sequential read-then-patch still applies per file, but independent files go together.
5. **Verify with a path-filtered audit.** Run `check_vault.py --quick --json`, parse from the first `[`, then filter issues by YOUR file paths. Report only failures that touch your files; pre-existing debt is a separate class.

## Required End State (identical to canonical)
- source preserved in `raw/` (via mv, body intact)
- durable wiki/extract material created
- links to real existing targets only (create missing targets first)
- domain `wiki/index.md` + `wiki/log.md` updated
- original `_Inbox/` item removed
- `vault-audit-fix` run; report distinguishes ingest-caused vs pre-existing
- post-ingestion report produced

## Exact commands
```bash
# 1. move raw (preserves body verbatim)
mv "_Inbox/<file>.md" "Domain/raw/YYYY-MM-DD-slug.md"
# 2. audit with path filter
cd "/c/Users/Tiger/Vault" && python3 scripts/check_vault.py --quick --json > "$HOME/audit.json" 2>&1
python3 -c "import json;raw=open('$HOME/audit.json',encoding='utf-8').read();d=json.loads(raw[raw.find('['):]);print('non-clean:',sum(1 for c in d if not c.get('clean')));ours=[(c['code'],[i for i in c.get('issues',[]) if any(k in i.get('path','') for k in ['your','file','slugs'])]) for c in d if not c.get('clean')];print('OUR-FAIL:',len(ours))"
```

## Pitfalls
- **MSYS `/c/...` paths for file tools**: `write_file`/`patch` may resolve `/c/...` as `C:\c\...`. Use native `C:\Users\Tiger\Vault\...` for file tools; terminal accepts either.
- **CK04**: capital letters in any filename. Always lowercase-kebab.
- **CK11**: `platform:`/`creator:` target page missing → create it (Platform page usually exists; creator Person/Company usually does not).
- **Don't skip the audit** — pre-existing debt must be reported separately, not hidden and not blamed on the ingest.
- **gbrain visibility**: vault is git-backed; new artifacts invisible to `gbrain sync` until committed. Don't claim queryable without a commit + positive `gbrain query`.

## Relationship to vault-ingestion
This skill is the optimized mechanical layer under `vault-ingestion`. Load `vault-ingestion` for full governance, approval gates, and report templates; use this skill's techniques for faster execution. Never trade quality for speed.
