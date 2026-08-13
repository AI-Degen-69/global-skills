---
name: hermes-auxiliary-model-verification
description: Use when verifying Hermes auxiliary model slots and image/vision task coverage.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, auxiliary-models, model-routing, image-generation, vision, smoke-test, configuration]
    related_skills: [hermes-agent, hermes-model-optimization, hermes-plugin-compatibility-maintenance]
---

# Hermes Auxiliary Model Verification

Use this skill to smoke-test Hermes auxiliary/task routes through the same runtime code paths Hermes uses, instead of only inspecting `config.yaml`.

## Trigger conditions

Use when the user:

- changes `auxiliary.title_generation`, `auxiliary.skills_hub`, `auxiliary.vision`, `auxiliary.web_extract`, or similar task slots;
- changes image generation providers/plugins;
- asks whether title generation, skills, vision/image understanding, or image generation works;
- reports auxiliary model timeouts, empty session titles, missing image output, or skill-router failures.

## Core principle

Configuration inspection is not verification. A route is verified only when the real task path returns a concrete result:

- title generation → non-empty short title from `agent.title_generator.generate_title`;
- skills hub → non-empty response from `agent.auxiliary_client.call_llm(task="skills_hub")`;
- vision → accurate description of a known local/URL image through `vision_analyze` or the underlying vision task;
- image generation → actual image URL/path, plus a filesystem or HTTP reachability check.

## Workflow

1. **Read config first.** Inspect the `auxiliary:` and `image_gen:` sections so the report names the provider/model actually being exercised.
2. **Create a reversible handle before config changes.** If enabling a plugin or editing config, back up `config.yaml` under `.hermes/backups/` and report the backup path.
3. **Test text auxiliary routes in isolated one-task runs.** Avoid bundling multiple aux calls into one long script; a single slow/free upstream can mask which route hung.
4. **When the request is multi-profile, test in profile context.** Do not assume the global `~/.hermes/config.yaml` proves profile-local overrides are healthy. Read each target profile's `config.yaml` when present and switch into that profile before the smoke test so the runtime exercises the same config the user will actually use.
5. **Use the real code paths.**
   - Title: call `generate_title(...)` from `agent.title_generator`.
   - Generic text slots: call `call_llm(task="<slot>", ...)` from `agent.auxiliary_client`.
   - Vision: test with a known simple image and require the answer to mention expected shapes/text.
   - Image generation: prefer the built-in `image_generate` tool; if a provider plugin was just enabled and the current session has not reloaded plugins, direct-import the provider only as a same-session smoke test and state that a restart/new session is needed for the built-in tool.
6. **Use tight positive success criteria.** Record elapsed time, returned text, provider/model, and artifact path/size.
7. **Separate image generation from image understanding.** A text-to-image backend working does not prove `auxiliary.vision` works, and a vision model working does not prove `image_generate` works.
8. **After any repair, prove the profile parses before declaring success.** A fixed file is not enough; re-run a profile-level command and then rerun the routed smoke test inside that profile.
9. **Clean up temporary probes.** Remove generated test fixtures and one-off plan files; keep useful generated image artifacts only if they are the proof artifact or user-facing deliverable.

## Pitfalls

- Some free model slugs exist for text but do not support image input. For vision, a valid result must come from an endpoint that accepts image content; a 404 such as `No endpoints found that support image input` means the configured model is not a working vision route.
- Profile-local `config.yaml` files can fail in subtle ways after manual edits. One durable failure mode is an adjacent-block formatting error where the last scalar of one section is concatenated with the next top-level key (for example `trace: disabledauxiliary:`). Symptoms: a single profile behaves differently from the global default, overrides appear ignored, or the profile silently falls back to inherited settings. Fix the newline/indentation, then prove recovery with both a profile command and an in-profile aux smoke test.
- Image generation providers are plugin-backed. `hermes plugins enable <provider>` may take effect only in the next session/runtime. For immediate verification, direct-importing the provider can prove backend credentials/auth, but the user should be told the built-in tool may need a restart/reload.
- Do not encode transient missing credentials as a permanent limitation. Capture the fix path: e.g. set `FAL_KEY`, add Nous Portal credits, configure another image provider, or enable a Codex-auth image plugin.
- Free-tier upstreams can be slow or unstable. Prefer per-route scripts with `timeout` wrappers and report exact elapsed times rather than declaring the whole auxiliary stack broken.

## Reference map

- `references/malformed-profile-auxiliary-config.md` — profile-local YAML failure pattern and verification checklist for broken `auxiliary:` blocks.
- `references/smoke-test-recipes.md` — concrete Python snippets and command patterns for title, skills hub, vision, and image generation smoke tests.
