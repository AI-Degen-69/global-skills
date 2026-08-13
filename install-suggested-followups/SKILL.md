---
name: install-suggested-followups
description: Use when teaching an agent to embed the suggested-followups behavior permanently.
version: 1.0.1
author: Codebuff (Codex CLI)
license: MIT
platforms: [windows, macos, linux]
metadata:
  tags:
    - agent-behavior
    - followups
    - suggestions
    - system-installer
    - self-audit
    - cross-runtime
  related_skills:
    - post-task-summary-protocol
    - completion-contract-loop
    - user-interaction-patterns
    - exact-output-compliance
triggers:
  - "install suggested followups"
  - "permanent followups"
  - "fix the suggestions loop"
  - "suggested followups behavior"
  - "make followups durable"
  - "install-suggested-followups"
mutating: true
---

# Install Suggested Followups

## Overview

This skill is a **self-installer**. It teaches an agent to audit its own
system-prompt layers and write the suggested-followups behavior into the one
file that persists across sessions and model reloads — the agent's own
governance file, not a transient or skills-only file.

The behavior the agent must embed:

1. Every reply ends with a `## Followup Suggestions` section written as
   **plain markdown prose** (never clickable host cards).
2. Every followup MUST start with a **bold title** that ends with `:` and
   is followed by a single descriptive sentence (the action verb +
   concrete subject pattern).
3. While the task is unfinished, the agent MUST push back, propose
   alternatives, and propose refinements directly in the followup list.
4. When the task is genuinely done, the reply MUST carry the literal line
   `Task complete.` in the prose above the section AND the first followup
   MUST open with the literal phrase `**Main objective was done.**`. Any
   remaining followups MUST start with `**Optional polish:**` and never
   be framed as required work.
5. The host's clickable suggestion component / `suggest_followups` tool is
   banned for this purpose — using it is the exact cause of the
   suggestions-loop this skill exists to break.

This is a generalization of the `~/.knowledge.md` fix-patch that the user
already proved works in Codebuff/Codex CLI. This skill encodes the patch
into a portable installer so the same behavior persists across agents
without copy-pasting the patch into each agent's runtime.

## When to Use

Trigger this skill when any of the following is true:

- The agent is reporting tasks as complete and immediately adding more
  suggestions in a loop. (`Suggestion loop` symptom.)
- The user wants followups to appear as **plain markdown text** instead of
  the host's clickable cards.
- A new agent runtime is being onboarded (fresh Hermes profile, fresh
  Codex/Codebuff install, fresh Claude Code setup) and the user wants
  followups behavior installed at the core before they start using it.
- After a model switch, prompt rebuild, or major `SOUL.md` overwrite that
  dropped the previous behavior.
- After the user manually upgrades `~/.knowledge.md` and wants the same
  behavior applied to other runtimes.

Do not trigger this skill for one-off reply formatting. It is a
governance installer; use it once per runtime per behavior-change.

## Contract

This skill guarantees that, after it runs:

- The agent has located its own canonical system file (the one the host
  concatenates into the system prompt on every reload).
- The system file contains a `## Followup Suggestions (mandatory output
  format)` section with the full spec block from this skill.
- The spec includes: the bold-prefix rule, the no-clickable-component
  rule, the `Task complete.` trigger, the `**Main objective was done.**`
  first-card rule, and the `**Optional polish:**` residual rule.
- The change is durable across sessions and model reloads (restart or
  reload is documented if the runtime caches its prompt).
- A verification report is produced with the exact file path and the
  exact diff hunk summary.

## The Required Behavior (the spec)

This is the canonical block the agent must embed in its own system file.
It is reproduced verbatim from the spec — DO NOT paraphrase, shorten,
or re-order it. The wording is part of the contract.

````markdown
## Followup Suggestions (mandatory output format)

Mandatory output format for every reply — defined at the system layer and
required to match across sessions, reloads, and devices. End every reply
with a `## Followup Suggestions` section written as plain markdown prose —
never as a clickable host card or suggestion tool, which forces an
infinite suggestion loop.

Each followup MUST start with a **bold title** that opens with an action
verb and ends with `:` followed by a single descriptive sentence.

