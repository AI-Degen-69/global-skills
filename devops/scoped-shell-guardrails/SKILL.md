---
name: scoped-shell-guardrails
description: Use when a workflow needs scoped shell guardrails (not fully read-only or blocked).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [guardrails, hooks, scope, policy, safety]
    related_skills: [hermes-agent]
---

# Scoped Shell Guardrails

## When to Use

Use this skill when a workflow is **scoped rather than purely read-only or purely blocked**. Typical cases:

- target-domain ingestion with allowed writes inside one domain but not elsewhere
- maintenance workflows where generated files are allowed only for a specific target
- shell-hook / pre-tool-call governance for tools like `terminal`, `write_file`, `patch`, or `execute_code`
- any policy that says "allow X here, but not there"

## Core Rule

If hooks only validate the **outer tool call**, assume there is a guardrail gap until you explicitly cover:

1. direct path edits
2. known mutating commands
3. interpreter/subprocess bypasses

Path blocking alone is not enough for scoped workflows.

## Design Pattern

### 1. Split policy into three layers

- **Protected paths**: hard block
- **Scoped writes**: allow only with an explicit scope signal
- **Global or unrelated writes**: approval-gated or blocked

### 2. Guard every relevant tool surface

At minimum, review coverage for:

- `write_file`
- `patch`
- `terminal`
- `execute_code`

If `execute_code` is not covered, you do not have a real write boundary.

### 3. Add command-policy for known mutators

For deterministic scripts or commands that write files internally, do not rely on path regexes alone. Add explicit command handling for cases like:

- global catalog rebuilds
- `--all` regeneration commands
- domain-specific rebuild commands
- helper scripts that treat unknown args as normal execution instead of safe help output

### 4. Require an explicit scope signal

For scoped writes, require a machine-checkable signal such as:

- active target file
- environment variable
- runtime marker file
- explicit CLI argument that must match the active target

The hook should verify both the requested write target and the active scope signal.

### 5. Distinguish read-only verification from mutating maintenance

Default verification commands should be read-only. Mutating maintenance must be opt-in or approval-gated.

### 6. End with changed-file verification

Before claiming success, require a final classification pass over changed files:

- expected in-scope changes
- expected generated scoped files
- unexpected out-of-scope changes
- protected changes

If unexpected or protected paths changed, stop and report.

## Recommended Procedure

1. Identify the protected files that must never change silently.
2. Enumerate deterministic mutators that can write indirectly.
3. Enumerate interpreter paths that can bypass ordinary path hooks.
4. Define the active-scope marker.
5. Implement hook logic in shared helpers first.
6. Update hook config only after the logic is correct.
7. Patch procedure skills/docs so the workflow actually sets and clears the scope marker.
8. Verify both allowed and blocked cases with synthetic payloads.
9. Add final changed-file verification to the governing workflow.

## Verification Patterns

Positive tests should prove:

- protected direct writes are blocked
- safe read-only commands are allowed
- matching in-scope generated writes are allowed

Negative tests should prove:

- global mutators are blocked
- unrelated-domain rebuilds are blocked
- out-of-scope wiki/content edits are blocked during scoped mode
- `execute_code` cannot write directly or invoke mutating scripts as a bypass

## Pitfalls

1. Protecting `write_file` and `patch` but forgetting `terminal`.
2. Protecting `terminal` path strings but forgetting script-internal writes.
3. Forgetting `execute_code`, leaving a trivial Python bypass.
4. Allowing scoped writes without a machine-readable active target.
5. Running global mutators during scoped maintenance because they felt "safe".
6. Reporting success before changed-file verification.
7. Documenting policy in prose while hooks enforce something weaker.

## References

- `references/vault-domain-ingestion-case-study.md` — concrete example of scoped ingestion guardrails spanning direct edits, terminal-triggered script writes, and `execute_code` bypasses.
- Add concrete mutation-path examples, command patterns, and verification payloads under `references/` when you discover them.
