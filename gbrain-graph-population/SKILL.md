---
name: gbrain-graph-population
description: Use when repairing gbrain's wikilink edge graph or de-orphaning notes.
---

# gbrain graph population & link-refresh

Use when: a vault note shows as a gbrain "orphan" (no inbound links) and you want to wire it
into the graph via an Obsidian `[[wikilink]]` MOC/index page, or when you edited a page and
gbrain's backlinks/orphan count didn't update.

## How the resolver actually matches (gbrain v0.42.x)
- The edge graph is REAL. `gbrain backlinks <slug>` / `gbrain links <slug>` show `wikilink-resolved`
  edges built by the **sync importer's link pass** (NOT the `extract` LLM step — `gbrain extract --stale`
  reporting "0 links" is normal; it's about the LLM enrichment, not wikilinks).
- Link text resolves to a page by **slug basename** = the filename stem, hyphenated
  (e.g. `[[article]]` → `types/article`, `[[13-06-2026-headroom-...-report]]` → that slug).
  - Full slug paths (`[[types/article]]`) do NOT resolve. Title text works ONLY for some pages
    (`[[Eugene Fama]]` → `finance/wiki/eugene-fama` works; `[[eugene-fama]]` does NOT, because the
    slug has a hyphen the link lacks). Prefer slug-basename form for reliability.
  - Duplicate-titled pages (e.g. 3 auto-generated reports all titled "Post-Ingestion Report")
    collide — give each a UNIQUE title so its `[[basename]]` link disambiguates.
- `gbrain backlinks`/`links`/`graph` intermittently throw `CONNECT_TIMEOUT` to Supabase — a transient
  DB flake, NOT an empty graph. Retry; don't conclude the graph is broken from one `[]`.

## CRITICAL: sync does NOT re-extract links for unchanged pages
- `gbrain sync` (even `--full`) SKIPS the link-extraction pass for pages already embedded. Editing a
  file + `git commit` + `gbrain sync` will NOT refresh that page's wikilink edges.
- Wikilink edges are only (re)built on a **FRESH page import**.

## Force a link-refresh on a LIVE page (safe path)
`gbrain put <slug> < file.md`   (re-imports the page; link extraction runs). Do NOT delete first.

## TRAP: `gbrain delete` then `put`/`capture` CANNOT revive a soft-deleted page
- `delete` only soft-deletes; the row lingers 72h and is recoverable via `restore_page`. There is NO
  `undelete`/`--hard` flag and no manual purge. `put`/`capture` on a soft-deleted slug return
  `created_or_updated` but then `page_not_found_after_write` — the page stays deleted and its edges
  double-count in backlinks.
- If you soft-delete a page by mistake: the only clean fix is to **recreate it at a NEW slug**
  (e.g. rename `Hermes/Genuine Orphans Index.md` → `Hermes/Orphan Index.md` = slug `hermes/orphan-index`)
  and `capture`/`put` the new slug. The old slug auto-purges in 72h.

## Retiring indexed vault pages or whole folders
- Deleting markdown from the Vault filesystem is **not enough** when gbrain already indexed those pages.
  Commit the deletion first, then run `gbrain sync --source <source-id>` so the source walker sees the
  removal against the committed tree.
- `page_count` dropping and query-cache stats showing `0 rows` are useful signals, but **not proof** the
  page vanished from live search. Verify with a search that should uniquely hit the retired page.
- If search still returns the slug after the filesystem delete + sync, use `gbrain delete <slug>` to
  hide the lingering page row safely; it remains recoverable for 72h and autopilot later hard-purges it.
- Do **not** recreate the same slug immediately after `delete`; that falls into the soft-delete trap above.
  If the goal is retirement, leave it deleted. If the goal is replacement, write the replacement at a new slug.

## Workflow (de-orphan N notes via a MOC)
See `references/relink-and-soft-delete-notes.md` for a condensed recovery matrix (basename-link examples, soft-delete symptoms, ghost-edge checks, Windows capture vs pipe guidance) and `references/retiring-indexed-vault-pages.md` for retirement-specific cleanup.

1. Build `Hermes/Orphan Index.md` listing every target as `- [[<slug-basename>]] — \`path.md\``.
   Keep prose/short links (avoid list+code-span if a page ever fails to parse — body prose is safest).
2. `git add -A && git commit -m "..."`  (durable recovery handle).
3. `gbrain capture --file "Hermes/Orphan Index.md" --slug hermes/orphan-index`
   (capture reads the file as a Buffer and adds write-through; more reliable than pipe `put` on Windows).
4. Verify: `gbrain backlinks <each-target-slug>` → expect `inbound >= 1`; `gbrain orphans --count`
   should drop by the number of formerly-orphaned targets.
5. If a target still shows 0: check its title is unique and the link uses its slug-basename.

## Pitfalls
- `gbrain list --deleted` is unreliable (returns a full page listing, not just deleted) — don't trust
  it to enumerate soft-deleted pages. Confirm a specific slug with `gbrain get <slug> --include-deleted`.
- `gbrain put --file` via stdin pipe can hit a ~45KB Windows pipe-buffer limit; use
  `gbrain capture --file PATH --slug SLUG` instead for any non-trivial file.
- Historical cron output can embed an **old prompt snapshot**. When validating autopilot cleanup behavior,
  inspect the live job in `cron/jobs.json` (match on `jobs[].id`) before treating a logged prompt as current.
- Never guess the resolver matches titles or full paths — it matches slug basename.

## Verification
- Positive proof = `gbrain backlinks <target>` returns a JSON array with `from_slug` = your MOC slug and
  `link_source: "wikilink-resolved"`. Absence of errors is NOT proof.
- `gbrain orphans --count` before/after should differ by the de-orphaned count.
- If backlinks show BOTH the live MOC slug and an old soft-deleted slug, the old row is still in its 72h purge window; verify the new slug covers every target, then wait for purge instead of re-deleting/recreating again.
- If `gbrain get <old-slug> --include-deleted` later flips from recoverable output to `page_not_found`, that means the ghost slug has fully purged — expected, not a new failure.