In the per-reply output, the section looks like this:

```markdown
## Followup Suggestions

- **<Action verb + concrete subject>:** <single sentence describing the next step the user can take>.
- **<Action verb + concrete subject>:** <single sentence describing the next step the user can take>.
- **<Action verb + concrete subject>:** <single sentence describing the next step the user can take>.
```

Rules:

1. Every followup MUST begin with `**...**` ending in `:`. No exceptions.
2. The description after the colon is one sentence — concrete and
   immediately actionable. No vague prompts like "iterate" or "improve".
3. Until the task is genuinely complete, push back, propose
   alternatives, and explain refinements directly in the followups. Do
   NOT just echo the user's last message back as a followup.
4. When the task is genuinely done, the prose above the section MUST
   contain the literal line `Task complete.` AND the first followup
   MUST open with the literal phrase `**Main objective was done.**`.
   Any remaining followups MUST start with `**Optional polish:**`
   and never be framed as work required to consider the turn complete.
5. Do NOT emit the host's clickable suggestions UI (cards, buttons,
   `suggest_followups` tool, etc.) for this purpose — that produces
   the suggestion loop. Plain markdown only.
````

### Worked examples

The spec rules above are normative. These examples show how the rules
apply in practice; do not treat the example phrasing as a substitute
for the spec.

Iterating on a broken feature (no `Task complete.` line yet):

```markdown
## Followup Suggestions

- **Fix the failing type check:** rerun the typecheck and patch the
  three exact errors before closing the turn.
- **Rename `foo` to `bar` in `src/index.ts`:** update the import path
  and rerun the smoke test.
- **Add a unit test for `parse()`:** cover the two empty-input
  branches that drove the bug.
```

Task genuinely done:

```markdown
Task complete.

## Followup Suggestions

- **Main objective was done.**
- **Optional polish:** add a CHANGELOG entry describing the new
  behavior so future readers see it landed.
```

## Audit Phase

The agent first audits its own runtime to find the canonical
system-prompt file. The audit is runtime-specific. The agent MUST
identify which runtime is currently active before writing anything.

### Runtime Detection

Use the smallest signal first; do not assume a runtime without proof.

| Signal | Runtime |
|---|---|
| `~/.hermes/` exists with `profiles/` and a `gateway` or `agent` process | **Hermes** |
| `~/.hermes/profiles/<active>/SOUL.md` was loaded into this turn | **Hermes (active profile)** |
| `~/.knowledge.md` was loaded into the system prompt of this turn | **Codex / Codebuff CLI** |
| `~/.claude/CLAUDE.md` exists OR a project-level `CLAUDE.md` was loaded | **Claude Code** |
| `~/.codex/instructions.md` or `~/.codex/AGENTS.md` exists | **Codex CLI** |
| `AGENTS.md` at the project root was loaded | **Generic OpenAI-style runner** |
| None of the above match | **Unknown** — escalate before writing |

If multiple signals match (e.g., Hermes AND Codex are both available
because Hermes is delegating to a Codex CLI subagent), pick the file
that THIS TURN's system prompt was loaded from. That is the
authoritative file. Writing to a sibling runtime while another runtime
is driving this turn is drift, not installation.

### Runtime: Hermes

Inspect, in priority order:

1. `~/.hermes/profiles/<active>/SOUL.md` — the **active profile's SOUL**
   is the canonical level for per-profile override behavior. This is
   almost always the file to write.
2. `~/.hermes/profiles/<active>/AGENTS.md` — second-best if SOUL is
   marked read-only or template-only.
3. `~/.hermes/SOUL.md` — root SOUL applies only if the active profile
   explicitly inherits it and does not override the section.
4. `~/.hermes/AGENTS.md` — root AGENTS.
5. `~/.hermes/profiles/<active>/config.yaml` — only as a last resort
   when a YAML `behavior:` block is the documented extension point.

Discovery commands:

```bash
ls -la ~/.hermes/ ~/.hermes/profiles/*/ 2>/dev/null
test -f ~/.hermes/profiles/<active>/SOUL.md && echo "active SOUL found"
hermes profile show --json 2>/dev/null | head -40    # active profile name
```

