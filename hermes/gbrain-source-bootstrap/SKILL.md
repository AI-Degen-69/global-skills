---
name: gbrain-source-bootstrap
description: Use when creating or reusing a dedicated artifacts repo that gbrain should index.
---

# gbrain-source-bootstrap

Use this when wiring a local artifacts repo into gbrain, or when `gstack-artifacts-init` / `gstack-gbrain-source-wireup` appear to half-succeed and you need to separate Git transport problems from embedding-provider problems.

## When to use

- A workflow creates or reuses a dedicated artifacts repo that gbrain should index.
- The machine is authenticated to GitHub via `gh` over HTTPS rather than SSH keys.
- `gstack-gbrain-source-wireup --strict` fails during `gbrain sync` and you need to determine whether the failure is transport, database, source-registration, or embedding-provider configuration.
- The database URL points at a Supabase/PgBouncer pooler on port `6543` and the operator needs to know which notices are benign.
- Heavy gbrain migrations or dream-cycle cleanup stall, wedge, or time out against a pooled Supabase URL and you need to decide whether to switch to the direct `5432` endpoint.
- A late migration that writes back into the Git-backed source fails repeatedly with no clear error and you need to check git-dirty refusal before blaming the database.

## Core idea

Treat source bootstrap as three independent layers and verify them in this order:

1. **Git transport** — can the machine initialize and push/pull the artifacts repo using the auth actually present on the box?
2. **Source registration** — did gbrain register the worktree as a source at the expected path?
3. **Embedding** — only after 1 and 2 pass, care about whether the configured embedding provider has its API key and can complete the embed phase.

This prevents misdiagnosing an embedding-key failure as a broken database URL or broken Git bootstrap.

## Procedure

### 1) Normalize GitHub transport to match auth reality

On Windows hosts that use GitHub CLI HTTPS auth, force GitHub SSH-form remotes to rewrite to HTTPS before running the artifacts initializer:

```bash
gh auth setup-git >/dev/null 2>&1 || true
GIT_CONFIG_COUNT=1 \
GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf \
GIT_CONFIG_VALUE_0=git@github.com: \
bin/gstack-artifacts-init --remote https://github.com/<owner>/<repo> --url-form-supported false
git -C ~/.gstack config url.https://github.com/.insteadOf git@github.com:
```

Why: some initializers print a canonical HTTPS remote but still derive an SSH-form push target. If the box is authenticated through `gh` but has no SSH key configured, connectivity checks can fail for the wrong reason.

### 2) Run source wireup with the intended database URL

Use the final, actual gbrain database URL and run the wireup strictly.

```bash
bin/gstack-gbrain-source-wireup --strict --database-url '<postgres-url>'
```

Interpret the result in layers:
- If it fails before source creation, fix Git/worktree/database issues first.
- If it creates the source and only then fails in `gbrain sync`, inspect whether the failure is really just embedding setup.

### 3) Verify plumbing without embeddings

If `gbrain sync` complains that the embedding model requires a missing API key, verify the source/database/worktree path independently:

```bash
gbrain sync --repo ~/.gstack-brain-worktree --no-embed --yes
```

Success means the core plumbing is correct even if embeddings are deferred.

### 4) Finish embeddings separately

Once the non-embed sync succeeds, either:
- set the missing provider key, or
- switch `embedding_model` to a provider that is actually configured,
then run a normal sync/embed pass later.

### 5) If heavy migrations stall on Supabase poolers, move to the direct `5432` host

If `gbrain apply-migrations --yes`, `gbrain doctor`, or `gbrain dream` keep hanging around graph/takes/facts backfills while the database URL uses a Supabase/PgBouncer-style pooled endpoint, test the direct Postgres host on port `5432` before doing anything more invasive.

Pattern:
- Pooler / transaction-mode URLs can be fine for light traffic yet wedge or crawl on long-running migration phases.
- The durable fix is usually **not** "retry harder" — it is switching `database_url` from the pooled endpoint to the direct `db.<project>.supabase.co:5432` endpoint with a known-good password.
- Preserve a recovery handle first (copy the config file or back up the prior URL), then patch the live config.

Recommended sequence:
1. Confirm which Supabase project the current brain already uses; do **not** switch projects blindly and orphan the existing pages.
2. Independently verify the direct `5432` credentials outside gbrain.
3. Back up the current config file.
4. Patch `database_url` to the direct `5432` URL.
5. Re-run `gbrain doctor --fast` and the blocked migration.
6. If one heavyweight phase is idempotent but slow (for example link extraction), let it finish once, then re-run the full migration chain with a longer timeout.

