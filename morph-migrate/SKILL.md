---
name: morph-migrate
description: Migrate this app's LLM calls onto a Morph open model (GLM-5.2), either fully or as a scored 5% production trial. Use when the user wants to move a provider/model to Morph, A/B a Morph model against their incumbent, or run a canary on real traffic.
metadata:
  author: morph
  version: "0.1.0"
  argument-hint: <full | 5% trial>
---

# Morph Migrate

I migrate this app onto a Morph open model. Morph serves GLM-5.2 (`morph-glm52-744b`)
on an OpenAI- and Anthropic-compatible API at `https://api.morphllm.com`, so the
migration is usually a base URL + model swap, not a rewrite. I never change the
app's behavior beyond the model call, and I keep a one-flag rollback the whole way.

I work in four phases and I stop for approval before I touch any code.

## Phase 1 — Explore

Map how this app calls an LLM before proposing anything. Fan out:

- Find LLM call sites and the client construction (SDK, base URL, model id).
  Search for `openai`, `anthropic`, `chat.completions`, `messages.create`,
  `baseURL`/`base_url`, `model:`/`model=`.
- Identify the current provider and model, and where the API key comes from.
- Check whether Morph is already wired up: look for a `MORPH_API_KEY` in the
  environment/`.env` **without printing its value** (grep for the name only).
- Note the language/framework and how the app builds (so I can verify later).

Report the call sites, the incumbent provider+model, and the config surface as a
short list. No edits in this phase.

## Phase 2 — Choose & plan

Ask exactly:

> **Full migration to GLM-5.2, or a 5% production trial?**

Then write a concrete plan for the chosen path — the exact files and lines I'll
touch, the env flag that flips it back, and how I'll verify. Show the plan and
**get explicit approval before editing.** Do not edit in this phase.

## Phase 3 — Execute

### Full migration

- Repoint the LLM client at Morph: `baseURL` → `https://api.morphllm.com`, model
  → `morph-glm52-744b`, key → `MORPH_API_KEY`.
- Keep the old path behind a flag so a revert is one env var, e.g.
  `LLM_PROVIDER=morph|incumbent` (default to what preserves current behavior if
  the flag is unset, so an un-set deploy is safe).
- Change nothing else — no prompt edits, no control-flow changes.

### 5% production trial (canary)

- Add a minimal traffic split keyed off `MORPH_CANARY_PERCENT` (default `5`):
  that percentage of calls route to Morph (`morph-glm52-744b`), the rest stay on
  the incumbent, unchanged. Decide per-request (a hash or RNG at the call site);
  don't reshape the surrounding code.
- Score **both arms** with Reflex so the comparison is apples-to-apples. In the
  app's own code, after each completed turn (Morph arm *and* incumbent arm),
  `POST https://api.morphllm.com/v1/reflex/predict` with header
  `Authorization: Bearer $MORPH_API_KEY` and body
  `{"model":"<reflex>","text":"<the turn's text>"}`, where `<reflex>` is a failure
  mode worth watching (`stuck-in-a-loop` is a good default; pick one or two that fit
  this app). Read the predicted label from the `classes` array in the response, and
  **record it next to which arm served the turn** (`morph` | `incumbent`) — a log
  line, a metrics counter, whatever this app already uses.
- This scoring runs in the app at request time, so it's a plain HTTPS call, **not**
  the coding-agent `reflex_predict` MCP tool. The `model` field is the reflex name,
  not the LLM; the arm is your own tag. Reflex scoring is observational — it must
  never gate or alter a response.

Then verify the build compiles. **Max 2 fix attempts**; if it still fails, stop
and report rather than thrashing.

## Phase 4 — Verify

- Trigger exactly one request and confirm it reached Morph (assert the response,
  or check the base URL/model actually used).
- Confirm the Reflex scoring is recording: check that per-arm labels are landing in
  the log/counter you wired in Phase 3. Then **tally the recorded labels by arm** and
  show the failure-rate comparison directly (Morph vs incumbent) from where the app
  logged them. These are live predicts, so read them from the app's own sink — the
  Morph dashboard's `reflex_summary` only rolls up *traced* turns, not raw
  `/v1/reflex/predict` calls, so don't rely on it for the trial's numbers.
- End with the upgrade script for the user:
  > **When the comparison looks clean, tell me "go to 100%".** I'll flip
  > `MORPH_CANARY_PERCENT=100` (or set `LLM_PROVIDER=morph`) and drop the split.

## Guardrails

- Observational-safe: never let Reflex scoring change a response or block a call.
- Never change control flow beyond the traffic split. No prompt or tool changes.
- Keep the one-flag rollback (`LLM_PROVIDER` / `MORPH_CANARY_PERCENT`) intact.
- Never print the API key. Reference `MORPH_API_KEY`; check for its presence by
  name, never echo its value.
- **Codex apps:** Codex speaks only the OpenAI Responses API, and Morph's chat
  models serve Chat Completions/Messages, not Responses. Do not fake an env swap.
  Front Morph with a Responses gateway (LiteLLM) and point Codex's `base_url` at
  it — see `docs/sdk/components/coding-agents.mdx`.
