---
name: vault-inbox-selection-and-ordering
description: Use when the user refers to inbox files by position (first/next/latest) to ingest.
---

# Vault Inbox Selection and Ordering

## When to use
- The user says things like "ingest the first two files", "do the next one", "take the latest item", or otherwise refers to inbox items by relative position rather than exact filename.
- The task is about Vault ingestion or inbox triage.
- The user is correcting which files count for ingestion scope.

## Core rule
For Robert, **INGEST refers only to files in `_Inbox/` unless he explicitly says otherwise**.
Do not interpret "first files" as files from the whole Vault, a domain folder, or search results outside `_Inbox/`.

## Ordering rule
Interpret relative position words (`first`, `second`, `next`, `last`, `latest`, `oldest`) against the **user's intended inbox ordering**, not whatever order a tool happens to return.

Default priority for resolving order:
1. If Robert states his ordering convention, use that.
2. If the UI/workspace context indicates a visible sort order, mirror that order.
3. If neither is explicit, state the ordering basis you are using before acting.

For this user, a key learned preference is:
- When Robert says the inbox is arranged **by date ascending**, then "the first two files" means the **oldest two inbox items in that visible ascending order**.

## Procedure
1. Restrict candidate files to `Vault/_Inbox/`.
2. Determine the active ordering basis.
3. Map positional language to concrete filenames.
4. Echo the exact filenames you believe are in scope when ambiguity exists.
5. Only then run the ingestion workflow.

## Pitfalls
- Do **not** use cross-vault search results as the meaning of "first files" for ingestion.
- Do **not** assume tool return order equals the user's visual order.
- Do **not** silently switch between newest-first and oldest-first.
- If the user corrects the ordering basis, treat that correction as authoritative for the current ingestion task.

## User-specific workflow preference
Robert may refer to inbox items from how they appear in his interface rather than from filesystem sort defaults. For ingestion requests, prefer **his stated visible order** over agent-chosen ordering.

## Reference
- See `references/inbox-ordering-example.md` for the concrete Hebrew/English correction pattern that established this rule.
