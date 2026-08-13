---
name: script-backed-research-crons
description: Use when building recurring research/radar cron jobs that should collect evidence deterministically, persist a
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [cron, research, radar, scripts, automation, telegram, artifacts]
    related_skills: [safe-maintenance-crons, arxiv, blogwatcher]
---

# Script-Backed Research Crons

## Overview

Use this skill for recurring research briefs, trend radars, market scans, release-watch jobs, and source-monitoring jobs where the final output should be a short human update but the underlying collection should be deterministic and inspectable.

The governing pattern is:
1. **collector script first**
2. **dated artifacts second**
3. **LLM summary last**

Do not start with a prompt-only cron if the job is meant to monitor multiple sources over time. Prompt-only research crons are harder to debug, less reproducible, and lose the intermediate evidence you need when a result looks wrong.

## When to Use

Use this skill when the job should:
- scan several public sources on a schedule
- rank or filter candidate signals before summarization
- keep a dated trail of what was seen
- send a Telegram-friendly digest rather than raw crawler output
- support later inspection, ingestion, or downstream chaining

Examples:
- AI/agent research radar
- release-watch digest
- market research leads scan
- vault/knowledge-system monitoring brief
- blog/paper/news roundup with ranking

## Core Architecture

### 1. Deterministic collector script

Create a Python script under `C:/Users/Tiger/AppData/Local/hermes/scripts/` that:
- fetches a bounded set of sources
- normalizes items into one schema
- ranks them with explicit scoring rules
- writes durable artifacts under a dated directory
- prints a compact stdout summary that the cron can inject into the agent prompt

Collector scripts should prefer stdlib or already-installed dependencies. Keep them cheap and repeatable.

### 2. Durable artifacts

Write artifacts under a stable date-partitioned root, for example:
- `.../research-radar/YYYY-MM-DD/ranked-signals.json`
- `.../research-radar/YYYY-MM-DD/ranked-signals.md`
- `.../research-radar/YYYY-MM-DD/unified-feed.md`

Recommended artifact set:
- `ranked-*.json` — machine-readable source of truth
- `ranked-*.md` — quick human inspection
- `unified-feed.md` — broader evidence trail beyond the top items

The point is not archival for its own sake. The point is to make later debugging and reuse easy.

### 3. Script-backed LLM brief

Attach the collector as the cron job's `script`, then make the prompt explicitly say:
- read the injected script output first
- treat the artifacts as the primary evidence source
- do only lightweight follow-up checks when necessary
- produce a concise Telegram-shaped brief

This keeps the LLM in the role it is best at: explanation, prioritization, and concise action framing.

## Prompt Pattern

A good research-cron prompt should explicitly require:
- exact item count (`top 3`, `top 5`, etc.)
- simple explanations, not academic summaries
- clear separation of facts vs interpretation
- links for every item
- one short "what to do next" section
- one final recommendation

For Telegram or Discord delivery:
- use `**bold**` section labels sparingly
- use light emojis only when they improve scanability
- avoid long paragraphs
- do not rely on underline formatting
- prefer a compact card/list layout over a narrative brief when the user asked for links-only monitoring
- if the user specifies exact fields, emit only those fields and nothing else
- for video/watch feeds, default to: title as the link, creator/channel, views, likes if available
- keep scheduler/engine/debug metadata out of the delivered channel message unless the user explicitly asked for ops detail

## Job Configuration Rules

### Use fully qualified skill names

When attaching skills to cron jobs, use the fully qualified skill path, not a bare short name, if there is any possibility of collision.

Good:
- `autonomous-ai-agents/hermes-agent`
- `research/arxiv` when needed by your local library naming

Risky:
- `hermes-agent`

Reason: scheduled jobs can skip an ambiguous short skill reference even when an interactive session might still let you recover manually.

### Restrict toolsets

Typical research radar job:
- `web`
- `file`
- `skills`

Add more only if the job genuinely needs them.

### Delivery