### 6) If the last migration writes into the Git-backed source, check for dirty-tree refusal

Late migrations that fence DB facts back into markdown can fail deterministically even when the database is healthy. Before blaming Supabase, inspect whether the source worktree itself is dirty.

Pattern:
- Some gbrain migrations refuse to write into a Git-backed source when `git status --porcelain` is non-empty.
- This can present as a repeatable `status=failed` with little or no surfaced detail from the orchestrator.
- The correct diagnosis is: **database fixed, writeback blocked by source cleanliness policy**.

Recommended sequence:
1. Check the source `local_path` and run `git -C <path> status --porcelain`.
2. If the tree is dirty, stop treating the failure as a DB or provider problem.
3. Ask the user whether to commit, stash, or intentionally skip that migration.
4. Only re-run the writeback migration after the tree is clean.

This is especially relevant for fact-fencing migrations that move DB-only facts into markdown pages.

### 7) On Windows/MSYS, treat intermittent `spawnSync git ETIMEDOUT` during HEAD verification as a retry-class fault

If `gbrain sync`, `gbrain doctor --fast`, or a queued source sync records an unresolved failure like:

- `path: <head>`
- `error: git HEAD verification failed: spawnSync git ETIMEDOUT`
- `code: UNKNOWN`

then the immediate lesson is **not** "the repo is broken". This pattern can come from a cold or flaky MSYS/Node `execFileSync('git', ...)` spawn during `rev-parse HEAD`, even when a manual `git rev-parse HEAD` is fast.

Recommended sequence:
1. Verify the repo is otherwise healthy with direct git commands (`git rev-parse HEAD`, `git status --porcelain`) before blaming repo state.
2. Read the sync implementation and confirm the failing path is the HEAD-verification wrapper, not parse/import logic.
3. Patch the local `git()` helper used by sync to retry timeout-class failures (`ETIMEDOUT` / timed-out `SIGTERM`) with short backoff before surfacing failure.
4. Re-run a real source sync and look for a positive signal like a logged retry followed by `EXIT=0` and a successful sync summary.
5. Only after a post-patch sync succeeds should you clear stale `<head>` sentinel failures from the failure ledger.

Important distinction:
- The durable lesson is the **retry pattern around flaky git spawn on Windows/MSYS**, not a blanket claim that gbrain sync is broken.
- If the patch proves itself by converting a timed-out `rev-parse HEAD` into a successful sync on retry, treat older `<head>` sentinel entries as historical noise and acknowledge them without deleting audit history.

### 8) For Ollama-backed chat on `dream` / `autopilot`, verify real chat and guard against silent skip

If gbrain automation is using an Ollama-compatible chat endpoint (local Ollama or a cloud OpenAI-compatible host exposed through the `ollama` recipe), do not stop at "config parses" or `gbrain doctor` alone.

Pattern discovered on Windows gbrain v0.42.x:
- gbrain has an `ollama` provider, but **not** a separate `ollama-cloud` recipe.
- Cloud-hosted Ollama must therefore be wired by keeping `chat_model` in `ollama:<model>` form and pointing the Ollama base URL at the cloud endpoint.
- For `dream` / `autopilot`, an unreachable chat model may **gracefully skip** the proposal cycle and still exit 0, surfacing JSON like `"status": "skipped"` and/or `"phases": []` rather than a loud auth/transport failure.
- A bare `chat_fallback_chain` is not sufficient when the command exits successfully after skipping the proposal phase.

Recommended sequence:
1. Confirm the actual provider reality before patching config: if the source shows only the `ollama` recipe, keep the model in `ollama:<model>` form and route cloud access through the Ollama base URL / API key.
2. Add a **direct chat probe** that curls the cloud endpoint with the intended model and fails non-zero on unauthorized or missing chat response.
3. For automation commands that may skip quietly, wrap `gbrain dream` / `autopilot` in a script that:
   - runs the cloud attempt first,
   - inspects the JSON output for the skip signature (`"phases": []` or `"status": "skipped"`),
   - temporarily switches `chat_model` to a locally loaded fallback model,
   - re-runs locally,
   - restores the original cloud model afterward.
4. When the fallback model differs from the cloud model, switch `chat_model` during the local attempt; do not assume the cloud model name exists locally.
5. In cron jobs, run the chat probe **before** the dream step and report distinctly when cloud chat is down, because otherwise the job may appear to "work" while producing no proposal phases.

