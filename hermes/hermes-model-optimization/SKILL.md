---
name: hermes-model-optimization
description: Use when tuning Hermes model slots (main vs auxiliary) for cost/quality.
# Reference index
# - references/auxiliary-title-generation-verification.md: verify Title generation auxiliary routing; manual session renames do not exercise the auxiliary model.
# - references/fallback-provider-verification.md: verify Hermes fallback provider parsing and live failover activation; includes the dict-shape requirement for `fallback_providers` and a temp-home smoke test recipe.
triggers:
  - User asks to set up, optimize, or review Hermes models
  - User wants value-for-money model selection
  - User mentions "auxiliary models" setup
  - User asks about OpenRouter model pricing for Hermes
  - New generation of models released, user wants to re-evaluate
---

# Hermes Model Optimization

Two kinds of model slots in Hermes:
- **Main model** — every user message, tool-call loop, streamed response
- **Auxiliary models** — 11 side-job slots the agent offloads: Vision, Web Extract, Compression, Skills Hub, Approval, MCP, Title Gen, Triage Specifier, Kanban Decomposer, Profile Describer, Curator

Every auxiliary slot defaults to `auto` (uses main model). Override individual slots to save cost on mechanical side-work that doesn't need reasoning-model prices.

## 1. Research Phase — Find the Best Models

Before configuring anything, query OpenRouter's model list to get current pricing and capabilities:

```bash
# List all available models (no auth needed for the public endpoint)
curl -s "https://openrouter.ai/api/v1/models" | python3 -c "
import json,sys
data=json.load(sys.stdin)
for m in data['data']:
    n=m['name'].lower()
    # Filter for aux-suitable models (cheap, fast, capable)
    if any(t in n for t in ['flash-lite','flash','nano','mini','maverick','scout','qwen3.7-plus','step-3.7']):
        p=m.get('pricing',{})
        print(f\"{m['id']:55s} prompt={p.get('prompt','?'):>12s} comp={p.get('completion','?'):>12s} ctx={m.get('context_length',0)}\")
"
```

Key metrics to compare:
- **Prompt/completion price per 1M tokens** (from the pricing field)
- **Vision support** — check `architecture.input_modalities` for `image`
- **Context length** — most aux tasks don't need huge context, but Compression and Curator benefit from 100K+

A snapshot of current pricing lives in `references/openrouter-pricing.md` — load it first before re-researching to save time.

## 2. Model Selection Principles

### Subscription providers beat paid OpenRouter routing
If the user has a **paid subscription** to a model provider (OpenAI Codex, Nous Portal, Groq, etc.), route aux and delegation to that provider **before** reaching for OpenRouter paid models. Subscription value is "free at the margin" versus $0.10–$2.50/M on OpenRouter. The selection order is:
1. Subscription providers first (OpenAI Codex → Nous Portal → Groq → …)
2. OpenRouter free-tier models second (`:free` suffix)
3. OpenRouter paid models last

### Vision → Google Gemini Flash (when not on a subscription vision plan)
Google dominates image analysis. `google/gemini-2.5-flash` is the best value — excellent vision at $0.30/$2.50 per 1M tokens. **Substitution rule:** if the chosen subscription provider supplies a vision-capable model at zero marginal cost (e.g. `o4-mini` on Codex), use it instead — the price differential (free vs $0.30/M) dominates any quality gap for routine auxiliary vision tasks.

### Text-only aux tasks → cheapest capable model
Tasks like Title Gen, Approval, Skills Hub, Triage Specifier, Profile Describer need basic LLM capability but zero reasoning. The cheapest model with 100K+ context wins. Current best: `google/gemini-2.5-flash-lite` at $0.10/$0.40.

### MCP → leave on auto
MCP tool routing is tightly coupled to the main model's behavior. Overriding can cause tool-selection mismatches.

### Curator → consider the stronger Flash variant
Curator runs skill-usage review passes that can run for minutes. It needs enough intelligence to evaluate skill quality. Flash (not lite) is worth the small price premium here.

## 3. Configuration

Use `hermes config set` — it auto-routes to the right config file.

**Subscription-first pattern** (all 10 aux slots + delegation via subscription before OpenRouter):

```bash
# Set aux model provider (e.g. openai for Codex subscription)
# Then override each slot that should not be on auto:
for slot in vision web_extract compression skills_hub approval title_generation \
            triage_specifier kanban_decomposer profile_describer curator; do
  hermes config set auxiliary.$slot.provider openai
  hermes config set auxiliary.$slot.model o4-mini   # or whatever subscription default is
done

# Delegation (subagent model)
hermes config set delegation.provider openai
# Leave model blank to inherit provider default, or set explicitly:
# hermes config set delegation.model o4-mini

# MCP — leave untouched (auto)
```