Prefer direct Telegram delivery for production, but verify first with a one-shot local smoke job.

For Discord delivery on Windows, also verify that no other Hermes profile currently owns the same bot token before trusting a failed or missing delivery. See `references/windows-discord-cron-delivery-debugging.md`.

### Same-target auto-delivery contract

Some scheduled Hermes runtimes auto-deliver the assistant's **final response** to the job's configured destination. In those runs, an explicit `hermes send` or `send_message` to the **same target** can be suppressed with a notice that the cron job will already auto-deliver there.

Rules:
- treat the final assistant response as the primary deliverable when the runtime says same-target delivery is automatic
- do not keep retrying same-target explicit sends after that notice; that is duplicate-delivery churn, not remediation
- still write the durable artifact files to disk and verify them separately
- if extra notifications are truly required, use a different target or a distinct explicit-notification path documented by the platform-specific delivery skill

Good capture shape in the final brief:
- note that same-target explicit send was intentionally skipped because the runtime auto-delivers the final response
- include the durable artifact path(s) so the user can inspect the saved files independently of chat delivery

### Translate shell-style cron commands into structured fields

When the user pastes a shell command like `hermes cron create ... --name ... --deliver telegram`, do **not** mirror line-continuation backslashes or shell quoting artifacts into the cron payload. Convert it into structured cron fields (`schedule`, `prompt`, `name`, `deliver`) and then immediately inspect the created job.

Post-create sanity checks:
- confirm the name is correct
- confirm the prompt preview is not a stray slash or truncated fragment
- confirm delivery resolved to the intended target, not `local`
- if a malformed duplicate was created, remove it immediately and keep only the corrected job

## Verification Checklist

Before claiming the cron is ready:
1. Run the collector script directly.
2. Verify artifacts were written in the expected dated directory.
3. Inspect at least one artifact file for sane rankings.
4. Create a one-shot `deliver=local` smoke cron using the same script-backed pattern.
5. Trigger it and run a tick if needed.
6. Read the output artifact under `cron/output/<job_id>/`.
7. Confirm the final brief shape, links, and tone.
8. Verify the scheduler is actually operational (`hermes cron status` / gateway running). Cron configured is not the same as cron firing.
9. Only then rely on the live Telegram delivery path.

## Pitfalls

### Pitfall: prompt-only cron with no evidence trail

A pure LLM cron can produce decent text once, but it gives you no reproducible source trail when the ranking looks wrong.

Fix: move collection and ranking into a deterministic script and make the prompt summarize that evidence.

### Pitfall: bare skill names in scheduled jobs

An ambiguous bare skill name can cause cron runs to skip the intended skill silently or semi-silently.

Fix: use the fully qualified skill path in the cron job definition.

### Pitfall: over-weighting noisy source items

Feeds often contain junky release tags, merge-backup entries, or operational noise that scores well only because the source seems relevant.

Fix: add deterministic exclusion or down-weight rules in the collector script before the LLM ever sees the candidate list.

### Pitfall: no source diversity in top picks

A scoring system can accidentally return three variants of the same source type.

Fix: select top items with light source-diversity rules before final summarization.

### Pitfall: reporting pipeline optimized for the agent, not the user

A technically correct cron can still fail the real task if the delivered message is full of engine notes, artifact paths, planning metadata, or source-explainer prose when the user only wanted a clean watchlist.

Fix:
- design the delivered message around the user's consumption pattern first
- if the user asks for a narrow field set, treat that as a schema, not a suggestion
- keep operational metadata in saved artifacts or references, not in the channel post
- for YouTube/trending watch jobs, prefer one item per video with: linked title, creator, views, likes if available
- only add extra interpretation when the user explicitly asks for analysis

### Pitfall: formatting improvements applied only in chat

If you adjust wording or layout only in the current conversation, the scheduled job still emits the old format.

Fix: patch the cron prompt itself and verify the next output artifact.

### Pitfall: Windows cron script resolution does not follow your assumed workdir

