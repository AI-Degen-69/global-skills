---
name: cross-harness-plugin-porting
description: Use when evaluating or porting an external agent plugin into Hermes.
version: 1.0.0
author: Hermes
---

# Cross-Harness Plugin Porting

## When to Use
Use this skill when the user asks whether an external agent ecosystem artifact can be used in Hermes, especially when they say things like:
- "can we install this into Hermes?"
- "does this plugin work with Hermes?"
- "port this workflow to Hermes"
- "is this skill pack/plugin compatible with Hermes?"
- "can Hermes implement this methodology?"

Typical sources:
- Claude Code plugins
- Codex plugins / agent packs
- Cursor plugins
- Copilot agent/plugin repos
- multi-agent workflow repos that ship prompts, manifests, or slash-command systems

## Core Principle
Separate **workflow portability** from **packaging compatibility**.

A methodology may be fully implementable in Hermes even when the upstream repo is **not directly installable**. Do not collapse those into a single yes/no answer.

## Procedure
1. **Identify the artifact class**
   Determine whether the upstream thing is primarily:
   - a workflow/methodology,
   - a skills/prompt pack,
   - a native plugin/tooling extension,
   - or a mixed repo.

2. **Check Hermes-native install surfaces**
   Verify Hermes' relevant extension shapes before concluding compatibility:
   - skills under `~/.hermes/skills/`
   - plugins with Hermes-native manifest/loader structure
   - optional plugin-bundled skills

3. **Inspect the upstream repo/package shape**
   Look for concrete compatibility signals, not branding claims:
   - manifest files
   - loader entrypoints
   - plugin metadata formats
   - skill/prompt file layout
   - agent definitions
   - setup/install commands

4. **Map concepts, not names**
   Translate upstream primitives into Hermes primitives:
   - slash-command skill → Hermes skill
   - subagent orchestration → `delegate_task`
   - persistent project plan → `.hermes/plans/`
   - task list/workflow tracker → `todo`
   - custom runtime hooks → Hermes plugin or cron/hook surface
   - memory/learning loop → Hermes skills + memory

5. **Decide the integration tier**
   Classify the result into one of these:
   - **Directly installable**: repo/package already matches Hermes extension format
   - **Skill-portable**: workflow can be implemented as Hermes skills without a plugin
   - **Plugin-portable**: needs a Hermes-native plugin adapter/port
   - **Concept-only**: methodology is useful, but implementation would be substantial

6. **Recommend the lowest-risk path**
   Default to:
   - **skill-first port**, then
   - plugin only where skills are insufficient.

   This avoids overbuilding and proves value before custom extension work.

## Output Format
Answer in four parts when the task is non-trivial:
1. **Direct answer** — can/can't install directly
2. **Why** — concrete manifest/runtime mismatch or match
3. **What is still reusable** — workflow, skills, prompts, review loop, etc.
4. **Recommended implementation path** — usually skill-first, plugin-later

## Pitfalls
- **Do not confuse methodology with installer compatibility.** A good workflow can still be non-native to Hermes.
- **Do not trust repo marketing copy alone.** Verify with actual file structure and install surfaces.
- **Do not jump straight to plugin authoring.** If skills and existing tools cover 80% of the value, start there.
- **Do not answer only from memory.** Check both Hermes' extension model and the upstream repo shape.
- **Do not reduce the result to a binary no.** If direct install fails but the workflow ports cleanly, say so clearly.

## Verification
A compatibility conclusion is only complete when you have:
- verified Hermes install/extension surfaces,
- inspected the upstream repo/package structure,
- identified the concrete mismatch or match,
- and produced a recommended porting path.

## References
- `references/compound-engineering-to-hermes.md` — example evaluation of EveryInc Compound Engineering against Hermes
