---
name: vault-graph-hygiene
description: Use when improving wikilinks, duplicate handling, orphan reduction, and graph-quality issues in Robert's vault
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, links, duplicates, graph]
    related_skills: [vault-audit-fix, vault-ingestion, vault-retrieval]
---

# Vault Graph Hygiene

## Overview

This skill owns link quality, duplicate candidates, and orphan handling. It is conservative: improve real semantic graph structure, but do not turn hygiene into broad destructive graph surgery.

## When to Use

- An audit surfaces broken or low-quality links.
- A post-ingestion pass needs semantic links.
- Duplicate candidates or orphan notes need structured review.
- Robert asks for graph cleanup.

## Rules

- Link only real semantically meaningful targets.
- Do not create speculative missing notes just to satisfy a link idea.
- Do not add links inside code blocks, examples, or literal wikilink documentation unless the target really exists and the link is intended.
- Audit duplicate candidates first.
- Before acting on a large orphan count, classify the population: genuine vault notes vs indexed source-repo code/config vs auto-generated artifacts/skill outputs vs ghost entries with no backing file. Do not treat one headline orphan number as one cleanup queue.
- Verify how gbrain is deriving graph state before promising an orphan-count reduction. Check whether `graph`/`backlinks` are populated and whether `extract` is actually ingesting links; do not assume adding Obsidian `[[wikilinks]]` will move gbrain's orphan metric.
- When gbrain graph state matters, verify the **resolver form** before bulk editing. In the 2026-07-10 vault session, working links were usually slug-basename links (for example `[[article]]` → `types/article`), not full slug paths; some placeholders resolved only via normalized title form.
- If you need gbrain to rebuild wikilink edges for an already-indexed page, do not rely on `gbrain sync` alone. A fresh import can be required to re-run link extraction for that source page.
- Do **not** treat `gbrain delete` + `put` as automatically reversible. If a slug becomes soft-deleted and refuses to come back live, switch to a fresh slug and verify backlinks against the live replacement page instead of looping on re-put attempts.
- When validating `gbrain dream` / proposal generation as evidence that a chat model works, inspect the JSON body for real phases. `status: skipped` with `phases: []` can mean the model path was unavailable even though the command exited successfully.
- On Windows, treat case-only path differences (`Types/` vs `types/`) as dangerous. Verify the actual tracked path and filesystem behavior before deleting an apparent duplicate; case-insensitive filesystems can make a “stray duplicate” the canonical file.
- Merge, rename, or delete only with approval unless a live procedure explicitly authorizes a narrow safe fix.
- Run `vault-audit-fix` after graph edits.

See also `references/gbrain-orphan-triage.md` for the concrete triage pattern and Windows case-path pitfall, `references/gbrain-link-refresh.md` for the fresh-import/link-refresh behavior, and `references/gbrain-runtime-and-ghost-slug-notes.md` for soft-delete / ghost-slug behavior plus dream-model validation caveats.

## Common Pitfalls

1. Over-linking every mention instead of choosing meaningful graph edges.
2. Confusing duplicate suspicion with merge authorization.
3. Fixing one link issue while creating new unresolved links.
4. Treating orphan reduction as permission to invent pages.
5. Trusting gbrain's orphan headline without checking whether the count is mostly indexed code, generated artifacts, or ghost pages outside normal vault-note hygiene scope.
6. Assuming Obsidian `[[...]]` links automatically feed gbrain's orphan/backlink metrics; verify extraction behavior first.
7. Deleting a case-variant “duplicate” on Windows before confirming whether git and the filesystem treat it as the canonical tracked file.
8. Rewriting links in full-slug form (`[[finance/wiki/eugene-fama]]`) when gbrain is resolving by basename/title-normalization instead.
9. Expecting `gbrain sync --full` to refresh link edges for an already-indexed source page; in some flows only a fresh import re-runs wikilink extraction.
10. Assuming `gbrain delete` + `put` is a safe refresh loop; a soft-deleted slug can stay non-live and leave ghost backlink sources until purge, so recovery may require a fresh replacement slug.
11. Treating `gbrain dream` exit code 0 as proof the chat model worked; in tested flows an unavailable model can yield `status: skipped` and `phases: []` instead.

## Verification Checklist

- [ ] Added only semantic links to real targets.
- [ ] Did not create speculative missing pages.
- [ ] Classified any large orphan set before acting on it (human notes vs source/code vs generated vs ghost entries).
- [ ] Verified whether gbrain graph/backlink extraction is populated before claiming orphan-count impact.
- [ ] If link edges did not update, checked resolver form (basename/title vs full slug) and considered a fresh import for the source page.
- [ ] If a source page was soft-deleted during refresh experiments, verified the final backlinks point at a live replacement slug rather than trusting ghost deleted-slug sources.
- [ ] If `gbrain dream` was used as a model-health check, inspected JSON phase/status content rather than trusting exit code alone.
- [ ] Checked case-sensitive/case-insensitive path behavior before deleting or renaming apparent duplicates on Windows.
- [ ] Escalated merges, renames, and deletions when required.
- [ ] Reran `vault-audit-fix` after edits.