Verification:
- Positive cloud proof = a real `dream`/`autopilot` run yields a non-empty `phases` array including proposal work (for example `propose_takes`), not merely a zero exit code.
- Positive fallback proof = a forced-skip/mock test shows the wrapper logging the fallback banner, producing proposal phases locally, exiting 0, and restoring `chat_model` to the cloud value afterward.
- Positive probe proof = the probe exits 0 on a real chat response and non-zero on a bad key / unreachable cloud.

## Expected signals

### Benign / informational

- `Prepared statements disabled (PgBouncer transaction-mode convention on port 6543)`
  - This is informational when using a transaction-pooler style Postgres endpoint.
- `Detached HEAD ... skipping git pull. Syncing from local working tree.`
  - Normal for a detached worktree used as a gbrain source.
- `0 markdown files`
  - Not a bootstrap failure by itself; it only means that repo currently has nothing importable under the active sync strategy.

### Real blockers

- Git connectivity failing because the tool is effectively trying SSH on a machine only authenticated for HTTPS.
- Source removal/re-add loops caused by path mismatch.
- Embedding-provider errors that are mistaken for source-registration failure.
- A repeatable timeout with **no successful retry path** after patching the HEAD-verification wrapper. That indicates a real git-process or environment issue, not just the common Windows/MSYS flake.

## Pitfalls

- Do not treat an embed-time API-key error as proof that the database URL or source registration is wrong.
- Do not assume a printed HTTPS remote means future pushes will use HTTPS; verify whether Git still rewrites or stores a push target in SSH form.
- Do not chase the PgBouncer prepared-statements notice as a bug when using Supabase session poolers on `6543`; it is often expected.
- Do not keep re-running heavy migrations on the pooled endpoint once you have evidence they stall there; test the direct `5432` host instead.
- Do not interpret a late writeback migration failure as a DB outage until you have checked whether the Git-backed source has uncommitted changes.
- Do not auto-commit a dirty user vault just to satisfy a migration. Surface commit vs stash vs skip explicitly.
- Do not memorialize a one-off `spawnSync git ETIMEDOUT` as "gbrain is broken on Windows". Capture the retry/verification pattern instead.
- Do not assume a zero exit code from `gbrain dream` / `autopilot` proves the chat model worked when using Ollama-compatible providers; check for non-empty proposal phases.
- Do not invent a separate `ollama-cloud` provider in gbrain config if the installed gbrain source only exposes the `ollama` recipe.
- Do not trust `chat_fallback_chain` alone to save `dream` / `autopilot` when unreachable chat causes a graceful skip; add output-aware fallback and a direct chat probe.
- Do not leave a local fallback wrapper on the local model after completion; restore the cloud `chat_model` after the fallback attempt.
- Do not store raw provider keys in skills, git, or memory; keep them in env/config only.
- Do not delete historical `<head>` failure records once the retry fix works; acknowledge them while preserving audit history.

## Verification checklist

- `gh auth status` shows an active GitHub account if using GitHub CLI auth.
- The artifacts init completes and the persistent Git rewrite is present in `~/.gstack` when HTTPS auth is intended.
- `gstack-gbrain-source-wireup --strict` creates the expected source/worktree.
- `gbrain sync --repo ~/.gstack-brain-worktree --no-embed --yes` succeeds before you spend time on embedding setup.
- For stalled Supabase brains, the direct `5432` URL is verified independently before patching config, and `gbrain doctor --fast` becomes responsive afterward.
- For failed facts→markdown migrations, `git -C <source-local-path> status --porcelain` is checked before retrying.
- For Windows/MSYS `<head>` timeout cases, a post-patch sync shows a retry log and then finishes `EXIT=0` without recording a fresh open `<head>` failure.
- For Ollama-compatible cloud chat automation, a direct probe succeeds against the intended endpoint/model, and a real or mocked fallback test proves that `dream`/`autopilot` does not silently succeed with `phases: []`.
- Only after the above passes do you configure embedding keys/models.

## Support files

- `references/windows-github-auth-and-no-embed-verification.md` — concrete notes on the Windows HTTPS-auth rewrite and the non-embed verification path.
- `references/supabase-direct-migrations-and-dirty-tree-refusal.md` — migration recovery pattern for pooled-vs-direct Supabase URLs and git-dirty writeback failures.
- `references/windows-msys-git-head-timeout-retry.md` — Windows/MSYS `<head>` timeout diagnosis, retry patch pattern, and stale-ledger acknowledgement workflow.
- `references/ollama-cloud-fallback-and-chat-probe.md` — Ollama-cloud via gbrain's `ollama` provider, skip-signature detection, wrapper fallback pattern, and probe-first cron guidance.