Verify with:
```bash
hermes config | grep -A 20 "Auxiliary"
```

Or read the config file directly:
```bash
cat ~/.hermes/config.yaml | grep -A 3 "auxiliary:"
```

## 4. Cost Discipline

Aux models run side-jobs thousands of times. The cost difference between running them on a reasoning model vs a flash model compounds fast:

| Task | Main model (DeepSeek v4 / Opus) | Flash-lite | Savings |
|------|------|------|------|
| Title Gen (500 tok) | $0.005/call | $0.0002/call | **25x** |
| Compression (8K tok) | $0.08/call | $0.003/call | **27x** |
| Vision (image+2K tok) | $0.02/call | $0.005/call | **4x** |
| Curator (30K tok) | $0.30/run | $0.012/run | **25x** |

On subscription providers, the marginal cost drops to **zero** — which is the real reason to prefer subscriptions for high-volume aux work.

## 4b. Delegation / Subagent Model

Subagent runs are full agent loops and can burn significant tokens. Route delegation to the same subscription-first provider:

```bash
hermes config set delegation.provider openai   # or nos, groq, etc.
# model: leave blank → inherits provider default (Codex subscription default)
# or pin explicitly:
# hermes config set delegation.model o4-mini
```

Verify:
```bash
hermes config | grep -A 8 "delegation:"
```

## 4c. Fallback Provider Sanity Checks

When the user asks whether Hermes will **fall back correctly**, do not trust `config.yaml` at a glance. Verify the chain at two levels:

1. **Parser level** — run `hermes fallback list`.
   - If Hermes says `No fallback providers configured`, the runtime will not fall back no matter what the YAML appears to say.
2. **Live failover level** — force a one-shot primary failure in a **temporary `HERMES_HOME`** and inspect the logs for actual activation.

Critical config shape rule:

```yaml
fallback_providers:
  - provider: openrouter
    model: nvidia/nemotron-3-super-12b-a12b:free
```

Do **not** use string shorthand like:

```yaml
fallback_providers:
  - openrouter:nvidia/nemotron-3-super-12b-a12b:free
```

The parser only accepts dict entries with `provider` + `model`. If the entry is a string, `hermes fallback list` will report an empty chain and failover will never activate.

Safe verification pattern:
- Clone `.env`, `auth.json`, and a minimal `config.yaml` into a temp `HERMES_HOME`.
- Point the primary provider at a deliberately dead endpoint (for example `http://127.0.0.1:9/...`).
- Keep the fallback entry valid.
- Run a one-shot `hermes chat -q ...` there.
- Inspect `hermes logs agent` in that temp home for lines like `Fallback activated: ...`.

Interpretation rules:
- If the primary fails and logs show `Fallback activated`, the engine works.
- If activation happens but the request still ends in a provider 400, the **fallback model ID is wrong**, not the fallback mechanism.
- `hermes fallback list` is the fastest parser sanity check before any live smoke test.

Verify:
```bash
hermes fallback list
hermes logs agent --since 5m --level INFO -n 200
```

## 5. Re-evaluation Cadence

Revisit auxiliary model assignments when:
- A new generation of Flash/Lite models drops (Google releases frequently)
- OpenRouter adds new free-tier or drastically cheaper models
- User switches main model to a different provider
- Monthly token spend looks unexpectedly high

## Pitfalls

- **`fallback_providers` must be dict entries, not strings** — `hermes fallback list` is the authoritative parser check. If it says no fallbacks are configured, the YAML is inert.
- **A fallback activation can still fail on a bad model ID** — distinguish `Fallback activated: ...` in logs from the downstream provider response. Activation proves the mechanism; a 400 after activation means the fallback target itself is invalid.
- **Don't override MCP** — tool routing breaks when the aux model has different tool-calling behavior than the main model.
- **Don't use text-only models for Vision** — `meta-llama/llama-4-maverick` has vision but some cheap models don't. Always check `input_modalities`.
- **Don't overthink it** — the price gap between flash-lite and flash is $0.20/M. Unless Curator or Compression is running constantly, the difference is cents per month. Pick one consistent model for all text slots and move on.
- **`hermes config set` routes API keys to `.env`, everything else to `config.yaml`** — never hand-edit the config to add provider credentials.
- **Subscriptions are not infinite** — Codex/Portal/Groq subscriptions have rate limits. For high-volume parallel subagent runs (5+ concurrent children on a busy day), monitor for quota hits and fall back to OpenRouter `:free` models for non-critical aux slots if needed.
- **Delegation model blank ≠ no model** — leaving `delegation.model` empty makes Hermes use the provider default, which is usually fine but worth verifying the first time with `hermes config | grep -A 8 "delegation:"`.