On Windows Hermes setups, a relative cron `script` name can still be resolved under `C:/Users/Tiger/AppData/Local/hermes/scripts/` even when the job's stored `workdir` suggests another directory. That can produce misleading `Script not found:` errors or a mismatch between the job definition you think you have and the path the scheduler actually probes.

Fix:
- inspect the persisted job definition and last error path
- align the wrapper script with the resolver's actual lookup directory
- keep `script` and `workdir` pointed at the same real directory
- rerun and verify with an actual `delivered to discord:...` scheduler log line

### Pitfall: direct script output works, cron capture still goes silent

A collector can print fine when run manually yet still be classified by Hermes cron as `script produced no output` or `(no_agent): empty stdout — silent run`.

Fix:
- prove the collector's direct stdout first
- then interpose a tiny wrapper that runs the collector, saves stdout to a debug artifact, and re-emits it verbatim
- target the cron at that wrapper until scheduler capture is stable
- keep the wrapper small and deterministic so delivery debugging stays separate from the research logic

### Pitfall: Discord delivery debugging without clearing cross-profile gateway contention

On multi-profile Hermes setups, another profile can already own the same Discord bot token. In that state, cron delivery tests are noisy and misleading because the scheduler may appear healthy while the gateway keeps rejecting ownership.

Fix:
- inspect the owning PID/profile from the logs
- stop the competing profile gateway first
- only then rerun the cron and judge delivery from fresh scheduler log lines

See `references/windows-discord-cron-delivery-debugging.md` for the exact repair sequence.

### Pitfall: bare JSON list as injected script output

A script that prints a top-level JSON array can be awkward for cron prompt injection and downstream handling. In at least one real repair, a docs-drift cron failed with `AttributeError: 'list' object has no attribute 'items'` even though the collector itself ran fine.

Fix:
- prefer a top-level object envelope such as `{ "drifts": [...] }` rather than a bare list
- make the prompt name the exact top-level field it should read
- keep the script output contract stable and explicit
- when debugging, compare the collector's direct stdout with the rendered file in `cron/output/<job_id>/`

### Pitfall: failure delivery with no remediation follow-through

If a cron sends a failure alert and you stop at the raw error, the user gets noise instead of operations.

Fix:
- inspect the cron output artifact immediately
- inspect the job definition itself for malformed fields or stale values
- identify whether the failure is in the collector, the prompt contract, or delivery/rendering
- rerun after the fix and verify the new run state before closing the task

### Pitfall: mis-clearing script mode

Do not use the string literal `"none"` as a cron job script value. That is treated as a real script path rather than "no script".

Fix: clear the script field properly via cron update semantics instead of storing a placeholder string.

### Pitfall: scheduler not actually running

A job can look correctly configured in `cron list` and still never execute because the gateway/scheduler is down.

Fix: verify operational status explicitly before sign-off. If `hermes cron status` says cron jobs will not fire, start or repair the gateway first, then rerun the smoke check.

## Support Files

See `references/research-radar-pattern.md` for a compact pattern covering collector schema, artifact layout, smoke verification, and ranking hygiene.

See `references/docs-drift-cron-debugging.md` for a concrete repair pattern covering injected-output shape, script-field cleanup, and post-failure verification.

See `references/same-target-auto-delivery.md` for the duplicate-delivery guard pattern when a scheduled runtime auto-delivers the final response to the same destination.

See `references/channel-digest-formatting.md` for the pattern that separates operator artifacts from the human-facing channel post, with a minimal schema for link-first watchlists.

## Common Pitfalls

- letting the LLM perform broad open-ended web exploration every run
- skipping artifact creation because the current output "looks fine"
- verifying only the script and not the cron-rendered brief
- trusting ambiguous short skill names in scheduled jobs
- shipping a ranking system without noise filters or diversity checks

## Final Rule

If the cron's value depends on repeated monitoring, make it **artifact-backed by default**. The final message is the product surface, but the collector script is the operational core.