### Runtime: Codex / Codebuff CLI

Inspect, in priority order:

1. `~/.knowledge.md` — the user-preferences file Codebuff concatenates
   into the system prompt. This is almost always the file to write.
2. `~/.knowledge.local.md` — local override, if present.

Discovery:

```bash
ls -la ~/.knowledge* 2>/dev/null
```

If the running agent is Codex CLI itself (rather than Codebuff
calling Codex as a subagent), also inspect `~/.codex/instructions.md`
and `~/.codex/AGENTS.md`.

### Runtime: Claude Code

Inspect, in priority order:

1. **Project-level** `<repo-root>/CLAUDE.md` — applies only inside the
   project. Use this when the user wants the behavior scoped to one
   project.
2. **User-level** `~/.claude/CLAUDE.md` — applies to every Claude Code
   session globally. Use this when the user wants the behavior global.

Discovery:

```bash
ls -la ~/.claude/CLAUDE.md 2>/dev/null
git -C <repo-root> ls-files CLAUDE.md .claude/CLAUDE.md 2>/dev/null
```

### Runtime: Generic (AGENTS.md-based runners)

Inspect:

- `<project>/AGENTS.md`
- `~/.config/<runner>/AGENTS.md`

Confirm the runner actually loads AGENTS.md before writing the spec
into it. Some runners ignore AGENTS.md; for those, fall back to the
host CLI documentation to find the authoritative prompt file.

### Runtime: Unknown

If none of the above signals matched AND the agent cannot identify its
own runtime from process / env inspection, STOP. Escalate to the user
with: "I cannot determine which runtime I am running on. Please name
the runtime and the canonical system file path so I can install the
followups spec." Do NOT guess and write — that creates drift across
multiple system files and makes future auditing impossible.

## Already-Installed Detection

Before writing anything, the agent MUST fingerprint the candidate file
for the spec. If the spec is already present, the install is a no-op.

