---
name: hermes-auxiliary-model-validation
description: Use when validating Hermes auxiliary model routes for title/skills/vision tasks.
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, auxiliary-models, config, vision, image-generation, smoke-test]
---

# Hermes Auxiliary Model Validation

Use this when Robert changes Hermes auxiliary models or asks whether helper tasks work: title generation, skills hub/search, vision/image analysis, web extraction, compression, approval, MCP routing, or image generation.

## Operating rule

Do not trust the model picker UI alone. Validate each configured route through the same runtime path the task uses, then report the exact provider/model, latency, output, and any config change made.

## Workflow

1. Inspect the relevant `auxiliary.<task>` config and the image generation backend selection.
2. Create a recovery handle before changing Hermes config:
   - Copy `config.yaml` to `.hermes/backups/config-before-<purpose>-<timestamp>.yaml`, or use `hermes config` commands that report the edited file plus a backup you created.
3. Test text auxiliary tasks with `agent.auxiliary_client.call_llm(task=...)` or the task wrapper:
   - Title generation: call `agent.title_generator.generate_title(...)` and require a non-empty concise title.
   - Skills hub: call `call_llm(task="skills_hub", ...)` and require a structured non-empty answer.
4. Test vision/image analysis with a real local image payload and an explicit provider/model override if the current tool process appears stale.
5. Test image generation through the active image backend. If the built-in tool cannot see a newly-enabled plugin in the current process, smoke-test the provider class directly, then tell Robert a new session/restart is needed for the tool surface to pick it up.
6. Clean up temporary test images, scripts, and one-off plan files. Keep only useful generated artifacts and backup handles.

## Pitfalls and fixes

- `vision_analyze` may keep using stale auxiliary config inside an already-running session after `hermes config set`. Verify the config on disk, then run a direct `call_llm(task="vision", provider=..., model=...)` smoke test with an image data URL. New sessions should pick up the config normally.
- A text-only or unsupported OpenRouter model configured under `auxiliary.vision` can fail with “No endpoints found that support image input.” The fix is not to mark vision broken; switch `auxiliary.vision` to a model/provider that actually accepts image input, then verify with a real image.
- `patch` may refuse edits to Hermes config files. Use `hermes config set auxiliary.<task>.<field> <value>` for config changes.
- Image generation is separate from `auxiliary.vision`. If FAL/managed portal credits are unavailable, enable or configure a valid `image_gen` backend such as bundled `image_gen/openai-codex`, then restart/new-session if the current tool registry has not reloaded.
- Windows paths passed to Python inside Git Bash should use native `C:/Users/...` strings for Python `Path(...)`; `/c/...` can be interpreted incorrectly by Python when not converted by the shell.

## Verification standard

A route is verified only when there is positive evidence:

- Title: returned title text and elapsed seconds.
- Skills hub: returned content/JSON and elapsed seconds.
- Vision: accurate description/transcription of a known local image.
- Image generation: success response with provider, model, output path/URL, file existence or reachable URL, and size where local.

## Reference

- `references/live-smoke-snippets.md` contains reusable Python snippets for direct auxiliary and image backend smoke tests.
