# Hermes uptime monitor example

## Script-path rule
For Hermes cron jobs on this Windows host, prefer:
- `--script <name>.py`

Avoid preserving a literal scheduler path form like:
- `--script ~/.hermes/scripts/<name>.py`

> ⚠️ `check-uptime.py` was retired and moved to `hermes/scripts/.trash/` (2026-07-26); the original example referenced a script that no longer exists.

The scheduler resolves script names from its scripts directory; the relative form is the reliable default.

## Healthy/silent prompt contract
Use a deterministic script marker and a prompt that converts healthy runs into silence.

Example prompt:

```text
If the script reports OUTAGE DETECTED, summarize which services are down and suggest likely causes. If NO_ISSUES, respond with [SILENT].
```

Example healthy script output:

```text
NO_ISSUES
```

Expected cron artifact response:

```text
[SILENT]
```

## Example smoke-check shapes
Use cheap authenticated or local-real-path checks instead of fake health URLs.

### Local
- Ollama API: `http://127.0.0.1:11434/api/tags`
- Hermes UI: `http://127.0.0.1:9120/`
- Hermes Cron: `hermes cron status`
- Honcho integration: `hermes honcho status`

### Remote
- OpenAI: `GET https://api.openai.com/v1/models`
- OpenRouter: `GET https://openrouter.ai/api/v1/models`
- Firecrawl: `GET https://api.firecrawl.dev/v2/team/credit-usage`
- Brave Search: `GET https://api.search.brave.com/res/v1/web/search?q=ping&count=1`
- Browser Use: `GET https://api.browser-use.com/api/v3/browsers`

## Why these checks worked
- They are low-cost.
- They are auth-sensitive.
- They exercise the actual dependency path Hermes uses.
- They return structured data that is easy to validate without brittle HTML scraping.

## End-to-end verification pattern
1. Run the script directly and confirm `NO_ISSUES` or `OUTAGE DETECTED`.
2. Resume the cron if paused.
3. Force a run.
4. Confirm an artifact exists under:
   - `~/.hermes/cron/output/<job_id>/...`
5. Read the artifact and verify:
   - script output was injected correctly
   - final response followed the prompt contract
6. Confirm `cronjob list` shows `last_status: ok` and an updated `last_run_at`.

## Selection caution
Do not add every configured provider automatically. Include only providers whose failure would meaningfully affect the user’s current Hermes workflows; otherwise the watchdog turns into noise.
