# Retiring indexed vault pages: cleanup pattern

Use when a vault note or folder was intentionally removed from disk but gbrain search still returns the old slug.

## Short recipe
1. Delete the markdown in the Vault repo.
2. Commit the deletion so the source walker sees it against the committed tree.
3. Run `gbrain sync --source <source-id>`.
4. Verify with a search that should uniquely hit the retired page.
5. If the slug still appears in search, run `gbrain delete <slug>`.
6. Verify search no longer returns that slug.

## Why this exists
- Source `page_count` can drop correctly while search still returns a lingering page.
- Query cache can show `0 rows` and the ghost can still remain.
- The safe fix is **soft-delete via gbrain**, not DB surgery and not immediate recreation at the same slug.

## Session note that produced this reference
Retiring `Vault/Hermes/memory/` exposed a ghost-page path:
- filesystem folder deleted
- source page_count dropped (`1091 -> 1085`)
- query cache reported `0 rows`
- search still returned `hermes/memory/index`
- `gbrain delete hermes/memory/index` removed it from search safely

## Verification standard
Positive proof is search behavior, not just counters:
- good: search returns no match for the retired slug
- weak: page_count changed
- weak: cache rows are zero

## Cron/autopilot audit pitfall
- Historical cron output under `cron/output/<job-id>/...` can embed an **old prompt snapshot** that no longer matches the live job.
- Before editing or blaming a recurring cleanup job, inspect the live scheduler entry in `cron/jobs.json` and read `jobs[].prompt` for the job's `id`.
- Do not treat stale wording inside an old run log as current config. Verify the live prompt first.
- If the prompt says an MOC/capture step should "skip if file missing", a deleted helper page is not a resurrection risk by itself.

## Safety
- `gbrain delete` is a 72h soft-delete; it hides the page from search and list/get by default.
- Do not recreate the same slug during that window.
- If you actually need replacement content, publish it at a new slug.