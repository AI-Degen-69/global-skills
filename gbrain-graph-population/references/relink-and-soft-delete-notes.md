# gbrain relink + soft-delete notes

Condensed operational notes from a full de-orphan / graph-repair session.

## Resolver behavior matrix

- Reliable form: `[[<slug-basename>]]`
  - `types/article` → `[[article]]`
  - `hermes/memory/projects/readme` → `[[readme]]`
  - `agent-skills/outputs/13-06-2026-headroom-better-stack-review-report` → `[[13-06-2026-headroom-better-stack-review-report]]`
- Do **not** rely on full slug paths like `[[types/article]]`.
- Human titles can work for some pages, but not consistently enough for repair work.
- Duplicate titles create ambiguous targets. Fix the title collision or use basename links.

## Re-import semantics

- `gbrain sync` updates source state but does **not** reliably rebuild wikilink edges for already-embedded pages.
- A fresh `put` / `capture` on the **source page containing the links** is what rebuilds the edges.
- If backlinks stay stale, verify you refreshed the linking page, not just the target page.

## Soft-delete trap

If you ran `gbrain delete <slug>`:
- `put` / `capture` can report success while the page remains soft-deleted.
- Symptom: `page_not_found_after_write` or `get <slug>` still missing while backlinks may still show ghost edges.
- Clean fix: create a **new slug** (rename the file, then `capture` / `put` the new slug).
- Old slug is expected to age out via purge; do not build follow-up work on reviving it.

## Windows/MSYS notes

- On Windows, `gbrain capture --file PATH --slug SLUG` is safer than piping a large file into `gbrain put`.
- Terminal commands may use `/c/...`, but file-writing tools should prefer native `C:\Users\...` paths.

## Verification pattern

1. Capture/put the linking MOC page.
2. Check `gbrain backlinks <target-slug>` for `from_slug=<your-moc>` and `link_source="wikilink-resolved"`.
3. Recheck orphan count after the live MOC is active.
4. If counts and backlinks disagree, inspect for ghost edges from a previously soft-deleted slug.