Fingerprint signals (any one is sufficient to declare "already
installed"):

- The literal string `## Followup Suggestions (mandatory output format)`
  appears as a heading in the candidate file. This indicates the spec
  was installed by this skill (or by an equivalent installer) — a
  fingerprint that survives copy-paste variations in body text.
- The literal string `Main objective was done.` appears in the file.
- The literal string `Optional polish:` appears as the start of a
  list item in the file.
- The literal string `do NOT emit the host's clickable suggestions UI`
  (case-insensitive) appears in the file.

If the spec is already present, stop and report "already installed at
<path>". Do not rewrite, do not patch around it, do not append a
second copy.

### Partial-Coverage Handling

If only some of the fingerprint signals match (e.g., the bold-prefix
rule exists but the `Task complete.` terminator does not), report the
gap explicitly and ask the user before patching. Do not silently merge
the missing pieces — that can collide with custom phrasing the user
deliberately kept.

### Conflict Detection

If the file already contains content that contradicts the spec, the
agent MUST surface the conflict before writing. Conflict patterns:

- A line like "Use the suggestion tool/cards for followups" — this is
  the path that causes the loop.
- A closed-list ritual like "Always present `1/2/3 next steps`" without
  bold-prefix and without the loop terminator.
- A `Task is done` line that uses a different phrase than the spec's
  `Task complete.` literal.

When a conflict is found, present the diff to the user before writing.
Do not auto-merge conflicting content.

## Install Phase

The agent performs exactly one of three actions:

1. **No-op** — spec already fully present (see Already-Installed).
2. **Append** — append the spec block as a new section, ideally at the
   end of the file or after the last behavior section.
3. **Patch (gated)** — only when the user has approved a conflict
   merge, replace the colliding content with the spec.

Default action is **Append**. Append produces:

```markdown

## Followup Suggestions (mandatory output format)

[... full canonical block from this skill ...]

```

Insert a blank line before the heading. Do not duplicate the heading
if it already exists. Do not apply a YAML frontmatter rewrite. The
agent's candidate file write paths (per runtime detection) are listed
in the Audit Phase above.

## Verification Phase

After the install, the agent MUST verify the write succeeded:

1. **Grep for the heading**: confirm `## Followup Suggestions (mandatory
   output format)` is now present in the target file.
2. **Grep for the loop terminator**: confirm `Main objective was done.`
   is present.
3. **Grep for the polish clause**: confirm `Optional polish:` is
   present.
4. **Readback**: read the surrounding 30 lines around the insertion
   point and confirm there is no malformed markdown (e.g., doubled
   headings, broken fences, swallowed indentation).
5. **Restart / reload note**: if the runtime caches its prompt, tell
   the user to restart or reload so the next session picks up the spec.

If any verification step fails, roll back the write if the runtime
supports it (most file-write tools do not; in that case, manually
re-edit the file back to the previous state with `str_replace`).

## Reporting

Produce a concise install report:

```
Runtime detected:   <Hermes | Codex/Codebuff | Claude Code | Generic | Unknown>
Canonical file:     <absolute path>
Action taken:       <no-op | appended | patched-with-approval>
Section heading:    ## Followup Suggestions (mandatory output format)
Spec size:          <approx lines appended>
Verification:
  - heading present:    <yes | no>
  - terminator present: <yes | no>
  - polish present:     <yes | no>
  - readback clean:     <yes | no>
Reload required:    <yes | no — restart the runtime / new session>
Conflicts found:    <none | list them>
Approval needed:    <none | list anything that needs user confirmation>
```

## Anti-Patterns

- **Writing the spec into a skill file instead of the system file.**
  Skill files are loaded conditionally. The system file is the
  source of truth and persists across reloads. This is the #1 most
  common failure mode.
- **Re-creating the clickable suggestion component path the spec
  bans.** The host's `suggest_followups` tool/component is exactly
  what causes the loop the user is trying to fix. Patch it away if
  present; do not re-introduce it.
- **Rewriting the file when the spec is already partially present.**
  Always do an already-installed fingerprint check first.
- **Adapting the spec wording to "fit" the file's tone.** The spec's
  exact phrasing (`Task complete.`, `Main objective was done.`,
  `Optional polish:`) is part of the contract and is what the
  verification grep checks against.
- **Writing into multiple sibling runtimes simultaneously.** Pick
  the one that THIS TURN's prompt loaded from. Writing to siblings
  in the same install run is drift.
- **Skipping the unknown-runtime escalation.** If the runtime
  cannot be identified, ask. Never guess.
- **Treating the user's `~/.knowledge.md` fix patch as inspiration
  to clone into every file.** Use the patch as the spec, but only
  write it into the canonical file for the active runtime, not
  into every adjacent preference file.
- **Reusing a fenced markdown block to wrap a block that itself
  contains a fenced markdown block without nesting the fences.**
  Use 4-backtick (or higher) outer fences when the spec block
  itself contains an example that uses 3-backtick fences. The
  published version of this skill uses 4-backtick fences for the
  spec block for exactly this reason.

## Common Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Spec appended to the wrong file | Profile override vs root override mismatch in Hermes, or wrote to `~/.knowledge.md` when Claude Code was the active runtime | Re-run the audit; pick the file the active runtime actually loaded this turn |
| Followups still render as clickable cards after install | Spec was written but the runtime is still using the host's suggestion UI instead of the spec's plain markdown | Restart the runtime / open a new session so the updated prompt concatenates |
| Agent loops indefinitely despite spec installed | Spec is missing the `Task complete.` terminator or the `**Main objective was done.**` first-card requirement | Re-append the missing rule to the same file |
| Spec duplicated in the same file (two `## Followup Suggestions` headings) | Already-installed check was skipped because the grep was case-sensitive or because the user already had a partial copy | Read the file once, dedupe, and re-run the verification grep |
| Bold-prefix followups appear without the action verb | The agent followed the bold-prefix shape but lost the action verb because the template said `<concrete subject>` instead of `<Action verb + concrete subject>` | Re-state the rule in the spec with the action verb prefix |
| Vague followups like "iterate" or "improve this" survived install | Spec was installed but the bold-description sentence rule was not enforced because the spec said "single descriptive sentence" without "concrete and immediately actionable" | Tighten the rule and re-install |
| Spec installed but only half the runtimes picked it up | The user has Hermes AND Codex CLI running in parallel; install ran on Hermes but Codex keeps using its own UI | Run the audit for each runtime independently; do not assume cross-runtime propagation |
| Spec block has broken nested markdown fences after install | The agent copy-pasted the spec without nesting the outer fence at 4 backticks | Use 4-backtick outer fences around the spec block (as published in this skill) |

## Companion Scripts

A drop-in installer pair lives next to this skill for fresh machines
and slash-command invocation:

- `scripts/install-suggested-followups.sh` — bash / POSIX-shell
  installer. Detects the active runtime (Hermes / Codex / Codebuff /
  Claude Code / Generic `AGENTS.md`), fingerprints the target file
  for already-installed, appends the canonical spec block, verifies
  with grep, and prints the install report. Supports
  `--runtime=<name>`, `--target=/abs/path`, `--dry-run`, `--help`.
  Exit codes: `0` ok / `1` generic / `64` ambiguous-or-conflict /
  `73` write failed.
- `scripts/install-suggested-followups.ps1` — PowerShell installer
  for Windows / cross-platform PowerShell Core (`pwsh`). Same
  argument shape (`-Runtime`, `-Target`, `-DryRun`, `-Help`). Writes
  UTF-8 without BOM via `[System.IO.File]` so leading headings don't
  get a stray BOM and downstream parsers don't choke.

Both scripts embed the same canonical spec block used by the SKILL.md
"The Required Behavior (the spec)" section, written byte-identical
when the scripts pass. To invoke by path (the simplest install mode;
these are NOT registered as agent slash commands — wire them up to a
slash command at the agent layer if you want path-less invocation).
The examples below assume the current working directory is the
Global-Skills repo root; from any other directory, prefix the path
with the absolute repo location:

```bash
# from the Global-Skills repo root
./install-suggested-followups/scripts/install-suggested-followups.sh --dry-run
./install-suggested-followups/scripts/install-suggested-followups.sh
```

```powershell
# from the Global-Skills repo root
pwsh -File ./install-suggested-followups/scripts/install-suggested-followups.ps1 -DryRun
pwsh -File ./install-suggested-followups/scripts/install-suggested-followups.ps1
```

The scripts do the audit → fingerprint → append → verify pipeline
the agent does manually; you don't have to re-read the SKILL.md body
on a fresh box.

## References

- `meta/skill-library/SKILL.md` — class-level rules about where the
  spec belongs and what NOT to capture when learning a new behavior.
- `meta/skill-maintenance/SKILL.md` — patterns for cross-runtime
  drift detection and frontmatter/file-name hygiene.
- `meta/post-task-summary-protocol/SKILL.md` — adjacent pattern about
  how replies close out.
- `meta/completion-contract-loop/SKILL.md` — adjacent pattern about
  stop conditions, applied here to "task is genuinely done."
- `meta/exact-output-compliance/SKILL.md` — explains why the literal
  wording of the spec (`Task complete.`, `Main objective was done.`,
  `Optional polish:`) is part of the contract, not decoration.
- `~/.knowledge.md` — the user's canonical fix patch this skill
  generalizes. The wording of the spec is a portable version of
  that patch's wording.

## Verification Checklist

- [ ] Runtime detection succeeded (Hermes / Codex / Claude Code /
      Generic / Unknown-with-escalation).
- [ ] Canonical system file identified and confirmed it is the one
      THIS TURN's prompt loaded from.
- [ ] Already-installed fingerprint check ran — no full copy of the
      spec was found in the target file.
- [ ] No unresolvable conflict with current file content, OR user
      approval was obtained for a patch.
- [ ] Spec block appended as a new section with the exact heading
      `## Followup Suggestions (mandatory output format)`.
- [ ] Spec block uses 4-backtick outer fences so its inner 3-backtick
      example renders cleanly when the agent copy-installs it into
      another system file.
- [ ] Verification grep confirmed the heading, the `Main objective was
      done.` terminator, and the `Optional polish:` clause are all
      present.
- [ ] Readback of 30 lines around the insertion point showed clean
      markdown.
- [ ] If the runtime caches prompts, the user was told to restart /
      open a new session.
- [ ] Install report produced with all required fields.
